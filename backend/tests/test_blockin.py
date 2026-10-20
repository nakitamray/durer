import cv2
import numpy as np

from durer.blockin import block_in, light_and_dark, placement
from durer.masses import Hierarchy


def still_life():
    """A wall, a table, a dark box and a lit ball."""
    img = np.full((400, 600, 3), (205, 215, 225), np.uint8)
    img[260:] = (120, 135, 150)
    cv2.rectangle(img, (60, 150), (220, 300), (60, 70, 140), -1)
    cv2.circle(img, (420, 230), 80, (60, 80, 210), -1)
    # shadow side of the ball
    cv2.ellipse(img, (420, 230), (80, 80), 0, -60, 120, (30, 35, 95), -1)
    return img


def test_hierarchy_nests():
    img = still_life()
    h = Hierarchy(img, drawing=False)
    coarse, fine = h.cut(4), h.cut(20)
    assert coarse.max() + 1 <= 4
    # every fine region sits entirely inside one coarse region
    for r in np.unique(fine):
        assert len(np.unique(coarse[fine == r])) == 1


def test_big_shapes_follow_the_objects():
    h = Hierarchy(still_life(), drawing=False)
    labels = h.cut(5)
    # the box and the ball end up in different regions from the wall
    assert labels[220, 140] != labels[50, 300]
    assert labels[230, 400] != labels[50, 300]
    assert labels[220, 140] != labels[230, 400]


def test_placement_of_a_leaning_bar():
    m = np.zeros((200, 200), np.uint8)
    cv2.fillPoly(m, [np.array([[60, 20], [80, 20], [140, 180], [120, 180]])], 1)
    p = placement(m > 0)
    x0, y0, x1, y1 = p["box"]
    # the extremes are trimmed a little so stray specks don't stretch the box
    assert abs(x0 - 60) <= 4 and abs(y0 - 20) <= 4
    assert abs(x1 - 140) <= 4 and abs(y1 - 180) <= 4
    # leans right going down, about 20 degrees off vertical
    assert 12 < p["lean"] < 28


def test_block_in_finds_the_objects():
    r = block_in(still_life())
    scale = r["width"] / 600
    x0, y0, x1, y1 = (v / scale for v in r["placement"]["box"])
    # the box and the ball, not the wall or the table
    assert 40 < x0 < 90 and 470 < x1 < 520
    assert 130 < y0 < 175 and 290 < y1 < 330
    assert r["big"] and len(r["medium"]) >= len(r["big"])
    assert len(r["small"]) >= len(r["medium"])


def test_light_and_dark():
    img = still_life()
    out = light_and_dark(img)
    assert out["path"].startswith("M")
    assert 0 < out["shadow"] < 1
    less = light_and_dark(img, bias=1)["shadow"]
    more = light_and_dark(img, bias=5)["shadow"]
    assert less <= out["shadow"] <= more


def test_hatching_is_shadow_in_a_drawing():
    img = np.full((300, 300, 3), 235, np.uint8)
    cv2.circle(img, (150, 150), 100, (60, 60, 60), 2)
    for x in range(160, 240, 4):
        cv2.line(img, (x, 90), (x - 20, 210), (70, 70, 70), 1)
    out = light_and_dark(img)
    assert out["shadow"] > 0.02
