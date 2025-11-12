@echo off
title Building Portable IDM Video Downloader
color 0B
cls

echo.
echo ================================================================
echo    Building IDM Video Downloader - Portable Edition
echo    License Valid Until: December 31, 2025
echo ================================================================
echo.

echo [Step 1/4] Checking dependencies...
python --version
if errorlevel 1 (
    echo Error: Python not found!
    pause
    exit /b 1
)

echo.
echo [Step 2/4] Installing PyInstaller if needed...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    pip install pyinstaller
)

echo.
echo [Step 3/4] Cleaning old builds...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
if exist "IDM_Portable" rmdir /s /q "IDM_Portable" 2>nul

echo.
echo [Step 4/4] Building portable executable...
echo (This will take 2-5 minutes, please wait...)
echo.

python -m PyInstaller --onefile --windowed --name="IDM_VideoDownloader" --clean --noconfirm video_downloader.py

if errorlevel 1 (
    echo.
    echo ❌ Build FAILED!
    echo Check the errors above.
    pause
    exit /b 1
)

echo.
echo [Finalizing] Creating portable package...
mkdir "IDM_Portable" 2>nul
copy "dist\IDM_VideoDownloader.exe" "IDM_Portable\" >nul

echo Creating documentation...
(
echo ================================================================
echo    IDM Video Downloader - Portable Edition
echo ================================================================
echo.
echo Version: 1.0.0
echo License: Trial version valid until December 31, 2025
echo.
echo QUICK START:
echo   1. Double-click IDM_VideoDownloader.exe
echo   2. Paste a YouTube URL
echo   3. Click "Fetch Info"
echo   4. Select Video or Audio download type
echo   5. Choose quality and download
echo.
echo FEATURES:
echo   - Download YouTube videos in multiple qualities
echo   - Extract audio as MP3 ^(320/192/128/96 kbps^)
echo   - No installation required
echo   - Completely portable
echo   - Works offline after download
echo.
echo SYSTEM REQUIREMENTS:
echo   - Windows 7 or later
echo   - Internet connection for downloads
echo   - No additional software needed
echo.
echo EXPIRATION:
echo   This trial version will stop working after December 31, 2025.
echo   Days remaining will be shown when you start the application.
echo.
echo SUPPORTED SITES:
echo   YouTube, Vimeo, Facebook, Instagram, TikTok, and 1000+ more
echo.
echo ================================================================
) > "IDM_Portable\README.txt"

echo.
echo ================================================================
echo ✅ BUILD SUCCESSFUL!
echo ================================================================
echo.
echo Portable package created in: IDM_Portable\
echo Executable: IDM_VideoDownloader.exe
echo.

for %%A in ("IDM_Portable\IDM_VideoDownloader.exe") do (
    set size=%%~zA
    set /a sizeMB=%%~zA/1024/1024
)

echo File size: %sizeMB% MB
echo.
echo You can now:
echo   • Run the executable from IDM_Portable folder
echo   • Copy IDM_Portable folder to USB drive
echo   • Share with others ^(valid until Dec 31, 2025^)
echo.
echo Opening folder...
echo.

timeout /t 3 /nobreak >nul
start "" "IDM_Portable"

pause