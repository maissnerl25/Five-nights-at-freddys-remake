@echo off
REM Build the game executable with Python 3.12 and PyInstaller.
echo Pouzivam Python 3.12...
py -3.12 --version
echo Instaluji pyinstaller a pygame pokud nejsou nainstalovane...
py -3.12 -m pip install --user pyinstaller pygame
echo.
echo Cistim stary build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist game.spec del /f game.spec
echo.
echo Builduju exe...
py -3.12 -m PyInstaller --onefile --windowed --collect-all pygame --add-data "assets;assets" game.py
echo.
echo Build finished. Output is in dist\game.exe
pause
