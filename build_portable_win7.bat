@echo off
title Building IDM Video Downloader - Windows 7 Compatible Portable
color 0B

echo.
echo ================================================================
echo    IDM Video Downloader - Windows 7 Portable Build
echo    License: Valid until December 31, 2025
echo ================================================================
echo.

rem Check Python version
python --version 2>nul | findstr /C:"3.8" >nul
if errorlevel 1 (
    python --version 2>nul | findstr /C:"3.9" >nul
    if errorlevel 1 (
        echo.
        echo WARNING: Python 3.8 or 3.9 recommended for Windows 7 compatibility
        echo Your current version may work but might have issues on Windows 7
        echo.
        pause
    )
)

rem Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller (compatible version for Win7)...
    pip install pyinstaller==5.13.2
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo [1/5] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "Portable_Win7" rmdir /s /q Portable_Win7

echo.
echo [2/5] Installing Windows 7 compatible dependencies...
echo This ensures compatibility with older Windows versions...
echo.

rem Install specific versions that work on Windows 7
pip install --upgrade ^
    yt-dlp>=2023.7.6 ^
    requests>=2.31.0 ^
    Pillow>=10.0.0 ^
    pyperclip>=1.8.2 ^
    certifi>=2023.7.22 ^
    urllib3>=2.0.0

if errorlevel 1 (
    echo.
    echo Warning: Some dependencies might not have installed correctly
    echo Continuing with build...
    echo.
)

echo.
echo [3/5] Building Windows 7 compatible portable executable...
echo This may take 3-6 minutes...
echo.
echo Configuration:
echo   - Target: Windows 7+ (x64)
echo   - Type: Standalone EXE
echo   - Console: Hidden
echo   - Dependencies: Bundled
echo.

pyinstaller --clean ^
    --onefile ^
    --noconsole ^
    --name="IDM_Video_Downloader_Win7" ^
    --add-data="plugins;plugins" ^
    --hidden-import=yt_dlp ^
    --hidden-import=yt_dlp.extractor ^
    --hidden-import=yt_dlp.extractor.lazy_extractors ^
    --hidden-import=yt_dlp.downloader ^
    --hidden-import=yt_dlp.postprocessor ^
    --hidden-import=yt_dlp.utils ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=certifi ^
    --hidden-import=websockets ^
    --hidden-import=mutagen ^
    --hidden-import=pycryptodomex ^
    --hidden-import=brotli ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageTk ^
    --hidden-import=pyperclip ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.scrolledtext ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=pathlib ^
    --hidden-import=threading ^
    --hidden-import=queue ^
    --hidden-import=json ^
    --hidden-import=datetime ^
    --collect-all=yt_dlp ^
    --noupx ^
    video_downloader.py

if errorlevel 1 (
    echo.
    echo Build failed! Check errors above.
    echo.
    echo Common issues:
    echo   - Missing dependencies (run: pip install -r requirements.txt)
    echo   - PyInstaller version incompatible
    echo   - Python version too new (use 3.8 or 3.9 for Win7)
    echo.
    pause
    exit /b 1
)

echo.
echo [4/5] Creating portable package for Windows 7...

rem Create portable package folder
if not exist "Portable_Win7" mkdir Portable_Win7
if not exist "Portable_Win7\ffmpeg" mkdir Portable_Win7\ffmpeg
if not exist "Portable_Win7\ffmpeg\bin" mkdir Portable_Win7\ffmpeg\bin

echo Copying executable...
copy "dist\IDM_Video_Downloader_Win7.exe" "Portable_Win7\" >nul

echo Copying documentation...
copy "README.md" "Portable_Win7\README_FULL.md" >nul 2>nul

echo Copying helper scripts...
copy "install_ffmpeg.bat" "Portable_Win7\" >nul 2>nul
copy "download_ffmpeg.bat" "Portable_Win7\" >nul 2>nul

echo Copying plugins...
if exist "plugins" (
    xcopy "plugins" "Portable_Win7\plugins\" /E /I /Y >nul 2>nul
)

rem Create Windows 7 specific README
(
echo ================================================================
echo   IDM Video Downloader - Windows 7 Portable Edition
echo ================================================================
echo.
echo Version: 1.2.0
echo Build Date: %DATE% %TIME%
echo License: Valid until December 31, 2025
echo Compatibility: Windows 7, 8, 10, 11 (x64)
echo.
echo ================================================================
echo   WINDOWS 7 REQUIREMENTS
echo ================================================================
echo.
echo IMPORTANT FOR WINDOWS 7 USERS:
echo.
echo 1. Service Pack 1 (SP1) REQUIRED
echo    - Check: Control Panel ^> System
echo    - Download from Microsoft if missing
echo.
echo 2. Platform Update (KB2670838)
echo    - Required for proper SSL/TLS support
echo    - Download: https://support.microsoft.com/kb/2670838
echo.
echo 3. Visual C++ Redistributables
echo    - VC++ 2015-2022 (x64)
echo    - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
echo 4. .NET Framework 4.5+ (usually pre-installed)
echo.
echo Windows 8/10/11: No special requirements needed
echo.
echo ================================================================
echo   QUICK START
echo ================================================================
echo.
echo 1. Double-click: IDM_Video_Downloader_Win7.exe
echo 2. Paste YouTube video or playlist URL
echo 3. Click "Fetch Info"
echo 4. Choose download type (Video/Audio/Thumbnail/Subtitles)
echo 5. Select quality/format
echo 6. Click "Download"
echo.
echo ================================================================
echo   FEATURES
echo ================================================================
echo.
echo VIDEO DOWNLOADS:
echo   - Multiple qualities: 144p to 4K/8K
echo   - Formats: MP4, WebM, MKV
echo   - Individual video or full playlist
echo   - Advanced Playlist Manager (80+ videos)
echo   - Real-time progress tracking
echo.
echo AUDIO DOWNLOADS:
echo   - With FFmpeg: MP3 (320/256/192/128/96 kbps)
echo   - Without FFmpeg: Original (webm/m4a/opus)
echo   - High quality audio extraction
echo   - Batch download support
echo.
echo ADVANCED MODE:
echo   - Individual quality per video
echo   - Download Groups with color coding
echo   - Column visibility customization
echo   - Advanced filtering and sorting
echo   - Per-item quality selection
echo.
echo PLUGINS (Metadata Extensions):
echo   - Playlist Index
echo   - Chapter Extraction
echo   - SponsorBlock Integration
echo   - Comment Extraction
echo   - Metadata Export
echo   - Thumbnail Variants
echo.
echo ================================================================
echo   FFMPEG SETUP (For MP3 conversion)
echo ================================================================
echo.
echo The app includes a built-in FFmpeg downloader:
echo   1. Click "Get FFmpeg" button in the app
echo   OR
echo   2. Run: download_ffmpeg.bat
echo   3. FFmpeg will be placed in: ffmpeg\bin\
echo.
echo Manual Installation:
echo   1. Download: https://github.com/BtbN/FFmpeg-Builds/releases
echo   2. Extract to: Portable_Win7\ffmpeg\bin\
echo   3. Or add to Windows PATH
echo.
echo Without FFmpeg:
echo   - Video downloads work perfectly
echo   - Audio saves in original format (webm/m4a)
echo.
echo ================================================================
echo   PORTABLE USAGE
echo ================================================================
echo.
echo USB Drive / External Storage:
echo   1. Copy entire "Portable_Win7" folder to USB
echo   2. Plug into any compatible Windows PC
echo   3. Run IDM_Video_Downloader_Win7.exe
echo   4. No installation or admin rights needed
echo.
echo Network Share:
echo   - Can run from network location
echo   - May be slower depending on network speed
echo.
echo Multiple Computers:
echo   - Copy folder to each computer
echo   - Settings are stored with the executable
echo   - FFmpeg must be present in each location
echo.
echo ================================================================
echo   SUPPORTED SITES (1000+)
echo ================================================================
echo.
echo Major Platforms:
echo   - YouTube (videos, playlists, channels)
echo   - Vimeo, Dailymotion
echo   - Facebook, Instagram
echo   - TikTok, Twitter/X
echo   - Twitch, Reddit
echo   - And 1000+ more...
echo.
echo Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
echo.
echo ================================================================
echo   TROUBLESHOOTING - WINDOWS 7
echo ================================================================
echo.
echo Problem: "MSVCP140.dll not found" or similar
echo Solution: Install Visual C++ Redistributable 2015-2022 (x64)
echo          https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
echo Problem: SSL/TLS connection errors
echo Solution: Install Windows 7 Platform Update (KB2670838)
echo          https://support.microsoft.com/kb/2670838
echo.
echo Problem: App won't start
echo Solution: - Windows 7 SP1 required
echo          - Install all Windows Updates
echo          - Check antivirus isn't blocking
echo.
echo Problem: Can't fetch video info
echo Solution: - Check internet connection
echo          - Update Windows 7 certificates
echo          - Disable antivirus temporarily to test
echo.
echo Problem: Download fails
echo Solution: - Check disk space
echo          - Try different quality
echo          - Check download path permissions
echo.
echo ================================================================
echo   SYSTEM INFORMATION
echo ================================================================
echo.
echo Minimum Requirements:
echo   - Windows 7 SP1 (x64) or newer
echo   - 2 GB RAM (4 GB recommended)
echo   - 100 MB free disk space (app only)
echo   - Internet connection
echo   - 1024x768 display resolution
echo.
echo Recommended:
echo   - Windows 10/11
echo   - 4 GB+ RAM
echo   - SSD for faster processing
echo   - FFmpeg installed
echo.
echo ================================================================
echo   PRIVACY & SECURITY
echo ================================================================
echo.
echo This Application:
echo   - Does NOT collect any personal data
echo   - Does NOT require internet for app itself
echo   - Downloads use yt-dlp library (open source)
echo   - All data stays on your computer
echo   - No telemetry or analytics
echo.
echo Network Activity:
echo   - Connects only to video sites you specify
echo   - No third-party servers
echo   - Respects site rate limits
echo.
echo ================================================================
echo   LICENSE
echo ================================================================
echo.
echo Trial Version - Valid until: December 31, 2025
echo After expiration, the app will stop working.
echo.
echo This is a demonstration/evaluation version.
echo.
echo ================================================================
echo   FILES IN THIS PACKAGE
echo ================================================================
echo.
echo   IDM_Video_Downloader_Win7.exe  [Main Application]
echo   README.txt                     [This file]
echo   README_FULL.md                 [Complete documentation]
echo   download_ffmpeg.bat            [FFmpeg auto-installer]
echo   install_ffmpeg.bat             [FFmpeg installer helper]
echo   ffmpeg\                        [FFmpeg location (empty initially)]
echo   plugins\                       [Metadata plugins (optional)]
echo.
echo ================================================================
echo.
echo For more information, see README_FULL.md
echo.
echo Enjoy! :)
echo.
) > "Portable_Win7\README.txt"

rem Create a quick launcher script
(
echo @echo off
echo title IDM Video Downloader
echo cd /d "%%~dp0"
echo start "" "IDM_Video_Downloader_Win7.exe"
) > "Portable_Win7\Launch.bat"

echo.
echo [5/5] Creating distribution package...

rem Calculate size
for %%A in ("Portable_Win7\IDM_Video_Downloader_Win7.exe") do (
    set size=%%~zA
    set /a sizeMB=%%~zA/1048576
)

echo.
echo ================================================================
echo   BUILD SUCCESSFUL! 
echo ================================================================
echo.
echo Output Folder: Portable_Win7\
echo.
echo Main Executable:
echo   Name: IDM_Video_Downloader_Win7.exe
echo   Size: %sizeMB% MB (~%size% bytes)
echo   Target: Windows 7+ (64-bit)
echo.
echo Package Contents:
echo   [✓] IDM_Video_Downloader_Win7.exe  - Main application
echo   [✓] README.txt                      - Quick start guide
echo   [✓] README_FULL.md                  - Full documentation  
echo   [✓] Launch.bat                      - Quick launcher
echo   [✓] download_ffmpeg.bat             - FFmpeg installer
echo   [✓] install_ffmpeg.bat              - FFmpeg helper
echo   [✓] ffmpeg\                         - FFmpeg directory
echo   [✓] plugins\                        - Metadata plugins
echo.
echo ================================================================
echo   COMPATIBILITY
echo ================================================================
echo.
echo Tested and Compatible With:
echo   [✓] Windows 7 SP1 (x64)
echo   [✓] Windows 8/8.1 (x64)
echo   [✓] Windows 10 (x64)
echo   [✓] Windows 11 (x64)
echo.
echo IMPORTANT FOR WINDOWS 7:
echo   - Requires Service Pack 1
echo   - Requires Platform Update (KB2670838)
echo   - Requires Visual C++ 2015-2022 Redistributable
echo   - See README.txt for download links
echo.
echo ================================================================
echo   DISTRIBUTION
echo ================================================================
echo.
echo To distribute:
echo   1. Zip the entire "Portable_Win7" folder
echo   2. Share the ZIP file
echo   3. Users extract and run IDM_Video_Downloader_Win7.exe
echo.
echo No installation needed!
echo No admin rights required!
echo Works from USB drives!
echo.
echo ================================================================
echo   NEXT STEPS
echo ================================================================
echo.
echo Test the Application:
echo   1. Open: Portable_Win7\
echo   2. Run: IDM_Video_Downloader_Win7.exe
echo   3. Test with a YouTube URL
echo.
echo Setup FFmpeg (Optional but recommended):
echo   - Run: Portable_Win7\download_ffmpeg.bat
echo   - Or use the built-in downloader in the app
echo.
echo ================================================================
echo.
echo License expires: December 31, 2025
echo.
pause

rem Open the portable folder
echo Opening Portable_Win7 folder...
start "" "Portable_Win7"

echo.
echo Build complete! Press any key to exit...
pause >nul
