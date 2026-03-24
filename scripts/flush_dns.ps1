# Repair-O - Flush DNS
Write-Output "[Repair-O] Flushing DNS cache..."
ipconfig /flushdns
Clear-DnsClientCache -ErrorAction SilentlyContinue
Write-Output "[OK] DNS cache flushed."
