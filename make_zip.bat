@echo off
title RepairO - Create Portable ZIP
color 0B

echo.
echo  Creating portable ZIP for distribution...
echo.

if not exist "dist\RepairO\RepairO.exe" (
    echo  [ERROR] Build not found. Run build.bat first.
    pause & exit /b 1
)

:: Get today's date for filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set dt=%%I
set DATESTAMP=%dt:~0,8%

set ZIPNAME=RepairO_v1.0_Portable_%DATESTAMP%.zip

echo  Zipping dist\RepairO\ to %ZIPNAME% ...

:: Use PowerShell to zip (built into Windows 10+)
powershell -Command "Compress-Archive -Path 'dist\RepairO\*' -DestinationPath '%ZIPNAME%' -Force"

if exist "%ZIPNAME%" (
    for %%A in ("%ZIPNAME%") do set ZIPSIZE=%%~zA
    set /a ZIPMB=%ZIPSIZE% / 1048576
    echo.
    echo  [OK] Created: %ZIPNAME%
    echo       Size: ~%ZIPMB% MB
    echo.
    echo  To use: Extract the ZIP anywhere, run RepairO.exe
    echo          No installation needed.
) else (
    echo  [ERROR] ZIP creation failed.
)

pause
