@echo off
setlocal enabledelayedexpansion
title Jarvis Installation Protocol
echo ==========================================
echo JARVIS SMART WEB INSTALLER
echo ==========================================
echo.
cd /d "%~dp0"

echo [1/4] Comprobando instalacion de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ALERTA] Python no esta instalado.
    echo Descargando e instalando Python 3.11 usando winget...
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo instalar Python automaticamente.
        echo Se abrira tu navegador para que lo descargues manualmente.
        echo Por favor, asegurate de marcar la casilla "Add Python to PATH" durante la instalacion.
        pause
        start https://www.python.org/downloads/
        exit /b 1
    )
    echo [EXITO] Python instalado correctamente. Por favor, reinicia este script.
    pause
    exit /b 0
) else (
    echo [EXITO] Python detectado.
)

echo.
echo [2/4] Creando Entorno Virtual Aislado...
if not exist ".venv" (
    python -m venv .venv
    echo [EXITO] Entorno virtual creado.
) else (
    echo [INFO] El entorno virtual ya existe.
)

echo.
echo [3/4] Instalando Librerias de IA y Vision (Esto puede tardar unos minutos)...
call .venv\Scripts\activate
python -m pip install --upgrade pip >nul 2>&1
pip install -r backend\requirements.txt

echo.
echo ==========================================
echo [4/4] INSTALACION COMPLETADA
echo ==========================================
echo.
echo Iniciando el Panel de Ajustes para tu configuracion inicial...
start /b python backend\gui.py
exit
