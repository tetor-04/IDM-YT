@echo off
echo Building Windows 7 Compatible Portable Application...
echo.

rem Install PyInstaller if needed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller==5.13.2
)

rem Clean previous builds
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist  
if exist "Portable_Win7" rmdir /s /q Portable_Win7

echo.
echo Building executable (this may take 3-5 minutes)...
echo.

pyinstaller --clean --onefile --noconsole ^
    --name="IDM_Video_Downloader_Win7" ^
    --add-data="plugins;plugins" ^
    --hidden-import=yt_dlp ^
    --hidden-import=yt_dlp.extractor ^
    --hidden-import=requests ^
    --hidden-import=PIL ^
    --hidden-import=pyperclip ^
    --collect-all=yt_dlp ^
    --noupx ^
    video_downloader.py

if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo.
echo Creating portable package...

mkdir Portable_Win7
mkdir Portable_Win7\ffmpeg\bin
copy "dist\IDM_Video_Downloader_Win7.exe" "Portable_Win7\" >nul
copy "README.md" "Portable_Win7\" >nul 2>nul

echo.
echo Build successful!
echo Output: Portable_Win7\IDM_Video_Downloader_Win7.exe
echo.
