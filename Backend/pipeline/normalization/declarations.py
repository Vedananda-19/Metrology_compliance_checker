from pipeline.extraction.declarations import FACT_MAP, LABELS
from datetime import date
import re

MIN_PANELS_FOR_COVERAGE = 1
UNCLASSIFIED_TAG = "unclassified"
INDIA = re.compile(r"(?i)\b(india|bharat)\b")

# The rules match these against a strict pattern, so the fact has to hold the value itself.
# The model copies the printed wording with it - "Tel: 1800 103 1947", "Email: care@acme.in".
PHONE = re.compile(r"\+?[0-9][0-9()\-\s]{6,18}[0-9]")
EMAIL = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")
PIN = re.compile(r"\b[1-9][0-9]{5}\b")

UNIT_STATE = {
    "g": "solid", "gm": "solid", "gms": "solid", "kg": "solid", "mg": "solid",
    "ml": "liquid", "l": "liquid", "ltr": "liquid", "litre": "liquid",
    "cm": "linear", "mm": "linear", "m": "linear",
    "n": "countable", "u": "countable", "pcs": "countable", "pieces": "countable",
}


def to_number(text):
    match = re.search(r"-?\d+(?:\.\d+)?", str(text).replace(",", ""))
    return float(match.group()) if match else None


def coerce(value, kind):
    if value is None or str(value).strip() == "":
        return None
    text = str(value).strip()
    if kind is str:
        return text
    number = to_number(text)
    if number is None:
        return None
    return int(number) if kind is int else number


def normalize(extracted) -> dict:
    values = {}
    for field, (path, kind, _) in FACT_MAP.items():
        declared = getattr(extracted, field, None)
        if declared is None:
            continue
        value = coerce(declared.value, kind)
        if value is None:
            continue
        values[path] = {"value": value, "confidence": round(float(declared.confidence or 0.0), 3)}

    qualifier = getattr(extracted, "manufacturer_role_qualifier", None)
    if qualifier is not None:
        values["manufacturer.role_qualified"] = {
            "value": bool(coerce(qualifier.value, str)),
            "confidence": round(float(qualifier.confidence or 0.0), 3),
        }
    return values


def missing(values: dict) -> list[str]:
    return sorted(path for path, _, _ in FACT_MAP.values() if path not in values)


def label_for(path: str) -> str:
    return LABELS.get(path, path)


def _extracted(item: dict | None, pattern) -> dict | None:
    """The value on its own, when the model brought the printed label along with it."""
    if not item or not item.get("value"):
        return None
    text = str(item["value"]).strip()
    match = pattern.search(text)
    if match is None or match.group().strip() == text:
        return None
    return {**item, "value": match.group().strip()}


def _pin_code(item: dict | None) -> dict | None:
    """The PIN out of an address line - the rules check it, nothing else declares it."""
    if not item or not item.get("value"):
        return None
    codes = PIN.findall(str(item["value"]))
    return {**item, "value": codes[-1]} if codes else None


def build_facts(values: dict, panel_count: int, ocr_text: str) -> dict:
    facts = dict(values)

    facts["inspection.date"] = date.today().isoformat()
    facts["inspection.input_type"] = "package"
    facts["package.level"] = "retail"
    facts["package.intended_for"] = "consumer"
    facts["label.affixation"] = "printed_on_package"
    facts["extraction.coverage_complete"] = panel_count >= MIN_PANELS_FOR_COVERAGE and bool(ocr_text.strip())

    facts["product.tags"] = [UNCLASSIFIED_TAG]

    unit = (values.get("net_quantity.unit") or {}).get("value")
    state = UNIT_STATE.get(str(unit).strip().lower()) if unit else None
    if state:
        facts["product.physical_state"] = state

    languages = ["en"]
    if any("ऀ" <= character <= "ॿ" for character in ocr_text):
        languages.append("hi-Deva")
    facts["label.declaration_languages"] = {"value": languages, "confidence": 0.9}
    facts["label.full_text"] = {"value": ocr_text, "confidence": 1.0}

    importer = values.get("importer.name") or {}
    country = str((values.get("product.country_of_manufacture") or {}).get("value") or "").strip()
    # "Country of Origin: India" is printed on domestic packages and means the opposite of
    # imported - only a named importer or a foreign origin makes this an imported package
    domestic = bool(country and INDIA.search(country))
    if domestic:
        # the rules compare this against "India" literally, so "Made in India" must read as India
        facts["product.country_of_manufacture"] = {**values["product.country_of_manufacture"], "value": "India"}
    is_imported = bool(importer.get("value")) or bool(country and not domestic)
    facts["product.is_imported"] = is_imported
    if country:
        facts["product.packed_in_india"] = domestic
    elif is_imported:
        facts["product.packed_in_india"] = False

    for path, pattern in (("consumer_care.phone", PHONE), ("consumer_care.email", EMAIL)):
        value = _extracted(values.get(path), pattern)
        if value:
            facts[path] = value

    pin = _pin_code(values.get("manufacturer.address.text"))
    if pin:
        facts["manufacturer.address.pin"] = pin

    packer = values.get("packer.name") or {}
    manufacturer = values.get("manufacturer.name") or {}
    if packer.get("value"):
        facts["parties.packer_is_distinct"] = packer.get("value") != manufacturer.get("value")

    return facts
