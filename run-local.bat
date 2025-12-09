@echo off

echo Icon Manager Local Run Script (Compatible with Python 3.13)
echo ------------------------

REM Create necessary directory structure
echo Creating necessary directory structure...
mkdir static 2>nul
mkdir static\icons 2>nul
mkdir static\icons\Uncategorized 2>nul
mkdir templates 2>nul
mkdir data 2>nul

REM Check if pip is installed, if not prompt to install Python
echo Checking Python environment...
pip --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: pip not found, please install Python 3.6 or higher first
    echo Recommended to install Python 3.10 or 3.11 for best compatibility
    pause
    exit /b 1
)

REM Install required dependencies (using --user option to avoid permission issues)
echo Installing Python dependencies...
echo Note: Using --user option to install to user directory, avoiding permission issues
echo If the installation process is slow, please be patient...
pip install --user -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Dependency installation failed!
    echo Please try the following solutions:
    echo 1. Ensure you have network connection
    echo 2. Try running this script with administrator privileges
    echo 3. If still failing, you can try installing Flask alone: pip install --user flask
    echo 4. Then run: python app.py (basic functionality may still be available even if some dependencies aren't installed)
    echo ----------------------------------------
    echo Press 1 to continue installation (retry), press 2 to skip dependency installation and run the app directly
    choice /c 12 /n
    if %ERRORLEVEL% equ 2 (
        echo Skipping dependency installation, trying to run the app directly...
    ) else (
        pause
        exit /b 1
    )
)

echo Setting environment variables...
REM Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set SECRET_KEY=icon_manager_secret_key
set ICON_STORAGE_PATH=./static/icons

echo Starting Icon Manager...
echo ----------------------------------------
echo Access URL: http://localhost:5000
echo ----------------------------------------
echo Tips:
echo - Please open the above address in your browser to access Icon Manager
echo - To stop the application, close this window or press Ctrl+C

REM Run application directly with Python to avoid flask command issues
python app.py

if %ERRORLEVEL% neq 0 (
    echo Application failed to start!
    echo Possible reasons:
    echo 1. Port 5000 is already in use
    echo 2. Missing dependencies
    echo 3. Permission issues
    echo Please try running this script with administrator privileges
)

echo Application stopped
pause