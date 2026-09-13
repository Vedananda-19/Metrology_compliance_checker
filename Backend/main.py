from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, enable_pgvector
from config import ALLOWED_ORIGINS, LLM_ENABLED, LLM_MODEL, USE_SUPABASE_STORAGE, OCR_LANG
from routes.auth_router import auth_router
from routes.inspection_router import inspection_router
from routes.rule_router import rule_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

enable_pgvector()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Packaged Commodity Compliance Prototype")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)
app.include_router(auth_router)
app.include_router(inspection_router)
app.include_router(rule_router)


@app.exception_handler(Exception)
async def unhandled_error(request: Request, error: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on the server"})


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_enabled": LLM_ENABLED,
        "llm_model": LLM_MODEL if LLM_ENABLED else None,
        "ocr": f"paddleocr:{OCR_LANG}",
        "storage": "supabase" if USE_SUPABASE_STORAGE else "local",
    }
