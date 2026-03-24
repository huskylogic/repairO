# Repair-O - Clear System Restore Points
Write-Output "[Repair-O] Deleting all shadow copies / System Restore points..."
try {
    $result = & vssadmin delete shadows /all /quiet 2>&1
    Write-Output "  $result"
    Write-Output "[OK] All shadow copies deleted."
} catch {
    Write-Output "[ERROR] Failed to delete shadow copies: $_"
    exit 1
}
