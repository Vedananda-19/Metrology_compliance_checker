from fastapi.testclient import TestClient
from pathlib import Path
import sys

from main import app
from database import SessionLocal
from models import ExtractedFacts, AuditLogs, Violations, RuleResults
from services import processing_service

LABELS = Path(__file__).resolve().parent / "demo" / "labels"
client = TestClient(app)
failures = []


def check(condition, message):
    if condition:
        print(f"  ok    {message}")
    else:
        failures.append(message)
        print(f"  FAIL  {message}")


def auth_headers(username: str):
    client.post("/auth/register", json={
        "username": username, "password": "inspector123", "confirmPassword": "inspector123",
        "full_name": "R. Sharma", "designation": "Legal Metrology Officer", "office": "Pune Division",
    })
    response = client.post("/auth/login", data={"username": username, "password": "inspector123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def upload(inspection_id, headers, names):
    files = [("files", (n, (LABELS / n).read_bytes(), "image/png")) for n in names]
    return client.post(f"/inspections/{inspection_id}/images", headers=headers, files=files)


def run_product(headers, prefix, label):
    print(f"\n--- {label} ---")
    created = client.post("/inspections", headers=headers, json={"title": label, "location": "Market Yard, Pune"})
    check(created.status_code == 200, f"inspection created ({created.status_code})")
    inspection_id = created.json()["id"]
    print(f"  reference: {created.json()['reference']}")

    response = upload(inspection_id, headers, [f"{prefix}_front.png", f"{prefix}_back.png"])
    check(response.status_code == 200 and len(response.json()) == 2, "two images uploaded")
    images = response.json()

    order = [images[1]["id"], images[0]["id"]]
    reordered = client.patch(f"/inspections/{inspection_id}/images/order", headers=headers, json={"image_ids": order})
    check(reordered.status_code == 200 and reordered.json()[0]["id"] == order[0], "images reordered")
    client.patch(f"/inspections/{inspection_id}/images/order", headers=headers, json={"image_ids": [images[0]["id"], images[1]["id"]]})

    for image in images:
        client.patch(f"/inspections/{inspection_id}/images/{image['id']}", headers=headers,
                     json={"usability": "USABLE", "panel": "front" if "front" in image["original_filename"] else "back"})
    verified = client.post(f"/inspections/{inspection_id}/verify-images", headers=headers)
    check(verified.status_code == 200, "images verified")

    db = SessionLocal()
    from models import Inspections
    inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
    inspection.status = "PROCESSING"
    db.commit()
    db.close()

    processing_service.execute(inspection_id, None)

    detail = client.get(f"/inspections/{inspection_id}", headers=headers).json()
    check(detail["status"] == "EXTRACTION_REVIEW", f"status is {detail['status']}")
    check(detail["automated_verdict"] is not None, f"verdict {detail['automated_verdict']}")
    check(len(detail["processing_log"]) >= 8, f"{len(detail['processing_log'])} processing events logged")
    print(f"  product: {detail['product']['common_name']} | tags {detail['product']['tags']}")
    print(f"  counts:  {detail['summary']['counts']}")

    ocr = client.get(f"/inspections/{inspection_id}/ocr", headers=headers).json()
    regions = sum(len(entry["regions"]) for entry in ocr)
    check(regions > 10, f"{regions} OCR regions stored with boxes")

    declarations = client.get(f"/inspections/{inspection_id}/declarations", headers=headers).json()
    check(len(declarations) > 5, f"{len(declarations)} declarations extracted")

    findings = client.get(f"/inspections/{inspection_id}/findings", headers=headers).json()
    violations = [f for f in findings if f["kind"] == "VIOLATION"]
    open_items = [f for f in findings if f["kind"] == "RESULT"]
    print(f"  violations: {[f['rule_id'] + ' ' + f['provision'] for f in violations]}")
    check(len(open_items) > 0, f"{len(open_items)} requirements left as requires-verification")

    return inspection_id, declarations, findings, violations


def main():
    if not (LABELS / "biscuit_front.png").exists():
        print("run demo/make_labels.py first")
        sys.exit(1)

    headers = auth_headers("inspector")
    me = client.get("/auth/me", headers=headers)
    check(me.status_code == 200, "authenticated as inspector")
    check(client.get("/inspections").status_code == 401, "unauthenticated access rejected")

    shampoo_id, declarations, findings, violations = run_product(headers, "shampoo", "Aquapure shampoo")
    rules_hit = {f["rule_id"] for f in violations}
    check("LMPC-R6-1e-001" in rules_hit, "missing MRP raised under Rule 6(1)(e)")
    check("LMPC-R12-6-001" in rules_hit, "misleading quantity raised under Rule 12(6)")

    mrp_violation = next((f for f in violations if f["rule_id"] == "LMPC-R6-1e-001"), None)
    if mrp_violation:
        check(len(mrp_violation["evidence"]) > 0, f"MRP violation carries {len(mrp_violation['evidence'])} evidence item(s)")
    qty_violation = next((f for f in violations if f["rule_id"] == "LMPC-R12-6-001"), None)
    if qty_violation:
        boxed = [e for e in qty_violation["evidence"] if e.get("x1") is not None]
        check(len(boxed) > 0, "quantity violation points at a real OCR bounding box")

    print("\n--- human review preserves both values ---")
    response = client.patch(f"/inspections/{shampoo_id}/declarations", headers=headers, json={
        "edits": [{"fact_path": "net_quantity.text", "human_value": "Net Vol. 100 ml", "verification_status": "VERIFIED"}]
    })
    check(response.status_code == 200, "declaration edited")

    db = SessionLocal()
    row = db.query(ExtractedFacts).filter(
        ExtractedFacts.inspection_id == shampoo_id, ExtractedFacts.fact_path == "net_quantity.text"
    ).first()
    check(row.ai_value == "Net Vol. about 100 ml", f"AI value preserved: {row.ai_value!r}")
    check(row.human_value == "Net Vol. 100 ml", f"human value stored: {row.human_value!r}")
    check(row.verified_at is not None, "verified_at recorded")
    edit_log = db.query(AuditLogs).filter(
        AuditLogs.inspection_id == shampoo_id, AuditLogs.action == "declaration_edited"
    ).first()
    check(edit_log is not None and edit_log.old_value.get("ai_value") == "Net Vol. about 100 ml",
          "audit row holds both the model value and the correction")
    db.close()

    confirmed = client.post(f"/inspections/{shampoo_id}/declarations/confirm", headers=headers)
    check(confirmed.status_code == 200, f"declarations confirmed, status {confirmed.json().get('status')}")

    findings = client.get(f"/inspections/{shampoo_id}/findings", headers=headers).json()
    rules_hit = {f["rule_id"] for f in findings if f["kind"] == "VIOLATION"}
    check("LMPC-R12-6-001" not in rules_hit, "correcting 'about' cleared the misleading-quantity violation")
    check("LMPC-R6-1e-001" in rules_hit, "missing MRP still stands after re-evaluation")

    print("\n--- not-verifiable requirements are never compliant ---")
    rules = client.get(f"/inspections/{shampoo_id}/rules", headers=headers).json()
    measurement = [r for r in rules if r["verification_mode"] == "MEASUREMENT_REQUIRED"]
    check(all(r["status"] != "COMPLIANT" for r in measurement),
          f"{len(measurement)} measurement rules all left unverified")
    check(any(r["rule_id"].startswith("LMPC-R7-2") for r in measurement), "Rule 7 numeral height needs measurement")

    print("\n--- violation review and finalize ---")
    violations = [f for f in client.get(f"/inspections/{shampoo_id}/findings", headers=headers).json() if f["kind"] == "VIOLATION"]
    for violation in violations:
        client.patch(f"/inspections/{shampoo_id}/findings/{violation['id']}", headers=headers,
                     json={"officer_decision": "CONFIRMED", "officer_reason": "Verified against the package"})

    finalized = client.post(f"/inspections/{shampoo_id}/finalize", headers=headers,
                            json={"inspector_observations": "MRP absent on every panel photographed."})
    check(finalized.status_code == 200, f"finalized ({finalized.status_code})")
    check(finalized.json()["final_verdict"] == "NON_COMPLIANT", f"final verdict {finalized.json().get('final_verdict')}")

    blocked = client.patch(f"/inspections/{shampoo_id}/declarations", headers=headers, json={
        "edits": [{"fact_path": "mrp.value", "human_value": 99, "verification_status": "VERIFIED"}]
    })
    check(blocked.status_code == 409, f"finalized inspection rejects edits ({blocked.status_code})")

    pdf = client.get(f"/inspections/{shampoo_id}/report/pdf", headers=headers)
    check(pdf.status_code == 200 and pdf.content[:4] == b"%PDF", f"PDF generated ({len(pdf.content)} bytes)")
    Path("data/sample_report.pdf").write_bytes(pdf.content)

    report = client.get(f"/inspections/{shampoo_id}/report", headers=headers).json()
    check(len(report["audit_logs"]) >= 5, f"{len(report['audit_logs'])} audit entries in report")

    print("\n--- ownership isolation ---")
    other = auth_headers("inspector2")
    check(client.get(f"/inspections/{shampoo_id}", headers=other).status_code == 403,
          "another inspector cannot open this inspection")

    biscuit_id, _, biscuit_findings, biscuit_violations = run_product(headers, "biscuit", "Sunrise biscuits")
    biscuit_rules = {f["rule_id"] for f in biscuit_violations}
    check("LMPC-R6-1e-001" not in biscuit_rules, "compliant label does not raise a missing-MRP violation")

    history = client.get("/inspections", headers=headers).json()
    check(len(history) == 2, f"{len(history)} inspections in history")
    check(any(i["status"] == "FINALIZED" for i in history), "finalized inspection visible in history")

    print("\n" + "=" * 60)
    if failures:
        print(f"{len(failures)} CHECK(S) FAILED")
        for item in failures:
            print("  -", item)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
