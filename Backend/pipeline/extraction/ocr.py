import logging
import threading
from pathlib import Path

import cv2
from config import MAX_IMAGE_EDGE, VISION_CREDENTIALS_PATH
from pipeline.preprocessing.images import decode, resize

logger = logging.getLogger(__name__)

_client = None
_lock = threading.Lock()


def credentials_path() -> Path | None:
    if not VISION_CREDENTIALS_PATH:
        return None
    path = Path(VISION_CREDENTIALS_PATH)
    return path if path.is_file() else None


def get_client():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                from google.cloud import vision
                from google.oauth2 import service_account

                path = credentials_path()
                if path is None:
                    raise RuntimeError(
                        "Google Cloud Vision credentials are missing. Set GOOGLE_APPLICATION_CREDENTIALS "
                        "or VISION_CREDENTIALS_PATH to a service-account JSON with Cloud Vision enabled."
                    )
                credentials = service_account.Credentials.from_service_account_file(str(path))
                _client = vision.ImageAnnotatorClient(credentials=credentials)
    return _client


def annotate(data: bytes):
    from google.cloud import vision

    image = resize(decode(data), MAX_IMAGE_EDGE)
    ok, encoded = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not ok:
        raise RuntimeError("Could not encode the image for OCR")

    response = get_client().document_text_detection(
        image=vision.Image(content=encoded.tobytes()),
        image_context=vision.ImageContext(language_hints=["en", "hi"]),
    )
    if response.error.message:
        raise RuntimeError(f"Cloud Vision OCR failed: {response.error.message}")
    return response


def read_text(data: bytes) -> str:
    return read_document(data)[0]


def word_boxes(response) -> list[dict]:
    words = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    text = "".join(symbol.text for symbol in word.symbols)
                    xs = [vertex.x for vertex in word.bounding_box.vertices]
                    ys = [vertex.y for vertex in word.bounding_box.vertices]
                    if not text.strip() or not xs or not ys:
                        continue
                    words.append(
                        {
                            "text": text,
                            "x": min(xs),
                            "y": min(ys),
                            "width": max(xs) - min(xs),
                            "height": max(ys) - min(ys),
                        }
                    )
    return words


def read_document(data: bytes) -> tuple[str, list[dict]]:
    response = annotate(data)
    text = (response.full_text_annotation.text or "").strip()
    if not text:
        annotations = response.text_annotations or []
        if annotations:
            text = (annotations[0].description or "").strip()
    return text, word_boxes(response)
