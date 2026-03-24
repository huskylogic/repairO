# Repair-O - Windows Defender Quick Scan
Write-Output "[Repair-O] Starting Windows Defender Quick Scan..."
try {
    Start-MpScan -ScanType QuickScan -ErrorAction Stop
    Write-Output "[OK] Quick scan initiated. Monitor Windows Security for results."
} catch {
    Write-Output "[ERROR] Could not start Defender scan: $_"
    Write-Output "  Ensure Windows Defender is enabled and not overridden by third-party AV."
    exit 1
}
