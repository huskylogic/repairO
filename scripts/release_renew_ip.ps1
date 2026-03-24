# Repair-O - Release/Renew IP
Write-Output "[Repair-O] Releasing and renewing IP address..."
ipconfig /release
Write-Output "  [OK] IP released."
ipconfig /renew
Write-Output "  [OK] IP renewed."
ipconfig /all
Write-Output "[OK] Done."
