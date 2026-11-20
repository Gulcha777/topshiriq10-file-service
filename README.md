# Topshiriq №10 (M10 + A10): Fayllarni yuklash, qayta ishlash va Global Exception Handler

**Talaba:** Xamroyeva Gulruh  
**Guruh:** 1-1DIM-24  
**GitHub repozitoriy:** https://github.com/Gulcha777/topshiriq10-file-service

---

## Loyiha imkoniyatlari

1. **Fayl yuklash (`POST /api/v1/files/upload`):**
   - `multipart/form-data` orqali fayl qabul qiladi.
   - Ruxsat etilgan turlar: `jpg`, `png`, `pdf` (kengaytma, MIME va magic bytes tekshiruvi).
   - Maksimal hajm limiti: **5 MB** (oshsa `413 Payload Too Large`).
   - Har bir fayl diskka **UUID4** noyob nomi bilan saqlanadi.
2. **Rasmlarni qayta ishlash va metama'lumotlar:**
   - `jpg` va `png` rasmlar uchun Pillow yordamida avtomatik **300x300 thumbnail** yaratiladi.
   - Metama'lumotlar (`id`, `original_filename`, `stored_filename`, `size_bytes`, `width`, `height`, `created_at`) ma'lumotlar bazasida saqlanadi.
   - Yuklab olish: `GET /api/v1/files/{id}/download` va `GET /api/v1/files/{id}/thumbnail`.
3. **Global Exception Handler (`app/exceptions.py`):**
   - `NotFoundException` (`404`), `ValidationException` (`400`), `FileTooLargeException` (`413`) va kutilmagan xatoliklar (`500`).
   - Barcha xatoliklar yagona JSON formatda qaytadi: `{timestamp, status, error, message, path}`.
4. **Hujjatlar va testlar:**
   - **Swagger UI:** `http://localhost:8000/docs` (`docs/openapi.json`, `docs/swagger_ui.png`)
   - **Postman kolleksiyasi:** `postman/file_service.postman_collection.json`
   - **Avtomatik testlar:** `pytest -v` (`tests/test_files_and_errors.py`)

---

## Ishga tushirish

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Testlarni ishga tushirish:

```bash
pytest -v
```
