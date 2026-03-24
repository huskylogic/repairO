@echo off
title Repair-O - Build Tool
color 0B
cls

echo.
echo  =====================================================
echo   RepairO Build Tool
echo   Packages RepairO into a portable .exe folder
echo  =====================================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo          Install Python 3.9+ from python.org
    echo          Check "Add Python to PATH" during install.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do set PYVER=%%v
echo  [OK] %PYVER%

:: ── Install/Update dependencies ───────────────────────────────────────────────
echo  [..] Installing build dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install pyinstaller pyqt5 pillow --quiet --upgrade
if errorlevel 1 ( echo  [ERROR] pip install failed. & pause & exit /b 1 )
echo  [OK] Dependencies ready.

:: ── Clean previous build ──────────────────────────────────────────────────────
echo  [..] Cleaning previous build...
if exist build    rmdir /s /q build
if exist dist     rmdir /s /q dist
echo  [OK] Clean.

:: ── Try to get UPX for smaller output ─────────────────────────────────────────
echo  [..] Checking for UPX compressor...
upx --version >nul 2>&1
if errorlevel 1 (
    echo  [INFO] UPX not found - build will work fine but may be slightly larger.
    echo         Download UPX from https://upx.github.io/ and add to PATH for smaller output.
) else (
    echo  [OK] UPX found - output will be compressed.
)

:: ── Build ─────────────────────────────────────────────────────────────────────
echo.
echo  [..] Building RepairO.exe...
echo       This takes 60-120 seconds, please wait...
echo.

python -m PyInstaller RepairO.spec --noconfirm

if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed. Check output above for details.
    pause & exit /b 1
)

:: ── Verify output ─────────────────────────────────────────────────────────────
if not exist "dist\RepairO\RepairO.exe" (
    echo  [ERROR] RepairO.exe not found in dist\RepairO\
    pause & exit /b 1
)

:: ── Add placeholder tools and logs folders to dist ────────────────────────────
if not exist "dist\RepairO\tools" mkdir "dist\RepairO\tools"
if not exist "dist\RepairO\logs"  mkdir "dist\RepairO\logs"

:: ── Copy README into dist ─────────────────────────────────────────────────────
copy README.md "dist\RepairO\README.md" >nul 2>&1

:: ── Get file size ─────────────────────────────────────────────────────────────
for %%A in ("dist\RepairO\RepairO.exe") do set EXESIZE=%%~zA
set /a EXEMB=%EXESIZE% / 1048576

echo.
echo  =====================================================
echo   BUILD COMPLETE!
echo  =====================================================
echo.
echo   Output:  dist\RepairO\RepairO.exe
echo   Size:    ~%EXEMB% MB
echo.
echo   PORTABLE USE:
echo   Copy the entire dist\RepairO\ folder to a USB drive.
echo   Run RepairO.exe from the USB - no installation needed.
echo   Tools will download into the RepairO\tools\ folder
echo   on the USB drive, so they travel with the toolkit.
echo.
echo   TO UPDATE LATER:
echo   1. Edit main.py or any .ps1 script
echo   2. Run build.bat again
echo   3. New exe replaces the old one in dist\RepairO\
echo.

:: ── Offer to open output folder ───────────────────────────────────────────────
set /p OPEN="Open the output folder now? (y/n): "
if /i "%OPEN%"=="y" explorer dist\RepairO

pause
