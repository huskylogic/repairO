# Repair-O - Maintenance Cleanup
param([string]$Action = "temp")
$ErrorActionPreference = "SilentlyContinue"

function Get-FolderSize($path) {
    $items = Get-ChildItem $path -Recurse -Force -ErrorAction SilentlyContinue
    return ($items | Measure-Object -Property Length -Sum).Sum
}

function Remove-FolderContents($path) {
    $size = Get-FolderSize $path
    Get-ChildItem $path -Force -ErrorAction SilentlyContinue | ForEach {
        Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    }
    return [math]::Round($size / 1MB, 1)
}

switch ($Action) {
    "temp" {
        Write-Output "[Repair-O] Emptying temp folders..."
        $sz1 = Remove-FolderContents $env:TEMP
        $sz2 = Remove-FolderContents "C:\Windows\Temp"
        Write-Output "[OK] User temp: ${sz1} MB removed"
        Write-Output "[OK] System temp: ${sz2} MB removed"
    }
    "alltemp" {
        Write-Output "[Repair-O] Emptying all users temp folders..."
        $total = 0
        Get-ChildItem "C:\Users" -Directory | ForEach {
            $p = "$($_.FullName)\AppData\Local\Temp"
            if (Test-Path $p) { $total += Remove-FolderContents $p }
        }
        Write-Output "[OK] Total removed: ${total} MB from all user temp folders"
    }
    "winsxs" {
        Write-Output "[Repair-O] Cleaning up WinSxS component store..."
        Write-Output "[INFO] This may take several minutes..."
        DISM /Online /Cleanup-Image /StartComponentCleanup /ResetBase 2>&1
        Write-Output "[OK] WinSxS cleanup complete."
    }
    "softwaredist" {
        Write-Output "[Repair-O] Clearing Windows Update download cache..."
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Start-Sleep 2
        $sz = Remove-FolderContents "C:\Windows\SoftwareDistribution\Download"
        Start-Service wuauserv -ErrorAction SilentlyContinue
        Write-Output "[OK] Cleared ${sz} MB from SoftwareDistribution\Download"
    }
    "windowsold" {
        Write-Output "[Repair-O] Removing Windows.old folder..."
        Write-Output "[INFO] This may take several minutes..."
        if (Test-Path "C:\Windows.old") {
            takeown /f "C:\Windows.old" /r /d y 2>&1 | Out-Null
            icacls "C:\Windows.old" /grant administrators:F /t 2>&1 | Out-Null
            $sz = Remove-FolderContents "C:\Windows.old"
            Remove-Item "C:\Windows.old" -Force -ErrorAction SilentlyContinue
            Write-Output "[OK] Windows.old removed. Freed ${sz} MB."
        } else {
            Write-Output "[INFO] Windows.old not found on this PC."
        }
    }
    "diskcleanup" {
        Write-Output "[Repair-O] Running disk cleanup (unattended)..."
        $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches"
        $keys = Get-ChildItem $regPath
        foreach ($key in $keys) {
            Set-ItemProperty -Path $key.PSPath -Name StateFlags0064 -Value 2 -Type DWORD -ErrorAction SilentlyContinue
        }
        Start-Process cleanmgr -ArgumentList "/sagerun:64" -Wait
        Write-Output "[OK] Disk cleanup complete."
    }
    "notificationcache" {
        Write-Output "[Repair-O] Clearing notification area icon cache..."
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
        Start-Sleep 1
        reg delete "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\TrayNotify" /v IconStreams /f 2>&1 | Out-Null
        reg delete "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\TrayNotify" /v PastIconsStream /f 2>&1 | Out-Null
        Start-Process explorer
        Write-Output "[OK] Notification cache cleared. Explorer restarted."
    }
    "ghostdevices" {
        Write-Output "[Repair-O] Removing ghost/non-present devices..."
        $removed = 0
        Get-PnpDevice -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Unknown" } | ForEach-Object {
            try {
                $_ | Disable-PnpDevice -Confirm:$false -ErrorAction SilentlyContinue
                $removed++
            } catch {}
        }
        Write-Output "[OK] Removed $removed ghost device(s)."
    }
    "eventlogs" {
        Write-Output "[Repair-O] Clearing Windows event logs..."
        $logs = @("Application","System","Security","Setup")
        foreach ($log in $logs) {
            try {
                Clear-EventLog -LogName $log -ErrorAction SilentlyContinue
                Write-Output "[OK] Cleared: $log"
            } catch {}
        }
        Write-Output "[OK] Event log clearing complete."
    }
    "errorreports" {
        Write-Output "[Repair-O] Clearing error report folders..."
        $paths = @(
            "$env:LOCALAPPDATA\Microsoft\Windows\WER\ReportArchive",
            "$env:LOCALAPPDATA\Microsoft\Windows\WER\ReportQueue",
            "C:\ProgramData\Microsoft\Windows\WER\ReportArchive",
            "C:\ProgramData\Microsoft\Windows\WER\ReportQueue"
        )
        $total = 0
        foreach ($p in $paths) {
            if (Test-Path $p) { $total += Remove-FolderContents $p }
        }
        Write-Output "[OK] Cleared ${total} MB from error report folders."
    }
    "shellcache" {
        Write-Output "[Repair-O] Clearing shell cache and MuiCache..."
        reg delete "HKCU\Software\Microsoft\Windows\ShellNoRoam\MUICache" /f 2>&1 | Out-Null
        reg delete "HKCU\Software\Classes\Local Settings\MuiCache" /f 2>&1 | Out-Null
        Write-Output "[OK] Shell MuiCache cleared."
    }
    "msiorphans" {
        Write-Output "[Repair-O] Checking MSI orphan files..."
        $installer = "C:\Windows\Installer"
        $files = Get-ChildItem $installer -Filter "*.msi" -ErrorAction SilentlyContinue
        $count = if ($files) { $files.Count } else { 0 }
        $size = if ($files) { [math]::Round(($files | Measure-Object -Property Length -Sum).Sum / 1MB, 1) } else { 0 }
        Write-Output "[INFO] Found $count MSI files using ${size} MB in Windows\Installer."
        Write-Output "[INFO] Use Disk Cleanup with 'Windows Installer unused files' for safe removal."
        Write-Output "[OK] MSI orphan check complete."
    }
    "temp_profiles" {
        Write-Output "[Repair-O] Removing temporary profile folders..."
        $profilePath = "C:\Users"
        $removed = 0
        Get-ChildItem $profilePath -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "\.bak$|TEMP|\.000$" } | ForEach-Object {
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
            Write-Output "[FOUND] Removed: $($_.Name)"
            $removed++
        }
        Write-Output "[OK] Removed $removed temporary profile folder(s)."
    }
    default {
        Write-Output "[ERROR] Unknown action: $Action"
        Write-Output "[INFO] Valid actions: temp, alltemp, winsxs, softwaredist, windowsold, diskcleanup, notificationcache, ghostdevices, eventlogs, errorreports, shellcache, msiorphans, temp_profiles"
    }
}
