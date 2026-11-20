from datetime import datetime, timezone
from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class AppException(Exception):
    def __init__(self, status_code: int, message: str, details: list[dict] | None = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "So'ralgan resurs topilmadi", details: list[dict] | None = None):
        super().__init__(status_code=404, message=message, details=details)


class ValidationException(AppException):
    def __init__(self, message: str = "Validatsiya xatosi", details: list[dict] | None = None):
        super().__init__(status_code=400, message=message, details=details)


class FileTooLargeException(AppException):
    def __init__(self, message: str = "Fayl hajmi ruxsat etilgan maksimal chegaradan oshdi", details: list[dict] | None = None):
        super().__init__(status_code=413, message=message, details=details)


def _build_error_payload(status_code: int, message: str, path: str, details: list[dict] | None = None) -> dict:
    try:
        error_phrase = HTTPStatus(status_code).phrase
    except ValueError:
        error_phrase = "Error"
    payload = {
        "timestamp": _iso_now(),
        "status": status_code,
        "error": error_phrase,
        "message": message,
        "path": path,
    }
    if details:
        payload["details"] = details
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=_build_error_payload(exc.status_code, exc.message, request.url.path, exc.details))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"field": ".".join(str(p) for p in err.get("loc", []) if p != "body") or None, "message": err.get("msg", "Noto'g'ri qiymat")} for err in exc.errors()]
        return JSONResponse(status_code=400, content=_build_error_payload(400, "So'rov parametrlari validatsiyadan o'tmadi", request.url.path, details))

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=_build_error_payload(exc.status_code, str(exc.detail), request.url.path))

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content=_build_error_payload(500, "Serverda kutilmagan ichki xatolik yuz berdi", request.url.path))
