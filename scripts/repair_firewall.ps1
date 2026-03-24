# Repair-O - Repair Windows Firewall
Write-Output "[Repair-O] Resetting Windows Firewall to defaults..."
netsh advfirewall reset
Start-Service mpssvc -ErrorAction SilentlyContinue
Write-Output "[OK] Firewall reset to default policy."
