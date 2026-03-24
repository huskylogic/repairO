# Repair-O - DISM Scan Health
# Force unbuffered output so progress shows in real time
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output "[Repair-O] Starting DISM ScanHealth..."
Write-Output "[Repair-O] This may take 5-15 minutes. Please wait."
Write-Output "----------------------------------------------------"

$start = Get-Date

# Run DISM and capture output line by line
$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = "dism.exe"
$pinfo.Arguments = "/Online /Cleanup-Image /ScanHealth"
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
    Write-Output "[OK] DISM ScanHealth completed in $elapsed seconds."
    Write-Output "[OK] No component store corruption detected."
} elseif ($p.ExitCode -eq -2146498554) {
    Write-Output "[FOUND] Component store corruption detected."
    Write-Output "[ACTION] Run 'DISM Restore Health' to repair it."
} else {
    Write-Output "[WARN] DISM exited with code: $($p.ExitCode)"
    Write-Output "[INFO] Check above output for details."
}
