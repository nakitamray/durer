"""Printable sheets: a blank grid to draw on, and the reference with the same grid."""

import io

import cv2
import numpy as np
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .grid import UNITS, Grid

PT_PER_INCH = 72
LINE = Color(0.45, 0.42, 0.38)
LABEL = Color(0.35, 0.32, 0.28)


def _draw_grid(c: canvas.Canvas, g: Grid, to_pt: float, page_h: float):
    x0 = g.offset_x * to_pt
    # reportlab's origin is bottom-left, ours is top-left
    y_top = page_h - g.offset_y * to_pt
    w = g.drawing_width * to_pt
    h = g.drawing_height * to_pt
    cw = g.cell_width * to_pt
    ch = g.cell_height * to_pt

    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.rect(x0, y_top - h, w, h)
    c.setLineWidth(0.35)
    for i in range(1, g.cols):
        c.line(x0 + i * cw, y_top, x0 + i * cw, y_top - h)
    for j in range(1, g.rows):
        c.line(x0, y_top - j * ch, x0 + w, y_top - j * ch)

    c.setFillColor(LABEL)
    c.setFont("Helvetica", 6.5)
    for i, label in enumerate(g.col_labels):
        c.drawCentredString(x0 + (i + 0.5) * cw, y_top + 4, label)
    for j, label in enumerate(g.row_labels):
        c.drawRightString(x0 - 4, y_top - (j + 0.5) * ch - 2, label)


def grid_sheets(img: np.ndarray, g: Grid, paper_w: float, paper_h: float, title: str = "") -> bytes:
    to_pt = UNITS[g.unit] * PT_PER_INCH
    page_w, page_h = paper_w * to_pt, paper_h * to_pt

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))
    c.setTitle(title or "durer grid")

    note = f"{g.cols} x {g.rows} squares, each {g.cell_width:g} x {g.cell_height:g} {g.unit}"

    # page 1: empty grid, for tracing lightly onto paper
    _draw_grid(c, g, to_pt, page_h)
    c.setFont("Helvetica", 7)
    c.drawString(g.offset_x * to_pt, 14, note)
    c.showPage()

    # page 2: the reference under the same grid
    ok, png = cv2.imencode(".png", img)
    if ok:
        c.drawImage(
            ImageReader(io.BytesIO(png.tobytes())),
            g.offset_x * to_pt,
            page_h - (g.offset_y + g.drawing_height) * to_pt,
            g.drawing_width * to_pt,
            g.drawing_height * to_pt,
        )
    _draw_grid(c, g, to_pt, page_h)
    c.setFont("Helvetica", 7)
    c.drawString(g.offset_x * to_pt, 14, note)
    c.showPage()

    c.save()
    return buf.getvalue()
