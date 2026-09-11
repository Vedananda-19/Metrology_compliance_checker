from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
from sqlalchemy.orm import Session
from models import (
    Inspections,
    InspectionImages,
    OCRTextRegions,
    Products,
    ExtractedFacts,
    RuleResults,
    Violations,
    Evidence,
    Rules,
    RuleSets,
    ReferenceTables,
)
from services import storage_service
from pipeline import preprocess, ocr, extraction, classify, vision, facts as fact_builder, events, retrieval
from engine import engine as rule_engine
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class SilentReporter:
    def emit(self, *args, **kwargs):
        return None

    started = completed = failed = emit

AUTOMATED_MODES = {"LABEL_AUTOMATED", "VISION_AUTOMATED"}
OPEN_STATUSES = {"REQUIRES_VERIFICATION"}


def fact_paths_in(node, found=None):
    found = found if found is not None else []
    if isinstance(node, dict):
        if "fact" in node and isinstance(node["fact"], str):
            found.append(node["fact"])
        if "each" in node and isinstance(node["each"], str):
            found.append(node["each"])
        for value in node.values():
            fact_paths_in(value, found)
    elif isinstance(node, list):
        for value in node:
            fact_paths_in(value, found)
    return found


class PipelineState(TypedDict, total=False):
    inspection_id: str
    user_id: str
    run_no: int
    panels: list[dict]
    regions: list[dict]
    label_text: str
    declarations: dict
    classification: dict
    ruleset: dict
    tables: dict
    report: dict
    development_mode: bool
    degraded_mode: bool
    error: str


def load_rule_data(db: Session, version: str):
    record = db.query(RuleSets).filter(RuleSets.rule_set_version == version).first()
    if record is None:
        return rule_engine.load_ruleset(), rule_engine.load_tables()

    rows = db.query(Rules).filter(Rules.rule_set_version == version).all()
    ruleset = {
        "rule_set_id": record.rule_set_id,
        "rule_set_version": record.rule_set_version,
        "title": record.title,
        "legal_basis": record.legal_basis,
        "macros": record.macros,
        "fact_vocabulary": record.fact_vocabulary,
        "rules": [
            {
                "rule_id": row.rule_id,
                "version": row.version,
                "status": row.status,
                "title": row.title,
                "category": row.category,
                "provision": row.provision,
                "verification_mode": row.verification_mode,
                "severity": row.severity,
                "applies_when": row.applies_when,
                "exempt_when": row.exempt_when or [],
                "check": row.check_expr,
                "outcome_on_fail": row.outcome_on_fail,
                "fail_message": row.fail_message,
                "evidence_facts": row.evidence_facts or [],
                "threshold_source": row.threshold_source,
                "effective_from": row.effective_from.isoformat(),
                "effective_to": row.effective_to.isoformat() if row.effective_to else None,
                "amendment_status": row.amendment_status,
            }
            for row in rows
        ],
    }
    tables = {
        row.table_name: row.data
        for row in db.query(ReferenceTables).filter(ReferenceTables.rule_set_version == version).all()
    }
    return ruleset, tables


class Pipeline:
    def __init__(self):
        graph = StateGraph(PipelineState)
        graph.add_node("preprocess_images", self.preprocess_images)
        graph.add_node("run_ocr", self.run_ocr)
        graph.add_node("normalize_ocr", self.normalize_ocr)
        graph.add_node("extract_declarations", self.extract_declarations)
        graph.add_node("classify_product", self.classify_product)
        graph.add_node("determine_applicable_rules", self.determine_applicable_rules)
        graph.add_node("evaluate_compliance", self.evaluate_compliance)
        graph.add_node("generate_evidence", self.generate_evidence)
        graph.add_node("generate_report_data", self.generate_report_data)

        graph.set_entry_point("preprocess_images")
        graph.add_edge("preprocess_images", "run_ocr")
        graph.add_edge("run_ocr", "normalize_ocr")
        graph.add_edge("normalize_ocr", "extract_declarations")
        graph.add_edge("extract_declarations", "classify_product")
        graph.add_edge("classify_product", "determine_applicable_rules")
        graph.add_edge("determine_applicable_rules", "evaluate_compliance")
        graph.add_edge("evaluate_compliance", "generate_evidence")
        graph.add_edge("generate_evidence", "generate_report_data")
        graph.add_edge("generate_report_data", END)

        self.graph = graph.compile()
        self.db: Session | None = None
        self._reporter: events.Reporter | None = None

    @property
    def reporter(self):
        return self._reporter or SilentReporter()

    @reporter.setter
    def reporter(self, value):
        self._reporter = value

    def run(self, db: Session, inspection: Inspections, reporter: events.Reporter, run_no: int = 1):
        self.db = db
        self.reporter = reporter
        state: PipelineState = {
            "inspection_id": inspection.id,
            "user_id": inspection.user_id,
            "run_no": run_no,
            "development_mode": False,
            "degraded_mode": False,
        }
        return self.graph.invoke(state)

    def preprocess_images(self, state: PipelineState):
        db = self.db
        images = (
            db.query(InspectionImages)
            .filter(
                InspectionImages.inspection_id == state["inspection_id"],
                InspectionImages.usability == "USABLE",
            )
            .order_by(InspectionImages.display_order)
            .all()
        )
        self.reporter.completed("IMAGE_RECEIVED", f"{len(images)} usable image(s) loaded", count=len(images))
        self.reporter.started("PREPROCESSING", "Correcting orientation, scale and contrast")

        panels = []
        for order, image in enumerate(images):
            try:
                data = storage_service.download(image.storage_path)
                prepared = preprocess.prepare(data)
            except Exception as error:
                logger.exception("Preprocessing failed for %s", image.id)
                image.ocr_status = "FAILED"
                self.reporter.emit("PREPROCESSING", "failed", f"{image.original_filename or image.id} could not be read")
                continue

            image.width_px = prepared["width"]
            image.height_px = prepared["height"]
            panels.append(
                {
                    "image_id": image.id,
                    "image_order": order,
                    "panel": image.panel,
                    "prepared": prepared,
                    "image": prepared["original"],
                    "regions": [],
                }
            )

        db.flush()
        if not panels:
            self.reporter.failed("PREPROCESSING", "No image could be prepared for reading")
            return {"panels": [], "error": "No usable image could be prepared"}

        self.reporter.completed("PREPROCESSING", f"{len(panels)} image(s) prepared")
        return {"panels": panels}

    def run_ocr(self, state: PipelineState):
        panels = state.get("panels") or []
        if not panels:
            return {"regions": []}

        db = self.db
        db.query(OCRTextRegions).filter(OCRTextRegions.inspection_id == state["inspection_id"]).delete()
        db.flush()

        self.reporter.started("OCR", "Reading text with PaddleOCR")
        all_regions = []
        for panel in panels:
            image = db.query(InspectionImages).filter(InspectionImages.id == panel["image_id"]).first()
            result = ocr.run(panel["prepared"])
            image.ocr_status = result["status"]
            image.mean_ocr_confidence = result["mean_confidence"]

            stored = []
            for region in result["regions"]:
                record = OCRTextRegions(
                    image_id=panel["image_id"],
                    inspection_id=state["inspection_id"],
                    text=region["text"],
                    confidence=region["confidence"],
                    polygon=region["polygon"],
                    x1=region["x1"],
                    y1=region["y1"],
                    x2=region["x2"],
                    y2=region["y2"],
                    reading_order=region["reading_order"],
                )
                db.add(record)
                db.flush()
                enriched = dict(region)
                enriched["id"] = record.id
                enriched["image_id"] = panel["image_id"]
                enriched["image_order"] = panel["image_order"]
                stored.append(enriched)

            panel["regions"] = stored
            all_regions.extend(stored)

        db.flush()
        if not all_regions:
            self.reporter.failed("OCR", "No readable text was found on the uploaded images")
            return {"regions": [], "error": "OCR found no text"}

        self.reporter.completed("OCR", f"{len(all_regions)} text region(s) extracted", regions=len(all_regions))
        return {"regions": all_regions}

    def normalize_ocr(self, state: PipelineState):
        regions = state.get("regions") or []
        label_text = "\n".join(extraction.lines_from(regions))
        return {"label_text": label_text}

    def extract_declarations(self, state: PipelineState):
        regions = state.get("regions") or []
        if not regions:
            return {"declarations": {}}

        self.reporter.started("DECLARATION_EXTRACTION", "Converting label text into declarations")
        result = extraction.run(regions)
        declarations = result["facts"]

        panels = state.get("panels") or []
        measurements = vision.analyse(panels) if panels else {"facts": {}, "signals": {}}
        declarations.update(measurements["facts"])

        self.persist_facts(state["inspection_id"], declarations)
        self.reporter.completed(
            "DECLARATION_EXTRACTION",
            f"{len(declarations)} declaration field(s) extracted",
            development_mode=result["development_mode"],
        )
        return {"declarations": declarations, "development_mode": result["development_mode"]}

    def persist_facts(self, inspection_id: str, declarations: dict):
        db = self.db
        existing = {
            row.fact_path: row
            for row in db.query(ExtractedFacts).filter(ExtractedFacts.inspection_id == inspection_id).all()
        }
        for path, fact in declarations.items():
            row = existing.get(path)
            if row is None:
                row = ExtractedFacts(inspection_id=inspection_id, fact_path=path)
                db.add(row)
            elif row.verification_status == "VERIFIED":
                row.ai_value = fact.get("value")
                row.ai_confidence = fact.get("confidence")
                continue

            row.ai_value = fact.get("value")
            row.ai_confidence = fact.get("confidence")
            row.extractor = fact.get("extractor")
            row.image_id = fact.get("image_id")
            row.region_id = fact.get("region_id")
            row.bbox = fact.get("bbox")
        db.flush()

    def classify_product(self, state: PipelineState):
        db = self.db
        self.reporter.started("PRODUCT_CLASSIFICATION", "Identifying the commodity")
        result = classify.run(state.get("label_text", ""), state.get("declarations") or {})

        record = db.query(Products).filter(Products.inspection_id == state["inspection_id"]).first()
        if record is None:
            record = Products(inspection_id=state["inspection_id"])
            db.add(record)

        record.brand = result["brand"]
        record.common_name = result["common_name"]
        record.category = result["category"]
        record.tags = result["tags"]
        record.physical_state = result["physical_state"]
        record.classification_confidence = result["confidence"]
        record.classification_source = result["source"]
        db.flush()

        message = f"Classified as {result['category']}"
        if result["needs_review"]:
            message += " (low confidence, flagged for review)"
        self.reporter.completed("PRODUCT_CLASSIFICATION", message, tags=result["tags"], confidence=result["confidence"])
        return {"classification": result}

    def determine_applicable_rules(self, state: PipelineState):
        db = self.db
        inspection = db.query(Inspections).filter(Inspections.id == state["inspection_id"]).first()
        self.reporter.started("RULE_IDENTIFICATION", "Selecting the provisions in force")
        ruleset, tables = load_rule_data(db, inspection.rule_set_version)
        active = [r for r in ruleset["rules"] if r["status"] == "active"]
        self.reporter.completed(
            "RULE_IDENTIFICATION",
            f"{len(active)} rule(s) from {ruleset['rule_set_version']} considered",
            rule_set_version=ruleset["rule_set_version"],
        )
        return {"ruleset": ruleset, "tables": tables}

    def evaluate_compliance(self, state: PipelineState):
        db = self.db
        inspection = db.query(Inspections).filter(Inspections.id == state["inspection_id"]).first()
        product = db.query(Products).filter(Products.inspection_id == inspection.id).first()

        self.reporter.started("COMPLIANCE_ANALYSIS", "Evaluating declarations against the rules")
        raw_facts = fact_builder.build(db, inspection, product)

        try:
            report = rule_engine.run(
                raw_facts,
                on_date=inspection.judged_as_of,
                ruleset=state.get("ruleset"),
                tables=state.get("tables"),
            )
        except Exception as error:
            logger.exception("Rule engine failed")
            self.reporter.failed("COMPLIANCE_ANALYSIS", "Deterministic evaluation could not run")
            return {"degraded_mode": True, "error": f"Rule engine failed: {error}"}

        self.store_results(inspection, report, state.get("run_no", 1))
        counts = report["counts"]
        self.reporter.completed(
            "COMPLIANCE_ANALYSIS",
            f"{counts['NON_COMPLIANT']} violation(s), {counts['REQUIRES_VERIFICATION']} to verify",
            verdict=report["automated_verdict"],
            counts=counts,
        )
        return {"report": report}

    def store_results(self, inspection: Inspections, report: dict, run_no: int):
        db = self.db
        db.query(Evidence).filter(
            Evidence.violation_id.in_(
                db.query(Violations.id).filter(Violations.inspection_id == inspection.id)
            )
        ).delete(synchronize_session=False)
        db.query(Violations).filter(Violations.inspection_id == inspection.id).delete()
        db.query(RuleResults).filter(RuleResults.inspection_id == inspection.id).delete()
        db.flush()

        rule_index = {
            (row.rule_id, row.version): row
            for row in db.query(Rules).filter(Rules.rule_set_version == inspection.rule_set_version).all()
        }

        for entry in report["results"]:
            result = RuleResults(
                inspection_id=inspection.id,
                rule_id=entry["rule_id"],
                rule_version=entry["version"],
                run_no=run_no,
                title=entry["title"],
                provision=entry["provision"],
                severity=entry["severity"],
                verification_mode=entry["verification_mode"],
                threshold_source=entry["threshold_source"],
                status=entry["status"],
                queue=entry.get("queue"),
                reason=entry.get("reason"),
                exemption_ref=entry.get("exemption_ref"),
                missing_facts=entry.get("missing_facts", []),
                low_conf_facts=entry.get("low_confidence_facts", []),
                assumptions=entry.get("assumptions", []),
                notes=entry.get("notes", []),
                evidence=entry.get("evidence", []),
            )
            db.add(result)
            db.flush()

            if entry["status"] != "NON_COMPLIANT":
                continue

            rule = rule_index.get((entry["rule_id"], entry["version"]))
            provision = rule.provision if rule else {}
            observed = {item["fact"]: item["value"] for item in entry.get("evidence", [])}
            confidences = [item.get("confidence", 1.0) for item in entry.get("evidence", [])]

            violation = Violations(
                inspection_id=inspection.id,
                result_id=result.id,
                rule_id=entry["rule_id"],
                rule_version=entry["version"],
                title=entry["title"],
                provision=entry["provision"],
                severity=entry["severity"],
                confidence=round(min(confidences), 3) if confidences else None,
                observed_value=observed,
                expected=entry["title"],
                legal_requirement=provision.get("text_excerpt"),
                source_reference=f"Rule {entry['provision']}"
                + (f", page {provision.get('pdf_page')}" if provision.get("pdf_page") else ""),
            )
            db.add(violation)

        inspection.automated_verdict = report["automated_verdict"]
        db.flush()

    def generate_evidence(self, state: PipelineState):
        db = self.db
        if state.get("degraded_mode"):
            return {}

        self.reporter.started("EVIDENCE_GENERATION", "Linking findings to image regions")
        violations = db.query(Violations).filter(Violations.inspection_id == state["inspection_id"]).all()
        region_index = {
            row.id: row
            for row in db.query(OCRTextRegions).filter(
                OCRTextRegions.inspection_id == state["inspection_id"]
            ).all()
        }
        fact_index = {
            row.fact_path: row
            for row in db.query(ExtractedFacts).filter(
                ExtractedFacts.inspection_id == state["inspection_id"]
            ).all()
        }

        created = 0
        rule_index = {
            (row.rule_id, row.version): row
            for row in db.query(Rules).all()
        }

        for violation in violations:
            result = db.query(RuleResults).filter(RuleResults.id == violation.result_id).first()
            paths = [item["fact"] for item in (result.evidence or [])]
            missing = list(result.missing_facts or [])

            if not missing:
                rule = rule_index.get((result.rule_id, result.rule_version))
                if rule is not None:
                    candidates = dict.fromkeys(fact_paths_in(rule.check_expr))
                    missing = [
                        path for path in candidates
                        if path not in fact_index or fact_index[path].ai_value in (None, "", [])
                    ]

            for path in paths:
                row = fact_index.get(path)
                if row is None:
                    continue
                region = region_index.get(row.region_id) if row.region_id else None
                db.add(
                    Evidence(
                        violation_id=violation.id,
                        image_id=row.image_id,
                        region_id=row.region_id,
                        fact_path=path,
                        observed_text=region.text if region else None,
                        kind="OCR_REGION" if region else "DECLARATION",
                    )
                )
                created += 1

            for path in missing:
                db.add(
                    Evidence(
                        violation_id=violation.id,
                        fact_path=path,
                        kind="ABSENT_DECLARATION",
                        note="Declaration was looked for on every usable panel and not found",
                    )
                )
                created += 1

        db.flush()
        self.reporter.completed("EVIDENCE_GENERATION", f"{created} evidence item(s) linked")
        return {}

    def generate_report_data(self, state: PipelineState):
        db = self.db
        inspection = db.query(Inspections).filter(Inspections.id == state["inspection_id"]).first()
        inspection.development_mode = bool(state.get("development_mode"))
        inspection.degraded_mode = bool(state.get("degraded_mode"))
        inspection.processing_error = state.get("error")
        db.flush()
        self.reporter.completed("REPORT_GENERATION", "Inspection ready for review")
        return {}
