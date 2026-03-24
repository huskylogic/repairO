# Repair-O - Repair Safe Mode Services
# Restores the registry keys Windows needs to boot into Safe Mode.
# Keys use the service name only (no .exe suffix) as Windows expects.
Write-Output "[Repair-O] Restoring Safe Mode services registry keys..."

# These are the services Safe Mode needs to function.
# Grouped as: Minimal (core) and Network (core + networking)
$minimalOnly = @("AppMgmt","AudioSrv","ERSvc","LmHosts","Netlogon","ProtectedStorage",
                 "seclogon","SharedAccess","ShellHWDetection","Themes","TrkWks",
                 "W32Time","wscsvc","wuauserv")
$bothModes   = @("Dhcp","Dnscache","EventLog","LanmanServer","LanmanWorkstation",
                 "PlugPlay","RpcSs","SamSs","Schedule","Winmgmt")

$regBase = "HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal"
$regNet  = "HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Network"

function Set-SafeBootKey($path, $svc) {
    # Key is just the service name — no .exe suffix
    $key = "$path\$svc"
    if (-not (Test-Path $key)) {
        try {
            New-Item -Path $key -Force | Out-Null
            Set-ItemProperty -Path $key -Name "(Default)" -Value "Service" -ErrorAction SilentlyContinue
            Write-Output "  [OK] Created: $svc"
        } catch {
            Write-Output "  [WARN] Could not create $svc : $_"
        }
    } else {
        Write-Output "  [EXISTS] $svc already present"
    }
}

Write-Output "  Restoring Minimal Safe Mode keys..."
foreach ($svc in $bothModes)   { Set-SafeBootKey $regBase $svc }
foreach ($svc in $minimalOnly) { Set-SafeBootKey $regBase $svc }

Write-Output "  Restoring Safe Mode with Networking keys..."
foreach ($svc in $bothModes) { Set-SafeBootKey $regNet $svc }

Write-Output ""
Write-Output "[OK] Safe Mode service keys processed."
Write-Output "[INFO] Reboot and press F8 to test Safe Mode."
