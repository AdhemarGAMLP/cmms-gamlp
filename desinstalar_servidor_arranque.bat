@echo off
title Desinstalador - Servidor SGEM GAMLP al Arranque
echo Eliminando tarea de inicio automatico...
schtasks /Delete /TN "SGEM_GAMLP_ServidorWeb" /F
schtasks /Delete /TN "HEAS_CMMS_ServidorWeb" /F >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Tarea eliminada. El servidor ya no iniciara automaticamente.
) else (
    echo [INFO] La tarea no existia o ya fue eliminada.
)
pause
