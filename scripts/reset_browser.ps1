# Repair-O - Reset Browser
param([string]$Browser = "all")
$ErrorActionPreference = "SilentlyContinue"

function Reset-Chrome {
    Write-Output "[Repair-O] Resetting Google Chrome..."
    $path = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
    if (Test-Path $path) {
        Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue
        Start-Sleep 1
        Remove-Item "$path\Preferences" -Force -ErrorAction SilentlyContinue
        Remove-Item "$path\Secure Preferences" -Force -ErrorAction SilentlyContinue
        Write-Output "[OK] Chrome reset complete."
    } else { Write-Output "[WARN] Chrome profile not found." }
}

function Reset-Firefox {
    Write-Output "[Repair-O] Resetting Firefox..."
    $path = "$env:APPDATA\Mozilla\Firefox\Profiles"
    if (Test-Path $path) {
        Stop-Process -Name "firefox" -Force -ErrorAction SilentlyContinue
        Start-Sleep 1
        Get-ChildItem $path -Directory | ForEach {
            Remove-Item "$($_.FullName)\prefs.js" -Force -ErrorAction SilentlyContinue
        }
        Write-Output "[OK] Firefox reset complete."
    } else { Write-Output "[WARN] Firefox profile not found." }
}

function Reset-Edge {
    Write-Output "[Repair-O] Resetting Microsoft Edge..."
    $path = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default"
    if (Test-Path $path) {
        Stop-Process -Name "msedge" -Force -ErrorAction SilentlyContinue
        Start-Sleep 1
        Remove-Item "$path\Preferences" -Force -ErrorAction SilentlyContinue
        Remove-Item "$path\Secure Preferences" -Force -ErrorAction SilentlyContinue
        Write-Output "[OK] Edge reset complete."
    } else { Write-Output "[WARN] Edge profile not found." }
}

switch ($Browser.ToLower()) {
    "chrome"  { Reset-Chrome }
    "firefox" { Reset-Firefox }
    "edge"    { Reset-Edge }
    "all"     { Reset-Chrome; Reset-Firefox; Reset-Edge }
}
