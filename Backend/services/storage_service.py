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

logger = logging.getLogger(__name__)

_client = None


def get_client():
    global _client
    if not USE_SUPABASE_STORAGE:
        return None
    if _client is None:
        from supabase import create_client

        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def local_path(storage_path: str) -> Path:
    return Path(LOCAL_UPLOAD_DIR) / storage_path


def upload(storage_path: str, data: bytes, content_type: str = "image/jpeg"):
    client = get_client()
    if client is None:
        target = local_path(storage_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return storage_path

    try:
        client.storage.from_(SUPABASE_BUCKET).upload(
            storage_path, data, {"content-type": content_type, "upsert": "true"}
        )
    except Exception as error:
        logger.exception("Supabase upload failed")
        raise HTTPException(502, f"Image upload failed: {error}")
    return storage_path


def download(storage_path: str) -> bytes:
    client = get_client()
    if client is None:
        target = local_path(storage_path)
        if not target.exists():
            raise HTTPException(404, "Image file is missing from storage")
        return target.read_bytes()

    try:
        return client.storage.from_(SUPABASE_BUCKET).download(storage_path)
    except Exception as error:
        logger.exception("Supabase download failed")
        raise HTTPException(502, f"Image download failed: {error}")


def remove(storage_path: str):
    client = get_client()
    if client is None:
        target = local_path(storage_path)
        if target.exists():
            target.unlink()
        return

    try:
        client.storage.from_(SUPABASE_BUCKET).remove([storage_path])
    except Exception:
        logger.exception("Supabase delete failed")


def signed_url(storage_path: str, expires_in: int = 3600):
    client = get_client()
    if client is None:
        return None
    try:
        result = client.storage.from_(SUPABASE_BUCKET).create_signed_url(storage_path, expires_in)
        return result.get("signedURL") or result.get("signed_url")
    except Exception:
        logger.exception("Supabase signed url failed")
        return None
