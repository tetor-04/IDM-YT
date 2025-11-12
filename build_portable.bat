@echo off
title Building IDM Video Downloader - Portable Windows Version
color 0B

echo.
echo ================================================================
echo    Building IDM Video Downloader - Portable Windows Version
echo    License: Valid until December 31, 2025
echo ================================================================
echo.

rem Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo [1/4] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "Portable" rmdir /s /q Portable

echo.
echo [2/4] Building portable executable...
echo This may take 2-5 minutes...
echo.

pyinstaller --onefile ^
    --noconsole ^
    --name="IDM_Video_Downloader" ^
    --hidden-import=yt_dlp ^
    --hidden-import=yt_dlp.extractor ^
    --hidden-import=yt_dlp.downloader ^
    --hidden-import=yt_dlp.postprocessor ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=certifi ^
    --hidden-import=websockets ^
    --hidden-import=mutagen ^
    --hidden-import=pycryptodomex ^
    --hidden-import=brotli ^
    --clean ^
    video_downloader.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo [3/4] Creating portable package...

rem Create portable package folder
if not exist "Portable" mkdir Portable
copy "dist\IDM_Video_Downloader.exe" "Portable\" >nul
copy "README.md" "Portable\README_FULL.md" >nul 2>nul
copy "install_ffmpeg.bat" "Portable\" >nul 2>nul

rem Create a README for the portable version
(
echo ================================================================
echo   IDM Video Downloader - Portable Windows Edition
echo ================================================================
echo.
echo Version: 1.0.0
echo License: Valid until December 31, 2025
echo Build Date: %DATE% %TIME%
echo.
echo ================================================================
echo   QUICK START
echo ================================================================
echo.
echo 1. Double-click: IDM_Video_Downloader.exe
echo 2. Paste a YouTube video URL
echo 3. Click "Fetch Info" to load video details
echo 4. Choose download type:
echo    - Video: Select quality (4K, 1080p, 720p, etc.^)
echo    - Audio: Select quality (320/192/128/96 kbps^)
echo 5. Select download location
echo 6. Click "Download"
echo.
echo ================================================================
echo   FEATURES
echo ================================================================
echo.
echo VIDEO DOWNLOADS:
echo   - Multiple qualities: 144p to 4K
echo   - Formats: MP4, WebM, and more
echo   - Real-time progress tracking
echo   - Works without FFmpeg
echo.
echo AUDIO DOWNLOADS:
echo   - With FFmpeg: MP3 format (320/192/128/96 kbps^)
echo   - Without FFmpeg: Original format (webm/m4a^)
echo   - High quality audio extraction
echo.
echo INTERFACE:
echo   - User-friendly GUI
echo   - Separate Video/Audio modes
echo   - Real-time progress bar
echo   - Detailed logging
echo   - Custom download path
echo.
echo ================================================================
echo   FFMPEG (Optional - for MP3 conversion^)
echo ================================================================
echo.
echo To convert audio to MP3, install FFmpeg:
echo.
echo METHOD 1: Use the included script
echo   - Run: install_ffmpeg.bat
echo   - Follow the menu options
echo.
echo METHOD 2: Chocolatey
echo   choco install ffmpeg
echo.
echo METHOD 3: Winget
echo   winget install ffmpeg
echo.
echo METHOD 4: Manual
echo   1. Download: https://ffmpeg.org/download.html
echo   2. Extract to C:\ffmpeg
echo   3. Add C:\ffmpeg\bin to system PATH
echo   4. Restart computer
echo.
echo NOTE: Audio downloads work WITHOUT FFmpeg
echo       (saves in original format like webm/m4a^)
echo.
echo ================================================================
echo   SUPPORTED SITES
echo ================================================================
echo.
echo YouTube and 1000+ other video sites including:
echo   - Vimeo, Dailymotion, Facebook, Instagram
echo   - TikTok, Twitter, Twitch
echo   - And many more...
echo.
echo ================================================================
echo   TROUBLESHOOTING
echo ================================================================
echo.
echo Problem: Can't fetch video info
echo Solution: - Check your internet connection
echo          - URL may contain playlist params (app auto-removes^)
echo          - Try updating yt-dlp (in non-portable version^)
echo.
echo Problem: Audio download fails
echo Solution: - Install FFmpeg for MP3 conversion
echo          - Or download in original format (works without FFmpeg^)
echo.
echo Problem: Download is slow
echo Solution: - Depends on your internet speed
echo          - Server speed varies by site
echo.
echo ================================================================
echo   SYSTEM REQUIREMENTS
echo ================================================================
echo.
echo - Windows 7, 8, 10, or 11
echo - Internet connection
echo - 50MB free disk space (for app^)
echo - FFmpeg (optional, for MP3 conversion^)
echo.
echo ================================================================
echo   LICENSE INFORMATION
echo ================================================================
echo.
echo This is a TRIAL version valid until: December 31, 2025
echo After this date, the application will stop working.
echo.
echo ================================================================
echo   PORTABLE FEATURES
echo ================================================================
echo.
echo - No installation required
echo - Run from any location
echo - Run from USB drive
echo - No registry modifications
echo - Self-contained executable
echo - Copy and share easily
echo.
echo For more details, see README_FULL.md
echo.
echo Enjoy downloading! ^)
echo.
) > "Portable\README.txt"

echo.
echo [4/4] Finalizing...

echo.
echo ================================================================
echo   BUILD SUCCESSFUL!
echo ================================================================
echo.
echo Portable Application: Portable\IDM_Video_Downloader.exe
echo.
echo File Information:
for %%A in ("Portable\IDM_Video_Downloader.exe") do (
    echo   Name: %%~nxA
    echo   Size: %%~zA bytes
    set /a sizeMB=%%~zA/1048576
)
echo   Size: ~%sizeMB% MB
echo.
echo Package Contents:
echo   - IDM_Video_Downloader.exe  [Main Application]
echo   - README.txt                [Quick Start Guide]
echo   - README_FULL.md            [Complete Documentation]
echo   - install_ffmpeg.bat        [FFmpeg Installer Helper]
echo.
echo ================================================================
echo   USAGE
echo ================================================================
echo.
echo Option 1: Run from current location
echo   ^> Portable\IDM_Video_Downloader.exe
echo.
echo Option 2: Copy to another location
echo   ^> Copy the entire 'Portable' folder anywhere
echo   ^> Run IDM_Video_Downloader.exe
echo.
echo Option 3: USB/External Drive
echo   ^> Copy 'Portable' folder to USB drive
echo   ^> Plug into any Windows PC and run
echo.
echo ================================================================
echo.
echo License expires: December 31, 2025
echo.
echo Press any key to open the Portable folder...

pause

rem Open the portable folder
start "" "Portable"
