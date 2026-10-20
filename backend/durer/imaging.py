import cv2
import numpy as np

MAX_SIDE = 1600
MAX_BYTES = 15 * 1024 * 1024


class ImageError(ValueError):
    pass


def decode(data: bytes, max_side: int = MAX_SIDE) -> np.ndarray:
    """Read uploaded bytes into a BGR array, shrinking anything huge."""
    if not data:
        raise ImageError("empty upload")
    if len(data) > MAX_BYTES:
        raise ImageError("image is larger than 15 MB")

    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ImageError("couldn't read that file as an image")

    h, w = img.shape[:2]
    scale = max_side / max(h, w)
    if scale < 1:
        img = cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def to_gray(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def encode_png(img: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise ImageError("couldn't encode result")
    return buf.tobytes()
