# Repair-O - Find Moved / Broken Shortcuts
Write-Output "[Repair-O] Scanning for broken shortcuts..."
$searchPaths = @(
    "$env:USERPROFILE\Desktop",
    "$env:PUBLIC\Desktop",
    "$env:APPDATA\Microsoft\Windows\Start Menu",
    "$env:ProgramData\Microsoft\Windows\Start Menu"
)
$broken = @()
foreach ($path in $searchPaths) {
    if (-not (Test-Path $path)) { continue }
    $shortcuts = Get-ChildItem -Path $path -Recurse -Filter "*.lnk" -ErrorAction SilentlyContinue
    foreach ($sc in $shortcuts) {
        try {
            $shell = New-Object -ComObject WScript.Shell
            $link  = $shell.CreateShortcut($sc.FullName)
            $target = $link.TargetPath
            if ($target -and -not (Test-Path $target)) {
                Write-Output "  [BROKEN] $($sc.Name) -> $target"
                $broken += $sc.FullName
            }
        } catch { }
    }
}
if ($broken.Count -eq 0) { Write-Output "[OK] No broken shortcuts found." }
else { Write-Output "[RESULT] Found $($broken.Count) broken shortcut(s). Review above." }
