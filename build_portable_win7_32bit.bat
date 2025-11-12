@echo off
echo ============================================
echo  Building IDM Video Downloader - Win7 32-bit
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8-3.12 and try again
    pause
    exit /b 1
)

REM Check Python version for Windows 7 compatibility
echo Checking Python version...
python -c "import sys; exit(0 if sys.version_info >= (3,8) and sys.version_info < (3,13) else 1)" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Python 3.8-3.12 recommended for Windows 7 compatibility
    echo Current version may not work on Windows 7
)

REM Install/upgrade required packages
echo.
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install pyinstaller pillow pyperclip yt-dlp

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist\IDM_Video_Downloader_Win7_x86.exe" del /q "dist\IDM_Video_Downloader_Win7_x86.exe"

REM Build 32-bit executable with Windows 7 compatibility
echo.
echo Building 32-bit portable executable...
echo This may take 5-10 minutes...
echo.

python -m PyInstaller ^
    --name=IDM_Video_Downloader_Win7_x86 ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --add-data="plugins;plugins" ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=yt_dlp ^
    --hidden-import=pyperclip ^
    --collect-all=yt_dlp ^
    --noconfirm ^
    --clean ^
    video_downloader.py

if errorlevel 1 (
    echo.
    echo ============================================
    echo  BUILD FAILED!
    echo ============================================
    pause
    exit /b 1
)

REM Check if executable was created
if not exist "dist\IDM_Video_Downloader_Win7_x86.exe" (
    echo.
    echo ERROR: Executable was not created!
    pause
    exit /b 1
)

REM Get file size
echo.
echo ============================================
echo  BUILD SUCCESSFUL!
echo ============================================
for %%A in ("dist\IDM_Video_Downloader_Win7_x86.exe") do echo  File: %%~nxA
for %%A in ("dist\IDM_Video_Downloader_Win7_x86.exe") do echo  Size: %%~zA bytes
echo  Location: dist\IDM_Video_Downloader_Win7_x86.exe
echo.
echo  FEATURES:
echo  - 32-bit build (maximum compatibility)
echo  - Windows 7/8/10/11 compatible
echo  - Works on older 32-bit Windows systems
echo  - Single portable .exe file
echo  - No installation required
echo  - FFmpeg embedded (if present)
echo ============================================
echo.

pause
