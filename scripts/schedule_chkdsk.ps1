# Repair-O - Schedule CHKDSK
Write-Output "[Repair-O] Scheduling CHKDSK for next reboot..."
# Use registry method — reliable across all PowerShell versions.
# The old 'echo y | chkdsk' pipe trick works inconsistently in PS.
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager"
Set-ItemProperty -Path $regPath -Name "BootExecute" -Value @("autocheck autochk *","autocheck autochk /r \??\C:") -Type MultiString
if ($LASTEXITCODE -eq 0 -or $?) {
    Write-Output "[OK] CHKDSK scheduled for C: on next reboot."
    Write-Output "[INFO] Reboot when ready. CHKDSK will run before Windows loads."
} else {
    Write-Output "[ERROR] Could not schedule CHKDSK. Run Repair-O as Administrator."
}
