import asyncio

from fastapi import APIRouter, Depends, File, UploadFile, Response, HTTPException, WebSocket, WebSocketDisconnect
from database import db_dependency
from schemas import (
    CurrentUser,
    CreateInspectionModel,
    InspectionOut,
    InspectionDetailOut,
    ImageOut,
    OcrTextOut,
    DeclarationOut,
    EvaluationOut,
    AssignModel,
    CardModel,
    UserOut,
    FindingReviewOut,
    ReviewModel,
    ReviseModel,
    FontMeasurementOut,
)
from models import STAGES
from services.auth_service import get_current_user, verify_ws_token
from services import inspection_service, storage_service
from pipeline.run import run_pipeline
from pipeline import progress
from pipeline.progress import hub
from typing import Annotated

inspection_router = APIRouter(prefix="/inspections", tags=["inspections"])
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]


def to_out(db, inspection) -> InspectionOut:
    payload = InspectionOut.model_validate(inspection)
    payload.priority = inspection_service.derive_priority(db, inspection)
    payload.assignee_name = (inspection.assignee.full_name or inspection.assignee.username) if inspection.assignee else None
    payload.owner_name = (inspection.inspector.full_name or inspection.inspector.username) if inspection.inspector else None
    payload.verified_by_name = (inspection.verifier.full_name or inspection.verifier.username) if inspection.verifier else None
    return payload


@inspection_router.post("", response_model=InspectionOut)
def create_inspection(data: CreateInspectionModel, db: db_dependency, user: user_dependency):
    return to_out(db, inspection_service.create_inspection(data.title, db, user))


@inspection_router.get("", response_model=list[InspectionOut])
def list_inspections(db: db_dependency, user: user_dependency, scope: str = "mine", officer_id: str | None = None, q: str | None = None):
    rows = inspection_service.list_inspections(db, user, scope, officer_id, q)
    return [to_out(db, row) for row in rows]


@inspection_router.get("/officers/list", response_model=list[UserOut])
def list_officers(db: db_dependency, user: user_dependency):
    if user.role != "INSPECTOR":
        raise HTTPException(403, "Only an inspector can list officers")
    return inspection_service.list_officers(db)


@inspection_router.get("/{inspection_id}", response_model=InspectionDetailOut)
def get_inspection(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection = inspection_service.get_visible(db, inspection_id, user)
    return InspectionDetailOut(
        **to_out(db, inspection).model_dump(),
        images=[ImageOut.model_validate(image) for image in inspection.images],
        ocr_texts=[OcrTextOut.model_validate(item) for item in sorted(inspection.ocr_texts, key=lambda x: x.display_order)],
        declarations=[DeclarationOut.model_validate(item) for item in inspection.declarations],
        evaluation=EvaluationOut.model_validate(inspection.evaluation) if inspection.evaluation else None,
        reviews=[FindingReviewOut.model_validate(item) for item in inspection.reviews],
        font_measurements=[FontMeasurementOut.model_validate(item) for item in inspection.font_measurements],
    )


@inspection_router.patch("/{inspection_id}/assign", response_model=InspectionOut)
def assign_case(inspection_id: str, data: AssignModel, db: db_dependency, user: user_dependency):
    return to_out(db, inspection_service.assign(inspection_id, data.officer_id, db, user))


@inspection_router.patch("/{inspection_id}/card", response_model=InspectionOut)
def update_card(inspection_id: str, data: CardModel, db: db_dependency, user: user_dependency):
    return to_out(db, inspection_service.update_card(inspection_id, data.stage, data.note, db, user))


@inspection_router.put("/{inspection_id}/findings/{rule_id}", response_model=InspectionDetailOut)
def review_finding(inspection_id: str, rule_id: str, data: ReviewModel, db: db_dependency, user: user_dependency):
    inspection_service.review_finding(inspection_id, rule_id, data.decision, data.note, db, user)
    return get_inspection(inspection_id, db, user)


@inspection_router.put("/{inspection_id}/declarations", response_model=InspectionDetailOut)
def revise_declarations(inspection_id: str, data: ReviseModel, db: db_dependency, user: user_dependency):
    inspection_service.revise_declarations(inspection_id, data.values, db, user)
    return get_inspection(inspection_id, db, user)


@inspection_router.patch("/{inspection_id}/finalize", response_model=InspectionDetailOut)
def finalize_verification(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection_service.finalize_verification(inspection_id, db, user)
    return get_inspection(inspection_id, db, user)


@inspection_router.get("/{inspection_id}/report")
def download_report(inspection_id: str, db: db_dependency, user: user_dependency, format: str = "pdf"):
    fmt = format.lower()
    if fmt not in ("pdf", "docx"):
        raise HTTPException(400, "Report format must be pdf or docx")
    content, media_type, filename = inspection_service.build_report(inspection_id, fmt, db, user)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@inspection_router.post("/{inspection_id}/images", response_model=list[ImageOut])
def upload_images(inspection_id: str, db: db_dependency, user: user_dependency, files: list[UploadFile] = File(...)):
    return inspection_service.add_images(inspection_id, files, db, user)


@inspection_router.delete("/{inspection_id}/images/{image_id}")
def delete_image(inspection_id: str, image_id: str, db: db_dependency, user: user_dependency):
    return inspection_service.delete_image(inspection_id, image_id, db, user)


@inspection_router.get("/{inspection_id}/images/{image_id}/file")
def get_image_file(inspection_id: str, image_id: str, db: db_dependency, user: user_dependency):
    inspection_service.get_visible(db, inspection_id, user)
    image = inspection_service.get_image(db, inspection_id, image_id)
    data = storage_service.download(image.storage_path)
    return Response(content=data, media_type=image.content_type or "image/jpeg")


@inspection_router.post("/{inspection_id}/process", response_model=InspectionDetailOut)
def process(inspection_id: str, db: db_dependency, user: user_dependency, reference_size_mm: float | None = None):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection.status = "PROCESSING"
    inspection.error = None
    inspection.verification_complete = False
    if inspection.stage == STAGES[0]:
        inspection.stage = STAGES[1]
    db.commit()

    try:
        run_pipeline(db, inspection, reference_size_mm)
        inspection.status = "COMPLETED"
        db.commit()
        progress.publish(inspection_id, "done", "success", "Inspection processed")
    except Exception as error:
        db.rollback()
        inspection.status = "FAILED"
        inspection.error = str(error)
        db.commit()
        progress.publish(inspection_id, "done", "error", str(error))
        raise HTTPException(400, str(error))

    return get_inspection(inspection_id, db, user)


@inspection_router.websocket("/{inspection_id}/progress")
async def progress_socket(websocket: WebSocket, inspection_id: str, token: str | None = None):
    user = verify_ws_token(token)
    if user is None:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    hub.bind_loop(asyncio.get_running_loop())
    queue = hub.subscribe(inspection_id)
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
            if event.get("stage") == "done":
                break
    except WebSocketDisconnect:
        pass
    finally:
        hub.unsubscribe(inspection_id, queue)
