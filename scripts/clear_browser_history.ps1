# Repair-O - Clear Browser History
param([string]$Browser = "all")
$ErrorActionPreference = "SilentlyContinue"

function Clear-ChromeHistory {
    Write-Output "[Repair-O] Clearing Chrome history..."
    Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue; Start-Sleep 1
    $profiles = Get-ChildItem "$env:LOCALAPPDATA\Google\Chrome\User Data" -Directory | Where {$_.Name -match "^Default$|^Profile"}
    foreach ($p in $profiles) {
        Remove-Item "$($p.FullName)\History" -Force -ErrorAction SilentlyContinue
        Remove-Item "$($p.FullName)\History-journal" -Force -ErrorAction SilentlyContinue
        Remove-Item "$($p.FullName)\Cookies" -Force -ErrorAction SilentlyContinue
        Remove-Item "$($p.FullName)\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Output "[OK] Chrome history cleared."
}

function Clear-FirefoxHistory {
    Write-Output "[Repair-O] Clearing Firefox history..."
    Stop-Process -Name "firefox" -Force -ErrorAction SilentlyContinue; Start-Sleep 1
    Get-ChildItem "$env:APPDATA\Mozilla\Firefox\Profiles" -Directory | ForEach {
        Remove-Item "$($_.FullName)\places.sqlite" -Force -ErrorAction SilentlyContinue
        Remove-Item "$($_.FullName)\cookies.sqlite" -Force -ErrorAction SilentlyContinue
        Remove-Item "$($_.FullName)\cache2\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Output "[OK] Firefox history cleared."
}

function Clear-EdgeHistory {
    Write-Output "[Repair-O] Clearing Edge history..."
    Stop-Process -Name "msedge" -Force -ErrorAction SilentlyContinue; Start-Sleep 1
    $profiles = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Edge\User Data" -Directory | Where {$_.Name -match "^Default$|^Profile"}
    foreach ($p in $profiles) {
        Remove-Item "$($p.FullName)\History" -Force -ErrorAction SilentlyContinue
        Remove-Item "$($p.FullName)\Cookies" -Force -ErrorAction SilentlyContinue
        Remove-Item "$($p.FullName)\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Output "[OK] Edge history cleared."
}

function Clear-QuickAccess {
    Write-Output "[Repair-O] Clearing Quick Access and Jump Lists..."
    Remove-Item "$env:APPDATA\Microsoft\Windows\Recent\*" -Force -Recurse -ErrorAction SilentlyContinue
    Remove-Item "$env:APPDATA\Microsoft\Windows\Recent\AutomaticDestinations\*" -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:APPDATA\Microsoft\Windows\Recent\CustomDestinations\*" -Force -ErrorAction SilentlyContinue
    Write-Output "[OK] Quick Access and Jump Lists cleared."
}

switch ($Browser.ToLower()) {
    "chrome"       { Clear-ChromeHistory }
    "firefox"      { Clear-FirefoxHistory }
    "edge"         { Clear-EdgeHistory }
    "quickaccess"  { Clear-QuickAccess }
    "all"          { Clear-ChromeHistory; Clear-FirefoxHistory; Clear-EdgeHistory; Clear-QuickAccess }
}
