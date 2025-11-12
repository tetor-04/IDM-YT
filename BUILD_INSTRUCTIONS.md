# Building Portable Windows Application
## IDM Video Downloader v1.2.0

## Prerequisites

1. **Python 3.7 or later** installed on Windows
2. **pip** package manager (included with Python)
3. **Internet connection** for downloading dependencies

## Build Methods

### Method 1: Automatic Build (Recommended)

Simply run the build script:

```batch
build_portable_win7.bat
```

This will:
- ✅ Check Python installation
- ✅ Install required packages (PyInstaller, yt-dlp, Pillow, pyperclip)
- ✅ Clean previous builds
- ✅ Build the executable
- ✅ Create portable package with plugins and README
- ✅ Display build summary

**Output:** `dist\IDM_VideoDownloader_Portable\`

### Method 2: Quick Build

For a faster build without packaging:

```batch
build_quick.bat
```

**Output:** `dist\IDM_VideoDownloader.exe`

### Method 3: Manual Build

If you want to build manually:

```batch
# 1. Install PyInstaller
pip install pyinstaller

# 2. Build with spec file
pyinstaller build_portable.spec

# 3. Executable will be in dist\ folder
```

## Windows 7 Compatibility

The build is configured for **Windows 7 SP1** and later:

- ✅ No admin privileges required
- ✅ Compatible with Windows 7, 8, 8.1, 10, 11
- ✅ Single executable (no installation needed)
- ✅ Portable (can run from USB drive)
- ✅ Includes all dependencies

## Package Contents

After building, you'll get:

```
IDM_VideoDownloader_Portable/
├── IDM_VideoDownloader_v1.2.0.exe    (Main executable)
├── plugins/                          (Optional plugins)
│   ├── metadata_plugin.py
│   ├── chapters_text_plugin.py
│   ├── comments_plugin.py
│   ├── sponsorblock_plugin.py
│   ├── thumbnails_variants_plugin.py
│   └── playlist_index_plugin.py
└── README.txt                        (User instructions)
```

## Troubleshooting

### "Python not found"
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### "PyInstaller not found"
```batch
pip install pyinstaller
```

### Build fails with import errors
```batch
pip install --upgrade yt-dlp pillow pyperclip requests
```

### Executable is too large
- The exe is ~80-120MB (includes Python runtime + all libraries)
- Use UPX compression (enabled by default in spec file)
- This is normal for Python applications

### Antivirus flags the executable
- This is a false positive (common with PyInstaller)
- You can submit the file to antivirus vendors
- Users may need to add exception in their antivirus

## Testing

After building, test the executable:

1. Navigate to `dist\IDM_VideoDownloader_Portable\`
2. Double-click `IDM_VideoDownloader_v1.2.0.exe`
3. Try downloading a test video
4. Check if plugins load correctly
5. Test FFmpeg download feature

## Distribution

To distribute your application:

1. Zip the entire `IDM_VideoDownloader_Portable` folder
2. Share the zip file
3. Users just extract and run the .exe

**No installation required!**

## File Size Optimization

Current build includes:
- Python runtime: ~15MB
- yt-dlp library: ~3MB
- PIL/Pillow: ~5MB
- Other dependencies: ~10MB
- Application code: ~500KB

Total: ~80-120MB (compressed to ~40-60MB with UPX)

## Advanced Configuration

Edit `build_portable.spec` to customize:

- `excludes`: Remove unused libraries to reduce size
- `upx=True`: Enable/disable UPX compression
- `console=False`: Show/hide console window
- `icon`: Add custom icon file
- `hiddenimports`: Add additional dependencies

## Version Info

To add version information to the executable:

1. Create a `version.txt` file:
```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 2, 0, 0),
    prodvers=(1, 2, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'Your Name'),
        StringStruct('FileDescription', 'IDM Video Downloader'),
        StringStruct('FileVersion', '1.2.0.0'),
        StringStruct('ProductName', 'IDM Video Downloader'),
        StringStruct('ProductVersion', '1.2.0.0')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
```

2. Add to spec file: `version_file='version.txt'`

## Support

For issues during build:
- Check Python version: `python --version` (should be 3.7+)
- Check PyInstaller version: `pyinstaller --version` (should be 5.0+)
- Check pip: `pip --version`
- Clear cache: Delete `build/`, `dist/`, `__pycache__/` folders

## License

Built application includes:
- License valid until December 31, 2025
- For personal use only
- See README.txt in portable package for details
