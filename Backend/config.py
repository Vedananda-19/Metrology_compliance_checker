from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_HOURS = 12

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "inspection-images")
USE_SUPABASE_STORAGE = bool(SUPABASE_URL and SUPABASE_KEY)
LOCAL_UPLOAD_DIR = os.getenv("LOCAL_UPLOAD_DIR", "uploads")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "3072"))
LLM_ENABLED = bool(LLM_API_KEY)

LEGAL_PDF_PATH = os.getenv("LEGAL_PDF_PATH", "legal/lmpc_2011.pdf")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
MAX_IMAGE_EDGE = 1600
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
BLUR_SAMPLE_EDGE = int(os.getenv("BLUR_SAMPLE_EDGE", "640"))
BLUR_MIN_VARIANCE = float(os.getenv("BLUR_MIN_VARIANCE", "80"))
