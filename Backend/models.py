from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    Text,
    JSON,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from database import Base, embedding_column
from datetime import datetime, timezone
import uuid


def new_id():
    return str(uuid.uuid4())


def now_utc():
    return datetime.now(timezone.utc)


class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=new_id)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    office = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    inspections = relationship("Inspections", back_populates="inspector")


class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String, primary_key=True)
    device = Column(String)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))


class RuleSets(Base):
    __tablename__ = "rule_sets"

    rule_set_version = Column(String, primary_key=True)
    rule_set_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    legal_basis = Column(String)
    status = Column(String, nullable=False, default="published")
    macros = Column(JSON, nullable=False, default=dict)
    fact_vocabulary = Column(JSON, nullable=False, default=dict)
    content_sha256 = Column(String)
    published_at = Column(DateTime(timezone=True), default=now_utc)

    rules = relationship("Rules", back_populates="rule_set")
    reference_tables = relationship("ReferenceTables", back_populates="rule_set")


class Rules(Base):
    __tablename__ = "rules"

    rule_id = Column(String, primary_key=True)
    version = Column(Integer, primary_key=True)
    rule_set_version = Column(String, ForeignKey("rule_sets.rule_set_version"), nullable=False)
    status = Column(String, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String)
    provision = Column(JSON, nullable=False)
    provision_id = Column(String)
    verification_mode = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    applies_when = Column(JSON, nullable=False)
    exempt_when = Column(JSON, nullable=False, default=list)
    check_expr = Column(JSON, nullable=False)
    outcome_on_fail = Column(String, nullable=False)
    fail_message = Column(Text, nullable=False)
    evidence_facts = Column(JSON, default=list)
    threshold_source = Column(String, nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    amendment_status = Column(String)
    notes = Column(Text)

    rule_set = relationship("RuleSets", back_populates="rules")


class ReferenceTables(Base):
    __tablename__ = "reference_tables"

    rule_set_version = Column(String, ForeignKey("rule_sets.rule_set_version"), primary_key=True)
    table_name = Column(String, primary_key=True)
    data = Column(JSON, nullable=False)

    rule_set = relationship("RuleSets", back_populates="reference_tables")


class LegalProvisions(Base):
    __tablename__ = "legal_provisions"

    provision_id = Column(String, primary_key=True)
    source = Column(String, nullable=False, default="LMPC Rules 2011")
    rule_ref = Column(String, nullable=False)
    pdf_page = Column(Integer)
    text = Column(Text, nullable=False)
    text_source = Column(String, default="rule_excerpt")
    effective_from = Column(Date)
    effective_to = Column(Date)
    embedding = Column(embedding_column(), nullable=True)


class Inspections(Base):
    __tablename__ = "inspections"

    id = Column(String, primary_key=True, default=new_id)
    reference = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    location = Column(String)
    status = Column(String, nullable=False, default="DRAFT")
    rule_set_version = Column(String, ForeignKey("rule_sets.rule_set_version"))
    judged_as_of = Column(Date)
    automated_verdict = Column(String)
    final_verdict = Column(String)
    development_mode = Column(Boolean, default=False)
    degraded_mode = Column(Boolean, default=False)
    processing_log = Column(JSON, default=list)
    processing_error = Column(Text)
    inspector_observations = Column(Text)
    finalized_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    inspector = relationship("Users", back_populates="inspections")
    images = relationship("InspectionImages", back_populates="inspection", cascade="all, delete-orphan")
    product = relationship("Products", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
    facts = relationship("ExtractedFacts", back_populates="inspection", cascade="all, delete-orphan")
    results = relationship("RuleResults", back_populates="inspection", cascade="all, delete-orphan")
    violations = relationship("Violations", back_populates="inspection", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLogs", back_populates="inspection", cascade="all, delete-orphan")
    report = relationship("Reports", back_populates="inspection", uselist=False, cascade="all, delete-orphan")


class InspectionImages(Base):
    __tablename__ = "inspection_images"

    id = Column(String, primary_key=True, default=new_id)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    panel = Column(String, default="unspecified")
    storage_path = Column(String, nullable=False)
    original_filename = Column(String)
    content_type = Column(String)
    display_order = Column(Integer, default=0)
    usability = Column(String, default="PENDING")
    review_note = Column(String)
    width_px = Column(Integer)
    height_px = Column(Integer)
    ocr_status = Column(String, default="PENDING")
    mean_ocr_confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    inspection = relationship("Inspections", back_populates="images")
    regions = relationship("OCRTextRegions", back_populates="image", cascade="all, delete-orphan")


class OCRTextRegions(Base):
    __tablename__ = "ocr_text_regions"

    id = Column(String, primary_key=True, default=new_id)
    image_id = Column(String, ForeignKey("inspection_images.id", ondelete="CASCADE"), nullable=False)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    polygon = Column(JSON, nullable=False)
    x1 = Column(Integer, nullable=False)
    y1 = Column(Integer, nullable=False)
    x2 = Column(Integer, nullable=False)
    y2 = Column(Integer, nullable=False)
    reading_order = Column(Integer, default=0)

    image = relationship("InspectionImages", back_populates="regions")


class Products(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=new_id)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), unique=True, nullable=False)
    brand = Column(String)
    common_name = Column(String)
    category = Column(String)
    tags = Column(JSON, default=list)
    physical_state = Column(String)
    classification_confidence = Column(Float)
    classification_source = Column(String)
    human_override_tags = Column(JSON)
    overridden_by = Column(String, ForeignKey("users.id"))
    overridden_at = Column(DateTime(timezone=True))

    inspection = relationship("Inspections", back_populates="product")


class ExtractedFacts(Base):
    __tablename__ = "extracted_facts"

    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), primary_key=True)
    fact_path = Column(String, primary_key=True)
    ai_value = Column(JSON)
    ai_confidence = Column(Float)
    extractor = Column(String)
    image_id = Column(String, ForeignKey("inspection_images.id", ondelete="SET NULL"))
    region_id = Column(String, ForeignKey("ocr_text_regions.id", ondelete="SET NULL"))
    bbox = Column(JSON)
    human_value = Column(JSON)
    verification_status = Column(String, nullable=False, default="UNVERIFIED")
    verified_by = Column(String, ForeignKey("users.id"))
    verified_at = Column(DateTime(timezone=True))

    inspection = relationship("Inspections", back_populates="facts")
    region = relationship("OCRTextRegions")


class RuleResults(Base):
    __tablename__ = "rule_results"
    __table_args__ = (
        UniqueConstraint("inspection_id", "rule_id", "rule_version", "run_no", name="uq_rule_result_run"),
        ForeignKeyConstraint(["rule_id", "rule_version"], ["rules.rule_id", "rules.version"]),
        Index("ix_rule_results_inspection", "inspection_id", "run_no"),
    )

    id = Column(String, primary_key=True, default=new_id)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(String, nullable=False)
    rule_version = Column(Integer, nullable=False)
    run_no = Column(Integer, nullable=False, default=1)
    title = Column(String)
    provision = Column(String)
    severity = Column(String)
    verification_mode = Column(String)
    threshold_source = Column(String)
    status = Column(String, nullable=False)
    queue = Column(String)
    reason = Column(Text)
    exemption_ref = Column(String)
    missing_facts = Column(JSON, default=list)
    low_conf_facts = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)
    notes = Column(JSON, default=list)
    evidence = Column(JSON, default=list)
    officer_decision = Column(String)
    officer_note = Column(Text)
    llm_suggested_status = Column(String)
    llm_reason = Column(Text)
    llm_confidence = Column(Float)
    evaluated_at = Column(DateTime(timezone=True), default=now_utc)

    inspection = relationship("Inspections", back_populates="results")
    violation = relationship("Violations", back_populates="result", uselist=False)


class Violations(Base):
    __tablename__ = "violations"

    id = Column(String, primary_key=True, default=new_id)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    result_id = Column(String, ForeignKey("rule_results.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(String, nullable=False)
    rule_version = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    provision = Column(String)
    severity = Column(String, nullable=False)
    confidence = Column(Float)
    observed_value = Column(JSON)
    expected = Column(Text)
    legal_requirement = Column(Text)
    source_reference = Column(String)
    llm_explanation = Column(Text)
    officer_decision = Column(String, default="PENDING")
    officer_reason = Column(Text)
    decided_by = Column(String, ForeignKey("users.id"))
    decided_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=now_utc)

    inspection = relationship("Inspections", back_populates="violations")
    result = relationship("RuleResults", back_populates="violation")
    evidence_items = relationship("Evidence", back_populates="violation", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=new_id)
    violation_id = Column(String, ForeignKey("violations.id", ondelete="CASCADE"), nullable=False)
    image_id = Column(String, ForeignKey("inspection_images.id", ondelete="SET NULL"))
    region_id = Column(String, ForeignKey("ocr_text_regions.id", ondelete="SET NULL"))
    fact_path = Column(String)
    observed_text = Column(Text)
    kind = Column(String, default="OCR_REGION")
    note = Column(Text)

    violation = relationship("Violations", back_populates="evidence_items")
    image = relationship("InspectionImages")
    region = relationship("OCRTextRegions")


class AuditLogs(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=new_id)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    target = Column(String)
    old_value = Column(JSON)
    new_value = Column(JSON)
    source = Column(String, default="INSPECTOR")
    created_at = Column(DateTime(timezone=True), default=now_utc)

    inspection = relationship("Inspections", back_populates="audit_logs")


class Reports(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=new_id)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), unique=True, nullable=False)
    rule_set_version = Column(String)
    storage_path = Column(String)
    summary = Column(JSON, default=dict)
    generated_at = Column(DateTime(timezone=True), default=now_utc)

    inspection = relationship("Inspections", back_populates="report")
