from pydantic import BaseModel, Field, field_validator
from pipeline import llm

FIELDS = {
    "product_name": "Product name",
    "brand_name": "Brand name",
    "common_or_generic_name": "Common or generic name",
    "manufacturer_name": "Manufacturer name",
    "manufacturer_address": "Manufacturer address",
    "packer_name": "Packer name",
    "importer_name": "Importer name",
    "country_of_origin": "Country of origin",
    "net_quantity": "Net quantity declaration",
    "mrp": "Retail sale price declaration",
    "manufacturing_date": "Month and year of manufacture",
    "consumer_care_name": "Consumer care name",
    "consumer_care_address": "Consumer care address",
    "consumer_care_phone": "Consumer care telephone",
    "consumer_care_email": "Consumer care email",
    "dimensions": "Dimensions declaration",
}


class Declared(BaseModel):
    value: str | None = Field(default=None, description="Exact value read from the label, or null when absent")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

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
    packer_name: Declared = Field(default_factory=Declared)
    importer_name: Declared = Field(default_factory=Declared)
    country_of_origin: Declared = Field(default_factory=Declared)
    net_quantity: Declared = Field(default_factory=Declared)
    mrp: Declared = Field(default_factory=Declared)
    manufacturing_date: Declared = Field(default_factory=Declared)
    consumer_care_name: Declared = Field(default_factory=Declared)
    consumer_care_address: Declared = Field(default_factory=Declared)
    consumer_care_phone: Declared = Field(default_factory=Declared)
    consumer_care_email: Declared = Field(default_factory=Declared)
    dimensions: Declared = Field(default_factory=Declared)


SYSTEM_PROMPT = """You read OCR text taken from the panels of a packaged commodity sold in India and
return the declarations printed on it.

- Only report a value if it is actually present in the OCR text. Never guess and never complete a
  partial address.
- If a declaration is not in the text, leave value null and confidence 0. A missing declaration is a
  legally meaningful finding, so inventing one is worse than reporting nothing.
- Copy values exactly as printed, including qualifiers such as 'about' or 'minimum'. Those words
  matter to the assessment and must not be cleaned up."""


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
