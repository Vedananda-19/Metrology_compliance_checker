from sqlalchemy import Column, Integer, Float, String, Text, JSON, DateTime, ForeignKey
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
    full_name = Column(String)

    inspections = relationship("Inspections", back_populates="inspector")


class Inspections(Base):
    __tablename__ = "inspections"

    id = Column(String, primary_key=True, default=new_id)
    reference = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    status = Column(String, nullable=False, default="DRAFT")
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    inspector = relationship("Users", back_populates="inspections")
    images = relationship("InspectionImages", back_populates="inspection", cascade="all, delete-orphan")
    ocr_texts = relationship("OcrTexts", back_populates="inspection", cascade="all, delete-orphan")
    declarations = relationship("Declarations", back_populates="inspection", cascade="all, delete-orphan")
    evaluation = relationship("Evaluations", back_populates="inspection", uselist=False, cascade="all, delete-orphan")


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


class RulePassages(Base):
    __tablename__ = "rule_passages"

    id = Column(String, primary_key=True, default=new_id)
    rule_ref = Column(String, nullable=False)
    pdf_page = Column(Integer)
    text = Column(Text, nullable=False)
    embedding = Column(embedding_column(), nullable=True)
