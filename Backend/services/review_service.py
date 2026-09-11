from fastapi import HTTPException
from sqlalchemy import func
from models import (
    ExtractedFacts,
    RuleResults,
    Violations,
    Evidence,
    OCRTextRegions,
    Products,
    Users,
)
from schemas import DeclarationOut, RuleOut, FindingOut, EvidenceOut, ComplianceSummary
from services import inspection_service, audit_service
from pipeline import extraction, facts as fact_builder
from datetime import datetime, timezone

AUTOMATED_MODES = {"LABEL_AUTOMATED", "VISION_AUTOMATED"}

CATEGORY_BY_PREFIX = [
    ("Mandatory declarations", ("6(1)", "6(2)", "6(3)", "6(5)", "4", "25")),
    ("Manufacturer information", ("10(", "6(1)(a)")),
    ("Quantity compliance", ("11(", "12(", "13(", "14", "16", "17", "19(", "21(", "5")),
    ("Price compliance", ("2(m)", "8(2)", "18(")),
    ("Date information", ("6(1)(d)",)),
    ("Display and legibility", ("7(", "8(1)", "9(")),
    ("Wholesale and registration", ("24(", "27", "31")),
]


def category_for(provision: str) -> str:
    text = provision or ""
    for label, prefixes in CATEGORY_BY_PREFIX:
        if any(text.startswith(prefix) for prefix in prefixes):
            return label
    return "Other applicable requirements"


def latest_run(db, inspection_id: str) -> int:
    value = db.query(func.max(RuleResults.run_no)).filter(
        RuleResults.inspection_id == inspection_id
    ).scalar()
    return value or 1


def results_for(db, inspection_id: str):
    run_no = latest_run(db, inspection_id)
    return (
        db.query(RuleResults)
        .filter(RuleResults.inspection_id == inspection_id, RuleResults.run_no == run_no)
        .all()
    )


def declarations(db, inspection_id: str):
    rows = (
        db.query(ExtractedFacts)
        .filter(ExtractedFacts.inspection_id == inspection_id)
        .order_by(ExtractedFacts.fact_path)
        .all()
    )
    output = []
    for row in rows:
        if row.fact_path not in extraction.LABELS or row.fact_path == "label.full_text":
            continue
        output.append(
            DeclarationOut(
                fact_path=row.fact_path,
                label=extraction.LABELS.get(row.fact_path, row.fact_path),
                ai_value=row.ai_value,
                ai_confidence=row.ai_confidence,
                human_value=row.human_value,
                effective_value=fact_builder.effective_value(row),
                verification_status=row.verification_status,
                extractor=row.extractor,
                image_id=row.image_id,
                region_id=row.region_id,
                bbox=row.bbox,
                verified_at=row.verified_at,
            )
        )
    return output


def patch_declarations(inspection_id: str, edits, db, user):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection_service.assert_not_finalized(inspection)

    for edit in edits:
        row = (
            db.query(ExtractedFacts)
            .filter(
                ExtractedFacts.inspection_id == inspection_id,
                ExtractedFacts.fact_path == edit.fact_path,
            )
            .first()
        )
        if row is None:
            row = ExtractedFacts(
                inspection_id=inspection_id,
                fact_path=edit.fact_path,
                extractor="inspector",
            )
            db.add(row)

        previous = {"human_value": row.human_value, "verification_status": row.verification_status}
        row.human_value = edit.human_value
        row.verification_status = edit.verification_status
        row.verified_by = user.user_id
        row.verified_at = datetime.now(timezone.utc)

        audit_service.record(
            db,
            inspection_id,
            user.user_id,
            "declaration_edited",
            edit.fact_path,
            {"ai_value": row.ai_value, **previous},
            {"human_value": edit.human_value, "verification_status": edit.verification_status},
        )

    db.commit()
    return declarations(db, inspection_id)


def confirm_declarations(inspection_id: str, db, user, reevaluate):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection_service.assert_not_finalized(inspection)

    reevaluate(db, inspection)
    audit_service.record(db, inspection_id, user.user_id, "declarations_confirmed")

    product = inspection_service.get_product(db, inspection_id)
    needs_classification = product is None or (product.classification_confidence or 0) < 0.6
    target = "CLASSIFICATION_REVIEW" if needs_classification else "RULE_REVIEW"
    inspection_service.advance_to(db, inspection, target)
    db.commit()
    return {"message": "Declarations confirmed", "status": inspection.status}


def override_product(inspection_id: str, data, db, user, reevaluate):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection_service.assert_not_finalized(inspection)

    product = db.query(Products).filter(Products.inspection_id == inspection_id).first()
    if product is None:
        raise HTTPException(404, "This inspection has no classification yet")

    previous = {"tags": product.tags, "category": product.category, "physical_state": product.physical_state}
    product.human_override_tags = data.tags
    if data.category:
        product.category = data.category
    if data.physical_state:
        product.physical_state = data.physical_state
    product.overridden_by = user.user_id
    product.overridden_at = datetime.now(timezone.utc)

    audit_service.record(
        db, inspection_id, user.user_id, "classification_overridden", None, previous,
        {"tags": data.tags, "category": data.category, "physical_state": data.physical_state},
    )
    reevaluate(db, inspection)
    inspection_service.advance_to(db, inspection, "RULE_REVIEW")
    db.commit()
    db.refresh(product)
    return product


def why_it_applies(result: RuleResults) -> str:
    if result.status == "NOT_APPLICABLE":
        return "Scope conditions for this provision are not met by this package"
    if result.status == "EXEMPT":
        return f"Exempt under {result.exemption_ref}" if result.exemption_ref else "Exempt"
    if result.assumptions:
        return "; ".join(str(a) for a in result.assumptions[:2])
    return "Package falls within the scope of this provision"


def rules(db, inspection_id: str, include_not_applicable: bool = False):
    output = []
    for result in results_for(db, inspection_id):
        if not include_not_applicable and result.status == "NOT_APPLICABLE":
            continue
        output.append(
            RuleOut(
                rule_id=result.rule_id,
                rule_version=result.rule_version,
                title=result.title,
                provision=result.provision,
                severity=result.severity,
                verification_mode=result.verification_mode,
                threshold_source=result.threshold_source,
                status=result.status,
                queue=result.queue,
                reason=result.reason,
                exemption_ref=result.exemption_ref,
                machine_checkable=result.verification_mode in AUTOMATED_MODES,
                why_it_applies=why_it_applies(result),
                officer_decision=result.officer_decision,
            )
        )
    output.sort(key=lambda r: (r.status != "NON_COMPLIANT", r.status != "REQUIRES_VERIFICATION", r.provision or ""))
    return output


def patch_rules(inspection_id: str, decisions, db, user):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection_service.assert_not_finalized(inspection)
    run_no = latest_run(db, inspection_id)

    for decision in decisions:
        result = (
            db.query(RuleResults)
            .filter(
                RuleResults.inspection_id == inspection_id,
                RuleResults.rule_id == decision.rule_id,
                RuleResults.rule_version == decision.rule_version,
                RuleResults.run_no == run_no,
            )
            .first()
        )
        if result is None:
            raise HTTPException(404, f"{decision.rule_id} was not evaluated on this inspection")

        previous = result.officer_decision
        result.officer_decision = decision.officer_decision
        result.officer_note = decision.officer_note
        audit_service.record(
            db, inspection_id, user.user_id, "rule_decision", f"{decision.rule_id} v{decision.rule_version}",
            {"officer_decision": previous},
            {"officer_decision": decision.officer_decision, "note": decision.officer_note},
        )

    inspection_service.advance_to(db, inspection, "COMPLIANCE_REVIEW")
    db.commit()
    return rules(db, inspection_id)


def evidence_out(items):
    output = []
    for item in items:
        region = item.region
        output.append(
            EvidenceOut(
                id=item.id,
                image_id=item.image_id,
                region_id=item.region_id,
                fact_path=item.fact_path,
                observed_text=item.observed_text,
                kind=item.kind,
                note=item.note,
                x1=region.x1 if region else None,
                y1=region.y1 if region else None,
                x2=region.x2 if region else None,
                y2=region.y2 if region else None,
                polygon=region.polygon if region else None,
            )
        )
    return output


def findings(db, inspection_id: str):
    output = []
    violations = (
        db.query(Violations)
        .filter(Violations.inspection_id == inspection_id)
        .order_by(Violations.severity)
        .all()
    )
    for violation in violations:
        result = db.query(RuleResults).filter(RuleResults.id == violation.result_id).first()
        output.append(
            FindingOut(
                id=violation.id,
                kind="VIOLATION",
                rule_id=violation.rule_id,
                rule_version=violation.rule_version,
                title=violation.title,
                provision=violation.provision,
                severity=violation.severity,
                confidence=violation.confidence,
                status="NON_COMPLIANT",
                reason=result.reason if result else None,
                observed_value=violation.observed_value,
                expected=violation.expected,
                legal_requirement=violation.legal_requirement,
                source_reference=violation.source_reference,
                llm_explanation=violation.llm_explanation,
                officer_decision=violation.officer_decision,
                officer_reason=violation.officer_reason,
                evidence=evidence_out(violation.evidence_items),
                missing_facts=list(result.missing_facts or []) if result else [],
                threshold_source=result.threshold_source if result else None,
                verification_mode=result.verification_mode if result else None,
            )
        )

    for result in results_for(db, inspection_id):
        if result.status != "REQUIRES_VERIFICATION":
            continue
        output.append(
            FindingOut(
                id=result.id,
                kind="RESULT",
                rule_id=result.rule_id,
                rule_version=result.rule_version,
                title=result.title,
                provision=result.provision,
                severity=result.severity,
                status=result.status,
                queue=result.queue,
                reason=result.reason,
                llm_suggested_status=result.llm_suggested_status,
                llm_reason=result.llm_reason,
                llm_confidence=result.llm_confidence,
                officer_decision=result.officer_decision,
                officer_reason=result.officer_note,
                missing_facts=list(result.missing_facts or []) + list(result.low_conf_facts or []),
                threshold_source=result.threshold_source,
                verification_mode=result.verification_mode,
            )
        )
    return output


def patch_finding(inspection_id: str, finding_id: str, data, db, user):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection_service.assert_not_finalized(inspection)

    violation = (
        db.query(Violations)
        .filter(Violations.id == finding_id, Violations.inspection_id == inspection_id)
        .first()
    )
    if violation is not None:
        previous = violation.officer_decision
        violation.officer_decision = data.officer_decision
        violation.officer_reason = data.officer_reason
        violation.decided_by = user.user_id
        violation.decided_at = datetime.now(timezone.utc)
        audit_service.record(
            db, inspection_id, user.user_id, "violation_decision", f"{violation.rule_id} v{violation.rule_version}",
            {"officer_decision": previous},
            {"officer_decision": data.officer_decision, "reason": data.officer_reason},
        )
        inspection_service.advance_to(db, inspection, "VIOLATION_REVIEW")
        db.commit()
        return findings(db, inspection_id)

    result = (
        db.query(RuleResults)
        .filter(RuleResults.id == finding_id, RuleResults.inspection_id == inspection_id)
        .first()
    )
    if result is None:
        raise HTTPException(404, "Finding not found on this inspection")

    previous = result.officer_decision
    result.officer_decision = data.officer_decision
    result.officer_note = data.officer_reason
    source = "LLM_SUGGESTION_ACCEPTED" if (
        data.officer_decision == "CONFIRMED" and result.llm_suggested_status
    ) else "INSPECTOR"
    audit_service.record(
        db, inspection_id, user.user_id, "verification_decision", f"{result.rule_id} v{result.rule_version}",
        {"officer_decision": previous, "llm_suggested_status": result.llm_suggested_status},
        {"officer_decision": data.officer_decision, "reason": data.officer_reason},
        source=source,
    )
    inspection_service.advance_to(db, inspection, "VIOLATION_REVIEW")
    db.commit()
    return findings(db, inspection_id)


def summary(db, inspection_id: str, inspection):
    results = results_for(db, inspection_id)
    violations = db.query(Violations).filter(Violations.inspection_id == inspection_id).all()
    overturned = {v.result_id for v in violations if v.officer_decision == "OVERTURNED"}

    counts = {"COMPLIANT": 0, "NON_COMPLIANT": 0, "REQUIRES_VERIFICATION": 0, "NOT_APPLICABLE": 0, "EXEMPT": 0, "OBSERVATION": 0}
    grouped = {}
    manual = 0

    for result in results:
        status = result.status
        if status == "NON_COMPLIANT" and result.id in overturned:
            status = "REQUIRES_VERIFICATION"
        counts[status] = counts.get(status, 0) + 1
        if result.queue == "MANUAL_CHECKLIST":
            manual += 1
        if status in ("NOT_APPLICABLE",):
            continue
        bucket = grouped.setdefault(category_for(result.provision), {"category": category_for(result.provision), "passed": 0, "failed": 0, "review": 0, "exempt": 0})
        if status == "COMPLIANT":
            bucket["passed"] += 1
        elif status == "NON_COMPLIANT":
            bucket["failed"] += 1
        elif status == "EXEMPT":
            bucket["exempt"] += 1
        else:
            bucket["review"] += 1

    return ComplianceSummary(
        automated_verdict=inspection.automated_verdict,
        final_verdict=inspection.final_verdict,
        counts=counts,
        by_category=sorted(grouped.values(), key=lambda b: b["category"]),
        open_manual_checklist=manual,
        rules_evaluated=len(results),
    )


def compute_final_verdict(db, inspection_id: str) -> str:
    violations = db.query(Violations).filter(Violations.inspection_id == inspection_id).all()
    confirmed = [v for v in violations if v.officer_decision != "OVERTURNED"]
    if confirmed:
        return "NON_COMPLIANT"

    unresolved = [
        r for r in results_for(db, inspection_id)
        if r.status == "REQUIRES_VERIFICATION" and r.officer_decision not in ("ACCEPTED", "CONFIRMED", "REMOVED")
    ]
    if unresolved:
        return "REQUIRES_REVIEW"
    return "COMPLIANT"


def finalize(inspection_id: str, data, db, user):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection_service.assert_not_finalized(inspection)

    if not results_for(db, inspection_id):
        raise HTTPException(400, "This inspection has not been processed yet")

    pending = (
        db.query(Violations)
        .filter(Violations.inspection_id == inspection_id, Violations.officer_decision == "PENDING")
        .count()
    )
    if pending:
        raise HTTPException(400, f"{pending} violation(s) still need an accept or reject decision")

    if data and data.inspector_observations is not None:
        inspection.inspector_observations = data.inspector_observations

    inspection.final_verdict = compute_final_verdict(db, inspection_id)
    inspection_service.mark_finalized(db, inspection)
    audit_service.record(
        db, inspection_id, user.user_id, "inspection_finalized", None, None,
        {"final_verdict": inspection.final_verdict},
    )
    db.commit()
    db.refresh(inspection)
    return inspection
