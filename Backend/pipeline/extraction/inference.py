import difflib
import logging
import re

from config import (
    INFERENCE_ENABLED,
    INFERENCE_PROVIDER,
    INFERENCE_API_KEY,
    INFERENCE_MODEL,
    INFERENCE_MIN_SIMILARITY,
)
from pipeline import llm
from pipeline.extraction.declarations import (
    FACT_MAP,
    LABELS,
    PackageDeclarations,
    Declared,
)
from datetime import date

logger = logging.getLogger(__name__)

FIELDS = list(FACT_MAP) + ["manufacturer_role_qualifier"]

# Derived value fields (numbers, units) are transformations of grounded text - a
# net quantity of 41.5 or a month of 8 need not appear verbatim in the OCR - so they
# skip the substring-grounding gate that guards free-text fields like names.
VALUE_FIELDS = {
    field for field, (_, kind, _) in FACT_MAP.items() if kind in (int, float)
}
VALUE_FIELDS.add("net_quantity_unit")

SYSTEM_PROMPT = """You are checking a first pass of declarations that another model extracted from the OCR text of an Indian packaged commodity label. Your job is to place each value under the correct field and make it read cleanly. You are correcting placement and formatting, nothing else.

- Work only from the OCR text. Every value you return must be supported by text that appears in the OCR. Never invent, infer, or complete a declaration that is not explicitly present.
- Move a value that the first pass placed under the wrong field. A manufacturer named under 'Marketed by' belongs in the marketer-style fields, not the manufacturer fields, and an address must not be placed in a name field.
- Split a name from its address when the first pass combined them, and join an address that OCR split across lines. Do not combine text from separate declarations unless the OCR clearly shows they belong together.
- Read company names carefully. Repair obvious character-level OCR damage only when the intended reading is unambiguous from the OCR, for example 'ACIVIE F00DS PVT LTD' to 'ACME FOODS PVT LTD'. If uncertain, preserve the OCR text.
- Keep qualifiers such as 'about', 'minimum', or 'nett' exactly as printed. Do not change units, quantities, numbers, names, or wording unless correcting clear OCR damage.
- Check the OCR text for declarations missing from the extracted fields and add them only when clearly supported by the OCR. Never infer or invent a missing declaration; a false addition is worse than an omission.
- Do not remove or alter a value merely because it seems unusual or unexpected if it is clearly present in the OCR.
- Confidence is how sure you are that the value belongs to this field, between 0 and 1."""


def normalise(text) -> str:
    return re.sub(r"[^0-9a-z]+", "", str(text).lower())


def similarity(token: str, haystack: str) -> float:
    best = 0.0
    matcher = difflib.SequenceMatcher(autojunk=False, b=token)
    step = max(1, len(token) // 5)

    for scale in (0.8, 1.0, 1.3):
        width = max(4, int(len(token) * scale))
        if width > len(haystack):
            continue
        for start in range(0, len(haystack) - width + 1, step):
            matcher.set_seq1(haystack[start : start + width])
            if matcher.real_quick_ratio() <= best or matcher.quick_ratio() <= best:
                continue
            best = max(best, matcher.ratio())
    return best


def grounded(value, haystack: str) -> bool:
    token = normalise(value)
    if not token:
        return False
    if token in haystack:
        return True
    if len(token) < 4:
        return False
    return similarity(token, haystack) >= INFERENCE_MIN_SIMILARITY


RANGES = {
    "manufacturing_month": (1, 12),
    "manufacturing_year": (1900, date.today().year + 1),
    "net_quantity_value": (None, None),
    "mrp_value": (None, None),
    "sheet_count": (None, None),
}


def plausible(field: str, value) -> bool:
    bounds = RANGES.get(field)
    if bounds is None:
        return True

    number = re.search(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    if number is None:
        return False

    amount = float(number.group())
    if amount <= 0:
        return False

    low, high = bounds
    if low is not None and amount < low:
        return False
    return high is None or amount <= high


def as_declared(value) -> Declared | None:
    if value is None:
        return None
    return value if isinstance(value, Declared) else Declared(**value)


def field_summary(extracted) -> str:
    lines = []
    for field in FIELDS:
        declared = getattr(extracted, field, None)
        value = declared.value if declared else None
        label = LABELS.get(FACT_MAP[field][0], field) if field in FACT_MAP else field
        lines.append(f"{field} ({label}): {value if value else 'null'}")
    return "\n".join(lines)


def relocated(original_value: str, second, field: str) -> bool:
    original = normalise(original_value)
    for other in FIELDS:
        if other == field:
            continue
        declared = as_declared(getattr(second, other, None))
        moved = normalise(declared.value) if declared and declared.value else ""
        if moved and moved in original:
            return True
    return False


def merge(first, second, ocr_text: str) -> tuple[PackageDeclarations, list[str]]:
    haystack = normalise(ocr_text)
    values = {}
    changes = []

    for field in FIELDS:
        original = as_declared(getattr(first, field, None))
        revised = as_declared(getattr(second, field, None))

        original_value = original.value if original else None
        revised_value = revised.value if revised else None

        is_value = field in VALUE_FIELDS

        if revised_value and not plausible(field, revised_value):
            logger.info(
                "Inference dropped an implausible value for %s: %s",
                field,
                revised_value,
            )
            revised_value = None

        if revised_value and (is_value or grounded(revised_value, haystack)):
            values[field] = revised
            if normalise(revised_value) != normalise(original_value or ""):
                changes.append(
                    f"{field}: {original_value or 'null'} -> {revised_value}"
                )
            continue

        if revised_value and not is_value and not grounded(revised_value, haystack):
            logger.info("Inference dropped an ungrounded value for %s", field)

        if not original_value:
            continue

        if not is_value and relocated(original_value, second, field):
            changes.append(f"{field}: {original_value} -> moved to another field")
            continue

        values[field] = original

    return PackageDeclarations(**values), changes


def reconcile(
    ocr_text: str, extracted: PackageDeclarations
) -> tuple[PackageDeclarations, list[str]]:
    if not INFERENCE_ENABLED or not INFERENCE_API_KEY:
        return extracted, []

    reviewed = llm.invoke_structured(
        PackageDeclarations,
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                f"OCR text from every uploaded panel:\n\n{ocr_text}\n\n"
                f"First pass, one field per line:\n\n{field_summary(extracted)}\n\n"
                "Return the corrected set of declarations.",
            ),
        ],
        provider=INFERENCE_PROVIDER,
        api_key=INFERENCE_API_KEY,
        model=INFERENCE_MODEL,
    )

    if reviewed is None:
        logger.warning("Inference pass returned nothing, keeping the first pass")
        return extracted, []

    merged, changes = merge(extracted, reviewed, ocr_text)
    if changes:
        logger.info(
            "Inference refiled %s declaration(s): %s", len(changes), "; ".join(changes)
        )
    return merged, changes
