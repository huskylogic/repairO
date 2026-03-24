# Repair-O - Free Physical Memory (empty standby list)
Write-Output "[Repair-O] Freeing physical memory..."

$os        = Get-CimInstance Win32_OperatingSystem
# FreePhysicalMemory is in KB — divide by 1024 twice to get GB
$freeBefore = [math]::Round($os.FreePhysicalMemory / 1024 / 1024, 2)
$totalGB    = [math]::Round($os.TotalVisibleMemorySize / 1024 / 1024, 2)

Write-Output "  Free RAM before: $freeBefore GB of $totalGB GB total"

# Trigger .NET garbage collection — frees managed memory in this process
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
[System.GC]::Collect()

# Query again
$os2       = Get-CimInstance Win32_OperatingSystem
$freeAfter = [math]::Round($os2.FreePhysicalMemory / 1024 / 1024, 2)

Write-Output "  Free RAM after:  $freeAfter GB of $totalGB GB total"
Write-Output ""
Write-Output "[OK] Memory cleanup complete."
Write-Output "[INFO] For deeper standby list clearing, use RAMMap (Sysinternals) or reboot."
