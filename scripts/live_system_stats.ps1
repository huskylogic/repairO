# Repair-O - Live System Stats (pipe-delimited for status bar)
$ErrorActionPreference = "SilentlyContinue"
$cpu = [int]((Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average)
$os = Get-CimInstance Win32_OperatingSystem
$rPct = [int]([math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 0))
$rFree = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
$rTotal = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$d = Get-PSDrive C
$dFree = [math]::Round($d.Free / 1GB, 1)
$dTotal = [math]::Round(($d.Free + $d.Used) / 1GB, 1)
$dPct = [int]([math]::Round($d.Used / ($d.Free + $d.Used) * 100, 0))
$pf = Get-CimInstance Win32_PageFileUsage
$pfGB = if ($pf) { [math]::Round($pf.AllocatedBaseSize / 1024, 1) } else { 0 }
$pfPct = if ($pf -and $pf.AllocatedBaseSize -gt 0) { [int]([math]::Round($pf.CurrentUsage / $pf.AllocatedBaseSize * 100, 0)) } else { 0 }
$ver = $os.Caption -replace "Microsoft ", ""
$build = $os.BuildNumber
Write-Output "$cpu|$rPct|$rFree|$rTotal|$dFree|$dTotal|$dPct|$pfGB|$pfPct|$ver|$build"
