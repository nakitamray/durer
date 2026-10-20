import numpy as np
import pytest

from durer.contour import line_drawing
from durer.values import value_study


def test_line_drawing_finds_the_shapes(sample_image):
    out = line_drawing(sample_image, detail=3)
    assert out.shape == (300, 400, 4)
    alpha = out[..., 3]
    # edge of the circle should be inked, the flat background shouldn't
    assert alpha[150, 218:224].max() > 0
    assert alpha[10:30, 10:30].max() == 0


def test_line_drawing_rejects_bad_detail(sample_image):
    with pytest.raises(ValueError):
        line_drawing(sample_image, detail=9)


def test_value_study_three_tones(sample_image):
    poster, tones = value_study(sample_image, levels=3)
    assert poster.shape == (300, 400)
    assert [t["grade"] for t in tones] == ["4B", "HB", "2H"]
    grays = [t["gray"] for t in tones]
    assert grays == sorted(grays)
    assert sum(t["coverage"] for t in tones) == pytest.approx(1, abs=0.01)
    assert len(np.unique(poster)) <= 3


def test_value_study_levels(sample_image):
    with pytest.raises(ValueError):
        value_study(sample_image, levels=7)
