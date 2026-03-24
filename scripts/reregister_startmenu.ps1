# Repair-O - Re-Register Start Menu for All Users
Write-Output "[Repair-O] Re-registering Start Menu for all users..."
Get-AppxPackage -AllUsers *StartMenuExperienceHost* | ForEach-Object {
    Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml" -ErrorAction SilentlyContinue
    Write-Output "  [OK] Re-registered: $($_.Name)"
}
Get-AppxPackage -AllUsers *ShellExperienceHost* | ForEach-Object {
    Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml" -ErrorAction SilentlyContinue
    Write-Output "  [OK] Re-registered: $($_.Name)"
}
Write-Output "[OK] Start Menu re-registration complete. May require sign-out/in."
