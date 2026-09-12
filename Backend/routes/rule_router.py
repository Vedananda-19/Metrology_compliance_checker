from fastapi import APIRouter, Depends
from schemas import CurrentUser
from services.auth_service import get_current_user
from engine import engine as rule_engine
from typing import Annotated

rule_router = APIRouter(prefix="/rules", tags=["rules"])
user_dependency = Annotated[CurrentUser, Depends(get_current_user)]

_catalogue = None


def catalogue():
    global _catalogue
    if _catalogue is None:
        ruleset = rule_engine.load_ruleset()
        _catalogue = {
            "rule_set_version": ruleset["rule_set_version"],
            "title": ruleset["title"],
            "rules": [
                {
                    "rule_id": rule["rule_id"],
                    "version": rule["version"],
                    "status": rule["status"],
                    "provision": rule["provision"]["rule"],
                    "pdf_page": rule["provision"].get("pdf_page"),
                    "title": rule["title"],
                    "text_excerpt": rule["provision"].get("text_excerpt"),
                    "severity": rule["severity"],
                    "verification_mode": rule["verification_mode"],
                    "threshold_source": rule["threshold_source"],
                }
                for rule in ruleset["rules"]
            ],
        }
    return _catalogue


@rule_router.get("")
def list_rules(user: user_dependency):
    return catalogue()
