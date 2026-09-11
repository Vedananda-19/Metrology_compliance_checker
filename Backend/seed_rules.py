from database import SessionLocal, Base, engine, enable_pgvector
from models import RuleSets, Rules, ReferenceTables, LegalProvisions
from engine import engine as rule_engine
from datetime import date
import hashlib
import json
import re


def parse_date(value):
    return date.fromisoformat(value) if value else None


def provision_id_for(rule_ref: str) -> str:
    return "LMPC2011:" + re.sub(r"\s+", " ", rule_ref).strip()


def seed_rule_set(db, ruleset, tables):
    version = ruleset["rule_set_version"]
    payload = json.dumps(ruleset, sort_keys=True) + json.dumps(tables, sort_keys=True)
    content_sha = hashlib.sha256(payload.encode()).hexdigest()

    record = db.query(RuleSets).filter(RuleSets.rule_set_version == version).first()
    if record is None:
        record = RuleSets(rule_set_version=version)
        db.add(record)

    record.rule_set_id = ruleset["rule_set_id"]
    record.title = ruleset["title"]
    record.legal_basis = ruleset.get("legal_basis")
    record.status = "published"
    record.macros = ruleset["macros"]
    record.fact_vocabulary = ruleset["fact_vocabulary"]
    record.content_sha256 = content_sha
    db.flush()
    return record


def seed_rules(db, ruleset):
    version = ruleset["rule_set_version"]
    count = 0
    for rule in ruleset["rules"]:
        record = (
            db.query(Rules)
            .filter(Rules.rule_id == rule["rule_id"], Rules.version == rule["version"])
            .first()
        )
        if record is None:
            record = Rules(rule_id=rule["rule_id"], version=rule["version"])
            db.add(record)

        record.rule_set_version = version
        record.status = rule["status"]
        record.title = rule["title"]
        record.category = rule.get("category")
        record.provision = rule["provision"]
        record.provision_id = provision_id_for(rule["provision"]["rule"])
        record.verification_mode = rule["verification_mode"]
        record.severity = rule["severity"]
        record.applies_when = rule["applies_when"]
        record.exempt_when = rule.get("exempt_when", [])
        record.check_expr = rule["check"]
        record.outcome_on_fail = rule["outcome_on_fail"]
        record.fail_message = rule.get("fail_message", "")
        record.evidence_facts = rule.get("evidence_facts", [])
        record.threshold_source = rule["threshold_source"]
        record.effective_from = parse_date(rule["effective_from"])
        record.effective_to = parse_date(rule.get("effective_to"))
        record.amendment_status = rule.get("amendment_status")
        record.notes = rule.get("notes")
        count += 1
    return count


def seed_reference_tables(db, version, tables):
    for name, data in tables.items():
        record = (
            db.query(ReferenceTables)
            .filter(
                ReferenceTables.rule_set_version == version,
                ReferenceTables.table_name == name,
            )
            .first()
        )
        if record is None:
            record = ReferenceTables(rule_set_version=version, table_name=name)
            db.add(record)
        record.data = data
    return len(tables)


def seed_provisions_from_rules(db, ruleset):
    seen = {}
    for rule in ruleset["rules"]:
        provision = rule["provision"]
        pid = provision_id_for(provision["rule"])
        excerpt = provision.get("text_excerpt", "")
        if pid in seen and len(excerpt) <= len(seen[pid].get("text_excerpt", "")):
            continue
        seen[pid] = provision

    for pid, provision in seen.items():
        record = db.query(LegalProvisions).filter(LegalProvisions.provision_id == pid).first()
        if record is None:
            record = LegalProvisions(provision_id=pid)
            db.add(record)
        elif record.text_source == "pdf_ocr":
            continue
        record.source = provision.get("source", "LMPC Rules 2011")
        record.rule_ref = provision["rule"]
        record.pdf_page = provision.get("pdf_page")
        record.text = provision.get("text_excerpt", "")
        record.text_source = "rule_excerpt"
    return len(seen)


def main():
    enable_pgvector()
    Base.metadata.create_all(bind=engine)

    ruleset = rule_engine.load_ruleset()
    tables = rule_engine.load_tables()

    db = SessionLocal()
    try:
        record = seed_rule_set(db, ruleset, tables)
        version, content_sha = record.rule_set_version, record.content_sha256
        rules = seed_rules(db, ruleset)
        reference = seed_reference_tables(db, version, tables)
        provisions = seed_provisions_from_rules(db, ruleset)
        db.commit()
    finally:
        db.close()

    print(f"rule set    : {version}  ({content_sha[:12]})")
    print(f"rules       : {rules}")
    print(f"ref tables  : {reference}")
    print(f"provisions  : {provisions} seeded from rule excerpts")
    print("run seed_provisions.py next to OCR the PDF and add full provision text")


if __name__ == "__main__":
    main()
