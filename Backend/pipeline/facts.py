from models import ExtractedFacts, InspectionImages
from datetime import date

MIN_PANELS_FOR_COVERAGE = 2
MIN_MEAN_OCR_CONFIDENCE = 0.8


def language_codes(text: str):
    codes = ["en"]
    if any("ऀ" <= ch <= "ॿ" for ch in text or ""):
        codes.append("hi-Deva")
    return codes


def coverage_complete(images, label_text: str) -> bool:
    usable = [i for i in images if i.usability == "USABLE"]
    if len(usable) < MIN_PANELS_FOR_COVERAGE:
        return False
    if any(i.ocr_status != "DONE" for i in usable):
        return False
    confidences = [i.mean_ocr_confidence for i in usable if i.mean_ocr_confidence is not None]
    if not confidences or min(confidences) < MIN_MEAN_OCR_CONFIDENCE:
        return False
    return bool(label_text and label_text.strip())


def fact_node(row: ExtractedFacts):
    node = {
        "value": row.ai_value,
        "confidence": row.ai_confidence if row.ai_confidence is not None else 1.0,
        "source": row.extractor or "AI",
    }
    if row.human_value is not None:
        node["human_value"] = row.human_value
    if row.verification_status:
        node["verification_status"] = row.verification_status
    if row.image_id or row.bbox:
        node["evidence"] = {"image_id": row.image_id, "region_id": row.region_id, "bbox": row.bbox}
    return node


def stored_facts(db, inspection_id: str):
    rows = db.query(ExtractedFacts).filter(ExtractedFacts.inspection_id == inspection_id).all()
    return {row.fact_path: fact_node(row) for row in rows}


def effective_value(row: ExtractedFacts):
    if row.verification_status == "VERIFIED" and row.human_value is not None:
        return row.human_value
    if row.verification_status == "REJECTED":
        return None
    return row.ai_value


def build(db, inspection, product=None):
    raw = stored_facts(db, inspection.id)
    images = (
        db.query(InspectionImages)
        .filter(InspectionImages.inspection_id == inspection.id)
        .order_by(InspectionImages.display_order)
        .all()
    )

    label_node = raw.get("label.full_text") or {}
    label_text = str(label_node.get("value") or "")

    raw["inspection.date"] = (inspection.judged_as_of or date.today()).isoformat()
    raw["inspection.input_type"] = "package"
    raw["extraction.coverage_complete"] = coverage_complete(images, label_text)
    raw["package.level"] = "retail"
    raw["package.intended_for"] = "consumer"

    if "label.declaration_languages" not in raw:
        raw["label.declaration_languages"] = {"value": language_codes(label_text), "confidence": 0.9}
    if "label.affixation" not in raw:
        raw["label.affixation"] = "printed_on_package"

    if product is not None:
        tags = product.human_override_tags or product.tags or []
        if tags:
            raw["product.tags"] = list(tags)
        if product.physical_state:
            raw["product.physical_state"] = product.physical_state
        if product.common_name and "product.common_name" not in raw:
            raw["product.common_name"] = {"value": product.common_name, "confidence": product.classification_confidence or 0.7}

    importer = raw.get("importer.name") or {}
    country = raw.get("product.country_of_manufacture") or {}
    is_imported = bool(importer.get("value")) or bool(country.get("value"))
    raw["product.is_imported"] = is_imported
    if is_imported:
        raw["product.packed_in_india"] = False

    packer = raw.get("packer.name") or {}
    manufacturer = raw.get("manufacturer.name") or {}
    if packer.get("value"):
        raw["parties.packer_is_distinct"] = packer.get("value") != manufacturer.get("value")

    return raw
