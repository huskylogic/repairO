# Repair-O - Fix Device Manager (scan for hardware changes)
Write-Output "[Repair-O] Scanning for hardware changes..."
$code = @"
using System;
using System.Runtime.InteropServices;
public class DevMgmt {
    [DllImport("newdev.dll", CharSet=CharSet.Auto, SetLastError=true)]
    public static extern bool UpdateDriverForPlugAndPlayDevices(
        IntPtr hwndParent, string HardwareId, string FullInfPath,
        uint InstallFlags, ref bool bRebootRequired);
}
"@
try {
    Add-Type -TypeDefinition $code -ErrorAction SilentlyContinue
} catch {}
# Use pnputil to scan
pnputil /scan-devices 2>&1
Write-Output "[OK] Hardware scan complete."
