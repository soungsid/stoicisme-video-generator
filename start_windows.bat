@echo off
echo ========================================
echo YouTube Video Generator - Windows Setup
echo ========================================
echo.

:: Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Verifier si Node.js est installe
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Node.js n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Node.js depuis https://nodejs.org/
    pause
    exit /b 1
)

echo [1/6] Creation de l'environnement virtuel Python...
cd backend
if not exist "venv" (
    python -m venv venv
    echo Environnement virtuel cree avec succes
) else (
    echo Environnement virtuel existe deja
)

echo.
echo [2/6] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo [3/6] Installation des dependances Python...
pip install -r requirements.txt

echo.
echo [4/6] Installation des dependances Node.js...
cd ..\frontend
if not exist "node_modules" (
    call npm install
) else (
    echo node_modules existe deja
)

echo.
echo [5/6] Demarrage du backend...
cd ..\backend
start "Backend Server" cmd /k "venv\Scripts\activate.bat && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload"

echo.
echo [6/6] Demarrage du frontend...
cd ..\frontend
start "Frontend Server" cmd /k "set PORT=3000 && npm start"

echo.
echo ========================================
echo Serveurs demarres avec succes !
echo ========================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo ========================================
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul
