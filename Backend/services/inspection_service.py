from fastapi import HTTPException, UploadFile
from sqlalchemy import func
from models import Inspections, InspectionImages, OCRTextRegions, Users, Products, Violations
from schemas import CreateInspectionModel, UpdateInspectionModel
from services import storage_service, audit_service
from config import ALLOWED_IMAGE_TYPES, RULE_SET_VERSION
from datetime import date, datetime, timezone
import uuid

STATUS_ORDER = [
    "DRAFT",
    "IMAGES_UPLOADED",
    "IMAGE_REVIEW",
    "PROCESSING",
    "EXTRACTION_REVIEW",
    "CLASSIFICATION_REVIEW",
    "RULE_REVIEW",
    "COMPLIANCE_REVIEW",
    "VIOLATION_REVIEW",
    "FINAL_REVIEW",
    "FINALIZED",
]

EDITABLE_BEFORE_PROCESSING = {"DRAFT", "IMAGES_UPLOADED", "IMAGE_REVIEW"}


def rank(status: str) -> int:
    return STATUS_ORDER.index(status) if status in STATUS_ORDER else -1


def next_reference(db) -> str:
    year = date.today().year
    prefix = f"INS-{year}-"
    count = db.query(func.count(Inspections.id)).filter(Inspections.reference.like(f"{prefix}%")).scalar()
    return f"{prefix}{count + 1:05d}"


def get_owned(db, inspection_id: str, user_id: str) -> Inspections:
    inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(404, "Inspection not found")
    if inspection.user_id != user_id:
        raise HTTPException(403, "This inspection belongs to another inspector")
    return inspection


def assert_not_finalized(inspection: Inspections):
    if inspection.status == "FINALIZED":
        raise HTTPException(409, "This inspection is finalized and can no longer be modified")


def assert_can_transition(inspection: Inspections, target: str):
    assert_not_finalized(inspection)
    if rank(target) < rank(inspection.status):
        raise HTTPException(409, f"Cannot move an inspection from {inspection.status} back to {target}")


def advance_to(db, inspection: Inspections, target: str):
    if rank(target) > rank(inspection.status):
        inspection.status = target
        db.flush()
    return inspection


def create_inspection(data: CreateInspectionModel, db, user):
    inspection = Inspections(
        reference=next_reference(db),
        user_id=user.user_id,
        title=data.title,
        location=data.location,
        status="DRAFT",
        rule_set_version=RULE_SET_VERSION,
        judged_as_of=date.today(),
        processing_log=[],
    )
    db.add(inspection)
    db.flush()
    audit_service.record(db, inspection.id, user.user_id, "inspection_created", inspection.reference)
    db.commit()
    db.refresh(inspection)
    return inspection


def update_inspection(inspection_id: str, data: UpdateInspectionModel, db, user):
    inspection = get_owned(db, inspection_id, user.user_id)
    assert_not_finalized(inspection)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inspection, field, value)
    db.commit()
    db.refresh(inspection)
    return inspection


def list_inspections(db, user, limit: int = 50):
    return (
        db.query(Inspections)
        .filter(Inspections.user_id == user.user_id)
        .order_by(Inspections.created_at.desc())
        .limit(limit)
        .all()
    )


def add_images(inspection_id: str, files: list[UploadFile], db, user):
    inspection = get_owned(db, inspection_id, user.user_id)
    assert_not_finalized(inspection)
    if inspection.status not in EDITABLE_BEFORE_PROCESSING:
        raise HTTPException(409, "Images cannot be changed once processing has started")
    if not files:
        raise HTTPException(400, "No images were uploaded")

    start = db.query(func.count(InspectionImages.id)).filter(
        InspectionImages.inspection_id == inspection.id
    ).scalar()

    created = []
    for offset, upload in enumerate(files):
        if upload.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(400, f"Unsupported image type {upload.content_type}")
        data = upload.file.read()
        if not data:
            raise HTTPException(400, f"{upload.filename} is empty")

        image_id = str(uuid.uuid4())
        suffix = (upload.filename or "image.jpg").rsplit(".", 1)[-1].lower()
        storage_path = f"inspections/{inspection.id}/{image_id}.{suffix}"
        storage_service.upload(storage_path, data, upload.content_type)

        width, height = image_size(data)
        record = InspectionImages(
            id=image_id,
            inspection_id=inspection.id,
            storage_path=storage_path,
            original_filename=upload.filename,
            content_type=upload.content_type,
            display_order=start + offset,
            width_px=width,
            height_px=height,
        )
        db.add(record)
        created.append(record)

    audit_service.record(
        db, inspection.id, user.user_id, "images_uploaded", None, None, {"count": len(created)}
    )
    advance_to(db, inspection, "IMAGES_UPLOADED")
    db.commit()
    for record in created:
        db.refresh(record)
    return created


def image_size(data: bytes):
    try:
        from PIL import Image
        import io

        with Image.open(io.BytesIO(data)) as image:
            return image.width, image.height
    except Exception:
        return None, None


def list_images(db, inspection_id: str):
    return (
        db.query(InspectionImages)
        .filter(InspectionImages.inspection_id == inspection_id)
        .order_by(InspectionImages.display_order)
        .all()
    )


def get_image(db, inspection_id: str, image_id: str) -> InspectionImages:
    image = (
        db.query(InspectionImages)
        .filter(InspectionImages.id == image_id, InspectionImages.inspection_id == inspection_id)
        .first()
    )
    if image is None:
        raise HTTPException(404, "Image not found on this inspection")
    return image


def delete_image(inspection_id: str, image_id: str, db, user):
    inspection = get_owned(db, inspection_id, user.user_id)
    assert_not_finalized(inspection)
    if inspection.status not in EDITABLE_BEFORE_PROCESSING:
        raise HTTPException(409, "Images cannot be removed once processing has started")

    image = get_image(db, inspection_id, image_id)
    storage_service.remove(image.storage_path)
    db.delete(image)
    db.flush()

    for order, remaining in enumerate(list_images(db, inspection_id)):
        remaining.display_order = order

    audit_service.record(db, inspection.id, user.user_id, "image_removed", image_id, {"filename": image.original_filename}, None)
    db.commit()
    return {"message": "Image removed"}


def reorder_images(inspection_id: str, image_ids: list[str], db, user):
    inspection = get_owned(db, inspection_id, user.user_id)
    assert_not_finalized(inspection)
    images = {image.id: image for image in list_images(db, inspection_id)}
    if set(image_ids) != set(images):
        raise HTTPException(400, "The ordering must list every image on this inspection exactly once")

    for order, image_id in enumerate(image_ids):
        images[image_id].display_order = order
    audit_service.record(db, inspection.id, user.user_id, "images_reordered", None, None, {"order": image_ids})
    db.commit()
    return list_images(db, inspection_id)


def review_image(inspection_id: str, image_id: str, data, db, user):
    inspection = get_owned(db, inspection_id, user.user_id)
    assert_not_finalized(inspection)
    image = get_image(db, inspection_id, image_id)

    previous = image.usability
    image.usability = data.usability
    if data.review_note is not None:
        image.review_note = data.review_note
    if data.panel is not None:
        image.panel = data.panel

    audit_service.record(
        db, inspection.id, user.user_id, "image_reviewed", image_id,
        {"usability": previous}, {"usability": data.usability, "note": data.review_note},
    )
    advance_to(db, inspection, "IMAGE_REVIEW")
    db.commit()
    db.refresh(image)
    return image


def verify_images(inspection_id: str, db, user):
    inspection = get_owned(db, inspection_id, user.user_id)
    assert_not_finalized(inspection)
    images = list_images(db, inspection_id)
    if not images:
        raise HTTPException(400, "Upload at least one image before confirming")

    usable = [image for image in images if image.usability == "USABLE"]
    if not usable:
        raise HTTPException(400, "Mark at least one image usable before processing")

    audit_service.record(db, inspection.id, user.user_id, "images_verified", None, None, {"usable": len(usable)})
    advance_to(db, inspection, "IMAGE_REVIEW")
    db.commit()
    return {"message": f"{len(usable)} image(s) confirmed for processing", "usable": len(usable)}


def usable_images(db, inspection_id: str):
    return [image for image in list_images(db, inspection_id) if image.usability == "USABLE"]


def regions_for(db, inspection_id: str, image_id: str = None):
    query = db.query(OCRTextRegions).filter(OCRTextRegions.inspection_id == inspection_id)
    if image_id:
        query = query.filter(OCRTextRegions.image_id == image_id)
    return query.order_by(OCRTextRegions.reading_order).all()


def decorate(db, inspection: Inspections):
    inspector = db.query(Users).filter(Users.id == inspection.user_id).first()
    image_count = db.query(func.count(InspectionImages.id)).filter(
        InspectionImages.inspection_id == inspection.id
    ).scalar()
    violation_count = db.query(func.count(Violations.id)).filter(
        Violations.inspection_id == inspection.id,
        Violations.officer_decision != "OVERTURNED",
    ).scalar()
    return {
        "inspector_name": (inspector.full_name or inspector.username) if inspector else None,
        "image_count": image_count or 0,
        "violation_count": violation_count or 0,
    }


def get_product(db, inspection_id: str):
    return db.query(Products).filter(Products.inspection_id == inspection_id).first()


def mark_finalized(db, inspection: Inspections):
    inspection.status = "FINALIZED"
    inspection.finalized_at = datetime.now(timezone.utc)
    db.flush()
