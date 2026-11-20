from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.exceptions import NotFoundException
from app.models import FileMetadata
from app.schemas import ErrorResponse, FileListResponse, FileUploadResponse
from app.services import validate_and_process_upload

router = APIRouter(prefix="/api/v1/files", tags=["Files"])


def _to_response(record: FileMetadata) -> FileUploadResponse:
    return FileUploadResponse(
        id=record.id,
        original_filename=record.original_filename,
        stored_filename=record.stored_filename,
        content_type=record.content_type,
        extension=record.extension,
        size_bytes=record.size_bytes,
        has_thumbnail=record.has_thumbnail,
        width=record.width,
        height=record.height,
        download_url=f"/api/v1/files/{record.id}/download",
        thumbnail_url=f"/api/v1/files/{record.id}/thumbnail" if record.has_thumbnail else None,
        created_at=record.created_at,
    )


@router.post("/upload", response_model=FileUploadResponse, status_code=201, summary="Fayl yuklash (multipart/form-data)", responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}})
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    meta_dict = await validate_and_process_upload(file, settings)
    record = FileMetadata(**meta_dict)
    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_response(record)


@router.get("", response_model=FileListResponse, summary="Barcha yuklangan fayllar metama'lumotlari")
def list_files(db: Session = Depends(get_db)):
    records = db.scalars(select(FileMetadata).order_by(FileMetadata.created_at.desc())).all()
    return FileListResponse(total=len(records), items=[_to_response(r) for r in records])


@router.get("/{file_id}", response_model=FileUploadResponse, summary="Bitta fayl metama'lumotlari", responses={404: {"model": ErrorResponse}})
def get_file_metadata(file_id: str, db: Session = Depends(get_db)):
    record = db.get(FileMetadata, file_id)
    if record is None:
        raise NotFoundException(f"ID='{file_id}' bo'lgan fayl topilmadi")
    return _to_response(record)


@router.get("/{file_id}/download", summary="Asl faylni yuklab olish", responses={404: {"model": ErrorResponse}})
def download_file(file_id: str, db: Session = Depends(get_db)):
    record = db.get(FileMetadata, file_id)
    if record is None:
        raise NotFoundException(f"ID='{file_id}' bo'lgan fayl topilmadi")
    file_path = Path(record.storage_path)
    if not file_path.exists():
        raise NotFoundException(f"Fayl diskda mavjud emas: {record.stored_filename}")
    return FileResponse(path=file_path, media_type=record.content_type, filename=record.original_filename)


@router.get("/{file_id}/thumbnail", summary="Thumbnail rasmni yuklab olish", responses={404: {"model": ErrorResponse}})
def download_thumbnail(file_id: str, db: Session = Depends(get_db)):
    record = db.get(FileMetadata, file_id)
    if record is None:
        raise NotFoundException(f"ID='{file_id}' bo'lgan fayl topilmadi")
    if not record.has_thumbnail or not record.thumbnail_path:
        raise NotFoundException("Ushbu fayl turi uchun thumbnail mavjud emas")
    thumb_path = Path(record.thumbnail_path)
    if not thumb_path.exists():
        raise NotFoundException("Thumbnail fayli diskda topilmadi")
    return FileResponse(path=thumb_path, media_type=record.content_type, filename=f"thumb_{record.original_filename}")


@router.delete("/{file_id}", status_code=204, summary="Faylni o'chirish", responses={404: {"model": ErrorResponse}})
def delete_file(file_id: str, db: Session = Depends(get_db)):
    record = db.get(FileMetadata, file_id)
    if record is None:
        raise NotFoundException(f"ID='{file_id}' bo'lgan fayl topilmadi")
    Path(record.storage_path).unlink(missing_ok=True)
    if record.thumbnail_path:
        Path(record.thumbnail_path).unlink(missing_ok=True)
    db.delete(record)
    db.commit()
