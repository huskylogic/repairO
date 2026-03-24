# Repair-O - List Installed Programs
# Returns JSON array of installed programs from registry
$ErrorActionPreference = "SilentlyContinue"

$paths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$programs = foreach ($path in $paths) {
    Get-ItemProperty $path -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -and $_.DisplayName.Trim() -ne "" } |
    Select-Object @{N="Name";E={$_.DisplayName.Trim()}},
                  @{N="Version";E={$_.DisplayVersion}},
                  @{N="Publisher";E={$_.Publisher}},
                  @{N="InstallDate";E={$_.InstallDate}},
                  @{N="InstallLocation";E={$_.InstallLocation}},
                  @{N="UninstallString";E={$_.UninstallString}},
                  @{N="QuietUninstall";E={$_.QuietUninstallString}},
                  @{N="EstimatedSize";E={$_.EstimatedSize}},
                  @{N="RegKey";E={$_.PSPath}}
}

$unique = $programs | Sort-Object Name | Group-Object Name | ForEach-Object { $_.Group[0] }

$unique | ConvertTo-Json -Depth 3
