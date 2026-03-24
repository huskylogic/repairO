# ⚕ TechMedic
### Professional PC Repair Toolkit — Portable Edition

TechMedic is a Windows-based IT technician toolkit combining a Python PyQt5 GUI
with PowerShell backend scripts to diagnose, clean, and repair Windows systems.
No installation required — runs directly from a USB drive.

---

## 🚀 Running TechMedic

### Option A: Run as portable EXE (recommended)
1. Copy the `TechMedic\` folder to any location (USB drive, Desktop, etc.)
2. Right-click `TechMedic.exe` → **Run as Administrator**
3. That's it. No install, no Python needed.

### Option B: Run from Python source (for development)
1. Install Python 3.9+ from python.org (check "Add Python to PATH")
2. Double-click `run_TechMedic.bat` (installs deps and launches)

---

## 🔨 Building the EXE

### First time setup:
```
Double-click build.bat
```
That's it. It will:
- Install Python dependencies (PyInstaller, PyQt5, etc.)
- Bundle everything into `dist\TechMedic\TechMedic.exe`
- Takes ~60-120 seconds

### After making changes:
```
Edit main.py or any scripts\*.ps1 file
Double-click build.bat again
New exe appears in dist\TechMedic\
```

### Creating a shareable ZIP:
```
Double-click make_zip.bat
Creates TechMedic_v1.0_Portable_YYYYMMDD.zip
```

---

## 📁 Folder Structure

```
TechMedic\                      ← Keep this whole folder on your USB
│
├── TechMedic.exe               ← Launch this (run as Admin)
├── tools\                      ← External tools download here automatically
│   ├── stinger\
│   ├── tdsskiller\
│   ├── malwarebytes\
│   └── ...
├── logs\                       ← Run logs saved here
│
├── (internal - don't need to touch)
├── _internal\                  ← PyInstaller bundle internals
│   ├── scripts\                ← PowerShell scripts (bundled)
│   └── tools_manifest.json     ← Tool download URLs

── SOURCE FILES (for development) ──────────────────────────────
├── main.py                     ← Main Python GUI
├── downloader.py               ← Tool download manager
├── scripts\                    ← PowerShell scripts (source)
├── tools_manifest.json         ← Tool definitions and download URLs
├── TechMedic.spec              ← PyInstaller config
├── version_info.txt            ← EXE version metadata
├── build.bat                   ← One-click build script
└── make_zip.bat                ← Create portable ZIP for sharing
```

---

## ✏️ How to Add New Features

### Add a new PowerShell task:
1. Create `scripts\your_task.ps1`
2. Add a `Task(...)` entry to `TRIAGE_TASKS` or `TREAT_TASKS` in `main.py`
3. Run `build.bat` to rebuild

### Add a new external tool:
1. Add an entry to `tools_manifest.json` with the download URL
2. Add a `Task(task_type="tool", tool_id="your_tool_id")` entry
3. Run `build.bat` to rebuild

---

## 🩺 Features

### Tab 1: Diagnose
- Full system vitals: OS, CPU, RAM, Disk, GPU, Network, Security, Updates
- Export full report to Desktop as .txt

### Tab 2: Triage (Malware Removal)
- Create System Restore Point
- Registry Hive Backup
- Repair Safe Mode Services
- Find Broken Shortcuts
- Fix File Associations (.exe, .bat, .reg, .lnk, .msi, .com, .vbs)
- Remove Malware Policies
- Clear Proxy Settings
- Delete Temp Files (all users)
- Delete Temp Internet Files (IE/Edge/Chrome/Firefox)
- Clear System Restore Points
- Empty Recycle Bin
- Delete Pending File Rename Operations
- Windows Defender Quick Scan + Full Scan
- External tools: Stinger, TDSSKiller, Malwarebytes, Autoruns, KillEmAll, AdwCleaner, RKill

### Tab 3: Treat (System Repairs)
- SFC /scannow, DISM Scan + Restore Health
- Re-Register Start Menu (All Users)
- Reset OneDrive, Repair Permissions
- Repair Windows Update, WMI/WBEM/DCOM, Firewall
- Repair System Restore, Security Center, Windows Defender
- Rebuild Icon Cache, Clear Print Spooler
- Fix Device Manager, Clear Proxy
- Full Network Reset, Release/Renew IP, Reset Winsock
- Flush DNS, Reset TCP/IP, Re-Register System DLLs
- Repair Group Policy, Rebuild BCD, Schedule CHKDSK
- External tools: .NET Repair, Windows Repair AIO, Account Profile Fixer, DISM++

### Tab 4: Toolkit
- One-click download + launch for all external tools
- Organized by category: Analysis, Malware Removal, Repair Tools

### Tab 5: Run Queue
- Add any tasks from Triage and Treat
- Drag to reorder
- "Run All" executes sequentially with live output
- Results summary: ✅/❌ per task
