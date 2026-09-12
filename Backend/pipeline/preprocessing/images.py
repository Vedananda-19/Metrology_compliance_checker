import cv2
import numpy as np
from config import BLUR_MIN_VARIANCE, BLUR_SAMPLE_EDGE, MAX_IMAGE_EDGE


def decode(data: bytes):
    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Image could not be decoded")
    return image


def resize(image, max_edge: int = MAX_IMAGE_EDGE):
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_edge:
        return image
    factor = max_edge / longest
    return cv2.resize(image, (int(width * factor), int(height * factor)), interpolation=cv2.INTER_AREA)


def enhance(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    channels = list(cv2.split(lab))
    channels[0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(channels[0])
    return cv2.cvtColor(cv2.merge(channels), cv2.COLOR_LAB2BGR)


def prepare(data: bytes):
    return enhance(resize(decode(data)))


def laplacian_variance(image) -> float:
    sample = resize(image, BLUR_SAMPLE_EDGE)
    gray = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def too_blurry(data: bytes) -> bool:
    return laplacian_variance(decode(data)) < BLUR_MIN_VARIANCE
