from fastapi import APIRouter, Depends, HTTPException
from database import db_dependency
from schemas import CurrentUser
from services.auth_service import get_current_user
from models import Rules, RuleSets, LegalProvisions
from pipeline import retrieval
from typing import Annotated

rule_router = APIRouter(prefix="/rules", tags=["rules"])
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]


@rule_router.get("/sets")
def list_rule_sets(db: db_dependency, user: user_dependency):
    return [
        {
            "rule_set_version": row.rule_set_version,
            "rule_set_id": row.rule_set_id,
            "title": row.title,
            "legal_basis": row.legal_basis,
            "status": row.status,
            "content_sha256": row.content_sha256,
            "rule_count": db.query(Rules).filter(Rules.rule_set_version == row.rule_set_version).count(),
        }
        for row in db.query(RuleSets).all()
    ]


@rule_router.get("/catalogue")
def list_rules(db: db_dependency, user: user_dependency, version: str | None = None, mode: str | None = None):
    query = db.query(Rules)
    if version:
        query = query.filter(Rules.rule_set_version == version)
    if mode:
        query = query.filter(Rules.verification_mode == mode)
    return [
        {
            "rule_id": row.rule_id,
            "version": row.version,
            "status": row.status,
            "title": row.title,
            "provision": row.provision.get("rule"),
            "pdf_page": row.provision.get("pdf_page"),
            "text_excerpt": row.provision.get("text_excerpt"),
            "verification_mode": row.verification_mode,
            "severity": row.severity,
            "threshold_source": row.threshold_source,
            "effective_from": row.effective_from,
            "effective_to": row.effective_to,
        }
        for row in query.order_by(Rules.rule_id, Rules.version).all()
    ]


@rule_router.get("/provisions/search")
def search_provisions(q: str, db: db_dependency, user: user_dependency, limit: int = 5):
    if not q.strip():
        raise HTTPException(400, "Provide a search term")
    return [
        {
            "provision_id": row.provision_id,
            "rule_ref": row.rule_ref,
            "pdf_page": row.pdf_page,
            "text": row.text,
            "text_source": row.text_source,
        }
        for row in retrieval.search(db, q, limit)
    ]
