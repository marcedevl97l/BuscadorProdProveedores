@echo off
chcp 65001 >nul
color 0B
cls

echo.
echo ════════════════════════════════════════════════════════════
echo    ⚡ INICIO RÁPIDO - Buscador de Productos
echo ════════════════════════════════════════════════════════════
echo.

REM Verificar que existe la base de datos (en ambas ubicaciones posibles)
set DB_ENCONTRADA=0
if exist db.sqlite (
    set DB_ENCONTRADA=1
    echo    ✓ Base de datos encontrada: db.sqlite
)
if exist data\db.sqlite (
    set DB_ENCONTRADA=1
    echo    ✓ Base de datos encontrada: data\db.sqlite
)

if %DB_ENCONTRADA%==0 (
    echo    ❌ ERROR: No existe la base de datos
    echo.
    echo    📌 Ejecuta primero: INICIAR_PROYECTO.bat
    echo       para crear la base de datos y cargar los productos
    echo.
    pause
    exit /b 1
)

echo    🌐 Iniciando servidor...
echo    🔗 Abriendo: http://localhost:5000
echo.
echo    ⏸️  Presiona Ctrl+C para detener el servidor
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM Abrir navegador después de 2 segundos
timeout /t 2 /nobreak >nul
start http://localhost:5000

REM Iniciar Flask
python app.py

pause