# Repair-O - Activate Windows with BIOS OEM Key
Write-Output "[Repair-O] Checking for BIOS embedded OEM product key..."
$key = (Get-WmiObject -Query "SELECT OA3xOriginalProductKey FROM SoftwareLicensingService").OA3xOriginalProductKey
if ($key) {
    Write-Output "[OK] BIOS OEM key found: $key"
    Write-Output "[Repair-O] Attempting activation..."
    $sls = Get-WmiObject -Query "SELECT * FROM SoftwareLicensingService"
    $sls.InstallProductKey($key) | Out-Null
    $sls.RefreshLicenseStatus() | Out-Null
    $status = (Get-CimInstance SoftwareLicensingProduct | Where {$_.PartialProductKey -and $_.Name -match "Windows"} | Select -First 1).LicenseStatus
    if ($status -eq 1) {
        Write-Output "[OK] Windows activated successfully!"
    } else {
        Write-Output "[WARN] Key installed but activation status unclear. Try running: slmgr /ato"
    }
} else {
    Write-Output "[WARN] No BIOS OEM key found on this machine."
    Write-Output "[INFO] This PC may not have an embedded license key."
}
