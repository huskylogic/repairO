# Repair-O - Repair Permissions (icacls reset)
# Resets ACLs on user-writable areas only — NOT the Windows directory.
# Resetting C:\Windows permissions requires TrustedInstaller ownership
# and almost always generates access denied errors even as admin.

Write-Output "[Repair-O] Repairing file permissions..."
Write-Output "  Targeting user profile and common problem areas."
Write-Output "  This may take a minute..."

$targets = @(
    "$env:USERPROFILE",
    "$env:APPDATA",
    "$env:LOCALAPPDATA",
    "$env:ProgramData",
    "C:\Users\Public"
)

$errors   = 0
$successes = 0

foreach ($path in $targets) {
    if (Test-Path $path) {
        Write-Output ""
        Write-Output "  Resetting: $path"
        $result = & icacls $path /reset /t /c /q 2>&1
        # icacls exits 0 even with partial failures, so check output
        $failed = $result | Where-Object { $_ -match "access is denied" -or $_ -match "failed" }
        if ($failed) {
            Write-Output "  [WARN] Some entries skipped (system-protected): $($failed.Count) items"
            $errors++
        } else {
            Write-Output "  [OK] Done."
            $successes++
        }
    } else {
        Write-Output "  [SKIP] Not found: $path"
    }
}

Write-Output ""
Write-Output "[Repair-O] Permission repair complete."
Write-Output "  Targets processed: $successes   Partial/skipped: $errors"
Write-Output ""
Write-Output "[INFO] Note: C:\Windows system files are protected by TrustedInstaller"
Write-Output "       and cannot be reset by icacls even as Administrator — this is normal."
Write-Output "       Use 'sfc /scannow' to repair Windows system file permissions."
