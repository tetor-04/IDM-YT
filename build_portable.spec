# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for IDM Video Downloader - Windows 7+ Compatible

block_cipher = None

a = Analysis(
    ['video_downloader.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('plugins', 'plugins'),  # Include plugins folder
    ],
    hiddenimports=[
        'yt_dlp', 
        'requests', 
        'urllib3', 
        'certifi', 
        'websockets',
        'pyperclip',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        'threading',
        'queue',
        'pathlib',
        'json',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'pytest'],  # Reduce size
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IDM_VideoDownloader_v1.2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file here if you have one (e.g., 'icon.ico')
    version_file=None,  # Can add version info here
    uac_admin=False,  # Don't require admin privileges
    uac_uiaccess=False,
)
