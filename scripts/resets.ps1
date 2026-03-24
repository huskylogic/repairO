# Repair-O - System Resets
param([string]$Action = "")
$ErrorActionPreference = "SilentlyContinue"

switch ($Action) {
    "dns" {
        Write-Output "[Repair-O] Resetting DNS cache..."
        ipconfig /flushdns 2>&1 | Out-Null
        Write-Output "[OK] DNS cache flushed."
    }
    "hosts" {
        Write-Output "[Repair-O] Resetting hosts file..."
        $default = "# Copyright (c) 1993-2009 Microsoft Corp.`n#`n# This is a sample HOSTS file`n`n127.0.0.1       localhost`n::1             localhost"
        Set-Content "C:\Windows\System32\drivers\etc\hosts" $default -Force
        ipconfig /flushdns 2>&1 | Out-Null
        Write-Output "[OK] Hosts file reset to default."
    }
    "ip_winsock" {
        Write-Output "[Repair-O] Resetting IP, Winsock and proxy..."
        netsh winsock reset 2>&1 | Out-Null
        netsh int ip reset 2>&1 | Out-Null
        netsh winhttp reset proxy 2>&1 | Out-Null
        ipconfig /release 2>&1 | Out-Null
        ipconfig /renew 2>&1 | Out-Null
        ipconfig /flushdns 2>&1 | Out-Null
        Write-Output "[OK] IP, Winsock and proxy reset. Reboot recommended."
    }
    "firewall" {
        Write-Output "[Repair-O] Resetting Windows Firewall..."
        netsh advfirewall reset 2>&1 | Out-Null
        Set-Service MpsSvc -StartupType Automatic
        Start-Service MpsSvc
        Write-Output "[OK] Firewall reset to defaults and restarted."
    }
    "print_spooler" {
        Write-Output "[Repair-O] Resetting print spooler..."
        Stop-Service Spooler -Force
        Remove-Item "C:\Windows\System32\spool\PRINTERS\*" -Force -Recurse -ErrorAction SilentlyContinue
        Start-Service Spooler
        Write-Output "[OK] Print spooler cleared and restarted."
    }
    "group_policy" {
        Write-Output "[Repair-O] Resetting group policies..."
        Remove-Item "C:\Windows\System32\GroupPolicy" -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item "C:\Windows\System32\GroupPolicyUsers" -Recurse -Force -ErrorAction SilentlyContinue
        gpupdate /force 2>&1 | Out-Null
        Write-Output "[OK] Group policies reset."
    }
    "windows_store" {
        Write-Output "[Repair-O] Resetting Windows Store..."
        wsreset.exe 2>&1 | Out-Null
        Get-AppxPackage -AllUsers Microsoft.WindowsStore | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml" -ErrorAction SilentlyContinue}
        Write-Output "[OK] Windows Store reset."
    }
    "wlan" {
        Write-Output "[Repair-O] Resetting WLAN profiles..."
        # Use XML output for language-independent profile name extraction
        $profileNames = @()
        try {
            [xml]$wlanXml = netsh wlan show profiles xml 2>&1
            $profileNames = $wlanXml.SelectNodes("//name") | ForEach-Object { $_.InnerText }
        } catch {
            # Fallback: parse text output looking for the colon-separated name on any line with a profile
            $profileNames = netsh wlan show profiles 2>&1 |
                Where-Object { $_ -match ":\s*.+$" -and $_ -match "Profile" } |
                ForEach-Object { ($_ -split ":\s*",2)[1].Trim() } |
                Where-Object { $_ -ne "" }
        }
        $removed = 0
        foreach ($p in $profileNames) {
            netsh wlan delete profile name="$p" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { $removed++ }
        }
        netsh wlan reset 2>&1 | Out-Null
        Write-Output "[OK] $removed WLAN profile(s) removed and settings reset."
        if ($removed -eq 0) { Write-Output "[INFO] No profiles found or Wi-Fi adapter not present." }
    }
    "permissions" {
        Write-Output "[Repair-O] Resetting registry and file permissions..."
        secedit /configure /cfg "$env:windir\inf\defltbase.inf" /db defltbase.sdb /verbose 2>&1 | Out-Null
        Write-Output "[OK] Default permissions restored."
    }
    "user_shell_folders" {
        Write-Output "[Repair-O] Resetting user shell folders..."
        $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        $defaults = @{
            "Desktop"   = "%USERPROFILE%\Desktop"
            "Personal"  = "%USERPROFILE%\Documents"
            "{374DE290-123F-4565-9164-39C4925E467B}" = "%USERPROFILE%\Downloads"
            "My Pictures" = "%USERPROFILE%\Pictures"
            "My Music"  = "%USERPROFILE%\Music"
            "My Video"  = "%USERPROFILE%\Videos"
        }
        foreach ($k in $defaults.Keys) {
            Set-ItemProperty -Path $regPath -Name $k -Value $defaults[$k] -ErrorAction SilentlyContinue
        }
        Write-Output "[OK] Shell folders reset to defaults."
    }
    "numlock" {
        Write-Output "[Repair-O] Setting NumLock ON at logon..."
        reg add "HKCU\Control Panel\Keyboard" /v InitialKeyboardIndicators /t REG_SZ /d 2 /f | Out-Null
        reg add "HKEY_USERS\.DEFAULT\Control Panel\Keyboard" /v InitialKeyboardIndicators /t REG_SZ /d 2 /f | Out-Null
        Write-Output "[OK] NumLock will be ON at next logon."
    }
    "chrome" { & "$PSScriptRoot\reset_browser.ps1" -Browser chrome }
    "firefox" { & "$PSScriptRoot\reset_browser.ps1" -Browser firefox }
    "edge" { & "$PSScriptRoot\reset_browser.ps1" -Browser edge }
    default { Write-Output "[ERROR] Unknown reset action: $Action" }
}
