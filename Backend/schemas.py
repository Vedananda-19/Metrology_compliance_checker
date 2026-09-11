from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Any, Literal


class RegisterModel(BaseModel):
    username: str
    password: str
    confirmPassword: str
    full_name: str | None = None
    designation: str | None = None
    office: str | None = None


class CurrentUser(BaseModel):
    user_id: str
    username: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    username: str
    full_name: str | None = None
    designation: str | None = None
    office: str | None = None


class CreateInspectionModel(BaseModel):
    title: str | None = None
    location: str | None = None


class UpdateInspectionModel(BaseModel):
    title: str | None = None
    location: str | None = None
    inspector_observations: str | None = None


class ImageOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    panel: str | None = None
    display_order: int
    usability: str
    review_note: str | None = None
    width_px: int | None = None
    height_px: int | None = None
    ocr_status: str
    mean_ocr_confidence: float | None = None
    original_filename: str | None = None
    url: str | None = None


class ImageOrderModel(BaseModel):
    image_ids: list[str]


class ImageReviewModel(BaseModel):
    usability: Literal["PENDING", "USABLE", "RETAKE", "REMOVED"]
    review_note: str | None = None
    panel: str | None = None


class RegionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    image_id: str
    text: str
    confidence: float
    polygon: list[list[int]]
    x1: int
    y1: int
    x2: int
    y2: int


class ImageOCROut(BaseModel):
    image: ImageOut
    regions: list[RegionOut]


class DeclarationOut(BaseModel):
    fact_path: str
    label: str
    ai_value: Any = None
    ai_confidence: float | None = None
    human_value: Any = None
    effective_value: Any = None
    verification_status: str
    extractor: str | None = None
    image_id: str | None = None
    region_id: str | None = None
    bbox: list[int] | None = None
    verified_at: datetime | None = None


class DeclarationEditModel(BaseModel):
    fact_path: str
    human_value: Any = None
    verification_status: Literal["UNVERIFIED", "VERIFIED", "REJECTED"] = "VERIFIED"


class DeclarationPatchModel(BaseModel):
    edits: list[DeclarationEditModel]


class ProductOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    brand: str | None = None
    common_name: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    physical_state: str | None = None
    classification_confidence: float | None = None
    classification_source: str | None = None
    human_override_tags: list[str] | None = None


class ProductOverrideModel(BaseModel):
    tags: list[str]
    category: str | None = None
    physical_state: str | None = None


class RuleOut(BaseModel):
    rule_id: str
    rule_version: int
    title: str
    provision: str | None = None
    severity: str | None = None
    verification_mode: str | None = None
    threshold_source: str | None = None
    status: str
    queue: str | None = None
    reason: str | None = None
    exemption_ref: str | None = None
    machine_checkable: bool
    why_it_applies: str | None = None
    officer_decision: str | None = None


class RuleDecisionModel(BaseModel):
    rule_id: str
    rule_version: int
    officer_decision: Literal["ACCEPTED", "REMOVED", "UNCERTAIN"]
    officer_note: str | None = None


class RuleDecisionPatchModel(BaseModel):
    decisions: list[RuleDecisionModel]


class EvidenceOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    image_id: str | None = None
    region_id: str | None = None
    fact_path: str | None = None
    observed_text: str | None = None
    kind: str
    note: str | None = None
    x1: int | None = None
    y1: int | None = None
    x2: int | None = None
    y2: int | None = None
    polygon: list[list[int]] | None = None


class FindingOut(BaseModel):
    id: str
    kind: Literal["VIOLATION", "RESULT"]
    rule_id: str
    rule_version: int
    title: str
    provision: str | None = None
    severity: str | None = None
    confidence: float | None = None
    status: str
    queue: str | None = None
    reason: str | None = None
    observed_value: Any = None
    expected: str | None = None
    legal_requirement: str | None = None
    source_reference: str | None = None
    llm_explanation: str | None = None
    llm_suggested_status: str | None = None
    llm_reason: str | None = None
    llm_confidence: float | None = None
    officer_decision: str | None = None
    officer_reason: str | None = None
    evidence: list[EvidenceOut] = Field(default_factory=list)
    missing_facts: list[str] = Field(default_factory=list)
    threshold_source: str | None = None
    verification_mode: str | None = None


class FindingDecisionModel(BaseModel):
    officer_decision: Literal["CONFIRMED", "OVERTURNED", "PENDING", "UNCERTAIN"]
    officer_reason: str | None = None


class ComplianceSummary(BaseModel):
    automated_verdict: str | None = None
    final_verdict: str | None = None
    counts: dict[str, int] = Field(default_factory=dict)
    by_category: list[dict[str, Any]] = Field(default_factory=list)
    open_manual_checklist: int = 0
    rules_evaluated: int = 0


class InspectionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    reference: str
    title: str | None = None
    location: str | None = None
    status: str
    rule_set_version: str | None = None
    judged_as_of: date | None = None
    automated_verdict: str | None = None
    final_verdict: str | None = None
    development_mode: bool = False
    degraded_mode: bool = False
    processing_error: str | None = None
    inspector_observations: str | None = None
    finalized_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    inspector_name: str | None = None
    image_count: int = 0
    violation_count: int = 0


class InspectionDetailOut(InspectionOut):
    images: list[ImageOut] = Field(default_factory=list)
    product: ProductOut | None = None
    summary: ComplianceSummary | None = None
    processing_log: list[dict[str, Any]] = Field(default_factory=list)


class AuditLogOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    action: str
    target: str | None = None
    old_value: Any = None
    new_value: Any = None
    source: str
    created_at: datetime
    username: str | None = None


class FinalizeModel(BaseModel):
    inspector_observations: str | None = None


class ReportOut(BaseModel):
    inspection: InspectionDetailOut
    declarations: list[DeclarationOut] = Field(default_factory=list)
    rules: list[RuleOut] = Field(default_factory=list)
    findings: list[FindingOut] = Field(default_factory=list)
    audit_logs: list[AuditLogOut] = Field(default_factory=list)
    rule_set_title: str | None = None
    generated_at: datetime | None = None
