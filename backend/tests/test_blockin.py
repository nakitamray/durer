import cv2
import numpy as np

from durer.blockin import block_in, notan, placement, shadow_mask


def photo():
    """A dark red ball on a light wall, lit from the left."""
    img = np.full((400, 400, 3), (205, 215, 225), np.uint8)
    cv2.circle(img, (200, 210), 110, (50, 50, 190), -1)
    # shadow side
    cv2.ellipse(img, (200, 210), (110, 110), 0, -70, 110, (25, 25, 90), -1)
    return img


def test_placement_of_a_leaning_bar():
    mask = np.zeros((200, 200), bool)
    pts = np.array([[60, 20], [80, 20], [140, 180], [120, 180]])
    m = np.zeros((200, 200), np.uint8)
    cv2.fillPoly(m, [pts], 1)
    mask[m > 0] = True
    p = placement(mask)
    x0, y0, x1, y1 = p["box"]
    assert (x0, y0) == (60, 20) and (x1, y1) == (140, 180)
    # leans right going down, about 20 degrees off vertical
    assert 12 < p["lean"] < 28


def test_block_in_finds_the_ball():
    r = block_in(photo())
    x0, y0, x1, y1 = r["placement"]["box"]
    scale = r["width"] / 400
    assert abs((x1 - x0) / scale - 220) < 40
    assert len(r["big"]) == 1
    # a circle as a few straight lines
    assert 5 <= len(r["big"][0]) <= 14
    assert len(r["medium"]) >= 2


def test_notan_shadow_side():
    img = photo()
    shadow = shadow_mask(img, drawing=False)
    assert shadow[210, 260]  # right half of the ball is in shadow
    assert not shadow[30, 30]  # wall is light
    out = notan(img)
    assert out["path"].startswith("M")
    more = notan(img, bias=5)["shadow"]
    less = notan(img, bias=1)["shadow"]
    assert less <= out["shadow"] <= more


def test_hatching_is_shadow_in_a_drawing():
    img = np.full((300, 300, 3), 235, np.uint8)
    cv2.circle(img, (150, 150), 100, (60, 60, 60), 2)
    for x in range(160, 240, 5):
        cv2.line(img, (x, 90), (x - 20, 210), (70, 70, 70), 1)
    shadow = shadow_mask(img, drawing=True)
    assert shadow[150, 200]
    assert not shadow[150, 80]
