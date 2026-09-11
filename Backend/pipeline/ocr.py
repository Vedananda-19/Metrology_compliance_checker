import logging
import threading

_engine = None
_lock = threading.Lock()

logger = logging.getLogger(__name__)


def get_engine():
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                from paddleocr import PaddleOCR

                _engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _engine


def normalize_polygon(polygon, scale: float):
    points = []
    for point in polygon:
        x = int(round(float(point[0]) / scale))
        y = int(round(float(point[1]) / scale))
        points.append([max(x, 0), max(y, 0)])
    return points


def bounding_box(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def read_regions(processed_image, scale: float = 1.0):
    engine = get_engine()
    raw = engine.ocr(processed_image, cls=True)

    regions = []
    for page in raw or []:
        for entry in page or []:
            polygon, (text, confidence) = entry[0], entry[1]
            text = (text or "").strip()
            if not text:
                continue
            points = normalize_polygon(polygon, scale)
            x1, y1, x2, y2 = bounding_box(points)
            regions.append(
                {
                    "text": text,
                    "confidence": float(confidence),
                    "polygon": points,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                }
            )

    regions.sort(key=lambda r: (r["y1"], r["x1"]))
    for index, region in enumerate(regions):
        region["reading_order"] = index
    return regions


def run(prepared: dict):
    try:
        regions = read_regions(prepared["processed"], prepared["scale"])
    except Exception as error:
        logger.exception("OCR failed")
        return {"status": "FAILED", "regions": [], "mean_confidence": None, "error": str(error)}

    if not regions:
        return {"status": "EMPTY", "regions": [], "mean_confidence": None, "error": None}

    mean_confidence = sum(r["confidence"] for r in regions) / len(regions)
    return {"status": "DONE", "regions": regions, "mean_confidence": mean_confidence, "error": None}


def joined_text(regions) -> str:
    return " ".join(r["text"] for r in sorted(regions, key=lambda r: r.get("reading_order", 0)))
