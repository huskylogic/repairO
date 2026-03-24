# Repair-O - Reset TCP/IP Stack
Write-Output "[Repair-O] Resetting TCP/IP stack..."
netsh int ip reset
netsh int ipv4 reset
netsh int ipv6 reset
Write-Output "[OK] TCP/IP reset. REBOOT required."
