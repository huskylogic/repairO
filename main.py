"""
Repair-O v1.0 - Professional PC Repair Toolkit
Complete GUI with all tabs: Scan & Report, Fast Fixes, Fix & Repair, Tools, Run Tasks
"""

import sys
import os
import json
import subprocess
import threading
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QScrollArea, QFrame, QGroupBox, QGridLayout,
    QTextEdit, QPushButton, QCheckBox, QProgressBar, QSplitter,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QListWidget,
    QListWidgetItem, QAbstractItemView, QDialog, QMessageBox,
    QStackedWidget, QComboBox, QLineEdit, QFileDialog, QProgressDialog,
    QDialog, QInputDialog, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

# ─────────────────────────────────────────────
#  PATHS
#
#  When running as a PyInstaller .exe, sys._MEIPASS points to the
#  temporary extraction folder where bundled files are unpacked.
#  We use that for READ-ONLY assets (scripts, manifest, icon).
#
#  For WRITABLE data (downloaded tools, logs) we use the folder
#  where RepairO.exe actually lives — so the whole folder stays
#  portable and self-contained on a USB drive.
# ─────────────────────────────────────────────
import sys

def _bundle_dir():
    """Read-only bundle dir: where bundled assets live."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller exe — assets are in _MEIPASS
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def _portable_dir():
    """Writable portable dir: folder containing the exe (or script)."""
    if getattr(sys, "frozen", False):
        # sys.executable = path to RepairO.exe
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

BUNDLE_DIR  = _bundle_dir()
BASE_DIR    = _portable_dir()
SCRIPTS_DIR = os.path.join(BUNDLE_DIR, "scripts")   # read-only (bundled)
TOOLS_DIR   = os.path.join(BASE_DIR,   "tools")     # writable (portable folder)
LOGS_DIR    = os.path.join(BASE_DIR,   "logs")      # writable (portable folder)

for d in [TOOLS_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ─────────────────────────────────────────────
#  THEMES
# ─────────────────────────────────────────────
THEMES = {
    # ── Default (original blue/dark) ──────────────────────────────
    "Default": {
        "bg": "#13131f", "panel": "#1e1e30", "panel2": "#252538",
        "border": "#333355", "accent": "#38bdf8", "accent2": "#0ea5e9",
        "green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171",
        "text": "#e2e8f0", "muted": "#94a3b8",
        "triage": "#fb923c", "treat": "#a78bfa",
        "toolkit": "#34d399", "queue": "#f472b6",
        "maintain": "#fb923c", "tweaks": "#a78bfa",
    },
    # ── Cinder Scarlet (scarlet & gold on deep maroon) ────────────────
    "Cinder Scarlet": {
        "bg": "#0d0000", "panel": "#1a0000", "panel2": "#2a0a00",
        "border": "#740001", "accent": "#EEBA30", "accent2": "#D3A625",
        "green": "#4ade80", "yellow": "#EEBA30", "red": "#AE0001",
        "text": "#f5e6d0", "muted": "#b89060",
        "triage": "#EEBA30", "treat": "#AE0001",
        "toolkit": "#D3A625", "queue": "#AE0001",
        "maintain": "#EEBA30", "tweaks": "#D3A625",
    },
    # ── Abyssal Jade (emerald green & silver on near-black) ──────────
    "Abyssal Jade": {
        "bg": "#020a05", "panel": "#0a1a0f", "panel2": "#0f2318",
        "border": "#1A472A", "accent": "#2A623D", "accent2": "#1A472A",
        "green": "#2A623D", "yellow": "#AAAAAA", "red": "#c05050",
        "text": "#d8ead0", "muted": "#5D7A65",
        "triage": "#AAAAAA", "treat": "#2A623D",
        "toolkit": "#AAAAAA", "queue": "#2A623D",
        "maintain": "#2A623D", "tweaks": "#AAAAAA",
    },
    # ── Skystone Blue (midnight blue & bronze on near-black) ──────────
    "Skystone Blue": {
        "bg": "#02040a", "panel": "#070d1e", "panel2": "#0e1830",
        "border": "#0E1A40", "accent": "#946B2D", "accent2": "#222F5B",
        "green": "#4ade80", "yellow": "#946B2D", "red": "#f87171",
        "text": "#dce4f8", "muted": "#4a5a88",
        "triage": "#946B2D", "treat": "#4a70c0",
        "toolkit": "#946B2D", "queue": "#4a70c0",
        "maintain": "#4a70c0", "tweaks": "#946B2D",
    },
    # ── Harvest Gold (warm gold & black on dark brown) ──────────────
    "Harvest Gold": {
        "bg": "#080600", "panel": "#161200", "panel2": "#221c00",
        "border": "#372E29", "accent": "#ECB939", "accent2": "#D3A020",
        "green": "#4ade80", "yellow": "#ECB939", "red": "#f87171",
        "text": "#f0ead0", "muted": "#726255",
        "triage": "#ECB939", "treat": "#D3A020",
        "toolkit": "#ECB939", "queue": "#726255",
        "maintain": "#D3A020", "tweaks": "#ECB939",
    },
    # ── Midnight (deep purple/indigo, moody) ───────────────────────
    "Midnight": {
        "bg": "#0a0812", "panel": "#140f20", "panel2": "#1e1830",
        "border": "#3a2860", "accent": "#c084fc", "accent2": "#a855f7",
        "green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171",
        "text": "#ede9fe", "muted": "#8b7aa8",
        "triage": "#f472b6", "treat": "#c084fc",
        "toolkit": "#818cf8", "queue": "#f472b6",
        "maintain": "#c084fc", "tweaks": "#818cf8",
    },
    # ── Ember (warm orange/red on near-black) ──────────────────────
    "Ember": {
        "bg": "#0f0800", "panel": "#1e1000", "panel2": "#2a1800",
        "border": "#4a2800", "accent": "#f97316", "accent2": "#ea580c",
        "green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171",
        "text": "#fef3e8", "muted": "#a07050",
        "triage": "#f97316", "treat": "#fb923c",
        "toolkit": "#fbbf24", "queue": "#f97316",
        "maintain": "#fb923c", "tweaks": "#f97316",
    },
    # ── Arctic (icy cyan/white on near-black) ──────────────────────
    "Arctic": {
        "bg": "#050d12", "panel": "#0a1820", "panel2": "#0f2030",
        "border": "#1a3848", "accent": "#67e8f9", "accent2": "#22d3ee",
        "green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171",
        "text": "#e0f8ff", "muted": "#5a8a98",
        "triage": "#67e8f9", "treat": "#818cf8",
        "toolkit": "#22d3ee", "queue": "#f472b6",
        "maintain": "#67e8f9", "tweaks": "#818cf8",
    },
    # ── Stealth (muted greys, minimal color) ───────────────────────
    "Stealth": {
        "bg": "#0a0a0a", "panel": "#141414", "panel2": "#1e1e1e",
        "border": "#333333", "accent": "#aaaaaa", "accent2": "#888888",
        "green": "#6abf6a", "yellow": "#c8a840", "red": "#c06060",
        "text": "#cccccc", "muted": "#666666",
        "triage": "#aaaaaa", "treat": "#888888",
        "toolkit": "#aaaaaa", "queue": "#888888",
        "maintain": "#aaaaaa", "tweaks": "#888888",
    },
    # ── Light Mode (clean white/grey, blue accents) ──────────────
    "Light": {
        "bg": "#f0f2f5", "panel": "#ffffff", "panel2": "#e8eaed",
        "border": "#c8ccd2", "accent": "#1a73e8", "accent2": "#1558c0",
        "green": "#188038", "yellow": "#f29900", "red": "#c5221f",
        "text": "#202124", "muted": "#5f6368",
        "triage": "#e37400", "treat": "#7b1fa2",
        "toolkit": "#188038", "queue": "#c2185b",
        "maintain": "#e37400", "tweaks": "#7b1fa2",
    },
}

def _build_stylesheet(c):
    return f"""
* {{ font-family: 'Segoe UI', sans-serif; }}
QMainWindow, QDialog {{ background: {c['bg']}; color: {c['text']}; }}
QWidget {{ background: transparent; color: {c['text']}; font-size: 10pt; }}
QScrollArea {{ border: none; }}
QScrollBar:vertical {{ background: {c['bg']}; width: 7px; border-radius: 3px; }}
QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 3px; min-height: 20px; }}
QScrollBar::handle:vertical:hover {{ background: {c['accent']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QTabWidget::pane {{ border: 1px solid {c['border']}; background: {c['panel']}; border-radius: 0 6px 6px 6px; }}
QTabBar::tab {{ background: {c['bg']}; color: {c['muted']}; padding: 10px 22px; border: 1px solid {c['border']}; border-bottom: none; border-radius: 5px 5px 0 0; margin-right: 3px; font-weight: 600; }}
QTabBar::tab:selected {{ background: {c['panel']}; color: {c['accent']}; border-bottom: 3px solid {c['accent']}; }}
QTabBar::tab:hover:!selected {{ background: {c['panel2']}; color: {c['text']}; }}
QPushButton {{ background: {c['accent2']}; color: white; border: none; padding: 8px 16px; border-radius: 5px; font-weight: 600; }}
QPushButton:hover {{ background: {c['accent']}; color: {c['bg']}; }}
QPushButton:disabled {{ background: #2a2a40; color: #555; }}
QGroupBox {{ background: {c['panel2']}; border: 1px solid {c['border']}; border-radius: 7px; margin-top: 14px; padding: 12px 10px 10px 10px; font-weight: 700; color: {c['accent']}; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
QCheckBox {{ color: {c['text']}; spacing: 8px; padding: 3px 0; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 2px solid {c['border']}; border-radius: 3px; background: {c['bg']}; }}
QCheckBox::indicator:checked {{ background: {c['accent2']}; border-color: {c['accent']}; }}
QCheckBox:hover {{ color: {c['accent']}; }}
QTextEdit {{ background: {c['panel2']}; color: {c['text']}; border: 1px solid {c['border']}; border-radius: 4px; font-family: 'Consolas', monospace; font-size: 9pt; padding: 4px; }}
QProgressBar {{ background: {c['bg']}; border: 1px solid {c['border']}; border-radius: 5px; text-align: center; color: white; font-size: 8pt; height: 16px; }}
QProgressBar::chunk {{ background: {c['accent2']}; border-radius: 4px; }}
QTreeWidget {{ background: {c['panel2']}; border: 1px solid {c['border']}; border-radius: 4px; color: {c['text']}; alternate-background-color: {c['panel']}; }}
QTreeWidget::item {{ padding: 3px; }}
QTreeWidget::item:selected {{ background: {c['accent2']}; color: white; }}
QHeaderView::section {{ background: {c['bg']}; color: {c['accent']}; padding: 6px 8px; border: none; border-right: 1px solid {c['border']}; font-weight: 700; }}
QListWidget {{ background: {c['panel2']}; border: 1px solid {c['border']}; border-radius: 4px; color: {c['text']}; }}
QListWidget::item {{ padding: 6px; border-bottom: 1px solid {c['bg']}; }}
QListWidget::item:selected {{ background: {c['accent2']}; color: white; }}
QFrame#divider {{ background: {c['border']}; max-height: 1px; min-height: 1px; }}
"""

def _load_active_theme():
    """Load saved theme from prefs file, default to Default.
    Falls back to Default if the saved theme name no longer exists
    (e.g. after a rename like Ravenclaw -> Skystone Blue)."""
    try:
        prefs = os.path.join(os.path.expanduser("~"), ".repairo_prefs.json")
        if os.path.exists(prefs):
            import json as _j
            with open(prefs) as _f:
                saved = _j.load(_f).get("theme", "Default")
            if saved in THEMES:
                return saved
            # Saved theme no longer exists — migrate old names gracefully
            _migrations = {
                "Gryffindor": "Cinder Scarlet",
                "Slytherin":  "Abyssal Jade",
                "Ravenclaw":  "Skystone Blue",
                "Hufflepuff": "Harvest Gold",
            }
            if saved in _migrations and _migrations[saved] in THEMES:
                return _migrations[saved]
    except Exception:
        pass
    return "Default"

def _save_active_theme(name):
    try:
        prefs = os.path.join(os.path.expanduser("~"), ".repairo_prefs.json")
        import json as _j
        data = {}
        if os.path.exists(prefs):
            with open(prefs) as _f:
                data = _j.load(_f)
        data["theme"] = name
        with open(prefs, "w") as _f:
            _j.dump(data, _f)
    except Exception:
        pass

# Initialise C and STYLESHEET from saved/default theme
C = dict(THEMES[_load_active_theme()])

STYLESHEET = _build_stylesheet(C)

# ─────────────────────────────────────────────
#  TASK DEFINITION
# ─────────────────────────────────────────────
class Task:
    def __init__(self, task_id, name, description, category,
                 task_type="script", script=None, tool_id=None,
                 requires_reboot=False, script_args=None):
        self.task_id         = task_id
        self.name            = name
        self.description     = description
        self.category        = category
        self.task_type       = task_type
        self.script          = script
        self.tool_id         = tool_id
        self.requires_reboot = requires_reboot
        self.script_args     = script_args or []

    @property
    def script_path(self):
        return os.path.join(SCRIPTS_DIR, self.script) if self.script else None


# ─────────────────────────────────────────────
#  TASK REGISTRIES
# ─────────────────────────────────────────────
TRIAGE_TASKS = [
    Task("restore_point",   "Create System Restore Point",           "Creates a restore point before making changes",                "triage", script="create_restore_point.ps1"),
    Task("registry_backup", "Registry Hive Backup",                  "Exports all major registry hives to Desktop",                 "triage", script="registry_backup.ps1"),
    Task("safemode_repair", "Repair Safe Mode Services",             "Restores safe mode boot registry entries",                    "triage", script="repair_safemode.ps1"),
    Task("find_shortcuts",  "Find Moved Shortcuts",                  "Scans Desktop/Start Menu for broken shortcuts",               "triage", script="find_moved_shortcuts.ps1"),
    Task("fix_assoc",       "Fix File Associations",                 "Restores .exe, .bat, .reg, .lnk, .msi, .com, .vbs defaults", "triage", script="fix_file_associations.ps1"),
    Task("remove_policies", "Remove Policies",                       "Removes Software\\Policies\\Microsoft registry keys",         "triage", script="remove_policies.ps1"),
    Task("clear_proxy",     "Clear Proxy Settings",                  "Resets WinHTTP and IE proxy settings",                       "triage", script="clear_proxy.ps1"),
    Task("delete_temp",     "Delete Temp Files",                     "Clears %TEMP%, C:\\Windows\\Temp, all user temp folders",    "triage", script="delete_temp_files.ps1"),
    Task("delete_inet",     "Delete Temp Internet Files",            "Clears IE/Edge/Chrome cache for all users",                  "triage", script="delete_temp_internet.ps1"),
    Task("clear_restore",   "Clear System Restore Points",           "Deletes all shadow copies (vssadmin)",                       "triage", script="clear_system_restore.ps1"),
    Task("recycle_bin",     "Empty Recycle Bin",                     "Empties recycle bin for all users",                          "triage", script="empty_recycle_bin.ps1"),
    Task("del_pending",     "Delete Pending File Rename Operations", "Removes PendingFileRenameOperations registry key",            "triage", script="delete_pending_renames.ps1"),
    Task("defender_quick",  "Windows Defender Quick Scan",           "Runs a quick malware scan via Windows Defender",              "triage", script="defender_quick_scan.ps1"),
    Task("defender_full",   "Windows Defender Full Scan",            "Runs a full malware scan (may take hours)",                  "triage", script="defender_full_scan.ps1"),
    Task("stinger",         "McAfee Stinger (Trellix)",              "Targeted virus removal — auto-downloaded",                   "triage", task_type="tool", tool_id="stinger"),
    Task("tdsskiller",      "Kaspersky TDSSKiller",                  "Removes rootkits and bootkits — auto-downloaded",            "triage", task_type="tool", tool_id="tdsskiller"),
    Task("malwarebytes",    "Malwarebytes",                          "Full malware scanner — auto-downloaded",                     "triage", task_type="tool", tool_id="malwarebytes"),
    Task("autoruns",        "Autoruns (Sysinternals)",               "Manage all startup entries — auto-downloaded",               "triage", task_type="tool", tool_id="autoruns"),
    Task("killemall",       "KillEmAll",                             "Kills all non-essential processes — auto-downloaded",        "triage", task_type="tool", tool_id="killemall"),
    Task("adwcleaner",      "AdwCleaner",                            "Removes adware and PUPs — auto-downloaded",                  "triage", task_type="tool", tool_id="adwcleaner"),
    Task("rkill",           "RKill",                                 "Stops malicious processes — auto-downloaded",                "triage", task_type="tool", tool_id="rkill"),
    Task("roguekiller",     "RogueKiller",                           "Advanced malware and rootkit scanner — auto-downloaded",     "triage", task_type="tool", tool_id="roguekiller"),
    # Pre-repair
    Task("tech_power",      "Set Technician Power Settings",         "Prevents sleep/hibernate during long repair jobs",           "triage", script="set_tech_power.ps1"),
    Task("free_memory",     "Free Physical Memory",                  "Clears memory standby list to free up RAM",                  "triage", script="free_memory.ps1"),
    Task("enable_f8",       "Enable Legacy F8 Boot Menu",            "Re-enables F8 Advanced Boot Options at startup",             "triage", script="enable_f8_boot.ps1"),
]

TREAT_TASKS = [
    Task("sfc",             "System File Checker (SFC)",             "sfc /scannow — repairs protected system files",              "treat",  script="sfc_scan.ps1"),
    Task("dism_scan",       "DISM Scan Health",                      "Checks Windows image for corruption",                       "treat",  script="dism_scan.ps1"),
    Task("dism_restore",    "DISM Restore Health",                   "Downloads and repairs Windows image corruption",             "treat",  script="dism_restore.ps1"),
    Task("startmenu",       "Re-Register Start Menu (All Users)",    "Resets Start Menu for all user accounts",                   "treat",  script="reregister_startmenu.ps1"),
    Task("onedrive_reset",  "Reset OneDrive",                        "Resets and re-registers OneDrive client",                   "treat",  script="reset_onedrive.ps1"),
    Task("repair_perms",    "Repair Permissions (icacls)",           "Resets ACLs on Windows directory",                         "treat",  script="repair_permissions.ps1"),
    Task("repair_wu",       "Repair Windows Update",                 "Stops WU, clears cache, re-registers DLLs, restarts",      "treat",  script="repair_windows_update.ps1"),
    Task("repair_wmi",      "Repair WMI / WBEM / DCOM",             "Salvages WMI repository, re-registers WMI DLLs",           "treat",  script="repair_wmi.ps1"),
    Task("repair_fw",       "Repair Firewall",                       "netsh advfirewall reset to defaults",                       "treat",  script="repair_firewall.ps1"),
    Task("repair_sr",       "Repair System Restore",                 "Re-enables VSS service and resets config",                 "treat",  script="repair_system_restore.ps1"),
    Task("repair_sec",      "Repair Security Center",                "Re-registers and restarts Windows Security Center",         "treat",  script="repair_security_center.ps1"),
    Task("repair_def",      "Repair Windows Defender",               "Re-registers Defender DLLs, resets definitions",           "treat",  script="repair_defender.ps1"),
    Task("repair_sm2",      "Repair Safe Mode Services",             "Restores safe mode boot registry keys",                    "treat",  script="repair_safemode.ps1"),
    Task("icon_cache",      "Rebuild Icon Cache",                    "Deletes and rebuilds icon and thumbnail cache",             "treat",  script="rebuild_icon_cache.ps1"),
    Task("print_spooler",   "Clear Print Spooler",                   "Stops spooler, clears queue, restarts service",            "treat",  script="clear_print_spooler.ps1"),
    Task("device_mgr",      "Fix Device Manager",                    "Scans for hardware changes, re-enumerates devices",         "treat",  script="fix_device_manager.ps1"),
    Task("proxy_clear2",    "Clear Proxy Settings",                  "Clears proxy via netsh and registry",                      "treat",  script="clear_proxy.ps1"),
    Task("net_reset",       "Reset Network (Full)",                  "Full network stack reset",                                  "treat",  script="reset_network.ps1",    requires_reboot=True),
    Task("ip_renew",        "Release / Renew IP Address",            "ipconfig /release and /renew",                              "treat",  script="release_renew_ip.ps1"),
    Task("winsock",         "Reset Winsock",                         "netsh winsock reset",                                       "treat",  script="reset_winsock.ps1",    requires_reboot=True),
    Task("flush_dns",       "Flush DNS Cache",                       "ipconfig /flushdns",                                        "treat",  script="flush_dns.ps1"),
    Task("reset_tcpip",     "Reset TCP/IP Stack",                    "netsh int ip reset",                                        "treat",  script="reset_tcpip.ps1",      requires_reboot=True),
    Task("reg_dlls",        "Re-Register System DLLs",              "regsvr32 on common Windows DLLs",                           "treat",  script="reregister_dlls.ps1"),
    Task("group_policy",    "Repair Group Policy",                   "gpupdate /force and secedit defaults",                      "treat",  script="repair_group_policy.ps1"),
    Task("rebuild_bcd",     "Rebuild BCD / Boot Config",             "bootrec /rebuildbcd (boot repair)",                        "treat",  script="rebuild_bcd.ps1",      requires_reboot=True),
    Task("chkdsk",          "Schedule CHKDSK on Reboot",            "Schedules chkdsk C: /f /r for next reboot",                "treat",  script="schedule_chkdsk.ps1",  requires_reboot=True),
    Task("dotnet_repair",   ".NET Framework Repair Tool",            "Repairs broken .NET Framework installations",               "treat",  task_type="tool", tool_id="netframeworkrepair"),
    Task("winrepair",       "Windows Repair AIO (Tweaking.com)",     "All-in-one Windows repair suite",                          "treat",  task_type="tool", tool_id="windowsrepair"),
    Task("apf",             "Account Profile Fixer (Carifred)",      "Fixes corrupt Windows user profiles",                      "treat",  task_type="tool", tool_id="apf"),
    Task("dismpp",          "DISM++",                                "GUI-based DISM for advanced image management",              "treat",  task_type="tool", tool_id="dismpp"),
    # Resets
    Task("reset_hosts",     "Reset Hosts File",                      "Restores default hosts file, flushes DNS",                  "treat",  script="resets.ps1",  script_args=["-Action","hosts"]),
    Task("reset_ip_winsock","Reset IP, Winsock & Proxy",             "Full network stack reset — reboot required",                "treat",  script="resets.ps1",  script_args=["-Action","ip_winsock"], requires_reboot=True),
    Task("reset_firewall",  "Reset Windows Firewall",                "Resets firewall to defaults, restarts service",             "treat",  script="resets.ps1",  script_args=["-Action","firewall"]),
    Task("reset_spooler",   "Reset Print Spooler",                   "Clears stuck print queue, restarts spooler",               "treat",  script="resets.ps1",  script_args=["-Action","print_spooler"]),
    Task("reset_gp",        "Reset Group Policies",                  "Removes policy registry keys, runs gpupdate",               "treat",  script="resets.ps1",  script_args=["-Action","group_policy"]),
    Task("reset_store",     "Reset Windows Store",                   "Runs wsreset, re-registers Store app",                     "treat",  script="resets.ps1",  script_args=["-Action","windows_store"]),
    Task("reset_wlan",      "Reset WLAN Profiles",                   "Removes all WiFi profiles and resets settings",            "treat",  script="resets.ps1",  script_args=["-Action","wlan"]),
    Task("reset_chrome",    "Reset Chrome",                          "Resets Chrome settings and preferences",                   "treat",  script="resets.ps1",  script_args=["-Action","chrome"]),
    Task("reset_firefox",   "Reset Firefox",                         "Resets Firefox settings and preferences",                  "treat",  script="resets.ps1",  script_args=["-Action","firefox"]),
    Task("reset_edge",      "Reset Microsoft Edge",                  "Resets Edge settings and preferences",                    "treat",  script="resets.ps1",  script_args=["-Action","edge"]),
    Task("reset_perms",     "Reset Registry & File Permissions",     "Restores default security permissions",                    "treat",  script="resets.ps1",  script_args=["-Action","permissions"]),
    Task("reset_shell_fld", "Reset User Shell Folders",              "Restores default paths for Desktop/Documents/etc",        "treat",  script="resets.ps1",  script_args=["-Action","user_shell_folders"]),
    Task("reset_numlock",   "Set NumLock ON at Logon",               "Ensures NumLock is active at login screen",                "treat",  script="resets.ps1",  script_args=["-Action","numlock"]),
    # Common Fixes
    Task("fix_wmi2",        "Fix WMI & System Restore",             "Rebuilds WMI repository",                                  "treat",  script="fixes.ps1",   script_args=["-Action","wmi"]),
    Task("fix_installer",   "Fix Install Problems",                  "Re-registers Windows Installer service",                   "treat",  script="fixes.ps1",   script_args=["-Action","installer"]),
    Task("fix_exe_assoc",   "Fix Executable File Associations",      "Restores broken .exe file associations",                   "treat",  script="fixes.ps1",   script_args=["-Action","exe_associations"]),
    Task("fix_wu2",         "Fix & Enable Windows Update",           "Resets all Windows Update components",                    "treat",  script="fixes.ps1",   script_args=["-Action","windows_update"]),
    Task("fix_defender",    "Fix Microsoft Defender Services",       "Restores and re-enables Defender",                        "treat",  script="fixes.ps1",   script_args=["-Action","defender_services"]),
    Task("fix_store_apps",  "Fix Windows Store & Metro Apps",        "Re-registers all app packages",                           "treat",  script="fixes.ps1",   script_args=["-Action","store_apps"]),
    Task("fix_startmenu2",  "Fix & Repair Start Menu",               "Re-registers Start Menu and Shell Experience Host",       "treat",  script="fixes.ps1",   script_args=["-Action","start_menu"]),
    Task("fix_profiles",    "Fix Corrupted User Profiles",           "Scans for orphaned profile registry entries",             "treat",  script="fixes.ps1",   script_args=["-Action","user_profile"]),
    Task("fix_scheduler",   "Fix Task Scheduler",                    "Restarts Task Scheduler service",                         "treat",  script="fixes.ps1",   script_args=["-Action","task_scheduler"]),
    Task("fix_wifi_slow",   "Fix WiFi Slow to Connect",              "Removes WiFi delay registry settings",                    "treat",  script="fixes.ps1",   script_args=["-Action","wifi_slow"]),
    Task("fix_net_vis",     "Fix PC Not Visible on Network",         "Enables network discovery services",                      "treat",  script="fixes.ps1",   script_args=["-Action","network_visibility"]),
    Task("fix_app_resp",    "Fix Apps Not Responding Too Soon",      "Extends app response timeout to 30 seconds",              "treat",  script="fixes.ps1",   script_args=["-Action","apps_not_responding"]),
    Task("fix_desktop",     "Fix Desktop Icons & Context Menu",      "Refreshes icon cache and context menu",                   "treat",  script="fixes.ps1",   script_args=["-Action","desktop_icons"]),
    Task("fix_unhide",      "Unhide User Files & Folders",           "Removes hidden/system attributes from user files",        "treat",  script="fixes.ps1",   script_args=["-Action","unhide_files"]),
    Task("fix_drives",      "Unhide All Fixed Drives",               "Removes drive-hiding registry policies",                  "treat",  script="fixes.ps1",   script_args=["-Action","unhide_drives"]),
    Task("fix_chkdsk",      "Schedule CHKDSK on Reboot",            "Schedules disk check for next startup",                   "treat",  script="fixes.ps1",   script_args=["-Action","chkdsk"], requires_reboot=True),
    Task("fix_cancel_chk",  "Cancel Scheduled CHKDSK",              "Removes pending CHKDSK from boot sequence",               "treat",  script="fixes.ps1",   script_args=["-Action","cancel_chkdsk"]),
    Task("fix_mem_diag",    "Run Memory Diagnostics",                "Schedules Windows Memory Diagnostic on reboot",           "treat",  script="fixes.ps1",   script_args=["-Action","memory_diagnostic"], requires_reboot=True),
    Task("fix_winsxs",      "Clean Up WinSxS Folder",               "DISM StartComponentCleanup — frees significant space",    "treat",  script="fixes.ps1",   script_args=["-Action","winsxs_cleanup"]),
    Task("fix_reg_dlls",    "Register System DLLs",                  "regsvr32 on 25+ common Windows DLLs",                    "treat",  script="fixes.ps1",   script_args=["-Action","register_dlls"]),
    Task("fix_boot",        "Repair Windows Boot",                   "bootrec /fixmbr /fixboot /rebuildbcd",                    "treat",  script="fixes.ps1",   script_args=["-Action","boot_repair"], requires_reboot=True),
    Task("activate_bios",   "Activate Windows with BIOS Key",        "Extracts and applies embedded OEM product key",           "treat",  script="activate_windows_bios.ps1"),
    Task("repair_vss",      "Repair VSS Service",                    "Re-registers VSS providers — required for System Restore", "treat",  script="repair_vss.ps1"),
    Task("rebuild_search",  "Rebuild Windows Search Index",          "Deletes and rebuilds search index — fixes broken search",  "treat",  script="rebuild_search_index.ps1"),
]

TOOLKIT_GROUPS = [
    ("System Tools & Windows Built-ins", [
        Task("t_sysr",       "System Restore Manager",  "View, create, delete, and restore points",              "toolkit", task_type="builtin", tool_id="sysrestore"),
        Task("t_devmgr",     "Device Manager",          "Manage hardware devices",                               "toolkit", task_type="builtin", tool_id="devmgmt"),
        Task("t_diskpart",   "Disk Management",         "Manage partitions and drives",                          "toolkit", task_type="builtin", tool_id="diskmgmt"),
        Task("t_evtlog",     "Event Viewer",            "Browse system and application event logs",              "toolkit", task_type="builtin", tool_id="eventvwr"),
        Task("t_svcs",       "Services Manager",        "Start, stop, configure Windows services",               "toolkit", task_type="builtin", tool_id="services"),
        Task("t_regedit",    "Registry Editor",         "Browse and edit the Windows registry",                  "toolkit", task_type="builtin", tool_id="regedit"),
        Task("t_tasksch",    "Task Scheduler",          "View and manage scheduled tasks",                       "toolkit", task_type="builtin", tool_id="taskschd"),
        Task("t_gpedit",     "Group Policy Editor",     "Configure group policies (Pro/Enterprise only)",        "toolkit", task_type="builtin", tool_id="gpedit"),
        Task("t_perfmon",    "Performance Monitor",     "Real-time system performance counters",                 "toolkit", task_type="builtin", tool_id="perfmon"),
        Task("t_rsrmon",     "Resource Monitor",        "CPU, RAM, disk, network resource usage",                "toolkit", task_type="builtin", tool_id="resmon"),
        Task("t_sysconf",    "System Configuration",   "Boot options, startup, services (msconfig)",             "toolkit", task_type="builtin", tool_id="msconfig"),
        Task("t_sysinfo",    "System Information",      "Full hardware and software summary (msinfo32)",          "toolkit", task_type="builtin", tool_id="msinfo32"),
        Task("t_secpol",     "Security Policy Editor",  "Local security policy settings",                        "toolkit", task_type="builtin", tool_id="secpol"),
        Task("t_certmgr",    "Certificate Manager",     "View and manage Windows certificates",                  "toolkit", task_type="builtin", tool_id="certmgr"),
        Task("t_dxdiag",     "DirectX Diagnostic",      "DirectX info and display/audio diagnostics",            "toolkit", task_type="builtin", tool_id="dxdiag"),
    ]),
    ("Analysis Tools", [
        Task("t_autoruns",   "Autoruns",          "Sysinternals startup manager",          "toolkit", task_type="tool", tool_id="autoruns"),
        Task("t_procexp",    "Process Explorer",  "Advanced process manager",              "toolkit", task_type="tool", tool_id="procexp"),
        Task("t_tcpview",    "TCPView",           "Active network connections",             "toolkit", task_type="tool", tool_id="tcpview"),
        Task("t_hwinfo",     "HWiNFO64",          "Detailed hardware diagnostics",         "toolkit", task_type="tool", tool_id="hwinfo"),
        Task("t_diskinfo",   "CrystalDiskInfo",   "HDD/SSD S.M.A.R.T. health",            "toolkit", task_type="tool", tool_id="crystaldiskinfo"),
    ]),
    ("Hardware Info", [
        Task("t_cpuz",       "CPU-Z",             "Detailed CPU, RAM, and motherboard info","toolkit", task_type="tool", tool_id="cpuz"),
        Task("t_gpuz",       "GPU-Z",             "Detailed GPU information and sensors",  "toolkit", task_type="tool", tool_id="gpuz"),
        Task("t_speccy",     "Speccy",            "Complete system information summary",   "toolkit", task_type="tool", tool_id="speccy"),
        Task("t_ohm",        "OpenHardwareMonitor","Real-time temps, voltages, fan speeds", "toolkit", task_type="tool", tool_id="openhardwaremonitor"),
    ]),
    ("Malware Removal", [
        Task("t_stinger",    "Trellix Stinger",   "Targeted virus removal",                "toolkit", task_type="tool", tool_id="stinger"),
        Task("t_tdss",       "TDSSKiller",        "Rootkit and bootkit removal",           "toolkit", task_type="tool", tool_id="tdsskiller"),
        Task("t_mb",         "Malwarebytes",      "Full malware scanner",                  "toolkit", task_type="tool", tool_id="malwarebytes"),
        Task("t_adw",        "AdwCleaner",        "Adware and PUP removal",               "toolkit", task_type="tool", tool_id="adwcleaner"),
        Task("t_rkill",      "RKill",             "Stops malicious processes",             "toolkit", task_type="tool", tool_id="rkill"),
        Task("t_kill",       "KillEmAll",         "Kill all non-essential processes",      "toolkit", task_type="tool", tool_id="killemall"),
        Task("t_rogue",      "RogueKiller",       "Advanced malware and rootkit scanner",  "toolkit", task_type="tool", tool_id="roguekiller"),
    ]),
    ("Repair Tools", [
        Task("t_dotnet",     ".NET Framework Repair",   "Repairs .NET installations",         "toolkit", task_type="tool", tool_id="netframeworkrepair"),
        Task("t_winrep",     "Windows Repair AIO",      "Tweaking.com repair suite",           "toolkit", task_type="tool", tool_id="windowsrepair"),
        Task("t_apf",        "Account Profile Fixer",   "Fixes corrupt user profiles",        "toolkit", task_type="tool", tool_id="apf"),
        Task("t_dismpp",     "DISM++",                  "Advanced DISM GUI",                   "toolkit", task_type="tool", tool_id="dismpp"),
    ]),
    ("Migration & Backup", [
        Task("t_fabs",       "Fab's AutoBackup 7 Pro",  "Backup/restore user data, browsers, email, WiFi keys  —  Licensed tool", "toolkit", task_type="tool", tool_id="fabs"),
    ]),

    ("NirSoft Utilities  ⚠ Defender may flag these — add exclusion first", [
        Task("t_nir_wireless",  "WirelessKeyView",      "Export all saved WiFi passwords",                    "toolkit", task_type="tool", tool_id="wirelesskeyview"),
        Task("t_nir_produkey",  "ProduKey",             "Recover Windows & Office product keys",              "toolkit", task_type="tool", tool_id="produkey"),
        Task("t_nir_webbpass",  "WebBrowserPassView",   "View saved passwords from Chrome/Firefox/Edge",      "toolkit", task_type="tool", tool_id="webbrowserpassview"),
        Task("t_nir_netpass",   "NetPass",              "Recover stored Windows network credentials",         "toolkit", task_type="tool", tool_id="netpass"),
        Task("t_nir_bsview",    "BlueScreenView",       "Analyze past BSODs and minidumps",                   "toolkit", task_type="tool", tool_id="bluescreenview"),
        Task("t_nir_shellexv",  "ShellExView",          "Find & disable bad shell extensions causing crashes", "toolkit", task_type="tool", tool_id="shellexview"),
        Task("t_nir_lastact",   "LastActivityView",     "Timeline of recent PC activity",                     "toolkit", task_type="tool", tool_id="lastactivityview"),
        Task("t_nir_myunist",   "MyUninstaller",        "Alternative uninstaller with more detail",           "toolkit", task_type="tool", tool_id="myuninstaller"),
        Task("t_nir_startuprun","StartupRun",           "View and manage all startup entries",                "toolkit", task_type="tool", tool_id="startuprun"),
        Task("t_nir_processact","ProcessActivityView",  "See which processes accessed which files",           "toolkit", task_type="tool", tool_id="processactivityview"),
    ]),
]

MAINTENANCE_TASKS = [
    # Temp & Disk
    Task("maint_temp",       "Empty Temp Folders",                   "Clears current user and system temp folders",               "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","temp"]),
    Task("maint_alltemp",    "Empty All Users Temp Folders",         "Clears temp for every user account on this PC",             "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","alltemp"]),
    Task("maint_diskclean",  "Run Disk Cleanup (Unattended)",        "Runs cleanmgr with all categories selected",                "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","diskcleanup"]),
    Task("maint_softwaredist","Clear Windows Update Cache",          "Deletes SoftwareDistribution\\Download folder",             "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","softwaredist"]),
    Task("maint_winold",     "Delete Windows.old Folder",            "Removes old Windows installation files",                   "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","windowsold"]),
    Task("maint_winsxs",     "Clean WinSxS Component Store",        "DISM StartComponentCleanup — frees significant space",      "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","winsxs"]),
    Task("maint_msiorphans", "Cleanup MSI Orphan Files",             "Reports orphaned MSI files in Windows\\Installer",         "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","msiorphans"]),
    Task("maint_ghostdev",   "Remove Ghost Devices",                 "Uninstalls non-present/phantom devices from Device Manager","maintain", script="maintenance_cleanup.ps1", script_args=["-Action","ghostdevices"]),
    Task("maint_notifcache", "Clear Notification Area Cache",        "Removes phantom/ghost icons from system tray",              "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","notificationcache"]),
    Task("maint_temprofiles","Delete Temporary Profile Folders",     "Removes leftover .bak and TEMP profile folders",           "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","temp_profiles"]),
    # Privacy
    Task("maint_quickaccess","Clear Quick Access & Jump Lists",      "Removes recent files and jump list entries",                "maintain", script="clear_browser_history.ps1", script_args=["-Browser","quickaccess"]),
    Task("maint_chromehist", "Clear Chrome History & Cache",         "Removes Chrome browsing history, cookies, cache",          "maintain", script="clear_browser_history.ps1", script_args=["-Browser","chrome"]),
    Task("maint_ffhist",     "Clear Firefox History & Cache",        "Removes Firefox browsing history, cookies, cache",         "maintain", script="clear_browser_history.ps1", script_args=["-Browser","firefox"]),
    Task("maint_edgehist",   "Clear Edge History & Cache",           "Removes Edge browsing history, cookies, cache",            "maintain", script="clear_browser_history.ps1", script_args=["-Browser","edge"]),
    Task("maint_allbrowsers","Clear All Browsers History",           "Clears history, cache, cookies in Chrome/Firefox/Edge",    "maintain", script="clear_browser_history.ps1", script_args=["-Browser","all"]),
    Task("maint_eventlogs",  "Clear Windows Event Logs",             "Clears Application, System, Security, Setup logs",         "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","eventlogs"]),
    Task("maint_errreports", "Clear Error Report Folders",           "Removes Windows Error Reporting crash data",                "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","errorreports"]),
    Task("maint_shellcache", "Clear Shell & MuiCache",               "Removes cached app name and shell entries",                "maintain", script="maintenance_cleanup.ps1", script_args=["-Action","shellcache"]),
    # Updates & System
    Task("maint_wu",         "Run Windows Update",                   "Opens Windows Update and triggers scan",                   "maintain", script="fixes.ps1", script_args=["-Action","update_windows"]),
    Task("maint_battery",    "Battery Health Report",                "Generates powercfg battery report (opens in browser)",     "maintain", script="battery_report.ps1"),
    Task("maint_power",      "Power Efficiency Report",              "60-second power trace, opens HTML report",                 "maintain", script="power_efficiency.ps1"),
    # Post-Repair Installs
    Task("install_chrome",   "Install/Update Chrome",                "Silent Chrome install via winget",                         "maintain", script="post_repair_install.ps1", script_args=["-App","chrome"]),
    Task("install_firefox",  "Install/Update Firefox",               "Silent Firefox install via winget",                        "maintain", script="post_repair_install.ps1", script_args=["-App","firefox"]),
    Task("install_7zip",     "Install/Update 7-Zip",                 "Silent 7-Zip install via winget",                         "maintain", script="post_repair_install.ps1", script_args=["-App","7zip"]),
    Task("install_vcredist", "Install Visual C++ Runtimes",          "Installs all VC++ redistributables via winget",            "maintain", script="post_repair_install.ps1", script_args=["-App","vcredist"]),
    Task("install_dotnet",   "Install .NET 8 Runtime",               "Installs Microsoft .NET 8 Desktop Runtime",                "maintain", script="post_repair_install.ps1", script_args=["-App","dotnet"]),
    Task("install_all",      "Install All Essentials",               "Chrome + Firefox + 7-Zip + VC++ + .NET in one shot",       "maintain", script="post_repair_install.ps1", script_args=["-App","all"]),
]

TWEAKS_TASKS = [
    # Startup/Shutdown
    Task("twk_no_delay",     "Disable Startup App Delay",            "Removes artificial delay before startup apps load",         "tweaks", script="tweaks.ps1", script_args=["-Action","disable_startup_delay"]),
    Task("twk_prefetch",     "Optimize Prefetch for Startup",        "Enables full prefetch/superfetch for faster boot",          "tweaks", script="tweaks.ps1", script_args=["-Action","optimize_prefetch"]),
    Task("twk_fast_shutdown","Faster Shutdown",                      "Reduces app/service wait time during shutdown",             "tweaks", script="tweaks.ps1", script_args=["-Action","faster_shutdown"]),
    # Display
    Task("twk_no_anim",      "Disable Window Animations",            "Removes open/close animations — big speed boost on slow PCs","tweaks", script="tweaks.ps1", script_args=["-Action","disable_animations"]),
    Task("twk_menu_speed",   "Faster Menus & Dialogs",               "Removes menu display delay",                               "tweaks", script="tweaks.ps1", script_args=["-Action","optimize_menus"]),
    Task("twk_file_list",    "Optimize File Listings",               "Disables last access time updates, faster folder browsing", "tweaks", script="tweaks.ps1", script_args=["-Action","optimize_file_listings"]),
    Task("twk_icon_cache",   "Increase Icon Cache Size",             "Larger icon cache reduces blank icon occurrences",          "tweaks", script="tweaks.ps1", script_args=["-Action","increase_icon_cache"]),
    # Performance
    Task("twk_foreground",   "Boost Foreground App Responsiveness",  "Increases CPU priority for the active window",              "tweaks", script="tweaks.ps1", script_args=["-Action","foreground_responsiveness"]),
    Task("twk_cpu_fg",       "Optimize CPU for Foreground Apps",     "Adjusts Win32PrioritySeparation for foreground tasks",      "tweaks", script="tweaks.ps1", script_args=["-Action","optimize_cpu_foreground"]),
    Task("twk_no_store_bg",  "Disable Background Store Apps",        "Stops Windows Store apps running in the background",        "tweaks", script="tweaks.ps1", script_args=["-Action","disable_store_background"]),
    Task("twk_no_error_rpt", "Disable Error Reporting (WerFault)",   "Stops WerFault.exe from spiking CPU after crashes",         "tweaks", script="tweaks.ps1", script_args=["-Action","disable_error_reporting"]),
    Task("twk_no_default_reset","Prevent Default App Reset",         "Stops Windows resetting file associations after updates",   "tweaks", script="tweaks.ps1", script_args=["-Action","prevent_default_app_reset"]),
    # Networking
    Task("twk_dns_cache",    "Optimize DNS Cache",                   "Increases DNS cache size and TTL for faster browsing",      "tweaks", script="tweaks.ps1", script_args=["-Action","optimize_dns_cache"]),
    Task("twk_tcpip",        "Optimize TCP/IP",                      "Enables TCP auto-tuning and performance features",          "tweaks", script="tweaks.ps1", script_args=["-Action","optimize_tcpip"]),
    Task("twk_lan",          "Optimize LAN Settings",                "Disables bandwidth throttling, increases file cache",       "tweaks", script="tweaks.ps1", script_args=["-Action","optimize_lan"]),
    # BSOD & Crash Diagnostics
    Task("twk_bsod_no_reboot",  "Disable Auto-Reboot on BSOD",      "Keeps BSOD visible so you can read the stop code",         "tweaks", script="bsod_tweaks.ps1", script_args=["-Action","disable_autoreboot"]),
    Task("twk_bsod_reboot",     "Re-enable Auto-Reboot on BSOD",    "Restores default auto-reboot behaviour after BSOD",        "tweaks", script="bsod_tweaks.ps1", script_args=["-Action","enable_autoreboot"]),
    Task("twk_minidumps",       "Enable Minidump on BSOD",          "Saves crash dump files for analysis with WhoCrashed",      "tweaks", script="bsod_tweaks.ps1", script_args=["-Action","enable_minidumps"]),
    Task("twk_classic_bsod",    "Enable Classic BSOD Style",        "Restores text-heavy BSOD instead of minimal smiley screen","tweaks", script="bsod_tweaks.ps1", script_args=["-Action","enable_classic_bsod"]),
    Task("twk_check_dumps",     "Check for Crash Dump Files",       "Lists existing minidump files on this machine",            "tweaks", script="bsod_tweaks.ps1", script_args=["-Action","check_dumps"]),
    # Clock & Time
    Task("twk_sync_clock",      "Sync System Clock Now",             "Forces immediate NTP clock sync",                         "tweaks", script="time_tools.ps1", script_args=["-Action","sync_now"]),
    Task("twk_enable_timesync", "Enable Automatic Time Sync",        "Configures W32tm and NTP, enables auto-sync",             "tweaks", script="time_tools.ps1", script_args=["-Action","enable_autosync"]),
]

ALL_TASKS = {t.task_id: t for t in TRIAGE_TASKS + TREAT_TASKS + MAINTENANCE_TASKS + TWEAKS_TASKS}

# Tasks that take a long time and don't report incremental progress
# These get an indeterminate (animated) progress bar + elapsed timer
LONG_RUNNING_TASKS = {
    "sfc", "dism_scan", "dism_restore", "defender_full", "defender_quick",
    "repair_wu", "repair_wmi", "repair_perms", "reg_dlls", "chkdsk",
    "rebuild_bcd", "group_policy"
}


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def divider():
    f = QFrame(); f.setObjectName("divider"); f.setFrameShape(QFrame.HLine); return f

def lbl(text, color=None, bold=False, size=None):
    w = QLabel(text); w.setWordWrap(True)
    s = ""
    if color: s += f"color:{color};"
    if bold:  s += "font-weight:700;"
    if size:  s += f"font-size:{size}pt;"
    if s: w.setStyleSheet(s)
    return w

def hdr(text, color=None):
    return lbl(text, color=color or C["accent"], bold=True, size=13)

def badge(text, color):
    w = QLabel(f"  {text}  ")
    w.setStyleSheet(f"color:{color};border:1px solid {color};border-radius:4px;padding:1px 4px;font-size:8pt;font-weight:700;")
    return w

def tool_exe(tool_id):
    """Returns path to downloaded tool exe, or None."""
    try:
        mp = os.path.join(BUNDLE_DIR, "tools_manifest.json")
        with open(mp) as f:
            for t in json.load(f)["tools"]:
                if t["id"] == tool_id:
                    p = os.path.join(TOOLS_DIR, tool_id, t["filename"])
                    return p if os.path.exists(p) else None
    except: pass
    return None


# ─────────────────────────────────────────────
#  TASK ROW  (checkbox + badges + run/queue btns)
# ─────────────────────────────────────────────
class TaskRow(QWidget):
    def __init__(self, task, queue_ref=None):
        super().__init__()
        self.task = task
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        self.cb = QCheckBox(task.name)
        self.cb.setToolTip(task.description)
        layout.addWidget(self.cb)
        layout.addStretch()

        if task.task_type == "tool":
            layout.addWidget(badge("External Tool", C["yellow"]))
        if task.requires_reboot:
            layout.addWidget(badge("⚠ Reboot", C["triage"]))

        run_btn = QPushButton("▶")
        run_btn.setFixedSize(28, 28)
        run_btn.setToolTip(f"Run '{task.name}' now")
        run_btn.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};border-radius:4px;font-size:11pt;padding:0;")
        run_btn.clicked.connect(self._run)
        layout.addWidget(run_btn)

        if queue_ref:
            q_btn = QPushButton("+")
            q_btn.setFixedSize(28, 28)
            q_btn.setToolTip("Add to Run Queue")
            q_btn.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};border-radius:4px;font-size:14pt;padding:0;")
            q_btn.clicked.connect(lambda: queue_ref.add_task(task))
            layout.addWidget(q_btn)

    def is_checked(self): return self.cb.isChecked()

    def _run(self):
        dlg = TaskRunDialog(self.task, self)
        dlg.exec_()


# ─────────────────────────────────────────────
#  TASK RUN DIALOG
# ─────────────────────────────────────────────
class TaskRunDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.proc = None
        self.setWindowTitle(f"Repair-O — {task.name}")
        self.resize(680, 440)
        self.setStyleSheet(f"background:{C['bg']};color:{C['text']};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(hdr(task.name))
        layout.addWidget(lbl(task.description, color=C["muted"]))
        layout.addWidget(divider())
        self.prog = QProgressBar(); self.prog.setValue(0)
        layout.addWidget(self.prog)
        self.status = lbl("Ready.", color=C["muted"])
        layout.addWidget(self.status)
        self.out = QTextEdit(); self.out.setReadOnly(True)
        layout.addWidget(self.out)
        brow = QHBoxLayout()
        self.run_btn = QPushButton("▶  Run Now")
        self.run_btn.clicked.connect(self.run)
        brow.addWidget(self.run_btn)
        self.stop_btn = QPushButton("🛑  Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(f"background:{C['red']};color:white;")
        self.stop_btn.clicked.connect(self.stop_task)
        brow.addWidget(self.stop_btn)
        close_btn = QPushButton("Close"); close_btn.clicked.connect(self.accept)
        brow.addWidget(close_btn)
        layout.addLayout(brow)

    def run(self):
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.out.clear()
        self.status.setText("Running...")
        self._start_time = datetime.now()

        if self.task.task_id in LONG_RUNNING_TASKS:
            self.prog.setRange(0, 0)
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._tick_timer)
            self._timer.start(1000)
        else:
            self.prog.setRange(0, 100)
            self.prog.setValue(10)

        if self.task.task_type == "tool": self._launch_tool()
        else: self._run_script()

    def stop_task(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.status.setText("🛑 Stopped by user.")
        self.stop_btn.setEnabled(False)
        self.run_btn.setEnabled(True)
        if hasattr(self, '_timer'):
            self._timer.stop()
        self.prog.setRange(0, 100)
        self.prog.setValue(0)

    def _tick_timer(self):
        elapsed = int((datetime.now() - self._start_time).total_seconds())
        m, s = divmod(elapsed, 60)
        self.status.setText(f"⏳ Running... {m}m {s:02d}s elapsed — please wait")

    def _finish_run(self, returncode):
        if hasattr(self, '_timer'):
            self._timer.stop()
        self.prog.setRange(0, 100)
        self.prog.setValue(100)
        elapsed = int((datetime.now() - self._start_time).total_seconds())
        m, s = divmod(elapsed, 60)
        if returncode == 0:
            self.status.setText(f"✅ Completed successfully in {m}m {s:02d}s")
        else:
            self.status.setText(f"⚠ Finished with exit code {returncode} ({m}m {s:02d}s)")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _run_script(self):
        script = self.task.script_path
        if not script or not os.path.exists(script):
            self._stub(); return
        def worker():
            try:
                self.proc = subprocess.Popen(
                    ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", script],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                while True:
                    line = self.proc.stdout.readline()
                    if not line and self.proc.poll() is not None:
                        break
                    if line:
                        stripped = line.rstrip()
                        if stripped:
                            self.out.append(stripped)
                            QApplication.processEvents()
                self.proc.wait()
                QTimer.singleShot(0, lambda: self._finish_run(self.proc.returncode))
            except Exception as e:
                QTimer.singleShot(0, lambda: self.status.setText(f"❌ Error: {e}"))
                QTimer.singleShot(0, lambda: self.run_btn.setEnabled(True))
                QTimer.singleShot(0, lambda: self.stop_btn.setEnabled(False))
        threading.Thread(target=worker, daemon=True).start()

    def _launch_tool(self):
        exe = tool_exe(self.task.tool_id)
        if exe:
            subprocess.Popen([exe])
            self.status.setText(f"✅ Launched."); self.prog.setValue(100)
        else:
            self.status.setText("⚠ Not downloaded. Use Toolkit tab to download first.")
            self.prog.setValue(0)
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _stub(self):
        import time
        self.out.append(f"[Repair-O] Stub: {self.task.script}")
        self.out.append("[Repair-O] Script pending implementation — simulating...")
        for i in range(1, 6):
            self.prog.setValue(i * 20)
            self.out.append(f"  Step {i}/5 ... OK")
            QApplication.processEvents(); time.sleep(0.25)
        self.status.setText("✅ Stub complete.")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


# ─────────────────────────────────────────────
#  SYS INFO WORKER
# ─────────────────────────────────────────────
class SysInfoWorker(QThread):
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    def __init__(self, path): super().__init__(); self.path = path
    def run(self):
        self.progress.emit(10, "Launching PowerShell...")
        try:
            r = subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",self.path],
                               capture_output=True, text=True, timeout=90,
                               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)
            self.progress.emit(80, "Parsing...")
            if r.returncode != 0 and not r.stdout:
                self.error.emit(r.stderr or "No output."); return
            self.finished.emit(json.loads(r.stdout)); self.progress.emit(100,"Done.")
        except json.JSONDecodeError as e:
            self.error.emit(f"JSON error: {e}")
        except FileNotFoundError:
            self.error.emit("PowerShell not found.")
        except subprocess.TimeoutExpired:
            self.error.emit("Timed out.")
        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────────────────────────────
#  TAB 1: DIAGNOSE
# ─────────────────────────────────────────────
class AlertCard(QFrame):
    """A single alert card shown in the alerts panel."""
    COLORS = {
        "ERROR": ("#7f1d1d", "#ef4444", "❌"),
        "WARN":  ("#78350f", "#f59e0b", "⚠"),
        "INFO":  ("#1e3a5f", "#60a5fa", "ℹ"),
        "OK":    ("#14532d", "#22c55e", "✅"),
    }
    def __init__(self, level, title, detail, parent=None):
        super().__init__(parent)
        bg, fg, icon = self.COLORS.get(level, self.COLORS["INFO"])
        self.setStyleSheet(f"background:{bg};border-radius:6px;border:1px solid {fg};padding:0px;margin:2px 0;")
        row = QHBoxLayout(self); row.setContentsMargins(10, 7, 10, 7); row.setSpacing(8)
        ico = QLabel(icon); ico.setStyleSheet(f"font-size:14pt;color:{fg};")
        ico.setFixedWidth(22); row.addWidget(ico)
        txt = QVBoxLayout(); txt.setSpacing(1)
        t = QLabel(title); t.setStyleSheet(f"color:{fg};font-weight:bold;font-size:9.5pt;")
        d = QLabel(detail); d.setStyleSheet(f"color:#cccccc;font-size:8.5pt;"); d.setWordWrap(True)
        txt.addWidget(t); txt.addWidget(d)
        row.addLayout(txt, 1)


class DiagnoseTab(QWidget):
    def __init__(self):
        super().__init__()
        self.raw_data = {}
        self.script_path   = os.path.join(SCRIPTS_DIR, "system_info.ps1")
        self.alerts_script = os.path.join(SCRIPTS_DIR, "system_alerts.ps1")
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,16); layout.setSpacing(10)

        # ── Header row ────────────────────────────────────────────────────
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("📊  Scan & Report")); hrow.addStretch()
        self.scan_btn = QPushButton("⚡  Run Diagnostics"); self.scan_btn.clicked.connect(self.run_scan)
        self.exp_btn  = QPushButton("💾  Export Report")
        self.exp_btn.setStyleSheet(f"background:#14532d;color:{C['green']};")
        self.exp_btn.clicked.connect(self.export); self.exp_btn.setEnabled(False)
        hrow.addWidget(self.scan_btn); hrow.addWidget(self.exp_btn)
        layout.addLayout(hrow)

        self.prog = QProgressBar(); self.prog.setVisible(False)
        layout.addWidget(self.prog)
        self.status = lbl("Click 'Run Diagnostics' to gather system information.", color=C["muted"])
        layout.addWidget(self.status)
        layout.addWidget(divider())

        # ── Main splitter: alerts panel LEFT | system info RIGHT ──────────
        main_split = QSplitter(Qt.Horizontal)

        # ── LEFT: Alerts Panel ────────────────────────────────────────────
        alerts_widget = QWidget()
        alerts_widget.setMinimumWidth(260); alerts_widget.setMaximumWidth(340)
        alerts_layout = QVBoxLayout(alerts_widget)
        alerts_layout.setContentsMargins(0, 0, 8, 0); alerts_layout.setSpacing(6)

        alert_hdr_row = QHBoxLayout()
        alert_hdr_lbl = QLabel("🚨  System Alerts")
        alert_hdr_lbl.setStyleSheet(f"color:{C['accent']};font-size:10pt;font-weight:bold;")
        self.alert_refresh_btn = QPushButton("↻")
        self.alert_refresh_btn.setFixedSize(24, 24)
        self.alert_refresh_btn.setToolTip("Refresh alerts")
        self.alert_refresh_btn.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};border-radius:4px;font-size:12pt;padding:0;")
        self.alert_refresh_btn.clicked.connect(self._run_alerts)
        alert_hdr_row.addWidget(alert_hdr_lbl); alert_hdr_row.addStretch(); alert_hdr_row.addWidget(self.alert_refresh_btn)
        alerts_layout.addLayout(alert_hdr_row)

        self.alerts_status = QLabel("Scanning…")
        self.alerts_status.setStyleSheet(f"color:{C['muted']};font-size:8pt;")
        alerts_layout.addWidget(self.alerts_status)

        alerts_scroll = QScrollArea(); alerts_scroll.setWidgetResizable(True)
        alerts_scroll.setStyleSheet(f"background:{C['panel']};border:1px solid {C['border']};border-radius:6px;")
        self.alerts_content = QWidget()
        self.alerts_vbox = QVBoxLayout(self.alerts_content)
        self.alerts_vbox.setContentsMargins(6, 6, 6, 6); self.alerts_vbox.setSpacing(4)
        self.alerts_vbox.addStretch()
        alerts_scroll.setWidget(self.alerts_content)
        alerts_layout.addWidget(alerts_scroll, 1)
        main_split.addWidget(alerts_widget)

        # ── RIGHT: System Info (tree + detail) ───────────────────────────
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget); info_layout.setContentsMargins(0,0,0,0)
        info_split = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget(); self.tree.setHeaderLabels(["Category","Summary"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tree.setAlternatingRowColors(True); self.tree.itemClicked.connect(self._select)
        info_split.addWidget(self.tree)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.detail_w = QWidget(); self.detail_l = QVBoxLayout(self.detail_w)
        self.detail_l.setAlignment(Qt.AlignTop); self.scroll.setWidget(self.detail_w)
        info_split.addWidget(self.scroll); info_split.setSizes([240, 600])
        info_layout.addWidget(info_split)
        main_split.addWidget(info_widget)

        main_split.setSizes([300, 700])
        layout.addWidget(main_split)

        # Auto-run alerts on first load
        QTimer.singleShot(800, self._run_alerts)

    # ── Alerts panel ─────────────────────────────────────────────────────
    def _run_alerts(self):
        self.alerts_status.setText("Scanning…")
        self.alert_refresh_btn.setEnabled(False)
        import threading as _t, json as _j

        def _fetch():
            try:
                flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                r = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", self.alerts_script],
                    capture_output=True, text=True, timeout=45, creationflags=flags
                )
                raw = r.stdout.strip()
                parts       = raw.split("---PASSED---")
                alerts_json = parts[0].strip()
                passed_json = parts[1].strip() if len(parts) > 1 else "[]"
                alerts = _j.loads(alerts_json) if alerts_json else []
                passed = _j.loads(passed_json) if passed_json else []
                QTimer.singleShot(0, lambda: self._populate_alerts(alerts, passed))
            except Exception as e:
                QTimer.singleShot(0, lambda: self._alerts_error(str(e)))

        _t.Thread(target=_fetch, daemon=True).start()

    def _populate_alerts(self, alerts, passed):
        while self.alerts_vbox.count():
            item = self.alerts_vbox.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not alerts and not passed:
            self.alerts_vbox.addWidget(lbl("No data returned.", color=C["muted"]))
        else:
            order = {"ERROR": 0, "WARN": 1, "INFO": 2}
            for a in sorted(alerts, key=lambda a: order.get(a.get("Level","INFO"), 2)):
                self.alerts_vbox.addWidget(AlertCard(a.get("Level","INFO"), a.get("Title","Alert"), a.get("Detail","")))
            if passed:
                sep = QLabel("✅  Passing Checks")
                sep.setStyleSheet(f"color:{C['muted']};font-size:8pt;font-weight:bold;margin-top:8px;")
                self.alerts_vbox.addWidget(sep)
                for p in passed:
                    self.alerts_vbox.addWidget(AlertCard("OK", str(p), ""))

        self.alerts_vbox.addStretch()
        ts       = datetime.now().strftime("%H:%M:%S")
        n_issues = len([a for a in alerts if a.get("Level") in ("ERROR","WARN")])
        self.alerts_status.setText(
            f"✅ No issues  ·  {ts}" if n_issues == 0 else f"⚠ {n_issues} issue(s)  ·  {ts}"
        )
        self.alert_refresh_btn.setEnabled(True)

    def _alerts_error(self, msg):
        while self.alerts_vbox.count():
            item = self.alerts_vbox.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.alerts_vbox.addWidget(AlertCard("WARN", "Alerts scan failed", msg[:120]))
        self.alerts_vbox.addStretch()
        self.alerts_status.setText("Error running alerts scan")
        self.alert_refresh_btn.setEnabled(True)

    # ── System Info scan ─────────────────────────────────────────────────
    def run_scan(self):
        if not os.path.exists(self.script_path):
            self.status.setText("❌ system_info.ps1 not found in scripts/"); return
        self.scan_btn.setEnabled(False); self.exp_btn.setEnabled(False)
        self.prog.setVisible(True); self.prog.setValue(0)
        self.tree.clear(); self._clear()
        w = SysInfoWorker(self.script_path)
        w.finished.connect(self._done); w.error.connect(self._err)
        w.progress.connect(lambda v,m: (self.prog.setValue(v), self.status.setText(f"⏳ {m}")))
        w.start(); self._worker = w

    def _done(self, data):
        self.raw_data = data; self.prog.setVisible(False)
        self.scan_btn.setEnabled(True); self.exp_btn.setEnabled(True)
        self.status.setText(f"✅ Done — {datetime.now().strftime('%H:%M:%S')}")
        icons = {"OS":"🖥","Computer":"🖱","CPU":"⚙","RAM":"🧠","Disks":"💾",
                 "GPU":"🎮","Network":"🌐","Security":"🔒","Updates":"🔄","Startup":"🚀","Environment":"🔧"}
        summaries = {
            "OS": lambda d: d.get("Name",""), "Computer": lambda d: f"{d.get('Manufacturer','')} {d.get('Model','')}",
            "CPU": lambda d: d.get("Name",""), "RAM": lambda d: f"{d.get('Total (GB)','')} GB",
            "Disks": lambda d: f"{len(d)} drive(s)", "GPU": lambda d: d[0].get("Name","") if isinstance(d,list) and d else "",
            "Network": lambda d: f"{len(d)} adapter(s)" if isinstance(d,list) else "",
            "Security": lambda d: d.get("Antivirus",""), "Updates": lambda d: "Last 10",
            "Startup": lambda d: "", "Environment": lambda d: d.get("Username",""),
        }
        for key in ["OS","Computer","CPU","RAM","Disks","GPU","Network","Security","Updates","Startup","Environment"]:
            if key not in data: continue
            try: sm = summaries.get(key, lambda d:"")(data[key])
            except: sm = ""
            item = QTreeWidgetItem([f"{icons.get(key,'•')}  {key}", sm])
            item.setData(0, Qt.UserRole, key); item.setForeground(1, QColor(C["muted"]))
            self.tree.addTopLevelItem(item)
        if self.tree.topLevelItemCount() > 0:
            f = self.tree.topLevelItem(0); self.tree.setCurrentItem(f); self._select(f, 0)

    def _err(self, msg):
        self.prog.setVisible(False); self.scan_btn.setEnabled(True)
        self.status.setText("❌ Error"); self._clear()
        self.detail_l.addWidget(lbl(f"Error:\n\n{msg}", color=C["red"]))

    def _select(self, item, col):
        key = item.data(0, Qt.UserRole)
        if not key or key not in self.raw_data: return
        self._clear(); val = self.raw_data[key]
        self.detail_l.addWidget(hdr(f"  {key}")); self.detail_l.addWidget(divider())
        if isinstance(val, dict): self._render(val)
        elif isinstance(val, list):
            for i, entry in enumerate(val):
                if isinstance(entry, dict):
                    nm = entry.get("Name", entry.get("Description", f"Item {i+1}"))
                    g = QGroupBox(nm); gl = QGridLayout(g)
                    for r,(k,v) in enumerate(entry.items()):
                        kl = QLabel(f"{k}:"); kl.setStyleSheet(f"color:{C['muted']};font-size:9pt;"); kl.setMinimumWidth(140)
                        vl = QLabel(str(v)); vl.setStyleSheet(f"color:{C['text']};font-size:9pt;"); vl.setWordWrap(True)
                        vl.setTextInteractionFlags(Qt.TextSelectableByMouse)
                        gl.addWidget(kl,r,0,Qt.AlignTop); gl.addWidget(vl,r,1,Qt.AlignTop)
                    self.detail_l.addWidget(g)
                else: self.detail_l.addWidget(lbl(str(entry)))
        else: self.detail_l.addWidget(lbl(str(val)))
        self.detail_l.addStretch()

    def _render(self, d):
        grid = QGridLayout(); grid.setColumnStretch(1,1)
        for row,(k,v) in enumerate(d.items()):
            kl = QLabel(f"{k}:"); kl.setStyleSheet(f"color:{C['muted']};font-size:9pt;"); kl.setMinimumWidth(165); kl.setAlignment(Qt.AlignTop)
            vs = str(v) if not isinstance(v,(list,dict)) else json.dumps(v,indent=2)
            vl = QLabel(vs); vl.setStyleSheet(f"color:{C['text']};font-weight:500;font-size:9pt;")
            vl.setWordWrap(True); vl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            grid.addWidget(kl,row,0,Qt.AlignTop); grid.addWidget(vl,row,1,Qt.AlignTop)
        cw = QWidget(); cw.setLayout(grid); self.detail_l.addWidget(cw)

    def _clear(self):
        while self.detail_l.count():
            item = self.detail_l.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def export(self):
        if not self.raw_data: return
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.expanduser("~"), "Desktop", f"RepairO_Report_{ts}.txt")
        try:
            lines = ["="*70, "  Repair-O System Report",
                     f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "="*70,""]
            for sec,data in self.raw_data.items():
                lines += [f"\n{'─'*60}",f"  {sec.upper()}",f"{'─'*60}"]
                if isinstance(data,dict):
                    for k,v in data.items(): lines.append(f"  {k:<32} {v}")
                elif isinstance(data,list):
                    for i,entry in enumerate(data):
                        lines.append(f"\n  [{i+1}]")
                        if isinstance(entry,dict):
                            for k,v in entry.items(): lines.append(f"    {k:<30} {v}")
                        else: lines.append(f"    {entry}")
                else: lines.append(f"  {data}")
            with open(path,"w",encoding="utf-8") as f: f.write("\n".join(lines))
            self.status.setText("✅ Report saved to Desktop.")
        except Exception as e: self.status.setText(f"❌ Export failed: {e}")


# ─────────────────────────────────────────────
#  TASK SECTION BUILDER (reused by Triage & Treat)
# ─────────────────────────────────────────────
def build_task_section(tasks, queue_ref, accent_color, builtin_label, ext_label):
    """Returns (scroll_widget, list_of_task_rows)"""
    rows = []
    scroll = QScrollArea(); scroll.setWidgetResizable(True)
    content = QWidget(); content.setStyleSheet(f"background:{C['panel']};")
    vl = QVBoxLayout(content); vl.setContentsMargins(12,12,12,12); vl.setSpacing(4)

    builtin = [t for t in tasks if t.task_type == "script"]
    ext     = [t for t in tasks if t.task_type == "tool"]

    if builtin:
        g = QGroupBox(builtin_label)
        g.setStyleSheet(f"QGroupBox {{ color:{accent_color}; }}")
        gl = QVBoxLayout(g)
        for task in builtin:
            r = TaskRow(task, queue_ref)
            gl.addWidget(r); rows.append(r)
        vl.addWidget(g)

    if ext:
        g2 = QGroupBox(ext_label)
        g2.setStyleSheet(f"QGroupBox {{ color:{C['yellow']}; }}")
        gl2 = QVBoxLayout(g2)
        for task in ext:
            r = TaskRow(task, queue_ref)
            gl2.addWidget(r); rows.append(r)
        vl.addWidget(g2)

    vl.addStretch()
    scroll.setWidget(content)
    return scroll, rows


def build_task_section_grouped(groups, queue_ref, accent_color):
    """Build a scrollable task list from pre-grouped task lists."""
    scroll = QScrollArea(); scroll.setWidgetResizable(True)
    content = QWidget(); content.setStyleSheet(f"background:{C['panel']};")
    vl = QVBoxLayout(content); vl.setContentsMargins(12,12,12,12); vl.setSpacing(6)
    all_rows = []
    for group_name, tasks in groups:
        if not tasks: continue
        g = QGroupBox(f"  {group_name}")
        g.setStyleSheet(f"QGroupBox {{ color:{accent_color}; }}")
        gl = QVBoxLayout(g)
        for task in tasks:
            row = TaskRow(task, queue_ref)
            gl.addWidget(row)
            all_rows.append(row)
        vl.addWidget(g)
    vl.addStretch()
    scroll.setWidget(content)
    return scroll, all_rows


# ─────────────────────────────────────────────
#  TAB 2: TRIAGE
# ─────────────────────────────────────────────
class TriageTab(QWidget):
    def __init__(self, queue_ref):
        super().__init__()
        self.queue_ref    = queue_ref
        self._section_idx  = 2
        self._section_name = "Fast Fixes"
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(10)
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("⚡  Fast Fixes", C["triage"])); hrow.addStretch()
        for txt, fn in [("Select All", lambda: [r.cb.setChecked(True) for r in self.rows]),
                         ("Clear All",  lambda: [r.cb.setChecked(False) for r in self.rows])]:
            b = QPushButton(txt); b.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};")
            b.clicked.connect(fn); hrow.addWidget(b)
        add_q = QPushButton("+ Add Selected to Queue")
        add_q.setStyleSheet(f"background:#14532d;color:{C['green']};")
        add_q.clicked.connect(self._add_queue); hrow.addWidget(add_q)
        run = QPushButton("▶▶  Run Selected Now"); run.clicked.connect(self._run_sel)
        hrow.addWidget(run); layout.addLayout(hrow)
        layout.addWidget(lbl("Malware removal tasks. Select any combination and run them in order.", color=C["muted"]))
        layout.addWidget(divider())
        scroll, self.rows = build_task_section(
            TRIAGE_TASKS, queue_ref, C["triage"],
            "⚙  Built-in Tasks (PowerShell)", "🛠  External Tools (Auto-Download)")
        layout.addWidget(scroll)

    def _add_queue(self):
        for r in self.rows:
            if r.is_checked(): self.queue_ref.add_task(r.task)

    def _run_sel(self):
        sel = [r.task for r in self.rows if r.is_checked()]
        if not sel: QMessageBox.information(self,"Repair-O","No tasks selected."); return
        self.queue_ref.add_tasks_and_run(sel)
        # Navigate to Run Tasks section and tell it where we came from
        main_win = self.window()
        if hasattr(main_win, "_go_section"):
            # Tell the queue tab which section to go back to
            src_idx  = getattr(self, "_section_idx",  9)
            src_name = getattr(self, "_section_name", "this section")
            self.queue_ref.set_source_section(src_idx, src_name)
            main_win._go_section(9)


# ─────────────────────────────────────────────
#  TAB 3: TREAT
# ─────────────────────────────────────────────
class TreatTab(QWidget):
    def __init__(self, queue_ref):
        super().__init__()
        self.queue_ref    = queue_ref
        self._section_idx  = 3
        self._section_name = "Fix & Repair"
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(10)
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("🔧  Fix & Repair", C["treat"])); hrow.addStretch()
        for txt, fn in [("Select All", lambda: [r.cb.setChecked(True) for r in self.rows]),
                         ("Clear All",  lambda: [r.cb.setChecked(False) for r in self.rows])]:
            b = QPushButton(txt); b.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};")
            b.clicked.connect(fn); hrow.addWidget(b)
        add_q = QPushButton("+ Add Selected to Queue")
        add_q.setStyleSheet(f"background:#14532d;color:{C['green']};")
        add_q.clicked.connect(self._add_queue); hrow.addWidget(add_q)
        run = QPushButton("▶▶  Run Selected Now"); run.clicked.connect(self._run_sel)
        hrow.addWidget(run); layout.addLayout(hrow)
        layout.addWidget(lbl("System repair tasks. Always create a restore point first!", color=C["muted"]))
        layout.addWidget(divider())
        scroll, self.rows = build_task_section(
            TREAT_TASKS, queue_ref, C["treat"],
            "🪟  Windows Built-in Repairs", "🛠  External Repair Tools (Auto-Download)")
        layout.addWidget(scroll)

    def _add_queue(self):
        for r in self.rows:
            if r.is_checked(): self.queue_ref.add_task(r.task)

    def _run_sel(self):
        sel = [r.task for r in self.rows if r.is_checked()]
        if not sel: QMessageBox.information(self,"Repair-O","No tasks selected."); return
        self.queue_ref.add_tasks_and_run(sel)
        # Navigate to Run Tasks section and tell it where we came from
        main_win = self.window()
        if hasattr(main_win, "_go_section"):
            # Tell the queue tab which section to go back to
            src_idx  = getattr(self, "_section_idx",  9)
            src_name = getattr(self, "_section_name", "this section")
            self.queue_ref.set_source_section(src_idx, src_name)
            main_win._go_section(9)


# ─────────────────────────────────────────────
#  TAB 4: TOOLKIT
# ─────────────────────────────────────────────
class ToolkitTab(QWidget):
    def __init__(self):
        super().__init__()
        self.cards = []
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(10)
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("🧰  Tools", C["toolkit"])); hrow.addStretch()
        dl_all = QPushButton("⬇  Download All Tools")
        dl_all.setStyleSheet(f"background:#14532d;color:{C['green']};")
        dl_all.clicked.connect(self._dl_all); hrow.addWidget(dl_all)
        layout.addLayout(hrow)
        layout.addWidget(lbl("Click Download to get each tool.  ✅ = downloaded and ready to launch.", color=C["muted"]))
        layout.addWidget(divider())

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); content.setStyleSheet(f"background:{C['panel']};")
        vl = QVBoxLayout(content); vl.setContentsMargins(12,12,12,12); vl.setSpacing(8)

        for group_name, tasks in TOOLKIT_GROUPS:
            is_nirsoft = "NirSoft" in group_name
            g = QGroupBox(f"  {group_name}")
            if is_nirsoft:
                g.setStyleSheet(
                    f"QGroupBox {{ color:{C['toolkit']}; font-weight:bold; }}"
                    f"QGroupBox::title {{ padding: 0 6px; }}"
                )
                # Subtle Defender note with button — no yellow
                warn_widget = QWidget()
                warn_layout = QHBoxLayout(warn_widget)
                warn_layout.setContentsMargins(8, 6, 8, 6)
                warn_text = QLabel(
                    "Defender may flag these tools. Add an exclusion before downloading."
                )
                warn_text.setWordWrap(True)
                warn_text.setStyleSheet(f"color:{C['muted']};font-size:8.5pt;")
                excl_btn = QPushButton("🛡  Add Defender Exclusion")
                excl_btn.setStyleSheet(
                    f"background:{C['panel']};color:{C['accent']};border:1px solid {C['accent']};"
                    f"border-radius:4px;padding:5px 12px;font-weight:bold;"
                )
                excl_btn.setFixedWidth(210)
                excl_btn.clicked.connect(self._add_defender_exclusion)
                warn_layout.addWidget(warn_text, 1)
                warn_layout.addWidget(excl_btn)
                warn_widget.setStyleSheet(
                    f"background:{C['panel2']};border:1px solid {C['border']};border-radius:6px;"
                )
                gl = QVBoxLayout(g)
                gl.addWidget(warn_widget)
            else:
                is_systools = "System Tools" in group_name
                gc = C["accent"] if is_systools else C["toolkit"]
                g.setStyleSheet(f"QGroupBox {{ color:{gc}; font-weight:bold; }}")
                gl = QVBoxLayout(g)
                if is_systools:
                    sys_note = QLabel("  Click ▶ Open to launch directly — no download needed")
                    sys_note.setStyleSheet(f"color:{C['muted']};font-size:8pt;padding:4px 8px;")
                    gl.addWidget(sys_note)
            for task in tasks:
                card = self._make_card(task)
                gl.addWidget(card)
            vl.addWidget(g)
        vl.addStretch()
        scroll.setWidget(content); layout.addWidget(scroll)

    def _add_defender_exclusion(self):
        """Add Windows Defender exclusion for the tools folder."""
        script = os.path.join(SCRIPTS_DIR, "nirsoft_defender_exclusion.ps1")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        # Show status in a simple message-style label while running
        btn = self.sender()
        if btn:
            btn.setEnabled(False)
            btn.setText("⏳ Adding exclusion...")

        output_lines = []
        def worker():
            try:
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                     "-File", script, "-ToolsDir", TOOLS_DIR],
                    capture_output=True, text=True, timeout=60, creationflags=flags)
                output_lines.extend((r.stdout + r.stderr).strip().splitlines())
            except Exception as e:
                output_lines.append(f"[ERROR] {e}")
            finally:
                QTimer.singleShot(0, finish)

        def finish():
            if btn:
                btn.setEnabled(True)
                btn.setText("🛡 Add Defender Exclusion Now")
            if any("[OK]" in l for l in output_lines):
                QMessageBox.information(self, "Exclusion Added",
                    f"\u2705 Defender exclusion added!\n\n"
                    f"NirSoft tools folder:\n{TOOLS_DIR}\n\n"
                    f"Windows Defender will no longer delete these tools.\n"
                    f"You can now safely download the NirSoft utilities.")
            else:
                result = "\n".join(output_lines[-5:]) if output_lines else "No output"
                QMessageBox.warning(self, "Exclusion Failed",
                    f"Could not add exclusion:\n\n{result}\n\n"
                    f"Make sure Repair-O is running as Administrator.")

        import threading as _t
        _t.Thread(target=worker, daemon=True).start()

    def _make_card(self, task):
        # Check manifest flags for this tool
        licensed = False
        license_url = ""
        is_nirsoft = False
        try:
            import json as _json
            with open(os.path.join(BUNDLE_DIR, "tools_manifest.json")) as _f:
                _manifest = _json.load(_f)
            for _t in _manifest.get("tools", []):
                if _t.get("id") == task.tool_id:
                    if _t.get("licensed"):
                        licensed = True
                        license_url = _t.get("license_url", "")
                    if _t.get("nirsoft"):
                        is_nirsoft = True
                    break
        except Exception:
            pass

        card = QFrame()
        is_builtin = task.task_type == "builtin"
        bg     = C["panel2"]  # same background for all card types
        border = C["border"]  # same neutral border for all card types
        card.setStyleSheet(f"QFrame{{background:{bg};border:1px solid {border};border-radius:5px;}}")
        card.setFixedHeight(50)
        row = QHBoxLayout(card); row.setContentsMargins(12,4,12,4)
        exe = tool_exe(task.tool_id)
        status = QLabel("✅" if exe else ("💰" if licensed else "⬜"))
        status.setFixedWidth(22)
        row.addWidget(status)
        nm = lbl(task.name, bold=True); nm.setMinimumWidth(200); row.addWidget(nm)
        desc_text = task.description
        row.addWidget(lbl(desc_text, color=C["muted"])); row.addStretch()
        prog = QProgressBar(); prog.setFixedWidth(110); prog.setVisible(False)
        row.addWidget(prog)

        if licensed:
            # Licensed tool — show "Buy License" + "Browse..." buttons instead
            buy_btn = QPushButton("🛒  Buy License")
            buy_btn.setFixedWidth(110)
            buy_btn.setStyleSheet(f"background:{C['yellow']};color:#111;border:none;font-weight:bold;border-radius:3px;")
            _url = license_url
            buy_btn.clicked.connect(lambda _, u=_url: self._open_url(u))
            row.addWidget(buy_btn)
            locate_btn = QPushButton("📂  Locate exe")
            locate_btn.setFixedWidth(100)
            locate_btn.setStyleSheet(f"background:{C['panel']};color:{C['muted']};border:1px solid {C['border']};border-radius:3px;")
            locate_btn.clicked.connect(lambda _, t=task, s=status: self._locate_exe(t, s))
            row.addWidget(locate_btn)
            launch = QPushButton("▶  Launch"); launch.setFixedWidth(90)
            launch.setEnabled(exe is not None)
            if not exe: launch.setStyleSheet(f"background:{C['panel']};color:#555;border:1px solid {C['border']};")
            launch.clicked.connect(lambda _, t=task, lb=launch: self._launch(t, lb))
            row.addWidget(launch)
            self.cards.append({"task": task, "status": status, "dl_btn": locate_btn, "launch_btn": launch, "prog": prog})
        elif task.task_type == "builtin":
            # Windows built-in — just show an Open button, no download needed
            status.setText("🪟")
            badge = QLabel("Windows Built-in")
            badge.setStyleSheet(
                f"background:#0f2a2a;color:{C['accent']};border:1px solid {C['accent']};"
                f"border-radius:3px;padding:1px 6px;font-size:7.5pt;")
            row.addWidget(badge)
            row.addStretch()
            launch = QPushButton("▶  Open")
            launch.setFixedWidth(90)
            launch.setStyleSheet(
                f"background:{C['accent']};color:#000;border:none;"
                f"border-radius:3px;font-weight:bold;padding:4px;")
            launch.clicked.connect(lambda _, t=task, lb=launch: self._launch(t, lb))
            row.addWidget(launch)
            self.cards.append({"task": task, "status": status, "dl_btn": launch, "launch_btn": launch, "prog": prog})
        else:
            dl_btn = QPushButton("⬇ Download" if not exe else "🔄 Re-dl")
            dl_btn.setFixedWidth(100)
            dl_btn.setStyleSheet(f"background:{C['panel']};color:{C['muted']};border:1px solid {C['border']};border-radius:3px;")
            dl_btn.clicked.connect(lambda _, t=task, s=status, d=dl_btn, p=prog: self._download(t, s, d, p))
            row.addWidget(dl_btn)
            launch = QPushButton("▶  Launch"); launch.setFixedWidth(90)
            launch.setEnabled(exe is not None)
            if not exe: launch.setStyleSheet(f"background:{C['panel']};color:#555;border:1px solid {C['border']};")
            launch.clicked.connect(lambda _, t=task, lb=launch: self._launch(t, lb))
            row.addWidget(launch)
            self.cards.append({"task": task, "status": status, "dl_btn": dl_btn, "launch_btn": launch, "prog": prog})
        return card

    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def _locate_exe(self, task, status_lbl):
        """Let user browse to a manually downloaded/installed exe."""
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, f"Locate {task.name} executable", "", "Executables (*.exe)")
        if not path:
            return
        # Copy into tools folder so Repair-O can find it next time
        import shutil
        dest_dir = os.path.join(TOOLS_DIR, task.tool_id)
        os.makedirs(dest_dir, exist_ok=True)
        try:
            # Read manifest to get expected filename
            import json as _j
            with open(os.path.join(BUNDLE_DIR, "tools_manifest.json")) as _f:
                manifest = _j.load(_f)
            fname = next((t["filename"] for t in manifest["tools"] if t["id"] == task.tool_id), os.path.basename(path))
        except Exception:
            fname = os.path.basename(path)
        dest = os.path.join(dest_dir, fname)
        if path != dest:
            shutil.copy2(path, dest)
        status_lbl.setText("✅")
        for c in self.cards:
            if c["task"].tool_id == task.tool_id:
                c["launch_btn"].setEnabled(True)
        QMessageBox.information(self, "Tool Located", f"{task.name} is now registered.\nClick Launch to run it.")

    def _download(self, task, status, dl_btn, prog):
        try:
            from downloader import ToolDownloader
            dl = ToolDownloader(BUNDLE_DIR, tools_dir=TOOLS_DIR)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e)); return

        dl_btn.setEnabled(False)
        prog.setVisible(True)
        prog.setRange(0, 100)
        prog.setValue(0)
        _cards_ref = self.cards
        _tid = task.tool_id
        _name = task.name

        # Use a DownloadWorker QThread so signals work correctly
        worker = DownloadWorker(dl, _tid)
        worker.sig_progress.connect(lambda p: prog.setValue(p))
        def _on_done():
            prog.setVisible(False)
            prog.setValue(0)
            status.setText("✅")
            dl_btn.setText("🔄 Re-dl")
            dl_btn.setEnabled(True)
            for c in _cards_ref:
                if c["task"].tool_id == _tid:
                    c["launch_btn"].setEnabled(True)
        def _on_err(msg):
            prog.setVisible(False)
            prog.setValue(0)
            dl_btn.setEnabled(True)
            status.setText("❌")
            QMessageBox.warning(self, f"Download Failed: {_name}", msg)
        worker.sig_done.connect(_on_done)
        worker.sig_error.connect(_on_err)
        # Keep reference so it isn't garbage collected
        if not hasattr(self, "_dl_workers"):
            self._dl_workers = []
        self._dl_workers.append(worker)
        worker.finished.connect(lambda w=worker: self._dl_workers.remove(w) if w in self._dl_workers else None)
        worker.start()

    def _launch(self, task, btn):
        # Handle Windows built-in tools
        if task.task_type == "builtin":
            builtin_map = {
                "sysrestore": lambda: _launch_restore_manager(self),
                "devmgmt":    lambda: subprocess.Popen(["mmc","devmgmt.msc"]),
                "diskmgmt":   lambda: subprocess.Popen(["mmc","diskmgmt.msc"]),
                "eventvwr":   lambda: subprocess.Popen(["eventvwr.msc"]),
                "services":   lambda: subprocess.Popen(["services.msc"]),
                "regedit":    lambda: subprocess.Popen(["regedit"]),
                "taskschd":   lambda: subprocess.Popen(["taskschd.msc"]),
                "gpedit":     lambda: subprocess.Popen(["gpedit.msc"]),
                "perfmon":    lambda: subprocess.Popen(["perfmon"]),
                "resmon":     lambda: subprocess.Popen(["resmon"]),
                "msconfig":   lambda: subprocess.Popen(["msconfig"]),
                "msinfo32":   lambda: subprocess.Popen(["msinfo32"]),
                "secpol":     lambda: subprocess.Popen(["secpol.msc"]),
                "certmgr":    lambda: subprocess.Popen(["certmgr.msc"]),
                "dxdiag":     lambda: subprocess.Popen(["dxdiag"]),
            }
            fn = builtin_map.get(task.tool_id)
            if fn:
                try: fn()
                except Exception as e: QMessageBox.warning(self, "Error", str(e))
            return
        exe = tool_exe(task.tool_id)
        if exe: subprocess.Popen([exe])
        else: QMessageBox.information(self, "Not Downloaded", f"Download or locate {task.name} first.")

    def _dl_all(self):
        try:
            import json as _j
            with open(os.path.join(BUNDLE_DIR, "tools_manifest.json")) as _f:
                manifest = _j.load(_f)
            tool_flags = {t["id"]: t for t in manifest.get("tools", [])}
        except Exception:
            tool_flags = {}

        for c in self.cards:
            tid = c["task"].tool_id
            if tool_exe(tid):
                continue  # already downloaded
            flags = tool_flags.get(tid, {})
            if flags.get("licensed"):
                continue  # skip — needs purchase
            if flags.get("nirsoft"):
                continue  # skip — user must add Defender exclusion first
            self._download(c["task"], c["status"], c["dl_btn"], c["prog"])




# ─────────────────────────────────────────────
#  TAB: MIGRATION
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  USER SCAN WORKER  (MigrationTab)
# ─────────────────────────────────────────────
class UserScanWorker(QThread):
    """Scans a drive for user profiles. Uses Qt signals so UI updates
    are always delivered safely on the main thread."""
    found    = pyqtSignal(list)   # emitted with parsed user list on success
    message  = pyqtSignal(str, str)  # (text, colour)
    finished = pyqtSignal()

    def __init__(self, script, drive):
        super().__init__()
        self.script = script
        self.drive  = drive
        self._abort = False

    def abort(self):
        self._abort = True
        self.terminate()   # hard-kill the thread if still running

    def run(self):
        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            r = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                 "-File", self.script, "-SourceDrive", self.drive],
                capture_output=True, text=True, timeout=30, creationflags=flags)
            if self._abort:
                return
            raw = r.stdout.strip()
            if not raw:
                self.message.emit("No user profiles found.", C["yellow"])
                return
            data = json.loads(raw)
            if isinstance(data, dict):
                data = [data]
            self.found.emit(data)
        except subprocess.TimeoutExpired:
            self.message.emit("[ERROR] Scan timed out after 30s.", C["red"])
        except json.JSONDecodeError:
            self.message.emit("[WARN] Could not parse user list. Run as Administrator.", C["yellow"])
        except Exception as e:
            self.message.emit(f"[ERROR] {e}", C["red"])
        finally:
            self.finished.emit()

class MigrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self._scanned_users = []
        self._winold_users  = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        root.addWidget(hdr("Move & Backup", color=C["accent"]))
        root.addWidget(lbl(
            "Back up user data before a reinstall, restore it on the new PC, "
            "or recover files from Windows.old.",
            color=C["muted"]
        ))
        root.addWidget(divider())

        # Mode buttons
        mode_row = QHBoxLayout(); mode_row.setSpacing(10)
        self._mode_btns = {}
        modes = [
            ("backup",  "💾  Backup This PC",            C["green"]),
            ("restore", "📥  Restore to This PC",        C["accent"]),
            ("winold",  "🪟  Recover from Windows.old",  C["yellow"]),
        ]
        for mid, mlabel, mcolor in modes:
            btn = QPushButton(mlabel)
            btn.setCheckable(True)
            text_color = "#111" if mcolor == C["yellow"] else "white"
            btn.setStyleSheet(
                f"QPushButton {{background:{C['panel2']};color:{C['muted']};"
                f"border:1px solid {C['border']};border-radius:8px;"
                f"padding:14px 10px;font-size:10pt;font-weight:bold;}}"
                f"QPushButton:checked {{background:{mcolor};color:{text_color};border:none;}}"
                f"QPushButton:hover:!checked {{border-color:{mcolor};color:{C['text']};}}"
            )
            btn.clicked.connect(lambda _, m=mid: self._set_mode(m))
            mode_row.addWidget(btn)
            self._mode_btns[mid] = btn
        root.addLayout(mode_row)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_backup_page())   # 0
        self.stack.addWidget(self._build_restore_page())  # 1
        self.stack.addWidget(self._build_winold_page())   # 2
        root.addWidget(self.stack, 1)

        # Shared output
        root.addWidget(divider())
        root.addWidget(lbl("Output:", color=C["muted"]))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(155)
        self.output.setStyleSheet(
            f"background:{C['bg']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:6px;"
            f"font-family:Consolas,monospace;font-size:8.5pt;padding:6px;"
        )
        root.addWidget(self.output)
        self.prog_bar = QProgressBar()
        self.prog_bar.setValue(0)
        root.addWidget(self.prog_bar)

        self._set_mode("backup")

    def _set_mode(self, mode):
        pages = {"backup": 0, "restore": 1, "winold": 2}
        self.stack.setCurrentIndex(pages.get(mode, 0))
        for mid, btn in self._mode_btns.items():
            btn.setChecked(mid == mode)

    # ── BACKUP PAGE ───────────────────────────────────────────────────────────
    def _build_backup_page(self):
        w = QWidget()
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(0, 8, 0, 0)

        dr = QHBoxLayout()
        dr.addWidget(lbl("Source drive:", color=C["muted"]))
        self.bk_drive = QComboBox(); self.bk_drive.setFixedWidth(70)
        self._fill_drives(self.bk_drive)
        self.bk_drive.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:4px;")
        dr.addWidget(self.bk_drive)
        scan_btn = QPushButton("  Scan for Users")
        scan_btn.setStyleSheet(
            f"background:{C['accent']};color:white;"
            f"border:none;border-radius:5px;padding:6px 14px;font-weight:bold;")
        scan_btn.clicked.connect(self._scan_backup_users)
        dr.addWidget(scan_btn)
        self.bk_cancel_btn = QPushButton("🛑  Cancel")
        self.bk_cancel_btn.setEnabled(False)
        self.bk_cancel_btn.setStyleSheet(
            f"background:{C['red']};color:white;"
            f"border:none;border-radius:5px;padding:6px 14px;font-weight:bold;")
        self.bk_cancel_btn.clicked.connect(self._cancel_scan)
        dr.addWidget(self.bk_cancel_btn)
        dr.addStretch()
        lay.addLayout(dr)

        lay.addWidget(lbl("Users to back up:", color=C["muted"]))
        self.bk_user_list = QListWidget()
        self.bk_user_list.setMaximumHeight(95)
        self.bk_user_list.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;")
        lay.addWidget(self.bk_user_list)

        lay.addWidget(lbl("Folders to include:", color=C["muted"]))
        fold_row = QHBoxLayout(); fold_row.setSpacing(12)
        self.bk_checks = {}
        for f in ["Desktop","Documents","Downloads","Pictures","Videos","Music","AppData","Favorites"]:
            cb = QCheckBox(f); cb.setChecked(f not in ["AppData","Favorites"])
            cb.setStyleSheet(f"color:{C['text']};")
            self.bk_checks[f] = cb; fold_row.addWidget(cb)
        fold_row.addStretch(); lay.addLayout(fold_row)

        opts = QHBoxLayout()
        self.bk_skip_hidden = QCheckBox("Skip hidden files"); self.bk_skip_hidden.setChecked(True)
        self.bk_skip_hidden.setStyleSheet(f"color:{C['text']};")
        self.bk_skip_sys = QCheckBox("Skip system files"); self.bk_skip_sys.setChecked(True)
        self.bk_skip_sys.setStyleSheet(f"color:{C['text']};")
        opts.addWidget(self.bk_skip_hidden); opts.addWidget(self.bk_skip_sys); opts.addStretch()
        lay.addLayout(opts)

        dst_row = QHBoxLayout()
        dst_row.addWidget(lbl("Save backup to:", color=C["muted"]))
        self.bk_dest = QLineEdit()
        self.bk_dest.setPlaceholderText("Choose an external drive or folder  e.g.  D:\\  or  E:\\Backups")
        self.bk_dest.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:6px;")
        dst_row.addWidget(self.bk_dest, 1)
        br = QPushButton("Browse...")
        br.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 10px;")
        br.clicked.connect(lambda: self._browse(self.bk_dest))
        dst_row.addWidget(br); lay.addLayout(dst_row)

        run_btn = QPushButton("  Start Backup")
        run_btn.setStyleSheet(
            f"background:{C['green']};color:white;"
            f"border:none;border-radius:6px;padding:12px;font-weight:bold;font-size:11pt;")
        run_btn.clicked.connect(self._run_backup)
        lay.addWidget(run_btn); lay.addStretch()
        return w

    # ── RESTORE PAGE ──────────────────────────────────────────────────────────
    def _build_restore_page(self):
        w = QWidget()
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(0, 8, 0, 0)

        lay.addWidget(lbl(
            "Point to the RepairO_Backup_... folder created during backup.",
            color=C["muted"]))

        src_row = QHBoxLayout()
        src_row.addWidget(lbl("Backup folder:", color=C["muted"]))
        self.rs_src = QLineEdit()
        self.rs_src.setPlaceholderText("e.g.  D:\\RepairO_Backup_John_20260220")
        self.rs_src.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:6px;")
        src_row.addWidget(self.rs_src, 1)
        br1 = QPushButton("Browse...")
        br1.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 10px;")
        br1.clicked.connect(lambda: self._browse(self.rs_src))
        src_row.addWidget(br1); lay.addLayout(src_row)

        dst_row = QHBoxLayout()
        dst_row.addWidget(lbl("Restore into profile:", color=C["muted"]))
        self.rs_dest = QLineEdit()
        self.rs_dest.setPlaceholderText("e.g.  C:\\Users\\John")
        self.rs_dest.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:6px;")
        dst_row.addWidget(self.rs_dest, 1)
        br2 = QPushButton("Browse...")
        br2.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 10px;")
        br2.clicked.connect(lambda: self._browse(self.rs_dest))
        dst_row.addWidget(br2); lay.addLayout(dst_row)

        self.rs_skip = QCheckBox("Skip files that already exist in destination  (recommended)")
        self.rs_skip.setChecked(True)
        self.rs_skip.setStyleSheet(f"color:{C['text']};")
        lay.addWidget(self.rs_skip)

        lay.addWidget(lbl(
            "  Make sure the destination user account already exists in Windows "
            "before restoring. If not, create it first in Settings > Accounts.",
            color=C["yellow"]))

        run_btn = QPushButton("  Restore Now")
        run_btn.setStyleSheet(
            f"background:{C['accent']};color:white;"
            f"border:none;border-radius:6px;padding:12px;font-weight:bold;font-size:11pt;")
        run_btn.clicked.connect(self._run_restore)
        lay.addWidget(run_btn); lay.addStretch()
        return w

    # ── WINDOWS.OLD PAGE ──────────────────────────────────────────────────────
    def _build_winold_page(self):
        w = QWidget()
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(0, 8, 0, 0)

        lay.addWidget(lbl(
            "Windows.old is created when you reinstall Windows without formatting. "
            "Use this to recover documents, pictures, and settings from the old install.",
            color=C["muted"]))

        dr_row = QHBoxLayout()
        dr_row.addWidget(lbl("Drive:", color=C["muted"]))
        self.wo_drive = QComboBox(); self.wo_drive.setFixedWidth(70)
        self._fill_drives(self.wo_drive)
        self.wo_drive.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:4px;")
        dr_row.addWidget(self.wo_drive)
        scan_wo = QPushButton("  Scan Windows.old")
        scan_wo.setStyleSheet(
            f"background:{C['yellow']};color:#111;"
            f"border:none;border-radius:5px;padding:6px 14px;font-weight:bold;")
        scan_wo.clicked.connect(self._scan_winold)
        dr_row.addWidget(scan_wo); dr_row.addStretch()
        lay.addLayout(dr_row)

        self.wo_result = QTextEdit(); self.wo_result.setReadOnly(True)
        self.wo_result.setMaximumHeight(110)
        self.wo_result.setPlaceholderText("Scan results will appear here...")
        self.wo_result.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;"
            f"font-family:Consolas,monospace;font-size:8.5pt;padding:6px;")
        lay.addWidget(self.wo_result)

        user_row = QHBoxLayout()
        user_row.addWidget(lbl("Recover user:", color=C["muted"]))
        self.wo_user = QComboBox(); self.wo_user.setMinimumWidth(160)
        self.wo_user.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:4px;")
        user_row.addWidget(self.wo_user); user_row.addStretch()
        lay.addLayout(user_row)

        dst_row = QHBoxLayout()
        dst_row.addWidget(lbl("Restore into:", color=C["muted"]))
        self.wo_dest = QLineEdit()
        self.wo_dest.setPlaceholderText("e.g.  C:\\Users\\John")
        self.wo_dest.setStyleSheet(
            f"background:{C['panel2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:6px;")
        dst_row.addWidget(self.wo_dest, 1)
        br3 = QPushButton("Browse...")
        br3.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 10px;")
        br3.clicked.connect(lambda: self._browse(self.wo_dest))
        dst_row.addWidget(br3); lay.addLayout(dst_row)

        run_btn = QPushButton("  Recover Now")
        run_btn.setStyleSheet(
            f"background:{C['yellow']};color:#111;"
            f"border:none;border-radius:6px;padding:12px;font-weight:bold;font-size:11pt;")
        run_btn.clicked.connect(self._run_winold)
        lay.addWidget(run_btn); lay.addStretch()
        return w

    # ── Shared helpers ────────────────────────────────────────────────────────
    def _fill_drives(self, combo):
        import string
        combo.clear()
        for letter in string.ascii_uppercase:
            if os.path.exists(f"{letter}:\\"):
                combo.addItem(f"{letter}:", f"{letter}:")

    def _browse(self, line_edit):
        from PyQt5.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            line_edit.setText(folder)

    def _log(self, msg, color=None):
        _c = color or C["text"]
        QTimer.singleShot(0, lambda m=msg, c=_c:
            self.output.append(f'<span style="color:{c};">{m}</span>'))

    def _run_ps(self, script_name, params, long_running=False):
        self.output.clear()
        if long_running:
            self.prog_bar.setRange(0, 0)
        else:
            self.prog_bar.setRange(0, 100)
            self.prog_bar.setValue(10)
        script = os.path.join(SCRIPTS_DIR, script_name)
        if not os.path.exists(script):
            self._log(f"[ERROR] Script not found: {script_name}", C["red"])
            self.prog_bar.setRange(0, 100)
            return
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script] + params
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        def worker():
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, creationflags=flags)
                for line in proc.stdout:
                    line = line.rstrip()
                    if not line: continue
                    c = C["green"]  if line.startswith("[OK]")  else \
                        C["red"]    if "[ERROR]" in line         else \
                        C["yellow"] if "[WARN]" in line or "[INFO]" in line else \
                        C["muted"]  if line.startswith("----")  else C["text"]
                    self._log(line, c)
                proc.wait()
            except Exception as e:
                self._log(f"[ERROR] {e}", C["red"])
            finally:
                QTimer.singleShot(0, lambda: (
                    self.prog_bar.setRange(0, 100),
                    self.prog_bar.setValue(100)
                ))
        threading.Thread(target=worker, daemon=True).start()

    def _scan_backup_users(self):
        drive = self.bk_drive.currentText()
        self.bk_user_list.clear()
        self._scanned_users = []
        script = os.path.join(SCRIPTS_DIR, "migration_scan_users.ps1")
        if not os.path.exists(script):
            self._log("[ERROR] migration_scan_users.ps1 not found.", C["red"]); return

        self._log(f"Scanning {drive} for user profiles...", C["muted"])
        self.bk_cancel_btn.setEnabled(True)
        self.prog_bar.setRange(0, 0)  # indeterminate spinner

        self._scan_worker = UserScanWorker(script, drive)
        self._scan_worker.found.connect(self._on_users_found)
        self._scan_worker.message.connect(lambda msg, col: self._log(msg, col))
        self._scan_worker.finished.connect(self._on_scan_finished)
        self._scan_worker.start()

    def _cancel_scan(self):
        if hasattr(self, "_scan_worker") and self._scan_worker.isRunning():
            self._scan_worker.abort()
        self._log("Scan cancelled.", C["yellow"])
        self._on_scan_finished()

    def _on_users_found(self, data):
        self._scanned_users = data
        self.bk_user_list.clear()
        for u in data:
            size = u.get("SizeGB", 0)
            item = QListWidgetItem(f"  {u['Name']}   (~{size} GB)")
            item.setData(Qt.UserRole, u)
            item.setCheckState(Qt.Checked)
            self.bk_user_list.addItem(item)
        self._log(f"[OK] Found {len(data)} user(s). Check the ones to back up.", C["green"])

    def _on_scan_finished(self):
        self.bk_cancel_btn.setEnabled(False)
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)

    def _scan_winold(self):
        drive = self.wo_drive.currentText()
        self.wo_result.clear(); self.wo_user.clear(); self._winold_users = []
        self._log(f"Scanning {drive}\\Windows.old...", C["muted"])
        script = os.path.join(SCRIPTS_DIR, "migration_windows_old.ps1")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        def worker():
            try:
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                     "-File", script, "-Drive", drive],
                    capture_output=True, text=True, timeout=30, creationflags=flags)
                users, display = [], []
                for line in r.stdout.strip().splitlines():
                    if line.startswith("USERS_JSON:"):
                        try:
                            parsed = json.loads(line[len("USERS_JSON:"):])
                            if isinstance(parsed, dict): parsed = [parsed]
                            users = parsed
                        except Exception: pass
                    else:
                        display.append(line)
                self._winold_users = users
                def update():
                    self.wo_result.setPlainText("\n".join(display))
                    for u in users:
                        self.wo_user.addItem(u.get("Name","Unknown"), u.get("FullName",""))
                    if users:
                        self._log(f"[OK] Found {len(users)} user(s) in Windows.old.", C["green"])
                QTimer.singleShot(0, update)
            except Exception as e:
                QTimer.singleShot(0, lambda: self._log(f"[ERROR] {e}", C["red"]))
        threading.Thread(target=worker, daemon=True).start()

    def _run_backup(self):
        dest = self.bk_dest.text().strip()
        if not dest:
            QMessageBox.warning(self, "No Destination",
                "Please choose a destination drive or folder.\nAn external USB drive is recommended.")
            return
        users = [self.bk_user_list.item(i).data(Qt.UserRole)
                 for i in range(self.bk_user_list.count())
                 if self.bk_user_list.item(i).checkState() == Qt.Checked]
        if not users:
            QMessageBox.warning(self, "No Users", "Scan for users and check at least one.")
            return
        folders = ",".join(k for k, cb in self.bk_checks.items() if cb.isChecked())
        if not folders:
            QMessageBox.warning(self, "No Folders", "Select at least one folder type.")
            return
        extra = []
        if self.bk_skip_hidden.isChecked(): extra += ["-SkipHidden"]
        if self.bk_skip_sys.isChecked():    extra += ["-SkipSystem"]
        for u in users:
            self._run_ps("migration_backup.ps1", [
                "-SourceUser", u["Name"],
                "-SourcePath", u["Path"],
                "-Destination", dest,
                "-Folders", folders,
            ] + extra, long_running=True)

    def _run_restore(self):
        src  = self.rs_src.text().strip()
        dest = self.rs_dest.text().strip()
        if not src or not dest:
            QMessageBox.warning(self, "Missing Info",
                "Please select the backup folder AND the destination profile folder.")
            return
        extra = ["-SkipExisting"] if self.rs_skip.isChecked() else []
        self._run_ps("migration_restore.ps1",
                     ["-BackupPath", src, "-DestPath", dest] + extra,
                     long_running=True)

    def _run_winold(self):
        user_path = self.wo_user.currentData()
        dest = self.wo_dest.text().strip()
        if not user_path or not dest:
            QMessageBox.warning(self, "Missing Info",
                "Please scan Windows.old, pick a user, and choose a destination folder.")
            return
        self._run_ps("migration_restore.ps1",
                     ["-BackupPath", user_path, "-DestPath", dest, "-SkipExisting"],
                     long_running=True)


class UninstallerTab(QWidget):
    def __init__(self):
        super().__init__()
        self._programs = []
        self._filtered = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(16,12,16,12); root.setSpacing(10)
        root.addWidget(hdr("Remove Software", color=C["red"]))
        root.addWidget(lbl("Scan installed programs. Select one or more to uninstall. Hold Ctrl or Shift to select multiple.", color=C["muted"]))
        root.addWidget(divider())

        # Toolbar
        tb = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Filter programs...")
        self.search.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:6px;padding:6px 10px;font-size:10pt;")
        self.search.textChanged.connect(self._filter)
        tb.addWidget(self.search, 1)
        scan_btn = QPushButton("Scan Installed Programs")
        scan_btn.setStyleSheet(f"background:{C['accent']};color:white;border:none;border-radius:6px;padding:8px 18px;font-weight:bold;")
        scan_btn.clicked.connect(self._scan)
        tb.addWidget(scan_btn)
        root.addLayout(tb)

        self.count_lbl = lbl("Click Scan to load installed programs.", color=C["muted"])
        root.addWidget(self.count_lbl)

        # Split: list | detail+actions
        split = QHBoxLayout(); split.setSpacing(12)

        # Left: program list — multi-select enabled
        self.prog_list = QListWidget()
        self.prog_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.prog_list.setStyleSheet(f"""
            QListWidget {{background:{C['panel']};border:1px solid {C['border']};border-radius:8px;color:{C['text']};font-size:9.5pt;}}
            QListWidget::item {{padding:6px 12px;border-bottom:1px solid {C['border']};}}
            QListWidget::item:selected {{background:{C['accent']};color:white;}}
            QListWidget::item:hover {{background:{C['panel2']};}}
        """)
        self.prog_list.itemSelectionChanged.connect(self._on_selection_changed)
        split.addWidget(self.prog_list, 2)

        # Right: detail panel + action buttons
        detail = QWidget(); detail.setStyleSheet(f"background:{C['panel']};border-radius:8px;")
        dp = QVBoxLayout(detail); dp.setContentsMargins(16,16,16,16); dp.setSpacing(8)

        self.det_name = QLabel("Select a program")
        self.det_name.setWordWrap(True)
        self.det_name.setStyleSheet(f"color:{C['text']};font-size:12pt;font-weight:bold;background:transparent;")
        dp.addWidget(self.det_name)
        self.det_info = lbl("", color=C["muted"])
        self.det_info.setWordWrap(True)
        dp.addWidget(self.det_info)
        self.sel_count = lbl("", color=C["accent"])
        dp.addWidget(self.sel_count)
        dp.addWidget(divider())


        btn_style_green = f"background:{C['green']};color:white;border:none;border-radius:5px;padding:8px 4px;font-weight:bold;font-size:9pt;"
        btn_style_red   = f"background:{C['red']};color:white;border:none;border-radius:5px;padding:8px 4px;font-weight:bold;font-size:9pt;"
        btn_style_muted = f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:5px;padding:8px 4px;font-size:9pt;"

        self.btn_normal = QPushButton("✔  Uninstall")
        self.btn_normal.setEnabled(False)
        self.btn_normal.setStyleSheet(btn_style_green)
        self.btn_normal.setToolTip("Launches each program's own built-in uninstaller")
        self.btn_normal.clicked.connect(self._uninstall_normal)

        self.btn_force = QPushButton("💀  Force Remove")
        self.btn_force.setEnabled(False)
        self.btn_force.setStyleSheet(btn_style_red)
        self.btn_force.setToolTip("Kills processes, deletes files, scrubs registry — use when normal uninstall fails")
        self.btn_force.clicked.connect(self._uninstall_force)

        self.btn_leftovers = QPushButton("🔍  Leftovers")
        self.btn_leftovers.setEnabled(False)
        self.btn_leftovers.setStyleSheet(btn_style_muted)
        self.btn_leftovers.setToolTip("Scan for orphaned files and registry entries (single selection only)")
        self.btn_leftovers.clicked.connect(self._scan_leftovers)

        btn_row = QHBoxLayout(); btn_row.setSpacing(6)
        btn_row.addWidget(self.btn_normal, 2)
        btn_row.addWidget(self.btn_force, 2)
        btn_row.addWidget(self.btn_leftovers, 1)
        dp.addLayout(btn_row)
        dp.addWidget(lbl("Hover over buttons for details  |  Leftovers = single selection only", color=C["muted"]))


        dp.addStretch()
        dp.addWidget(lbl("Output:", color=C["muted"]))
        self.output = QTextEdit(); self.output.setReadOnly(True)
        self.output.setMaximumHeight(160)
        self.output.setStyleSheet(f"background:{C['bg']};color:{C['text']};border:1px solid {C['border']};border-radius:6px;font-family:Consolas,monospace;font-size:8.5pt;padding:6px;")
        dp.addWidget(self.output)
        self.prog_bar = QProgressBar(); self.prog_bar.setValue(0)
        dp.addWidget(self.prog_bar)
        split.addWidget(detail, 3)
        root.addLayout(split, 1)

    def _get_selected_programs(self):
        return [item.data(Qt.UserRole) for item in self.prog_list.selectedItems() if item.data(Qt.UserRole)]

    def _on_selection_changed(self):
        selected = self._get_selected_programs()
        count = len(selected)
        if count == 0:
            self.det_name.setText("Select a program")
            self.det_info.setText("")
            self.sel_count.setText("")
            self.btn_normal.setEnabled(False)
            self.btn_force.setEnabled(False)
            self.btn_leftovers.setEnabled(False)
        elif count == 1:
            p = selected[0]
            self.det_name.setText(p.get("Name", ""))
            sk = p.get("EstimatedSize") or 0
            size_str = f"{sk//1024} MB" if sk > 1024 else f"{sk} KB" if sk else "Unknown"
            self.det_info.setText(
                f"Version:   {p.get('Version') or 'Unknown'}\n"
                f"Publisher: {p.get('Publisher') or 'Unknown'}\n"
                f"Installed: {p.get('InstallDate') or 'Unknown'}\n"
                f"Size:      {size_str}\n"
                f"Location:  {p.get('InstallLocation') or 'Unknown'}"
            )
            self.sel_count.setText("")
            has_u = bool(p.get("UninstallString") or p.get("QuietUninstallString"))
            self.btn_normal.setEnabled(has_u)
            self.btn_force.setEnabled(True)
            self.btn_leftovers.setEnabled(True)
        else:
            self.det_name.setText(f"{count} programs selected")
            names = [p.get("Name","") for p in selected[:5]]
            if count > 5: names.append(f"...and {count-5} more")
            self.det_info.setText("\n".join(names))
            self.sel_count.setText(f"All {count} will be processed one by one.")
            # Enable uninstall if any have an uninstall string
            any_u = any(p.get("UninstallString") or p.get("QuietUninstallString") for p in selected)
            self.btn_normal.setEnabled(any_u)
            self.btn_force.setEnabled(True)
            self.btn_leftovers.setEnabled(False)  # Leftovers only makes sense for one at a time

    def _scan(self):
        self.prog_list.clear()
        self.count_lbl.setText("Scanning...")
        self.output.clear()
        script = os.path.join(SCRIPTS_DIR, "uninstall_list.ps1")
        def worker():
            try:
                flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script],
                    capture_output=True, text=True, timeout=60, creationflags=flags)
                raw = r.stdout.strip()
                if not raw:
                    QTimer.singleShot(0, lambda: self.count_lbl.setText("No programs found."))
                    return
                data = json.loads(raw)
                if isinstance(data, dict): data = [data]
                self._programs = sorted([p for p in data if p.get("Name")], key=lambda x: x["Name"].lower())
                self._filtered = list(self._programs)
                QTimer.singleShot(0, self._populate_list)
            except Exception as e:
                QTimer.singleShot(0, lambda: self.count_lbl.setText(f"Error: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def _populate_list(self):
        self.prog_list.clear()
        for p in self._filtered:
            item = QListWidgetItem(p.get("Name", ""))
            item.setData(Qt.UserRole, p)
            self.prog_list.addItem(item)
        self.count_lbl.setText(f"{len(self._filtered)} programs  ({len(self._programs)} total)  —  Ctrl+Click or Shift+Click to select multiple")

    def _filter(self, text):
        if not self._programs: return
        t = text.lower()
        self._filtered = [p for p in self._programs
                          if t in p.get("Name","").lower() or t in (p.get("Publisher") or "").lower()]
        self._populate_list()

    def _log(self, msg, color=None):
        c = color or C["text"]
        QTimer.singleShot(0, lambda m=msg, _c=c:
            self.output.append(f'<span style="color:{_c};">{m}</span>'))

    def _run_ps_foreground(self, script_name, params):
        """Run a PS script that shows its own UI — don't capture output, just wait."""
        script = os.path.join(SCRIPTS_DIR, script_name)
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script] + params
        flags = 0
        try:
            proc = subprocess.Popen(cmd, creationflags=flags)
            proc.wait()
            return proc.returncode
        except Exception as e:
            return -1

    def _launch_uninstaller_direct(self, uninstall_string):
        """Launch uninstaller directly — fire and forget, don't wait for child processes."""
        import shlex, re
        cmd_str = uninstall_string.strip()
        try:
            if cmd_str.lower().startswith("msiexec"):
                # MSI — wait is reliable since msiexec is a single process
                guid = re.search(r'{[A-F0-9-]+}', cmd_str, re.IGNORECASE)
                if guid:
                    proc = subprocess.Popen(["msiexec.exe", "/x", guid.group(), "/norestart"])
                else:
                    proc = subprocess.Popen(cmd_str, shell=True)
                proc.wait()
                return proc.returncode
            elif cmd_str.startswith('"'):
                end_quote = cmd_str.find('"', 1)
                exe = cmd_str[1:end_quote]
                args = cmd_str[end_quote+1:].strip()
                if args:
                    proc = subprocess.Popen([exe] + shlex.split(args))
                else:
                    proc = subprocess.Popen([exe])
            else:
                proc = subprocess.Popen(cmd_str, shell=True)
            # Fire and forget — don't wait. Many uninstallers (Spotify, Discord, etc.)
            # spawn a child process then exit, so waiting would either return instantly
            # or hang forever. The user completes the uninstall in the window that opened.
            return 0
        except Exception as e:
            return -1

    def _run_ps_background(self, script_name, params):
        """Run a PS script that streams output to the log (no UI)."""
        self.output.clear(); self.prog_bar.setRange(0, 0)
        self._set_btns(False)
        script = os.path.join(SCRIPTS_DIR, script_name)
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script] + params
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        def worker():
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, creationflags=flags)
                for line in proc.stdout:
                    line = line.rstrip()
                    if not line: continue
                    c = C["green"]  if line.startswith("[OK]")   else \
                        C["red"]    if "[ERROR]" in line          else \
                        C["yellow"] if "[WARN]" in line or "[INFO]" in line or "[TIP]" in line or "[FOUND]" in line else C["text"]
                    self._log(line, c)
                proc.wait()
            except Exception as e:
                self._log(f"Error: {e}", C["red"])
            finally:
                QTimer.singleShot(0, lambda: (
                    self.prog_bar.setRange(0, 100),
                    self.prog_bar.setValue(100),
                    self._set_btns(True)
                ))
        threading.Thread(target=worker, daemon=True).start()

    def _set_btns(self, enabled):
        selected = self._get_selected_programs()
        has_any = len(selected) > 0
        any_u = any(p.get("UninstallString") or p.get("QuietUninstallString") for p in selected)
        self.btn_normal.setEnabled(enabled and any_u)
        self.btn_force.setEnabled(enabled and has_any)
        self.btn_leftovers.setEnabled(enabled and len(selected) == 1)

    def _uninstall_normal(self):
        selected = self._get_selected_programs()
        if not selected: return
        names = "\n".join(f"  • {p.get('Name','')}" for p in selected)
        msg = f"Uninstall {len(selected)} program(s)?\n\n{names}\n\nWill attempt silent uninstall first, then standard if needed."
        if QMessageBox.question(self, "Confirm Uninstall", msg,
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        self.output.clear()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        self._set_btns(False)
        script = os.path.join(SCRIPTS_DIR, "uninstall_normal.ps1")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        programs = list(selected)  # copy

        def worker():
            total = len(programs)
            for i, p in enumerate(programs):
                name = p.get("Name", "Unknown")
                u_str = p.get("UninstallString", "") or ""
                q_str = p.get("QuietUninstallString", "") or ""
                pct = int((i / total) * 90)
                QTimer.singleShot(0, lambda v=pct: self.prog_bar.setValue(v))
                self._log(f"\n[{i+1}/{total}] {name}", C["yellow"])
                if not u_str and not q_str:
                    self._log(f"  [WARN] No uninstall string found for {name}", C["yellow"])
                    continue
                try:
                    proc = subprocess.Popen(
                        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                         "-File", script,
                         "-AppName", name,
                         "-UninstallString", u_str,
                         "-QuietString", q_str],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, creationflags=flags)
                    for line in proc.stdout:
                        line = line.rstrip()
                        if line:
                            c = C["green"] if "[OK]" in line else C["yellow"] if "[INFO]" in line or "[WARN]" in line else C["text"]
                            self._log(f"  {line}", c)
                    proc.wait()
                except Exception as e:
                    self._log(f"  [ERROR] {e}", C["red"])
            QTimer.singleShot(0, lambda: (
                self.prog_bar.setValue(100),
                self._set_btns(True),
                self._log("\n[DONE] Uninstall sequence complete. Refresh list to verify.", C["green"])
            ))
        threading.Thread(target=worker, daemon=True).start()

    def _uninstall_force(self):
        selected = self._get_selected_programs()
        if not selected: return
        names = "\n".join(f"  • {p.get('Name','')}" for p in selected)
        msg = f"FORCE REMOVE {len(selected)} program(s)?\n\n{names}\n\nThis will kill processes, delete install folders, and scrub registry entries.\nThis CANNOT be undone."
        if QMessageBox.question(self, "Confirm Force Remove", msg,
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        self.output.clear()
        self.prog_bar.setRange(0, 0)
        self._set_btns(False)
        def worker():
            for p in selected:
                name = p.get("Name", "Unknown")
                self._log(f"[Repair-O] Force removing: {name}", C["text"])
                self._run_ps_foreground("uninstall_force.ps1", [
                    "-ProgramName", name,
                    "-InstallLocation", p.get("InstallLocation") or "",
                    "-RegKey", p.get("RegKey") or ""
                ])
                self._log(f"[OK] {name} — force removal complete", C["green"])
            self._log("----------------------------------------------------", C["muted"])
            self._log(f"[OK] Done. Force removed {len(selected)} program(s).", C["green"])
            QTimer.singleShot(0, lambda: (
                self.prog_bar.setRange(0, 100),
                self.prog_bar.setValue(100),
                self._set_btns(True)
            ))
        threading.Thread(target=worker, daemon=True).start()

    def _scan_leftovers(self):
        selected = self._get_selected_programs()
        if len(selected) != 1: return
        p = selected[0]
        self._run_ps_background("uninstall_leftovers.ps1", [
            "-ProgramName", p.get("Name", ""),
            "-Publisher",   p.get("Publisher") or ""])



# ─────────────────────────────────────────────
#  TAB: MAINTENANCE
# ─────────────────────────────────────────────
class MaintenanceTab(QWidget):
    def __init__(self, queue_ref):
        super().__init__()
        self.queue_ref    = queue_ref
        self._section_idx  = 4
        self._section_name = "Clean Up"
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(10)
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("🧹  Clean Up", C["maintain"])); hrow.addStretch()
        for txt, fn in [("Select All", lambda: [r.cb.setChecked(True) for r in self.rows]),
                         ("Clear All",  lambda: [r.cb.setChecked(False) for r in self.rows])]:
            b = QPushButton(txt); b.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};")
            b.clicked.connect(fn); hrow.addWidget(b)
        add_q = QPushButton("+ Add to Queue")
        add_q.setStyleSheet(f"background:#14532d;color:{C['green']};")
        add_q.clicked.connect(self._add_queue); hrow.addWidget(add_q)
        run = QPushButton("▶▶  Run Selected Now"); run.clicked.connect(self._run_sel)
        hrow.addWidget(run); layout.addLayout(hrow)
        layout.addWidget(lbl("Cleanup, privacy, browser clearing, Windows Update, and post-repair installs.", color=C["muted"]))
        layout.addWidget(divider())
        groups = [
            ("🗑  Disk & Temp Cleanup", [t for t in MAINTENANCE_TASKS if t.task_id.startswith("maint_temp") or t.task_id in ("maint_diskclean","maint_softwaredist","maint_winold","maint_winsxs","maint_msiorphans","maint_ghostdev","maint_notifcache","maint_temprofiles")]),
            ("🔒  Privacy & Browser",   [t for t in MAINTENANCE_TASKS if t.task_id.startswith("maint_quick") or t.task_id.startswith("maint_chrome") or t.task_id.startswith("maint_ff") or t.task_id.startswith("maint_edge") or t.task_id.startswith("maint_allbrow") or t.task_id in ("maint_eventlogs","maint_errreports","maint_shellcache")]),
            ("🔄  Updates & Reports",   [t for t in MAINTENANCE_TASKS if t.task_id in ("maint_wu","maint_battery","maint_power")]),
            ("📦  Post-Repair Installs",[t for t in MAINTENANCE_TASKS if t.task_id.startswith("install_")]),
        ]
        scroll, self.rows = build_task_section_grouped(groups, queue_ref, C["maintain"])
        layout.addWidget(scroll)

    def _add_queue(self):
        for r in self.rows:
            if r.is_checked(): self.queue_ref.add_task(r.task)

    def _run_sel(self):
        sel = [r.task for r in self.rows if r.is_checked()]
        if not sel: QMessageBox.information(self,"Repair-O","No tasks selected."); return
        self.queue_ref.add_tasks_and_run(sel)
        main_win = self.window()
        if hasattr(main_win, "tabs"): main_win.tabs.setCurrentIndex(8)


# ─────────────────────────────────────────────
#  TAB: TWEAKS
# ─────────────────────────────────────────────
class TweaksTab(QWidget):
    def __init__(self, queue_ref):
        super().__init__()
        self.queue_ref    = queue_ref
        self._section_idx  = 5
        self._section_name = "Speed Up"
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(10)
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("🚀  Speed Up", C["tweaks"])); hrow.addStretch()
        warn = QLabel("⚠  All tweaks are safe registry/system changes. A restore point is recommended before applying.")
        warn.setStyleSheet(f"color:{C['yellow']};font-size:8.5pt;")
        hrow.addWidget(warn)
        hrow.addSpacing(12)
        for txt, fn in [("Select All", lambda: [r.cb.setChecked(True) for r in self.rows]),
                         ("Clear All",  lambda: [r.cb.setChecked(False) for r in self.rows])]:
            b = QPushButton(txt); b.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};")
            b.clicked.connect(fn); hrow.addWidget(b)
        add_q = QPushButton("+ Add to Queue")
        add_q.setStyleSheet(f"background:#14532d;color:{C['green']};")
        add_q.clicked.connect(self._add_queue); hrow.addWidget(add_q)
        run = QPushButton("▶▶  Apply Selected"); run.clicked.connect(self._run_sel)
        hrow.addWidget(run); layout.addLayout(hrow)
        layout.addWidget(divider())
        groups = [
            ("🚀  Startup & Shutdown",     [t for t in TWEAKS_TASKS if t.task_id in ("twk_no_delay","twk_prefetch","twk_fast_shutdown")]),
            ("🖥  Display Performance",    [t for t in TWEAKS_TASKS if t.task_id in ("twk_no_anim","twk_menu_speed","twk_file_list","twk_icon_cache")]),
            ("⚙  System Performance",     [t for t in TWEAKS_TASKS if t.task_id in ("twk_foreground","twk_cpu_fg","twk_no_store_bg","twk_no_error_rpt","twk_no_default_reset")]),
            ("🌐  Networking",             [t for t in TWEAKS_TASKS if t.task_id in ("twk_dns_cache","twk_tcpip","twk_lan")]),
            ("💥  BSOD & Crash Diagnostics", [t for t in TWEAKS_TASKS if t.task_id in ("twk_bsod_no_reboot","twk_bsod_reboot","twk_minidumps","twk_classic_bsod","twk_check_dumps")]),
            ("🕐  Clock & Time Sync",      [t for t in TWEAKS_TASKS if t.task_id in ("twk_sync_clock","twk_enable_timesync")]),
        ]
        scroll, self.rows = build_task_section_grouped(groups, queue_ref, C["tweaks"])
        layout.addWidget(scroll)

    def _add_queue(self):
        for r in self.rows:
            if r.is_checked(): self.queue_ref.add_task(r.task)

    def _run_sel(self):
        sel = [r.task for r in self.rows if r.is_checked()]
        if not sel: QMessageBox.information(self,"Repair-O","No tasks selected."); return
        self.queue_ref.add_tasks_and_run(sel)
        main_win = self.window()
        if hasattr(main_win, "tabs"): main_win.tabs.setCurrentIndex(8)




# ─────────────────────────────────────────────
#  DOWNLOAD WORKER — QThread for safe progress signals
# ─────────────────────────────────────────────
class DownloadWorker(QThread):
    sig_progress = pyqtSignal(int)   # 0-100
    sig_done     = pyqtSignal()
    sig_error    = pyqtSignal(str)

    def __init__(self, downloader, tool_id):
        super().__init__()
        self.downloader = downloader
        self.tool_id    = tool_id

    def run(self):
        """Run the download synchronously inside this QThread so signals fire correctly."""
        def on_prog(pct, msg):
            self.sig_progress.emit(int(pct))
        def on_done(tid):
            self.sig_done.emit()
        def on_err(tid, msg):
            self.sig_error.emit(str(msg))
        # Call _download_thread directly (synchronous) rather than spawning another thread
        t = self.downloader.tools.get(self.tool_id)
        if not t:
            self.sig_error.emit(f"Unknown tool: {self.tool_id}")
            return
        self.downloader._download_thread(t, on_prog, on_done, on_err)


# ─────────────────────────────────────────────
#  RUN WORKER — QThread that executes tasks safely
# ─────────────────────────────────────────────
class RunWorker(QThread):
    sig_log        = pyqtSignal(str, str)
    sig_progress   = pyqtSignal(int, str, int, int, str)
    sig_task_state = pyqtSignal(str, str)
    sig_done       = pyqtSignal(int, int, int)

    def __init__(self, tasks, scripts_dir):
        super().__init__()
        self.tasks       = tasks
        self.scripts_dir = scripts_dir

    def log(self, msg, color=None):
        self.sig_log.emit(str(msg), color or C["text"])

    def run(self):
        import time as _time
        from datetime import datetime

        tasks   = self.tasks
        total   = len(tasks)
        results = {"done": 0, "error": 0}

        self.log(f"[Repair-O] Starting {total} task(s)", C["accent"])

        for idx, task in enumerate(tasks):
            pct  = int(idx / total * 100)
            name = task.name
            tid  = task.task_id

            self.sig_progress.emit(pct, f"Task {idx+1}/{total}", 0, 0, f"⏳  Running: {name}")
            self.sig_task_state.emit(tid, f"  ⏳ {name}")
            self.log(f"\n{'─'*50}", C["border"])
            self.log(f"[{idx+1}/{total}] {name}", C["accent"])

            ok = self._exec(task)

            if ok:
                results["done"] += 1
                self.log(f"  ✅ {name}", C["green"])
                self.sig_task_state.emit(tid, f"  ✅ {name}")
            else:
                results["error"] += 1
                self.log(f"  ❌ {name}", C["red"])
                self.sig_task_state.emit(tid, f"  ❌ {name}")

        self.log(f"\n[Repair-O] Queue complete. ✅ {results['done']} succeeded  ❌ {results['error']} failed", C["accent"])
        self.sig_done.emit(results["done"], results["error"], total)

    def _exec(self, task):
        import time as _time
        from datetime import datetime
        start = datetime.now()

        if task.task_type in ("tool", "builtin"):
            exe = tool_exe(task.tool_id)
            if exe:
                p = subprocess.Popen([exe]); p.wait()
                return p.returncode == 0
            else:
                self.log(f"  ⚠ Not downloaded: {task.name}", C["yellow"])
                return False

        script = task.script_path
        if not script or not os.path.exists(script):
            self.log(f"  [Stub] {task.script} not implemented", C["yellow"])
            return True

        is_long = task.task_id in LONG_RUNNING_TASKS
        if is_long:
            self.sig_progress.emit(-1, "", -1, 1, "")  # indeterminate
            self.log(f"  ⏳ This task may take several minutes...", C["muted"])
        else:
            self.sig_progress.emit(-1, "", 10, 0, "")

        try:
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script]
            if task.script_args:
                cmd += task.script_args
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)

            last_tick = _time.time()
            for line in proc.stdout:
                line = line.rstrip()
                if not line:
                    continue
                color = (C["green"]  if line.startswith("[OK]")   else
                         C["red"]    if "[ERROR]" in line          else
                         C["yellow"] if any(t in line for t in ("[WARN]","[INFO]","[TIP]","[FOUND]")) else
                         C["text"])
                self.log(f"    {line}", color)
                if is_long and (_time.time() - last_tick) > 5:
                    elapsed = int((datetime.now() - start).total_seconds())
                    m, s   = divmod(elapsed, 60)
                    self.sig_progress.emit(-1, "", -1, 1, f"⏳ Running: {task.name} ({m}m {s:02d}s)")
                    last_tick = _time.time()

            proc.wait()
            elapsed = int((datetime.now() - start).total_seconds())
            m, s    = divmod(elapsed, 60)
            self.sig_progress.emit(-1, "", 100, 0, "")
            self.log(f"  ⏱ Finished in {m}m {s:02d}s", C["muted"])
            return proc.returncode == 0

        except Exception as e:
            self.log(f"  Exception: {e}", C["red"])
            return False


# ─────────────────────────────────────────────
#  TAB 6: RUN QUEUE
# ─────────────────────────────────────────────
class RunQueueTab(QWidget):
    def __init__(self):
        super().__init__()
        self.running = False
        self._nav_callback  = None   # set by RepairO to allow navigation
        self._source_section = None  # stack index the user came from
        self._session_log   = []     # list of (task_name, status, timestamp)
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(10)
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("✅  Run Tasks", C["queue"])); hrow.addStretch()
        # Back to source button — hidden until we know where user came from
        self.back_src_btn = QPushButton("⬅  Back to Section")
        self.back_src_btn.setStyleSheet(
            f"background:{C['panel2']};color:{C['accent']};border:1px solid {C['accent']};"
            f"border-radius:4px;padding:4px 12px;font-weight:bold;")
        self.back_src_btn.setVisible(False)
        self.back_src_btn.clicked.connect(self._back_to_source)
        hrow.addWidget(self.back_src_btn)
        # Session report button
        self.report_btn = QPushButton("📄  Session Report")
        self.report_btn.setStyleSheet(
            f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:4px 12px;")
        self.report_btn.clicked.connect(self._show_report)
        hrow.addWidget(self.report_btn)
        clr = QPushButton("🗑  Clear Queue")
        clr.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};")
        clr.clicked.connect(self.clear); hrow.addWidget(clr)
        self.run_btn = QPushButton("▶▶  Run All")
        self.run_btn.setStyleSheet(f"background:#14532d;color:{C['green']};font-size:11pt;font-weight:800;")
        self.run_btn.clicked.connect(self.run_all); hrow.addWidget(self.run_btn)
        layout.addLayout(hrow)
        layout.addWidget(lbl("Add tasks from Fast Fixes, Fix & Repair, Clean Up, and Speed Up. Drag to reorder. Tasks run sequentially.", color=C["muted"]))
        layout.addWidget(divider())
        self.overall = QProgressBar(); self.overall.setFormat("Queue: 0 tasks"); self.overall.setValue(0)
        layout.addWidget(self.overall)
        splitter = QSplitter(Qt.Horizontal)
        # Left: queue list
        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0)
        ll.addWidget(lbl("Task Queue", bold=True, color=C["accent"]))
        self.qlist = QListWidget(); self.qlist.setDragDropMode(QAbstractItemView.InternalMove)
        ll.addWidget(self.qlist)
        rem = QPushButton("Remove Selected")
        rem.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};")
        rem.clicked.connect(self._remove); ll.addWidget(rem)
        splitter.addWidget(left)
        # Right: output
        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0)
        rl.addWidget(lbl("Live Output", bold=True, color=C["accent"]))
        self.current_lbl = lbl("No task running.", color=C["muted"]); rl.addWidget(self.current_lbl)
        self.task_prog = QProgressBar(); self.task_prog.setValue(0); rl.addWidget(self.task_prog)
        self.output = QTextEdit(); self.output.setReadOnly(True); rl.addWidget(self.output)
        splitter.addWidget(right); splitter.setSizes([300,680])
        layout.addWidget(splitter)
        self.summary = lbl("", color=C["muted"]); layout.addWidget(self.summary)

    def add_task(self, task):
        for i in range(self.qlist.count()):
            if self.qlist.item(i).data(Qt.UserRole) == task.task_id: return
        item = QListWidgetItem(f"  {task.name}")
        item.setData(Qt.UserRole, task.task_id)
        colors = {"triage": C["triage"], "treat": C["treat"], "maintain": C["maintain"], "tweaks": C["tweaks"]}
        item.setForeground(QColor(colors.get(task.category, C["text"])))
        self.qlist.addItem(item)
        self._update_count()
        self._log(f"[Queue] Added: {task.name}", C["muted"])

    def set_source_section(self, section_idx, section_name):
        """Called before navigating here so we know where to go back."""
        self._source_section = section_idx
        self._source_name    = section_name
        self.back_src_btn.setText(f"⬅  Back to {section_name}")
        self.back_src_btn.setVisible(True)

    def _back_to_source(self):
        if self._nav_callback and self._source_section is not None:
            self._nav_callback(self._source_section)

    def add_tasks_and_run(self, tasks):
        # Stop any running job first
        if self.running:
            QMessageBox.information(self, "Repair-O", "A task is already running. Wait for it to finish.")
            return
        # Clear queue completely so previous runs don't block re-adding
        self.qlist.clear()
        self._update_count()
        for t in tasks:
            self.add_task(t)
        if self.qlist.count() == 0:
            QMessageBox.information(self, "Repair-O", "No tasks could be added to the queue.")
            return
        self.run_all()

    def clear(self):
        self.qlist.clear(); self._update_count()
        self._log("[Queue] Cleared.", C["muted"])

    def _remove(self):
        row = self.qlist.currentRow()
        if row >= 0: self.qlist.takeItem(row); self._update_count()

    def _update_count(self):
        n = self.qlist.count()
        self.overall.setFormat(f"Queue: {n} task{'s' if n!=1 else ''}")

    def run_all(self):
        if self.running: return
        if self.qlist.count() == 0:
            QMessageBox.information(self,"Repair-O","Run Queue is empty."); return
        ids   = [self.qlist.item(i).data(Qt.UserRole) for i in range(self.qlist.count())]
        tasks = [ALL_TASKS[tid] for tid in ids if tid in ALL_TASKS]
        self.running = True
        self.run_btn.setEnabled(False)
        self.run_btn.setText("⏳  Running...")
        self.output.clear()
        self.summary.setText("")

        # Use QThread with signals so ALL widget updates happen on main thread
        self._worker = RunWorker(tasks, SCRIPTS_DIR)
        self._worker.sig_log.connect(self._on_log)
        self._worker.sig_progress.connect(self._on_progress)
        self._worker.sig_task_state.connect(self._on_task_state)
        self._worker.sig_done.connect(self._on_done)
        self._worker.start()

    def _on_log(self, msg, color):
        self.output.append(f'<span style="color:{color};">{msg}</span>')
        # Track completed/failed tasks for session report
        if msg.startswith("✅") or msg.startswith("❌"):
            from datetime import datetime
            self._session_log.append((datetime.now().strftime("%H:%M:%S"), msg))

    def _on_progress(self, overall_pct, overall_lbl, task_pct, task_range, current_lbl):
        # task_range: 0=normal 0-100, 1=indeterminate
        if task_range == 1:
            self.task_prog.setRange(0, 0)
        else:
            self.task_prog.setRange(0, 100)
        if task_pct >= 0:
            if task_range == 0:
                self.task_prog.setValue(task_pct)
        if overall_pct >= 0:
            self.overall.setValue(overall_pct)
        if overall_lbl:
            self.overall.setFormat(overall_lbl)
        if current_lbl:
            self.current_lbl.setText(current_lbl)

    def _on_task_state(self, task_id, display_text):
        for i in range(self.qlist.count()):
            if self.qlist.item(i).data(Qt.UserRole) == task_id:
                self.qlist.item(i).setText(display_text)

    def _on_done(self, done_count, error_count, total):
        self.overall.setValue(100)
        self.overall.setFormat(f"Done: {done_count}✅  Errors: {error_count}❌")
        self.current_lbl.setText("Queue complete.")
        self.summary.setText(f"✅ {done_count} succeeded  |  ❌ {error_count} failed  |  Total: {total}")
        self.task_prog.setRange(0, 100)
        self.task_prog.setValue(100)
        self.running = False
        self.run_btn.setEnabled(True)
        self.run_btn.setText("▶▶  Run All")
        # Highlight report button when there's something to report
        if self._session_log:
            self.report_btn.setStyleSheet(
                f"background:{C['accent2']};color:white;border:1px solid {C['accent2']};"
                f"border-radius:4px;padding:4px 12px;font-weight:bold;")

    def _show_report(self):
        """Show a session report dialog and offer to save it."""
        from datetime import datetime
        import platform
        dlg = QDialog(self)
        dlg.setWindowTitle("Repair-O — Session Report")
        dlg.setMinimumSize(680, 500)
        dlg.setStyleSheet(_build_stylesheet(C))
        layout = QVBoxLayout(dlg)
        layout.addWidget(hdr("📄  Session Report", C["accent"]))
        txt = QTextEdit(); txt.setReadOnly(True)
        txt.setStyleSheet(
            f"background:{C['bg']};color:{C['text']};font-family:Consolas,monospace;"
            f"font-size:9pt;border:1px solid {C['border']};border-radius:4px;")
        layout.addWidget(txt)
        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾  Save Report to Desktop")
        save_btn.setStyleSheet(f"background:#14532d;color:{C['green']};font-weight:bold;padding:6px 16px;")
        copy_btn = QPushButton("📋  Copy to Clipboard")
        copy_btn.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};padding:6px 16px;")
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};padding:6px 16px;")
        close_btn.clicked.connect(dlg.close)
        btn_row.addWidget(save_btn); btn_row.addWidget(copy_btn); btn_row.addStretch(); btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)
        # Build report text
        now = datetime.now()
        sep  = "=" * 55
        sep2 = "-" * 55
        try:
            import subprocess as _sp
            _r = _sp.run(["powershell","-NoProfile","-Command",
                "(Get-CimInstance Win32_ComputerSystem).Name + ' / ' + (Get-CimInstance Win32_OperatingSystem).Caption"],
                capture_output=True, text=True, timeout=8,
                creationflags=_sp.CREATE_NO_WINDOW if hasattr(_sp,"CREATE_NO_WINDOW") else 0)
            machine_info = _r.stdout.strip() or platform.node()
        except Exception:
            machine_info = platform.node()
        lines = [
            sep,
            "  REPAIR-O  —  Session Report",
            f"  Generated : {now.strftime('%Y-%m-%d  %H:%M:%S')}",
            f"  Machine   : {machine_info}",
        ]
        if hasattr(self, "_source_name"):
            lines.append(f"  Section   : {self._source_name}")
        lines += [sep, ""]
        # Task results
        done_tasks   = [e for e in self._session_log if e[1].startswith("✅")]
        failed_tasks = [e for e in self._session_log if e[1].startswith("❌")]
        lines.append(f"SUMMARY:  {len(done_tasks)} succeeded  |  {len(failed_tasks)} failed  |  {len(self._session_log)} total")
        lines.append("")
        if done_tasks:
            lines.append("COMPLETED:")
            for ts, msg in done_tasks:
                lines.append(f"  [{ts}]  {msg}")
            lines.append("")
        if failed_tasks:
            lines.append("ERRORS / FAILURES:")
            for ts, msg in failed_tasks:
                lines.append(f"  [{ts}]  {msg}")
            lines.append("")
        lines.append(sep2)
        lines.append("FULL OUTPUT LOG:")
        lines.append(sep2)
        # Strip HTML from output pane
        raw_html = self.output.toHtml()
        import re as _re
        plain = _re.sub(r"<[^>]+>", "", raw_html)
        plain = plain.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&nbsp;", " ")
        lines.append(plain.strip())
        lines.append("")
        lines.append(sep)
        lines.append("  End of Report")
        lines.append(sep)
        report_text = "\n".join(lines)
        txt.setPlainText(report_text)
        # Wire save and copy
        def _save():
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            fname   = f"RepairO_Report_{now.strftime('%Y%m%d_%H%M%S')}.txt"
            path    = os.path.join(desktop, fname)
            try:
                with open(path, "w", encoding="utf-8") as f: f.write(report_text)
                QMessageBox.information(dlg, "Saved", f"Report saved to Desktop:\n{fname}")
            except Exception as e:
                QMessageBox.warning(dlg, "Error", str(e))
        def _copy():
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(report_text)
            QMessageBox.information(dlg, "Copied", "Report copied to clipboard.")
        save_btn.clicked.connect(_save)
        copy_btn.clicked.connect(_copy)
        dlg.exec_()

    def _log(self, msg, color=None):
        # Legacy helper kept for compatibility - safe to call from main thread only
        _c = color or C["text"]
        self.output.append(f'<span style="color:{_c};">{msg}</span>')



# ─────────────────────────────────────────────
#  LOG PANEL
# ─────────────────────────────────────────────
class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(8)
        layout.addWidget(lbl("📋 Log", color=C["muted"]))
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setFixedHeight(65)
        layout.addWidget(self.log)
        clr = QPushButton("Clear"); clr.setFixedSize(56,26)
        clr.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};font-size:8pt;")
        clr.clicked.connect(self.log.clear); layout.addWidget(clr, alignment=Qt.AlignTop)
        self.entry(f"Repair-O started — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def entry(self, msg, level="INFO"):
        colors = {"INFO":C["text"],"OK":C["green"],"WARN":C["yellow"],"ERROR":C["red"]}
        color = colors.get(level, C["text"])
        ts = datetime.now().strftime("%H:%M:%S")
        _muted = C["muted"]
        self.log.append(f'<span style="color:{_muted};">[{ts}]</span> <span style="color:{color};">{msg}</span>')


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  SYSTEM RESTORE MANAGER
# ─────────────────────────────────────────────
def _launch_restore_manager(parent):
    dlg = SystemRestoreDialog(parent)
    dlg.exec_()


class SystemRestoreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Repair-O  |  System Restore Manager")
        self.resize(800, 550)
        self.setStyleSheet(f"background:{C['bg']};color:{C['text']};")
        layout = QVBoxLayout(self)

        # Header
        hdr_lbl = QLabel("🔄  System Restore Manager")
        hdr_lbl.setStyleSheet(f"font-size:14pt;font-weight:bold;color:{C['accent']};padding:8px;")
        layout.addWidget(hdr_lbl)

        info = QLabel("Select a restore point to restore, or manage restore points below.")
        info.setStyleSheet(f"color:{C['muted']};padding:0 8px 8px 8px;")
        layout.addWidget(info)

        # Restore point list
        self.rp_list = QTableWidget()
        self.rp_list.setColumnCount(3)
        self.rp_list.setHorizontalHeaderLabels(["#", "Description", "Creation Date"])
        self.rp_list.horizontalHeader().setStretchLastSection(False)
        self.rp_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.rp_list.setColumnWidth(0, 50)
        self.rp_list.setColumnWidth(2, 180)
        self.rp_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rp_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.rp_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.rp_list.setStyleSheet(f"""
            QTableWidget {{ background:{C['panel']};color:{C['text']};gridline-color:{C['border']};border:1px solid {C['border']}; }}
            QTableWidget::item:selected {{ background:{C['accent2']};color:#fff; }}
            QHeaderView::section {{ background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']}; }}
        """)
        layout.addWidget(self.rp_list)

        # Buttons row
        btn_row = QHBoxLayout()
        self.restore_btn = QPushButton("↩  Restore Selected")
        self.restore_btn.setStyleSheet(f"background:{C['accent2']};color:#fff;padding:6px 16px;font-weight:bold;")
        self.restore_btn.clicked.connect(self._restore_selected)
        self.restore_btn.setEnabled(False)

        self.delete_btn = QPushButton("🗑  Delete Selected")
        self.delete_btn.setStyleSheet(f"background:#7f1d1d;color:#fca5a5;padding:6px 16px;font-weight:bold;")
        self.delete_btn.clicked.connect(self._delete_selected)
        self.delete_btn.setEnabled(False)

        create_btn = QPushButton("✚  Create New")
        create_btn.setStyleSheet(f"background:#14532d;color:{C['green']};padding:6px 16px;font-weight:bold;")
        create_btn.clicked.connect(self._create_new)

        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};padding:6px 16px;")
        refresh_btn.clicked.connect(self._load_restore_points)

        disable_btn = QPushButton("⚠  Disable System Restore")
        disable_btn.setStyleSheet(f"background:{C['panel2']};color:{C['yellow']};padding:6px 16px;")
        disable_btn.clicked.connect(self._toggle_restore)

        for b in [self.restore_btn, self.delete_btn, create_btn, refresh_btn, disable_btn]:
            btn_row.addWidget(b)
        btn_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        # Log area
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(100)
        self.log.setStyleSheet(f"background:{C['panel']};color:{C['text']};border:1px solid {C['border']};font-family:Consolas,monospace;font-size:8.5pt;")
        layout.addWidget(self.log)

        self.rp_list.itemSelectionChanged.connect(self._on_select)
        self.restore_points = []
        self._load_restore_points()

    def _on_select(self):
        has = self.rp_list.currentRow() >= 0
        self.restore_btn.setEnabled(has)
        self.delete_btn.setEnabled(has)

    def _log_msg(self, msg, color=None):
        color = color or C["text"]
        self.log.append(f'<span style="color:{color};">{msg}</span>')

    def _load_restore_points(self):
        self.log.clear(); self._log_msg("[Repair-O] Loading restore points...", C["muted"])
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        def worker():
            try:
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                     "Get-ComputerRestorePoint | Select-Object -Property SequenceNumber,Description,CreationTime | ConvertTo-Json"],
                    capture_output=True, text=True, timeout=30, creationflags=flags)
                return r.stdout.strip()
            except Exception as e:
                return f"ERROR:{e}"
        def done(result):
            if result.startswith("ERROR:"):
                self._log_msg(f"[ERROR] {result}", C["red"]); return
            try:
                import json as _j
                data = _j.loads(result)
                if isinstance(data, dict): data = [data]
                self.restore_points = data
                self.rp_list.setRowCount(0)
                for rp in data:
                    row = self.rp_list.rowCount(); self.rp_list.insertRow(row)
                    self.rp_list.setItem(row, 0, QTableWidgetItem(str(rp.get("SequenceNumber",""))))
                    self.rp_list.setItem(row, 1, QTableWidgetItem(rp.get("Description","")))
                    ct = rp.get("CreationTime","")
                    if "Date(" in ct:
                        import re; ms = re.search(r'Date\((\d+)', ct)
                        if ms:
                            from datetime import datetime, timezone
                            ts = int(ms.group(1))//1000
                            ct = datetime.fromtimestamp(ts).strftime("%Y/%m/%d %H:%M:%S")
                    self.rp_list.setItem(row, 2, QTableWidgetItem(str(ct)))
                self._log_msg(f"[OK] Found {len(data)} restore point(s).", C["green"])
            except Exception as e:
                self._log_msg(f"[ERROR] Parse failed: {e}", C["red"])
        import threading as _t
        def _run():
            res = worker()
            QTimer.singleShot(0, lambda: done(res))
        _t.Thread(target=_run, daemon=True).start()

    def _restore_selected(self):
        row = self.rp_list.currentRow()
        if row < 0: return
        seq = self.rp_list.item(row, 0).text()
        desc = self.rp_list.item(row, 1).text()
        if QMessageBox.question(self, "Confirm Restore",
                f"Restore to point #{seq}:\n{desc}\n\nThe computer will restart. Continue?",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes: return
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                          f"Restore-Computer -RestorePoint {seq} -Confirm:$false"],
                         creationflags=flags)
        self._log_msg(f"[OK] Restore initiated for point #{seq}. System will restart.", C["green"])

    def _delete_selected(self):
        row = self.rp_list.currentRow()
        if row < 0: return
        seq = self.rp_list.item(row, 0).text()
        desc = self.rp_list.item(row, 1).text()
        if QMessageBox.question(self, "Confirm Delete",
                f"Delete restore point #{seq}?\n{desc}\n\nThis cannot be undone.",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes: return
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        def worker():
            r = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                 f"$rp = Get-ComputerRestorePoint | Where-Object {{$_.SequenceNumber -eq {seq}}}; if ($rp) {{ vssadmin delete shadows /shadow=$($rp.CreationTime) /quiet 2>&1 }}"],
                capture_output=True, text=True, timeout=30, creationflags=flags)
            QTimer.singleShot(0, lambda: (
                self._log_msg(f"[OK] Restore point #{seq} deleted.", C["green"]),
                self._load_restore_points()
            ))
        import threading as _t; _t.Thread(target=worker, daemon=True).start()

    def _create_new(self):
        name, ok = QInputDialog.getText(self, "Create Restore Point", "Description:", text="Repair-O Restore Point")
        if not ok or not name.strip(): return
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        self._log_msg("[Repair-O] Creating restore point...", C["muted"])
        def worker():
            r = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                 f"Checkpoint-Computer -Description '{name}' -RestorePointType MODIFY_SETTINGS"],
                capture_output=True, text=True, timeout=60, creationflags=flags)
            QTimer.singleShot(0, lambda: (
                self._log_msg("[OK] Restore point created.", C["green"]),
                self._load_restore_points()
            ))
        import threading as _t; _t.Thread(target=worker, daemon=True).start()

    def _toggle_restore(self):
        if QMessageBox.question(self, "Disable System Restore",
                "This will disable System Restore on C:.\nAll existing restore points will be deleted.\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes: return
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                          "Disable-ComputerRestore -Drive C: -Confirm:$false"],
                         creationflags=flags)
        self._log_msg("[WARN] System Restore disabled on C:", C["yellow"])



# ─────────────────────────────────────────────
#  QUICK INFO SNAPSHOT
# ─────────────────────────────────────────────
class QuickInfoTab(QWidget):
    """One-click machine info snapshot — copies to clipboard."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(10)
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("📋  Quick Info Snapshot", C["accent"])); hrow.addStretch()
        snap_btn = QPushButton("⚡  Grab Info Now")
        snap_btn.setStyleSheet(f"background:{C['accent2']};color:white;font-weight:bold;font-size:11pt;padding:8px 22px;")
        snap_btn.clicked.connect(self._grab)
        copy_btn = QPushButton("📋  Copy to Clipboard")
        copy_btn.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};padding:8px 16px;")
        copy_btn.clicked.connect(self._copy)
        hrow.addWidget(snap_btn); hrow.addWidget(copy_btn)
        layout.addLayout(hrow)
        layout.addWidget(lbl("Grabs machine name, user, Windows version, IP, serial number and more in seconds.", color=C["muted"]))
        layout.addWidget(divider())
        self.out = QTextEdit(); self.out.setReadOnly(True)
        self.out.setStyleSheet(f"background:{C['bg']};color:{C['text']};font-family:Consolas,monospace;font-size:9.5pt;border:1px solid {C['border']};border-radius:4px;")
        self.out.setPlaceholderText("Click 'Grab Info Now' to collect machine information...")
        layout.addWidget(self.out)
        self._last_text = ""

    def _grab(self):
        self.out.setPlainText("⏳ Collecting info...")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        script = os.path.join(SCRIPTS_DIR, "quick_info.ps1")
        def worker():
            try:
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script],
                    capture_output=True, text=True, timeout=20, creationflags=flags)
                return r.stdout.strip() or r.stderr.strip() or "No output."
            except subprocess.TimeoutExpired:
                return "Timed out after 20 seconds."
            except Exception as e:
                return f"Error: {e}"
        def done(text):
            self._last_text = text
            self.out.setPlainText(text)
        import threading as _t
        def _run():
            res = worker()
            QTimer.singleShot(0, lambda: done(res))
        _t.Thread(target=_run, daemon=True).start()

    def _copy(self):
        text = self.out.toPlainText()
        if text and text != "⏳ Collecting info...":
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "Machine info copied to clipboard.")


# ─────────────────────────────────────────────
#  CLIENT NOTES
# ─────────────────────────────────────────────
class ClientNotesTab(QWidget):
    """Simple per-job notes — saves to Desktop as a text file."""
    _NOTES_DIR = os.path.join(os.path.expanduser("~"), "Documents", "RepairO_Notes")

    def __init__(self):
        super().__init__()
        os.makedirs(self._NOTES_DIR, exist_ok=True)
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(8)
        hrow = QHBoxLayout()
        hrow.addWidget(hdr("📝  Client Notes", C["accent"])); hrow.addStretch()
        new_btn = QPushButton("➕  New Note")
        new_btn.clicked.connect(self._new_note)
        new_btn.setStyleSheet(f"background:{C['accent2']};color:white;font-weight:bold;")
        save_btn = QPushButton("💾  Save")
        save_btn.clicked.connect(self._save)
        save_btn.setStyleSheet(f"background:#14532d;color:{C['green']};font-weight:bold;")
        open_btn = QPushButton("📂  Open Folder")
        open_btn.clicked.connect(lambda: subprocess.Popen(["explorer", self._NOTES_DIR]))
        open_btn.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};")
        for b in [new_btn, save_btn, open_btn]: hrow.addWidget(b)
        layout.addLayout(hrow)
        layout.addWidget(lbl(f"Notes save to: {self._NOTES_DIR}", color=C["muted"]))
        layout.addWidget(divider())

        # Note list + editor side by side
        splitter = QSplitter(Qt.Horizontal)
        # Left: note list
        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0)
        ll.addWidget(lbl("Saved Notes", bold=True, color=C["accent"]))
        self.note_list = QListWidget()
        self.note_list.currentItemChanged.connect(self._load_selected)
        ll.addWidget(self.note_list)
        del_btn = QPushButton("🗑  Delete Selected")
        del_btn.setStyleSheet(f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};")
        del_btn.clicked.connect(self._delete_note)
        ll.addWidget(del_btn)
        splitter.addWidget(left)
        # Right: editor
        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0)
        self.note_title = QLineEdit()
        self.note_title.setPlaceholderText("Note title / client name...")
        self.note_title.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px;font-size:11pt;")
        rl.addWidget(self.note_title)
        self.note_body = QTextEdit()
        self.note_body.setPlaceholderText("What was wrong, what you did, date, anything useful...")
        self.note_body.setStyleSheet(f"background:{C['bg']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;font-size:10pt;")
        rl.addWidget(self.note_body)
        splitter.addWidget(right)
        splitter.setSizes([200, 600])
        layout.addWidget(splitter)
        self._current_file = None
        self._refresh_list()

    def _refresh_list(self):
        self.note_list.clear()
        for f in sorted(os.listdir(self._NOTES_DIR), reverse=True):
            if f.endswith(".txt"):
                item = QListWidgetItem(f[:-4])
                item.setData(Qt.UserRole, os.path.join(self._NOTES_DIR, f))
                self.note_list.addItem(item)

    def _new_note(self):
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d_%H%M")
        self.note_title.setText(f"Job_{ts}")
        self.note_body.clear()
        _dt = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.note_body.setPlainText(f"Date: {_dt}\nTech: \nClient: \nIssue: \nSteps taken: \nOutcome: \n")
        self._current_file = None

    def _save(self):
        title = self.note_title.text().strip() or "Untitled"
        # Sanitise filename
        safe = "".join(c for c in title if c.isalnum() or c in " _-").strip()
        path = os.path.join(self._NOTES_DIR, f"{safe}.txt")
        body_text = self.note_body.toPlainText()
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"=== {title} ===\n\n{body_text}")
        self._current_file = path
        self._refresh_list()
        QMessageBox.information(self, "Saved", f"Note saved: {safe}.txt")

    def _load_selected(self, item):
        if not item: return
        path = item.data(Qt.UserRole)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            title = lines[0].strip("= \n") if lines else ""
            body  = "\n".join(lines[2:]) if len(lines) > 2 else content
            self.note_title.setText(title)
            self.note_body.setPlainText(body)
            self._current_file = path
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _delete_note(self):
        item = self.note_list.currentItem()
        if not item: return
        path = item.data(Qt.UserRole)
        if QMessageBox.question(self, "Delete", f"Delete '{item.text()}'?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try: os.remove(path)
            except: pass
            self.note_title.clear(); self.note_body.clear()
            self._refresh_list()


# ─────────────────────────────────────────────
#  NETWORK TOOLS
# ─────────────────────────────────────────────
class NetworkToolsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(16,16,16,8); layout.setSpacing(10)
        layout.addWidget(hdr("🌐  Network Tools", C["accent"]))
        layout.addWidget(divider())

        # ── Row 1: Quick action buttons ──────────────────────────────────
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        actions = [
            ("🔄  Flush DNS",        self._flush_dns),
            ("🔌  Release IP",       self._release_ip),
            ("🔌  Renew IP",         self._renew_ip),
            ("♻  Reset Winsock",    self._reset_winsock),
            ("📋  Copy IP Info",     self._copy_ip_info),
        ]
        for label, fn in actions:
            b = QPushButton(label)
            b.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 12px;")
            b.clicked.connect(fn)
            btn_row.addWidget(b)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ── Row 2: DHCP / Static DNS ─────────────────────────────────────
        nic_row = QHBoxLayout(); nic_row.setSpacing(8)

        dhcp_btn = QPushButton("🌐  Apply DHCP to All NICs")
        dhcp_btn.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 14px;")
        dhcp_btn.setToolTip("Resets all active network adapters to automatic (DHCP) addressing")
        dhcp_btn.clicked.connect(self._apply_dhcp)
        nic_row.addWidget(dhcp_btn)

        self.dns_primary   = QLineEdit("8.8.8.8")
        self.dns_secondary = QLineEdit("8.8.4.4")
        for w, tip in [(self.dns_primary, "Primary DNS"), (self.dns_secondary, "Secondary DNS")]:
            w.setPlaceholderText(tip)
            w.setFixedWidth(120)
            w.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:5px;")
            nic_row.addWidget(w)

        dns_btn = QPushButton("🔧  Apply Static DNS to All NICs")
        dns_btn.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 14px;")
        dns_btn.setToolTip("Pushes the specified DNS servers to all active network adapters")
        dns_btn.clicked.connect(self._apply_static_dns)
        nic_row.addWidget(dns_btn)
        nic_row.addStretch()
        layout.addLayout(nic_row)

        # ── Row 3: Time Zone ─────────────────────────────────────────────
        tz_row = QHBoxLayout(); tz_row.setSpacing(8)
        tz_lbl = QLabel("🕐  Time Zone:")
        tz_lbl.setStyleSheet(f"color:{C['text']};font-weight:bold;")
        tz_row.addWidget(tz_lbl)

        self.tz_combo = QComboBox()
        self.tz_combo.setMinimumWidth(320)
        self.tz_combo.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:4px;")
        self.tz_combo.addItem("Loading time zones...")
        tz_row.addWidget(self.tz_combo, 1)

        set_tz_btn = QPushButton("Set Time Zone")
        set_tz_btn.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 14px;")
        set_tz_btn.clicked.connect(self._set_timezone)
        tz_row.addWidget(set_tz_btn)

        sync_btn = QPushButton("⏱  Sync Clock Now")
        sync_btn.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 14px;")
        sync_btn.clicked.connect(self._sync_clock)
        tz_row.addWidget(sync_btn)

        auto_sync_btn = QPushButton("✅  Enable Auto Time Sync")
        auto_sync_btn.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px 14px;")
        auto_sync_btn.clicked.connect(self._enable_autosync)
        tz_row.addWidget(auto_sync_btn)
        tz_row.addStretch()
        layout.addLayout(tz_row)

        # ── Row 4: Ping / Traceroute ──────────────────────────────────────
        ping_row = QHBoxLayout(); ping_row.setSpacing(6)
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Hostname or IP  (e.g. google.com  or  8.8.8.8)")
        self.host_input.setStyleSheet(f"background:{C['panel2']};color:{C['text']};border:1px solid {C['border']};border-radius:4px;padding:6px;")
        self.host_input.returnPressed.connect(self._ping)
        ping_row.addWidget(self.host_input, 1)
        for label, fn in [("📡  Ping", self._ping), ("🗺  Traceroute", self._traceroute)]:
            b = QPushButton(label)
            b.setStyleSheet(f"background:{C['accent2']};color:white;font-weight:bold;padding:6px 16px;border-radius:4px;")
            b.clicked.connect(fn)
            ping_row.addWidget(b)
        layout.addLayout(ping_row)

        self.out = QTextEdit(); self.out.setReadOnly(True)
        self.out.setStyleSheet(f"background:{C['bg']};color:{C['text']};font-family:Consolas,monospace;font-size:9.5pt;border:1px solid {C['border']};border-radius:4px;")
        layout.addWidget(self.out)

        # Load time zones in background
        QTimer.singleShot(500, self._load_timezones)

    def _load_timezones(self):
        """Populate the time zone combo from PowerShell in background."""
        import threading as _t, json as _j
        scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
        script = os.path.join(scripts_dir, "time_tools.ps1")
        flags  = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        def _fetch():
            try:
                r = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", script, "-Action", "list_zones"],
                    capture_output=True, text=True, timeout=15, creationflags=flags
                )
                zones = _j.loads(r.stdout)
                # Also get current zone
                r2 = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", script, "-Action", "get_current"],
                    capture_output=True, text=True, timeout=10, creationflags=flags
                )
                current_id = _j.loads(r2.stdout).get("Id", "")
                QTimer.singleShot(0, lambda: self._populate_tz(zones, current_id))
            except Exception as e:
                QTimer.singleShot(0, lambda: self.tz_combo.setItemText(0, f"Error loading zones: {e}"))
        _t.Thread(target=_fetch, daemon=True).start()

    def _populate_tz(self, zones, current_id):
        self.tz_combo.clear()
        self._tz_ids = []
        current_idx = 0
        for i, z in enumerate(zones):
            display = z.get("DisplayName", z.get("Id", "Unknown"))
            self.tz_combo.addItem(display)
            self._tz_ids.append(z.get("Id", ""))
            if z.get("Id", "") == current_id:
                current_idx = i
        self.tz_combo.setCurrentIndex(current_idx)

    def _run_ps(self, script_name, args, label):
        """Run a PowerShell script and show output."""
        self.out.append(f"\n▶ {label}\n{'─'*40}")
        scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
        script = os.path.join(scripts_dir, script_name)
        flags  = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        cmd    = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script] + args
        import threading as _t
        def _run():
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, creationflags=flags)
                out = r.stdout or r.stderr or "(no output)"
            except subprocess.TimeoutExpired:
                out = "Timed out after 60s."
            except Exception as e:
                out = f"Error: {e}"
            QTimer.singleShot(0, lambda: (self.out.append(out), self.out.moveCursor(self.out.textCursor().End)))
        _t.Thread(target=_run, daemon=True).start()

    def _run_cmd(self, cmd, label):
        self.out.append(f"\n▶ {label}\n{'─'*40}")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        def worker():
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, creationflags=flags)
                return r.stdout or r.stderr or "(no output)"
            except subprocess.TimeoutExpired:
                return "Timed out after 30s."
            except Exception as e:
                return f"Error: {e}"
        import threading as _t
        def _run():
            res = worker()
            QTimer.singleShot(0, lambda: (self.out.append(res), self.out.moveCursor(self.out.textCursor().End)))
        _t.Thread(target=_run, daemon=True).start()

    def _flush_dns(self):   self._run_cmd(["ipconfig", "/flushdns"], "Flush DNS Cache")
    def _release_ip(self):  self._run_cmd(["ipconfig", "/release"],  "Release IP Address")
    def _renew_ip(self):    self._run_cmd(["ipconfig", "/renew"],    "Renew IP Address")
    def _reset_winsock(self): self._run_cmd(["netsh", "winsock", "reset"], "Reset Winsock  (reboot required)")

    def _copy_ip_info(self):
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            r = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, timeout=10, creationflags=flags)
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(r.stdout)
            QMessageBox.information(self, "Copied", "Full IP configuration copied to clipboard.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _apply_dhcp(self):
        self._run_ps("apply_dhcp_all_nics.ps1", [], "Apply DHCP to All NICs")

    def _apply_static_dns(self):
        primary   = self.dns_primary.text().strip()   or "8.8.8.8"
        secondary = self.dns_secondary.text().strip() or "8.8.4.4"
        self._run_ps("apply_static_dns.ps1",
                     ["-Primary", primary, "-Secondary", secondary],
                     f"Apply Static DNS ({primary} / {secondary}) to All NICs")

    def _set_timezone(self):
        idx = self.tz_combo.currentIndex()
        if not hasattr(self, "_tz_ids") or idx < 0 or idx >= len(self._tz_ids):
            self.out.append("\n[WARN] Time zones not loaded yet — please wait a moment.")
            return
        tz_id = self._tz_ids[idx]
        self._run_ps("time_tools.ps1", ["-Action", "set_zone", "-TimeZone", tz_id],
                     f"Set Time Zone: {tz_id}")

    def _sync_clock(self):
        self._run_ps("time_tools.ps1", ["-Action", "sync_now"], "Sync System Clock")

    def _enable_autosync(self):
        self._run_ps("time_tools.ps1", ["-Action", "enable_autosync"], "Enable Automatic Time Sync")

    def _ping(self):
        host = self.host_input.text().strip()
        if not host: QMessageBox.warning(self, "Repair-O", "Enter a hostname or IP first."); return
        self._run_cmd(["ping", "-n", "4", host], f"Ping {host}")

    def _traceroute(self):
        host = self.host_input.text().strip()
        if not host: QMessageBox.warning(self, "Repair-O", "Enter a hostname or IP first."); return
        self._run_cmd(["tracert", "-d", "-h", "20", host], f"Traceroute {host}")

# ─────────────────────────────────────────────
#  THEME PICKER DIALOG
# ─────────────────────────────────────────────
class ThemePickerDialog(QDialog):
    """Modal theme picker — shows a preview swatch for each theme."""

    # Theme display names with emoji hints
    THEME_LABELS = {
        "Default":     "🔵  Default",
        "Cinder Scarlet":  "🔴  Cinder Scarlet",
        "Abyssal Jade":    "🟢  Abyssal Jade",
        "Skystone Blue":   "🔷  Skystone Blue",
        "Harvest Gold":    "🟡  Harvest Gold",
        "Midnight":    "🟣  Midnight",
        "Ember":       "🟠  Ember",
        "Arctic":      "🩵  Arctic",
        "Stealth":     "⚫  Stealth",
        "Light":       "☀️  Light",
    }

    def __init__(self, current_theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Theme")
        self.setMinimumWidth(520)
        self.setModal(True)
        self.chosen = current_theme

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("🎨  Choose a Theme")
        title.setStyleSheet(f"font-size:13pt;font-weight:bold;color:{C['accent']};")
        layout.addWidget(title)

        note = QLabel("Theme is saved and applied next time you open Repair-O.")
        note.setStyleSheet(f"font-size:8.5pt;color:{C['muted']};")
        layout.addWidget(note)
        layout.addWidget(self._divider())

        # Grid of theme swatches — 3 columns
        grid = QGridLayout(); grid.setSpacing(10)
        self._btns = {}
        for i, (name, label) in enumerate(self.THEME_LABELS.items()):
            swatch = self._make_swatch(name, label, name == current_theme)
            grid.addWidget(swatch, i // 3, i % 3)
            self._btns[name] = swatch
        layout.addLayout(grid)
        layout.addWidget(self._divider())

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(
            f"background:{C['panel2']};color:{C['muted']};border:1px solid {C['border']};"
            f"padding:6px 18px;border-radius:4px;")
        cancel.clicked.connect(self.reject)
        apply = QPushButton("✅  Apply Theme")
        apply.setStyleSheet(
            f"background:{C['accent2']};color:white;font-weight:bold;"
            f"padding:6px 18px;border-radius:4px;")
        apply.clicked.connect(self.accept)
        btn_row.addWidget(cancel)
        btn_row.addWidget(apply)
        layout.addLayout(btn_row)

    def _divider(self):
        f = QFrame(); f.setFrameShape(QFrame.HLine)
        f.setStyleSheet(f"color:{C['border']};background:{C['border']};max-height:1px;")
        return f

    def _make_swatch(self, name, label, selected):
        t = THEMES[name]
        frame = QFrame()
        frame.setCursor(Qt.PointingHandCursor)
        frame.setFixedHeight(80)
        border_col = t["accent"] if selected else t["border"]
        bw = "2px" if selected else "1px"
        frame.setStyleSheet(
            f"QFrame{{background:{t['panel']};border:{bw} solid {border_col};"
            f"border-radius:8px;}}"
            f"QFrame:hover{{border:2px solid {t['accent']};}}")

        vl = QVBoxLayout(frame); vl.setContentsMargins(10, 8, 10, 8); vl.setSpacing(4)

        # Mini color bar showing accent / bg / panel
        bar = QHBoxLayout(); bar.setSpacing(3)
        for col in [t["accent"], t["accent2"], t["triage"], t["treat"], t["bg"]]:
            dot = QLabel()
            dot.setFixedSize(14, 14)
            dot.setStyleSheet(f"background:{col};border-radius:7px;border:none;")
            bar.addWidget(dot)
        bar.addStretch()
        vl.addLayout(bar)

        lbl_w = QLabel(label)
        lbl_w.setStyleSheet(
            f"color:{t['text']};font-size:9pt;font-weight:bold;"
            f"background:transparent;border:none;")
        vl.addWidget(lbl_w)

        if selected:
            sel = QLabel("✓ Active")
            sel.setStyleSheet(f"color:{t['accent']};font-size:7.5pt;background:transparent;border:none;")
            vl.addWidget(sel)

        frame.mousePressEvent = lambda e, n=name: self._select(n)
        return frame

    def _select(self, name):
        self.chosen = name
        # Rebuild all swatches to update selection highlight
        for n, frame in list(self._btns.items()):
            t = THEMES[n]
            selected = (n == name)
            border_col = t["accent"] if selected else t["border"]
            bw = "2px" if selected else "1px"
            frame.setStyleSheet(
                f"QFrame{{background:{t['panel']};border:{bw} solid {border_col};"
                f"border-radius:8px;}}"
                f"QFrame:hover{{border:2px solid {t['accent']};}}")


class RepairO(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Repair-O  |  Professional PC Repair Toolkit")
        self.resize(1280, 880); self.setMinimumSize(1000, 660)
        # Set window icon
        _icon_path = os.path.join(BUNDLE_DIR, "assets", "RepairO.ico")
        if os.path.exists(_icon_path):
            from PyQt5.QtGui import QIcon
            self.setWindowIcon(QIcon(_icon_path))
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ── Title / nav bar ────────────────────────────────────────
        tb = QWidget(); tb.setFixedHeight(56)
        self.tb_widget = tb
        tb.setStyleSheet(f"background:{C['panel']};border-bottom:2px solid {C['accent2']};")
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(20,0,16,0); tbl.setSpacing(0)

        logo = QLabel("⚕")
        logo.setStyleSheet(f"font-size:22pt;color:{C['accent']};background:transparent;")
        tbl.addWidget(logo)
        self.name_lbl = QLabel("Repair-O")
        self.name_lbl.setStyleSheet(f"font-size:17pt;font-weight:900;color:{C['accent']};background:transparent;letter-spacing:1px;margin-left:6px;")
        tbl.addWidget(self.name_lbl)

        # Back-to-dashboard button (hidden when on dashboard)
        self.back_btn = QPushButton("⬅  Dashboard")
        self.back_btn.setStyleSheet(
            f"background:transparent;color:{C['muted']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:4px 12px;margin-left:18px;font-size:9pt;")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.show_dashboard)
        self.back_btn.setVisible(False)
        tbl.addWidget(self.back_btn)

        # Current section label
        self.section_lbl = QLabel("")
        self.section_lbl.setStyleSheet(f"font-size:11pt;font-weight:bold;color:{C['text']};background:transparent;margin-left:10px;")
        tbl.addWidget(self.section_lbl)

        tbl.addStretch()
        self.theme_btn = QPushButton("🎨  Theme")
        self.theme_btn.setStyleSheet(
            f"background:transparent;color:{C['muted']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:4px 10px;font-size:8.5pt;margin-right:8px;")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._open_theme_picker)
        tbl.addWidget(self.theme_btn)
        ver = QLabel("v1.0")
        ver.setStyleSheet(f"font-size:8pt;color:{C['muted']};background:transparent;")
        tbl.addWidget(ver)
        root.addWidget(tb)

        # ── Stack: Dashboard (index 0) + each section (indices 1-9) ──
        self.stack = QStackedWidget()

        # Build all section tabs
        self.queue_tab    = RunQueueTab()
        self.queue_tab._nav_callback = self._go_section
        self.diagnose     = DiagnoseTab()
        self.triage       = TriageTab(self.queue_tab)
        self.treat        = TreatTab(self.queue_tab)
        self.toolkit      = ToolkitTab()
        self.migration    = MigrationTab()
        self.uninstall    = UninstallerTab()
        self.maintenance  = MaintenanceTab(self.queue_tab)
        self.tweaks       = TweaksTab(self.queue_tab)
        self.quick_info   = QuickInfoTab()
        self.client_notes = ClientNotesTab()
        self.network_tools = NetworkToolsTab()

        # Keep tabs reference for backward compat (Run Selected Now switches to queue)
        _self = self
        class _FakeTabs:
            def setCurrentIndex(self2, i):
                # Old tab index 8 = Run Queue = new stack index 9
                stack_i = 9 if i == 8 else i
                _self._go_section(stack_i)
            def count(self2): return 13
        self.tabs = _FakeTabs()

        # Dashboard widget
        self.dashboard = self._build_dashboard()

        self.stack.addWidget(self.dashboard)     # index 0
        self.stack.addWidget(self.diagnose)      # index 1
        self.stack.addWidget(self.triage)        # index 2
        self.stack.addWidget(self.treat)         # index 3
        self.stack.addWidget(self.maintenance)   # index 4
        self.stack.addWidget(self.tweaks)        # index 5
        self.stack.addWidget(self.toolkit)       # index 6
        self.stack.addWidget(self.migration)     # index 7
        self.stack.addWidget(self.uninstall)     # index 8
        self.stack.addWidget(self.queue_tab)     # index 9
        self.stack.addWidget(self.quick_info)    # index 10
        self.stack.addWidget(self.client_notes)  # index 11
        self.stack.addWidget(self.network_tools) # index 12

        content = QWidget(); cl = QVBoxLayout(content)
        cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)
        cl.addWidget(self.stack)
        cl.addWidget(divider())
        self.log_panel = LogPanel(); cl.addWidget(self.log_panel)
        root.addWidget(content)

        sb = self.statusBar()
        sb.showMessage("Repair-O v1.0  |  Ready")
        sb.setStyleSheet(f"background:{C['panel']};color:{C['muted']};border-top:1px solid {C['border']};font-size:8pt;")

    # ── Stack navigation ─────────────────────────────────────────
    _SECTION_NAMES = {
        1: "📊  Scan & Report",   2: "⚡  Fast Fixes",       3: "🔧  Fix & Repair",
        4: "🧹  Clean Up",        5: "🚀  Speed Up",          6: "🧰  Tools",
        7: "📦  Move & Backup",   8: "🗑  Remove Software",   9: "✅  Run Tasks",
        10: "📋  Quick Info",     11: "📝  Client Notes",     12: "🌐  Network Tools",
    }

    def _go_section(self, idx):
        """Navigate to a section by 1-based index (mirrors old tab indices)."""
        # Remap: old tab 8 = Run Queue → stack index 9
        stack_idx = idx  # direct 1:1 after dashboard at 0
        self.stack.setCurrentIndex(stack_idx)
        self.back_btn.setVisible(True)
        self.section_lbl.setText(self._SECTION_NAMES.get(stack_idx, ""))

    def show_dashboard(self):
        self.stack.setCurrentIndex(0)
        self.back_btn.setVisible(False)
        self.section_lbl.setText("")

    def _open_theme_picker(self):
        current = _load_active_theme()
        dlg = ThemePickerDialog(current, self)
        dlg.setStyleSheet(_build_stylesheet(C))
        if dlg.exec_() == QDialog.Accepted and dlg.chosen != current:
            _save_active_theme(dlg.chosen)
            self._apply_theme(dlg.chosen)

    def _apply_theme(self, theme_name):
        """Apply a theme live without restarting."""
        global C, STYLESHEET
        C = dict(THEMES[theme_name])
        STYLESHEET = _build_stylesheet(C)
        # Apply stylesheet to the whole app
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().setStyleSheet(STYLESHEET)
        # Update title bar widgets that bake in colors at creation time
        self.back_btn.setStyleSheet(
            f"background:transparent;color:{C['muted']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:4px 12px;font-size:9pt;")
        self.section_lbl.setStyleSheet(
            f"font-size:11pt;font-weight:bold;color:{C['text']};background:transparent;margin-left:10px;")
        self.name_lbl.setStyleSheet(
            f"font-size:17pt;font-weight:900;color:{C['accent']};background:transparent;letter-spacing:1px;margin-left:6px;")
        self.tb_widget.setStyleSheet(
            f"background:{C['panel']};border-bottom:2px solid {C['accent2']};")
        self.theme_btn.setStyleSheet(
            f"background:transparent;color:{C['muted']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:4px 10px;font-size:8.5pt;margin-right:8px;")
        # Rebuild the dashboard cards since they bake in colors
        self._refresh_dashboard()

    def _refresh_dashboard(self):
        """Swap out the dashboard widget with a freshly built one, preserving stack indices."""
        current_idx = self.stack.currentIndex()
        old = self.stack.widget(0)
        new_dash = self._build_dashboard()
        # Replace at index 0 without shifting other widgets
        self.stack.insertWidget(0, new_dash)   # inserted at 0, old becomes index 1
        self.stack.removeWidget(old)            # remove old (now at 1), everything stays put
        old.deleteLater()
        # Restore position — indices are stable since we removed the old one
        self.stack.setCurrentIndex(current_idx)
        # Re-apply back button visibility
        if current_idx == 0:
            self.back_btn.setVisible(False)
            self.section_lbl.setText("")
        else:
            self.back_btn.setVisible(True)

    # ── Dashboard ─────────────────────────────────────────────────
    def _build_dashboard(self):
        w = QWidget()
        w.setStyleSheet(f"background:{C['bg']};")
        outer = QVBoxLayout(w); outer.setContentsMargins(24, 16, 24, 16); outer.setSpacing(12)

        intro = QLabel("Select a section to get started")
        intro.setStyleSheet(f"color:{C['muted']};font-size:10pt;")
        intro.setAlignment(Qt.AlignCenter)
        outer.addWidget(intro)

        # Card definitions: (stack_idx, emoji, title, subtitle, accent_color)
        cards = [
            (1, "📊", "Scan & Report",  "Full system info, hardware & diagnostics",           C["accent"]),
            (2, "⚡", "Fast Fixes",   "Common quick fixes to run first",                    C["triage"]),
            (3, "🔧", "Fix & Repair", "Windows repairs, SFC, DISM & external tools",        C["treat"]),
            (4, "🧹", "Clean Up",    "Temp files, browser history & disk cleanup",           C["maintain"]),
            (5, "🚀", "Speed Up",    "Performance tweaks & registry optimisations",          C["tweaks"]),
            (6, "🧰", "Tools",       "Download & launch repair utilities",                   C["accent2"]),
            (7, "📦", "Move & Backup", "Backup, restore & Windows.old data recovery",        C["green"]),
            (8, "🗑", "Remove Software", "Uninstall programs & clean up leftovers",          C["red"]),
            (9,  "✅", "Run Tasks",      "Review & run your queued tasks",                    C["queue"]),
            (10, "📋", "Quick Info",      "One-click machine info snapshot to clipboard",       C["accent"]),
            (11, "📝", "Client Notes",    "Log job notes and save them per client",             C["green"]),
            (12, "🌐", "Network Tools",   "Ping, traceroute, flush DNS, IP tools",              C["triage"]),
        ]

        # 3-column grid of cards
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        for i, (idx, emoji, title, subtitle, color) in enumerate(cards):
            card = self._dash_card(idx, emoji, title, subtitle, color)
            grid.addWidget(card, i // 3, i % 3)

        outer.addLayout(grid)
        outer.addStretch()
        return w

    def _dash_card(self, section_idx, emoji, title, subtitle, color):
        btn = QFrame()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(130)
        btn.setStyleSheet(
            f"QFrame{{background:{C['panel']};border:2px solid {C['border']};"
            f"border-radius:10px;}}"
            f"QFrame:hover{{border:2px solid {color};background:{C['panel2']};}}")
        layout = QVBoxLayout(btn)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        # Top row: colored accent bar + emoji text
        top = QHBoxLayout(); top.setSpacing(8)
        accent_bar = QLabel("")
        accent_bar.setFixedWidth(4)
        accent_bar.setStyleSheet(f"background:{color};border-radius:2px;min-height:40px;max-height:40px;")
        top.addWidget(accent_bar)

        em = QLabel(emoji)
        em.setStyleSheet(
            f"font-size:20pt;background:transparent;border:none;"
            f"color:{color};font-family:'Segoe UI Emoji','Apple Color Emoji',sans-serif;")
        em.setFixedWidth(36)
        top.addWidget(em)
        top.addStretch()
        layout.addLayout(top)

        t = QLabel(title)
        t.setStyleSheet(
            f"font-size:13pt;font-weight:bold;color:{C['text']};"
            f"background:transparent;border:none;padding:0;margin:0;")
        layout.addWidget(t)

        s = QLabel(subtitle)
        s.setStyleSheet(
            f"font-size:8.5pt;color:{C['muted']};"
            f"background:transparent;border:none;padding:0;margin:0;")
        s.setWordWrap(True)
        layout.addWidget(s)
        layout.addStretch()

        # Make the whole card clickable
        btn.mousePressEvent = lambda event, i=section_idx: self._go_section(i)
        return btn


if __name__ == "__main__":
    # Tell Windows this is its own app (not python.exe) so taskbar icon works
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("RepairO.App.1")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setApplicationName("Repair-O")

    # Set app icon from assets folder
    icon_path = os.path.join(BUNDLE_DIR, "assets", "RepairO.ico")
    if os.path.exists(icon_path):
        from PyQt5.QtGui import QIcon
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

    window = RepairO()
    # Also set on the main window itself (belt and suspenders)
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()
    sys.exit(app.exec_())
