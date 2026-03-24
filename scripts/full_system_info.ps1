# Repair-O - Full System Info for Diagnose tab
$ErrorActionPreference = "SilentlyContinue"
$os     = Get-CimInstance Win32_OperatingSystem
$cs     = Get-CimInstance Win32_ComputerSystem
$cpu    = Get-CimInstance Win32_Processor | Select -First 1
$bios   = Get-CimInstance Win32_BIOS
$mb     = Get-CimInstance Win32_BaseBoard
$gpu    = Get-CimInstance Win32_VideoController | Select -First 1
$net    = Get-CimInstance Win32_NetworkAdapterConfiguration | Where {$_.IPEnabled} | Select -First 1
$bat    = Get-CimInstance Win32_Battery | Select -First 1
$disk   = Get-PSDrive C
$screen = Get-CimInstance Win32_VideoController | Select -First 1

# Uptime
$boot      = $os.LastBootUpTime
$uptime    = (Get-Date) - $boot
$uptimeStr = "$($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m"

# Install date age
$installDate = $os.InstallDate
$installAge  = [math]::Round(((Get-Date) - $installDate).TotalDays, 0)

# RAM
$ramGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)

# Network
$lanIP  = if ($net) { ($net.IPAddress | Where {$_ -match '\.'} | Select -First 1) } else { "N/A" }
$gw     = if ($net) { ($net.DefaultIPGateway | Select -First 1) } else { "N/A" }
$dns    = if ($net) { ($net.DNSServerSearchOrder | Select -First 1) } else { "N/A" }
$domain = if ($cs.PartOfDomain) { $cs.Domain } else { "WORKGROUP: $($cs.Workgroup)" }

# WAN IP
try { $wan = (Invoke-WebRequest -Uri "https://api.ipify.org" -TimeoutSec 3 -UseBasicParsing).Content.Trim() } catch { $wan = "N/A" }

# Battery
$batStatus = if ($bat) {
    $pct    = $bat.EstimatedChargeRemaining
    $status = switch ($bat.BatteryStatus) { 1{"Discharging"} 2{"AC Power"} 3{"Fully Charged"} default{"Unknown"} }
    "$status ($pct%)"
} else { "No battery detected" }

# Boot mode
$bootMode = try { if ((bcdedit /enum | Select-String "safeboot")) { "Safe Mode" } else { "Normal" } } catch { "Normal" }

# Defender — wrapped in try/catch so a disabled/replaced AV doesn't crash the whole script
$avEnabled  = "Unknown"
$defUpToDate = "Unknown"
try {
    $defStatus   = Get-MpComputerStatus -ErrorAction Stop
    $avEnabled   = if ($defStatus.AMServiceEnabled) { "Enabled" } else { "Disabled" }
    $defUpToDate = if ($defStatus.AntispywareSignatureAge -le 3) { "Up to date" } else { "$($defStatus.AntispywareSignatureAge) days old" }
} catch {
    $avEnabled   = "Unable to query (third-party AV or Defender disabled)"
    $defUpToDate = "Unknown"
}

[PSCustomObject]@{
    # OS
    OSName       = $os.Caption -replace "Microsoft ",""
    OSBuild      = $os.BuildNumber
    OSArch       = $os.OSArchitecture
    OSInstall    = $installDate.ToString("MM/dd/yyyy")
    OSAge        = "$installAge days old"
    BootMode     = $bootMode
    # Uptime
    LastBoot     = $boot.ToString("MM/dd/yyyy hh:mm tt")
    Uptime       = $uptimeStr
    # Hardware
    Make         = $cs.Manufacturer
    Model        = $cs.Model
    CPU          = "$($cpu.Name) @ $([math]::Round($cpu.MaxClockSpeed/1000,2))GHz ($($cpu.NumberOfLogicalProcessors) logical)"
    RAMGB        = $ramGB
    GPU          = $gpu.Name
    Resolution   = "$($screen.CurrentHorizontalResolution)x$($screen.CurrentVerticalResolution)"
    MB           = "$($mb.Manufacturer) $($mb.Product)"
    BIOSVersion  = "$($bios.SMBIOSBIOSVersion) ($($bios.ReleaseDate.ToString('MM/dd/yyyy')))"
    # Storage
    DiskTotal    = [math]::Round(($disk.Used+$disk.Free)/1GB,1)
    DiskFree     = [math]::Round($disk.Free/1GB,1)
    # Network
    ComputerName = $cs.Name
    Domain       = $domain
    LanIP        = $lanIP
    Gateway      = $gw
    DNS          = $dns
    WAN          = $wan
    # Battery
    Battery      = $batStatus
    # Security
    AVStatus     = $avEnabled
    DefenderUp   = $defUpToDate
} | ConvertTo-Json
