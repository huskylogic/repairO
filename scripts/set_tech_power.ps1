# Repair-O - Set Technician Power Settings (prevent sleep during repairs)
Write-Output "[Repair-O] Setting technician power plan..."
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 0
powercfg /change hibernate-timeout-ac 0
Write-Output "[OK] Power settings configured:"
Write-Output "[OK] Sleep: Never | Monitor off: Never | Hibernate: Never"
Write-Output "[INFO] These settings prevent the PC from sleeping during long repair tasks."
Write-Output "[INFO] Restore normal power settings when done with repairs."
