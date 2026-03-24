# Repair-O - Reset OneDrive
Write-Output "[Repair-O] Resetting OneDrive..."
$onedriveExe = "$env:LOCALAPPDATA\Microsoft\OneDrive\onedrive.exe"
if (Test-Path $onedriveExe) {
    & $onedriveExe /reset
    Write-Output "[OK] OneDrive reset command sent. It will restart automatically."
} else {
    Write-Output "[WARN] OneDrive executable not found at expected path."
    Write-Output "  Try: %LOCALAPPDATA%\Microsoft\OneDrive\onedrive.exe /reset"
}
