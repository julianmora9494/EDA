@echo off
cd /d "%~dp0"

echo Iniciando EDA Dashboard...
echo.

REM Usar la ruta COMPLETA al Python del entorno virtual
set VENV_PYTHON=%~dp0venv_eda\Scripts\python.exe

REM Iniciar Backend con Python del venv
start "Backend" cmd /k "%VENV_PYTHON% -m uvicorn api.main:app --reload --port 8000"

REM Esperar 6 segundos
timeout /t 6 /nobreak >nul

REM Iniciar Frontend con Python del venv (desactivar file watcher)
start "Frontend" cmd /k "%VENV_PYTHON% -m streamlit run ui\app.py --server.port 8503 --server.fileWatcherType none"

REM Esperar 8 segundos
timeout /t 8 /nobreak >nul

REM Abrir navegador
start http://localhost:8503

echo.
echo Dashboard iniciado en:
echo - Backend: http://localhost:8000/docs
echo - Frontend: http://localhost:8503
echo.
echo NO cierres las 2 ventanas que se abrieron
echo.
