from fastapi import APIRouter, Depends, File, UploadFile, Response, HTTPException
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
)
from services.auth_service import get_current_user
from services import inspection_service, storage_service
from pipeline.run import run_pipeline
from typing import Annotated

inspection_router = APIRouter(prefix="/inspections", tags=["inspections"])
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]


def to_out(db, inspection) -> InspectionOut:
    payload = InspectionOut.model_validate(inspection)
    payload.priority = inspection_service.derive_priority(db, inspection)
    payload.assignee_name = (inspection.assignee.full_name or inspection.assignee.username) if inspection.assignee else None
    payload.owner_name = (inspection.inspector.full_name or inspection.inspector.username) if inspection.inspector else None
    return payload


@inspection_router.post("", response_model=InspectionOut)
def create_inspection(data: CreateInspectionModel, db: db_dependency, user: user_dependency):
    return to_out(db, inspection_service.create_inspection(data.title, db, user))


@inspection_router.get("", response_model=list[InspectionOut])
def list_inspections(db: db_dependency, user: user_dependency, scope: str = "mine", officer_id: str | None = None):
    rows = inspection_service.list_inspections(db, user, scope, officer_id)
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
    )


@inspection_router.patch("/{inspection_id}/assign", response_model=InspectionOut)
def assign_case(inspection_id: str, data: AssignModel, db: db_dependency, user: user_dependency):
    return to_out(db, inspection_service.assign(inspection_id, data.officer_id, db, user))


@inspection_router.patch("/{inspection_id}/card", response_model=InspectionOut)
def update_card(inspection_id: str, data: CardModel, db: db_dependency, user: user_dependency):
    return to_out(db, inspection_service.update_card(inspection_id, data.stage, data.note, db, user))


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
def process(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection.status = "PROCESSING"
    inspection.error = None
    db.commit()

    try:
        run_pipeline(db, inspection)
        inspection.status = "COMPLETED"
        db.commit()
    except Exception as error:
        db.rollback()
        inspection.status = "FAILED"
        inspection.error = str(error)
        db.commit()
        raise HTTPException(400, str(error))

    return get_inspection(inspection_id, db, user)
