from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    timestamp: str
    status: int
    error: str
    message: str
    path: str
    details: list[ErrorDetail] | None = None


class FileUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    stored_filename: str
    content_type: str
    extension: str
    size_bytes: int
    has_thumbnail: bool
    width: int | None = None
    height: int | None = None
    download_url: str
    thumbnail_url: str | None = None
    created_at: datetime


class FileListResponse(BaseModel):
    total: int
    items: list[FileUploadResponse]
