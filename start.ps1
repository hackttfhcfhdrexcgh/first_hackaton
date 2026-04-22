# Fog of War - MTBank - запуск из PowerShell
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fog of War - MTBank - Запуск" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[1/3] Установка Python-зависимостей..." -ForegroundColor Yellow
Push-Location "$root\backend"
pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) { Write-Host "Ошибка pip" -ForegroundColor Red; Pop-Location; exit 1 }
Pop-Location

Write-Host "[2/3] Установка Node-зависимостей..." -ForegroundColor Yellow
Push-Location "$root\frontend"
if (-not (Test-Path "node_modules")) {
    npm install --silent
    if ($LASTEXITCODE -ne 0) { Write-Host "Ошибка npm" -ForegroundColor Red; Pop-Location; exit 1 }
}
Pop-Location

Write-Host "[3/3] Запуск backend и frontend..." -ForegroundColor Yellow
Write-Host "`nBackend:  http://localhost:8000"
Write-Host "Frontend: http://localhost:5173`n"

Start-Process cmd -ArgumentList "/k", "cd /d `"$root\backend`" && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
Start-Sleep -Seconds 3
Start-Process cmd -ArgumentList "/k", "cd /d `"$root\frontend`" && npm run dev"
Start-Sleep -Seconds 6
Start-Process "http://localhost:5173"

Write-Host "Готово. Если браузер не открылся - зайди на http://localhost:5173" -ForegroundColor Green
