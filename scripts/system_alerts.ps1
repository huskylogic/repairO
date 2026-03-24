# Repair-O - System Alerts Scanner
$ErrorActionPreference = "SilentlyContinue"
$alerts = @()

# Windows Activation
$lic = Get-CimInstance SoftwareLicensingProduct | Where {$_.PartialProductKey -and $_.Name -match "Windows"}
$activated = ($lic | Where {$_.LicenseStatus -eq 1}) -ne $null
if (-not $activated) { $alerts += @{Level="ERROR"; Title="Windows Not Activated"; Detail="Windows license is not activated."} }

# Defender status
try {
    $def = Get-MpComputerStatus -ErrorAction Stop
    if (-not $def.AMServiceEnabled) { $alerts += @{Level="ERROR"; Title="Defender Disabled"; Detail="Windows Defender service is not running."} }
    if ($def.AntispywareSignatureAge -gt 3) { $alerts += @{Level="WARN"; Title="Defender Out of Date"; Detail="Virus definitions are $($def.AntispywareSignatureAge) days old."} }
    $defRunning = $def.AMServiceEnabled
    $defSigAge  = $def.AntispywareSignatureAge
} catch {
    $alerts += @{Level="WARN"; Title="Defender Status Unknown"; Detail="Could not query Defender — may be replaced by third-party AV."}
    $defRunning = $false
    $defSigAge  = 999
}

# Windows Update pending
try {
    $wu = (New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher()
    $pending = $wu.Search("IsInstalled=0 and Type='Software'").Updates.Count
    if ($pending -gt 0) { $alerts += @{Level="WARN"; Title="Windows Updates Pending"; Detail="$pending update(s) waiting to install."} }
} catch {}

# Crash dumps — null-safe check for PS5 compatibility
$dumps = Get-ChildItem "C:\Windows\Minidump" -ErrorAction SilentlyContinue
$dumpCount = if ($null -ne $dumps) { @($dumps).Count } else { 0 }
if ($dumpCount -gt 0) { $alerts += @{Level="WARN"; Title="Crash Dumps Found"; Detail="$dumpCount minidump file(s) in C:\Windows\Minidump."} }

# Disk space
$disk = Get-PSDrive C
$freePct = [math]::Round($disk.Free / ($disk.Free + $disk.Used) * 100, 0)
if ($freePct -lt 10) { $alerts += @{Level="ERROR"; Title="Critical Disk Space"; Detail="C: drive is $freePct% free. Less than 10% remaining."} }
elseif ($freePct -lt 20) { $alerts += @{Level="WARN"; Title="Low Disk Space"; Detail="C: drive is $freePct% free."} }

# Hidden devices
$hdCount = @(Get-PnpDevice | Where {$_.Status -eq "Error"}).Count
if ($hdCount -gt 0) { $alerts += @{Level="WARN"; Title="Device Errors Found"; Detail="$hdCount device(s) have errors in Device Manager."} }

# Event log errors (last 24h)
$errCount = @(Get-EventLog -LogName System -EntryType Error -After (Get-Date).AddHours(-24) -ErrorAction SilentlyContinue).Count
if ($errCount -gt 5) { $alerts += @{Level="WARN"; Title="System Event Errors"; Detail="$errCount system errors logged in the last 24 hours."} }

# Windows.old
$winOld = Test-Path "C:\Windows.old"
if ($winOld) {
    $size = [math]::Round((Get-ChildItem "C:\Windows.old" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB, 1)
    $alerts += @{Level="INFO"; Title="Windows.old Found"; Detail="$size GB of old Windows files can be removed."}
}

# SoftwareDistribution size
$swDist = Get-ChildItem "C:\Windows\SoftwareDistribution\Download" -Recurse -ErrorAction SilentlyContinue
if ($null -ne $swDist) {
    $size = [math]::Round((@($swDist) | Measure-Object -Property Length -Sum).Sum / 1GB, 1)
    if ($size -gt 1) { $alerts += @{Level="INFO"; Title="Windows Update Cache"; Detail="$size GB in SoftwareDistribution\Download can be cleared."} }
}

# System Restore points
$sr = @(Get-ComputerRestorePoint -ErrorAction SilentlyContinue)
$srHasPoints = $sr.Count -gt 0
if (-not $srHasPoints) { $alerts += @{Level="WARN"; Title="No Restore Points"; Detail="System Restore has no restore points or is disabled."} }

# Passed checks
$passed = @()
if ($activated)    { $passed += "Windows is activated" }
if ($defRunning)   { $passed += "Windows Defender is running" }
if ($freePct -ge 20) { $passed += "Disk space is adequate ($freePct% free)" }
if ($dumpCount -eq 0) { $passed += "No crash dumps found" }
if ($srHasPoints)  { $passed += "System Restore has restore points" }

$alerts | ConvertTo-Json -Depth 3
Write-Output "---PASSED---"
$passed | ConvertTo-Json
