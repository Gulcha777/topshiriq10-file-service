import io
import uuid
from pathlib import Path
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError
from app.config import Settings
from app.exceptions import FileTooLargeException, ValidationException

ALLOWED_MIME_BY_EXT = {"jpg": {"image/jpeg"}, "png": {"image/png"}, "pdf": {"application/pdf"}}
MAGIC_SIGNATURES = {"jpg": [b"\xff\xd8\xff"], "png": [b"\x89PNG\r\n\x1a\n"], "pdf": [b"%PDF-"]}


def _extract_extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        raise ValidationException("Fayl nomi yoki kengaytmasi mavjud emas", details=[{"field": "file", "message": "Ruxsat etilgan turlar: jpg, png, pdf"}])
    ext = filename.rsplit(".", 1)[-1].lower().strip()
    return "jpg" if ext == "jpeg" else ext


def _verify_magic_bytes(data: bytes, ext: str) -> bool:
    return any(data.startswith(sig) for sig in MAGIC_SIGNATURES.get(ext, []))


async def validate_and_process_upload(file: UploadFile, cfg: Settings) -> dict:
    ext = _extract_extension(file.filename)
    if ext not in cfg.allowed_ext_set:
        raise ValidationException(
            f"Ruxsat etilmagan fayl turi: '.{ext}'. Faqat {', '.join(sorted(cfg.allowed_ext_set))} yuklash mumkin",
            details=[{"field": "file", "message": f"'.{ext}' formati qo'llab-quvvatlanmaydi"}],
        )

    allowed_mimes = ALLOWED_MIME_BY_EXT.get(ext, set())
    if file.content_type and file.content_type.lower() not in allowed_mimes:
        raise ValidationException(
            f"Fayl MIME turi ({file.content_type}) kengaytmaga (.{ext}) mos kelmaydi",
            details=[{"field": "file", "message": "Content-Type mos emas"}],
        )

    raw_bytes = await file.read()
    size_bytes = len(raw_bytes)
    if size_bytes == 0:
        raise ValidationException("Bo'sh fayl yuklash mumkin emas", details=[{"field": "file", "message": "Fayl hajmi 0 bayt"}])

    if size_bytes > cfg.max_file_size_bytes:
        raise FileTooLargeException(
            f"Fayl hajmi ({size_bytes / (1024 * 1024):.2f} MB) maksimal {cfg.max_file_size_mb} MB limitdan katta",
            details=[{"field": "file", "message": f"Maksimal hajm: {cfg.max_file_size_mb} MB"}],
        )

    if not _verify_magic_bytes(raw_bytes, ext):
        raise ValidationException(
            "Fayl ichki tuzilmasi (magic bytes) ko'rsatilgan formatga mos kelmaydi",
            details=[{"field": "file", "message": "Soxta yoki buzilgan fayl sarlavhasi"}],
        )

    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}.{ext}"
    original_path: Path = cfg.originals_path / stored_filename
    original_path.write_bytes(raw_bytes)

    has_thumbnail = False
    thumbnail_path_str: str | None = None
    width: int | None = None
    height: int | None = None

    if ext in {"jpg", "png"}:
        try:
            with Image.open(io.BytesIO(raw_bytes)) as img:
                width, height = img.size
                thumb = img.copy()
                thumb.thumbnail((cfg.thumbnail_size, cfg.thumbnail_size))
                if ext == "jpg" and thumb.mode in ("RGBA", "P"):
                    thumb = thumb.convert("RGB")
                thumb_full_path = cfg.thumbnails_path / f"thumb_{stored_filename}"
                thumb.save(thumb_full_path, format="JPEG" if ext == "jpg" else "PNG", optimize=True, quality=85)
                has_thumbnail = True
                thumbnail_path_str = str(thumb_full_path)
        except UnidentifiedImageError as exc:
            original_path.unlink(missing_ok=True)
            raise ValidationException("Rasm fayli buzilgan yoki o'qib bo'lmaydi") from exc

    return {
        "id": file_id,
        "original_filename": file.filename or stored_filename,
        "stored_filename": stored_filename,
        "content_type": file.content_type or f"application/{ext}",
        "extension": ext,
        "size_bytes": size_bytes,
        "storage_path": str(original_path),
        "has_thumbnail": has_thumbnail,
        "thumbnail_path": thumbnail_path_str,
        "width": width,
        "height": height,
    }
