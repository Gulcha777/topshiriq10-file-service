#!/usr/bin/env bash
set -e
git init -b main
git add .
git commit -m "Topshiriq 10: File upload, thumbnail va Global Exception Handler"
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/Gulcha777/topshiriq10-file-service.git
git push -u origin main
