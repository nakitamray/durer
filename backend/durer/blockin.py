"""The early stages of a drawing, before any real lines go down.

1. placement: where the subject starts and stops, and which way it leans
2. big, medium and small shapes: the borders between masses at three
   levels of the same hierarchy (see masses.py), as straight lines
3. light and dark: each medium shape split into the part in light and the
   part in shadow

Coordinates come back in the working size along with its width and height,
so the frontend can scale them to the picture.
"""

from collections import OrderedDict

import cv2
import numpy as np
from skimage.morphology import skeletonize

from . import contour, marks
from .masses import WORK_SIDE, Hierarchy

LEVELS = {"big": 5, "medium": 12, "small": 28}
# a finer cut that light and dark are decided on, so the shadow shapes
# follow the same borders as the block-in
FINE = 70
# how far a straight line may stray from the real border, in working pixels
TOLERANCE = {"big": 7.0, "medium": 4.0, "small": 2.5}
MIN_LINE = {"big": 30, "medium": 18, "small": 10}

# light and dark: bias 1 (more light) .. 5 (more shadow) shifts the split
BIAS = {1: -8.0, 2: -4.0, 3: 0.0, 4: 4.0, 5: 8.0}

_cache: OrderedDict[bytes, tuple[np.ndarray, Hierarchy, dict]] = OrderedDict()


def prepare(img: np.ndarray) -> tuple[np.ndarray, Hierarchy, dict]:
    """Shrink the picture and build its hierarchy, reusing recent work since
    every step after the grid asks about the same picture."""
    small = marks.shrink(img, WORK_SIDE)
    key = cv2.resize(small, (32, 32)).tobytes() + bytes(str(small.shape), "ascii")
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]
    drawing = marks.is_drawing(small)
    h = Hierarchy(small, drawing)
    levels = {name: h.cut(k) for name, k in LEVELS.items()}
    levels["fine"] = h.cut(FINE)
    _cache[key] = (small, h, {"drawing": drawing, "levels": levels})
    while len(_cache) > 6:
        _cache.popitem(last=False)
    return _cache[key]


def borders(labels: np.ndarray) -> np.ndarray:
    """One pixel wide map of where one region meets another."""
    b = np.zeros(labels.shape, bool)
    b[:, :-1] |= labels[:, :-1] != labels[:, 1:]
    b[:-1, :] |= labels[:-1, :] != labels[1:, :]
    return b


def single_lines(b: np.ndarray, reach: int = 5) -> np.ndarray:
    """A thin region (a pen line in a drawing, a pole in a photo) has a
    border on each side. Pull borders that run close together into one."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (reach, reach))
    return skeletonize(cv2.dilate(b.astype(np.uint8), k).astype(bool))


def straight_lines(edges: np.ndarray, tolerance: float, min_len: float) -> list[list[list[float]]]:
    out = []
    for line in contour.trace(edges):
        pts = np.array(line, np.float32)
        if len(pts) < 2:
            continue
        if float(np.sum(np.hypot(*np.diff(pts, axis=0).T))) < min_len:
            continue
        simple = cv2.approxPolyDP(pts.reshape(-1, 1, 2), tolerance, False).reshape(-1, 2)
        out.append([[round(float(x), 1), round(float(y), 1)] for x, y in simple])
    return out


def saliency(img: np.ndarray) -> np.ndarray:
    """Spectral residual saliency (Hou and Zhang, 2007): whatever the
    picture's spectrum has that a generic picture's wouldn't."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    scale = 96 / max(h, w)
    g = cv2.resize(gray, (max(8, round(w * scale)), max(8, round(h * scale))))
    f = np.fft.fft2(g)
    log_amp = np.log(np.abs(f) + 1e-6)
    residual = log_amp - cv2.blur(log_amp, (3, 3))
    s = np.abs(np.fft.ifft2(np.exp(residual + 1j * np.angle(f)))) ** 2
    s = cv2.GaussianBlur(s.astype(np.float32), (0, 0), 3)
    s = cv2.resize(s, (w, h))
    return s / (s.max() + 1e-6)


def subject_mask(img: np.ndarray, levels: dict, drawing: bool) -> np.ndarray:
    if drawing:
        # a drawing's subject is wherever there's ink
        ink = marks.lines(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        if ink.sum() > 50:
            return ink

    sal = saliency(img)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    mean = lab.reshape(-1, 3).mean(axis=0)
    # regions that stand out, and that don't run off the edges of the frame
    # the way a sky or a table top does
    edge_penalty = [1.0, 0.6, 0.25, 0.1, 0.05]

    def scores(labels: np.ndarray) -> np.ndarray:
        out = []
        for r in range(int(labels.max()) + 1):
            m = labels == r
            area = m.mean()
            if area < 0.004:
                out.append(0.0)
                continue
            sides = int(m[0].any()) + int(m[-1].any()) + int(m[:, 0].any()) + int(m[:, -1].any())
            contrast = float(np.linalg.norm(lab[m].mean(axis=0) - mean)) / 60
            score = (float(sal[m].mean()) + contrast) * edge_penalty[sides]
            # a region filling most of the frame is background, not subject
            out.append(score * (1.0 if area < 0.5 else 0.2))
        return np.array(out)

    # big shapes keep whole objects together, so look there first; a busy
    # scene where nothing big stands out falls back to the medium shapes
    for name in ("big", "medium"):
        sc = scores(levels[name])
        if sc.max() > 0:
            return (sc >= sc.max() * 0.6)[levels[name]]
    return np.ones(levels["big"].shape, bool)


def placement(subject: np.ndarray) -> dict:
    ys, xs = np.nonzero(subject)
    # ignore the odd stray pixel at the extremes
    x0, x1 = (int(v) for v in np.percentile(xs, [0.5, 99.5]))
    y0, y1 = (int(v) for v in np.percentile(ys, [0.5, 99.5]))
    cx, cy = float(xs.mean()), float(ys.mean())

    # the long axis of the subject: its overall lean or gesture
    pts = np.stack([xs - cx, ys - cy], axis=1).astype(np.float64)
    _, vecs = np.linalg.eigh(np.cov(pts.T))
    dx, dy = vecs[:, -1]
    if dy < 0:
        dx, dy = -dx, -dy
    proj = pts @ np.array([dx, dy])
    lo, hi = (float(v) for v in np.percentile(proj, [1, 99]))
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


def block_in(img: np.ndarray) -> dict:
    small, _, info = prepare(img)
    h, w = small.shape[:2]
    levels = info["levels"]

    shapes = {
        name: straight_lines(
            single_lines(borders(levels[name]), 13 if info["drawing"] else 5),
            TOLERANCE[name],
            MIN_LINE[name],
        )
        for name in LEVELS
    }
    subject = subject_mask(small, levels, info["drawing"])
    return {
        "width": w,
        "height": h,
        "drawing": info["drawing"],
        "placement": placement(subject),
        **shapes,
    }


def to_path(polys: list[np.ndarray]) -> str:
    """Closed polygons as one svg path, holes and all (use fill-rule evenodd)."""
    parts = []
    for p in polys:
        head = f"M{p[0][0]:.1f} {p[0][1]:.1f}"
        parts.append(head + "".join(f"L{x:.1f} {y:.1f}" for x, y in p[1:]) + "Z")
    return "".join(parts)


def otsu(values: np.ndarray) -> float:
    """Otsu's threshold for values on a 0-100 scale."""
    v = np.clip(values * 2.55, 0, 255).astype(np.uint8).reshape(-1, 1)
    level, _ = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return level / 2.55


def light_and_dark(img: np.ndarray, bias: int = 3) -> dict:
    """Split the picture into light and shadow along the block-in's own
    borders. Each small piece of the hierarchy is lit or in shadow as a
    whole, so inside every medium shape you get the part that faces the
    light and the part that turns away from it."""
    if bias not in BIAS:
        raise ValueError("bias must be 1-5")
    small, _, info = prepare(img)
    h, w = small.shape[:2]
    medium, fine = info["levels"]["medium"], info["levels"]["fine"]

    if info["drawing"]:
        # in a drawing, darkness is how densely it's been hatched, and the
        # paper is light by definition, so only real hatching counts
        cover = marks.coverage(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
        value = 100 - np.clip(cover / 0.5, 0, 1) * 100
        level = 34.0
    else:
        smooth = cv2.bilateralFilter(small, 9, 40, 40)
        value = cv2.cvtColor(smooth.astype(np.float32) / 255, cv2.COLOR_BGR2LAB)[..., 0]
        level = otsu(value)
    level += BIAS[bias]

    n = int(fine.max()) + 1
    size = np.maximum(np.bincount(fine.ravel(), minlength=n), 1)
    mean = np.bincount(fine.ravel(), value.ravel(), n) / size
    # which medium shape each fine piece belongs to (the hierarchy nests,
    # so any pixel of the piece will do)
    flat = fine.ravel()
    first = np.full(n, -1)
    first[flat[::-1]] = np.arange(flat.size)[::-1]
    parent = medium.ravel()[first]

    dark = mean < level
    for r in np.unique(parent):
        pieces = parent == r
        if pieces.sum() < 2:
            continue
        v = mean[pieces]
        # a shape that clearly turns from light to dark gets split by its own
        # values; a flat shape is light or dark by the picture's overall split
        if v.max() - v.min() > 12:
            local = otsu(np.repeat(v, np.maximum(size[pieces] // 20, 1)))
            dark[pieces] = v < local + BIAS[bias]
    shadow = dark[fine]

    area = int(h * w * 0.0015)
    shadow = marks.keep_large(shadow, area)
    shadow = ~marks.keep_large(~shadow, area)

    contours, _ = cv2.findContours(shadow.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = [
        c.reshape(-1, 2) for c in (cv2.approxPolyDP(c, 2.0, True) for c in contours) if len(c) >= 3
    ]

    # where the light turns into shadow inside a shape: the new lines to draw
    turns = borders(shadow.astype(np.int32)) & ~cv2.dilate(
        borders(medium).astype(np.uint8), np.ones((3, 3), np.uint8)
    ).astype(bool)
    return {
        "width": w,
        "height": h,
        "path": to_path(polys),
        "turns": straight_lines(turns, 3.0, 14),
        "shadow": round(float(shadow.mean()), 4),
    }
