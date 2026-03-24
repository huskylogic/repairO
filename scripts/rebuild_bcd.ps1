# Repair-O - Rebuild BCD
Write-Output "[Repair-O] Rebuilding Boot Configuration Data..."
Write-Output "  [WARN] This is for boot repair only. Run from WinPE/Recovery if system won't boot."
Write-Output ""

# Detect UEFI vs BIOS — fixboot only works reliably on BIOS/Legacy systems
$isUEFI = $false
try {
    $env:firmware_type | Out-Null
    if ($env:firmware_type -eq "UEFI") { $isUEFI = $true }
} catch {}
# Fallback detection via bcdedit
if (-not $isUEFI) {
    $bcdOutput = bcdedit /enum firmware 2>&1
    if ($bcdOutput -match "Windows Boot Manager") { $isUEFI = $true }
}

bootrec /scanos
bootrec /rebuildbcd
bootrec /fixmbr

if ($isUEFI) {
    Write-Output ""
    Write-Output "[INFO] UEFI system detected — skipping 'bootrec /fixboot'."
    Write-Output "[INFO] On UEFI, /fixboot requires mounting the EFI partition first."
    Write-Output "[TIP]  If boot is still broken, run from Recovery: 'bcdboot C:\Windows /s X: /f UEFI'"
} else {
    bootrec /fixboot
    Write-Output ""
    Write-Output "[OK] MBR and boot sector repaired."
}

Write-Output ""
Write-Output "[OK] BCD rebuild complete. REBOOT to verify."
