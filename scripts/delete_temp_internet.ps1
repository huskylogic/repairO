# Repair-O - Delete Temp Internet Files
Write-Output "[Repair-O] Clearing browser/internet cache..."
# IE/Edge Legacy
$iePaths = @(
    "$env:LOCALAPPDATA\Microsoft\Windows\INetCache",
    "$env:LOCALAPPDATA\Microsoft\Windows\Temporary Internet Files",
    "$env:LOCALAPPDATA\Microsoft\Windows\WebCache"
)
foreach ($p in $iePaths) {
    if (Test-Path $p) {
        Remove-Item "$p\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Output "  [OK] Cleared: $p"
    }
}
# Edge (Chromium)
$edgeCache = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache"
if (Test-Path $edgeCache) {
    Remove-Item "$edgeCache\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Output "  [OK] Cleared Edge cache"
}
# Chrome
$chromeCache = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"
if (Test-Path $chromeCache) {
    Remove-Item "$chromeCache\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Output "  [OK] Cleared Chrome cache"
}
# Firefox
$ffPath = "$env:APPDATA\Mozilla\Firefox\Profiles"
if (Test-Path $ffPath) {
    Get-ChildItem "$ffPath\*\cache2" -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Output "  [OK] Cleared Firefox cache"
}
Write-Output "[OK] Internet temp files cleared."
