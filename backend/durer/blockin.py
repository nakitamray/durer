"""The early stages of a drawing, before any real lines go down.

1. placement: where the subject starts and stops, and which way it leans
2. big shapes: the whole silhouette as a handful of straight lines
3. medium shapes: the same silhouette with more corners, plus the main
   shadow shapes inside it
4. notan: everything split into just light and shadow

All of it is worked out from a mask of the subject and a shadow mask, at a
small working size. Coordinates come back in that working size along with
its width and height, so the frontend can scale them to the picture.
"""

import cv2
import numpy as np

from . import marks

WORK_SIDE = 520

# simplicity of the straight-line versions, as a share of the outline's length
BIG = 0.035
MEDIUM = 0.012
SHADOW = 0.02

# notan: bias 1 (more light) .. 5 (more shadow) scales the automatic threshold
BIAS = {1: 0.8, 2: 0.9, 3: 1.0, 4: 1.1, 5: 1.2}


def _fill_holes(mask: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    out = np.zeros(mask.shape, np.uint8)
    cv2.drawContours(out, contours, -1, 1, -1)
    return out.astype(bool)


def _tidy(mask: np.ndarray, size: float) -> np.ndarray:
    k = max(3, round(size)) | 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel).astype(bool)


def subject_mask(img: np.ndarray, drawing: bool) -> np.ndarray:
    h, w = img.shape[:2]
    side = max(h, w)
    if drawing:
        d = marks.density(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 0.012)
        level, _ = cv2.threshold(d, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        mask = d > level * 0.6
        mask = cv2.morphologyEx(
            mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((side // 30,) * 2, np.uint8)
        ).astype(bool)
    else:
        # grabcut, assuming the subject sits inside the frame with a little room
        gc = np.zeros((h, w), np.uint8)
        inset = max(2, round(side * 0.03))
        rect = (inset, inset, w - 2 * inset, h - 2 * inset)
        bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        cv2.grabCut(img, gc, rect, bg, fg, 5, cv2.GC_INIT_WITH_RECT)
        mask = (gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)
        mask = _tidy(mask, side * 0.012)

    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if count <= 1:
        return np.ones((h, w), bool)
    areas = stats[1:, cv2.CC_STAT_AREA]
    keep = np.zeros(count, bool)
    keep[1:] = areas >= areas.max() * 0.12
    return _fill_holes(keep[labels])


def shadow_mask(img: np.ndarray, drawing: bool, bias: int = 3) -> np.ndarray:
    if bias not in BIAS:
        raise ValueError("bias must be 1-5")
    h, w = img.shape[:2]
    side = max(h, w)
    if drawing:
        # in a drawing the shadows are wherever it's been hatched in
        cover = marks.coverage(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        shadow = cover > 0.3 / BIAS[bias]
        shadow = _tidy(shadow, side * 0.01)
        shadow = marks.keep_large(shadow, int(h * w * 0.004))
        return ~marks.keep_large(~shadow, int(h * w * 0.0015))
    else:
        smooth = cv2.bilateralFilter(img, 9, 40, 40)
        gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
        dark = 255 - cv2.GaussianBlur(gray, (0, 0), side * 0.006)
    level, _ = cv2.threshold(dark, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # more shadow = a lower bar for counting as dark
    shadow = dark > level / BIAS[bias]
    shadow = _tidy(shadow, side * 0.01)
    shadow = marks.keep_large(shadow, int(h * w * 0.0015))
    # small specks of light inside a shadow get swallowed too
    return ~marks.keep_large(~shadow, int(h * w * 0.0015))


def _closed(c: np.ndarray) -> list[list[float]]:
    return [[round(float(x), 1), round(float(y), 1)] for x, y in c.reshape(-1, 2)]


def _simplify(mask: np.ndarray, share: float, min_area: float, mode=cv2.RETR_EXTERNAL):
    contours, _ = cv2.findContours(mask.astype(np.uint8), mode, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in sorted(contours, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(c) < min_area:
            continue
        poly = cv2.approxPolyDP(c, share * cv2.arcLength(c, True), True)
        if len(poly) >= 3:
            out.append(_closed(poly))
    return out


def placement(subject: np.ndarray) -> dict:
    ys, xs = np.nonzero(subject)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    cx, cy = float(xs.mean()), float(ys.mean())

    # the long axis of the subject: its overall lean or gesture
    pts = np.stack([xs - cx, ys - cy], axis=1).astype(np.float64)
    _, vecs = np.linalg.eigh(np.cov(pts.T))
    dx, dy = vecs[:, -1]
    if dy < 0:
        dx, dy = -dx, -dy
    proj = pts @ np.array([dx, dy])
    lo, hi = float(proj.min()), float(proj.max())
    lean = float(np.degrees(np.arctan2(dx, dy)))  # 0 = straight up and down

    return {
        "box": [x0, y0, x1, y1],
        "center": [round(cx, 1), round(cy, 1)],
        "axis": [
            [round(cx + dx * lo, 1), round(cy + dy * lo, 1)],
            [round(cx + dx * hi, 1), round(cy + dy * hi, 1)],
        ],
        "lean": round(lean, 1),
    }


def to_path(polys: list[list[list[float]]]) -> str:
    """Closed polygons as one svg path, holes and all (use fill-rule evenodd)."""
    parts = []
    for p in polys:
        head = f"M{p[0][0]} {p[0][1]}"
        parts.append(head + "".join(f"L{x} {y}" for x, y in p[1:]) + "Z")
    return "".join(parts)


def block_in(img: np.ndarray) -> dict:
    small = marks.shrink(img, WORK_SIDE)
    h, w = small.shape[:2]
    area = h * w
    drawing = marks.is_drawing(small)

    subject = subject_mask(small, drawing)
    shadow = shadow_mask(small, drawing) & subject

    medium = _simplify(subject, MEDIUM, area * 0.004)
    medium += _simplify(shadow, SHADOW, area * 0.006)

    return {
        "width": w,
        "height": h,
        "drawing": drawing,
        "placement": placement(subject),
        "big": _simplify(subject, BIG, area * 0.01),
        "medium": medium,
    }


def notan(img: np.ndarray, bias: int = 3) -> dict:
    small = marks.shrink(img, WORK_SIDE)
    h, w = small.shape[:2]
    shadow = shadow_mask(small, marks.is_drawing(small), bias)
    contours, _ = cv2.findContours(shadow.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    for c in contours:
        poly = cv2.approxPolyDP(c, 1.2, True)
        if len(poly) >= 3:
            polys.append(_closed(poly))
    return {
        "width": w,
        "height": h,
        "path": to_path(polys),
        "shadow": round(float(shadow.mean()), 4),
    }
