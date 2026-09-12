from pydantic import BaseModel, Field, field_validator
from pipeline import llm

FACT_MAP = {
    "product_name": ("product.name", str, "Product name"),
    "brand_name": ("product.brand", str, "Brand name"),
    "common_or_generic_name": ("product.common_name", str, "Common or generic name"),
    "manufacturer_name": ("manufacturer.name", str, "Manufacturer name"),
    "manufacturer_address": ("manufacturer.address.text", str, "Manufacturer address"),
    "packer_name": ("packer.name", str, "Packer name"),
    "packer_address": ("packer.address.text", str, "Packer address"),
    "importer_name": ("importer.name", str, "Importer name"),
    "importer_address": ("importer.address.text", str, "Importer address"),
    "country_of_origin": ("product.country_of_manufacture", str, "Country of origin"),
    "net_quantity_text": ("net_quantity.text", str, "Net quantity declaration"),
    "net_quantity_value": ("net_quantity.value", float, "Net quantity value"),
    "net_quantity_unit": ("net_quantity.unit", str, "Net quantity unit"),
    "mrp_text": ("mrp.text", str, "Retail sale price declaration"),
    "mrp_value": ("mrp.value", float, "Retail sale price value"),
    "manufacturing_month": ("date_of_manufacture.month", int, "Month of manufacture"),
    "manufacturing_year": ("date_of_manufacture.year", int, "Year of manufacture"),
    "consumer_care_name": ("consumer_care.name", str, "Consumer care name"),
    "consumer_care_address": ("consumer_care.address", str, "Consumer care address"),
    "consumer_care_phone": ("consumer_care.phone", str, "Consumer care telephone"),
    "consumer_care_email": ("consumer_care.email", str, "Consumer care email"),
    "dimensions_text": ("dimensions.text", str, "Dimensions declaration"),
    "sheet_count": ("sheets.count", int, "Number of sheets"),
}

LABELS = {path: label for path, _, label in FACT_MAP.values()}
LABELS["manufacturer.role_qualified"] = "Declared with a 'Manufactured by' qualifier"


class Declared(BaseModel):
    value: str | None = Field(default=None, description="Exact value read from the label, or null when absent")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("value", mode="before")
    @classmethod
    def as_text(cls, value):
        if value is None or isinstance(value, str):
            return value
        return str(value)

    @field_validator("confidence", mode="before")
    @classmethod
    def absent_confidence_is_zero(cls, value):
        return 0.0 if value is None else value


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


SYSTEM_PROMPT = """You read OCR text taken from the panels of a packaged commodity sold in India and
return the declarations printed on it.

- Only report a value if it is actually present in the OCR text. Never guess and never complete a
  partial address.
- If a declaration is not in the text, leave value null and confidence 0. A missing declaration is a
  legally meaningful finding, so inventing one is worse than reporting nothing.
- Copy values exactly as printed, including qualifiers such as 'about' or 'minimum'. Those words
  matter to the assessment and must not be cleaned up.
- net_quantity_text and mrp_text are the whole declaration as printed. net_quantity_value, mrp_value,
  manufacturing_month and manufacturing_year are plain numbers with no unit, currency or separator.
- manufacturer_role_qualifier is the exact phrase used, such as 'Manufactured by', 'Packed by' or
  'Marketed by', or null if the label names a party without any such phrase."""


def extract(ocr_text: str) -> PackageDeclarations:
    result = llm.invoke_structured(
        PackageDeclarations,
        [
            ("system", SYSTEM_PROMPT),
            ("human", f"OCR text from every uploaded panel:\n\n{ocr_text}"),
        ],
    )
    if result is None:
        raise RuntimeError("Declaration extraction failed: the language model returned nothing")
    return result
