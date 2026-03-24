# Repair-O - Apply Static DNS to All Network Adapters
param(
    [string]$Primary   = "8.8.8.8",
    [string]$Secondary = "8.8.4.4"
)
Write-Output "[Repair-O] Applying DNS servers to all active adapters..."
Write-Output "  Primary:   $Primary"
Write-Output "  Secondary: $Secondary"
Write-Output ""
$nics  = Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled }
$count = 0
foreach ($nic in $nics) {
    Write-Output "  Processing: $($nic.Description)"
    try {
        $dns = @($Primary)
        if ($Secondary) { $dns += $Secondary }
        $nic.SetDNSServerSearchOrder($dns) | Out-Null
        Write-Output "  [OK] DNS set."
        $count++
    } catch {
        Write-Output "  [WARN] Could not set DNS: $_"
    }
}
ipconfig /flushdns 2>&1 | Out-Null
Write-Output ""
Write-Output "[OK] DNS applied to $count adapter(s). Cache flushed."
