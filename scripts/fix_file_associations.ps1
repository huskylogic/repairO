# Repair-O - Fix File Associations
Write-Output "[Repair-O] Restoring default file associations..."
$assocFixes = @{
    ".exe" = '"%1" %*'
    ".com" = '"%1" %*'
    ".bat" = '"%1" %*'
    ".cmd" = '"%1" %*'
    ".reg" = 'regedit.exe "%1"'
    ".msi" = 'msiexec /i "%1"'
    ".vbs" = 'wscript.exe "%1" %*'
    ".lnk" = ""
}
# Reset via ftype/assoc
cmd /c 'assoc .exe=exefile' 2>&1 | Write-Output
cmd /c 'ftype exefile="%1" %*' 2>&1 | Write-Output
cmd /c 'assoc .com=comfile' 2>&1 | Write-Output
cmd /c 'ftype comfile="%1" %*' 2>&1 | Write-Output
cmd /c 'assoc .bat=batfile' 2>&1 | Write-Output
cmd /c 'ftype batfile="%1" %*' 2>&1 | Write-Output
cmd /c 'assoc .cmd=cmdfile' 2>&1 | Write-Output
cmd /c 'ftype cmdfile="%1" %*' 2>&1 | Write-Output
cmd /c 'assoc .reg=regfile' 2>&1 | Write-Output
cmd /c 'ftype regfile=regedit.exe "%1"' 2>&1 | Write-Output
cmd /c 'assoc .msi=Msi.Package' 2>&1 | Write-Output
# Fix User Account Control IFEO key if present (malware hook)
$ifeoPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options"
$targets = @("taskmgr.exe","regedit.exe","cmd.exe")
foreach ($t in $targets) {
    $kp = "$ifeoPath\$t"
    if (Test-Path $kp) {
        $debugger = (Get-ItemProperty -Path $kp -ErrorAction SilentlyContinue).Debugger
        if ($debugger) {
            Remove-ItemProperty -Path $kp -Name "Debugger" -Force -ErrorAction SilentlyContinue
            Write-Output "  [FIX] Removed IFEO debugger hook on $t"
        }
    }
}
Write-Output "[OK] File associations restored."
