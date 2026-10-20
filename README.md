# Dürer

Upload any picture and Dürer walks you through drawing it the way I was taught as a kid: box it into a grid, mark where it sits, block in the big shapes, break them into medium and then small ones, split each shape into light and dark, then find the real lines and the tones.

I got the idea at the National Gallery of Art in DC. Someone next to me was copying a Monet into her sketchbook square by square, and it reminded me of my drawing lessons. The app is named after Albrecht Dürer, who wrote down the grid method in 1525 (he looked at his subject through a frame strung with threads).

## The steps

Each stage builds on the one before it, and the previous stage stays faintly underneath so you can see how the drawing grows.

**I. Mise en place.** Pick an image and the paper you're actually drawing on (5×7, 9×12, A4, ...). The image gets scaled to fit the sheet with a margin.

**II. La grille.** A grid goes over the image, and the margin shows how big each square is on *your* paper, in inches (to the nearest 1/8) or cm. Click a square to see it up close with halfway marks. You can also download a PDF with an empty grid page and a reference page, both printed at real size.

**III. L'emplacement.** Four marks for the highest, lowest, leftmost and rightmost points of the subject, plus the line it leans along, each labeled with the square it lands in.

**IV. Grandes formes.** The borders between the few biggest masses (sky and ground, the object and what's behind it), as long straight lines that run past their corners like a real block-in.

**V. Formes moyennes.** The next layer down: each big shape split into its parts. The big lines stay faintly underneath.

**VI. Petites formes.** One more layer of the same. Every small shape sits inside a medium one, so each stage only adds lines and never moves the ones already drawn.

**VII. Ombre et lumière.** Each shape split into the part facing the light and the part turning away from it, with the line where it turns. Shown as hatching or a flat fill, with a slider to move the split lighter or darker.

**VIII. Le contour.** The finished line drawing as vector strokes, each with its own weight, over the block-in.

**IX. Les valeurs.** The image grouped into 3–5 tones, each with a pencil grade (HB, 2B, 6B...) and how much of the picture it covers. The lightest group is left as bare paper.

## How it works

The image processing is done by a Python API, and the frontend is Svelte.

```
backend/   FastAPI + OpenCV + scikit-image + scikit-learn + ReportLab
frontend/  Svelte 5 + TypeScript + Vite, Rough.js for the hand-drawn lines
```

- **Grid** (`backend/durer/grid.py`): fits the image into the usable part of the paper. You choose the number of columns, and the number of rows is picked so the squares stay close to square.
- **Drawing or photo?** (`backend/durer/marks.py`): a picture that's light and the same color throughout (paper can be tinted) is treated as a pencil or ink drawing. Drawings and photos go through different paths in most steps below. For drawings, the paper tone is measured locally (a dilation of the gray image), so uneven lighting in a phone photo of a sketch doesn't count as ink.
- **Shapes, coarse to fine** (`backend/durer/masses.py`): the picture is cut into about 900 superpixels with SLIC. Those are merged back together one pair at a time, always the pair with the weakest edge along their shared border and the closest color, with tiny specks going first. Strong edges survive longest, so the last few regions left are the big masses. Recording the merges gives one tree, and stopping it at 5, 12 and 28 regions gives the big, medium and small shapes, each level nested inside the one before. Drawings are run on how dense their marks are rather than on color, so a hatched area reads as one mass.
- **Block-in lines** (`backend/durer/blockin.py`): the borders between regions are traced into polylines and straightened with Douglas–Peucker (`approxPolyDP`). Looser tolerances are used for the bigger shapes. Borders running close together (both sides of a pen line, say) are first merged into one.
- **Placement**: each big region gets a score from spectral residual saliency (Hou & Zhang 2007) plus how much its color stands out, cut down for every edge of the frame it touches, since skies and table tops run off the edges and subjects usually don't. If no big region stands out, the medium regions are scored instead. The subject's box and its lean (PCA on its pixels) become the placement marks.
- **Light and dark**: the same hierarchy cut finer (about 70 regions). Each piece is lit or in shadow as a whole, so the shadow shapes follow the block-in. A medium shape that clearly turns from light to dark is split by its own Otsu threshold, and a flat one is decided by the picture's overall threshold. The lines where light turns into shadow inside a shape come back as their own layer.
- **Contours** (`backend/durer/contour.py`): photos get a bilateral filter and Canny, with thresholds taken from percentiles of the gradient. Drawings use the skeleton of the ink itself (scikit-image), after a hysteresis threshold so faint parts of a stroke stay connected. The one-pixel-wide result is traced into polylines. At junctions the walk keeps going in the direction it was heading, so a long outline isn't chopped up wherever something touches it. Each polyline is then simplified, smoothed with Chaikin's algorithm and sent to the browser as an SVG path with a weight.
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

Or skip all of that: `.\dev.ps1` from the repo root makes the Python environment if it's missing, installs whatever's new in both halves, and opens the API and the app in their own windows. It's safe to run after every pull.

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

Headings are Cormorant Garamond and body text is EB Garamond. Handwriting that needs to be read (instructions, measurements) is Caveat. The doodle captions are Xanas Wedding (Groom) by Pedro Teixeira Foundry. Its demo version only has clean plain letters, so that's all the web font includes, and digits and punctuation fall back to Caveat. Xanas is a demo font for personal use.

## Next up

- form modeling after light and dark: big forms, then medium forms, then accents
- reading a box as a cube in perspective, or a bottle as a cylinder
- a learned edge model (HED / PiDiNet in PyTorch) for cleaner line art on photos
- uploading a photo of your own drawing and comparing it to the reference square by square
