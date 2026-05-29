@echo off
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python was not found.
    echo Please download and install Python from:  https://www.python.org/downloads/
    echo IMPORTANT: During installation, check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)
echo Installing dependencies for POE2 Overlay Timer...
echo.
pip install -r requirements.txt
echo.
echo ============================================
echo  Done!  You can now double-click run.bat
echo ============================================
echo.
pause
