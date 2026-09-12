import re

import cv2
import numpy as np
from pydantic import BaseModel
from config import MIN_MEASUREMENT_CONFIDENCE, MIN_CHARACTER_PIXELS

MEASURED = "MEASURED"
UNABLE = "UNABLE_TO_VERIFY"
PASS = "PASS"
FAIL = "FAIL"


class FontMeasurement(BaseModel):
    field: str
    measured_height_px: float | None = None
    measured_height_mm: float | None = None
    reference_size_mm: float
    reference_size_px: float | None = None
    scale_mm_per_pixel: float | None = None
    confidence: float = 0.0
    status: str = UNABLE
    detail: str | None = None


def tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[0-9a-z]+", str(text).lower()) if token]


def locate(value: str, words: list[dict]) -> dict | None:
    wanted = tokens(value)
    if not wanted or not words:
        return None

    normalised = [tokens(word["text"]) for word in words]
    best = None
    for start in range(len(words)):
        matched = 0
        while start + matched < len(words) and matched < len(wanted):
            if normalised[start + matched] != [wanted[matched]]:
                break
            matched += 1
        if matched and (best is None or matched > best[1]):
            best = (start, matched)

    if best is None:
        return None

    start, count = best
    span = words[start:start + count]
    left = min(word["x"] for word in span)
    top = min(word["y"] for word in span)
    right = max(word["x"] + word["width"] for word in span)
    bottom = max(word["y"] + word["height"] for word in span)
    return {"x": left, "y": top, "width": right - left, "height": bottom - top, "words": count}


SAMPLE_CONFIDENCE = {0: 0.0, 1: 0.55, 2: 0.8}


def character_height_px(image, box: dict) -> tuple[float, int] | None:
    pad = max(2, int(box["height"] * 0.15))
    top = max(0, box["y"] - pad)
    left = max(0, box["x"] - pad)
    crop = image[top:box["y"] + box["height"] + pad, left:box["x"] + box["width"] + pad]
    if crop.size == 0 or min(crop.shape[:2]) < MIN_CHARACTER_PIXELS:
        return None

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    heights = candidate_heights(gray, adaptive(gray))
    if len(heights) < 2:
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        heights = max(heights, candidate_heights(gray, otsu), key=len)

    if not heights:
        return None
    return float(np.median(heights)), len(heights)


def adaptive(gray):
    block = max(11, min(gray.shape[0], gray.shape[1]) | 1)
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block, 10
    )


def candidate_heights(gray, binary) -> list[float]:
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    heights = []
    for contour in contours:
        _, _, width, height = cv2.boundingRect(contour)
        if height < MIN_CHARACTER_PIXELS or height > gray.shape[0] * 0.95:
            continue
        if width > height * 6:
            continue
        heights.append(float(height))
    return heights


def measure(field: str, value: str, image, words: list[dict], scale: dict, reference_size_mm: float) -> FontMeasurement:
    result = FontMeasurement(field=field, reference_size_mm=reference_size_mm)

    if scale.get("status") != "OK":
        result.detail = scale.get("status")
        return result

    result.reference_size_px = scale["reference_size_px"]
    result.scale_mm_per_pixel = scale["scale_mm_per_pixel"]

    box = locate(value, words)
    if box is None:
        result.detail = "REGION_NOT_FOUND"
        return result

    measured = character_height_px(image, box)
    if measured is None:
        result.detail = "SEGMENTATION_FAILED"
        return result

    height_px, samples = measured
    evidence = SAMPLE_CONFIDENCE.get(samples, 1.0)
    confidence = round(scale["confidence"] * evidence * min(1.0, height_px / (MIN_CHARACTER_PIXELS * 2)), 3)
    if confidence < MIN_MEASUREMENT_CONFIDENCE:
        result.confidence = confidence
        result.detail = "LOW_CONFIDENCE"
        return result

    result.measured_height_px = round(height_px, 2)
    result.measured_height_mm = round(height_px * scale["scale_mm_per_pixel"], 2)
    result.confidence = confidence
    result.status = MEASURED
    return result


RULE7_MIN_HEIGHT_MM = [(50, 1.0), (100, 1.5), (500, 2.5), (2500, 4.0), (None, 6.0)]


def required_height_for_area(pdp_area_cm2: float | None) -> float | None:
    if pdp_area_cm2 is None or pdp_area_cm2 <= 0:
        return None
    for upper, height in RULE7_MIN_HEIGHT_MM:
        if upper is None or pdp_area_cm2 <= upper:
            return height
    return None


def check_minimum_font_size(measured_height_mm: float | None, required_height_mm: float | None) -> str:
    if measured_height_mm is None or required_height_mm is None:
        return UNABLE
    if measured_height_mm <= 0 or required_height_mm <= 0:
        return UNABLE
    return PASS if measured_height_mm >= required_height_mm else FAIL
