from engine import engine as rule_engine

_by_rule_id = None


def _index():
    global _by_rule_id
    if _by_rule_id is None:
        ruleset = rule_engine.load_ruleset()
        _by_rule_id = {}
        for rule in ruleset["rules"]:
            provision = rule.get("provision", {})
            _by_rule_id[rule["rule_id"]] = {
                "rule": provision.get("rule"),
                "pdf_page": provision.get("pdf_page"),
                "title": rule.get("title"),
                "text": provision.get("text_excerpt", ""),
                "source": provision.get("source"),
            }
    return _by_rule_id


def provision_for(rule_id: str) -> dict | None:
    return _index().get(rule_id)


def provisions_for(rule_ids) -> list[dict]:
    seen = set()
    out = []
    for rule_id in rule_ids:
        if rule_id in seen:
            continue
        seen.add(rule_id)
        provision = provision_for(rule_id)
        if provision and provision["text"]:
            out.append({"rule_id": rule_id, **provision})
    return out
