"""Box technique math: fit the image onto a sheet of paper and split it into cells."""

from dataclasses import asdict, dataclass

UNITS = {"in": 1.0, "cm": 1 / 2.54, "mm": 1 / 25.4}


def column_label(i: int) -> str:
    # A, B, ... Z, AA, AB ... like a spreadsheet
    label = ""
    i += 1
    while i:
        i, rem = divmod(i - 1, 26)
        label = chr(65 + rem) + label
    return label


@dataclass
class Grid:
    unit: str
    cols: int
    rows: int
    drawing_width: float
    drawing_height: float
    cell_width: float
    cell_height: float
    offset_x: float
    offset_y: float
    cell_px_width: float
    cell_px_height: float
    col_labels: list[str]
    row_labels: list[str]

    def to_dict(self):
        return asdict(self)


def plan_grid(
    image_width: int,
    image_height: int,
    paper_width: float,
    paper_height: float,
    cols: int,
    margin: float = 0.5,
    unit: str = "in",
) -> Grid:
    if unit not in UNITS:
        raise ValueError(f"unit must be one of {', '.join(UNITS)}")
    if image_width <= 0 or image_height <= 0:
        raise ValueError("image size must be positive")
    if not 1 <= cols <= 40:
        raise ValueError("cols must be between 1 and 40")

    usable_w = paper_width - 2 * margin
    usable_h = paper_height - 2 * margin
    if usable_w <= 0 or usable_h <= 0:
        raise ValueError("margin is too big for this paper")

    # scale the image to fit inside the usable area, keeping its proportions
    scale = min(usable_w / image_width, usable_h / image_height)
    draw_w = image_width * scale
    draw_h = image_height * scale

    # columns are fixed by the user, rows are picked so cells stay close to square
    cell_w = draw_w / cols
    rows = max(1, round(draw_h / cell_w))
    cell_h = draw_h / rows

    return Grid(
        unit=unit,
        cols=cols,
        rows=rows,
        drawing_width=round(draw_w, 3),
        drawing_height=round(draw_h, 3),
        cell_width=round(cell_w, 3),
        cell_height=round(cell_h, 3),
        offset_x=round((paper_width - draw_w) / 2, 3),
        offset_y=round((paper_height - draw_h) / 2, 3),
        cell_px_width=image_width / cols,
        cell_px_height=image_height / rows,
        col_labels=[column_label(i) for i in range(cols)],
        row_labels=[str(i + 1) for i in range(rows)],
    )
