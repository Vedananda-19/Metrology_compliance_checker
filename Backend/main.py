from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import Base, engine, enable_pgvector
from config import ALLOWED_ORIGINS, LLM_ENABLED, LLM_MODEL, RULE_SET_VERSION, USE_SUPABASE_STORAGE
from routes.auth_router import auth_router
from routes.inspection_router import inspection_router
from routes.report_router import report_router
from routes.rule_router import rule_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

enable_pgvector()
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from services import processing_service

    app.state.pipeline = processing_service.get_pipeline()
    logger.info(
        "rule set %s | llm %s | supabase storage %s",
        RULE_SET_VERSION,
        LLM_MODEL if LLM_ENABLED else "disabled (development extraction)",
        "on" if USE_SUPABASE_STORAGE else "local disk",
    )
    yield


app = FastAPI(title="Legal Metrology Compliance Scanner", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)
app.include_router(auth_router)
app.include_router(inspection_router)
app.include_router(report_router)
app.include_router(rule_router)


@app.exception_handler(Exception)
async def unhandled_error(request: Request, error: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on the server"})


@app.get("/")
def home():
    return "Legal Metrology Compliance Scanner API"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "rule_set_version": RULE_SET_VERSION,
        "llm_enabled": LLM_ENABLED,
        "llm_model": LLM_MODEL if LLM_ENABLED else None,
        "storage": "supabase" if USE_SUPABASE_STORAGE else "local",
    }
