import logging
import threading

import numpy as np
from config import MAX_IMAGE_EDGE, OCR_LANG
from pipeline.preprocessing.images import decode, resize

logger = logging.getLogger(__name__)

_engine = None
_lock = threading.Lock()


def get_engine():
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                from paddleocr import PaddleOCR

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
        lines.append(
            {
                "text": text.strip(),
                "x": int(min(xs)),
                "y": int(min(ys)),
                "width": int(max(xs) - min(xs)),
                "height": int(max(ys) - min(ys)),
                "confidence": float(confidence),
            }
        )
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
        words.append(
            {
                "text": token,
                "x": int(line["x"] + offset),
                "y": line["y"],
                "width": max(1, int(span)),
                "height": line["height"],
            }
        )
        offset += span
    return words


def read_document(data: bytes) -> tuple[str, list[dict]]:
    image = resize(decode(data), MAX_IMAGE_EDGE)
    if not isinstance(image, np.ndarray):
        raise RuntimeError("Could not decode the image for OCR")

    lines = _line_boxes(image)
    text = "\n".join(line["text"] for line in lines).strip()

    words = []
    for line in lines:
        words.extend(_split_words(line))
    return text, words


def read_text(data: bytes) -> str:
    return read_document(data)[0]
