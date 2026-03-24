# Repair-O - Scan for Leftovers after Uninstall
param(
    [string]$ProgramName = "",
    [string]$Publisher = ""
)

$ErrorActionPreference = "SilentlyContinue"
$found = @()

Write-Output "[Repair-O] Scanning for leftovers: $ProgramName"
Write-Output "----------------------------------------------------"

# Build search terms
$terms = @($ProgramName)
if ($Publisher -and $Publisher.Trim() -ne "") { $terms += $Publisher.Trim() }
# Add first word of program name as extra search term
$firstWord = ($ProgramName -split ' ')[0]
if ($firstWord.Length -gt 3) { $terms += $firstWord }

function Search-Path($basePath, $label) {
    foreach ($term in $terms) {
        if (-not (Test-Path $basePath)) { continue }
        Get-ChildItem $basePath -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "*$term*" } |
        ForEach-Object {
            $size = if ($_.PSIsContainer) {
                try { [math]::Round((Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue |
                      Measure-Object Length -Sum).Sum / 1MB, 1) } catch { 0 }
            } else { [math]::Round($_.Length / 1KB, 0) }
            Write-Output "  [$label] $($_.FullName)  ($size $(if($_.PSIsContainer){'MB'}else{'KB'}))"
            $script:found += $_.FullName
        }
    }
}

# File system locations
Write-Output "[Repair-O] Checking file system..."
Search-Path "C:\Program Files" "FILES"
Search-Path "C:\Program Files (x86)" "FILES"
Search-Path "$env:APPDATA" "APPDATA"
Search-Path "$env:LOCALAPPDATA" "LOCALAPPDATA"
Search-Path "$env:PROGRAMDATA" "PROGRAMDATA"
Search-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs" "STARTMENU"

# Registry locations
Write-Output "[Repair-O] Checking registry..."
$regBases = @(
    "HKLM:\Software",
    "HKLM:\Software\WOW6432Node",
    "HKCU:\Software"
)
foreach ($base in $regBases) {
    foreach ($term in $terms) {
        Get-ChildItem $base -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "*$term*" } |
        ForEach-Object {
            Write-Output "  [REGISTRY] $($_.Name)"
            $found += $_.Name
        }
    }
}

Write-Output "----------------------------------------------------"
if ($found.Count -eq 0) {
    Write-Output "[OK] No leftovers found. Clean uninstall!"
} else {
    Write-Output "[FOUND] $($found.Count) leftover item(s) found."
    Write-Output "[INFO] Review the items above and remove manually if desired."
    Write-Output "[TIP] Use 'Force Uninstall' to automatically clean these up."
}
