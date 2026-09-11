from pydantic import BaseModel, Field
from models import RuleResults, ExtractedFacts, Rules, Inspections
from pipeline import llm, retrieval, extraction
from typing import Literal
import logging

logger = logging.getLogger(__name__)

OPEN_STATUS = "REQUIRES_VERIFICATION"
SETTLED_STATUSES = {"COMPLIANT", "NON_COMPLIANT", "NOT_APPLICABLE", "EXEMPT"}
SUGGESTABLE = ["NON_COMPLIANT", "REQUIRES_VERIFICATION", "NOT_APPLICABLE", "EXEMPT", "COMPLIANT"]

RECOVERY_PROMPT = """You are re-reading OCR text from a packaged commodity label because an automated
check could not find certain values the first time.

For each requested fact path, return the value only if the OCR text genuinely contains it.
Return null when the text does not contain it. A null is a correct and useful answer here:
the check treats an absent declaration as a legal finding, so a guessed value corrupts the record.
Copy values exactly as printed, keeping qualifier words such as 'about' or 'minimum'.
source_text must be the OCR line the value came from, copied verbatim."""

OPINION_PROMPT = """You are assisting a Legal Metrology inspector. A deterministic rule engine could not
decide one requirement because data was missing or unreadable.

Give your reading of the requirement against the facts supplied, and say plainly what is uncertain.
You are advisory only. Your answer is shown to the inspector as a suggestion and never decides the
inspection by itself. Cite only the provision text supplied to you. Do not invent rule numbers,
page numbers or requirements. If the facts do not support a conclusion, say REQUIRES_VERIFICATION."""


class RecoveredFact(BaseModel):
    fact_path: str = Field(description="The exact fact path requested")
    value: str | None = Field(default=None, description="Value read from the OCR text, or null")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_text: str | None = Field(default=None)


class RecoveredFacts(BaseModel):
    facts: list[RecoveredFact] = Field(default_factory=list)


class RuleOpinion(BaseModel):
    suggested_status: Literal["COMPLIANT", "NON_COMPLIANT", "REQUIRES_VERIFICATION", "NOT_APPLICABLE", "EXEMPT"]
    reason: str = Field(description="Two or three sentences, plain language, no invented citations")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


NUMERIC_PATHS = {
    "net_quantity.value": float,
    "mrp.value": float,
    "date_of_manufacture.month": int,
    "date_of_manufacture.year": int,
    "sheets.count": int,
    "package.capacity_cc": float,
}


def open_results(db, inspection_id: str, run_no: int):
    return (
        db.query(RuleResults)
        .filter(
            RuleResults.inspection_id == inspection_id,
            RuleResults.run_no == run_no,
            RuleResults.status == OPEN_STATUS,
        )
        .all()
    )


def missing_paths(results, vocabulary: dict):
    wanted = {}
    for result in results:
        for path in list(result.missing_facts or []) + list(result.low_conf_facts or []):
            if path.startswith(("measurement.", "registry.", "transaction.", "label.numeral", "label.min_letter", "label.pdp")):
                continue
            wanted.setdefault(path, describe(path, vocabulary))
    return wanted


def describe(path: str, vocabulary: dict):
    if path in vocabulary:
        return str(vocabulary[path])
    head = path.split(".")[0]
    for key, value in vocabulary.items():
        if key.startswith(head):
            return str(value)
    return extraction.LABELS.get(path, path)


def coerce_value(path: str, value):
    kind = NUMERIC_PATHS.get(path)
    if kind is None:
        return extraction.coerce(value, str)
    return extraction.coerce(value, kind)


def recover_facts(db, inspection, results, regions, label_text: str, vocabulary: dict):
    wanted = missing_paths(results, vocabulary)
    if not wanted:
        return 0

    listing = "\n".join(f"- {path}: {meaning}" for path, meaning in sorted(wanted.items()))
    messages = [
        ("system", RECOVERY_PROMPT),
        ("human", f"OCR text from every usable panel:\n\n{label_text}\n\nFact paths to look for:\n{listing}"),
    ]
    result = llm.invoke_structured(RecoveredFacts, messages)
    if result is None:
        return 0

    extractor = f"llm:fallback:recovery"
    recovered = 0
    for item in result.facts:
        if item.fact_path not in wanted or item.value is None:
            continue
        value = coerce_value(item.fact_path, item.value)
        if value is None:
            continue

        row = (
            db.query(ExtractedFacts)
            .filter(
                ExtractedFacts.inspection_id == inspection.id,
                ExtractedFacts.fact_path == item.fact_path,
            )
            .first()
        )
        if row is not None and row.verification_status == "VERIFIED":
            continue
        if row is None:
            row = ExtractedFacts(inspection_id=inspection.id, fact_path=item.fact_path)
            db.add(row)

        region = extraction.find_region(regions, item.source_text)
        row.ai_value = value
        row.ai_confidence = round(float(item.confidence or 0.6), 3)
        row.extractor = extractor
        if region is not None:
            row.region_id = region.get("id")
            row.image_id = region.get("image_id")
            row.bbox = [region["x1"], region["y1"], region["x2"], region["y2"]]
        recovered += 1

    db.flush()
    return recovered


def suggest_for_result(db, result: RuleResults, rule: Rules, available_facts: dict):
    passages = retrieval.context_for(db, result.provision or "", result.title or "")
    provision_text = "\n".join(
        f"Rule {p['rule_ref']}" + (f" (page {p['pdf_page']})" if p["pdf_page"] else "") + f": {p['text']}"
        for p in passages
    )
    facts_text = "\n".join(f"- {path}: {value}" for path, value in sorted(available_facts.items())) or "none extracted"
    unresolved = ", ".join(list(result.missing_facts or []) + list(result.low_conf_facts or [])) or "none recorded"

    messages = [
        ("system", OPINION_PROMPT),
        (
            "human",
            f"Requirement: {result.title}\n"
            f"Provision: Rule {result.provision}\n"
            f"Why the engine could not decide: {result.reason}\n"
            f"Data the engine could not obtain: {unresolved}\n\n"
            f"Provision text available to you:\n{provision_text}\n\n"
            f"Facts extracted from the package:\n{facts_text}",
        ),
    ]
    return llm.invoke_structured(RuleOpinion, messages)


def add_opinions(db, inspection, results, available_facts: dict, rule_index: dict, limit: int = 12):
    added = 0
    for result in results[:limit]:
        if result.status in SETTLED_STATUSES:
            continue
        rule = rule_index.get((result.rule_id, result.rule_version))
        opinion = suggest_for_result(db, result, rule, available_facts)
        if opinion is None:
            continue
        result.llm_suggested_status = opinion.suggested_status
        result.llm_reason = opinion.reason
        result.llm_confidence = round(float(opinion.confidence or 0.0), 3)
        added += 1
    db.flush()
    return added


def effective_facts(db, inspection_id: str):
    rows = db.query(ExtractedFacts).filter(ExtractedFacts.inspection_id == inspection_id).all()
    values = {}
    for row in rows:
        if row.fact_path == "label.full_text":
            continue
        value = row.human_value if (row.verification_status == "VERIFIED" and row.human_value is not None) else row.ai_value
        if value is not None:
            values[row.fact_path] = value
    return values


def run(db, inspection: Inspections, state: dict, reporter, reevaluate):
    if not llm.available():
        return {"skipped": True, "recovered": 0, "suggested": 0}

    run_no = state.get("run_no", 1)
    results = open_results(db, inspection.id, run_no)
    if not results:
        return {"skipped": False, "recovered": 0, "suggested": 0}

    vocabulary = (state.get("ruleset") or {}).get("fact_vocabulary", {})
    regions = state.get("regions") or []
    label_text = state.get("label_text", "")

    reporter.started("COMPLIANCE_ANALYSIS", f"{len(results)} requirement(s) undecided, asking the model to re-read the label")
    recovered = recover_facts(db, inspection, results, regions, label_text, vocabulary)

    if recovered:
        reporter.completed("COMPLIANCE_ANALYSIS", f"{recovered} value(s) recovered, re-running the rule engine")
        reevaluate()
        results = open_results(db, inspection.id, state.get("run_no", run_no))

    rule_index = {
        (row.rule_id, row.version): row
        for row in db.query(Rules).filter(Rules.rule_set_version == inspection.rule_set_version).all()
    }
    suggested = add_opinions(db, inspection, results, effective_facts(db, inspection.id), rule_index)
    if suggested:
        reporter.completed(
            "COMPLIANCE_ANALYSIS",
            f"{suggested} advisory suggestion(s) added for inspector review",
            advisory=True,
        )
    return {"skipped": False, "recovered": recovered, "suggested": suggested}


def degraded_assessment(db, inspection: Inspections, label_text: str):
    if not llm.available():
        return 0
    return 0
