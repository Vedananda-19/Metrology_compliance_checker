from io import BytesIO

import numpy as np
from PIL import Image
from config import BLUR_MIN_VARIANCE, BLUR_SAMPLE_EDGE, MAX_IMAGE_EDGE

# Images are numpy arrays in BGR channel order (the OpenCV convention) so the
# optional font-measurement code can consume them unchanged. Decode/resize/encode
# go through Pillow so the core pipeline imports no OpenCV (and no libgomp) at boot.


def decode(data: bytes):
    try:
        image = Image.open(BytesIO(data)).convert("RGB")
    except Exception as error:
        raise ValueError("Image could not be decoded") from error
    return np.asarray(image)[:, :, ::-1].copy()


def _to_pil(image) -> Image.Image:
    return Image.fromarray(image[:, :, ::-1])


def resize(image, max_edge: int = MAX_IMAGE_EDGE):
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_edge:
        return image
    factor = max_edge / longest
    resized = _to_pil(image).resize((int(width * factor), int(height * factor)), Image.LANCZOS)
    return np.asarray(resized)[:, :, ::-1].copy()


def encode_jpeg(image, quality: int = 90) -> bytes:
    buffer = BytesIO()
    _to_pil(image).save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()


def laplacian_variance(image) -> float:
    gray = np.asarray(_to_pil(image).convert("L"), dtype=np.float64)
    laplacian = (
        -4.0 * gray
        + np.roll(gray, 1, axis=0) + np.roll(gray, -1, axis=0)
        + np.roll(gray, 1, axis=1) + np.roll(gray, -1, axis=1)
    )
    return float(laplacian.var())


def too_blurry(data: bytes) -> bool:
    return laplacian_variance(resize(decode(data), BLUR_SAMPLE_EDGE)) < BLUR_MIN_VARIANCE
