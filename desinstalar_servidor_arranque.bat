@echo off
title Desinstalador - Servidor HEAS CMMS al Arranque
echo Eliminando tarea de inicio automatico...
schtasks /Delete /TN "HEAS_CMMS_ServidorWeb" /F
if %ERRORLEVEL%==0 (
    echo [OK] Tarea eliminada. El servidor ya no iniciara automaticamente.
) else (
    echo [INFO] La tarea no existia o ya fue eliminada.
)
pause
