# Repair-O - System Information Script
# Returns all system vitals as JSON for the Python GUI to parse

$output = @{}

# --- OS Information ---
$os = Get-CimInstance Win32_OperatingSystem
$output["OS"] = @{
    "Name"              = $os.Caption
    "Version"           = $os.Version
    "Build"             = $os.BuildNumber
    "Architecture"      = $os.OSArchitecture
    "Install Date"      = $os.InstallDate.ToString("yyyy-MM-dd")
    "Last Boot"         = $os.LastBootUpTime.ToString("yyyy-MM-dd HH:mm:ss")
    "Uptime"            = "{0}d {1}h {2}m" -f ($os.LocalDateTime - $os.LastBootUpTime).Days, ($os.LocalDateTime - $os.LastBootUpTime).Hours, ($os.LocalDateTime - $os.LastBootUpTime).Minutes
    "Registered User"   = $os.RegisteredUser
    "Organization"      = $os.Organization
    "Serial Number"     = $os.SerialNumber
    "Windows Directory" = $os.WindowsDirectory
    "System Directory"  = $os.SystemDirectory
    "Locale"            = $os.Locale
    "Time Zone"         = (Get-TimeZone).DisplayName
}

# --- Computer / BIOS ---
$cs   = Get-CimInstance Win32_ComputerSystem
$bios = Get-CimInstance Win32_BIOS
$output["Computer"] = @{
    "Manufacturer"    = $cs.Manufacturer
    "Model"           = $cs.Model
    "System Type"     = $cs.SystemType
    "Domain"          = $cs.Domain
    "Workgroup"       = $cs.Workgroup
    "PC Name"         = $cs.Name
    "BIOS Version"    = $bios.SMBIOSBIOSVersion
    "BIOS Vendor"     = $bios.Manufacturer
    "BIOS Date"       = $bios.ReleaseDate.ToString("yyyy-MM-dd")
    "Serial Number"   = $bios.SerialNumber
    "Chassis Type"    = (Get-CimInstance Win32_SystemEnclosure).ChassisTypes -join ", "
}

# --- CPU ---
$cpu = Get-CimInstance Win32_Processor
$output["CPU"] = @{
    "Name"             = $cpu.Name.Trim()
    "Manufacturer"     = $cpu.Manufacturer
    "Cores"            = $cpu.NumberOfCores
    "Logical Procs"    = $cpu.NumberOfLogicalProcessors
    "Max Speed (MHz)"  = $cpu.MaxClockSpeed
    "Current Speed"    = $cpu.CurrentClockSpeed
    "Architecture"     = switch($cpu.Architecture) { 0{"x86"} 9{"x64"} 12{"ARM64"} default{"Unknown"} }
    "Socket"           = $cpu.SocketDesignation
    "L2 Cache (KB)"    = $cpu.L2CacheSize
    "L3 Cache (KB)"    = $cpu.L3CacheSize
    "CPU ID"           = $cpu.ProcessorId
    "Virtualization"   = if($cpu.VirtualizationFirmwareEnabled){"Enabled"}else{"Disabled"}
}

# --- RAM ---
$ram      = Get-CimInstance Win32_PhysicalMemory
$totalRAM = [math]::Round(($ram | Measure-Object -Property Capacity -Sum).Sum / 1GB, 2)
$ramSlots = @()
foreach ($stick in $ram) {
    $ramSlots += "{0}GB {1} @ {2}MHz ({3})" -f [math]::Round($stick.Capacity/1GB,1), $stick.MemoryType, $stick.Speed, $stick.BankLabel
}
$osRam = Get-CimInstance Win32_OperatingSystem
$output["RAM"] = @{
    "Total (GB)"       = $totalRAM
    "Available (GB)"   = [math]::Round($osRam.FreePhysicalMemory / 1MB, 2)
    "Used (GB)"        = [math]::Round(($osRam.TotalVisibleMemorySize - $osRam.FreePhysicalMemory) / 1MB, 2)
    "Slots Used"       = $ram.Count
    "Sticks"           = $ramSlots -join " | "
    "Virtual Total"    = [math]::Round($osRam.TotalVirtualMemorySize / 1MB, 2)
    "Virtual Free"     = [math]::Round($osRam.FreeVirtualMemory / 1MB, 2)
}

# --- Disk Drives (fast, no ASSOCIATORS — fixed to correctly map volumes per disk) ---
$disks = @{}
try {
    $physDisks    = Get-CimInstance Win32_DiskDrive
    $logicalDisks = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }

    # Build a map of disk index -> logical drives using Win32_DiskDriveToDiskPartition
    # and Win32_LogicalDiskToPartition (faster than ASSOCIATORS, still accurate)
    $partMap = @{}
    Get-CimInstance Win32_DiskDriveToDiskPartition | ForEach-Object {
        $driveId  = $_.Antecedent.DeviceID
        $partId   = $_.Dependent.DeviceID
        if (-not $partMap[$driveId]) { $partMap[$driveId] = @() }
        $partMap[$driveId] += $partId
    }
    $volMap = @{}
    Get-CimInstance Win32_LogicalDiskToPartition | ForEach-Object {
        $partId  = $_.Antecedent.DeviceID
        $volLetter = $_.Dependent.DeviceID
        $volMap[$partId] = $volLetter
    }

    foreach ($disk in $physDisks) {
        $diskKey = "Disk $($disk.Index)"
        $partIds = $partMap[$disk.DeviceID]
        $vols = @()
        if ($partIds) {
            foreach ($pid in $partIds) {
                $letter = $volMap[$pid]
                if ($letter) {
                    $ld = $logicalDisks | Where-Object { $_.DeviceID -eq $letter } | Select-Object -First 1
                    if ($ld) {
                        $vols += "$letter  $([math]::Round($ld.Size/1GB,1))GB total, $([math]::Round($ld.FreeSpace/1GB,1))GB free"
                    }
                }
            }
        }
        if ($vols.Count -eq 0) { $vols += "(no mapped volumes)" }
        $disks[$diskKey] = @{
            "Model"      = $disk.Model
            "Interface"  = $disk.InterfaceType
            "Size (GB)"  = [math]::Round($disk.Size / 1GB, 1)
            "Partitions" = $disk.Partitions
            "Serial"     = $disk.SerialNumber.Trim()
            "Status"     = $disk.Status
            "Volumes"    = ($vols -join " | ")
        }
    }
} catch {
    $disks["Error"] = @{ "Note" = "Could not retrieve disk info: $_" }
}
$output["Disks"] = $disks

# --- GPU ---
$gpus    = Get-CimInstance Win32_VideoController
$gpuList = @()
foreach ($gpu in $gpus) {
    $gpuList += @{
        "Name"           = $gpu.Name
        "VRAM (MB)"      = [math]::Round($gpu.AdapterRAM / 1MB, 0)
        "Driver Version" = $gpu.DriverVersion
        "Driver Date"    = $gpu.DriverDate.ToString("yyyy-MM-dd")
        "Resolution"     = "$($gpu.CurrentHorizontalResolution)x$($gpu.CurrentVerticalResolution)"
        "Refresh Rate"   = "$($gpu.CurrentRefreshRate)Hz"
        "Status"         = $gpu.Status
    }
}
$output["GPU"] = $gpuList

# --- Network Adapters ---
$nics    = Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled }
$nicList = @()
foreach ($nic in $nics) {
    $nicList += @{
        "Description"  = $nic.Description
        "MAC Address"  = $nic.MACAddress
        "IP Address"   = ($nic.IPAddress -join ", ")
        "Subnet"       = ($nic.IPSubnet -join ", ")
        "Gateway"      = ($nic.DefaultIPGateway -join ", ")
        "DNS Servers"  = ($nic.DNSServerSearchOrder -join ", ")
        "DHCP Enabled" = $nic.DHCPEnabled
        "DHCP Server"  = $nic.DHCPServer
    }
}
$output["Network"] = $nicList

# --- Antivirus / Security ---
try {
    $av = Get-CimInstance -Namespace "root/SecurityCenter2" -ClassName AntiVirusProduct -ErrorAction Stop
    $avList = @()
    foreach ($a in $av) {
        $state = switch ($a.productState.ToString("X6").Substring(2,2)) {
            "10" { "Enabled" } "11" { "Enabled" } "00" { "Disabled" } "01" { "Disabled" } default { "Unknown" }
        }
        $upToDate = switch ($a.productState.ToString("X6").Substring(4,2)) {
            "00" { "Up to Date" } "10" { "Out of Date" } default { "Unknown" }
        }
        $avList += "$($a.displayName) [$state, $upToDate]"
    }
    $output["Security"] = @{ "Antivirus" = ($avList -join " | ") }
} catch {
    $output["Security"] = @{ "Antivirus" = "Unable to query (run as Admin)" }
}

# UAC Status
$uac = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -ErrorAction SilentlyContinue).EnableLUA
$output["Security"]["UAC"] = if($uac -eq 1){"Enabled"}else{"Disabled"}

# Firewall
try {
    $fw       = Get-NetFirewallProfile -ErrorAction Stop
    $fwStatus = ($fw | ForEach-Object { "$($_.Name): $(if($_.Enabled){'On'}else{'Off'})" }) -join " | "
    $output["Security"]["Firewall"] = $fwStatus
} catch {
    $output["Security"]["Firewall"] = "Unable to query"
}

# Secure Boot
try {
    $sb = Confirm-SecureBootUEFI -ErrorAction Stop
    $output["Security"]["Secure Boot"] = if($sb){"Enabled"}else{"Disabled"}
} catch {
    $output["Security"]["Secure Boot"] = "Not supported / N/A"
}

# BitLocker
try {
    $bl       = Get-BitLockerVolume -ErrorAction Stop | Select-Object MountPoint, ProtectionStatus
    $blStatus = ($bl | ForEach-Object { "$($_.MountPoint): $($_.ProtectionStatus)" }) -join " | "
    $output["Security"]["BitLocker"] = $blStatus
} catch {
    $output["Security"]["BitLocker"] = "Unable to query"
}

# --- Installed Updates (last 10) ---
$updates    = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10
$updateList = @()
foreach ($u in $updates) {
    $updateList += "$($u.HotFixID) - $($u.Description) ($($u.InstalledOn))"
}
$output["Updates"] = @{ "Recent (Last 10)" = $updateList -join " | " }

# --- Startup Programs ---
$startupItems = @()
$regPaths = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
)
foreach ($path in $regPaths) {
    if (Test-Path $path) {
        $items = Get-ItemProperty $path
        $items.PSObject.Properties | Where-Object { $_.Name -notlike "PS*" } | ForEach-Object {
            $startupItems += "$($_.Name): $($_.Value)"
        }
    }
}
$output["Startup"] = @{ "Items" = $startupItems -join " | " }

# --- Environment ---
$output["Environment"] = @{
    "Username"       = $env:USERNAME
    "Computer Name"  = $env:COMPUTERNAME
    "User Domain"    = $env:USERDOMAIN
    "User Profile"   = $env:USERPROFILE
    "System Drive"   = $env:SystemDrive
    "Temp Path"      = $env:TEMP
    "PowerShell Ver" = $PSVersionTable.PSVersion.ToString()
    ".NET Version"   = [System.Runtime.InteropServices.RuntimeEnvironment]::GetSystemVersion()
}

# Output as JSON
$output | ConvertTo-Json -Depth 5
