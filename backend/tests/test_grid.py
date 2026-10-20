import pytest

from durer.grid import column_label, plan_grid


def test_column_labels():
    assert [column_label(i) for i in (0, 1, 25, 26, 27)] == ["A", "B", "Z", "AA", "AB"]


def test_landscape_image_on_portrait_paper():
    g = plan_grid(400, 300, paper_width=9, paper_height=12, cols=4, margin=0.5)
    # width is the limiting side: 8in usable
    assert g.drawing_width == pytest.approx(8)
    assert g.drawing_height == pytest.approx(6)
    assert g.cell_width == pytest.approx(2)
    assert g.rows == 3
    assert g.cell_height == pytest.approx(2)
    assert g.offset_x == pytest.approx(0.5)
    assert g.offset_y == pytest.approx(3)


def test_rows_keep_cells_near_square():
    g = plan_grid(1000, 1700, paper_width=9, paper_height=12, cols=5)
    ratio = g.cell_height / g.cell_width
    assert 0.85 < ratio < 1.15
    assert len(g.row_labels) == g.rows


def test_metric():
    g = plan_grid(100, 100, paper_width=21, paper_height=29.7, cols=4, margin=1, unit="cm")
    assert g.drawing_width == pytest.approx(19)
    assert g.cell_width == pytest.approx(4.75)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"cols": 0},
        {"unit": "ft"},
        {"margin": 10},
    ],
)
def test_bad_input(kwargs):
    args = {"paper_width": 9, "paper_height": 12, "cols": 4} | kwargs
    with pytest.raises(ValueError):
        plan_grid(400, 300, **args)
