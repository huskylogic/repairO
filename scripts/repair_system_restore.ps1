# Repair-O - Repair System Restore
Write-Output "[Repair-O] Repairing System Restore..."
Set-Service -Name "VSS" -StartupType Manual -ErrorAction SilentlyContinue
Set-Service -Name "swprv" -StartupType Manual -ErrorAction SilentlyContinue
Start-Service -Name "VSS" -ErrorAction SilentlyContinue
Enable-ComputerRestore -Drive "C:\" -ErrorAction SilentlyContinue
Write-Output "[OK] System Restore repair complete."
