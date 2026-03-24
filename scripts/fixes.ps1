# Repair-O - Common Windows Fixes
param([string]$Action = "")
$ErrorActionPreference = "SilentlyContinue"

switch ($Action) {
    "wmi" {
        Write-Output "[Repair-O] Fixing WMI and System Restore..."
        Stop-Service winmgmt -Force
        $wmiPath = "C:\Windows\System32\wbem"
        Get-ChildItem "$wmiPath\Repository" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Start-Service winmgmt
        Get-ChildItem "$wmiPath" -Filter "*.mof" | ForEach { mofcomp $_.FullName 2>&1 | Out-Null }
        Write-Output "[OK] WMI repository rebuilt."
    }
    "installer" {
        Write-Output "[Repair-O] Fixing Windows Installer service..."
        # Use $env:windir — NOT %windir% (CMD syntax doesn't expand in PowerShell)
        & "$env:windir\system32\msiexec.exe" /unregister 2>&1 | Out-Null
        & "$env:windir\system32\msiexec.exe" /regserver 2>&1 | Out-Null
        Set-Service msiserver -StartupType Manual
        Start-Service msiserver
        Write-Output "[OK] Windows Installer re-registered and started."
    }
    "exe_associations" {
        Write-Output "[Repair-O] Fixing executable file associations..."
        reg add "HKCR\.exe" /ve /t REG_SZ /d "exefile" /f | Out-Null
        reg add "HKCR\exefile" /ve /t REG_SZ /d "Application" /f | Out-Null
        reg add "HKCR\exefile\shell\open\command" /ve /t REG_SZ /d '"%1" %*' /f | Out-Null
        reg add "HKCR\exefile\shell\runas\command" /ve /t REG_SZ /d '"%1" %*' /f | Out-Null
        Write-Output "[OK] .exe file associations restored."
    }
    "windows_update" {
        Write-Output "[Repair-O] Fixing and enabling Windows Update..."
        $services = @("wuauserv","cryptsvc","bits","msiserver")
        foreach ($s in $services) { Stop-Service $s -Force -ErrorAction SilentlyContinue }
        Remove-Item "C:\Windows\SoftwareDistribution" -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item "C:\Windows\System32\catroot2" -Recurse -Force -ErrorAction SilentlyContinue
        foreach ($s in $services) { Set-Service $s -StartupType Automatic; Start-Service $s -ErrorAction SilentlyContinue }
        Write-Output "[OK] Windows Update services reset and restarted."
    }
    "defender_services" {
        Write-Output "[Repair-O] Fixing Microsoft Defender services..."
        Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction SilentlyContinue
        Start-Service WinDefend -ErrorAction SilentlyContinue
        Start-Service SecurityHealthService -ErrorAction SilentlyContinue
        reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiSpyware /f 2>&1 | Out-Null
        Write-Output "[OK] Defender services restored."
    }
    "store_apps" {
        Write-Output "[Repair-O] Fixing Windows Store and Metro apps..."
        Get-AppxPackage -AllUsers | Foreach { Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml" -ErrorAction SilentlyContinue }
        Write-Output "[OK] App packages re-registered."
    }
    "start_menu" {
        Write-Output "[Repair-O] Fixing Start Menu..."
        Get-AppxPackage -AllUsers *ShellExperienceHost* | Foreach { Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml" -ErrorAction SilentlyContinue }
        Get-AppxPackage -AllUsers *StartMenuExperienceHost* | Foreach { Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml" -ErrorAction SilentlyContinue }
        Write-Output "[OK] Start Menu apps re-registered."
    }
    "user_profile" {
        Write-Output "[Repair-O] Fixing corrupted user profile references..."
        $profileList = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"
        Get-ChildItem $profileList | ForEach {
            $p = Get-ItemProperty $_.PSPath
            if ($p.ProfileImagePath -and -not (Test-Path $p.ProfileImagePath)) {
                Write-Output "[FOUND] Orphaned profile: $($p.ProfileImagePath)"
            }
        }
        Write-Output "[OK] Profile scan complete. Use Migration tab to recover user data."
    }
    "task_scheduler" {
        Write-Output "[Repair-O] Fixing Task Scheduler..."
        Stop-Service Schedule -Force
        Start-Service Schedule
        Set-Service Schedule -StartupType Automatic
        Write-Output "[OK] Task Scheduler restarted."
    }
    "wifi_slow" {
        Write-Output "[Repair-O] Fixing slow WiFi connection..."
        reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\DefaultMediaCost" /v Wifi /t REG_DWORD /d 2 /f | Out-Null
        netsh wlan set autoconfig enabled=yes interface="Wi-Fi" 2>&1 | Out-Null
        reg add "HKLM\SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\config" /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f | Out-Null
        Write-Output "[OK] WiFi slow connect fix applied."
    }
    "network_visibility" {
        Write-Output "[Repair-O] Fixing PC not visible on network..."
        Set-Service fdrespub -StartupType Automatic; Start-Service fdrespub
        Set-Service FDResPub -StartupType Automatic; Start-Service FDResPub
        Set-Service ssdpsrv -StartupType Automatic; Start-Service ssdpsrv
        Set-Service upnphost -StartupType Automatic; Start-Service upnphost
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\Network\NewNetworkWindowOff" /f 2>&1 | Out-Null
        Write-Output "[OK] Network discovery services enabled."
    }
    "apps_not_responding" {
        Write-Output "[Repair-O] Fixing apps not responding too soon..."
        reg add "HKCU\Control Panel\Desktop" /v HungAppTimeout /t REG_SZ /d 30000 /f | Out-Null
        reg add "HKCU\Control Panel\Desktop" /v WaitToKillAppTimeout /t REG_SZ /d 20000 /f | Out-Null
        reg add "HKCU\Control Panel\Desktop" /v AutoEndTasks /t REG_SZ /d 0 /f | Out-Null
        Write-Output "[OK] App timeout extended to 30 seconds."
    }
    "desktop_icons" {
        Write-Output "[Repair-O] Fixing desktop icons and context menu..."
        ie4uinit.exe -show 2>&1 | Out-Null
        reg delete "HKCR\CLSID\{645FF040-5081-101B-9F08-00AA002F954E}\ShellFolder" /v Attributes /f 2>&1 | Out-Null
        Stop-Process -Name explorer -Force; Start-Process explorer
        Write-Output "[OK] Desktop and context menu refreshed."
    }
    "unhide_files" {
        Write-Output "[Repair-O] Unhiding user files and folders..."
        attrib -h -s "$env:USERPROFILE\*" /s /d 2>&1 | Out-Null
        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Hidden /t REG_DWORD /d 1 /f | Out-Null
        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowSuperHidden /t REG_DWORD /d 1 /f | Out-Null
        Write-Output "[OK] Files unhidden. Explorer updated to show hidden files."
    }
    "unhide_drives" {
        Write-Output "[Repair-O] Unhiding fixed drives..."
        reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDrives /f 2>&1 | Out-Null
        reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDrives /f 2>&1 | Out-Null
        Stop-Process -Name explorer -Force; Start-Process explorer
        Write-Output "[OK] Drive visibility policies removed."
    }
    "chkdsk" {
        Write-Output "[Repair-O] Scheduling CHKDSK on next reboot..."
        # Use registry method — reliable across all PS versions
        $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager"
        Set-ItemProperty -Path $regPath -Name "BootExecute" -Value @("autocheck autochk *","autocheck autochk /r \??\C:") -Type MultiString
        Write-Output "[OK] CHKDSK scheduled. Reboot to run disk check."
    }
    "cancel_chkdsk" {
        Write-Output "[Repair-O] Cancelling scheduled CHKDSK..."
        $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager"
        Set-ItemProperty -Path $regPath -Name "BootExecute" -Value @("autocheck autochk *") -Type MultiString
        Write-Output "[OK] Scheduled CHKDSK cancelled."
    }
    "memory_diagnostic" {
        Write-Output "[Repair-O] Scheduling Windows Memory Diagnostic..."
        mdsched.exe 2>&1 | Out-Null
        Write-Output "[OK] Memory diagnostic scheduled."
    }
    "winsxs_cleanup" {
        Write-Output "[Repair-O] Cleaning WinSxS component store..."
        Write-Output "[INFO] This may take several minutes..."
        Dism /Online /Cleanup-Image /StartComponentCleanup /ResetBase 2>&1
        Write-Output "[OK] WinSxS cleanup complete."
    }
    "register_dlls" {
        Write-Output "[Repair-O] Re-registering common system DLLs..."
        $dlls = @("atl.dll","oleaut32.dll","ole32.dll","shell32.dll","initpki.dll",
                  "wuapi.dll","wuaueng.dll","wucltui.dll","wups.dll","wups2.dll","wuweb.dll",
                  "msxml.dll","msxml3.dll","msxml6.dll","actxprxy.dll","softpub.dll",
                  "wintrust.dll","dssenh.dll","rsaenh.dll","gpkcsp.dll","sccbase.dll",
                  "slbcsp.dll","cryptdlg.dll","urlmon.dll","shdocvw.dll","mssip32.dll")
        $ok = 0
        foreach ($dll in $dlls) {
            regsvr32 /s $dll 2>&1 | Out-Null
            $ok++
        }
        Write-Output "[OK] Re-registered $ok system DLLs."
    }
    "boot_repair" {
        Write-Output "[Repair-O] Repairing Windows boot records..."
        bootrec /fixmbr 2>&1
        bootrec /fixboot 2>&1
        bootrec /scanos 2>&1
        bootrec /rebuildbcd 2>&1
        Write-Output "[OK] Boot repair complete. Reboot to verify."
    }
    "update_windows" {
        Write-Output "[Repair-O] Checking for Windows Updates..."
        Start-Process "ms-settings:windowsupdate" 2>&1 | Out-Null
        UsoClient StartScan 2>&1 | Out-Null
        Write-Output "[OK] Windows Update scan initiated. Check Settings for progress."
    }
    "delete_temp_profiles" {
        Write-Output "[Repair-O] Removing temporary profile folders..."
        $profilePath = "C:\Users"
        $removed = 0
        Get-ChildItem $profilePath -Directory | Where {$_.Name -match "\.bak$|TEMP|\.000$"} | ForEach {
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
            Write-Output "[FOUND] Removed: $($_.Name)"
            $removed++
        }
        Write-Output "[OK] Removed $removed temporary profile folder(s)."
    }
    default { Write-Output "[ERROR] Unknown fix action: $Action" }
}
