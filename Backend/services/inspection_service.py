from fastapi import HTTPException, UploadFile
from sqlalchemy import func
from models import Inspections, InspectionImages, Users, Evaluations, STAGES
from services import storage_service
from config import ALLOWED_IMAGE_TYPES
from datetime import date
import uuid

STATUSES = ["DRAFT", "PROCESSING", "COMPLETED", "FAILED"]


def next_reference(db) -> str:
    prefix = f"INS-{date.today().year}-"
    count = db.query(func.count(Inspections.id)).filter(Inspections.reference.like(f"{prefix}%")).scalar()
    return f"{prefix}{count + 1:05d}"


SEVERITY_PRIORITY = {"CRITICAL": "HIGH", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW", "INFO": "LOW"}
PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def can_see(inspection: Inspections, user) -> bool:
    if user.role == "INSPECTOR":
        return True
    return inspection.user_id == user.user_id or inspection.assigned_to == user.user_id


def get_visible(db, inspection_id: str, user) -> Inspections:
    inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(404, "Inspection not found")
    if not can_see(inspection, user):
        raise HTTPException(403, "This case belongs to another officer")
    return inspection


def get_owned(db, inspection_id: str, user_id: str) -> Inspections:
    inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(404, "Inspection not found")
    if inspection.user_id != user_id and inspection.assigned_to != user_id:
        raise HTTPException(403, "This case belongs to another officer")
    return inspection


def derive_priority(db, inspection: Inspections) -> str:
    record = db.query(Evaluations).filter(Evaluations.inspection_id == inspection.id).first()
    if record is None or not record.result:
        return "LOW"
    severities = [
        f.get("severity")
        for f in (record.result.get("findings") or [])
        if f.get("status") == "NON_COMPLIANT"
    ]
    if not severities:
        return "LOW"
    return min((SEVERITY_PRIORITY.get(s, "LOW") for s in severities), key=lambda p: PRIORITY_ORDER[p])


def list_officers(db):
    return db.query(Users).filter(Users.role == "OFFICER").order_by(Users.username).all()


def assign(inspection_id: str, officer_id: str | None, db, user):
    if user.role != "INSPECTOR":
        raise HTTPException(403, "Only an inspector can assign cases")

    inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(404, "Inspection not found")

    if officer_id is not None:
        officer = db.query(Users).filter(Users.id == officer_id, Users.role == "OFFICER").first()
        if officer is None:
            raise HTTPException(400, "That officer does not exist")

    inspection.assigned_to = officer_id
    inspection.stage = STAGES[0]
    db.commit()
    db.refresh(inspection)
    return inspection


def update_card(inspection_id: str, stage: str | None, note: str | None, db, user):
    if user.role == "INSPECTOR":
        raise HTTPException(403, "An inspector views officer boards read-only")

    inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(404, "Inspection not found")

    owner = inspection.assigned_to or inspection.user_id
    if owner != user.user_id:
        raise HTTPException(403, "This card is on another officer's board")

    if stage is not None:
        if stage not in STAGES:
            raise HTTPException(400, f"Unknown stage {stage}")
        inspection.stage = stage
    if note is not None:
        inspection.note = note.strip()[:500]
    db.commit()
    db.refresh(inspection)
    return inspection


def create_inspection(title: str | None, db, user):
    inspection = Inspections(reference=next_reference(db), user_id=user.user_id, title=title)
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


def list_inspections(db, user, scope: str = "mine", officer_id: str | None = None):
    query = db.query(Inspections)

    if scope == "all":
        if user.role != "INSPECTOR":
            raise HTTPException(403, "Only an inspector can see every case")
    elif officer_id:
        if user.role != "INSPECTOR" and officer_id != user.user_id:
            raise HTTPException(403, "You can only see your own cases")
        query = query.filter(Inspections.assigned_to == officer_id)
    elif user.role == "INSPECTOR":
        query = query.filter(Inspections.user_id == user.user_id)
    else:
        query = query.filter(
            (Inspections.assigned_to == user.user_id) | (Inspections.user_id == user.user_id)
        )

    return query.order_by(Inspections.created_at.desc()).all()


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
