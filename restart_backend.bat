@echo off
echo ========================================
echo Redemarrage du Backend
echo ========================================
echo.

echo [1/2] Arret du backend...
cd backend
taskkill /F /IM python.exe 2>nul

echo.
echo [2/2] Demarrage du backend...
start "Backend Server" cmd /k "venv\Scripts\activate.bat && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

echo.
echo ========================================
echo Backend redemarr�!
echo ========================================
echo Backend:  http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo ========================================
echo.
timeout /t 3 >nul
