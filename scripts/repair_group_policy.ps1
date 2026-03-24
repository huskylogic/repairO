# Repair-O - Repair Group Policy
Write-Output "[Repair-O] Repairing Group Policy..."
gpupdate /force 2>&1
Write-Output "  [OK] Group Policy updated."

# Use $env:windir — NOT %windir% (CMD syntax does not expand in PowerShell)
$inf = "$env:windir\inf\defltbase.inf"
$sdb = "$env:windir\security\local.sdb"

if (Test-Path $inf) {
    secedit /configure /db $sdb /cfg $inf /areas SECURITYPOLICY /quiet 2>&1
    Write-Output "  [OK] Security policy defaults restored."
} else {
    Write-Output "  [WARN] defltbase.inf not found — skipping security policy reset."
}

Write-Output "[OK] Group Policy repair complete."
