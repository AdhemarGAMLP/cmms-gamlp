@echo off
chcp 65001 > nul
title Respaldo Automatico - CMMS GAMLP
echo ========================================================
echo   RESPALDO AUTOMATICO CMMS GAMLP EN GITHUB
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Revisando cambios pendientes...
git add -A

git diff --cached --quiet
if %errorlevel% equ 0 (
    echo [INFO] No hay cambios nuevos. Todo tu codigo ya esta seguro y al dia en GitHub.
    echo.
    timeout /t 5
    exit /b 0
)

for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set FECHA=%%a-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set HORA=%%a:%%b

echo [2/3] Registrando cambios...
git commit -m "Respaldo automatico: %FECHA% %HORA%"

echo [3/3] Subiendo a GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   [EXITO] Codigo respaldado al 100%% en GitHub y Render!
    echo ========================================================
) else (
    echo.
    echo [ALERTA] Hubo un problema al subir. Revisa tu conexion a internet.
)

echo.
timeout /t 5
