from pydantic import BaseModel
from datetime import datetime
from typing import Any


class RegisterModel(BaseModel):
    username: str
    password: str
    confirmPassword: str
    full_name: str | None = None


class CurrentUser(BaseModel):
    user_id: str
    username: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    username: str
    full_name: str | None = None


class CreateInspectionModel(BaseModel):
    title: str | None = None


class ImageOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    display_order: int
    original_filename: str | None = None
    ocr_text: str | None = None


class DeclarationOut(BaseModel):
    model_config = {"from_attributes": True}

    field: str
    value: str | None = None
    confidence: float | None = None


class EvaluationOut(BaseModel):
    model_config = {"from_attributes": True}

    verdict: str | None = None
    result: dict[str, Any] = {}


class InspectionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    reference: str
    title: str | None = None
    status: str
    error: str | None = None
    created_at: datetime | None = None


class InspectionDetailOut(InspectionOut):
    images: list[ImageOut] = []
    declarations: list[DeclarationOut] = []
    evaluation: EvaluationOut | None = None
