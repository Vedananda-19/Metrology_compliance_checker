from models import InspectionImages, OcrTexts, Declarations, Evaluations, FontMeasurements
from services import storage_service
from pipeline import llm
from pipeline.extraction import ocr, declarations as extraction, inference
from pipeline.normalization import declarations as normalization
from pipeline.compliance import evaluate as compliance
from pipeline.extraction.declarations import FACT_MAP
from pipeline.preprocessing.images import decode, resize
from pipeline.measurement import font, reference

KIND_BY_PATH = {path: kind for path, kind, _ in FACT_MAP.values()}


def read_images(db, inspection_id: str) -> tuple[str, int, list[dict]]:
    records = (
        db.query(InspectionImages)
        .filter(InspectionImages.inspection_id == inspection_id)
        .order_by(InspectionImages.display_order)
        .all()
    )
    if not records:
        raise RuntimeError("Upload at least one image before processing")

    db.query(OcrTexts).filter(OcrTexts.inspection_id == inspection_id).delete()

    panels = []
    pages = []
    for record in records:
        image = storage_service.download(record.storage_path)
        text, words = ocr.read_document(image)
        pages.append({"image": resize(decode(image)), "words": words})
        db.add(
            OcrTexts(
                inspection_id=inspection_id,
                image_id=record.id,
                display_order=record.display_order,
                text=text,
            )
        )
        if text:
            panels.append(text)

    db.commit()
    if not panels:
        raise RuntimeError("No readable text was found on the uploaded images")
    return "\n".join(panels), len(panels), pages


def store_declarations(db, inspection_id: str, values: dict):
    db.query(Declarations).filter(Declarations.inspection_id == inspection_id).delete()
    for path, item in values.items():
        db.add(
            Declarations(
                inspection_id=inspection_id,
                field=path,
                value=str(item["value"]),
                confidence=item["confidence"],
            )
        )
    db.flush()


def store_evaluation(db, inspection_id: str, evaluation: dict):
    db.query(Evaluations).filter(Evaluations.inspection_id == inspection_id).delete()
    db.add(
        Evaluations(
            inspection_id=inspection_id,
            verdict=evaluation["verdict"],
            result=evaluation,
        )
    )
    db.flush()


def measure_fonts(db, inspection_id: str, extracted, pages: list[dict], reference_size_mm: float | None):
    db.query(FontMeasurements).filter(FontMeasurements.inspection_id == inspection_id).delete()
    if not reference_size_mm:
        return []

    scales = [reference.find_scale(page["image"], reference_size_mm) for page in pages]

    results = []
    for field in FACT_MAP:
        declared = getattr(extracted, field, None)
        value = declared.value if declared else None
        if not value:
            continue

        best = None
        for page, scale in zip(pages, scales):
            result = font.measure(field, value, page["image"], page["words"], scale, reference_size_mm)
            if result.status == font.MEASURED:
                best = result
                break
            best = best or result
        if best is None:
            continue

        db.add(FontMeasurements(inspection_id=inspection_id, **best.model_dump()))
        results.append(best)

    db.flush()
    return results


def run_pipeline(db, inspection, reference_size_mm: float | None = None):
    if not llm.available():
        raise RuntimeError("No LLM API key is configured, so declarations cannot be extracted")

    ocr_text, panel_count, pages = read_images(db, inspection.id)
    extracted = extraction.extract(ocr_text)
    extracted, _ = inference.reconcile(ocr_text, extracted)
    values = normalization.normalize(extracted)
    store_declarations(db, inspection.id, values)
    measure_fonts(db, inspection.id, extracted, pages, reference_size_mm)

    evaluation = compliance.evaluate(values, panel_count, ocr_text)
    store_evaluation(db, inspection.id, evaluation)
    return evaluation


def stored_values(db, inspection_id: str) -> dict:
    values = {}
    records = db.query(Declarations).filter(Declarations.inspection_id == inspection_id).all()
    for record in records:
        kind = KIND_BY_PATH.get(record.field)
        value = normalization.coerce(record.value, kind) if kind else record.value not in ("", "False", "None")
        if value is None:
            continue
        values[record.field] = {"value": value, "confidence": record.confidence or 0.0}
    return values


def panels_of(db, inspection_id: str) -> tuple[str, int]:
    rows = (
        db.query(OcrTexts)
        .filter(OcrTexts.inspection_id == inspection_id)
        .order_by(OcrTexts.display_order)
        .all()
    )
    panels = [row.text for row in rows if row.text]
    return "\n".join(panels), len(panels)


def reevaluate(db, inspection_id: str) -> dict:
    ocr_text, panel_count = panels_of(db, inspection_id)
    evaluation = compliance.evaluate(stored_values(db, inspection_id), panel_count, ocr_text)
    store_evaluation(db, inspection_id, evaluation)
    return evaluation
