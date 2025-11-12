@echo off
title IDM Video Downloader Launcher
color 0A
echo.
echo  ██╗██████╗ ███╗   ███╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗ 
echo  ██║██╔══██╗████╗ ████║    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗
echo  ██║██║  ██║██╔████╔██║    ██║   ██║██║██║  ██║█████╗  ██║   ██║
echo  ██║██║  ██║██║╚██╔╝██║    ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║
echo  ██║██████╔╝██║ ╚═╝ ██║     ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝
echo  ╚═╝╚═════╝ ╚═╝     ╚═╝      ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝ 
echo.
echo                    DOWNLOADER v1.0
echo.
echo ================================================================
echo.

:menu
echo Select an option:
echo.
echo [1] Run GUI Application (Recommended)
echo [2] Run CLI Application  
echo [3] Test System
echo [4] Install/Update Dependencies
echo [5] Open Download Folder
echo [6] Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto gui
if "%choice%"=="2" goto cli
if "%choice%"=="3" goto test
if "%choice%"=="4" goto install
if "%choice%"=="5" goto folder
if "%choice%"=="6" goto exit
goto menu

:gui
echo.
echo Starting GUI Application...
python video_downloader.py
goto menu

:cli
echo.
echo Starting CLI Application...
echo Enter video URL or type 'back' to return to menu:
set /p url="URL: "
if "%url%"=="back" goto menu
if "%url%"=="" goto cli
python cli_downloader.py "%url%" list
echo.
echo Enter format ID (or press Enter for 'best'):
set /p format="Format: "
if "%format%"=="" set format=best
python cli_downloader.py "%url%" "%format%"
goto menu

:test
echo.
echo Running System Test...
python test_system.py
echo.
pause
goto menu

:install
echo.
echo Installing/Updating Dependencies...
pip install --upgrade yt-dlp requests pillow
echo.
echo Dependencies updated!
pause
goto menu

:folder
echo.
echo Opening Downloads folder...
start "" "%USERPROFILE%\Downloads"
goto menu

:exit
echo.
echo Thank you for using IDM Video Downloader!
timeout /t 2 /nobreak > nul
exit