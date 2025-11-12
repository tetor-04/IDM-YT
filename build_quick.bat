@echo off
REM Quick Build Script for IDM Video Downloader

echo Building IDM Video Downloader...
echo.

REM Install/update PyInstaller
pip install --upgrade pyinstaller >nul 2>&1

REM Clean previous builds
if exist "dist" rd /s /q "dist" >nul 2>&1
if exist "build" rd /s /q "build" >nul 2>&1

REM Build with PyInstaller
pyinstaller --clean --onefile --noconsole --name "IDM_VideoDownloader" ^
    --add-data "plugins;plugins" ^
    --hidden-import=yt_dlp ^
    --hidden-import=PIL ^
    --hidden-import=pyperclip ^
    video_downloader.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\IDM_VideoDownloader.exe
    echo.
) else (
    echo.
    echo BUILD FAILED! Check errors above.
    echo.
)

pause
