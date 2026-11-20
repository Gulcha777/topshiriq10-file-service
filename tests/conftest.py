import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "test_files.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "uploads"))

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def make_sample_png(width: int = 800, height: int = 600) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(34, 112, 147)).save(buf, format="PNG")
    return buf.getvalue()


def make_sample_jpg(width: int = 1024, height: int = 768) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(180, 65, 50)).save(buf, format="JPEG")
    return buf.getvalue()


def make_sample_pdf() -> bytes:
    return b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
