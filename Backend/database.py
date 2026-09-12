from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
from config import EMBEDDING_DIM
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
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
