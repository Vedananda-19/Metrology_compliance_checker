from fastapi import HTTPException, UploadFile
from sqlalchemy import func
from models import Inspections, InspectionImages
from services import storage_service
from config import ALLOWED_IMAGE_TYPES
from datetime import date
import uuid

STATUSES = ["DRAFT", "PROCESSING", "COMPLETED", "FAILED"]


def next_reference(db) -> str:
    prefix = f"INS-{date.today().year}-"
    count = db.query(func.count(Inspections.id)).filter(Inspections.reference.like(f"{prefix}%")).scalar()
    return f"{prefix}{count + 1:05d}"


def get_owned(db, inspection_id: str, user_id: str) -> Inspections:
    inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(404, "Inspection not found")
    if inspection.user_id != user_id:
        raise HTTPException(403, "This inspection belongs to another inspector")
    return inspection


def create_inspection(title: str | None, db, user):
    inspection = Inspections(reference=next_reference(db), user_id=user.user_id, title=title)
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


def list_inspections(db, user):
    return (
        db.query(Inspections)
        .filter(Inspections.user_id == user.user_id)
        .order_by(Inspections.created_at.desc())
        .all()
    )


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


def add_images(inspection_id: str, files: list[UploadFile], db, user):
    inspection = get_owned(db, inspection_id, user.user_id)
    if inspection.status == "PROCESSING":
        raise HTTPException(409, "This inspection is being processed")
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

        record = InspectionImages(
            id=image_id,
            inspection_id=inspection.id,
            storage_path=storage_path,
            original_filename=upload.filename,
            content_type=upload.content_type,
            display_order=start + offset,
        )
        db.add(record)
        created.append(record)

    db.commit()
    for record in created:
        db.refresh(record)
    return created


def delete_image(inspection_id: str, image_id: str, db, user):
    inspection = get_owned(db, inspection_id, user.user_id)
    if inspection.status == "PROCESSING":
        raise HTTPException(409, "This inspection is being processed")

    image = get_image(db, inspection_id, image_id)
    storage_service.remove(image.storage_path)
    db.delete(image)
    db.flush()
    for order, remaining in enumerate(list_images(db, inspection_id)):
        remaining.display_order = order
    db.commit()
    return {"message": "Image removed"}
