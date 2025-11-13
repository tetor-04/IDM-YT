# IDM - Video Downloader

A Python-based Internet Download Manager (IDM) like application for downloading videos from YouTube and other supported platforms with multiple resolution options.

## Features

### Core Download Features
- 🎥 **Video Downloads** - YouTube and 1000+ other sites with multiple quality options (144p to 4K)
- 🎵 **Audio Downloads** - MP3 format with quality selection (128-320kbps)
- 🖼️ **Thumbnail Downloads** - Save video thumbnails in high quality
- 💬 **Subtitle Downloads** - Download subtitles in multiple languages (SRT/VTT)
- 📑 **Playlist Support** - Download entire playlists or select specific videos
- � **Channel Downloads** - Download all videos from a YouTube channel

### Advanced Features
- 📋 **Auto URL Detection** - Automatically detects video URLs from clipboard
- 🔌 **Plugin System** - Extensible with plugins for metadata, chapters, comments, and more
- 📊 **Advanced Playlist Manager** - Filter, sort, and batch download playlist videos
- 🎯 **Individual Video Windows** - Open specific videos from playlists in separate windows
- 📈 **Real-time Progress** - Live download progress with speed monitoring
- 📝 **Detailed Logging** - Timestamped logs for all operations

### User Interface
- 🖥️ **Modern GUI** - Clean, intuitive interface built with Tkinter
- 🎨 **Video Previews** - Thumbnail display with video information
- 📂 **Custom Download Paths** - Choose where to save your files
- ⚡ **Multi-threaded** - Non-blocking downloads with cancel support

## Requirements

- Python 3.7 or higher
- Internet connection
- Windows, macOS, or Linux
- **FFmpeg** (Required for audio downloads/MP3 conversion)

## Installation

### Option 1: Easy Installation (Windows)
1. Double-click `run_idm.bat` - it will automatically install dependencies and run the application

### Option 2: Manual Installation
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg (Required for Audio Downloads)**:
   - **Easy Method (Windows)**: Double-click `install_ffmpeg.bat` and follow the menu
   - **Chocolatey**: `choco install ffmpeg`
   - **Winget**: `winget install ffmpeg`
   - **Manual**: Download from https://ffmpeg.org/download.html and add to PATH

3. Run the application:
   ```bash
   python video_downloader.py
   ```

## Usage

### Basic Video Download
1. **Enter Video URL**: Paste the YouTube video URL (auto-detects from clipboard!)
2. **Fetch Information**: Click "Fetch Info" or press Enter to load video details
3. **Select Download Type**: Choose Video, Audio Only, Thumbnail, or Subtitles
4. **Select Quality**: Choose your preferred quality/format from the dropdown
5. **Set Download Path**: Browse and select where you want to save the file
6. **Start Download**: Click "Download" to begin
7. **Monitor Progress**: Watch the progress bar and detailed logs

### Playlist Downloads
1. **Paste Playlist URL**: The app will detect it's a playlist
2. **Choose Action**: Download entire playlist or just view info
3. **Advanced Manager Opens**: Filter, sort, and select videos
4. **Select Videos**: Choose which videos to download (Select All/None buttons available)
5. **Batch Download**: Download selected videos with progress tracking

### Channel Downloads
1. **Paste Channel URL**: The app detects YouTube channels
2. **Confirm**: Choose to download all channel videos or just view info
3. **Video List Loads**: All channel videos are displayed
4. **Select & Download**: Choose videos and download in batch

### Plugin/Extensions
1. **Click "Show Extensions"**: Expand the plugin panel
2. **Enable Plugins**: Check the plugins you want to use
3. **Run Extensions**: Click "Run Enabled Extensions" after fetching video info
   - **Metadata Plugin**: Extract detailed video metadata to JSON
   - **Chapters Plugin**: Save video chapters to text file
   - **Comments Plugin**: Download video comments
   - **Playlist Index**: Add index numbers to playlist downloads
   - **SponsorBlock**: Get sponsor segments information
   - **Thumbnail Variants**: Download all available thumbnail sizes

## Download Options

### Video Quality
- **4K (2160p)** - Ultra High Definition
- **2K (1440p)** - Quad HD  
- **1080p** - Full HD
- **720p** - HD
- **480p** - Standard Definition
- **360p, 240p, 144p** - Lower qualities

### Audio Quality (MP3)
- **320kbps** - Best quality
- **192kbps** - High quality
- **128kbps** - Standard quality
- **Original format** - WebM/M4A (without FFmpeg)

### Additional Downloads
- **Thumbnails** - JPG format (best quality)
- **Subtitles** - Multiple languages, auto-generated support, SRT/VTT formats

## Supported Platforms

This application supports video downloads from 1000+ websites including:
- YouTube
- Vimeo
- Facebook
- Instagram
- TikTok
- Twitter
- Dailymotion
- And many more...

## File Structure

```
IDM-YT/
├── video_downloader.py              # Main GUI application
├── cli_downloader.py                # Command-line interface
├── advanced_playlist_manager.py     # Advanced playlist management
├── playlist_manager.py              # Playlist utilities
├── channel_content_downloader.py    # Channel downloader
├── plugin_manager.py                # Plugin system manager
├── plugins/                         # Plugin directory
│   ├── __init__.py
│   ├── base_plugin.py
│   ├── chapters_text_plugin.py      # Extract chapter information
│   ├── comments_plugin.py           # Download video comments
│   ├── metadata_plugin.py           # Extract detailed metadata
│   ├── playlist_index_plugin.py     # Add playlist index to filenames
│   ├── sponsorblock_plugin.py       # SponsorBlock integration
│   └── thumbnails_variants_plugin.py # Download all thumbnail variants
├── requirements.txt                 # Python dependencies
├── run_idm.bat                      # Quick launcher (Windows)
├── install_ffmpeg.bat               # FFmpeg installer
├── download_ffmpeg.bat              # FFmpeg downloader
└── README.md                        # This file
```

## Key Components

### Main Application (`video_downloader.py`)
- **VideoDownloader Class**: Main GUI application
- Clipboard monitoring for auto URL detection
- Playlist and channel detection
- Plugin system integration
- Multi-threaded downloads with progress tracking

### CLI Version (`cli_downloader.py`)
Command-line interface for automation and scripting:
```bash
python cli_downloader.py "URL" [quality]
python cli_downloader.py "URL" list  # List available formats
```

### Advanced Playlist Manager
- Filter videos by keyword, duration, date
- Sort by various criteria (date, views, duration)
- Bulk selection with regex patterns
- Individual video preview windows
- Batch download with progress tracking

### Plugin System
- Extensible architecture with `BasePlugin`
- Easy plugin development
- Context-aware (single video vs playlist)
- Run plugins on-demand or automatically

## Configuration

### Default Settings
- **Download Path**: User's Downloads folder
- **Video Format**: Best available quality
- **Audio Format**: MP3 (192kbps for audio-only downloads)

### Customization
You can modify the `ydl_opts_base` dictionary in the code to change default yt-dlp options:
```python
self.ydl_opts_base = {
    'quiet': False,
    'no_warnings': False,
    'extractaudio': False,
    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
    # Add more options as needed
}
```

## Troubleshooting

### Common Issues

1. **"No module named 'yt_dlp'" Error**
   - Solution: Run `pip install yt-dlp`

2. **Video extraction fails**
   - Solution: Update yt-dlp with `pip install --upgrade yt-dlp`

3. **Download speed is slow**
   - This depends on your internet connection and the video server

4. **Some videos can't be downloaded**
   - Some videos may be geo-blocked or have download restrictions

### FFmpeg (Optional but recommended)
For better format conversion and audio extraction, install FFmpeg:
- Windows: Download from https://ffmpeg.org/download.html
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## Legal Notice

This tool is for educational purposes. Please respect:
- Platform terms of service
- Copyright laws
- Content creator rights
- Local regulations

Only download videos you have permission to download or that are in the public domain.

## License

This project is provided as-is for educational purposes. Use responsibly and in accordance with applicable laws and platform terms of service.

## Building Portable Executable

To create a standalone executable:
```bash
# Install PyInstaller
pip install pyinstaller

# Build portable version
build_portable.bat
```

The executable will be created in the `dist/` folder.

## Updates and Support

For the latest version of yt-dlp and new features:
- Check yt-dlp GitHub: https://github.com/yt-dlp/yt-dlp
- Update with: `pip install --upgrade yt-dlp`

## Documentation

📚 **[Complete Documentation](docs/README.md)** - Comprehensive guides and references

### Quick Links
- **Features**: [Clipboard Monitor](docs/features/FEATURE_1_CLIPBOARD_MONITOR.md) | [Playlist Support](docs/features/FEATURE_2_PLAYLIST_SUPPORT.md) | [All Features](docs/features/FEATURES.md)
- **Guides**: [Build Instructions](docs/guides/BUILD_INSTRUCTIONS.md) | [Plugin System](docs/guides/PLUGINS.md) | [User Manual](docs/guides/PRESENTATION_AND_USER_MANUAL.md)
- **Troubleshooting**: [FFmpeg Fix](docs/fixes/FFMPEG_FIX.md) | [MP3 Solutions](docs/fixes/MP3_SOLUTIONS.md) | [Channel Fix](docs/fixes/CHANNEL_URL_FIX.md)

## Contributing

Contributions are welcome! Feel free to:
- Report bugs or request features via Issues
- Submit pull requests for improvements
- Create new plugins to extend functionality

See the [docs/](docs/) folder for detailed documentation on features, building, and troubleshooting.

---

**Enjoy downloading videos responsibly!** 🎬📥