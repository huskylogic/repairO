# Repair-O - Restore user data from backup
param(
    [string]$BackupPath   = "",
    [string]$DestUser     = "",
    [string]$DestPath     = "",
    [switch]$SkipExisting
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output "[Repair-O] Restoring backup..."
Write-Output "[Repair-O] Source:      $BackupPath"
Write-Output "[Repair-O] Destination: $DestPath"
Write-Output "----------------------------------------------------"

if (-not (Test-Path $BackupPath)) {
    Write-Output "[ERROR] Backup folder not found: $BackupPath"; exit 1
}
if (-not (Test-Path $DestPath)) {
    Write-Output "[Repair-O] Creating destination profile folder..."
    New-Item -ItemType Directory -Path $DestPath -Force | Out-Null
}

$folders = Get-ChildItem $BackupPath -Directory
$totalCopied = 0

foreach ($folder in $folders) {
    $dst = Join-Path $DestPath $folder.Name
    Write-Output "[Repair-O] Restoring $($folder.Name)..."

    $args = @($folder.FullName, $dst, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/R:2", "/W:2")
    if ($SkipExisting) { $args += "/XN"; $args += "/XO" }

    & robocopy @args 2>&1 | Out-Null
    $exitCode = $LASTEXITCODE

    if ($exitCode -lt 8) {
        $count = (Get-ChildItem $dst -Recurse -File -ErrorAction SilentlyContinue).Count
        $totalCopied += $count
        Write-Output "[OK] $($folder.Name) — $count files restored"
    } else {
        Write-Output "[WARN] $($folder.Name) — robocopy exit $exitCode"
    }
}

Write-Output "----------------------------------------------------"
Write-Output "[OK] Restore complete! $totalCopied files restored."
Write-Output "[INFO] Files are now in: $DestPath"
