# Dürer

Upload any picture and Dürer breaks it down the way I was taught to draw as a kid: box it into a grid, block in the big shapes, get the main lines down one square at a time, then work out the values from light to dark.

I got the idea at the National Gallery of Art in DC. Someone next to me was copying a Monet into her sketchbook square by square, and it reminded me of my drawing lessons. The app is named after Albrecht Dürer, who wrote down the grid method in 1525 (he looked at his subject through a frame strung with threads).

## What it does

**I. Mise en place.** Pick an image and the paper you're actually drawing on (5×7, 9×12, A4, ...). The image gets scaled to fit the sheet with a margin.

**II. La grille.** A grid goes over the image, and the margin shows how big each square is on *your* paper, in inches (to the nearest ⅛) or cm. Click a square to see it up close with halfway marks. You can also download a PDF with an empty grid page and a reference page, both printed at real size.

**III. Les formes.** The picture broken into a few big, simple shapes (circles, ovals, rectangles, triangles) numbered biggest to smallest, which is the order you'd block them in. A slider reveals them one at a time, and another one controls how simple they get.

**IV. Le contour.** A line drawing of the main edges, laid over a faded copy of the image. A detail slider goes from a loose block-in to every line.

**V. Les valeurs.** The image is grouped into 3–5 tones, and each one gets a pencil grade (HB, 2B, 6B...) and a note on how much of the picture it covers. The lightest group is left as bare paper.

## How it works

The image processing is done by a Python API, and the frontend is Svelte.

```
backend/   FastAPI + OpenCV + scikit-learn + ReportLab
frontend/  Svelte 5 + TypeScript + Vite, Rough.js for the hand-drawn lines
```

- **Grid** (`backend/durer/grid.py`): fits the image into the usable part of the paper. You choose the number of columns, and the number of rows is picked so the squares stay close to square.
- **Shapes** (`backend/durer/shapes.py`): photos get flattened with mean shift and split into color regions with k-means in Lab space, with lightness counting for less so shading doesn't cut an object in half. Pencil and ink drawings are detected (light, and one color throughout) and handled differently: the marks are smudged together into a density map and thresholded, so a dense cluster of lines becomes one mass. Each region is then compared against a fitted ellipse, rotated rectangle and triangle, and the one with the most overlap (intersection over union) wins. If none is close enough it falls back to a simplified polygon.
- **Contours** (`backend/durer/contour.py`): runs a few passes of a bilateral filter to flatten texture while keeping edges, then Canny. The Canny thresholds come from percentiles of the gradient magnitude, so a faint pencil scan and a contrasty photo both work. Small specks are removed with connected components.
- **Values** (`backend/durer/values.py`): blurs the image (like squinting), then runs k-means on brightness and maps the clusters, darkest to lightest, onto pencil grades.
- **PDF** (`backend/durer/pdf.py`): ReportLab draws the grid in points from the real paper size, so the printout is to scale.

## Running it locally

You'll need [Python](https://www.python.org/downloads/) 3.11 to 3.13, [Node](https://nodejs.org/) 22 and Git.

### Windows (PowerShell)

```powershell
git clone https://github.com/nakitamray/durer.git
cd durer\backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn durer.main:app --reload
```

If PowerShell refuses to run `Activate.ps1`, allow local scripts once with `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and try again.

Then in a second PowerShell window:

```powershell
cd durer\frontend
npm install
npm run dev
```

After the first setup, `.\dev.ps1` from the repo root opens both in their own windows.

### macOS / Linux

API:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn durer.main:app --reload
```

Frontend (in another terminal):

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. In dev, Vite proxies `/api` to the API on port 8000.

Or run the API in Docker:

```bash
docker build -t durer-api backend
docker run -p 8000:8000 durer-api
```

## Tests

```bash
cd backend && pytest
cd frontend && npm run check
```

CI runs both, plus a Docker build, on every push.

## Config

| where    | variable          | default                 |
| -------- | ----------------- | ----------------------- |
| backend  | `ALLOWED_ORIGINS` | `http://localhost:5173` |
| frontend | `VITE_API_URL`    | `/api`                  |

## Next up

- 3D primitives for **Les formes**: reading a box as a cube in perspective, or a bottle as a cylinder
- a learned edge model (HED / PiDiNet in PyTorch) for cleaner line art on photos
- uploading a photo of your own drawing and comparing it to the reference square by square
