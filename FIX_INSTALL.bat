@echo off
title Reparador de Instalacion
echo 1. Creando carpeta de entorno...
python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo Error: No se pudo crear el entorno virtual. ¿Tienes Python instalado?
    pause
    exit
)

echo 2. Instalando librerias (esto puede tardar unos minutos)...
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install playwright pandas openpyxl flask flask-login beautifulsoup4 requests python-dotenv

echo 3. Instalando navegadores de Playwright...
.\.venv\Scripts\python -m playwright install chromium

echo 4. Verificando...
.\.venv\Scripts\python -c "import playwright; print('--- INSTALACION TERMINADA CON EXITO ---')"
pause
