# Repair-O - Windows Defender Full Scan
Write-Output "[Repair-O] Starting Windows Defender Full Scan..."
Write-Output "  [INFO] Full scans can take 1-4 hours depending on drive size."
try {
    Start-MpScan -ScanType FullScan -ErrorAction Stop
    Write-Output "[OK] Full scan initiated. Monitor Windows Security for results."
} catch {
    Write-Output "[ERROR] Could not start Defender scan: $_"
    exit 1
}
