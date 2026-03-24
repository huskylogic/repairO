# Repair-O - Time Zone and Clock Tools
param([string]$Action = "", [string]$TimeZone = "")
$ErrorActionPreference = "SilentlyContinue"

switch ($Action) {
    "list_zones" {
        Get-TimeZone -ListAvailable | Select-Object Id, DisplayName, BaseUtcOffset | ConvertTo-Json -Depth 2
    }
    "get_current" {
        $tz  = Get-TimeZone
        $now = Get-Date
        [PSCustomObject]@{
            Id          = $tz.Id
            DisplayName = $tz.DisplayName
            Offset      = $tz.BaseUtcOffset.ToString()
            LocalTime   = $now.ToString("yyyy-MM-dd HH:mm:ss")
            UTCTime     = $now.ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss")
        } | ConvertTo-Json
    }
    "set_zone" {
        if (-not $TimeZone) { Write-Output "[ERROR] No time zone specified."; exit 1 }
        try {
            Set-TimeZone -Id $TimeZone -ErrorAction Stop
            Write-Output "[OK] Time zone set to: $((Get-TimeZone).DisplayName)"
        } catch {
            Write-Output "[ERROR] Could not set time zone: $_"
            Write-Output "[TIP] Run Repair-O as Administrator."
            exit 1
        }
    }
    "sync_now" {
        Write-Output "[Repair-O] Syncing system clock..."
        $svc = Get-Service w32tm -ErrorAction SilentlyContinue
        if ($svc -and $svc.Status -ne "Running") { Start-Service w32tm -ErrorAction SilentlyContinue; Start-Sleep 1 }
        $r = & w32tm /resync /force 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Output "[OK] Clock synced. Current time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        } else {
            Write-Output "[WARN] Sync result: $r"
            Write-Output "[TIP] Check internet connection."
        }
    }
    "enable_autosync" {
        Write-Output "[Repair-O] Enabling automatic time synchronisation..."
        Set-Service w32tm -StartupType Automatic -ErrorAction SilentlyContinue
        Start-Service w32tm -ErrorAction SilentlyContinue
        & w32tm /config /manualpeerlist:"time.windows.com,0x9 pool.ntp.org,0x9" /syncfromflags:manual /reliable:YES /update 2>&1 | Out-Null
        & w32tm /resync /force 2>&1 | Out-Null
        reg add "HKLM\SYSTEM\CurrentControlSet\Services\W32Time\Parameters" /v Type /t REG_SZ /d NTP /f | Out-Null
        Write-Output "[OK] Auto time sync enabled (time.windows.com + pool.ntp.org)"
        Write-Output "     Current time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }
    default { Write-Output "[ERROR] Unknown action: $Action" }
}
