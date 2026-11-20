from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "File Upload & Global Exception Handler API"
    database_url: str = "sqlite:///./files_meta.db"
    upload_dir: str = "uploads"
    max_file_size_mb: int = 5
    thumbnail_size: int = 300
    allowed_extensions: str = "jpg,png,pdf"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_ext_set(self) -> set[str]:
        return {ext.strip().lower().lstrip(".") for ext in self.allowed_extensions.split(",") if ext.strip()}

    @property
    def originals_path(self) -> Path:
        p = Path(self.upload_dir) / "originals"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def thumbnails_path(self) -> Path:
        p = Path(self.upload_dir) / "thumbnails"
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
