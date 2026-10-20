"""Break a picture into a few big, simple shapes.

The idea is the same as blocking in a drawing: before any detail, find the
large masses and see them as ovals, boxes and triangles. The image is
flattened with mean shift, split into color groups with k-means, and each
large region is matched against simple shapes. Whichever simple shape covers
the region best (by overlap) wins; if none is close enough it falls back to a
straight-sided polygon.
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans

WORK_SIDE = 480

# simplicity -> (smallest region as a share of the picture, polygon tolerance, fit needed)
SIMPLICITY = {
    1: (0.003, 0.012, 0.90),
    2: (0.006, 0.018, 0.86),
    3: (0.010, 0.025, 0.82),
    4: (0.018, 0.035, 0.76),
    5: (0.030, 0.050, 0.70),
}

MAX_SHAPES = 30
# anything bigger than this is background (wall, sky, table), not a shape
MAX_REGION = 0.45


def _shrink(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    scale = WORK_SIDE / max(h, w)
    if scale >= 1:
        return img
    return cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)


def is_drawing(img: np.ndarray) -> bool:
    """Pencil or ink on paper: mostly light, and one color throughout
    (the paper can be tinted, like old sepia sheets)."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    chroma = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    spread = float(np.percentile(chroma, 95) - np.median(chroma))
    return spread < 10 and float(np.median(lab[..., 0])) > 150


def _color_masks(img: np.ndarray, groups: int, seed: int):
    flat = cv2.pyrMeanShiftFiltering(img, sp=12, sr=28)
    lab = cv2.cvtColor(flat, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    # lightness counts for less than hue, so a shaded ball stays one ball
    lab[:, 0] *= 0.5
    km = KMeans(n_clusters=groups, n_init=3, random_state=seed).fit(lab[::4])
    labels = km.predict(lab).reshape(img.shape[:2])
    return [(labels == g).astype(np.uint8) for g in range(groups)]


# simplicity -> how far the marks get smudged together, as a share of the picture
SMUDGE = {1: 0.007, 2: 0.011, 3: 0.016, 4: 0.022, 5: 0.03}


def _ink_masks(img: np.ndarray, simplicity: int):
    """Where the marks are dense. Lines on their own aren't shapes, but a
    cluster of them is a mass you'd block in."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    # paper isn't evenly lit, so measure ink against the local paper tone
    k = (max(h, w) // 20) | 1
    paper = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    ink = cv2.subtract(paper, gray)
    density = cv2.GaussianBlur(ink.astype(np.float32), (0, 0), max(h, w) * SMUDGE[simplicity])
    density = cv2.normalize(density, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, mask = cv2.threshold(density, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return [mask]


def _overlap(shape_mask: np.ndarray, region: np.ndarray) -> float:
    inter = np.count_nonzero(shape_mask & region)
    union = np.count_nonzero(shape_mask | region)
    return inter / union if union else 0.0


def _fill(shape, points=None, ellipse=None):
    mask = np.zeros(shape, np.uint8)
    if ellipse is not None:
        cv2.ellipse(mask, ellipse, 1, -1)
    else:
        cv2.fillPoly(mask, [np.round(points).astype(np.int32)], 1)
    return mask.astype(bool)


def classify(contour: np.ndarray, size: tuple[int, int], tolerance: float, needed: float):
    """Match one region outline to the simplest shape that fits it."""
    region = _fill(size, points=contour.reshape(-1, 2))
    candidates = []

    if len(contour) >= 5:
        (cx, cy), (a, b), angle = cv2.fitEllipse(contour)
        if a > 1 and b > 1:
            fit = _overlap(_fill(size, ellipse=((cx, cy), (a, b), angle)), region)
            ellipse = {"cx": cx, "cy": cy, "rx": a / 2, "ry": b / 2, "angle": angle}
            candidates.append((fit, "ellipse", ellipse))

    box = cv2.boxPoints(cv2.minAreaRect(contour))
    candidates.append((_overlap(_fill(size, points=box), region), "box", box))

    _, tri = cv2.minEnclosingTriangle(contour.astype(np.float32))
    if tri is not None:
        tri = tri.reshape(-1, 2)
        candidates.append((_overlap(_fill(size, points=tri), region), "triangle", tri))

    fit, kind, geom = max(candidates, key=lambda c: c[0])
    if fit < needed:
        peri = cv2.arcLength(contour, True)
        poly = cv2.approxPolyDP(contour, tolerance * peri, True).reshape(-1, 2)
        if len(poly) >= 3:
            fit, kind, geom = _overlap(_fill(size, points=poly), region), "polygon", poly

    if kind == "ellipse":
        geom = {k: round(float(v), 2) for k, v in geom.items()}
    else:
        geom = {"points": [[round(float(x), 2), round(float(y), 2)] for x, y in geom]}
    return kind, round(float(fit), 3), geom


def find_shapes(img: np.ndarray, simplicity: int = 3, groups: int = 5, seed: int = 0):
    if simplicity not in SIMPLICITY:
        raise ValueError("simplicity must be 1-5")
    min_share, tolerance, needed = SIMPLICITY[simplicity]

    small = _shrink(img)
    h, w = small.shape[:2]
    total = h * w
    drawing = is_drawing(small)
    masks = _ink_masks(small, simplicity) if drawing else _color_masks(small, groups, seed)

    k = max(3, round(min(h, w) * 0.012)) | 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))

    found = []
    for mask in masks:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            share = cv2.contourArea(c) / total
            if min_share <= share <= MAX_REGION:
                found.append((share, c))

    # biggest first: that's the order you'd block them in
    found.sort(key=lambda f: f[0], reverse=True)
    shapes = []
    for share, c in found[:MAX_SHAPES]:
        kind, fit, geom = classify(c, (h, w), tolerance, needed)
        m = cv2.moments(c)
        shapes.append(
            {
                "kind": kind,
                "fit": fit,
                "share": round(share, 4),
                "center": [round(m["m10"] / m["m00"], 2), round(m["m01"] / m["m00"], 2)],
                **geom,
            }
        )
    return {"width": w, "height": h, "drawing": drawing, "shapes": shapes}
