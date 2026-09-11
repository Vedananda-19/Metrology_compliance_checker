from pydantic import BaseModel, Field
from pipeline import llm
import re

MASS_UNITS = {"g", "gm", "gms", "gram", "grams", "kg", "kgs"}
VOLUME_UNITS = {"ml", "l", "ltr", "litre", "liter", "cc"}
LENGTH_UNITS = {"cm", "mm", "m", "metre", "meter"}
COUNT_UNITS = {"n", "u", "pc", "pcs", "piece", "pieces", "no", "nos", "units", "unit"}
ALL_UNITS = MASS_UNITS | VOLUME_UNITS | LENGTH_UNITS | COUNT_UNITS


class Declared(BaseModel):
    value: str | None = Field(default=None, description="Exact value read from the label, or null when absent")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="How sure you are this value is on the label")
    source_text: str | None = Field(default=None, description="The OCR line this value was taken from")


class PackageDeclarations(BaseModel):
    product_name: Declared = Field(default_factory=Declared)
    brand_name: Declared = Field(default_factory=Declared)
    common_or_generic_name: Declared = Field(default_factory=Declared)
    manufacturer_name: Declared = Field(default_factory=Declared)
    manufacturer_address: Declared = Field(default_factory=Declared)
    manufacturer_role_qualifier: Declared = Field(default_factory=Declared)
    packer_name: Declared = Field(default_factory=Declared)
    packer_address: Declared = Field(default_factory=Declared)
    importer_name: Declared = Field(default_factory=Declared)
    importer_address: Declared = Field(default_factory=Declared)
    country_of_origin: Declared = Field(default_factory=Declared)
    net_quantity_text: Declared = Field(default_factory=Declared)
    net_quantity_value: Declared = Field(default_factory=Declared)
    net_quantity_unit: Declared = Field(default_factory=Declared)
    mrp_text: Declared = Field(default_factory=Declared)
    mrp_value: Declared = Field(default_factory=Declared)
    manufacturing_month: Declared = Field(default_factory=Declared)
    manufacturing_year: Declared = Field(default_factory=Declared)
    consumer_care_name: Declared = Field(default_factory=Declared)
    consumer_care_address: Declared = Field(default_factory=Declared)
    consumer_care_phone: Declared = Field(default_factory=Declared)
    consumer_care_email: Declared = Field(default_factory=Declared)
    dimensions_text: Declared = Field(default_factory=Declared)
    sheet_count: Declared = Field(default_factory=Declared)


FACT_MAP = {
    "product_name": ("product.name", str),
    "brand_name": ("product.brand", str),
    "common_or_generic_name": ("product.common_name", str),
    "manufacturer_name": ("manufacturer.name", str),
    "manufacturer_address": ("manufacturer.address.text", str),
    "packer_name": ("packer.name", str),
    "packer_address": ("packer.address.text", str),
    "importer_name": ("importer.name", str),
    "importer_address": ("importer.address.text", str),
    "country_of_origin": ("product.country_of_manufacture", str),
    "net_quantity_text": ("net_quantity.text", str),
    "net_quantity_value": ("net_quantity.value", float),
    "net_quantity_unit": ("net_quantity.unit", str),
    "mrp_text": ("mrp.text", str),
    "mrp_value": ("mrp.value", float),
    "manufacturing_month": ("date_of_manufacture.month", int),
    "manufacturing_year": ("date_of_manufacture.year", int),
    "consumer_care_name": ("consumer_care.name", str),
    "consumer_care_address": ("consumer_care.address", str),
    "consumer_care_phone": ("consumer_care.phone", str),
    "consumer_care_email": ("consumer_care.email", str),
    "dimensions_text": ("dimensions.text", str),
    "sheet_count": ("sheets.count", int),
}

LABELS = {
    "product.name": "Product name",
    "product.brand": "Brand name",
    "product.common_name": "Common or generic name",
    "manufacturer.name": "Manufacturer name",
    "manufacturer.address.text": "Manufacturer address",
    "manufacturer.role_qualified": "Declared with 'Manufactured by' qualifier",
    "packer.name": "Packer name",
    "packer.address.text": "Packer address",
    "importer.name": "Importer name",
    "importer.address.text": "Importer address",
    "product.country_of_manufacture": "Country of origin",
    "net_quantity.text": "Net quantity declaration",
    "net_quantity.value": "Net quantity value",
    "net_quantity.unit": "Net quantity unit",
    "mrp.text": "Retail sale price declaration",
    "mrp.value": "Retail sale price value",
    "date_of_manufacture.month": "Month of manufacture",
    "date_of_manufacture.year": "Year of manufacture",
    "consumer_care.name": "Consumer care name",
    "consumer_care.address": "Consumer care address",
    "consumer_care.phone": "Consumer care telephone",
    "consumer_care.email": "Consumer care email",
    "dimensions.text": "Dimensions declaration",
    "sheets.count": "Number of sheets",
    "label.declaration_languages": "Declaration languages",
    "label.full_text": "All label text",
}

SYSTEM_PROMPT = """You read OCR text taken from the panels of a packaged commodity sold in India and
return the declarations printed on it.

Rules you must follow:
- Only report a value if it is actually present in the OCR text. Never guess, never complete a
  partial address, never convert or reformat a quantity or price.
- If a declaration is not in the text, leave value null and confidence 0. A missing declaration is
  a legally meaningful finding, so inventing one is worse than reporting nothing.
- Copy values exactly as printed, including qualifiers such as 'about', 'minimum' or 'approx'.
  Those words matter to the assessment and must not be cleaned up.
- source_text must be the OCR line you took the value from, copied verbatim.
- confidence reflects how clearly the text supports the value, not how plausible the value seems.
- net_quantity_value and mrp_value must be plain numbers with no unit or currency symbol.
- manufacturer_role_qualifier is the exact phrase used, such as 'Manufactured by', 'Packed by' or
  'Marketed by', or null if the label names a party without any such phrase."""


def to_number(text):
    if text is None:
        return None
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


def find_region(regions, source_text):
    if not source_text:
        return None
    needle = re.sub(r"\s+", " ", source_text).strip().lower()
    if not needle:
        return None
    best = None
    for region in regions:
        haystack = re.sub(r"\s+", " ", region["text"]).strip().lower()
        if not haystack:
            continue
        if needle == haystack:
            return region
        if needle in haystack or haystack in needle:
            if best is None or len(haystack) > len(best["text"]):
                best = region
    return best


def build_fact(value, confidence, region, extractor):
    fact = {"value": value, "confidence": round(float(confidence), 3), "extractor": extractor}
    if region:
        fact["region_id"] = region.get("id")
        fact["image_id"] = region.get("image_id")
        fact["bbox"] = [region["x1"], region["y1"], region["x2"], region["y2"]]
    return fact


def extract_with_llm(text: str, regions, extractor: str):
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"OCR text from every usable panel, one line per detected region:\n\n{text}"),
    ]
    result = llm.invoke_structured(PackageDeclarations, messages)
    if result is None:
        return None

    facts = {}
    for field_name, (fact_path, kind) in FACT_MAP.items():
        declared = getattr(result, field_name, None)
        if declared is None:
            continue
        value = coerce(declared.value, kind)
        if value is None:
            continue
        region = find_region(regions, declared.source_text)
        facts[fact_path] = build_fact(value, declared.confidence or 0.8, region, extractor)

    qualifier = getattr(result, "manufacturer_role_qualifier", None)
    if qualifier is not None:
        present = bool(coerce(qualifier.value, str))
        facts["manufacturer.role_qualified"] = build_fact(
            present, qualifier.confidence or 0.8, find_region(regions, qualifier.source_text), extractor
        )
    return facts


QUANTITY_RE = re.compile(
    r"(?:net\s*(?:wt|weight|vol|volume|qty|quantity|content)s?\.?\s*:?\s*)"
    r"(?P<qualifier>about|approx\.?|approximately|minimum|min\.?|max\.?|maximum|upto|up\s*to)?\s*"
    r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z]{1,6})\b",
    re.IGNORECASE,
)
MRP_RE = re.compile(
    r"(?:m\.?r\.?p|maximum\s+retail\s+price|retail\s+sale\s+price)\.?\s*:?\s*"
    r"(?:rs\.?|inr|₹)?\s*(?P<value>\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)
DATE_RE = re.compile(r"\b(?P<month>0?[1-9]|1[0-2])\s*[/\-]\s*(?P<year>20\d{2})\b")
PHONE_RE = re.compile(r"(?:phone|tel|ph|contact|toll[\s-]*free|customer\s*care)\D{0,10}(?P<value>[+0-9][0-9\-\s()]{7,18})", re.IGNORECASE)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PARTY_RE = re.compile(r"(manufactured|packed|marketed|imported)\s+(?:and\s+packed\s+)?by", re.IGNORECASE)
ADDRESS_HINT = re.compile(r"\b\d{6}\b|industrial|estate|road|street|plot|area|survey|phase|sector|district", re.IGNORECASE)
CARE_HEADING = re.compile(r"consumer\s+(?:complaint|care|cell)|customer\s+(?:care|relations|service)", re.IGNORECASE)


def sort_key(region):
    return (region.get("image_order", 0), region.get("reading_order", 0))


def lines_from(regions):
    return [r["text"].strip() for r in sorted(regions, key=sort_key) if r["text"].strip()]


def extract_with_rules(regions, extractor: str):
    lines = lines_from(regions)
    joined = " \n".join(lines)
    facts = {}

    def put(path, value, confidence, source_text):
        if value is None or (isinstance(value, str) and not value.strip()):
            return
        facts[path] = build_fact(value, confidence, find_region(regions, source_text), extractor)

    quantity = QUANTITY_RE.search(joined)
    if quantity:
        unit = quantity.group("unit")
        if unit.lower() in ALL_UNITS:
            source = quantity.group(0)
            put("net_quantity.text", source.strip(), 0.9, source)
            put("net_quantity.value", float(quantity.group("value")), 0.9, source)
            put("net_quantity.unit", unit, 0.9, source)

    mrp = MRP_RE.search(joined)
    if mrp:
        index = next((i for i, l in enumerate(lines) if MRP_RE.search(l)), None)
        line = lines[index] if index is not None else mrp.group(0)
        text = line.strip()
        if index is not None and index + 1 < len(lines) and re.search(r"inclusive|taxes", lines[index + 1], re.IGNORECASE):
            text = f"{text} {lines[index + 1].strip()}"
        put("mrp.text", text, 0.9, line)
        put("mrp.value", float(mrp.group("value").replace(",", "")), 0.9, line)

    date = DATE_RE.search(joined)
    if date:
        line = next((l for l in lines if date.group(0) in l), date.group(0))
        put("date_of_manufacture.month", int(date.group("month")), 0.88, line)
        put("date_of_manufacture.year", int(date.group("year")), 0.88, line)

    email = EMAIL_RE.search(joined)
    if email:
        put("consumer_care.email", email.group(0), 0.9, email.group(0))

    care_index = next((i for i, l in enumerate(lines) if CARE_HEADING.search(l)), None)
    care_block = lines[care_index + 1 : care_index + 7] if care_index is not None else []
    phone_scope = " \n".join(care_block) if care_block else joined
    phone = PHONE_RE.search(phone_scope) or PHONE_RE.search(joined)
    if phone:
        line = next((l for l in lines if phone.group("value").strip()[:6] in l), phone.group(0))
        put("consumer_care.phone", phone.group("value").strip(), 0.88, line)

    if care_block:
        put("consumer_care.name", care_block[0], 0.85, care_block[0])
        address = [l for l in care_block[1:] if ADDRESS_HINT.search(l)]
        if address:
            put("consumer_care.address", ", ".join(address), 0.85, address[0])

    party_index = next((i for i, l in enumerate(lines) if PARTY_RE.search(l)), None)
    if party_index is not None:
        keyword = PARTY_RE.search(lines[party_index]).group(1).lower()
        prefix = {"manufactured": "manufacturer", "packed": "packer", "marketed": "manufacturer", "imported": "importer"}[keyword]
        facts["manufacturer.role_qualified"] = build_fact(True, 0.85, find_region(regions, lines[party_index]), extractor)
        tail = lines[party_index].split(None)
        following = lines[party_index + 1 : party_index + 6]
        name = following[0] if following else None
        if name and len(tail) > 2:
            name = " ".join(tail[2:]) or name
        if name:
            put(f"{prefix}.name", name, 0.87, name)
        address = [l for l in following[1:] if ADDRESS_HINT.search(l) or re.search(r"india", l, re.IGNORECASE)]
        if address:
            put(f"{prefix}.address.text", ", ".join(address), 0.85, address[0])

    if "product.common_name" not in facts and lines:
        heading = next((l for l in lines[:6] if len(l.split()) >= 2 and not PARTY_RE.search(l)), lines[0])
        put("product.common_name", heading, 0.6, heading)

    return facts


def run(regions, extractor_base: str = "declarations"):
    extractor = llm.extractor_tag(extractor_base)
    text = "\n".join(lines_from(regions))

    facts = None
    if llm.available():
        facts = extract_with_llm(text, regions, extractor)

    used_fallback = facts is None
    if used_fallback:
        extractor = f"fallback:dev:{extractor_base}"
        facts = extract_with_rules(regions, extractor)

    facts["label.full_text"] = {"value": text, "confidence": 1.0, "extractor": extractor}
    return {"facts": facts, "extractor": extractor, "development_mode": used_fallback}
