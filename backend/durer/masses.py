"""Breaking a picture into masses, coarse to fine.

The picture is cut into superpixels (SLIC), and those are merged back
together one pair at a time. The pair that merges next is the one with the
weakest edge along its shared border and the closest color, with small
specks going first. Strong edges survive longest, so the last few regions
left are the big masses an artist would block in first.

Recording the order of merges gives one tree, and stopping it at different
counts gives the big, medium and small shapes. Every small shape sits
inside a medium one and every medium shape inside a big one, the same way a
block-in gets refined on paper.
"""

import heapq

import cv2
import numpy as np
from skimage.segmentation import slic

from . import marks

WORK_SIDE = 640
SUPERPIXELS = 900


def tone_image(img: np.ndarray, drawing: bool) -> np.ndarray:
    """What the masses are made of, as an 8-bit RGB picture. For photos
    that's a smoothed copy; for drawings it's how dense the marks are, so a
    hatched area reads as one dark mass."""
    if drawing:
        d = marks.density(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 0.006)
        return cv2.cvtColor(255 - d, cv2.COLOR_GRAY2RGB)
    return cv2.cvtColor(cv2.bilateralFilter(img, 9, 40, 40), cv2.COLOR_BGR2RGB)


def edge_strength(lab: np.ndarray) -> np.ndarray:
    """Color gradient, scaled so a clear edge is about 1."""
    mag = np.zeros(lab.shape[:2], np.float32)
    for c, weight in ((0, 1.0), (1, 0.6), (2, 0.6)):
        ch = cv2.GaussianBlur(lab[..., c], (0, 0), 1.2)
        mag += weight * (
            cv2.Sobel(ch, cv2.CV_32F, 1, 0) ** 2 + cv2.Sobel(ch, cv2.CV_32F, 0, 1) ** 2
        )
    mag = np.sqrt(mag)
    return mag / (np.percentile(mag, 98) + 1e-6)


class Hierarchy:
    def __init__(self, img: np.ndarray, drawing: bool):
        rgb = tone_image(img, drawing)
        self.pixels = slic(rgb, n_segments=SUPERPIXELS, compactness=10, start_label=0)
        # L 0-100, a and b around 0
        lab = cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
        n = int(self.pixels.max()) + 1
        self.n = n
        self.merges = self._merge(lab, edge_strength(lab), n)

    def _merge(self, lab: np.ndarray, edges: np.ndarray, n: int) -> list[tuple[int, int]]:
        px = self.pixels.ravel()
        area = np.bincount(px, minlength=n).astype(np.float64)
        color = np.stack([np.bincount(px, lab[..., c].ravel(), n) for c in range(3)], axis=1)

        # every pair of touching superpixels: how long their border is, and
        # how strong the edge along it is in total
        border: dict[int, dict[int, list[float]]] = {i: {} for i in range(n)}
        for a, b, ea, eb in (
            (self.pixels[:, :-1], self.pixels[:, 1:], edges[:, :-1], edges[:, 1:]),
            (self.pixels[:-1, :], self.pixels[1:, :], edges[:-1, :], edges[1:, :]),
        ):
            diff = a != b
            pa, pb = a[diff], b[diff]
            strength = np.maximum(ea[diff], eb[diff])
            lo, hi = np.minimum(pa, pb), np.maximum(pa, pb)
            key = lo.astype(np.int64) * n + hi
            uniq, inv = np.unique(key, return_inverse=True)
            length = np.bincount(inv)
            total = np.bincount(inv, strength)
            for k, ln, tot in zip(uniq.tolist(), length.tolist(), total.tolist(), strict=True):
                i, j = divmod(k, n)
                for x, y in ((i, j), (j, i)):
                    cur = border[x].setdefault(y, [0.0, 0.0])
                    cur[0] += ln
                    cur[1] += tot

        speck = area.mean()

        def cost(i: int, j: int) -> float:
            ln, tot = border[i][j]
            edge = tot / ln
            ci, cj = color[i] / area[i], color[j] / area[j]
            dist = float(np.linalg.norm((ci - cj) * (1.3, 1, 1))) / 25
            # small pieces merge before big ones, whatever is around them
            size = min(1.0, (min(area[i], area[j]) / (speck * 6)) ** 0.5)
            # the edge counts most: a smooth turn from light to dark across a
            # ball is one shape, even though its two ends are different colors
            return (edge + 0.35 * dist) * size

        alive = np.ones(n, bool)
        # entries carry both regions' versions so stale ones can be skipped
        version = np.zeros(n, np.int64)
        heap = [(cost(i, j), i, j, 0, 0) for i in range(n) for j in border[i] if i < j]
        heapq.heapify(heap)

        merges = []
        while heap and len(merges) < n - 1:
            _, i, j, vi, vj = heapq.heappop(heap)
            if not (alive[i] and alive[j]) or vi != version[i] or vj != version[j]:
                continue
            # fold j into i
            alive[j] = False
            area[i] += area[j]
            color[i] += color[j]
            for k, (ln, tot) in border.pop(j).items():
                if k == i:
                    continue
                del border[k][j]
                cur = border[i].setdefault(k, [0.0, 0.0])
                cur[0] += ln
                cur[1] += tot
                border[k][i] = cur
            del border[i][j]
            version[i] += 1
            merges.append((i, j))
            for k in border[i]:
                heapq.heappush(heap, (cost(i, k), i, k, version[i], version[k]))
        return merges

    def cut(self, k: int) -> np.ndarray:
        """Label map with about k regions."""
        parent = np.arange(self.n)
        for i, j in self.merges[: max(0, self.n - k)]:
            parent[j] = i

        def root(x):
            while parent[x] != x:
                x = parent[x]
            return x

        roots = np.array([root(i) for i in range(self.n)])
        _, region = np.unique(roots, return_inverse=True)
        return region[self.pixels]
