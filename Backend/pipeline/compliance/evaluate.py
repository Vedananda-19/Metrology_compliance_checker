from engine import engine as rule_engine
from pipeline.normalization import declarations as normalization
from datetime import date

STATUS_MAP = {
    "COMPLIANT": "COMPLIANT",
    "NON_COMPLIANT": "NON_COMPLIANT",
    "REQUIRES_VERIFICATION": "NOT_VERIFIABLE",
    "EXEMPT": "EXEMPT",
    "OBSERVATION": "OBSERVATION",
}
SHOWN = {"NON_COMPLIANT", "NOT_VERIFIABLE", "COMPLIANT", "EXEMPT", "OBSERVATION"}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


def _display(path: str, facts: dict) -> str | None:
    if path == "net_quantity.text":
        value = facts.get("net_quantity.value")
        unit = facts.get("net_quantity.unit")
        if isinstance(value, dict):
            suffix = f" {unit['value']}" if isinstance(unit, dict) else ""
            return f"Net quantity: {value['value']}{suffix}"
    if path == "mrp.text":
        value = facts.get("mrp.value")
        if isinstance(value, dict):
            return f"MRP: Rs {value['value']}"
    if isinstance(facts.get(path), dict):
        return f"{normalization.label_for(path)}: {facts[path]['value']}"
    return None


def observed_for(entry, facts: dict) -> str | None:
    used = [item["fact"] for item in entry.get("evidence", [])]
    parts = [display for p in used if (display := _display(p, facts))]
    if parts:
        return "; ".join(parts[:3])
    absent = entry.get("missing_facts") or []
    if absent:
        return "Not found on any panel: " + ", ".join(normalization.label_for(p) for p in absent[:3])
    return None


def explain(entry) -> str:
    if entry["status"] == "NON_COMPLIANT":
        return entry.get("reason") or "The package does not meet this requirement."
    if entry["status"] == "REQUIRES_VERIFICATION":
        return entry.get("reason") or "This requirement could not be decided from the uploaded images."
    if entry["status"] == "EXEMPT":
        return f"Exempt under {entry.get('exemption_ref')}." if entry.get("exemption_ref") else "Exempt."
    return "The package meets this requirement."


def summarise(report: dict) -> str:
    counts = report["counts"]
    verdict = report["automated_verdict"]
    if verdict == "NON_COMPLIANT":
        lead = f"{counts['NON_COMPLIANT']} requirement(s) were not met."
    elif verdict == "REQUIRES_VERIFICATION":
        lead = "No violation was found, but some requirements could not be decided from the images."
    elif verdict == "EXEMPT":
        lead = "The package is exempt from these Rules."
    else:
        lead = "Every requirement that could be checked was met."
    return (
        f"{lead} {counts['COMPLIANT']} passed, {counts['REQUIRES_VERIFICATION']} need verification, "
        f"{counts['EXEMPT']} exempt and {counts['NOT_APPLICABLE']} did not apply, "
        f"out of {report['rules_evaluated']} rules in force."
    )


def evaluate(values: dict, panel_count: int, ocr_text: str) -> dict:
    facts = normalization.build_facts(values, panel_count, ocr_text)
    report = rule_engine.run(facts, on_date=date.today())

    findings = []
    for entry in report["results"]:
        status = STATUS_MAP.get(entry["status"])
        if status not in SHOWN:
            continue
        findings.append(
            {
                "rule_id": entry["rule_id"],
                "rule_ref": entry["provision"],
                "requirement": entry["title"],
                "status": status,
                "severity": entry["severity"],
                "verification_mode": entry["verification_mode"],
                "threshold_source": entry["threshold_source"],
                "observed": observed_for(entry, facts),
                "explanation": explain(entry),
            }
        )

    findings.sort(key=lambda f: (f["status"] != "NON_COMPLIANT", SEVERITY_ORDER.get(f["severity"], 9)))

    return {
        "verdict": report["automated_verdict"],
        "summary": summarise(report),
        "rule_set_version": report["rule_set_version"],
        "counts": report["counts"],
        "rules_evaluated": report["rules_evaluated"],
        "findings": findings,
    }
