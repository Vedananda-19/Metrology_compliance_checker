from pydantic import BaseModel
from datetime import datetime
from typing import Any, Literal


class RegisterModel(BaseModel):
    username: str
    password: str
    confirmPassword: str
    full_name: str | None = None
    role: Literal["OFFICER", "INSPECTOR"] = "OFFICER"


class CurrentUser(BaseModel):
    user_id: str
    username: str
    role: str = "OFFICER"


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    username: str
    full_name: str | None = None
    role: str = "OFFICER"


class CreateInspectionModel(BaseModel):
    title: str | None = None


class ImageOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    display_order: int
    original_filename: str | None = None


class OcrTextOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    image_id: str | None = None
    display_order: int
    text: str


class DeclarationOut(BaseModel):
    model_config = {"from_attributes": True}

    field: str
    value: str | None = None
    confidence: float | None = None


class EvaluationOut(BaseModel):
    model_config = {"from_attributes": True}

    verdict: str | None = None
    result: dict[str, Any] = {}


class AssignModel(BaseModel):
    officer_id: str | None = None


class CardModel(BaseModel):
    stage: str | None = None
    note: str | None = None


class FindingReviewOut(BaseModel):
    model_config = {"from_attributes": True}

    rule_id: str
    decision: str
    note: str | None = None


class ReviewModel(BaseModel):
    decision: Literal["CONFIRMED", "DISMISSED", "VERIFIED_COMPLIANT", "VERIFIED_NON_COMPLIANT"] | None = None
    note: str | None = None


class ReviseModel(BaseModel):
    values: dict[str, str | None]


class FontMeasurementOut(BaseModel):
    model_config = {"from_attributes": True}

    field: str
    measured_height_px: float | None = None
    measured_height_mm: float | None = None
    reference_size_mm: float
    reference_size_px: float | None = None
    scale_mm_per_pixel: float | None = None
    confidence: float = 0.0
    status: str
    detail: str | None = None


class InspectionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    reference: str
    title: str | None = None
    status: str
    stage: str
    note: str | None = None
    error: str | None = None
    created_at: datetime | None = None
    assigned_to: str | None = None
    assignee_name: str | None = None
    owner_name: str | None = None
    priority: str = "LOW"
    verification_complete: bool = False
    verified_at: datetime | None = None
    verified_by_name: str | None = None


class InspectionDetailOut(InspectionOut):
    images: list[ImageOut] = []
    ocr_texts: list[OcrTextOut] = []
    declarations: list[DeclarationOut] = []
    evaluation: EvaluationOut | None = None
    reviews: list[FindingReviewOut] = []
    font_measurements: list[FontMeasurementOut] = []
