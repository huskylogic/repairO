# TechMedic — Master Feature Plan
# Version 1.0 Complete Specification

## TAB STRUCTURE
Tab 1: 🩺 Diagnose     — System Information (DONE v0.1)
Tab 2: 🦠 Triage       — Malware Removal
Tab 3: 🔧 Treat        — System Repairs
Tab 4: 🧰 Toolkit      — External Tools (auto-download)
Tab 5: 🚀 Run Queue    — Select tasks, Run All

---

## TAB 2: TRIAGE (Malware Removal)
All tasks are PowerShell scripts. Checkboxes. Run individually or queue.

### Built-in Tasks (native PowerShell)
[ ] Repair Safe Mode Services
    → Restore safe mode boot keys in registry
[ ] Registry Hive Backup
    → Export all major hives to Desktop\TechMedic_Backup\
[ ] Find Moved Shortcuts
    → Scan Desktop/Start Menu for broken shortcuts
[ ] Fix File Associations
    → Restore .exe, .bat, .reg, .lnk, .msi, .com, .vbs defaults
[ ] Remove Policies
    → Delete HKLM/HKCU Software\Policies\Microsoft keys
[ ] Clear Proxy Settings
    → WinHTTP proxy reset + IE proxy clear
[ ] Delete Temp Files
    → %TEMP%, C:\Windows\Temp, all user temp folders
[ ] Delete Temp Internet Files
    → IE/Edge/Chrome cache folders for all users
[ ] Clear System Restore
    → vssadmin delete shadows /all /quiet
[ ] Empty Recycle Bin
    → Clear-RecycleBin -Force -ErrorAction SilentlyContinue
[ ] Delete Pending File Rename Operations
    → Remove HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\PendingFileRenameOperations
[ ] Create System Restore Point
    → Checkpoint-Computer before any major changes
[ ] Windows Defender Quick Scan
    → Start-MpScan -ScanType QuickScan
[ ] Windows Defender Full Scan
    → Start-MpScan -ScanType FullScan

### External Tools (auto-downloaded to tools\)
[ ] McAfee Stinger (Trellix Stinger)
    URL: https://www.trellix.com/downloads/stinger/stinger64.exe
[ ] Kaspersky TDSSKiller
    URL: https://media.kaspersky.com/utilities/VirusUtilities/EN/tdsskiller.exe
[ ] Malwarebytes
    URL: https://downloads.malwarebytes.com/file/mb-windows
[ ] Autoruns (Sysinternals)
    URL: https://download.sysinternals.com/files/Autoruns.zip
[ ] KillEmAll
    URL: https://www.thecleaner.nl/files/killemall.zip
[ ] Ultra Adware Killer (Carifred)
    URL: https://www.carifred.com/ultra_adware_killer/UltraAdwareKiller.exe

---

## TAB 3: TREAT (System Repairs)

### Built-in PowerShell Repairs
[ ] DISM Scan Health
    → dism /online /cleanup-image /scanhealth
[ ] DISM Restore Health
    → dism /online /cleanup-image /restorehealth
[ ] System File Checker (SFC)
    → sfc /scannow
[ ] Re-Register Start Menu (All Users)
    → Get-AppxPackage -AllUsers *StartMenu* | Reset-AppxPackage
[ ] Reset OneDrive
    → %localappdata%\Microsoft\OneDrive\onedrive.exe /reset
[ ] Repair Permissions (icacls reset)
    → icacls C:\Windows /reset /t /c /q
[ ] Repair Windows Update
    → Stop services, clear cache, re-register DLLs, restart services
[ ] Repair WMI/WBEM
    → winmgmt /salvagerepository, re-register WMI DLLs
[ ] Repair DCOM
    → Re-register dcomcnfg DLLs
[ ] Repair Firewall
    → netsh advfirewall reset
[ ] Repair System Restore
    → Re-enable VSS service, reset config
[ ] Repair Security Center
    → Re-register wscsvc, restart service
[ ] Repair Windows Defender
    → Re-register defender DLLs, reset definitions
[ ] Repair Safe Mode Services
    → Restore safe boot registry entries
[ ] Rebuild Icon Cache
    → Delete iconcache.db, thumbnailcache files
[ ] Clear Print Spooler
    → Stop Spooler, delete C:\Windows\System32\spool\PRINTERS\*, start Spooler
[ ] Fix Device Manager
    → devmgmt.msc / scan for hardware changes via PowerShell
[ ] Clear Proxy Settings
    → netsh winhttp reset proxy + registry clear
[ ] Reset Network (All)
    → Full network stack reset (netsh int ip reset, winsock, firewall, etc.)
[ ] Release/Renew IP
    → ipconfig /release && ipconfig /renew
[ ] Reset Winsock
    → netsh winsock reset
[ ] Flush DNS
    → ipconfig /flushdns
[ ] Reset TCP/IP Stack
    → netsh int ip reset
[ ] Clear ARP Cache
    → arp -d *
[ ] Re-register System DLLs
    → Loop regsvr32 on common DLLs (ole32, oleaut32, jscript, vbscript, etc.)
[ ] Reset Internet Explorer/Edge Settings
    → Reset IE security zones, clear typed URLs
[ ] Repair Group Policy
    → gpupdate /force + secedit /configure defaults
[ ] Rebuild BCD (Boot Config)
    → bootrec /rebuildbcd, bootrec /fixmbr, bootrec /fixboot
[ ] Check Disk (Schedule CHKDSK)
    → chkdsk C: /f /r /x (schedule on next reboot)

### External Tool Repairs (auto-downloaded)
[ ] .NET Framework Repair Tool (Microsoft)
    URL: https://download.microsoft.com/download/...NetFxRepairTool.exe
[ ] Windows Repair AIO (Tweaking.com)
    URL: https://www.tweaking.com/files/setups/tweaking.com_windows_repair_aio.zip
[ ] Carifred Account Profile Fixer (APF)
    URL: https://www.carifred.com/apf/APF.exe
[ ] DISM++ (Chuyu Team)
    URL: https://github.com/Chuyu-Team/Dism-Multi-language/releases/latest

---

## TAB 4: TOOLKIT (External Tools, always available)

### Diagnostics / Analysis
[ ] Autoruns (Sysinternals)
[ ] Process Explorer (Sysinternals)
[ ] TCPView (Sysinternals)
[ ] HijackThis Fork
[ ] HWiNFO64
[ ] CrystalDiskInfo
[ ] MemTest86 (USB launcher)

### Malware Removal
[ ] McAfee Stinger / Trellix
[ ] Kaspersky TDSSKiller
[ ] Malwarebytes
[ ] Ultra Adware Killer
[ ] AdwCleaner (Malwarebytes)
[ ] KillEmAll
[ ] RKill

### System Utilities
[ ] DISM++
[ ] Windows Repair AIO
[ ] .NET Framework Repair Tool
[ ] Account Profile Fixer (APF)
[ ] Speccy (system info)
[ ] Recuva (file recovery)
[ ] CCleaner (optional)

### Network Tools
[ ] Wireshark
[ ] Nmap (portable)

---

## TAB 5: RUN QUEUE
- Select any tasks from Triage + Treat tabs
- "Run All" button executes them sequentially
- Progress bar per task + overall progress
- Live log output for each task
- Results summary: ✅ Done / ❌ Failed / ⏭ Skipped
- Option to export full run log

---

## TOOL DOWNLOADER (downloader.py)
- tools_manifest.json lists all tools with:
  - name, url, filename, version_url, checksum, launch_args
- Check if already downloaded (skip if present)
- Show download progress bar
- Verify file after download
- One "Update All Tools" button in Toolkit tab

---

## POWERSHELL SCRIPTS TO BUILD (scripts/)
system_info.ps1          ✅ DONE
repair_safemode.ps1
registry_backup.ps1
find_moved_shortcuts.ps1
fix_file_associations.ps1
remove_policies.ps1
clear_proxy.ps1
delete_temp_files.ps1
delete_temp_internet.ps1
clear_system_restore.ps1
empty_recycle_bin.ps1
delete_pending_renames.ps1
create_restore_point.ps1
defender_quick_scan.ps1
defender_full_scan.ps1
dism_scan.ps1
dism_restore.ps1
sfc_scan.ps1
reregister_startmenu.ps1
reset_onedrive.ps1
repair_permissions.ps1
repair_windows_update.ps1
repair_wmi.ps1
repair_firewall.ps1
repair_system_restore.ps1
repair_security_center.ps1
repair_defender.ps1
rebuild_icon_cache.ps1
clear_print_spooler.ps1
fix_device_manager.ps1
reset_network.ps1
release_renew_ip.ps1
reset_winsock.ps1
flush_dns.ps1
reset_tcpip.ps1
reregister_dlls.ps1
repair_group_policy.ps1
rebuild_bcd.ps1
schedule_chkdsk.ps1
