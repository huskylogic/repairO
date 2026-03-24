# Repair-O - Repair Security Center
Write-Output "[Repair-O] Repairing Windows Security Center..."
Stop-Service wscsvc -Force -ErrorAction SilentlyContinue
regsvr32 /s wscui.cpl
Set-Service wscsvc -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service wscsvc -ErrorAction SilentlyContinue
Write-Output "[OK] Security Center service restarted."
