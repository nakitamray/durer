"""Group an image into a handful of tones and match each to a pencil grade."""

import cv2
import numpy as np
from sklearn.cluster import KMeans

# darkest -> lightest
GRADES = {
    3: ["4B", "HB", "2H"],
    4: ["6B", "2B", "HB", "2H"],
    5: ["6B", "4B", "2B", "HB", "2H"],
}

SAMPLE_SIZE = 20_000


def value_study(img: np.ndarray, levels: int = 4, seed: int = 0):
    if levels not in GRADES:
        raise ValueError("levels must be 3, 4 or 5")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # squinting at the subject: blur away the small stuff before grouping
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    flat = gray.reshape(-1, 1).astype(np.float32)

    rng = np.random.default_rng(seed)
    sample = flat[rng.choice(len(flat), size=min(SAMPLE_SIZE, len(flat)), replace=False)]

    km = KMeans(n_clusters=levels, n_init=4, random_state=seed).fit(sample)
    centers = np.sort(km.cluster_centers_.ravel())

    # nearest center for every pixel (1-D, so no need for km.predict)
    idx = np.abs(flat - centers[None, :]).argmin(axis=1)
    poster = centers[idx].reshape(gray.shape).astype(np.uint8)

    counts = np.bincount(idx, minlength=levels)
    total = counts.sum()
    tones = [
        {
            "grade": grade,
            "gray": int(round(c)),
            "coverage": round(float(n / total), 4),
        }
        for grade, c, n in zip(GRADES[levels], centers, counts, strict=True)
    ]
    return poster, tones
