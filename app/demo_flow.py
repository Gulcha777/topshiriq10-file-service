import io
import json
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app


def _make_png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (800, 600), (41, 128, 185)).save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    client = TestClient(app, raise_server_exceptions=False)

    print("--- POST /api/v1/files/upload (haqiqiy PNG rasm)")
    r1 = client.post("/api/v1/files/upload", files={"file": ("mahsulot.png", _make_png(), "image/png")})
    print("HTTP", r1.status_code)
    print(json.dumps(r1.json(), indent=2, ensure_ascii=False))

    print("\n--- POST /api/v1/files/upload (ruxsat etilmagan .exe fayl)")
    r2 = client.post("/api/v1/files/upload", files={"file": ("virus.exe", b"MZ-fake", "application/octet-stream")})
    print("HTTP", r2.status_code)
    print(json.dumps(r2.json(), indent=2, ensure_ascii=False))

    print("\n--- POST /api/v1/files/upload (5 MB dan katta fayl)")
    big_pdf = b"%PDF-1.4" + (b"0" * (5 * 1024 * 1024 + 50))
    r3 = client.post("/api/v1/files/upload", files={"file": ("katta.pdf", big_pdf, "application/pdf")})
    print("HTTP", r3.status_code)
    print(json.dumps(r3.json(), indent=2, ensure_ascii=False))

    print("\n--- GET /api/v1/files/00000000-0000-0000-0000-000000000000 (mavjud emas)")
    r4 = client.get("/api/v1/files/00000000-0000-0000-0000-000000000000")
    print("HTTP", r4.status_code)
    print(json.dumps(r4.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
