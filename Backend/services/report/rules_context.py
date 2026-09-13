from functools import lru_cache
from pathlib import Path

from engine import engine as rule_engine

DIGEST_PATH = Path(__file__).with_name("rules_digest.txt")

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


def text_block(rule_ids) -> str:
    """The official text of the named rules, laid out for a prompt."""
    lines = []
    for provision in provisions_for(rule_ids):
        number = provision.get("rule") or provision["rule_id"]
        lines.append(f"[{provision['rule_id']}] Rule {number} — {provision['title']}\n{provision['text']}")
    return "\n\n".join(lines)


@lru_cache(maxsize=1)
def rules_digest() -> str:
    """Every rule of Chapter II in brief - the background a flagged rule sits in."""
    try:
        return DIGEST_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
