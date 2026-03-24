# Repair-O - DISM Restore Health
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]UTF8

Write-Output "[Repair-O] Starting DISM RestoreHealth..."
Write-Output "[Repair-O] This downloads repair files from Windows Update."
Write-Output "[Repair-O] May take 15-45 minutes depending on internet speed."
Write-Output "----------------------------------------------------"

$start = Get-Date

$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = "dism.exe"
$pinfo.Arguments = "/Online /Cleanup-Image /RestoreHealth"
$pinfo.RedirectStandardOutput = $true
$pinfo.RedirectStandardError = $true
$pinfo.UseShellExecute = $false
$pinfo.CreateNoWindow = $true

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $pinfo
$p.Start() | Out-Null

while (-not $p.StandardOutput.EndOfStream) {
    $line = $p.StandardOutput.ReadLine()
    if ($line -and $line.Trim() -ne "") {
        Write-Output $line
        [Console]::Out.Flush()
    }
}

$p.WaitForExit()
$elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds)

Write-Output "----------------------------------------------------"
if ($p.ExitCode -eq 0) {
    Write-Output "[OK] DISM RestoreHealth completed in $elapsed seconds."
    Write-Output "[OK] Component store repaired successfully."
    Write-Output "[NEXT] Run SFC /scannow to repair any remaining system files."
} else {
    Write-Output "[WARN] DISM exited with code: $($p.ExitCode)"
    Write-Output "[INFO] If restore failed, Windows Update may be broken."
    Write-Output "[TIP] Try 'Repair Windows Update' from the Treat tab first."
}
