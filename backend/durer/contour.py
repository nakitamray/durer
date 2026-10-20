"""Line drawing as vector strokes.

Edges are found as a one-pixel-wide map (Canny for photos, the skeleton of
the ink for drawings), then traced into polylines, simplified and smoothed.
Sending strokes instead of a bitmap means the lines stay crisp at any size
and each one can carry its own weight, like a pen line would.
"""

import cv2
import numpy as np
from skimage.morphology import skeletonize

from . import marks

WORK_SIDE = 1100
MAX_STROKES = 5000

# detail -> (edge percentile, shortest stroke kept in px for photos, for drawings)
# drawings need longer minimums or the hatching swamps the outlines
DETAIL = {
    1: (95, 70, 140),
    2: (92, 40, 80),
    3: (88, 22, 45),
    4: (84, 12, 22),
    5: (80, 6, 8),
}

# 4-neighbours first so the walk follows the line instead of cutting corners
STEPS = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def photo_edges(img: np.ndarray, pct: float) -> tuple[np.ndarray, np.ndarray]:
    smooth = img
    for _ in range(2):
        smooth = cv2.bilateralFilter(smooth, 9, 50, 50)
    gray = cv2.GaussianBlur(cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY), (3, 3), 0)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    mag = np.hypot(gx, gy)
    upper = max(float(np.percentile(mag, pct)), 20.0)
    edges = cv2.Canny(gx.astype(np.int16), gy.astype(np.int16), 0.4 * upper, upper, L2gradient=True)
    # line weight follows edge strength
    strength = mag / (np.percentile(mag[edges > 0], 90) + 1e-6) if edges.any() else mag
    return edges > 0, np.clip(strength, 0, 1.5)


def drawing_edges(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Centre lines of the pen and pencil strokes themselves."""
    mask = marks.lines(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    width = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 3)
    return skeletonize(mask), np.clip(width / 2, 0, 1.5)


def trace(skel: np.ndarray) -> list[list[tuple[int, int]]]:
    """Walk a one-pixel-wide map into separate polylines of (x, y)."""
    ys, xs = np.nonzero(skel)
    on = set(zip(ys.tolist(), xs.tolist(), strict=True))
    kernel = np.ones((3, 3), np.float32)
    kernel[1, 1] = 0
    neighbours = cv2.filter2D(skel.astype(np.uint8), -1, kernel, borderType=cv2.BORDER_CONSTANT)

    seen: set[tuple[int, int]] = set()

    def walk(start):
        path = [start]
        seen.add(start)
        y, x = start
        while True:
            # keep going the way the line is already heading, so a long
            # outline runs straight through places where hatching touches it
            back = path[max(0, len(path) - 4)]
            hy, hx = y - back[0], x - back[1]
            norm = np.hypot(hy, hx) or 1.0
            best, best_score = None, -2.0
            for i, (dy, dx) in enumerate(STEPS):
                n = (y + dy, x + dx)
                if n not in on or n in seen:
                    continue
                score = (hy * dy + hx * dx) / (norm * np.hypot(dy, dx)) if len(path) > 1 else -i
                if score > best_score:
                    best, best_score = n, score
            if best is None:
                break
            if best_score < 0.35 and len(path) > 2 and neighbours[y, x] >= 3:
                # a branch meeting a line at an angle ends here, and leaves
                # the junction free for the line running through it
                seen.discard((y, x))
                return [(px, py) for py, px in path]
            seen.add(best)
            path.append(best)
            y, x = best
        # join back onto whatever it ran into, so junctions and loops close up
        recent = set(path[-4:])
        for dy, dx in STEPS:
            n = (y + dy, x + dx)
            if n in seen and n not in recent:
                path.append(n)
                break
        return [(px, py) for py, px in path]

    ends = [p for p in zip(ys.tolist(), xs.tolist(), strict=True) if neighbours[p] == 1]
    lines = [walk(p) for p in ends if p not in seen]
    for p in zip(ys.tolist(), xs.tolist(), strict=True):
        if p not in seen:
            lines.append(walk(p))
    return lines


def chaikin(pts: np.ndarray, rounds: int = 2) -> np.ndarray:
    for _ in range(rounds):
        if len(pts) < 3:
            break
        a, b = pts[:-1], pts[1:]
        mid = np.empty((2 * len(a), 2))
        mid[0::2] = 0.75 * a + 0.25 * b
        mid[1::2] = 0.25 * a + 0.75 * b
        pts = np.vstack([pts[:1], mid, pts[-1:]])
    return pts


def to_path(pts: np.ndarray) -> str:
    head = f"M{pts[0, 0]:.1f} {pts[0, 1]:.1f}"
    return head + "".join(f"L{x:.1f} {y:.1f}" for x, y in pts[1:])


def line_drawing(img: np.ndarray, detail: int = 3) -> dict:
    if detail not in DETAIL:
        raise ValueError("detail must be 1-5")
    pct, photo_len, drawing_len = DETAIL[detail]

    small = marks.shrink(img, WORK_SIDE)
    h, w = small.shape[:2]
    if max(h, w) < WORK_SIDE * 0.8:
        # small images trace into jagged steps, so work on a bigger copy
        scale = WORK_SIDE / max(h, w)
        small = cv2.resize(
            small, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_CUBIC
        )
        h, w = small.shape[:2]
    drawing = marks.is_drawing(small)
    if drawing:
        skel, weight = drawing_edges(small)
        min_len = drawing_len
    else:
        skel, weight = photo_edges(small, pct)
        min_len = photo_len

    strokes = []
    for line in trace(skel):
        pts = np.array(line, dtype=np.float32)
        length = float(np.sum(np.hypot(*np.diff(pts, axis=0).T))) if len(pts) > 1 else 0.0
        if length < min_len:
            continue
        px = pts.astype(int)
        raw = float(np.mean(weight[px[:, 1], px[:, 0]]))
        # pen strokes keep their real thickness, photo edges scale with contrast
        stroke_w = 0.6 + raw
        simple = cv2.approxPolyDP(pts.reshape(-1, 1, 2), 0.8, False).reshape(-1, 2)
        strokes.append(
            {
                "d": to_path(chaikin(simple.astype(np.float64))),
                "length": round(length, 1),
                "weight": round(stroke_w, 2),
            }
        )

    strokes.sort(key=lambda s: s["length"], reverse=True)
    return {"width": w, "height": h, "drawing": drawing, "strokes": strokes[:MAX_STROKES]}
