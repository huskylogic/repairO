# Repair-O - Apply DHCP to All Network Adapters
Write-Output "[Repair-O] Setting all active network adapters to DHCP..."
$nics = Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled }
$count = 0
foreach ($nic in $nics) {
    Write-Output "  Processing: $($nic.Description)"
    try {
        $nic.EnableDHCP() | Out-Null
        $nic.SetDNSServerSearchOrder() | Out-Null
        Write-Output "  [OK] DHCP enabled, static DNS cleared."
        $count++
    } catch {
        Write-Output "  [WARN] Could not modify: $_"
    }
}
# Release and renew to get fresh addresses
Write-Output ""
Write-Output "[Repair-O] Releasing and renewing IP leases..."
ipconfig /release 2>&1 | Out-Null
ipconfig /renew  2>&1 | Out-Null
ipconfig /flushdns 2>&1 | Out-Null
Write-Output "[OK] DHCP applied to $count adapter(s). IP renewed."
Write-Output ""
ipconfig | Where-Object { $_ -match "IPv4|Default Gateway|Description" }
