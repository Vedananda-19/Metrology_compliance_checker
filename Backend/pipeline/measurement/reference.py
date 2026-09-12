import cv2
import numpy as np
from config import ARUCO_DICT, MARKER_MIN_SIDE_PX, MARKER_MAX_SIDE_RATIO

_detector = None


def detector():
    global _detector
    if _detector is None:
        dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, ARUCO_DICT))
        _detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    return _detector


def side_lengths(corners) -> list[float]:
    points = corners.reshape(4, 2).astype(float)
    return [float(np.linalg.norm(points[i] - points[(i + 1) % 4])) for i in range(4)]


def usable(sides: list[float]) -> bool:
    longest, shortest = max(sides), min(sides)
    if shortest < MARKER_MIN_SIDE_PX:
        return False
    return longest / shortest <= MARKER_MAX_SIDE_RATIO


def find_scale(image, reference_size_mm: float) -> dict:
    if not reference_size_mm or reference_size_mm <= 0:
        return {"status": "INVALID_REFERENCE_SIZE"}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector().detectMarkers(gray)
    if ids is None or not len(corners):
        return {"status": "MARKER_NOT_DETECTED"}

    candidates = [side_lengths(entry) for entry in corners]
    best = max(candidates, key=lambda sides: sum(sides) / 4)
    if not usable(best):
        return {"status": "MARKER_UNUSABLE"}

    side_px = sum(best) / 4
    squareness = min(best) / max(best)
    return {
        "status": "OK",
        "reference_size_px": round(side_px, 2),
        "scale_mm_per_pixel": reference_size_mm / side_px,
        "confidence": round(squareness, 3),
    }
