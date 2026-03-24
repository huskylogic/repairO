# Repair-O - Add Defender exclusion for NirSoft tools folder
param([string]$ToolsDir = "")

$ErrorActionPreference = "Continue"

if (-not $ToolsDir) {
    Write-Output "[ERROR] No tools directory specified."
    exit 1
}

Write-Output "[Repair-O] Adding Windows Defender exclusion for:"
Write-Output "[Repair-O] $ToolsDir"
Write-Output "----------------------------------------------------"

try {
    # Check if running as admin
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Output "[ERROR] Must run as Administrator to modify Defender exclusions."
        Write-Output "[TIP] Right-click Repair-O and choose 'Run as Administrator'."
        exit 1
    }

    # Add folder exclusion
    Add-MpPreference -ExclusionPath $ToolsDir -ErrorAction Stop
    Write-Output "[OK] Exclusion added for: $ToolsDir"
    Write-Output "[OK] Windows Defender will no longer scan or delete files in this folder."
    Write-Output "[INFO] This exclusion persists until you remove it manually in Defender settings."
    Write-Output "[INFO] Only Repair-O's own tools folder is excluded — your system remains protected."

} catch {
    Write-Output "[ERROR] Failed to add exclusion: $_"
    Write-Output "[TIP] Make sure Repair-O is running as Administrator."
    exit 1
}
