# Repair-O - Reset Winsock
Write-Output "[Repair-O] Resetting Winsock catalog..."
netsh winsock reset
Write-Output "[OK] Winsock reset. REBOOT required for changes to take effect."
