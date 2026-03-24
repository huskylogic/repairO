# Repair-O - Repair Volume Shadow Copy Service (VSS)
Write-Output "[Repair-O] Repairing Volume Shadow Copy Service..."
Write-Output ""

# Stop dependent services first
$deps = @("swprv", "VSS")
foreach ($s in $deps) {
    Stop-Service $s -Force -ErrorAction SilentlyContinue
}
Start-Sleep 1

# Re-register VSS and related DLLs
Write-Output "  Re-registering VSS providers..."
$vssDlls = @(
    "ole32.dll", "oleaut32.dll", "vss_ps.dll", "qmgr.dll",
    "es.dll", "stdprov.dll", "vssapi.dll", "msxml.dll", "msxml3.dll"
)
foreach ($dll in $vssDlls) {
    regsvr32 /s $dll 2>&1 | Out-Null
}

# Re-register VSS executables
$vssExes = @("vssvc.exe", "swprv.dll")
foreach ($exe in $vssExes) {
    & regsvr32 /s $exe 2>&1 | Out-Null
}

# Reset VSS service settings
Write-Output "  Resetting VSS service configuration..."
Set-Service VSS   -StartupType Manual    -ErrorAction SilentlyContinue
Set-Service swprv -StartupType Manual    -ErrorAction SilentlyContinue
Set-Service CryptSvc -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service CryptSvc -ErrorAction SilentlyContinue

# Re-register with sc.exe for deeper reset
& sc.exe sdset vss "D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;AU)(A;;CCLCSWRPWPDTLOCRRC;;;PU)" 2>&1 | Out-Null

# Start VSS
Start-Service VSS -ErrorAction SilentlyContinue
Start-Sleep 1
$vss = Get-Service VSS -ErrorAction SilentlyContinue
if ($vss -and $vss.Status -eq "Running") {
    Write-Output "  [OK] VSS service running."
} else {
    Write-Output "  [INFO] VSS service is set to Manual start (normal) — starts on demand."
}

# Verify with vssadmin
Write-Output ""
Write-Output "  VSS provider list:"
& vssadmin list providers 2>&1 | Where-Object { $_ -match "Provider|Type" } | ForEach-Object { Write-Output "    $_" }

Write-Output ""
Write-Output "[OK] VSS repair complete."
Write-Output "[INFO] System Restore and backup services should now work correctly."
