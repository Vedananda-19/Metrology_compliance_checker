import threading

_engine = None
_lock = threading.Lock()


def get_engine():
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                from paddleocr import PaddleOCR

                _engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _engine


def read_text(image) -> str:
    raw = get_engine().ocr(image, cls=True)
    lines = []
    for page in raw or []:
        for entry in page or []:
            text = (entry[1][0] or "").strip()
            if text:
                lines.append(text)
    return "\n".join(lines)
