@echo off
title Instalador - Servidor HEAS CMMS al Arranque
echo ============================================================
echo   HEAS CMMS - Instalar servidor web para inicio automatico
echo ============================================================
echo.
echo Este script configura Windows para iniciar automaticamente
echo el servidor web HEAS CMMS cada vez que se enciende el equipo.
echo.

set PYTHON=C:\Users\HP\miniconda3\python.exe
set SCRIPT=C:\Users\HP\Desktop\HEAS_CMMS\web_server.py
set WORKDIR=C:\Users\HP\Desktop\HEAS_CMMS

echo Registrando tarea en el Programador de Tareas de Windows...

schtasks /Create /TN "HEAS_CMMS_ServidorWeb" /TR "\"%PYTHON%\" \"%SCRIPT%\"" /SC ONSTART /RU "%USERNAME%" /RL HIGHEST /F /IT

if %ERRORLEVEL%==0 (
    echo.
    echo [OK] Tarea instalada correctamente.
    echo      El servidor web se iniciara automaticamente al encender el equipo.
    echo.
    echo Para verificar: Busca "Programador de Tareas" en Windows
    echo                y busca la tarea: HEAS_CMMS_ServidorWeb
) else (
    echo.
    echo [ERROR] No se pudo registrar la tarea.
    echo         Ejecuta este archivo como Administrador (clic derecho ^> Ejecutar como administrador)
)
echo.
pause
