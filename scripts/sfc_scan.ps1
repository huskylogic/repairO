# Repair-O - System File Checker
$ErrorActionPreference = "Continue"

Write-Output "[Repair-O] Starting System File Checker (SFC)..."
Write-Output "[Repair-O] This may take 10-20 minutes. Please wait."
Write-Output "----------------------------------------------------"

$start = Get-Date

$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = "sfc.exe"
$pinfo.Arguments = "/scannow"
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
        # SFC outputs in Unicode - clean up any weird chars
        $clean = $line -replace '[^\x20-\x7E\r\n]', ''
        if ($clean.Trim() -ne "") {
            Write-Output $clean
            [Console]::Out.Flush()
        }
    }
}

$p.WaitForExit()
$elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds)

Write-Output "----------------------------------------------------"
Write-Output "[Repair-O] SFC completed in $elapsed seconds."
Write-Output "[INFO] Full log available at: C:\Windows\Logs\CBS\CBS.log"

if ($p.ExitCode -eq 0) {
    Write-Output "[OK] SFC found no integrity violations."
} else {
    Write-Output "[INFO] SFC found and attempted to repair issues."
    Write-Output "[NEXT] If problems persist, run DISM RestoreHealth then SFC again."
}
