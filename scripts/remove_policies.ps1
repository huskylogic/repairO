# Repair-O - Remove Policies (malware-set restrictions)
Write-Output "[Repair-O] Removing malware-set policy restrictions..."
$policyPaths = @(
    "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System",
    "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\SystemRestore",
    "HKCU:\SOFTWARE\Policies\Microsoft\Windows\System",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
)
$restrictedValues = @("DisableTaskMgr","DisableRegistryTools","NoControlPanel",
    "DisableCMD","HideSCAHealth","DisableAntiSpyware","DisableAntiVirus",
    "DisableWindowsUpdateAccess","NoDispCPL","NoRun","NoClose","NoFind",
    "DisableRegedit","DisableSystemRestore")
foreach ($path in $policyPaths) {
    if (Test-Path $path) {
        foreach ($val in $restrictedValues) {
            $prop = Get-ItemProperty -Path $path -Name $val -ErrorAction SilentlyContinue
            if ($null -ne $prop.$val) {
                Remove-ItemProperty -Path $path -Name $val -Force -ErrorAction SilentlyContinue
                Write-Output "  [REMOVED] $val from $path"
            }
        }
    }
}
Write-Output "[OK] Policy cleanup complete."
