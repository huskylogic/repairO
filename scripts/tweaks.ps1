# Repair-O - System Tweaks
param([string]$Action = "")
$ErrorActionPreference = "SilentlyContinue"

Write-Output "[Repair-O] Applying tweak: $Action"

switch ($Action) {
    "disable_startup_delay" {
        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize" /v StartupDelayInMSec /t REG_DWORD /d 0 /f | Out-Null
        Write-Output "[OK] Startup delay disabled."
    }
    "optimize_prefetch" {
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v EnablePrefetcher /t REG_DWORD /d 3 /f | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v EnableSuperfetch /t REG_DWORD /d 3 /f | Out-Null
        Write-Output "[OK] Prefetch optimized for faster startup."
    }
    "faster_shutdown" {
        reg add "HKCU\Control Panel\Desktop" /v WaitToKillAppTimeout /t REG_SZ /d 2000 /f | Out-Null
        reg add "HKCU\Control Panel\Desktop" /v HungAppTimeout /t REG_SZ /d 2000 /f | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Control" /v WaitToKillServiceTimeout /t REG_SZ /d 2000 /f | Out-Null
        Write-Output "[OK] Shutdown wait time reduced to 2 seconds."
    }
    "disable_animations" {
        reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f | Out-Null
        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f | Out-Null
        Write-Output "[OK] Window animations disabled. Log off and back on to take effect."
    }
    "optimize_menus" {
        reg add "HKCU\Control Panel\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f | Out-Null
        reg add "HKCU\Control Panel\Desktop" /v DragFullWindows /t REG_SZ /d 0 /f | Out-Null
        Write-Output "[OK] Menu delay removed."
    }
    "optimize_file_listings" {
        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v NtfsDisableLastAccessUpdate /t REG_DWORD /d 1 /f | Out-Null
        Write-Output "[OK] File listing optimized."
    }
    "increase_icon_cache" {
        reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer" /v "Max Cached Icons" /t REG_SZ /d 4096 /f | Out-Null
        Write-Output "[OK] Icon cache size increased to 4096."
    }
    "foreground_responsiveness" {
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 38 /f | Out-Null
        Write-Output "[OK] Foreground app priority boosted."
    }
    "disable_store_background" {
        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f | Out-Null
        Write-Output "[OK] Background Store apps disabled."
    }
    "disable_error_reporting" {
        reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting" /v Disabled /t REG_DWORD /d 1 /f | Out-Null
        Stop-Service WerSvc -Force -ErrorAction SilentlyContinue
        Set-Service WerSvc -StartupType Disabled -ErrorAction SilentlyContinue
        Write-Output "[OK] Error reporting disabled. WerFault.exe CPU spikes stopped."
    }
    "optimize_cpu_foreground" {
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 26 /f | Out-Null
        Write-Output "[OK] CPU optimized for foreground apps."
    }
    "prevent_default_app_reset" {
        reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v DefaultAssociationsConfiguration /t REG_SZ /d "" /f | Out-Null
        Write-Output "[OK] Default app reset prevention applied."
    }
    "optimize_dns_cache" {
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v CacheHashTableBucketSize /t REG_DWORD /d 1 /f | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v CacheHashTableSize /t REG_DWORD /d 384 /f | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v MaxCacheEntryTtlLimit /t REG_DWORD /d 64000 /f | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters" /v MaxSOACacheEntryTtlLimit /t REG_DWORD /d 301 /f | Out-Null
        Restart-Service Dnscache -ErrorAction SilentlyContinue
        Write-Output "[OK] DNS cache optimized."
    }
    "optimize_tcpip" {
        netsh int tcp set global autotuninglevel=normal 2>&1 | Out-Null
        netsh int tcp set global ecncapability=enabled 2>&1 | Out-Null
        Write-Output "[OK] TCP/IP optimized."
    }
    "optimize_lan" {
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" /v DisableBandwidthThrottling /t REG_DWORD /d 1 /f | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" /v FileInfoCacheEntriesMax /t REG_DWORD /d 1024 /f | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" /v DirectoryCacheEntriesMax /t REG_DWORD /d 1024 /f | Out-Null
        Write-Output "[OK] LAN settings optimized."
    }
    default {
        Write-Output "[ERROR] Unknown tweak action: '$Action'"
        Write-Output "[INFO] Check that the tweak ID is correct in the task list."
    }
}
