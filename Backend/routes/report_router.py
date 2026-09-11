from fastapi import APIRouter, Depends, Response
from database import db_dependency
from schemas import CurrentUser, ReportOut, InspectionDetailOut, ProductOut, AuditLogOut
from services.auth_service import get_current_user
from services import inspection_service, review_service, report_service, audit_service
from routes.inspection_router import image_out
from models import RuleSets, Users
from typing import Annotated
from datetime import datetime, timezone

report_router = APIRouter(prefix="/inspections", tags=["reports"])
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]


@report_router.get("/{inspection_id}/report", response_model=ReportOut)
def get_report(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    product = inspection_service.get_product(db, inspection_id)
    rule_set = db.query(RuleSets).filter(RuleSets.rule_set_version == inspection.rule_set_version).first()

    base = InspectionDetailOut.model_validate(inspection).model_dump()
    base.update(inspection_service.decorate(db, inspection))
    base["images"] = [image_out(image) for image in inspection_service.list_images(db, inspection_id)]
    base["product"] = ProductOut.model_validate(product) if product else None
    base["summary"] = review_service.summary(db, inspection_id, inspection)
    base["processing_log"] = inspection.processing_log or []

    names = {row.id: (row.full_name or row.username) for row in db.query(Users).all()}
    logs = []
    for row in audit_service.history(db, inspection_id):
        payload = AuditLogOut.model_validate(row)
        payload.username = names.get(row.user_id)
        logs.append(payload)

    return ReportOut(
        inspection=InspectionDetailOut(**base),
        declarations=review_service.declarations(db, inspection_id),
        rules=review_service.rules(db, inspection_id),
        findings=review_service.findings(db, inspection_id),
        audit_logs=logs,
        rule_set_title=rule_set.title if rule_set else None,
        generated_at=datetime.now(timezone.utc),
    )


@report_router.get("/{inspection_id}/report/pdf")
def get_report_pdf(inspection_id: str, db: db_dependency, user: user_dependency):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    data = report_service.generate_and_store(db, inspection_id, user)
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{inspection.reference}.pdf"'},
    )
