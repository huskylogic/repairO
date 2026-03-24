# Repair-O - Registry Hive Backup
$backupDir = "$env:USERPROFILE\Desktop\RepairO_RegBackup_$(Get-Date -Format 'yyyyMMdd_HHmm')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Output "[Repair-O] Backing up registry hives to: $backupDir"
$hives = @{
    "HKLM_SOFTWARE" = "HKLM\SOFTWARE"
    "HKLM_SYSTEM"   = "HKLM\SYSTEM"
    "HKLM_SAM"      = "HKLM\SAM"
    "HKCU"          = "HKCU"
    "HKLM_SECURITY" = "HKLM\SECURITY"
}
foreach ($name in $hives.Keys) {
    $hive = $hives[$name]
    $dest = "$backupDir\$name.reg"
    Write-Output "  Exporting $hive ..."
    reg export $hive $dest /y 2>&1 | Out-Null
    if (Test-Path $dest) { Write-Output "  [OK] $name backed up" }
    else { Write-Output "  [WARN] $name may have failed (some hives require SYSTEM)" }
}
Write-Output "[OK] Registry backup complete: $backupDir"
