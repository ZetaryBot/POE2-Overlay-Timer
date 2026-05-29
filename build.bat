@echo off
echo Building POE2 Overlay Timer as standalone exe...
pip install pyinstaller
pyinstaller --onefile --windowed --name "POE2OverlayTimer" ^
    --add-data "config.json;." ^
    --add-data "notes;notes" ^
    main.py
echo.
echo Build complete.  Executable: dist\POE2OverlayTimer.exe
pause
