from fastapi import APIRouter, Depends, File, UploadFile, Response
from fastapi.responses import StreamingResponse
from database import db_dependency
from schemas import (
    CurrentUser,
    CreateInspectionModel,
    UpdateInspectionModel,
    InspectionOut,
    InspectionDetailOut,
    ImageOut,
    ImageOrderModel,
    ImageReviewModel,
    ImageOCROut,
    RegionOut,
    DeclarationOut,
    DeclarationPatchModel,
    ProductOut,
    ProductOverrideModel,
    RuleOut,
    RuleDecisionPatchModel,
    FindingOut,
    FindingDecisionModel,
    FinalizeModel,
    AuditLogOut,
)
from services.auth_service import get_current_user
from services import inspection_service, review_service, processing_service, storage_service
from services.reevaluation import reevaluate
from typing import Annotated

inspection_router = APIRouter(prefix="/inspections", tags=["inspections"])
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]


def to_out(db, inspection) -> InspectionOut:
    return InspectionOut(**InspectionOut.model_validate(inspection).model_dump() | inspection_service.decorate(db, inspection))


def image_out(image) -> ImageOut:
    payload = ImageOut.model_validate(image)
    payload.url = storage_service.signed_url(image.storage_path)
    return payload


@inspection_router.post("", response_model=InspectionOut)
def create_inspection(data: CreateInspectionModel, db: db_dependency, user: user_dependency):
    return to_out(db, inspection_service.create_inspection(data, db, user))


@inspection_router.get("", response_model=list[InspectionOut])
def list_inspections(db: db_dependency, user: user_dependency, limit: int = 50):
    return [to_out(db, item) for item in inspection_service.list_inspections(db, user, limit)]


@inspection_router.get("/{inspection_id}", response_model=InspectionDetailOut)
def get_inspection(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    product = inspection_service.get_product(db, inspection_id)
    base = InspectionDetailOut.model_validate(inspection).model_dump()
    base.update(inspection_service.decorate(db, inspection))
    base["images"] = [image_out(image) for image in inspection_service.list_images(db, inspection_id)]
    base["product"] = ProductOut.model_validate(product) if product else None
    base["summary"] = review_service.summary(db, inspection_id, inspection)
    base["processing_log"] = inspection.processing_log or []
    return InspectionDetailOut(**base)


@inspection_router.patch("/{inspection_id}", response_model=InspectionOut)
def update_inspection(inspection_id: str, data: UpdateInspectionModel, db: db_dependency, user: user_dependency):
    return to_out(db, inspection_service.update_inspection(inspection_id, data, db, user))


@inspection_router.post("/{inspection_id}/images", response_model=list[ImageOut])
def upload_images(inspection_id: str, db: db_dependency, user: user_dependency, files: list[UploadFile] = File(...)):
    return [image_out(image) for image in inspection_service.add_images(inspection_id, files, db, user)]


@inspection_router.get("/{inspection_id}/images", response_model=list[ImageOut])
def list_images(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection_service.get_owned(db, inspection_id, user.user_id)
    return [image_out(image) for image in inspection_service.list_images(db, inspection_id)]


@inspection_router.get("/{inspection_id}/images/{image_id}/file")
def get_image_file(inspection_id: str, image_id: str, db: db_dependency, user: user_dependency):
    inspection_service.get_owned(db, inspection_id, user.user_id)
    image = inspection_service.get_image(db, inspection_id, image_id)
    data = storage_service.download(image.storage_path)
    return Response(content=data, media_type=image.content_type or "image/jpeg")


@inspection_router.patch("/{inspection_id}/images/order", response_model=list[ImageOut])
def reorder_images(inspection_id: str, data: ImageOrderModel, db: db_dependency, user: user_dependency):
    return [image_out(image) for image in inspection_service.reorder_images(inspection_id, data.image_ids, db, user)]


@inspection_router.patch("/{inspection_id}/images/{image_id}", response_model=ImageOut)
def review_image(inspection_id: str, image_id: str, data: ImageReviewModel, db: db_dependency, user: user_dependency):
    return image_out(inspection_service.review_image(inspection_id, image_id, data, db, user))


@inspection_router.delete("/{inspection_id}/images/{image_id}")
def delete_image(inspection_id: str, image_id: str, db: db_dependency, user: user_dependency):
    return inspection_service.delete_image(inspection_id, image_id, db, user)


@inspection_router.post("/{inspection_id}/verify-images")
def verify_images(inspection_id: str, db: db_dependency, user: user_dependency):
    return inspection_service.verify_images(inspection_id, db, user)


@inspection_router.post("/{inspection_id}/process")
async def process(inspection_id: str, db: db_dependency, user: user_dependency):
    return processing_service.start(inspection_id, db, user)


@inspection_router.get("/{inspection_id}/events")
async def events_stream(inspection_id: str, db: db_dependency, user: user_dependency):
    generator = await processing_service.stream(inspection_id, db, user)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@inspection_router.get("/{inspection_id}/ocr", response_model=list[ImageOCROut])
def get_ocr(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection_service.get_owned(db, inspection_id, user.user_id)
    output = []
    for image in inspection_service.list_images(db, inspection_id):
        regions = inspection_service.regions_for(db, inspection_id, image.id)
        output.append(ImageOCROut(image=image_out(image), regions=[RegionOut.model_validate(r) for r in regions]))
    return output


@inspection_router.get("/{inspection_id}/declarations", response_model=list[DeclarationOut])
def get_declarations(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection_service.get_owned(db, inspection_id, user.user_id)
    return review_service.declarations(db, inspection_id)


@inspection_router.patch("/{inspection_id}/declarations", response_model=list[DeclarationOut])
def patch_declarations(inspection_id: str, data: DeclarationPatchModel, db: db_dependency, user: user_dependency):
    return review_service.patch_declarations(inspection_id, data.edits, db, user)


@inspection_router.post("/{inspection_id}/declarations/confirm")
def confirm_declarations(inspection_id: str, db: db_dependency, user: user_dependency):
    return review_service.confirm_declarations(inspection_id, db, user, reevaluate)


@inspection_router.patch("/{inspection_id}/product", response_model=ProductOut)
def override_product(inspection_id: str, data: ProductOverrideModel, db: db_dependency, user: user_dependency):
    return review_service.override_product(inspection_id, data, db, user, reevaluate)


@inspection_router.get("/{inspection_id}/rules", response_model=list[RuleOut])
def get_rules(inspection_id: str, db: db_dependency, user: user_dependency, include_not_applicable: bool = False):
    inspection_service.get_owned(db, inspection_id, user.user_id)
    return review_service.rules(db, inspection_id, include_not_applicable)


@inspection_router.patch("/{inspection_id}/rules", response_model=list[RuleOut])
def patch_rules(inspection_id: str, data: RuleDecisionPatchModel, db: db_dependency, user: user_dependency):
    return review_service.patch_rules(inspection_id, data.decisions, db, user)


@inspection_router.get("/{inspection_id}/findings", response_model=list[FindingOut])
def get_findings(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection_service.get_owned(db, inspection_id, user.user_id)
    return review_service.findings(db, inspection_id)


@inspection_router.patch("/{inspection_id}/findings/{finding_id}", response_model=list[FindingOut])
def patch_finding(inspection_id: str, finding_id: str, data: FindingDecisionModel, db: db_dependency, user: user_dependency):
    return review_service.patch_finding(inspection_id, finding_id, data, db, user)


@inspection_router.get("/{inspection_id}/audit", response_model=list[AuditLogOut])
def get_audit(inspection_id: str, db: db_dependency, user: user_dependency):
    from services import audit_service
    from models import Users

    inspection_service.get_owned(db, inspection_id, user.user_id)
    names = {row.id: (row.full_name or row.username) for row in db.query(Users).all()}
    entries = []
    for row in audit_service.history(db, inspection_id):
        payload = AuditLogOut.model_validate(row)
        payload.username = names.get(row.user_id)
        entries.append(payload)
    return entries


@inspection_router.post("/{inspection_id}/finalize", response_model=InspectionOut)
def finalize(inspection_id: str, data: FinalizeModel, db: db_dependency, user: user_dependency):
    return to_out(db, review_service.finalize(inspection_id, data, db, user))
