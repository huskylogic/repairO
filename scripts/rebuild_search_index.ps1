# Repair-O - Rebuild Windows Search Index
Write-Output "[Repair-O] Rebuilding Windows Search Index..."
Write-Output "  [INFO] This will delete and rebuild the search index."
Write-Output "  [INFO] Search results may be incomplete for 10-30 minutes while indexing runs."
Write-Output ""

# Stop the Windows Search service
Write-Output "  Stopping Windows Search service..."
Stop-Service WSearch -Force -ErrorAction SilentlyContinue
Start-Sleep 2

# Delete the index database
$indexPath = "$env:ProgramData\Microsoft\Search\Data\Applications\Windows"
if (Test-Path $indexPath) {
    Write-Output "  Deleting index files at: $indexPath"
    Get-ChildItem $indexPath -Recurse -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Output "  [OK] Index files removed."
} else {
    Write-Output "  [INFO] Index path not found at default location — may already be clean."
}

# Reset via registry flag (forces full rebuild on next start)
$regPath = "HKLM:\SOFTWARE\Microsoft\Windows Search"
try {
    Set-ItemProperty -Path $regPath -Name "SetupCompletedSuccessfully" -Value 0 -Type DWord -ErrorAction Stop
    Write-Output "  [OK] Rebuild flag set in registry."
} catch {
    Write-Output "  [WARN] Could not set registry flag: $_"
}

# Restart the service
Write-Output "  Starting Windows Search service..."
Start-Service WSearch -ErrorAction SilentlyContinue
Start-Sleep 2
$svc = Get-Service WSearch -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -eq "Running") {
    Write-Output "  [OK] Windows Search service running — indexing will begin shortly."
} else {
    Write-Output "  [WARN] Windows Search service did not start. May need a reboot."
}

Write-Output ""
Write-Output "[OK] Search index rebuild initiated."
Write-Output "[INFO] Full indexing typically completes within 15-30 minutes."
