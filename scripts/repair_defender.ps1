# Repair-O - Repair Windows Defender
Write-Output "[Repair-O] Repairing Windows Defender..."
$defPath = "$env:ProgramFiles\Windows Defender"
if (Test-Path $defPath) {
    Get-ChildItem "$defPath\*.dll" | ForEach-Object {
        regsvr32 /s $_.FullName 2>&1 | Out-Null
    }
}
Set-Service -Name "WinDefend" -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service -Name "WinDefend" -ErrorAction SilentlyContinue
Write-Output "  Updating definitions..."
Update-MpSignature -ErrorAction SilentlyContinue
Write-Output "[OK] Windows Defender repair complete."
