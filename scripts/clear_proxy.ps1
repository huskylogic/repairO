# Repair-O - Clear Proxy Settings
Write-Output "[Repair-O] Clearing proxy settings..."
netsh winhttp reset proxy
Write-Output "[OK] WinHTTP proxy reset."
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
Set-ItemProperty -Path $regPath -Name "ProxyEnable" -Value 0 -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $regPath -Name "ProxyServer" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $regPath -Name "ProxyOverride" -ErrorAction SilentlyContinue
Write-Output "[OK] IE/Edge proxy settings cleared."
Set-ItemProperty -Path $regPath -Name "AutoConfigURL" -Value "" -ErrorAction SilentlyContinue
Write-Output "[OK] Proxy auto-config URL cleared."
Write-Output "[OK] All proxy settings cleared."
