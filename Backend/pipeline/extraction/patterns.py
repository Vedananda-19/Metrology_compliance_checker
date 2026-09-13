"""Deterministic reader for the declarations that are machine-readable.

The model is good at deciding which company name is the manufacturer and which is the packer.
It is unreliable at the mechanical part - copying "70" and "g" out of "Net Wt. 70 g", or the
month out of "MFD: 08/2025" - and it leaves those fields null often enough to matter, because
the rules for net quantity, retail sale price and date of manufacture are checked against the
numbers, not the wording. An absent number reads to the engine as an absent declaration, so a
label that plainly carries one gets flagged.

So the numbers are read here, by pattern, from the text the label actually shows. This never
overwrites a value the model returned: it only fills a field the model left empty, preferring
the model's own reading of the declaration over a fresh scan of the OCR.
"""
import re
from datetime import date

from engine import engine as rule_engine
from pipeline.extraction.declarations import PackageDeclarations, Declared

FIELDS = list(PackageDeclarations.model_fields)

# Parsed out of the declaration the model itself read - as close to the label as we get.
GROUNDED = 0.95
# Read straight off the OCR text.
SCANNED = 0.9

_ALIASES = rule_engine.load_tables()["units"]["si_unit_aliases"]
_UNIT_WORDS = sorted(
    {alias for canonical, aliases in _ALIASES.items() if canonical != "count_2011" for alias in aliases},
    key=len,
    reverse=True,
)

# "70 g", "1.5 kg", "500 ML" - the unit must end the token, so "100 Gurgaon Road" is not a quantity
QUANTITY = re.compile(r"(?i)\b(\d+(?:[.,]\d+)?)\s*(" + "|".join(re.escape(u) for u in _UNIT_WORDS) + r")(?![a-z0-9])")
COUNT = re.compile(r"\b(\d+)\s*(N|U)(?![A-Za-z0-9])")
QUANTITY_KEYWORD = re.compile(r"(?i)\b(net|nett)\b[\s.:]*(wt|weight|qty|quantity|contents?|vol|volume)?\b")

PRICE_KEYWORD = re.compile(r"(?i)\b(m\.?\s*r\.?\s*p\.?|maximum\s+retail\s+price|max\.?\s*retail\s*price|retail\s+sale\s+price)")
PRICE = re.compile(r"(?i)(?:rs\.?|₹|inr)\s*/?\s*(\d[\d,]*(?:\.\d{1,2})?)|(\d[\d,]*(?:\.\d{1,2})?)\s*/-")
# "M.R.P. Rs. 14.00" and "(Incl. of all taxes)" are one declaration the OCR broke in two
TAX_TAIL = re.compile(r"(?i)^\(?\s*(incl|inclusive)")

# "Mfd. by" and "Packed by" name a party, not a date - the address underneath must never be
# read as one ("Plot 12-25" is not December 2025)
MANUFACTURE_KEYWORD = re.compile(
    r"(?i)\b(?:mfd|mfg|manufactured|manufacture|packed|pkd|date\s+of\s+(?:mfg|manufacture|packing|pre-?packing|import)"
    r"|month\s+and\s+year)\b(?!\.?\s*by\b)"
)
# a shelf-life date is not a date of manufacture
SHELF_LIFE = re.compile(r"(?i)\b(best\s+before|best\s+by|use\s+by|expir\w*|exp\.?|consume\s+before|shelf\s+life)\b")

DAY_MONTH_YEAR = re.compile(r"\b(\d{1,2})\s*[/\-.]\s*(\d{1,2})\s*[/\-.]\s*(\d{2,4})\b")
MONTH_YEAR = re.compile(r"\b(\d{1,2})\s*[/\-.]\s*(\d{2,4})\b")
MONTH_NAMES = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
NAMED_MONTH_YEAR = re.compile(r"(?i)\b(" + "|".join(MONTH_NAMES) + r")[a-z]*\.?,?\s*[/\-]?\s*(\d{2,4})\b")


def _lines(text: str) -> list[str]:
    return [line.strip() for line in str(text).splitlines() if line.strip()]


def _declared(value, confidence: float) -> Declared:
    return Declared(value=str(value).strip(), confidence=confidence)


def _quantity_in(text: str) -> tuple[str, str] | None:
    match = QUANTITY.search(text)
    if match:
        return match.group(1).replace(",", ""), match.group(2)
    match = COUNT.search(text)
    return (match.group(1), match.group(2)) if match else None


def _price_in(text: str) -> str | None:
    match = PRICE.search(text)
    if not match:
        return None
    return (match.group(1) or match.group(2)).replace(",", "")


def _year(digits: str) -> int:
    value = int(digits)
    return value + 2000 if value < 100 else value


def _date_in(text: str) -> tuple[int, int] | None:
    """Month and year from any of 15.08.2025, 08/2025, 08/25, AUG 2025."""
    limit = date.today().year + 1
    for match in DAY_MONTH_YEAR.finditer(text):
        month, year = int(match.group(2)), _year(match.group(3))
        if 1 <= month <= 12 and 1900 <= year <= limit:
            return month, year
    for match in NAMED_MONTH_YEAR.finditer(text):
        year = _year(match.group(2))
        if 1900 <= year <= limit:
            return MONTH_NAMES.index(match.group(1).lower()[:3]) + 1, year
    for match in MONTH_YEAR.finditer(text):
        month, year = int(match.group(1)), _year(match.group(2))
        if 1 <= month <= 12 and 1900 <= year <= limit:
            return month, year
    return None


def quantity_from(text: str) -> dict:
    """The number and unit inside a net-quantity declaration the model already read."""
    found = _quantity_in(text)
    if not found:
        return {}
    value, unit = found
    return {
        "net_quantity_value": _declared(value, GROUNDED),
        "net_quantity_unit": _declared(unit, GROUNDED),
    }


def price_from(text: str) -> dict:
    """The rupee amount inside a price declaration the model already read."""
    amount = _price_in(text)
    return {"mrp_value": _declared(amount, GROUNDED)} if amount else {}


def scan(ocr_text: str) -> dict:
    """Net quantity, retail sale price and date of manufacture, read off the OCR by pattern."""
    lines = _lines(ocr_text)
    found = {}

    for index, line in enumerate(lines):
        window = line if index + 1 >= len(lines) else f"{line} {lines[index + 1]}"

        if "net_quantity_value" not in found and QUANTITY_KEYWORD.search(line):
            # "Net Weight" on one line and "70 g" on the next is one declaration
            source = line if _quantity_in(line) else window
            quantity = _quantity_in(source)
            if quantity:
                found["net_quantity_text"] = _declared(source, SCANNED)
                found["net_quantity_value"] = _declared(quantity[0], SCANNED)
                found["net_quantity_unit"] = _declared(quantity[1], SCANNED)

        if "mrp_value" not in found and PRICE_KEYWORD.search(line):
            source = line
            if not _price_in(line) or (index + 1 < len(lines) and TAX_TAIL.match(lines[index + 1])):
                source = window
            amount = _price_in(source)
            if amount:
                found["mrp_text"] = _declared(source, SCANNED)
                found["mrp_value"] = _declared(amount, SCANNED)

        keyword = MANUFACTURE_KEYWORD.search(line)
        if "manufacturing_month" not in found and keyword and not SHELF_LIFE.search(line):
            # read only what follows the keyword, so a lot number earlier on the line is not a date
            tail = line[keyword.end():]
            rest = lines[index + 1] if index + 1 < len(lines) else ""
            source = tail if _date_in(tail) else ("" if SHELF_LIFE.search(rest) else f"{tail} {rest}")
            moment = _date_in(source)
            if moment:
                found["manufacturing_month"] = _declared(moment[0], SCANNED)
                found["manufacturing_year"] = _declared(moment[1], SCANNED)

    return found


def _squash(text) -> str:
    return re.sub(r"[^0-9a-z]+", "", str(text).lower())


def _completed(declared: Declared, scanned: Declared | None) -> Declared | None:
    """The model read one line of a declaration the OCR broke across two.

    "M.R.P. Rs. 14.00" with "(Incl. of all taxes)" underneath is one declaration, and the rules
    judge its form, so the half-read version fails a rule the package actually satisfies. Only a
    scan that contains the model's own words is used - this completes a reading, never replaces it.
    """
    if scanned is None:
        return None
    short, whole = _squash(declared.value), _squash(scanned.value)
    if short and short in whole and len(whole) > len(short):
        return Declared(value=scanned.value, confidence=min(declared.confidence, scanned.confidence))
    return None


# declarations the OCR routinely splits across two lines
JOINED_TEXT = ("net_quantity_text", "mrp_text")


def backfill(ocr_text: str, extracted: PackageDeclarations) -> tuple[PackageDeclarations, list[str]]:
    """Fill the machine-readable fields the model left empty. Never overwrites the model."""
    found = scan(ocr_text)

    # the model's own reading of a declaration beats a fresh scan, so it goes in last
    for text_field, parse in (("net_quantity_text", quantity_from), ("mrp_text", price_from)):
        declared = getattr(extracted, text_field, None)
        if declared and declared.value:
            found.update(parse(declared.value))

    values = {}
    filled = []
    for field in FIELDS:
        declared = getattr(extracted, field, None)
        item = found.get(field)

        if declared and declared.value:
            whole = _completed(declared, item) if field in JOINED_TEXT else None
            values[field] = whole or declared
            if whole:
                filled.append(f"{field}={whole.value} (completed from the line below)")
            continue

        if item is None:
            continue
        values[field] = item
        filled.append(f"{field}={item.value}")

    return PackageDeclarations(**values), filled
