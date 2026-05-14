@echo off
REM Build the game executable with PyInstaller.
echo Instaluji PyInstaller...
python -m pip install pyinstaller
echo.
echo Builduju exe...
python -m PyInstaller --onefile --windowed --add-data "assets;assets" game.py
echo.
echo Build finished. Output is in dist\game.exe
pause
