# Repair-O - BSOD and Crash Diagnostic Tweaks
param([string]$Action = "")
$ErrorActionPreference = "SilentlyContinue"

$crashKey = "HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl"

switch ($Action) {
    "disable_autoreboot" {
        Write-Output "[Repair-O] Disabling automatic reboot on BSOD..."
        Set-ItemProperty -Path $crashKey -Name "AutoReboot" -Value 0 -Type DWord
        Write-Output "[OK] Auto-reboot disabled. The BSOD screen will stay visible until manually rebooted."
        Write-Output "[INFO] This lets you read the stop code and note the failing module."
    }
    "enable_autoreboot" {
        Write-Output "[Repair-O] Re-enabling automatic reboot on BSOD..."
        Set-ItemProperty -Path $crashKey -Name "AutoReboot" -Value 1 -Type DWord
        Write-Output "[OK] Auto-reboot re-enabled (Windows default)."
    }
    "enable_minidumps" {
        Write-Output "[Repair-O] Enabling minidump creation on BSOD..."
        # CrashDumpEnabled: 0=None, 1=Complete, 2=Kernel, 3=Small(minidump), 7=Automatic
        Set-ItemProperty -Path $crashKey -Name "CrashDumpEnabled"  -Value 3 -Type DWord
        Set-ItemProperty -Path $crashKey -Name "MinidumpDir"       -Value "%SystemRoot%\Minidump" -Type ExpandString
        Set-ItemProperty -Path $crashKey -Name "LogEvent"          -Value 1 -Type DWord
        # Make sure the Minidump folder exists
        $dumpDir = "$env:SystemRoot\Minidump"
        if (-not (Test-Path $dumpDir)) {
            New-Item -ItemType Directory -Path $dumpDir -Force | Out-Null
        }
        Write-Output "[OK] Minidump enabled. Crash dumps saved to: $dumpDir"
        Write-Output "[INFO] Use WinDbg or WhoCrashed to analyse dump files."
    }
    "disable_minidumps" {
        Write-Output "[Repair-O] Disabling crash dump creation..."
        Set-ItemProperty -Path $crashKey -Name "CrashDumpEnabled" -Value 0 -Type DWord
        Write-Output "[OK] Crash dump creation disabled."
    }
    "enable_classic_bsod" {
        Write-Output "[Repair-O] Enabling classic (legacy) BSOD style..."
        # On Win10/11 this restores the older text-heavy BSOD vs the minimal smiley-face screen
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\CrashControl" /v DisplayParameters /t REG_DWORD /d 1 /f | Out-Null
        Write-Output "[OK] Classic BSOD style enabled."
        Write-Output "[INFO] Takes effect on next crash."
    }
    "check_dumps" {
        Write-Output "[Repair-O] Checking for existing crash dump files..."
        $dumpDir = "$env:SystemRoot\Minidump"
        $dumps   = Get-ChildItem $dumpDir -Filter "*.dmp" -ErrorAction SilentlyContinue
        if ($null -ne $dumps -and @($dumps).Count -gt 0) {
            Write-Output "[FOUND] $(@($dumps).Count) minidump file(s):"
            foreach ($d in $dumps) {
                Write-Output "  $($d.Name)  $([math]::Round($d.Length/1KB,0)) KB  $($d.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))"
            }
            Write-Output ""
            Write-Output "[INFO] Use WinDbg, WhoCrashed, or BlueScreenView to analyse these."
        } else {
            Write-Output "[OK] No minidump files found."
        }
        # Also check full dump
        $fullDump = "$env:SystemRoot\MEMORY.DMP"
        if (Test-Path $fullDump) {
            $sz = [math]::Round((Get-Item $fullDump).Length / 1GB, 1)
            Write-Output "[FOUND] Full memory dump: $fullDump ($sz GB)"
        }
    }
    default {
        Write-Output "[ERROR] Unknown action: $Action"
        Write-Output "[INFO] Valid: disable_autoreboot, enable_autoreboot, enable_minidumps, disable_minidumps, enable_classic_bsod, check_dumps"
    }
}
