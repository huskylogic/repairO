@echo off
title RepairO Setup
color 0B

echo.
echo  =============================================
echo   RepairO - Professional PC Repair Toolkit
echo   Setup / Launcher
echo  =============================================
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Please install Python 3.9+ from python.org
    echo          Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo  [OK] Python found.

:: Check for pip and install deps
echo  [..] Installing/verifying dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo  [OK] Dependencies ready.

echo.
echo  Launching RepairO...
echo.

:: Run as admin for full system access
net session >nul 2>&1
if errorlevel 1 (
    echo  [WARN] Not running as Administrator.
    echo         Some features may be limited. Right-click and run as Admin for full access.
    echo.
)

python main.py
pause
