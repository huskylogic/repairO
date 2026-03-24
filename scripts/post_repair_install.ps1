# Repair-O - Post-Repair Essential Installs via winget
param([string]$App = "")
$ErrorActionPreference = "SilentlyContinue"

function Install-App($id, $name) {
    Write-Output "[Repair-O] Installing/Updating: $name..."
    $result = winget install --id $id --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq -1978335189) {
        Write-Output "[OK] $name installed/updated."
    } else {
        Write-Output "[WARN] $name may have had issues. Exit: $LASTEXITCODE"
    }
}

switch ($App) {
    "chrome"   { Install-App "Google.Chrome" "Google Chrome" }
    "firefox"  { Install-App "Mozilla.Firefox" "Mozilla Firefox" }
    "7zip"     { Install-App "7zip.7zip" "7-Zip" }
    "vcredist" {
        Write-Output "[Repair-O] Installing Visual C++ Runtimes..."
        Install-App "Microsoft.VCRedist.2005.x86" "VC++ 2005 x86"
        Install-App "Microsoft.VCRedist.2008.x86" "VC++ 2008 x86"
        Install-App "Microsoft.VCRedist.2010.x86" "VC++ 2010 x86"
        Install-App "Microsoft.VCRedist.2012.x86" "VC++ 2012 x86"
        Install-App "Microsoft.VCRedist.2013.x86" "VC++ 2013 x86"
        Install-App "Microsoft.VCRedist.2015+.x86" "VC++ 2015-2022 x86"
        Install-App "Microsoft.VCRedist.2015+.x64" "VC++ 2015-2022 x64"
    }
    "dotnet"   { Install-App "Microsoft.DotNet.DesktopRuntime.8" ".NET 8 Desktop Runtime" }
    "directx"  {
        Write-Output "[Repair-O] Installing DirectX End-User Runtime..."
        Install-App "Microsoft.DirectX" "DirectX Runtime"
    }
    "all" {
        Install-App "Google.Chrome" "Google Chrome"
        Install-App "Mozilla.Firefox" "Mozilla Firefox"
        Install-App "7zip.7zip" "7-Zip"
        Install-App "Microsoft.VCRedist.2015+.x86" "VC++ 2015-2022 x86"
        Install-App "Microsoft.VCRedist.2015+.x64" "VC++ 2015-2022 x64"
        Install-App "Microsoft.DotNet.DesktopRuntime.8" ".NET 8 Runtime"
    }
    default { Write-Output "[ERROR] Unknown app: $App" }
}
