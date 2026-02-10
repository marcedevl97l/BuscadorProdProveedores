@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
color 0B
cls

echo.
echo INICIO RAPIDO - Buscador de Productos
echo.

set DB_ENCONTRADA=0

if exist db.sqlite (
    set DB_ENCONTRADA=1
    echo Base de datos encontrada: db.sqlite
)

if exist data\db.sqlite (
    set DB_ENCONTRADA=1
    echo Base de datos encontrada: data\db.sqlite
)

echo DB_ENCONTRADA = !DB_ENCONTRADA!

if "!DB_ENCONTRADA!"=="0" (
    echo ERROR: No existe la base de datos
    echo Ejecuta primero: INICIAR_PROYECTO.bat
    echo.
    pause
    goto :eof
)

echo Iniciando servidor...
echo Abriendo: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

timeout /t 2 /nobreak >nul
start http://localhost:5000

echo Ejecutando: python app.py
call python app.py

echo.
echo El servidor se detuvo.
pause
