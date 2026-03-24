# Repair-O - Force Uninstall
# Removes a program by killing processes, deleting files, and scrubbing registry
param(
    [string]$ProgramName = "",
    [string]$InstallLocation = "",
    [string]$RegKey = ""
)

$ErrorActionPreference = "Continue"
Write-Output "[Repair-O] FORCE UNINSTALL: $ProgramName"
Write-Output "[WARN] This will forcibly remove files and registry entries."
Write-Output "----------------------------------------------------"

# 1. Kill any running processes from the install folder
if ($InstallLocation -and (Test-Path $InstallLocation)) {
    Write-Output "[Repair-O] Looking for running processes in: $InstallLocation"
    $procs = Get-Process | Where-Object {
        try { $_.MainModule.FileName -like "$InstallLocation*" } catch { $false }
    }
    foreach ($p in $procs) {
        Write-Output "[Repair-O] Killing process: $($p.Name) (PID $($p.Id))"
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
}

# 2. Remove install folder
if ($InstallLocation -and (Test-Path $InstallLocation)) {
    Write-Output "[Repair-O] Removing install folder: $InstallLocation"
    try {
        Remove-Item -Path $InstallLocation -Recurse -Force -ErrorAction Stop
        Write-Output "[OK] Install folder removed."
    } catch {
        Write-Output "[WARN] Could not fully remove folder: $_"
        # Try robocopy empty-folder trick for locked files
        $empty = [System.IO.Path]::GetTempPath() + "\_tm_empty_"
        New-Item -ItemType Directory -Path $empty -Force | Out-Null
        robocopy $empty $InstallLocation /MIR /NFL /NDL /NJH /NJS | Out-Null
        Remove-Item $InstallLocation -Force -ErrorAction SilentlyContinue
        Remove-Item $empty -Force -ErrorAction SilentlyContinue
    }
}

# 3. Remove registry uninstall key
$regPaths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall"
)
foreach ($base in $regPaths) {
    Get-ChildItem $base -ErrorAction SilentlyContinue | ForEach-Object {
        $disp = (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DisplayName
        if ($disp -and $disp.Trim() -eq $ProgramName.Trim()) {
            Write-Output "[Repair-O] Removing registry key: $($_.PSPath)"
            Remove-Item $_.PSPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Output "[OK] Registry key removed."
        }
    }
}

# 4. Remove Start Menu shortcuts
$startMenuPaths = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs",
    "C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
)
foreach ($sm in $startMenuPaths) {
    Get-ChildItem $sm -Recurse -Filter "*.lnk" -ErrorAction SilentlyContinue | ForEach-Object {
        $shell = New-Object -ComObject WScript.Shell
        try {
            $shortcut = $shell.CreateShortcut($_.FullName)
            if ($shortcut.TargetPath -like "*$ProgramName*" -or
                $_.Name -like "*$ProgramName*") {
                Write-Output "[Repair-O] Removing shortcut: $($_.Name)"
                Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
            }
        } catch {}
    }
}

Write-Output "----------------------------------------------------"
Write-Output "[OK] Force uninstall complete for: $ProgramName"
Write-Output "[NEXT] Run 'Scan for Leftovers' to find remaining files/registry entries."
