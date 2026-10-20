import base64
import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from . import contour, grid, imaging, pdf, shapes, values

app = FastAPI(title="durer")

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


async def read_image(upload: UploadFile):
    try:
        return imaging.decode(await upload.read())
    except imaging.ImageError as e:
        raise HTTPException(400, str(e)) from e


def plan(img, paper_width, paper_height, cols, margin, unit):
    h, w = img.shape[:2]
    try:
        return grid.plan_grid(w, h, paper_width, paper_height, cols, margin, unit)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/grid")
async def make_grid(
    image: UploadFile = File(...),
    paper_width: float = Form(9),
    paper_height: float = Form(12),
    cols: int = Form(6),
    margin: float = Form(0.5),
    unit: str = Form("in"),
):
    img = await read_image(image)
    return plan(img, paper_width, paper_height, cols, margin, unit).to_dict()


@app.post("/shapes")
async def make_shapes(image: UploadFile = File(...), simplicity: int = Form(3)):
    img = await read_image(image)
    try:
        return shapes.find_shapes(img, simplicity)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e


@app.post("/contour")
async def make_contour(image: UploadFile = File(...), detail: int = Form(3)):
    img = await read_image(image)
    try:
        lines = contour.line_drawing(img, detail)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    return Response(imaging.encode_png(lines), media_type="image/png")


@app.post("/values")
async def make_values(image: UploadFile = File(...), levels: int = Form(4)):
    img = await read_image(image)
    try:
        poster, tones = values.value_study(img, levels)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    png = base64.b64encode(imaging.encode_png(poster)).decode()
    return {"image": f"data:image/png;base64,{png}", "tones": tones}


@app.post("/export")
async def export_pdf(
    image: UploadFile = File(...),
    paper_width: float = Form(9),
    paper_height: float = Form(12),
    cols: int = Form(6),
    margin: float = Form(0.5),
    unit: str = Form("in"),
):
    img = await read_image(image)
    g = plan(img, paper_width, paper_height, cols, margin, unit)
    data = pdf.grid_sheets(img, g, paper_width, paper_height)
    return Response(
        data,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="durer-grid.pdf"'},
    )
