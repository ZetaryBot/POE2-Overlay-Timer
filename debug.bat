@echo off
echo Running in DEBUG mode (overlay always visible, events printed here).
echo.
echo Usage:
echo   debug.bat                        show overlay, print all events
echo   debug.bat "The Riverbank"        also load notes for that map immediately
echo   debug.bat --list-notes           list all parsed notes and exit
echo.

if "%~1"=="" (
    python main.py --debug
) else if "%~1"=="--list-notes" (
    python main.py --list-notes
) else (
    python main.py --test-map "%~1"
)
pause
