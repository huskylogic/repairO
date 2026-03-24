# Repair-O - Re-Register Common System DLLs
Write-Output "[Repair-O] Re-registering system DLLs..."
$dlls = @(
    "ole32.dll","oleaut32.dll","actxprxy.dll","comsvcs.dll","jscript.dll",
    "vbscript.dll","msxml.dll","msxml3.dll","msxml6.dll","browseui.dll",
    "shdocvw.dll","shell32.dll","urlmon.dll","mshtml.dll","wintrust.dll",
    "atl.dll","scrrun.dll","softpub.dll","initpki.dll","dssenh.dll","rsaenh.dll"
)
$ok     = 0
$failed = 0
foreach ($dll in $dlls) {
    regsvr32 /s $dll 2>&1 | Out-Null
    # regsvr32 /s exits 0 on success, non-zero on failure
    if ($LASTEXITCODE -eq 0) {
        Write-Output "  [OK] $dll"
        $ok++
    } else {
        Write-Output "  [SKIP] $dll (exit $LASTEXITCODE — not registerable or not present)"
        $failed++
    }
}
Write-Output ""
Write-Output "[OK] DLL re-registration complete: $ok succeeded, $failed skipped."
Write-Output "[INFO] Skipped DLLs are not necessarily broken — some don't support self-registration."
