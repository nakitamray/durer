# Dürer

Upload any picture and Dürer walks you through drawing it the way I was taught as a kid: box it into a grid, mark where it sits, block it in with big straight lines, break those into smaller ones, fill the shadows, then find the real lines and the tones.

I got the idea at the National Gallery of Art in DC. Someone next to me was copying a Monet into her sketchbook square by square, and it reminded me of my drawing lessons. The app is named after Albrecht Dürer, who wrote down the grid method in 1525 (he looked at his subject through a frame strung with threads).

## The steps

Each stage builds on the one before it, and the previous stage stays faintly underneath so you can see how the drawing grows.

**I. Mise en place.** Pick an image and the paper you're actually drawing on (5×7, 9×12, A4, ...). The image gets scaled to fit the sheet with a margin.

**II. La grille.** A grid goes over the image, and the margin shows how big each square is on *your* paper, in inches (to the nearest 1/8) or cm. Click a square to see it up close with halfway marks. You can also download a PDF with an empty grid page and a reference page, both printed at real size.

**III. L'emplacement.** Four marks for the highest, lowest, leftmost and rightmost points of the subject, plus the line it leans along. The margin says which squares those land in and how big the subject is on the paper.

**IV. Grandes formes.** The whole silhouette as a handful of long straight lines that overshoot their corners, like a real block-in. There's also a "simple solids" view that reads the picture as circles, ovals, rectangles and triangles.

**V. Formes moyennes.** The same outline with more, shorter straight lines, plus the main shadow shapes inside it as flat planes.

**VI. Le notan.** Everything split into two values, light and shadow, drawn as hatching or a flat fill. A slider moves the split lighter or darker.

**VII. Le contour.** The finished line drawing as vector strokes, each with its own weight, over the block-in.

**VIII. Les valeurs.** The image grouped into 3–5 tones, each with a pencil grade (HB, 2B, 6B...) and how much of the picture it covers. The lightest group is left as bare paper.

## How it works

The image processing is done by a Python API, and the frontend is Svelte.

```
backend/   FastAPI + OpenCV + scikit-image + scikit-learn + ReportLab
frontend/  Svelte 5 + TypeScript + Vite, Rough.js for the hand-drawn lines
```

- **Grid** (`backend/durer/grid.py`): fits the image into the usable part of the paper. You choose the number of columns, and the number of rows is picked so the squares stay close to square.
- **Drawing or photo?** (`backend/durer/marks.py`): a picture that's light and the same color throughout (paper can be tinted) is treated as a pencil or ink drawing. Drawings and photos go through different paths in most steps below. For drawings, the paper tone is measured locally (a dilation of the gray image), so uneven lighting in a phone photo of a sketch doesn't count as ink.
- **Placement and block-in** (`backend/durer/blockin.py`): the subject is separated from the background with GrabCut for photos, or from how dense the marks are for drawings. Placement is the bounding box plus the main axis from PCA on the subject's pixels. Big and medium shapes are the subject's outline simplified with Douglas–Peucker (`approxPolyDP`) at two tolerances. The medium stage also adds the outlines of the shadow shapes.
- **Notan**: Otsu threshold on a smoothed brightness image for photos, or on how much of each neighbourhood is covered in hatching for drawings. A bias slider scales the threshold. Small specks of light or shadow are absorbed so the shapes stay simple. The result is sent as an SVG path with holes.
- **Contours** (`backend/durer/contour.py`): photos get a bilateral filter and Canny, with thresholds taken from percentiles of the gradient. Drawings use the skeleton of the ink itself (scikit-image), after a hysteresis threshold so faint parts of a stroke stay connected. The one-pixel-wide result is traced into polylines. At junctions the walk keeps going in the direction it was heading, so a long outline isn't chopped up wherever something touches it. Each polyline is then simplified, smoothed with Chaikin's algorithm and sent to the browser as an SVG path with a weight.
- **Simple solids** (`backend/durer/shapes.py`): color regions from mean shift + k-means in Lab space, with lightness weighted down so shading doesn't split an object. Each region is compared against a fitted ellipse, rotated rectangle and triangle by intersection over union.
- **Values** (`backend/durer/values.py`): blurs the image (like squinting), runs k-means on brightness, cleans the borders between tones with a median filter, and maps the groups onto pencil grades.
- **PDF** (`backend/durer/pdf.py`): ReportLab draws the grid in points from the real paper size, so the printout is to scale.
- **Frontend**: Svelte 5 with runes. Rough.js draws every line on the page (the grid, block-in lines, doodles, the pen and eraser) so nothing looks ruled by a machine.

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

## Fonts

Headings are Cormorant Garamond and body text is EB Garamond. The handwriting is Xanas Wedding (Groom) by Pedro Teixeira Foundry. It's the free demo version, so only the plain letters are included, and digits and punctuation fall back to La Belle Aurore.

## Next up

- form modeling after the notan: big forms, then medium forms, then accents
- reading a box as a cube in perspective, or a bottle as a cylinder
- a learned edge model (HED / PiDiNet in PyTorch) for cleaner line art on photos
- uploading a photo of your own drawing and comparing it to the reference square by square
