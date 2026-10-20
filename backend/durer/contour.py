"""Line drawing from an image.

Canny on its own picks up every bit of texture, so the image gets smoothed
with a bilateral filter first (keeps edges, flattens the rest) and the tiny
leftover specks are thrown out afterwards.
"""

import cv2
import numpy as np

# detail level -> (bilateral passes, smallest stroke kept in px)
DETAIL = {
    1: (4, 160),
    2: (3, 90),
    3: (2, 45),
    4: (1, 20),
    5: (0, 8),
}


def auto_canny(gray: np.ndarray, pct: float = 88) -> np.ndarray:
    # thresholds from the gradient itself instead of fixed numbers, so faint
    # pencil scans and contrasty photos both come out usable
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    mag = np.hypot(gx, gy)
    upper = float(np.percentile(mag, pct))
    upper = max(upper, 20.0)
    return cv2.Canny(gx.astype(np.int16), gy.astype(np.int16), 0.4 * upper, upper, L2gradient=True)


def drop_small_strokes(edges: np.ndarray, min_size: int) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(edges, connectivity=8)
    keep = np.zeros(count, dtype=bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= min_size
    return np.where(keep[labels], 255, 0).astype(np.uint8)


def line_drawing(img: np.ndarray, detail: int = 3) -> np.ndarray:
    """Returns a BGRA image: graphite colored lines on a transparent background."""
    if detail not in DETAIL:
        raise ValueError("detail must be 1-5")
    passes, min_size = DETAIL[detail]

    smooth = img
    for _ in range(passes):
        smooth = cv2.bilateralFilter(smooth, 9, 60, 60)

    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = auto_canny(gray)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
    edges = drop_small_strokes(edges, min_size)

    # soften so the lines look more like pencil than pixels
    alpha = cv2.GaussianBlur(edges, (3, 3), 0)

    h, w = edges.shape
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., 0] = 52  # B
    out[..., 1] = 54  # G
    out[..., 2] = 58  # R
    out[..., 3] = alpha
    return out
