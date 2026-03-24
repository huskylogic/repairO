# Repair-O - Delete Pending File Rename Operations
Write-Output "[Repair-O] Removing Pending File Rename Operations registry key..."
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager"
$prop = Get-ItemProperty -Path $regPath -Name "PendingFileRenameOperations" -ErrorAction SilentlyContinue
if ($null -ne $prop) {
    Remove-ItemProperty -Path $regPath -Name "PendingFileRenameOperations" -Force
    Write-Output "[OK] PendingFileRenameOperations key removed."
} else {
    Write-Output "[OK] PendingFileRenameOperations key not present - nothing to remove."
}
