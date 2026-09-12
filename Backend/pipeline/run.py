from models import InspectionImages, OcrTexts, Declarations, Evaluations
from services import storage_service
from pipeline import llm
from pipeline.preprocessing import images as preprocessing
from pipeline.extraction import ocr, declarations as extraction
from pipeline.normalization import declarations as normalization
from pipeline.compliance import evaluate as compliance
from pipeline.extraction.declarations import FACT_MAP

KIND_BY_PATH = {path: kind for path, kind, _ in FACT_MAP.values()}


def read_images(db, inspection_id: str) -> str:
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
    for record in records:
        image = preprocessing.prepare(storage_service.download(record.storage_path))
        text = ocr.read_text(image)
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
    return "\n".join(panels), len(panels)


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


def run_pipeline(db, inspection):
    if not llm.available():
        raise RuntimeError("No LLM API key is configured, so declarations cannot be extracted")

    ocr_text, panel_count = read_images(db, inspection.id)
    extracted = extraction.extract(ocr_text)
    values = normalization.normalize(extracted)
    store_declarations(db, inspection.id, values)

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
