# Repair-O - Enable Legacy F8 Boot Menu
Write-Output "[Repair-O] Enabling legacy F8 boot menu..."

# bcdedit /set {default} fails if the boot entry identifier isn't exactly right.
# The reliable approach is to use the current boot entry via /enum and set it directly,
# or use the simpler form that targets the active OS entry.

try {
    # Method 1: target current boot entry using {current} — works on most systems
    $r1 = & bcdedit /set "{current}" bootmenupolicy legacy 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Output "[OK] F8 boot menu enabled (current entry)."
        Write-Output "[INFO] Press F8 during startup to access Advanced Boot Options."
    } else {
        # Method 2: find the OS loader entry and set it directly
        Write-Output "[INFO] Trying alternate method..."
        $enum = & bcdedit /enum 2>&1 | Out-String
        # Extract identifier from the Windows Boot Loader section
        if ($enum -match 'identifier\s+([\{\w-\}]+)') {
            $id = $Matches[1]
            $r2 = & bcdedit /set "$id" bootmenupolicy legacy 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Output "[OK] F8 boot menu enabled (entry: $id)."
                Write-Output "[INFO] Press F8 during startup to access Advanced Boot Options."
            } else {
                Write-Output "[ERROR] Could not set bootmenupolicy: $r2"
                Write-Output "[TIP] Run Repair-O as Administrator and try again."
            }
        } else {
            Write-Output "[ERROR] Could not find boot entry identifier."
            Write-Output "[TIP] Run: bcdedit /set `"{current}`" bootmenupolicy legacy  in an admin PowerShell."
        }
    }
} catch {
    Write-Output "[ERROR] $($_.Exception.Message)"
}
