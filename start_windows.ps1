# YouTube Video Generator - Windows PowerShell Setup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YouTube Video Generator - Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier si Python est installe
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python trouve: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Python n'est pas installe" -ForegroundColor Red
    Write-Host "Telechargez Python depuis https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

# Verifier si Node.js est installe
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js trouve: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Node.js n'est pas installe" -ForegroundColor Red
    Write-Host "Telechargez Node.js depuis https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

Write-Host ""
Write-Host "[1/6] Creation de l'environnement virtuel Python..." -ForegroundColor Yellow
Set-Location backend

if (-Not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "Environnement virtuel cree avec succes" -ForegroundColor Green
} else {
    Write-Host "Environnement virtuel existe deja" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/6] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "[3/6] Installation des dependances Python..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "[4/6] Installation des dependances Node.js..." -ForegroundColor Yellow
Set-Location ..\frontend

if (-Not (Test-Path "node_modules")) {
    npm install
} else {
    Write-Host "node_modules existe deja" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/6] Demarrage du backend..." -ForegroundColor Yellow
Set-Location ..\backend
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& .\venv\Scripts\Activate.ps1; python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload" -PassThru
Write-Host "Backend demarre (PID: $($backendJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "[6/6] Demarrage du frontend..." -ForegroundColor Yellow
Set-Location ..\frontend
$env:PORT = "3000"
$frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -PassThru
Write-Host "Frontend demarre (PID: $($frontendJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Serveurs demarres avec succes !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour arreter les serveurs, fermez les fenetres PowerShell ou utilisez Ctrl+C" -ForegroundColor Yellow

Read-Host "Appuyez sur Entree pour fermer cette fenetre"
