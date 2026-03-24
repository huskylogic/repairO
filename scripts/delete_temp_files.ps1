# Repair-O - Delete Temp Files
Write-Output "[Repair-O] Deleting temporary files..."
$paths = @(
    $env:TEMP,
    "$env:WINDIR\Temp",
    "$env:WINDIR\Prefetch",
    "$env:LOCALAPPDATA\Temp"
)
$total = 0
foreach ($path in $paths) {
    if (Test-Path $path) {
        $files = Get-ChildItem -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        $size = ($files | Measure-Object -Property Length -Sum).Sum
        Get-ChildItem -Path $path -Force -ErrorAction SilentlyContinue |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        $total += [math]::Round($size / 1MB, 1)
        Write-Output "  [OK] Cleaned: $path ($([math]::Round($size/1MB,1)) MB)"
    }
}
# Clean all user temp folders
$userProfiles = Get-ChildItem "C:\Users" -Directory -ErrorAction SilentlyContinue
foreach ($user in $userProfiles) {
    $ut = "$($user.FullName)\AppData\Local\Temp"
    if (Test-Path $ut) {
        $size = (Get-ChildItem $ut -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Get-ChildItem $ut -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Write-Output "  [OK] Cleaned: $ut ($([math]::Round($size/1MB,1)) MB)"
    }
}
Write-Output "[OK] Temp file cleanup complete. ~$total MB freed."
