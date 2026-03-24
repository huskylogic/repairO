# Repair-O - Backup user data
param(
    [string]$SourceUser = "",
    [string]$SourcePath = "",
    [string]$Destination = "",
    [string]$Folders = "Desktop,Documents,Downloads,Pictures,Videos,Music",
    [switch]$SkipHidden,
    [switch]$SkipSystem
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output "[Repair-O] Starting backup of: $SourceUser"
Write-Output "[Repair-O] Source:      $SourcePath"
Write-Output "[Repair-O] Destination: $Destination"
Write-Output "----------------------------------------------------"

if (-not (Test-Path $SourcePath)) {
    Write-Output "[ERROR] Source path not found: $SourcePath"; exit 1
}

$destRoot = Join-Path $Destination "RepairO_Backup_$SourceUser`_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $destRoot -Force | Out-Null
Write-Output "[OK] Backup folder created: $destRoot"

$folderList = $Folders -split ','
$totalCopied = 0
$totalErrors = 0

foreach ($folder in $folderList) {
    $src = Join-Path $SourcePath $folder.Trim()
    if (-not (Test-Path $src)) {
        Write-Output "[SKIP] Not found: $folder"
        continue
    }
    $dst = Join-Path $destRoot $folder.Trim()
    Write-Output "[Repair-O] Copying $folder..."

    $args = @($src, $dst, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/R:2", "/W:2")
    if ($SkipHidden)  { $args += "/XA:H" }
    if ($SkipSystem)  { $args += "/XA:S" }

    $result = & robocopy @args 2>&1
    $exitCode = $LASTEXITCODE

    # robocopy exit codes: 0-7 are success/warnings, 8+ are errors
    if ($exitCode -lt 8) {
        $count = (Get-ChildItem $dst -Recurse -File -ErrorAction SilentlyContinue).Count
        $totalCopied += $count
        Write-Output "[OK] $folder — $count files copied"
    } else {
        $totalErrors++
        Write-Output "[WARN] $folder — robocopy exit code $exitCode"
    }
}

# Save backup manifest
$manifest = @{
    User        = $SourceUser
    SourcePath  = $SourcePath
    BackupDate  = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    Folders     = $folderList
    BackupRoot  = $destRoot
}
$manifest | ConvertTo-Json | Out-File (Join-Path $destRoot "backup_manifest.json") -Encoding UTF8

Write-Output "----------------------------------------------------"
Write-Output "[OK] Backup complete!"
Write-Output "[OK] Total files copied: $totalCopied"
if ($totalErrors -gt 0) { Write-Output "[WARN] $totalErrors folder(s) had errors — check above." }
Write-Output "[INFO] Backup saved to: $destRoot"
Write-Output "[INFO] Keep this folder safe — you will need it to restore."
