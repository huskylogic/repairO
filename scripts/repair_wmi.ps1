# Repair-O - Repair WMI/WBEM/DCOM
Write-Output "[Repair-O] Repairing WMI/WBEM/DCOM..."
Stop-Service winmgmt -Force -ErrorAction SilentlyContinue
Write-Output "  Running winmgmt /salvagerepository..."
winmgmt /salvagerepository C:\Windows\System32\wbem
Write-Output "  Re-registering WMI DLLs..."
$wbemPath = "$env:WINDIR\System32\wbem"
Get-ChildItem $wbemPath -Filter "*.dll" | ForEach-Object { regsvr32 /s $_.FullName }
Get-ChildItem $wbemPath -Filter "*.exe" | ForEach-Object { & $_.FullName /RegServer 2>&1 | Out-Null }
Write-Output "  Recompiling MOF files..."
Get-ChildItem "$wbemPath\*.mof" -ErrorAction SilentlyContinue | ForEach-Object {
    mofcomp $_.FullName | Out-Null
}
Start-Service winmgmt -ErrorAction SilentlyContinue
Write-Output "[OK] WMI repair complete."
