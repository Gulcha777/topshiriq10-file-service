@echo off
chcp 65001 >nul
echo ========================================================
echo   TOPSHIRIQ 10 - GITHUBGA AVTOMATIK YUKLASH SKRIPTI
echo ========================================================
echo.
git init -b main
git add .
git commit -m "Topshiriq 10: File upload, thumbnail va Global Exception Handler"
git remote remove origin 2>nul
git remote add origin https://github.com/Gulcha777/topshiriq10-file-service.git
echo.
echo GitHub repozitoriyga yuklanmoqda: https://github.com/Gulcha777/topshiriq10-file-service
git push -u origin main
echo.
pause
