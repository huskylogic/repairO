# Repair-O - Scan user profiles on a drive
param([string]$SourceDrive = "C:")
$ErrorActionPreference = "SilentlyContinue"

$usersPath = Join-Path $SourceDrive "Users"
if (-not (Test-Path $usersPath)) {
    Write-Output "[]"; exit 1
}

$skip = @("All Users","Default","Default User","Public","desktop.ini")
$users = Get-ChildItem $usersPath -Directory | Where-Object { $skip -notcontains $_.Name }

$results = foreach ($u in $users) {
    # Fast size estimate — only look one level deep at key folders.
    # A full recursive Get-ChildItem on a large profile can take several minutes.
    $sizeBytes = 0
    $keyFolders = @("Desktop","Documents","Downloads","Pictures","Videos","Music","AppData","Favorites","Contacts","Saved Games","OneDrive")
    foreach ($folder in $keyFolders) {
        $fp = Join-Path $u.FullName $folder
        if (Test-Path $fp) {
            try {
                # Shallow pass — immediate children only, no recursion
                $sizeBytes += (Get-ChildItem $fp -ErrorAction SilentlyContinue |
                    Measure-Object -Property Length -Sum).Sum
            } catch {}
        }
    }
    $sizeGB = [math]::Round($sizeBytes / 1GB, 1)

    [PSCustomObject]@{
        Name    = $u.Name
        Path    = $u.FullName
        SizeGB  = $sizeGB
        Folders = @(
            @{Name="Desktop";   Path=Join-Path $u.FullName "Desktop";           Exists=(Test-Path (Join-Path $u.FullName "Desktop"))},
            @{Name="Documents"; Path=Join-Path $u.FullName "Documents";         Exists=(Test-Path (Join-Path $u.FullName "Documents"))},
            @{Name="Downloads"; Path=Join-Path $u.FullName "Downloads";         Exists=(Test-Path (Join-Path $u.FullName "Downloads"))},
            @{Name="Pictures";  Path=Join-Path $u.FullName "Pictures";          Exists=(Test-Path (Join-Path $u.FullName "Pictures"))},
            @{Name="Videos";    Path=Join-Path $u.FullName "Videos";            Exists=(Test-Path (Join-Path $u.FullName "Videos"))},
            @{Name="Music";     Path=Join-Path $u.FullName "Music";             Exists=(Test-Path (Join-Path $u.FullName "Music"))},
            @{Name="AppData";   Path=Join-Path $u.FullName "AppData\Roaming";   Exists=(Test-Path (Join-Path $u.FullName "AppData\Roaming"))},
            @{Name="Favorites"; Path=Join-Path $u.FullName "Favorites";         Exists=(Test-Path (Join-Path $u.FullName "Favorites"))}
        )
    }
}

$results | ConvertTo-Json -Depth 5
