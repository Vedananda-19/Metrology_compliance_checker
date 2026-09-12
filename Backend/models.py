from sqlalchemy import Column, Integer, Float, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, embedding_column
from datetime import datetime, timezone
import uuid


def new_id():
    return str(uuid.uuid4())


def now_utc():
    return datetime.now(timezone.utc)


ROLES = ["OFFICER", "INSPECTOR"]
STAGES = ["ASSIGNED", "IN_PROGRESS", "ACTION_REQUIRED", "RESOLVED"]
DECISIONS = ["CONFIRMED", "DISMISSED", "VERIFIED_COMPLIANT", "VERIFIED_NON_COMPLIANT"]


class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=new_id)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, nullable=False, default="OFFICER")

    inspections = relationship("Inspections", foreign_keys="Inspections.user_id", back_populates="inspector")


class Inspections(Base):
    __tablename__ = "inspections"

    id = Column(String, primary_key=True, default=new_id)
    reference = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    status = Column(String, nullable=False, default="DRAFT")
    stage = Column(String, nullable=False, default=STAGES[0])
    assigned_to = Column(String, ForeignKey("users.id"))
    note = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    inspector = relationship("Users", foreign_keys=[user_id], back_populates="inspections")
    assignee = relationship("Users", foreign_keys=[assigned_to])
    images = relationship("InspectionImages", back_populates="inspection", cascade="all, delete-orphan")
    ocr_texts = relationship("OcrTexts", back_populates="inspection", cascade="all, delete-orphan")
    declarations = relationship("Declarations", back_populates="inspection", cascade="all, delete-orphan")
    evaluation = relationship("Evaluations", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("FindingReviews", back_populates="inspection", cascade="all, delete-orphan")
    font_measurements = relationship("FontMeasurements", back_populates="inspection", cascade="all, delete-orphan")


class InspectionImages(Base):
    __tablename__ = "inspection_images"

    id = Column(String, primary_key=True, default=new_id)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    storage_path = Column(String, nullable=False)
    original_filename = Column(String)
    content_type = Column(String)
    display_order = Column(Integer, default=0)

    inspection = relationship("Inspections", back_populates="images")


class OcrTexts(Base):
    __tablename__ = "ocr_texts"

    id = Column(String, primary_key=True, default=new_id)
    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    image_id = Column(String, ForeignKey("inspection_images.id", ondelete="CASCADE"))
    display_order = Column(Integer, default=0)
    text = Column(Text, nullable=False)

    inspection = relationship("Inspections", back_populates="ocr_texts")
    image = relationship("InspectionImages")


class Declarations(Base):
    __tablename__ = "declarations"

    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), primary_key=True)
    field = Column(String, primary_key=True)
    value = Column(String)
    confidence = Column(Float)

    inspection = relationship("Inspections", back_populates="declarations")


class Evaluations(Base):
    __tablename__ = "evaluations"

    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), primary_key=True)
    verdict = Column(String)
    result = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    inspection = relationship("Inspections", back_populates="evaluation")


class FindingReviews(Base):
    __tablename__ = "finding_reviews"

    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), primary_key=True)
    rule_id = Column(String, primary_key=True)
    decision = Column(String, nullable=False)
    note = Column(Text)
    reviewed_by = Column(String, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True), default=now_utc)

    inspection = relationship("Inspections", back_populates="reviews")
    reviewer = relationship("Users")


class FontMeasurements(Base):
    __tablename__ = "font_measurements"

    inspection_id = Column(String, ForeignKey("inspections.id", ondelete="CASCADE"), primary_key=True)
    field = Column(String, primary_key=True)
    measured_height_px = Column(Float)
    measured_height_mm = Column(Float)
    reference_size_mm = Column(Float, nullable=False)
    reference_size_px = Column(Float)
    scale_mm_per_pixel = Column(Float)
    confidence = Column(Float, default=0.0)
    status = Column(String, nullable=False)
    detail = Column(String)

    inspection = relationship("Inspections", back_populates="font_measurements")


class RulePassages(Base):
    __tablename__ = "rule_passages"

    id = Column(String, primary_key=True, default=new_id)
    rule_ref = Column(String, nullable=False)
    pdf_page = Column(Integer)
    text = Column(Text, nullable=False)
    embedding = Column(embedding_column(), nullable=True)
