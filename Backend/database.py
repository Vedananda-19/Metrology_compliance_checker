from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
from config import EMBEDDING_DIM
from pathlib import Path
import os


def current_branch() -> str:
    head = Path(__file__).resolve().parent.parent / ".git" / "HEAD"
    try:
        text = head.read_text(encoding="utf-8").strip()
    except OSError:
        return "default"
    if text.startswith("ref:"):
        return text.split("refs/heads/", 1)[-1].replace("/", "-") or "default"
    return text[:7]


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///./data/app-{current_branch()}.db"

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
IS_POSTGRES = DATABASE_URL.startswith("postgres")

if IS_POSTGRES:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
else:
    os.makedirs("data", exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def embedding_column():
    if IS_POSTGRES:
        from pgvector.sqlalchemy import Vector

        return Vector(EMBEDDING_DIM)
    return JSON


def enable_pgvector():
    if not IS_POSTGRES:
        return
    from sqlalchemy import text

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
