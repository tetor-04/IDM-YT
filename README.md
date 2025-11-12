# IDM - Video Downloader

A Python-based Internet Download Manager (IDM) like application for downloading videos from YouTube and other supported platforms with multiple resolution options.

## Features

- 🎥 Download videos from YouTube and 1000+ other sites
- 📊 Multiple quality/resolution options (144p to 4K)
- 🔊 Audio-only download support (MP3)
- 📂 Custom download directory selection
- 📈 Real-time download progress tracking
- 📝 Detailed logging with timestamps
- 🖥️ User-friendly GUI interface
- ⚡ Multi-threaded downloading
- 🚫 Download cancellation support

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

1. **Enter Video URL**: Paste the YouTube video URL in the input field
2. **Fetch Information**: Click "Fetch Info" or press Enter to load video details
3. **Select Quality**: Choose your preferred video quality/format from the dropdown
4. **Set Download Path**: Browse and select where you want to save the video
5. **Start Download**: Click "Download" to begin the download process
6. **Monitor Progress**: Watch the progress bar and detailed logs

## Supported Video Quality Options

- **4K (2160p)** - Ultra High Definition
- **2K (1440p)** - Quad HD  
- **1080p** - Full HD
- **720p** - HD
- **480p** - Standard Definition
- **360p** - Low Quality
- **240p** - Very Low Quality
- **Audio Only** - MP3 format

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
IDM/
├── video_downloader.py    # Main application file
├── requirements.txt       # Python dependencies
├── run_idm.bat           # Windows batch file to run app
└── README.md             # This file
```

## Key Components

### VideoDownloader Class
The main class that handles:
- GUI creation and management
- Video information extraction
- Format selection and processing
- Download progress tracking
- Error handling and logging

### Key Methods
- `fetch_video_info()`: Extracts video metadata using yt-dlp
- `start_download()`: Initiates the download process in a separate thread
- `progress_hook()`: Handles real-time progress updates
- `update_video_info()`: Updates GUI with video information

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

## Updates and Support

For the latest version of yt-dlp and new features:
- Check yt-dlp GitHub: https://github.com/yt-dlp/yt-dlp
- Update with: `pip install --upgrade yt-dlp`

---

**Enjoy downloading videos responsibly!** 🎬📥