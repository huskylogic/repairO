# Repair-O - Create System Restore Point
Write-Output "[Repair-O] Creating System Restore Point..."
try {
    Enable-ComputerRestore -Drive "C:\" -ErrorAction SilentlyContinue
    Checkpoint-Computer -Description "Repair-O Restore Point $(Get-Date -Format 'yyyy-MM-dd HH:mm')" -RestorePointType "MODIFY_SETTINGS"
    Write-Output "[OK] Restore point created successfully."
} catch {
    Write-Output "[ERROR] Failed to create restore point: $_"
    exit 1
}
