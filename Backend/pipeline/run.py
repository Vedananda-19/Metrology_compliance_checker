from models import InspectionImages, OcrTexts, Declarations, Evaluations
from services import storage_service
from pipeline import llm
from pipeline.preprocessing import images as preprocessing
from pipeline.extraction import ocr, declarations as extraction
from pipeline.normalization import declarations as normalization
from pipeline.compliance import evaluate as compliance


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
    return "\n".join(panels)


def store_declarations(db, inspection_id: str, values: dict):
    db.query(Declarations).filter(Declarations.inspection_id == inspection_id).delete()
    for field, item in values.items():
        db.add(
            Declarations(
                inspection_id=inspection_id,
                field=field,
                value=item["value"],
                confidence=item["confidence"],
            )
        )
    db.flush()


def store_evaluation(db, inspection_id: str, evaluation):
    db.query(Evaluations).filter(Evaluations.inspection_id == inspection_id).delete()
    db.add(
        Evaluations(
            inspection_id=inspection_id,
            verdict=evaluation.verdict,
            result=evaluation.model_dump(),
        )
    )
    db.flush()


def run_pipeline(db, inspection):
    if not llm.available():
        raise RuntimeError("No LLM API key is configured, so declarations cannot be extracted")

    ocr_text = read_images(db, inspection.id)
    extracted = extraction.extract(ocr_text)
    values = normalization.normalize(extracted)
    store_declarations(db, inspection.id, values)

    evaluation = compliance.evaluate(db, values)
    store_evaluation(db, inspection.id, evaluation)
    return evaluation
