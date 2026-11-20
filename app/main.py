from fastapi import FastAPI
from app.config import settings
from app.database import Base, engine
from app.exceptions import NotFoundException, register_exception_handlers
from app.routers.files import router as files_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Topshiriq №10 (M10 + A10): Fayllarni yuklash, qayta ishlash va Global Exception Handler.",
)

register_exception_handlers(app)
app.include_router(files_router)


@app.get("/health", tags=["Service"], summary="Xizmat holati")
def health_check():
    return {"status": "ok", "service": "file-service", "max_file_size_mb": settings.max_file_size_mb}


@app.get("/api/v1/demo-error", tags=["Service"], summary="Global Exception Handler sinovi")
def trigger_demo_error(kind: str = "not_found"):
    if kind == "not_found":
        raise NotFoundException("Demo: bu resurs topilmadi")
    raise RuntimeError("Demo: kutilmagan server xatoligi")
