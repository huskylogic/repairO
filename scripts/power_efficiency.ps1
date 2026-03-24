# Repair-O - Power Efficiency Report
$out = "$env:USERPROFILE\Desktop\PowerEfficiency.html"
Write-Output "[Repair-O] Running power efficiency diagnostics (60 sec trace)..."
Write-Output "[INFO] This will take about 60 seconds..."
powercfg /energy /output "$out" /duration 60 2>&1
if (Test-Path $out) {
    Write-Output "[OK] Power efficiency report saved to: $out"
    Write-Output "[INFO] Opening report in browser..."
    Start-Process $out
} else {
    Write-Output "[ERROR] Could not generate power report."
}
