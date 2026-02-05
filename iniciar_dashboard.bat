@echo off
REM EDA Dashboard - Ejecutable para iniciar la aplicación
cd /d "%~dp0"

echo.
echo ========================================
echo  INICIANDO EDA DASHBOARD
echo ========================================
echo.

set VENV_PYTHON=%~dp0venv_eda\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Entorno virtual no encontrado
    echo Crea el entorno con: python -m venv venv_eda
    pause
    exit /b 1
)

echo [INFO] Verificando dependencias...
"%VENV_PYTHON%" -c "import fastapi, uvicorn, streamlit, pandas" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    "%VENV_PYTHON%" -m pip install -r requirements.txt
)

echo [OK] Iniciando Backend (Puerto 8000)...
start "Backend - EDA Dashboard" cmd /k "cd /d "%~dp0" && "%VENV_PYTHON%" -m uvicorn api.main:app --reload --port 8000"

echo [INFO] Esperando 8 segundos...
timeout /t 8 /nobreak >nul

echo [OK] Iniciando Frontend (Puerto 8503)...
start "Frontend - EDA Dashboard" cmd /k "cd /d "%~dp0" && "%VENV_PYTHON%" -m streamlit run ui/app.py --server.port 8503"

echo [INFO] Esperando 10 segundos...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo  DASHBOARD INICIADO
echo ========================================
echo.
echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:8503
echo.

start "" http://localhost:8503

echo Abriendo navegador...
pause
