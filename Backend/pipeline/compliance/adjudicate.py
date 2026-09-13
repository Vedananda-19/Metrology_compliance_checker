"""Second opinion on the violations the deterministic engine raised.

The engine matches patterns, so it flags packages a careful reader would pass: an MRP printed
as "MRP (incl. of all taxes)" fails a pattern written for "inclusive of all taxes" although it
says exactly that. This pass re-reads every flagged violation against the official rule text and
withdraws the ones that are only a difference of wording, abbreviation or layout. It can never
raise a new violation - what is checked, and how, stays with the engine.

Cleared findings stay in the result as COMPLIANT, carrying the reason and the engine's original
wording, so the report and the officer can see what was withdrawn and why.
"""
import logging

from pydantic import BaseModel, Field

from config import INFERENCE_ENABLED, INFERENCE_PROVIDER, INFERENCE_API_KEY, INFERENCE_MODEL
from pipeline import llm
from pipeline.normalization import declarations as normalization
from services.report import rules_context

logger = logging.getLogger(__name__)

CLEAR = "CLEAR"
MAX_OCR_CHARS = 4000


class Review(BaseModel):
    rule_id: str = Field(description="The bracketed rule_id of the finding being reviewed")
    verdict: str = Field(description="UPHOLD to keep the violation, CLEAR to withdraw it")
    reason: str = Field(description="One sentence, quoting the label wording the decision rests on")


class Reviews(BaseModel):
    items: list[Review]


SYSTEM_PROMPT = """You are the second reader on a Legal Metrology inspection in India. A deterministic
rule engine has already compared a package label against the Legal Metrology (Packaged Commodities)
Rules, 2011 and flagged some declarations as violations. The engine matches fixed patterns, so it
mis-flags labels that satisfy a rule in different words. Your job is to catch those false readings.

For each flagged finding decide one of two things:

CLEAR - the label does what the rule requires, and the engine failed it only on form. The printed
wording differs from the pattern but carries the same meaning, or an abbreviation, punctuation,
spacing, capitalisation, word order or line break defeated the match. For example 'MRP (Incl. of all
taxes)', 'M.R.P. Rs 40 inclusive of all taxes' and 'Maximum Retail Price Rs 40/- incl. all taxes' all
satisfy the retail-sale-price rule; 'Net Wt. 100 g' satisfies a net-quantity rule written around
'Net quantity'. State the exact printed wording you relied on.

UPHOLD - anything else. Uphold when the declaration is simply absent from the label, when the rule
sets a number the package misses (a measured height, a quantity, a standard pack size, a permissible
error), when the wording is genuinely different in meaning or is vague, and whenever you are not
sure. Uphold too when the requirement merely looks unimportant - that is not your call.

A rule that calls for several things - a name and an address, or a name, an address and a telephone
number - is met only when every one of them is printed. A finding that lists declarations the engine
could not read off the label is never a wording problem: UPHOLD it. Finding one part present is not
a reason to clear the rule.

Rules you must follow:
- Work only from the label text and the declared values given to you. Never assume a declaration is
  printed somewhere you cannot see, and never supply a value the label does not carry.
- Judge each finding only against the rule text supplied for it. Do not clear one rule because a
  different rule is satisfied.
- You may only clear findings. You cannot add a violation, change a rule or reword a requirement.
- Doubt means UPHOLD. Wrongly clearing a real violation is far worse than leaving a wrong flag for
  the officer to dismiss.
- Return exactly one review for every finding you were given, keyed by its bracketed rule_id."""


def _digest_block() -> str:
    digest = rules_context.rules_digest()
    return f"Background - the packaged-commodities rules in brief:\n\n{digest}\n\n" if digest else ""


def _declared_block(values: dict) -> str:
    lines = []
    for path, item in sorted(values.items()):
        value = item["value"] if isinstance(item, dict) else item
        if value in (None, "", []):
            continue
        lines.append(f"- {normalization.label_for(path)} ({path}): {value}")
    return "\n".join(lines) or "- nothing was read from the label"


def _findings_block(violations: list[dict], details: dict) -> str:
    blocks = []
    for finding in violations:
        detail = details.get(finding["rule_id"]) or {}
        lines = [
            f"[{finding['rule_id']}] Rule {finding.get('rule_ref')} — {finding.get('requirement')}",
            f"Engine reason: {finding.get('explanation')}",
            f"What the engine read: {finding.get('observed') or 'not recorded'}",
        ]
        missing = detail.get("missing") or []
        if missing:
            lines.append("This rule needs these and they were not read off the label: " + ", ".join(missing))
        notes = detail.get("notes") or []
        if notes:
            lines.append("Engine notes: " + "; ".join(str(note) for note in notes))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def review(findings: list[dict], values: dict, ocr_text: str, details: dict | None = None) -> list[dict]:
    """Cross-check every NON_COMPLIANT finding; withdraw the ones the model clears."""
    violations = [finding for finding in findings if finding["status"] == "NON_COMPLIANT"]
    if not violations:
        return findings
    if not INFERENCE_ENABLED or not INFERENCE_API_KEY:
        return findings

    rule_ids = [finding["rule_id"] for finding in violations]

    result = llm.invoke_structured(
        Reviews,
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                f"{_digest_block()}Official rule text for the flagged rules (from the Rules, 2011):\n\n"
                f"{rules_context.text_block(rule_ids)}\n\n"
                f"Label text read from every uploaded panel:\n\n{ocr_text[:MAX_OCR_CHARS]}\n\n"
                f"Declarations read off the label:\n\n{_declared_block(values)}\n\n"
                f"Findings the engine flagged:\n\n{_findings_block(violations, details or {})}\n\n"
                "Review each finding and return CLEAR or UPHOLD with your reason.",
            ),
        ],
        provider=INFERENCE_PROVIDER,
        api_key=INFERENCE_API_KEY,
        model=INFERENCE_MODEL,
    )

    if result is None:
        logger.warning("Cross-check pass failed, every violation stands")
        return findings

    flagged = set(rule_ids)
    cleared = {}
    for item in result.items:
        rule_id = item.rule_id.strip().strip("[]")
        reason = item.reason.strip()
        if rule_id in flagged and item.verdict.strip().upper() == CLEAR and reason:
            cleared[rule_id] = reason

    for finding in violations:
        reason = cleared.get(finding["rule_id"])
        if not reason:
            continue
        finding["status"] = "COMPLIANT"
        finding["cleared_by_review"] = True
        finding["review_reason"] = reason
        finding["engine_explanation"] = finding.get("explanation")
        finding["explanation"] = reason

    if cleared:
        logger.info("Cross-check withdrew %s of %s violation(s): %s",
                    len(cleared), len(violations), ", ".join(sorted(cleared)))
    return findings
