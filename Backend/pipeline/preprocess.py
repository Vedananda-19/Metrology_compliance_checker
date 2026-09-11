import cv2
import numpy as np
from config import MAX_IMAGE_EDGE


def decode(data: bytes):
    array = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Image could not be decoded")
    return image


def scale_to_max_edge(image, max_edge: int = MAX_IMAGE_EDGE):
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_edge:
        return image, 1.0
    factor = max_edge / longest
    resized = cv2.resize(image, (int(width * factor), int(height * factor)), interpolation=cv2.INTER_AREA)
    return resized, factor


def estimate_skew(gray) -> float:
    edges = cv2.Canny(gray, 60, 180)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 120, minLineLength=gray.shape[1] // 3, maxLineGap=20)
    if lines is None:
        return 0.0
    angles = []
    for x1, y1, x2, y2 in lines[:, 0]:
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if abs(angle) < 20:
            angles.append(angle)
    if not angles:
        return 0.0
    return float(np.median(angles))


def deskew(image, angle: float):
    if abs(angle) < 0.4:
        return image
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    return cv2.warpAffine(image, matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def enhance(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    channels = list(cv2.split(lab))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    channels[0] = clahe.apply(channels[0])
    merged = cv2.merge(channels)
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def prepare(data: bytes):
    original = decode(data)
    height, width = original.shape[:2]
    scaled, factor = scale_to_max_edge(original)
    gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
    angle = estimate_skew(gray)
    processed = enhance(deskew(scaled, angle))
    return {
        "original": original,
        "processed": processed,
        "width": width,
        "height": height,
        "scale": factor,
        "skew_angle": angle,
    }
