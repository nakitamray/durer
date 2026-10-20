import cv2
import numpy as np
import pytest

from durer.marks import is_drawing
from durer.shapes import classify, find_shapes


def outline(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea)


@pytest.mark.parametrize(
    "draw, expected",
    [
        (lambda m: cv2.circle(m, (100, 100), 60, 1, -1), "ellipse"),
        (lambda m: cv2.ellipse(m, ((100, 100), (150, 70), 30), 1, -1), "ellipse"),
        (lambda m: cv2.rectangle(m, (40, 60), (170, 140), 1, -1), "box"),
        (
            lambda m: cv2.fillPoly(m, [np.array([[100, 20], [180, 180], [20, 180]])], 1),
            "triangle",
        ),
    ],
)
def test_classify_simple_shapes(draw, expected):
    mask = np.zeros((200, 200), np.uint8)
    draw(mask)
    kind, fit, _ = classify(outline(mask), mask.shape, 0.025, 0.82)
    assert kind == expected
    assert fit > 0.9


def test_irregular_shape_falls_back_to_polygon():
    mask = np.zeros((200, 200), np.uint8)
    # an L shape isn't close to any simple shape
    cv2.rectangle(mask, (20, 20), (60, 180), 1, -1)
    cv2.rectangle(mask, (20, 140), (180, 180), 1, -1)
    kind, _, geom = classify(outline(mask), mask.shape, 0.02, 0.82)
    assert kind == "polygon"
    assert len(geom["points"]) >= 5


def test_finds_ball_and_box(sample_image):
    sample_image = sample_image.copy()
    # give them color so it's treated as a photo
    cv2.circle(sample_image, (290, 150), 70, (40, 40, 200), -1)
    cv2.rectangle(sample_image, (40, 40), (180, 260), (200, 120, 40), -1)
    result = find_shapes(sample_image, simplicity=3)
    assert not result["drawing"]
    kinds = {s["kind"] for s in result["shapes"]}
    assert {"ellipse", "box"} <= kinds
    shares = [s["share"] for s in result["shapes"]]
    assert shares == sorted(shares, reverse=True)


def test_drawing_detection(sample_image):
    assert is_drawing(sample_image)
    colorful = sample_image.copy()
    cv2.circle(colorful, (290, 150), 70, (40, 40, 200), -1)
    assert not is_drawing(colorful)


def test_pencil_marks_become_a_mass():
    img = np.full((300, 300, 3), 240, np.uint8)
    rng = np.random.default_rng(1)
    # a dense patch of scribbles in the middle
    for _ in range(300):
        x, y = rng.integers(90, 210, size=2)
        dx, dy = rng.integers(-15, 15, size=2)
        cv2.line(img, (int(x), int(y)), (int(x + dx), int(y + dy)), (90, 90, 90), 1)
    result = find_shapes(img, simplicity=3)
    assert result["drawing"]
    assert len(result["shapes"]) >= 1
    cx, cy = result["shapes"][0]["center"]
    assert 100 < cx < 200 and 100 < cy < 200


def test_bad_simplicity(sample_image):
    with pytest.raises(ValueError):
        find_shapes(sample_image, simplicity=0)
