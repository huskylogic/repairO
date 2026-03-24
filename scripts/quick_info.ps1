# Repair-O - Quick Info Snapshot
# Grabs essential machine info fast — no slow WMI queries

$line = "=" * 55
$ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Output $line
Write-Output "  REPAIR-O  Quick Info Snapshot"
Write-Output "  Generated: $ts"
Write-Output $line

# --- Machine Identity ---
$cs   = Get-CimInstance Win32_ComputerSystem
$os   = Get-CimInstance Win32_OperatingSystem
$bios = Get-CimInstance Win32_BIOS

Write-Output ""
Write-Output "[ MACHINE ]"
Write-Output "  PC Name      : $($cs.Name)"
Write-Output "  Manufacturer : $($cs.Manufacturer)"
Write-Output "  Model        : $($cs.Model)"
Write-Output "  Serial No.   : $($bios.SerialNumber)"
Write-Output "  Domain/WG    : $(if($cs.PartOfDomain){ $cs.Domain } else { $cs.Workgroup })"

# --- OS ---
Write-Output ""
Write-Output "[ OPERATING SYSTEM ]"
Write-Output "  OS           : $($os.Caption)"
Write-Output "  Version      : $($os.Version)"
Write-Output "  Build        : $($os.BuildNumber)"
Write-Output "  Architecture : $($os.OSArchitecture)"
Write-Output "  Last Boot    : $($os.LastBootUpTime.ToString('yyyy-MM-dd HH:mm'))"
Write-Output "  Registered   : $($os.RegisteredUser)"

# --- Current User ---
Write-Output ""
Write-Output "[ CURRENT USER ]"
Write-Output "  User         : $env:USERNAME"
Write-Output "  User Domain  : $env:USERDOMAIN"
Write-Output "  Profile Path : $env:USERPROFILE"

# --- Network (fast — just ipconfig basics) ---
Write-Output ""
Write-Output "[ NETWORK ]"
$adapters = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notmatch "^127\." -and $_.IPAddress -notmatch "^169\." }
foreach ($a in $adapters) {
    Write-Output "  $($a.InterfaceAlias.PadRight(20)) $($a.IPAddress)"
}
try {
    $dns = (Get-DnsClientServerAddress -AddressFamily IPv4 -ErrorAction Stop |
        Where-Object { $_.ServerAddresses.Count -gt 0 } | Select-Object -First 1).ServerAddresses -join ", "
    Write-Output "  DNS Servers  : $dns"
} catch {}
try {
    $gw = (Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction Stop | Select-Object -First 1).NextHop
    Write-Output "  Default GW   : $gw"
} catch {}

# --- RAM ---
Write-Output ""
Write-Output "[ MEMORY ]"
$ramGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
$freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
Write-Output "  Total RAM    : $ramGB GB"
Write-Output "  Free RAM     : $freeGB GB"

# --- Drives (fast) ---
Write-Output ""
Write-Output "[ DRIVES ]"
Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 } | ForEach-Object {
    $size = [math]::Round($_.Size/1GB,1)
    $free = [math]::Round($_.FreeSpace/1GB,1)
    $pct  = if($_.Size -gt 0){ [math]::Round((($_.Size-$_.FreeSpace)/$_.Size)*100,0) } else { 0 }
    Write-Output ("  {0}  {1} GB total  {2} GB free  ({3}% used)" -f $_.DeviceID.PadRight(4), $size, $free, $pct)
}

Write-Output ""
Write-Output $line
Write-Output "  End of Snapshot"
Write-Output $line
