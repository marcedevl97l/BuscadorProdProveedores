@echo off
chcp 65001 >nul
color 0E
cls

echo.
echo ════════════════════════════════════════════════════════════
echo    🔄 ACTUALIZAR DATOS
echo ════════════════════════════════════════════════════════════
echo.

REM 1. BORRAR BASE DE DATOS VIEJA
echo [1/3] 🗑️  Limpiando base de datos...
if exist db.sqlite (
    del /F /Q db.sqlite
    echo       ✓ db.sqlite eliminado
)
if exist data\db.sqlite (
    del /F /Q data\db.sqlite
    echo       ✓ data\db.sqlite eliminado
)
echo.

REM 2. CREAR BASE DE DATOS NUEVA
echo [2/3] 🔨 Creando base de datos...
python init_db.py
if %ERRORLEVEL% NEQ 0 (
    echo       ❌ Error al crear base de datos
    pause
    exit /b 1
)
echo.

REM 3. RECARGAR DATOS
echo [3/4] 📊 Recargando datos de Excel...
python recolector.py
if %ERRORLEVEL% NEQ 0 (
    echo       ❌ Error al recargar datos de Excel
    pause
    exit /b 1
)
echo.

REM 4. RECARGAR DATOS DE FARMACOM
echo [4/4] 🌐 Recargando datos de Farmacom...
python scraper_farmacom.py
if %ERRORLEVEL% NEQ 0 (
    echo       ❌ Error al recargar datos de Farmacom
    pause
    exit /b 1
)
echo.

echo ════════════════════════════════════════════════════════════
echo    ✅ DATOS ACTUALIZADOS CORRECTAMENTE
echo ════════════════════════════════════════════════════════════
echo.
echo    💡 Ejecuta ABRIR_BUSCADOR.bat para usar el buscador
echo.

pause