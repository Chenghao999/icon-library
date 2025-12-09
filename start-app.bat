@echo off

echo ===========================
echo ICON MANAGER SYSTEM STARTUP
echo ============================

REM Create necessary directories
if not exist "static" mkdir "static"
if not exist "static\icons" mkdir "static\icons"
if not exist "data" mkdir "data"
if not exist "templates" mkdir "templates"

REM Set environment variables
echo Setting environment variables...
set FLASK_APP=app.py
set FLASK_ENV=development
set SECRET_KEY=your_development_secret_key_here
set ICON_STORAGE_PATH=./static/icons

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.6 or higher first.
    pause
    exit /b 1
)

REM Check if Flask is installed, try to install if not found
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Flask not found, trying to install...
    pip install flask --user
    if %errorlevel% neq 0 (
        echo WARNING: Failed to install Flask. Please install Flask manually.
        echo Command: pip install flask
        pause
    )
)

echo Starting icon manager system...
echo Access URL: http://localhost:5000
echo(
echo Press Ctrl+C to stop the server

REM Start the application
python app.py

REM Catch errors if any
if %errorlevel% neq 0 (
    echo(
    echo Application startup failed! Please check:
    echo 1. If port 5000 is already in use
    echo 2. If all dependencies are properly installed
    echo 3. If you have sufficient file permissions
    echo(
    echo Press any key to exit...
    pause
    exit /b 1
)