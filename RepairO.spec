# -*- mode: python ; coding: utf-8 -*-
# RepairO.spec - PyInstaller build configuration

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

added_files = [
    ('scripts/*.ps1',       'scripts'),
    ('tools_manifest.json', '.'),
    ('assets/RepairO.ico','assets'),
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # urllib - built-in, used by downloader.py
        'urllib',
        'urllib.request',
        'urllib.error',
        'urllib.parse',
        'urllib.response',
        'urllib.robotparser',
        # ssl - needed by urllib for https
        'ssl',
        '_ssl',
        # email - needed internally by ssl/http even though we don't use it directly
        'email',
        'email.mime',
        'email.mime.text',
        'email.mime.multipart',
        'email.mime.base',
        'email.parser',
        'email.generator',
        'email.encoders',
        'email.utils',
        'email.header',
        'email.charset',
        'email.message',
        'email.errors',
        'email._header_value_parser',
        'email._parseaddr',
        'email.feedparser',
        'email.contentmanager',
        'email.policy',
        'email.iterators',
        # http - also needed by urllib
        'http',
        'http.client',
        'http.cookiejar',
        # standard libs
        'json',
        'threading',
        'subprocess',
        'zipfile',
        'pathlib',
        'socket',
        'hashlib',
        'base64',
        'struct',
        'zlib',
        'shutil',
        'string',
        'webbrowser',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Only exclude things we truly never use
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'unittest',
        'ftplib',
        'imaplib',
        'poplib',
        'smtplib',
        'telnetlib',
        'xmlrpc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RepairO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/RepairO.ico',
    version='version_info.txt',
    uac_admin=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RepairO',
)
