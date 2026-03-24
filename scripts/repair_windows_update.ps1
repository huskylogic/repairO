# Repair-O - Repair Windows Update
Write-Output "[Repair-O] Repairing Windows Update..."
$services = @("wuauserv","cryptsvc","bits","msiserver")
foreach ($svc in $services) { Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue; Write-Output "  Stopped: $svc" }
Write-Output "  Renaming SoftwareDistribution and Catroot2..."
Rename-Item "$env:WINDIR\SoftwareDistribution"      "SoftwareDistribution.bak" -Force -ErrorAction SilentlyContinue
Rename-Item "$env:WINDIR\System32\catroot2"          "catroot2.bak"             -Force -ErrorAction SilentlyContinue
Write-Output "  Re-registering update DLLs..."
$dlls = @("atl.dll","urlmon.dll","mshtml.dll","shdocvw.dll","browseui.dll","jscript.dll",
          "vbscript.dll","scrrun.dll","msxml.dll","msxml3.dll","msxml6.dll","actxprxy.dll",
          "softpub.dll","wintrust.dll","dssenh.dll","rsaenh.dll","gpkcsp.dll","sccbase.dll",
          "slbcsp.dll","cryptdlg.dll","oleaut32.dll","ole32.dll","shell32.dll",
          "initpki.dll","wuapi.dll","wuaueng.dll","wuaueng1.dll","wucltui.dll","wups.dll",
          "wups2.dll","wuweb.dll","qmgr.dll","qmgrprxy.dll","wucltux.dll","muweb.dll","wuwebv.dll")
foreach ($dll in $dlls) {
    regsvr32 /s $dll 2>&1 | Out-Null
}
netsh winsock reset | Out-Null
netsh winhttp reset proxy | Out-Null
foreach ($svc in $services) { Start-Service -Name $svc -ErrorAction SilentlyContinue; Write-Output "  Started: $svc" }
Write-Output "[OK] Windows Update repair complete."
