import logging
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel
from pipeline import llm
from services.report import rules_context
from config import INFERENCE_PROVIDER, INFERENCE_API_KEY, INFERENCE_MODEL

logger = logging.getLogger(__name__)

DIGEST_PATH = Path(__file__).with_name("rules_digest.txt")


@lru_cache(maxsize=1)
def rules_digest() -> str:
    try:
        return DIGEST_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


class Justification(BaseModel):
    rule_id: str
    why: str


class Justifications(BaseModel):
    items: list[Justification]


SYSTEM_PROMPT = """You write the reasoning section of an official Legal Metrology compliance report for
an enforcement officer in India. A deterministic rule engine has already decided which declarations on
the package violate the Legal Metrology (Packaged Commodities) Rules, 2011. You do not decide
compliance and you never overturn the engine. Your only job is to explain, in clear plain English,
why each flagged item is a violation, grounded in the official rule text supplied to you.

- Write one or two short sentences per violation, about 30 to 45 words total. Say what the rule
  requires and why the package fails it. Be tight - this is a brief summary, not a paragraph.
- Use only the official rule text and the observed findings given to you. Do not cite rules that were
  not supplied and do not invent facts about the package.
- Write for a citizen who must understand the finding. Plain, factual, non-emotive."""


def _context_block(rule_ids) -> str:
    lines = []
    for provision in rules_context.provisions_for(rule_ids):
        number = provision.get("rule") or provision["rule_id"]
        lines.append(f"[{provision['rule_id']}] Rule {number} — {provision['title']}\n{provision['text']}")
    return "\n\n".join(lines)


def _fallback(findings) -> dict:
    return {finding["rule_id"]: finding.get("explanation") or "" for finding in findings}


def justify(findings: list[dict]) -> dict:
    if not findings:
        return {}

    if not INFERENCE_API_KEY:
        return _fallback(findings)

    rule_ids = [finding["rule_id"] for finding in findings]
    context = _context_block(rule_ids)

    observed = []
    for finding in findings:
        observed.append(
            f"[{finding['rule_id']}] {finding.get('rule_ref')} — {finding.get('requirement')}\n"
            f"Engine finding: {finding.get('explanation')}\n"
            f"Observed on package: {finding.get('observed') or 'not recorded'}"
        )

    digest = rules_digest()
    background = f"Background - the packaged-commodities rules in brief:\n\n{digest}\n\n" if digest else ""

    result = llm.invoke_structured(
        Justifications,
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                f"{background}Official rule text for the flagged rules (from the Rules, 2011):\n\n{context}\n\n"
                f"Findings the engine flagged:\n\n{chr(10).join(observed)}\n\n"
                "Return one justification per finding, keyed by its bracketed rule_id.",
            ),
        ],
        provider=INFERENCE_PROVIDER,
        api_key=INFERENCE_API_KEY,
        model=INFERENCE_MODEL,
    )

    if result is None:
        logger.warning("Justification LLM call failed, using engine explanations")
        return _fallback(findings)

    written = {item.rule_id.strip().strip("[]"): item.why.strip() for item in result.items if item.why.strip()}
    merged = _fallback(findings)
    for rule_id, why in written.items():
        if rule_id in merged:
            merged[rule_id] = why
    return merged
