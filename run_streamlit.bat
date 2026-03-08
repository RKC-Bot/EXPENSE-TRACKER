@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=.venv\Scripts\python.exe"
set "APP_FILE=main.py"
set "APP_PORT=8502"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] Virtual environment Python not found: %PYTHON_EXE%
  echo Make sure this file is inside the project folder with .venv.
  pause
  exit /b 1
)

if not exist "%APP_FILE%" (
  echo [ERROR] App file not found: %APP_FILE%
  pause
  exit /b 1
)

echo Starting Streamlit on http://127.0.0.1:%APP_PORT%
"%PYTHON_EXE%" -m streamlit run "%APP_FILE%" --server.address 127.0.0.1 --server.port %APP_PORT%

if errorlevel 1 (
  echo.
  echo [ERROR] Streamlit stopped with an error.
  pause
  exit /b 1
)

endlocal
