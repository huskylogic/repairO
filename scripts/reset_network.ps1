# Repair-O - Full Network Reset
Write-Output "[Repair-O] Performing full network stack reset..."
ipconfig /flushdns
Write-Output "  [OK] DNS cache flushed."
netsh winsock reset
Write-Output "  [OK] Winsock reset."
netsh int ip reset
Write-Output "  [OK] TCP/IP stack reset."
netsh int ipv4 reset
netsh int ipv6 reset
Write-Output "  [OK] IPv4/IPv6 reset."
netsh advfirewall reset
Write-Output "  [OK] Firewall reset."
arp -d *
Write-Output "  [OK] ARP cache cleared."
ipconfig /release 2>&1 | Out-Null
ipconfig /renew 2>&1 | Out-Null
Write-Output "  [OK] IP released and renewed."
Write-Output "[OK] Full network reset complete. A REBOOT is recommended."
