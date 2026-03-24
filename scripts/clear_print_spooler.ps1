# Repair-O - Clear Print Spooler
Write-Output "[Repair-O] Clearing Print Spooler queue..."
Stop-Service -Name Spooler -Force -ErrorAction SilentlyContinue
Write-Output "  Spooler stopped."
$spoolDir = "$env:WINDIR\System32\spool\PRINTERS"
Get-ChildItem $spoolDir -ErrorAction SilentlyContinue |
    Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
Write-Output "  Print queue cleared."
Start-Service -Name Spooler -ErrorAction SilentlyContinue
Write-Output "[OK] Print Spooler cleared and restarted."
