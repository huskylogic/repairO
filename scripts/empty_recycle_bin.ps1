# Repair-O - Empty Recycle Bin
Write-Output "[Repair-O] Emptying Recycle Bin for all users..."
try {
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue
    Write-Output "[OK] Recycle Bin emptied."
} catch {
    # Fallback for older PS versions
    $shell = New-Object -ComObject Shell.Application
    $bin = $shell.Namespace(0xA)
    $bin.Items() | ForEach-Object { Remove-Item $_.Path -Recurse -Force -ErrorAction SilentlyContinue }
    Write-Output "[OK] Recycle Bin emptied (fallback method)."
}
