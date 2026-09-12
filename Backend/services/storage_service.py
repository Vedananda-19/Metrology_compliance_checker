from fastapi import HTTPException
from config import (
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_BUCKET,
    USE_SUPABASE_STORAGE,
    LOCAL_UPLOAD_DIR,
)
from pathlib import Path
import logging
import httpx

logger = logging.getLogger(__name__)

TIMEOUT = 30


def headers(content_type: str | None = None) -> dict:
    values = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    if content_type:
        values["Content-Type"] = content_type
    return values


def api(path: str) -> str:
    return f"{SUPABASE_URL}/storage/v1{path}"


def local_path(storage_path: str) -> Path:
    return Path(LOCAL_UPLOAD_DIR) / storage_path


def list_buckets() -> list[dict]:
    response = httpx.get(api("/bucket"), headers=headers(), timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def ensure_bucket(public: bool = False) -> str:
    if not USE_SUPABASE_STORAGE:
        return "local disk"
    if any(bucket["name"] == SUPABASE_BUCKET for bucket in list_buckets()):
        return "already present"

    response = httpx.post(
        api("/bucket"),
        headers=headers("application/json"),
        json={"id": SUPABASE_BUCKET, "name": SUPABASE_BUCKET, "public": public},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return "created"


def upload(storage_path: str, data: bytes, content_type: str = "image/jpeg"):
    if not USE_SUPABASE_STORAGE:
        target = local_path(storage_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return storage_path

    try:
        response = httpx.post(
            api(f"/object/{SUPABASE_BUCKET}/{storage_path}"),
            headers={**headers(content_type), "x-upsert": "true"},
            content=data,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except Exception as error:
        logger.exception("Supabase upload failed")
        raise HTTPException(502, f"Image upload failed: {error}")
    return storage_path


def download(storage_path: str) -> bytes:
    if not USE_SUPABASE_STORAGE:
        target = local_path(storage_path)
        if not target.exists():
            raise HTTPException(404, "Image file is missing from storage")
        return target.read_bytes()

    try:
        response = httpx.get(
            api(f"/object/{SUPABASE_BUCKET}/{storage_path}"), headers=headers(), timeout=TIMEOUT
        )
        if response.status_code == 404:
            raise HTTPException(404, "Image file is missing from storage")
        response.raise_for_status()
        return response.content
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Supabase download failed")
        raise HTTPException(502, f"Image download failed: {error}")


def remove(storage_path: str):
    if not USE_SUPABASE_STORAGE:
        target = local_path(storage_path)
        if target.exists():
            target.unlink()
        return

    try:
        httpx.request(
            "DELETE",
            api(f"/object/{SUPABASE_BUCKET}/{storage_path}"),
            headers=headers(),
            timeout=TIMEOUT,
        )
    except Exception:
        logger.exception("Supabase delete failed")


def signed_url(storage_path: str, expires_in: int = 3600):
    if not USE_SUPABASE_STORAGE:
        return None

    try:
        response = httpx.post(
            api(f"/object/sign/{SUPABASE_BUCKET}/{storage_path}"),
            headers=headers("application/json"),
            json={"expiresIn": expires_in},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return f"{SUPABASE_URL}/storage/v1{response.json()['signedURL']}"
    except Exception:
        logger.exception("Supabase signed url failed")
        return None
