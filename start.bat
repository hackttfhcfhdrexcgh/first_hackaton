@echo off
chcp 65001 >nul
setlocal

echo ========================================
echo   Fog of War - MTBank - Запуск
echo ========================================
echo.

set "ROOT=%~dp0"

echo [1/3] Установка Python-зависимостей...
pushd "%ROOT%backend"
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ОШИБКА: не удалось установить Python-зависимости
    popd
    pause
    exit /b 1
)
popd

echo [2/3] Установка Node-зависимостей...
pushd "%ROOT%frontend"
if not exist node_modules (
    call npm install --silent
    if errorlevel 1 (
        echo ОШИБКА: не удалось установить npm-зависимости
        popd
        pause
        exit /b 1
    )
)
popd

echo [3/3] Запуск backend и frontend...
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.

start "Fog of War - Backend" cmd /k "cd /d "%ROOT%backend" && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul
start "Fog of War - Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

timeout /t 6 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo Если браузер не открылся - зайди на http://localhost:5173
echo.
pause
endlocal
