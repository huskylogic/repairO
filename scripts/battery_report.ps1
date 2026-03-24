# Repair-O - Battery Report
$out = "$env:USERPROFILE\Desktop\BatteryReport.html"
Write-Output "[Repair-O] Generating battery report..."
powercfg /batteryreport /output "$out" 2>&1
if (Test-Path $out) {
    Write-Output "[OK] Battery report saved to: $out"
    Write-Output "[INFO] Opening report in browser..."
    Start-Process $out
} else {
    Write-Output "[WARN] No battery detected or report could not be generated."
    Write-Output "[INFO] This PC may not have a battery."
}
