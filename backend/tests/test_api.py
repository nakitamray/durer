from fastapi.testclient import TestClient

from durer.main import app

client = TestClient(app)


def post(path, png, **data):
    return client.post(path, files={"image": ("x.png", png, "image/png")}, data=data)


def test_health():
    assert client.get("/health").json() == {"ok": True}


def test_grid(sample_png):
    r = post("/grid", sample_png, paper_width=9, paper_height=12, cols=4)
    assert r.status_code == 200
    body = r.json()
    assert body["cols"] == 4
    assert body["rows"] == 3


def test_contour_returns_strokes(sample_png):
    r = post("/contour", sample_png, detail=2)
    assert r.status_code == 200
    assert r.json()["strokes"]


def test_blockin(sample_png):
    r = post("/blockin", sample_png)
    assert r.status_code == 200
    body = r.json()
    assert len(body["placement"]["box"]) == 4
    assert body["big"]


def test_notan(sample_png):
    r = post("/notan", sample_png, bias=3)
    assert r.status_code == 200
    assert 0 <= r.json()["shadow"] <= 1


def test_values(sample_png):
    r = post("/values", sample_png, levels=4)
    assert r.status_code == 200
    body = r.json()
    assert body["image"].startswith("data:image/png;base64,")
    assert len(body["tones"]) == 4


def test_export_pdf(sample_png):
    r = post("/export", sample_png, cols=5)
    assert r.status_code == 200
    assert r.content.startswith(b"%PDF")


def test_not_an_image():
    r = post("/grid", b"hello")
    assert r.status_code == 400


def test_bad_params(sample_png):
    r = post("/grid", sample_png, cols=0)
    assert r.status_code == 422


def test_shapes(sample_png):
    r = post("/shapes", sample_png, simplicity=3)
    assert r.status_code == 200
    body = r.json()
    assert body["width"] > 0
    assert isinstance(body["shapes"], list)
