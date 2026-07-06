# build_exe.ps1 - generates JobApp-AI-Assistant-Windows.exe
# Ejecutar desde la raiz del proyecto: .\build_exe.ps1

$ErrorActionPreference = "Stop"
Write-Host "Instalando dependencias..." -ForegroundColor Cyan
pip install -r requirements.txt -q

Write-Host "Construyendo ejecutable..." -ForegroundColor Cyan
pyinstaller `
    --onefile `
    --noconsole `
    --name "JobApp-AI-Assistant-Windows" `
    --add-data "static;static" `
    --add-data "pagbiomics_embed.html;." `
    --hidden-import uvicorn.logging `
    --hidden-import uvicorn.loops `
    --hidden-import uvicorn.loops.auto `
    --hidden-import uvicorn.protocols `
    --hidden-import uvicorn.protocols.http `
    --hidden-import uvicorn.protocols.http.auto `
    --hidden-import uvicorn.protocols.websockets `
    --hidden-import uvicorn.protocols.websockets.auto `
    --hidden-import uvicorn.lifespan `
    --hidden-import uvicorn.lifespan.on `
    --hidden-import fastapi `
    --hidden-import jobapp_ai_assistant `
    --hidden-import multipart `
    --hidden-import pypdf `
    --hidden-import docx `
    --hidden-import reportlab `
    --hidden-import bs4 `
    --hidden-import httpx `
    launcher.py

Write-Host ""
Write-Host "LISTO: dist\JobApp-AI-Assistant-Windows.exe" -ForegroundColor Green
Write-Host "Doble-clic para arrancar. Prefiere localhost:8080; si esta ocupado usa 8090/8091/8000 o un puerto libre 8100+." -ForegroundColor Green
Write-Host "Para distribuir, comparte solo dist\JobApp-AI-Assistant-Windows.exe. Los datos se crean localmente en el PC del usuario." -ForegroundColor Green
