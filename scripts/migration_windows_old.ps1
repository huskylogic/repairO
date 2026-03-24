# Repair-O - Scan Windows.old for recoverable user data
param([string]$Drive = "C:")

$ErrorActionPreference = "SilentlyContinue"
$winOld = Join-Path $Drive "Windows.old\Users"

if (-not (Test-Path $winOld)) {
    Write-Output "[ERROR] Windows.old not found on $Drive"
    Write-Output "[INFO] Windows.old is only present after an in-place Windows reinstall."
    Write-Output "[INFO] If you reinstalled by formatting, data may not be recoverable this way."
    exit 1
}

Write-Output "[OK] Windows.old found at: $winOld"
$skip = @("All Users","Default","Default User","Public","desktop.ini")
$users = Get-ChildItem $winOld -Directory | Where-Object { $skip -notcontains $_.Name }

Write-Output "[Repair-O] Found $($users.Count) user profile(s):"
foreach ($u in $users) {
    $size = 0
    try { $size = [math]::Round((Get-ChildItem $u.FullName -Recurse | Measure-Object Length -Sum).Sum / 1GB, 2) } catch {}
    Write-Output "  - $($u.Name)  (~$size GB)"
    $commonFolders = @("Desktop","Documents","Downloads","Pictures","Videos","Music")
    foreach ($f in $commonFolders) {
        $fp = Join-Path $u.FullName $f
        if (Test-Path $fp) {
            $count = (Get-ChildItem $fp -Recurse -File -ErrorAction SilentlyContinue).Count
            Write-Output "      $f : $count files"
        }
    }
}
Write-Output ""
Write-Output "[INFO] Use 'Recover from Windows.old' to copy these files to the current Windows profile."
$results = $users | Select-Object Name, FullName | ConvertTo-Json
Write-Output "USERS_JSON:$results"
