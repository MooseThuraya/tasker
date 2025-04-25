@echo off
REM Task Manager Application Launcher for Windows
REM This script provides a quick way to start the application

echo Task Manager - Application Launcher
echo ----------------------------------

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.11 or higher.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [SETUP] Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo [SETUP] Creating .env file...
    copy .env.example .env
    echo   Note: You may want to edit .env for custom configuration.
)

REM Run the application
echo.
echo [START] Starting application...
echo [INFO] The application will be available at: http://localhost:5001
echo [INFO] Press Ctrl+C to stop the server when you're done
echo.
python app.py