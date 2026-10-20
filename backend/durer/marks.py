"""Helpers for telling drawings from photos, and finding the marks in a drawing."""

import cv2
import numpy as np


def is_drawing(img: np.ndarray) -> bool:
    """Pencil or ink on paper: mostly light, and one color throughout
    (the paper can be tinted, like old sepia sheets)."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    chroma = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    spread = float(np.percentile(chroma, 95) - np.median(chroma))
    return spread < 10 and float(np.median(lab[..., 0])) > 150


def ink(gray: np.ndarray) -> np.ndarray:
    """How much darker each pixel is than the paper around it. Paper is
    rarely lit evenly in a phone photo, so it's measured locally."""
    h, w = gray.shape
    k = (max(h, w) // 25) | 1
    paper = cv2.dilate(gray, np.ones((k, k), np.uint8))
    paper = cv2.GaussianBlur(paper, (k, k), 0)
    return cv2.subtract(paper, gray)


def density(gray: np.ndarray, spread: float) -> np.ndarray:
    """Ink smudged together, so a cluster of strokes reads as one mass.
    `spread` is the blur as a share of the picture's longer side."""
    h, w = gray.shape
    d = cv2.GaussianBlur(ink(gray).astype(np.float32), (0, 0), max(h, w) * spread)
    return cv2.normalize(d, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def shrink(img: np.ndarray, side: int) -> np.ndarray:
    h, w = img.shape[:2]
    scale = side / max(h, w)
    if scale >= 1:
        return img
    return cv2.resize(img, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)


def keep_large(mask: np.ndarray, min_area: int) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    keep = np.zeros(count, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= min_area
    return keep[labels]


def lines(gray: np.ndarray) -> np.ndarray:
    """The pen or pencil marks themselves, as a mask."""
    amount = ink(cv2.GaussianBlur(gray, (3, 3), 0))
    level, _ = cv2.threshold(amount, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # hysteresis: faint bits of a stroke count if they connect to a clear one
    strong = amount > max(level * 1.1, 20)
    weak = (amount > max(level * 0.6, 10)).astype(np.uint8)
    count, labels = cv2.connectedComponents(weak, connectivity=8)
    hit = np.zeros(count, bool)
    hit[np.unique(labels[strong])] = True
    hit[0] = False
    return keep_large(hit[labels], 10)


def coverage(gray: np.ndarray, window: float = 0.025) -> np.ndarray:
    """Share of each neighbourhood covered in marks. An outline barely
    registers, hatching fills a good part of the window."""
    h, w = gray.shape
    k = max(9, round(max(h, w) * window))
    cover = cv2.blur(lines(gray).astype(np.float32), (k, k))
    return cv2.GaussianBlur(cover, (0, 0), k / 2)
