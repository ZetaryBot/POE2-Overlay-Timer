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
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The program exited with an error.
    echo If you see "ModuleNotFoundError", please run install.bat first.
    echo.
    pause
)
