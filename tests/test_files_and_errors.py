from tests.conftest import make_sample_jpg, make_sample_pdf, make_sample_png


def test_upload_png_creates_thumbnail_and_metadata(client):
    png_bytes = make_sample_png(800, 600)
    res = client.post("/api/v1/files/upload", files={"file": ("rasm.png", png_bytes, "image/png")})
    assert res.status_code == 201
    data = res.json()
    assert data["original_filename"] == "rasm.png"
    assert data["stored_filename"].endswith(".png") and data["stored_filename"] != "rasm.png"
    assert data["has_thumbnail"] is True

    dl = client.get(data["download_url"])
    assert dl.status_code == 200 and dl.content == png_bytes

    th = client.get(data["thumbnail_url"])
    assert th.status_code == 200 and len(th.content) < len(png_bytes)


def test_upload_jpg_and_pdf(client):
    jpg_res = client.post("/api/v1/files/upload", files={"file": ("photo.jpg", make_sample_jpg(), "image/jpeg")})
    assert jpg_res.status_code == 201 and jpg_res.json()["has_thumbnail"] is True

    pdf_res = client.post("/api/v1/files/upload", files={"file": ("hujjat.pdf", make_sample_pdf(), "application/pdf")})
    assert pdf_res.status_code == 201 and pdf_res.json()["has_thumbnail"] is False


def test_reject_disallowed_extension_global_json_format(client):
    res = client.post("/api/v1/files/upload", files={"file": ("virus.exe", b"MZ-fake", "application/octet-stream")})
    assert res.status_code == 400
    err = res.json()
    assert set(err.keys()) >= {"timestamp", "status", "error", "message", "path"}
    assert err["status"] == 400 and err["error"] == "Bad Request"


def test_reject_spoofed_extension_magic_bytes(client):
    res = client.post("/api/v1/files/upload", files={"file": ("soxta.png", b"oddiy matn", "image/png")})
    assert res.status_code == 400


def test_reject_file_too_large_413(client):
    oversized = b"%PDF-1.4" + (b"0" * (5 * 1024 * 1024 + 100))
    res = client.post("/api/v1/files/upload", files={"file": ("katta.pdf", oversized, "application/pdf")})
    assert res.status_code == 413
    err = res.json()
    assert err["status"] == 413 and err["error"] == "Payload Too Large"


def test_not_found_exception_format_404(client):
    res = client.get("/api/v1/files/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
    assert res.json()["error"] == "Not Found"


def test_unhandled_exception_returns_500_json(client):
    res = client.get("/api/v1/demo-error?kind=crash")
    assert res.status_code == 500
    assert res.json()["error"] == "Internal Server Error"
