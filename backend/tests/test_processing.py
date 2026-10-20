import numpy as np
import pytest

from durer.contour import line_drawing
from durer.values import value_study


def test_line_drawing_traces_the_outlines(sample_image):
    out = line_drawing(sample_image, detail=3)
    assert out["strokes"], "expected at least one stroke"
    lengths = [s["length"] for s in out["strokes"]]
    assert lengths == sorted(lengths, reverse=True)
    # the circle's outline (r=70, scaled up with the image) should be one long stroke
    scale = out["width"] / 400
    assert lengths[0] > 2 * 3.14 * 70 * scale * 0.6
    assert all(s["d"].startswith("M") for s in out["strokes"])


def test_trace_keeps_a_line_whole():
    from durer.contour import trace

    skel = np.zeros((50, 50), bool)
    skel[25, 5:45] = True
    # a short branch touching the middle of it
    skel[15:25, 25] = True
    lines = trace(skel)
    longest = max(lines, key=len)
    assert len(longest) >= 40


def test_line_drawing_rejects_bad_detail(sample_image):
    with pytest.raises(ValueError):
        line_drawing(sample_image, detail=9)


def test_value_study_three_tones(sample_image):
    poster, tones = value_study(sample_image, levels=3)
    assert poster.shape == (300, 400)
    assert [t["grade"] for t in tones] == ["4B", "HB", "paper"]
    grays = [t["gray"] for t in tones]
    assert grays == sorted(grays)
    assert sum(t["coverage"] for t in tones) == pytest.approx(1, abs=0.01)
    assert len(np.unique(poster)) <= 3


def test_value_study_levels(sample_image):
    with pytest.raises(ValueError):
        value_study(sample_image, levels=7)
