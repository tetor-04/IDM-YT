# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['video_downloader.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['yt_dlp', 'yt_dlp.extractor', 'yt_dlp.downloader', 'yt_dlp.postprocessor', 'requests', 'urllib3', 'certifi', 'websockets', 'mutagen', 'pycryptodomex', 'brotli'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='IDM_Video_Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
