import base64
import logging
import threading

from config import MAX_IMAGE_EDGE, OCR_BACKEND, OCR_LANG
from pipeline.preprocessing.images import decode, resize, encode_jpeg

logger = logging.getLogger(__name__)

_engine = None
_lock = threading.Lock()

VISION_PROMPT = (
    "You are an OCR engine. Transcribe every piece of text printed on this packaged-commodity "
    "label exactly as it appears. Preserve line breaks, one line of the label per line of output. "
    "Keep punctuation, units, symbols and numbers verbatim. Do not translate, correct, summarise or "
    "add any commentary - output only the raw text you can read."
)


# --------------------------------------------------------------------------- OpenRouter vision OCR
def _vision_read(data: bytes) -> str:
    from pipeline import llm
    from langchain_core.messages import HumanMessage

    model = llm.get_model()
    if model is None:
        raise RuntimeError("No LLM API key is configured, so the vision OCR backend cannot run")

    image = resize(decode(data), MAX_IMAGE_EDGE)
    encoded = base64.b64encode(encode_jpeg(image, 80)).decode("ascii")

    message = HumanMessage(content=[
        {"type": "text", "text": VISION_PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}},
    ])
    response = model.invoke([message])
    content = response.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return (content or "").strip()


# --------------------------------------------------------------------------- PaddleOCR (optional, local)
def get_engine():
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                try:
                    from paddleocr import PaddleOCR
                except ImportError as error:
                    raise RuntimeError(
                        "OCR_BACKEND is 'paddle' but paddleocr is not installed. "
                        "Install it with: pip install -r requirements-ocr-paddle.txt"
                    ) from error
                _engine = PaddleOCR(use_angle_cls=True, lang=OCR_LANG, show_log=False)
    return _engine


def _line_boxes(image) -> list[dict]:
    result = get_engine().ocr(image, cls=True)
    if not result or result[0] is None:
        return []

    lines = []
    for entry in result[0]:
        polygon, (text, confidence) = entry
        if not text or not text.strip():
            continue
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        lines.append({
            "text": text.strip(),
            "x": int(min(xs)),
            "y": int(min(ys)),
            "width": int(max(xs) - min(xs)),
            "height": int(max(ys) - min(ys)),
        })
    lines.sort(key=lambda line: (line["y"], line["x"]))
    return lines


def _split_words(line: dict) -> list[dict]:
    tokens = line["text"].split()
    total = sum(len(token) for token in tokens)
    if total == 0:
        return []
    if len(tokens) == 1:
        return [{"text": tokens[0], "x": line["x"], "y": line["y"], "width": line["width"], "height": line["height"]}]

    words = []
    offset = 0.0
    for token in tokens:
        span = line["width"] * (len(token) / total)
        words.append({
            "text": token,
            "x": int(line["x"] + offset),
            "y": line["y"],
            "width": max(1, int(span)),
            "height": line["height"],
        })
        offset += span
    return words


def _paddle_read(data: bytes) -> tuple[str, list[dict]]:
    image = resize(decode(data), MAX_IMAGE_EDGE)
    lines = _line_boxes(image)
    text = "\n".join(line["text"] for line in lines).strip()
    words = []
    for line in lines:
        words.extend(_split_words(line))
    return text, words


# --------------------------------------------------------------------------- public API
def read_document(data: bytes) -> tuple[str, list[dict]]:
    """Return (text, word_boxes). Word boxes are empty for the vision backend."""
    if OCR_BACKEND == "paddle":
        return _paddle_read(data)
    return _vision_read(data), []


def read_text(data: bytes) -> str:
    return read_document(data)[0]
