# Repair-O - Rebuild Icon Cache
Write-Output "[Repair-O] Rebuilding icon and thumbnail cache..."
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$cachePaths = @(
    "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\iconcache*.db",
    "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\thumbcache*.db"
)
foreach ($pattern in $cachePaths) {
    Get-Item $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
        Write-Output "  [OK] Deleted: $($_.Name)"
    }
}
Start-Process explorer
Write-Output "[OK] Icon cache rebuilt. Explorer restarted."
