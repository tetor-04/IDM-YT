#!/usr/bin/env python3
"""
Internet Download Manager (IDM) - Video Downloader
A GUI application for downloading videos from YouTube and other platforms
with multiple resolution options.

License: Valid until December 31, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import json
import re
from datetime import datetime
import yt_dlp
from pathlib import Path
import sys
import subprocess
from video_window import VideoWindow
from plugin_manager import PluginManager
import shutil
from PIL import Image, ImageTk
import urllib.request
import io
import pyperclip  # For clipboard monitoring
import time
import random


# License expiration check
EXPIRATION_DATE = datetime(2025, 12, 31, 23, 59, 59)
VERSION = "1.2.0"


def check_ffmpeg():
    """Check if FFmpeg is installed and available"""
    try:
        # First check if ffmpeg is in the app's folder (portable)
        app_dir = Path(__file__).parent
        portable_ffmpeg = app_dir / "ffmpeg" / "bin" / "ffmpeg.exe"
        
        if portable_ffmpeg.exists():
            # Add to PATH for this session
            ffmpeg_bin_dir = str(portable_ffmpeg.parent)
            if ffmpeg_bin_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = ffmpeg_bin_dir + os.pathsep + os.environ.get('PATH', '')
            return True
        
        # Check if ffmpeg is in system PATH
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except:
        # Also check using shutil
        return shutil.which('ffmpeg') is not None


def check_license():
    """Check if the application license has expired"""
    current_date = datetime.now()
    
    if current_date > EXPIRATION_DATE:
        return False, "This trial version expired on December 31, 2025."
    
    days_remaining = (EXPIRATION_DATE - current_date).days
    return True, days_remaining


class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title(f"IDM - Video Downloader v{VERSION}")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Check license before proceeding
        is_valid, message = check_license()
        if not is_valid:
            messagebox.showerror("License Expired", 
                               f"{message}\n\nPlease contact support for a license renewal.")
            self.root.destroy()
            sys.exit(1)
        elif message <= 30:  # Show warning if less than 30 days remaining
            messagebox.showinfo("License Notice", 
                              f"This trial version will expire in {message} days.\n"
                              f"Expiration Date: {EXPIRATION_DATE.strftime('%B %d, %Y')}")
        
        # Initialize variables
        self.download_path = str(Path.home() / "Downloads")
        self.video_info = None
        self.download_thread = None
        self.ffmpeg_available = check_ffmpeg()
        self.ffmpeg_warning_shown = False  # Track if warning was shown
        # Subtitles backoff (Advanced) defaults
        self.subs_backoff_max_attempts = tk.IntVar(value=5)
        self.subs_backoff_base_sleep = tk.DoubleVar(value=2.0)
        self.subs_backoff_max_sleep = tk.DoubleVar(value=20.0)
        self.subs_show_advanced = tk.BooleanVar(value=False)
        
        # Playlist support
        self.is_playlist = False
        self.playlist_entries = []
        self.selected_playlist_items = []
        
        # Clipboard monitoring
        self.clipboard_content = ""
        self.clipboard_monitor_enabled = tk.BooleanVar(value=True)
        self.last_clipboard_url = ""
        
        # Initialize plugin system before building the GUI
        self.plugin_manager = PluginManager()
        try:
            self.plugin_manager.discover()
        except Exception:
            pass
        self.plugin_vars = {}

        # Create GUI
        self.create_gui()
        
        # Start clipboard monitoring
        self.monitor_clipboard()
        
        # Show FFmpeg warning if not available (only once, and less intrusive)
        # Commented out - user doesn't want this popup
        # if not self.ffmpeg_available and not self.ffmpeg_warning_shown:
        #     self.root.after(500, self.show_ffmpeg_warning)
        
        # Instead, just log it quietly
        if not self.ffmpeg_available:
            self.root.after(500, lambda: self.log_message("ℹ️ FFmpeg not detected - Audio will save in original format (webm/m4a). Install FFmpeg for MP3 conversion."))
        
        # Configure yt-dlp options
        self.ydl_opts_base = {
            'quiet': False,
            'no_warnings': False,
            'extractaudio': False,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
        }

    def ydl_download_with_backoff(self, ydl_opts, url, is_subtitles=False, context='single'):
        """Call yt-dlp with exponential backoff when encountering HTTP 429.

        - ydl_opts: options dict for YoutubeDL
        - url: single URL string to download
        - is_subtitles: True if we're downloading subtitles-only (more prone to 429)
        - context: 'single' or 'playlist' for logging context
        """
        if is_subtitles:
            try:
                max_attempts = int(self.subs_backoff_max_attempts.get())
            except Exception:
                max_attempts = 5
            try:
                base_sleep = float(self.subs_backoff_base_sleep.get())
            except Exception:
                base_sleep = (ydl_opts.get('sleep_requests', 1.0) or 1.0)
            try:
                max_cap = float(self.subs_backoff_max_sleep.get())
            except Exception:
                max_cap = 20.0
        else:
            max_attempts = 2
            base_sleep = ydl_opts.get('sleep_requests', 1.0) or 1.0
            max_cap = 20.0
        for attempt in range(max_attempts):
            try:
                # Evaluate any deferred/callable values in options
                ydl_opts_local = dict(ydl_opts)
                for _k in ('retries', 'extractor_retries', 'sleep_requests'):
                    if _k in ydl_opts_local and callable(ydl_opts_local[_k]):
                        try:
                            ydl_opts_local[_k] = ydl_opts_local[_k]()
                        except Exception:
                            pass
                with yt_dlp.YoutubeDL(ydl_opts_local) as ydl:
                    ydl.download([url])
                return
            except Exception as e:
                msg = str(e)
                is_429 = ('HTTP Error 429' in msg) or ('Too Many Requests' in msg)
                if is_subtitles and is_429 and attempt < max_attempts - 1:
                    delay = min(max_cap, base_sleep * (2 ** attempt) * random.uniform(1.0, 1.6))
                    try:
                        self.root.after(0, self.log_message, f"⏳ Rate limited (429). Retrying in {delay:.1f}s... [{context}]")
                    except Exception:
                        pass
                    time.sleep(delay)
                    # Increase per-request sleep for next attempt
                    ydl_opts['sleep_requests'] = min(max_cap / 2.0, max(ydl_opts.get('sleep_requests', 0) or 0, delay / 2.0))
                    continue
                raise
        
    def create_gui(self):
        """Create the main GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # URL Input Section - Compact (label, entry, button all in one line)
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="Video URL:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=('Arial', 10))
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.fetch_btn = ttk.Button(url_frame, text="Fetch Info", command=self.fetch_video_info)
        self.fetch_btn.grid(row=0, column=2)
        
        # Video Information Section (collapsible - hidden by default)
        self.info_frame = ttk.LabelFrame(main_frame, text="Video Information", padding="5")
        self.info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        self.info_frame.columnconfigure(1, weight=1)
        self.info_frame.grid_remove()  # Hide by default until video is fetched
        
        # Create a frame to hold thumbnail and text info side by side
        info_content_frame = ttk.Frame(self.info_frame)
        info_content_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N))
        info_content_frame.columnconfigure(1, weight=1)
        
        # Thumbnail display (left side)
        self.thumbnail_label = ttk.Label(info_content_frame, text="No thumbnail", 
                                        relief="sunken", width=20)
        self.thumbnail_label.grid(row=0, column=0, rowspan=4, sticky=(tk.W, tk.N), 
                                 padx=(0, 10), pady=(0, 5))
        
        # Text info (right side)
        text_info_frame = ttk.Frame(info_content_frame)
        text_info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N))
        text_info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(text_info_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.title_var = tk.StringVar()
        ttk.Label(text_info_frame, textvariable=self.title_var, wraplength=450).grid(
            row=0, column=1, sticky=(tk.W, tk.E)
        )
        
        ttk.Label(text_info_frame, text="Duration:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.duration_var = tk.StringVar()
        ttk.Label(text_info_frame, textvariable=self.duration_var).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(text_info_frame, text="Uploader:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.uploader_var = tk.StringVar()
        ttk.Label(text_info_frame, textvariable=self.uploader_var).grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(text_info_frame, text="Views:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5))
        self.views_var = tk.StringVar()
        ttk.Label(text_info_frame, textvariable=self.views_var).grid(row=3, column=1, sticky=tk.W)
        
        # Playlist Section (hidden by default)
        self.playlist_frame = ttk.LabelFrame(main_frame, text="📑 Playlist Items", padding="5")
        self.playlist_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        self.playlist_frame.columnconfigure(0, weight=1)
        self.playlist_frame.grid_remove()  # Hide by default
        
        # Playlist info bar
        playlist_info_frame = ttk.Frame(self.playlist_frame)
        playlist_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        playlist_info_frame.columnconfigure(1, weight=1)
        
        self.playlist_info_var = tk.StringVar()
        ttk.Label(playlist_info_frame, textvariable=self.playlist_info_var, 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Select All / None buttons
        playlist_btn_frame = ttk.Frame(playlist_info_frame)
        playlist_btn_frame.grid(row=0, column=1, sticky=tk.E)
        ttk.Button(playlist_btn_frame, text="Select All", 
                  command=self.select_all_playlist).pack(side=tk.LEFT, padx=2)
        ttk.Button(playlist_btn_frame, text="Select None", 
                  command=self.select_none_playlist).pack(side=tk.LEFT, padx=2)
        
        # Playlist items listbox with scrollbar
        playlist_list_frame = ttk.Frame(self.playlist_frame)
        playlist_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        playlist_list_frame.columnconfigure(0, weight=1)
        playlist_list_frame.rowconfigure(0, weight=1)
        
        playlist_scrollbar = ttk.Scrollbar(playlist_list_frame)
        playlist_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.playlist_listbox = tk.Listbox(playlist_list_frame, 
                                          height=8,
                                          selectmode=tk.MULTIPLE,
                                          yscrollcommand=playlist_scrollbar.set,
                                          font=('Arial', 9))
        self.playlist_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        playlist_scrollbar.config(command=self.playlist_listbox.yview)
        
        # Bind double-click to open individual video window
        self.playlist_listbox.bind('<Double-Button-1>', self.open_video_window)
        
        # Download Type Selection
        type_frame = ttk.LabelFrame(main_frame, text="Download Type", padding="5")
        type_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.download_type = tk.StringVar(value="video")
        ttk.Radiobutton(type_frame, text="🎥 Video", variable=self.download_type, 
                   value="video", command=self.toggle_download_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="🎵 Audio Only", variable=self.download_type, 
                   value="audio", command=self.toggle_download_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="🖼️ Thumbnail", variable=self.download_type, 
                   value="thumbnail", command=self.toggle_download_type).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="💬 Subtitles", variable=self.download_type, 
                   value="subtitles", command=self.toggle_download_type).pack(side=tk.LEFT, padx=10)

        # Extensions (Plugins) Section - Collapsible
        ext_container = ttk.Frame(main_frame)
        ext_container.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ext_container.columnconfigure(0, weight=1)
        
        # Toggle button for extensions
        self.extensions_visible = tk.BooleanVar(value=False)
        self.ext_toggle_btn = ttk.Button(ext_container, text="▶ Show Extensions (Plugins)", 
                                         command=self.toggle_extensions)
        self.ext_toggle_btn.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Extensions frame (hidden by default)
        self.ext_frame = ttk.LabelFrame(ext_container, text="Extensions (Plugins)", padding="5")
        self.ext_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.ext_frame.columnconfigure(0, weight=1)
        self.ext_frame.grid_remove()  # Hide by default
        
        plugin_row = 0
        for plugin in self.plugin_manager.get_plugins():
            var = tk.BooleanVar(value=getattr(plugin, 'enabled', True))
            self.plugin_vars[plugin.id] = var
            cb = ttk.Checkbutton(self.ext_frame, text=f"{plugin.name} — {plugin.description}", variable=var)
            cb.grid(row=plugin_row, column=0, sticky=tk.W, pady=2)
            plugin_row += 1
        ttk.Button(self.ext_frame, text="Run Enabled Extensions", command=self.run_extensions).grid(row=plugin_row, column=0, sticky=tk.W, pady=(6,0))
        
        # Video Format Selection Section
        self.video_frame = ttk.LabelFrame(main_frame, text="Video Quality Options", padding="5")
        self.video_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        self.video_frame.columnconfigure(1, weight=1)

        ttk.Label(self.video_frame, text="Video Quality:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.video_format_var = tk.StringVar()
        self.video_format_combo = ttk.Combobox(self.video_frame, textvariable=self.video_format_var,
                                               state="readonly", width=50)
        self.video_format_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))

        # Audio Format Selection Section
        self.audio_frame = ttk.LabelFrame(main_frame, text="Audio Quality Options", padding="5")
        self.audio_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        self.audio_frame.columnconfigure(1, weight=1)
        self.audio_frame.grid_remove()  # Hide by default

        ttk.Label(self.audio_frame, text="Audio Quality:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.audio_format_var = tk.StringVar()
        self.audio_format_combo = ttk.Combobox(self.audio_frame, textvariable=self.audio_format_var,
                                               state="readonly", width=50)
        self.audio_format_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))

        # Populate audio quality options based on FFmpeg availability
        if self.ffmpeg_available:
            audio_options = [
                ("Best Audio (m4a/webm)", "bestaudio"),
                ("MP3 (Best Quality)", "bestaudio[ext=m4a]/bestaudio"),
                ("MP3 (320kbps)", "bestaudio[ext=m4a]/bestaudio"),
                ("MP3 (192kbps)", "bestaudio[ext=m4a]/bestaudio"),
                ("MP3 (128kbps)", "bestaudio[ext=m4a]/bestaudio"),
                ("High Quality (128kbps+)", "bestaudio[abr>=128]"),
                ("Medium Quality (64-128kbps)", "bestaudio[abr>=64][abr<128]"),
            ]
        else:
            audio_options = [
                ("Best Audio (m4a/webm)", "bestaudio"),
                ("High Quality (128kbps+)", "bestaudio[abr>=128]"),
                ("Medium Quality (64-128kbps)", "bestaudio[abr>=64][abr<128]"),
            ]
        self.audio_format_combo['values'] = [opt[0] for opt in audio_options]
        self.audio_format_options = {opt[0]: opt[1] for opt in audio_options}
        self.audio_format_combo.current(0)

        # Thumbnail Options Section (hidden by default)
        self.thumb_frame = ttk.LabelFrame(main_frame, text="Thumbnail Options", padding="5")
        self.thumb_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.thumb_frame.columnconfigure(1, weight=1)
        self.thumb_frame.grid_remove()

        ttk.Label(self.thumb_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.thumb_convert_jpg = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.thumb_frame, text="Convert to JPG (best quality)",
                        variable=self.thumb_convert_jpg).grid(row=0, column=1, sticky=tk.W)

        # Subtitles Options Section (hidden by default)
        self.subs_frame = ttk.LabelFrame(main_frame, text="Subtitles Options", padding="5")
        self.subs_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.subs_frame.columnconfigure(1, weight=1)
        self.subs_frame.grid_remove()

        # Languages entry
        ttk.Label(self.subs_frame, text="Languages (comma-separated codes):").grid(row=0, column=0, sticky=tk.W)
        self.subs_langs_var = tk.StringVar(value="en, en-*")
        ttk.Entry(self.subs_frame, textvariable=self.subs_langs_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5,0))

        # All languages and auto-generated
        self.subs_all_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.subs_frame, text="Download all available languages",
            variable=self.subs_all_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5,0))

        self.subs_auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.subs_frame, text="Include auto-generated subtitles (fallback)",
            variable=self.subs_auto_var).grid(row=2, column=0, columnspan=2, sticky=tk.W)

        # Subtitles format
        ttk.Label(self.subs_frame, text="Subtitles format:").grid(row=3, column=0, sticky=tk.W, pady=(5,0))
        self.subs_format_var = tk.StringVar(value="best")
        subs_format_combo = ttk.Combobox(self.subs_frame, textvariable=self.subs_format_var,
                                         state="readonly", width=20)
        subs_format_combo['values'] = ["best", "srt", "vtt"]
        subs_format_combo.current(0)
        subs_format_combo.grid(row=3, column=1, sticky=tk.W, pady=(5,0))

        # Gentle warning about rate limiting when requesting many subtitles
        ttk.Label(
            self.subs_frame,
            text=("Tip: requesting 'all languages' together with 'auto-generated' can hit site rate limits.\n"
                  "If both are selected, the app limits to your language list to reduce errors."),
            foreground='gray'
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        # Prevent conflicting selection in UI: if user checks one, uncheck the other
        def on_subs_all_toggle():
            if self.subs_all_var.get() and self.subs_auto_var.get():
                # Prefer keeping auto-generated; uncheck all to reduce requests
                self.subs_all_var.set(False)
                messagebox.showinfo(
                    "Subtitles Options",
                    "To avoid rate limits, you can't select 'All languages' together with 'Auto-generated'.\n"
                    "We'll use your language list with auto-generated instead."
                )

        def on_subs_auto_toggle():
            if self.subs_auto_var.get() and self.subs_all_var.get():
                self.subs_all_var.set(False)
                messagebox.showinfo(
                    "Subtitles Options",
                    "To avoid rate limits, 'All languages' has been turned off while Auto-generated is enabled."
                )

        # Rebind the existing checkbuttons with command hooks
        for child in self.subs_frame.winfo_children():
            if isinstance(child, ttk.Checkbutton):
                txt = child.cget('text')
                if 'Download all available languages' in txt:
                    child.configure(command=on_subs_all_toggle)
                elif 'Include auto-generated subtitles' in txt:
                    child.configure(command=on_subs_auto_toggle)

        # Advanced toggles for backoff
        def toggle_subs_advanced():
            if self.subs_show_advanced.get():
                subs_adv_frame.grid()
            else:
                subs_adv_frame.grid_remove()

        adv_toggle = ttk.Checkbutton(
            self.subs_frame,
            text="Show advanced options",
            variable=self.subs_show_advanced,
            command=toggle_subs_advanced
        )
        adv_toggle.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        subs_adv_frame = ttk.Frame(self.subs_frame)
        subs_adv_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        subs_adv_frame.columnconfigure(1, weight=1)
        subs_adv_frame.grid_remove()

        ttk.Label(subs_adv_frame, text="Max retries:").grid(row=0, column=0, sticky=tk.W)
        try:
            spn_attempts = ttk.Spinbox(subs_adv_frame, from_=2, to=10, textvariable=self.subs_backoff_max_attempts, width=5)
        except Exception:
            spn_attempts = tk.Spinbox(subs_adv_frame, from_=2, to=10, textvariable=self.subs_backoff_max_attempts, width=5)
        spn_attempts.grid(row=0, column=1, sticky=tk.W, padx=(6,0))

        ttk.Label(subs_adv_frame, text="Base sleep (s):").grid(row=1, column=0, sticky=tk.W, pady=(4,0))
        try:
            spn_base = ttk.Spinbox(subs_adv_frame, from_=0.5, to=5.0, increment=0.5, textvariable=self.subs_backoff_base_sleep, width=5)
        except Exception:
            spn_base = tk.Spinbox(subs_adv_frame, from_=0.5, to=5.0, increment=0.5, textvariable=self.subs_backoff_base_sleep, width=5)
        spn_base.grid(row=1, column=1, sticky=tk.W, padx=(6,0), pady=(4,0))

        ttk.Label(subs_adv_frame, text="Max sleep (s):").grid(row=2, column=0, sticky=tk.W, pady=(4,0))
        try:
            spn_cap = ttk.Spinbox(subs_adv_frame, from_=5.0, to=60.0, increment=1.0, textvariable=self.subs_backoff_max_sleep, width=5)
        except Exception:
            spn_cap = tk.Spinbox(subs_adv_frame, from_=5.0, to=60.0, increment=1.0, textvariable=self.subs_backoff_max_sleep, width=5)
        spn_cap.grid(row=2, column=1, sticky=tk.W, padx=(6,0), pady=(4,0))

        # Download Path Section
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)

        ttk.Label(path_frame, text="Download Path:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.path_var = tk.StringVar(value=self.download_path)
        ttk.Entry(path_frame, textvariable=self.path_var, state="readonly").grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5)
        )
        ttk.Button(path_frame, text="Browse", command=self.browse_path).grid(row=0, column=2)

        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Download Progress", padding="5")
        progress_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var).grid(row=1, column=0, sticky=tk.W)

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(0, 10))

        self.download_btn = ttk.Button(button_frame, text="Download",
                                       command=self.start_download, state="disabled")
        self.download_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.cancel_btn = ttk.Button(button_frame, text="Cancel",
                                     command=self.cancel_download, state="disabled")
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 5))
        
        # FFmpeg Download Button (only show if FFmpeg not found)
        if not check_ffmpeg():
            self.ffmpeg_btn = ttk.Button(button_frame, text="📥 Get FFmpeg (for MP3)", 
                                        command=self.download_ffmpeg_gui, 
                                        style="Accent.TButton")
            self.ffmpeg_btn.pack(side=tk.LEFT)
        
        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(9, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # License Status Bar
        license_frame = ttk.Frame(main_frame)
        license_frame.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        _, days_remaining = check_license()
        license_text = f"Trial License • Expires: {EXPIRATION_DATE.strftime('%B %d, %Y')} ({days_remaining} days remaining)"
        self.license_label = ttk.Label(license_frame, text=license_text, 
                                      font=('Arial', 8), foreground='gray')
        self.license_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Clipboard monitor toggle
        self.clipboard_check = ttk.Checkbutton(license_frame, 
                                              text="📋 Auto-detect URLs", 
                                              variable=self.clipboard_monitor_enabled,
                                              command=self.toggle_clipboard_monitor)
        self.clipboard_check.pack(side=tk.LEFT, padx=20)
        
        version_label = ttk.Label(license_frame, text=f"Version {VERSION}", 
                                 font=('Arial', 8), foreground='gray')
        version_label.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Bind Enter key to URL entry
        self.url_entry.bind('<Return>', lambda e: self.fetch_video_info())
    
    def run_extensions(self):
        """Run all enabled plugins against current context."""
        # Sync enabled flags with UI vars
        for p in self.plugin_manager.get_plugins():
            var = self.plugin_vars.get(p.id)
            if var is not None:
                p.enabled = bool(var.get())

        enabled = self.plugin_manager.get_enabled()
        if not enabled:
            messagebox.showinfo("Extensions", "No extensions enabled.")
            return
        if not self.video_info and not (self.is_playlist and self.playlist_entries):
            messagebox.showwarning("Extensions", "Fetch a video or playlist first.")
            return
        self.log_message(f"🔌 Running {len(enabled)} extension(s)...")
        for p in enabled:
            try:
                # Determine context eligibility
                if self.is_playlist and not p.supports_playlist:
                    self.log_message(f"[EXT:{p.id}] Skipped (playlist not supported)")
                    continue
                if (not self.is_playlist) and p.requires_video and not self.video_info:
                    self.log_message(f"[EXT:{p.id}] Skipped (video info required)")
                    continue
                p.run(self, self.video_info, self.playlist_entries if self.is_playlist else None)
                self.log_message(f"[EXT:{p.id}] Completed")
            except Exception as e:
                self.log_message(f"[EXT:{p.id}] Error: {e}")
        
    def show_ffmpeg_warning(self):
        """Show warning about missing FFmpeg"""
        response = messagebox.showinfo(
            "FFmpeg Information",
            "ℹ️ FFmpeg Status: Not Found\n\n"
            "• Video downloads: ✅ Will work normally\n"
            "• Audio downloads: ⚠️ Will download in original format (webm/m4a)\n"
            "• For MP3 conversion: Install FFmpeg\n\n"
            "To install FFmpeg:\n"
            "• Run: install_ffmpeg.bat (in the app folder)\n"
            "• Or: choco install ffmpeg\n"
            "• Or: winget install ffmpeg\n\n"
            "You can use the app now and install FFmpeg later if needed."
        )
        self.log_message("ℹ️ FFmpeg not found - Audio will be saved in original format")
    
    def load_thumbnail(self, thumbnail_url):
        """Download and display video thumbnail"""
        try:
            if not thumbnail_url:
                return
                
            self.log_message(f"Loading thumbnail...")
            
            # Download thumbnail
            with urllib.request.urlopen(thumbnail_url, timeout=10) as response:
                image_data = response.read()
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Resize to fit in the display area (max 160x90 for 16:9 aspect ratio)
            max_width = 160
            max_height = 90
            
            # Calculate aspect ratio
            aspect_ratio = image.width / image.height
            
            if aspect_ratio > (max_width / max_height):
                # Width is the limiting factor
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                # Height is the limiting factor
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update label
            self.thumbnail_label.configure(image=photo, text="")
            self.thumbnail_label.image = photo  # Keep a reference
            
            self.log_message("✓ Thumbnail loaded")
            
        except Exception as e:
            self.log_message(f"⚠️ Could not load thumbnail: {str(e)}")
            self.thumbnail_label.configure(text="No thumbnail\navailable")
    
    def toggle_download_type(self):
        """Toggle between video and audio download options"""
        dtype = self.download_type.get()
        # Hide all optional frames first
        self.video_frame.grid_remove()
        self.audio_frame.grid_remove()
        self.thumb_frame.grid_remove()
        self.subs_frame.grid_remove()

        if dtype == "video":
            self.video_frame.grid()
        elif dtype == "audio":
            if not self.ffmpeg_available and not self.ffmpeg_warning_shown:
                self.log_message("ℹ️ Note: Without FFmpeg, audio saves as webm/m4a (not MP3)")
                self.ffmpeg_warning_shown = True
            self.audio_frame.grid()
        elif dtype == "thumbnail":
            self.thumb_frame.grid()
        elif dtype == "subtitles":
            self.subs_frame.grid()
    
    def toggle_extensions(self):
        """Toggle the visibility of the extensions panel"""
        if self.extensions_visible.get():
            # Hide extensions
            self.ext_frame.grid_remove()
            self.ext_toggle_btn.config(text="▶ Show Extensions (Plugins)")
            self.extensions_visible.set(False)
        else:
            # Show extensions
            self.ext_frame.grid()
            self.ext_toggle_btn.config(text="▼ Hide Extensions (Plugins)")
            self.extensions_visible.set(True)
    
    def log_message(self, message):
        """Add a message to the log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def fetch_video_info(self):
        """Fetch video information from the provided URL"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return
        
        # Check if URL is a channel/profile URL
        is_channel_url = any(pattern in url for pattern in [
            '/channel/', '/@', '/c/', '/user/'
        ])
        
        # If it's a channel URL, ensure we get the /videos tab
        if is_channel_url:
            # Clean up the URL to get videos
            if not url.endswith(('/videos', '/streams', '/shorts')):
                # Add /videos if not already specified
                url = url.rstrip('/') + '/videos'
                self.log_message(f"Channel URL detected, fetching videos tab: {url}")
        
        # Check if URL contains playlist parameter
        has_playlist_param = ('list=' in url and 'youtube.com' in url) or '/playlist' in url
        
        # Determine the URL type
        fetch_as_playlist = False
        
        if is_channel_url:
            # It's a channel URL - ask user what they want
            response = messagebox.askyesno(
                "Channel Detected",
                "🎬 YouTube channel/profile detected!\n\n"
                "Do you want to download ALL videos from this channel?\n\n"
                "• YES - Show all channel videos (may take time to load)\n"
                "• NO - Just view channel info",
                icon='question'
            )
            if response:
                fetch_as_playlist = True
                self.log_message("📺 User chose to fetch all channel videos")
            else:
                self.log_message("ℹ️ Fetching channel info only")
        elif has_playlist_param:
            # It's a playlist URL - ask user what they want
            if 'v=' in url:
                # URL has both video and playlist
                response = messagebox.askyesnocancel(
                    "Playlist or Video?",
                    "🎯 This URL contains both a video and a playlist!\n\n"
                    "What would you like to download?\n\n"
                    "• YES - Download entire playlist\n"
                    "• NO - Download only this video\n"
                    "• CANCEL - Go back",
                    icon='question'
                )
                if response is None:  # Cancel
                    self.fetch_btn.config(state="normal")
                    return
                elif response:  # Yes - playlist
                    fetch_as_playlist = True
                    self.log_message("📑 User chose to download playlist")
                else:  # No - single video
                    fetch_as_playlist = False
                    self.log_message("🎥 User chose to download single video only")
                    # Clean URL - remove playlist parameter
                    import urllib.parse
                    parsed = urllib.parse.urlparse(url)
                    params = urllib.parse.parse_qs(parsed.query)
                    if 'v' in params:
                        clean_params = {'v': params['v']}
                        new_query = urllib.parse.urlencode(clean_params, doseq=True)
                        url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                                      parsed.params, new_query, parsed.fragment))
                        self.log_message(f"Cleaned URL: {url}")
            else:
                # Pure playlist URL
                response = messagebox.askyesno(
                    "Playlist Detected",
                    "📑 YouTube playlist detected!\n\n"
                    "Do you want to download the entire playlist?\n\n"
                    "• YES - Show all playlist videos\n"
                    "• NO - Cancel",
                    icon='question'
                )
                if response:
                    fetch_as_playlist = True
                    self.log_message("📑 User chose to download playlist")
                else:
                    self.fetch_btn.config(state="normal")
                    return
        else:
            # Regular single video URL
            # Clean URL - remove any unwanted parameters
            if 'youtube.com' in url or 'youtu.be' in url:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                
                # Keep only the video ID parameter
                if 'v' in params:
                    clean_params = {'v': params['v']}
                    new_query = urllib.parse.urlencode(clean_params, doseq=True)
                    url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                                  parsed.params, new_query, parsed.fragment))
                    self.log_message(f"Cleaned URL (removed extra params): {url}")
        
        self.fetch_btn.config(state="disabled")
        self.status_var.set("Fetching video information...")
        self.log_message("Fetching video information...")
        
        def fetch_info():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'no_check_certificate': True,
                    'extract_flat': 'in_playlist' if fetch_as_playlist else False,
                    'socket_timeout': 30,
                }
                
                # For channel URLs, we need to extract all videos
                if is_channel_url and fetch_as_playlist:
                    ydl_opts['playlistend'] = None  # Get all videos
                    ydl_opts['ignoreerrors'] = True  # Skip unavailable videos
                
                self.root.after(0, self.log_message, f"Connecting to: {url}")
                
                if fetch_as_playlist:
                    if is_channel_url:
                        self.root.after(0, self.log_message, "� Loading channel videos... (this may take a minute)")
                    else:
                        self.root.after(0, self.log_message, "📑 Loading playlist items...")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.root.after(0, self.log_message, "Extracting video information...")
                    info = ydl.extract_info(url, download=False)
                    
                    if not info:
                        raise Exception("No video information received")
                    
                    # Check if it's a playlist
                    if info.get('_type') == 'playlist':
                        self.root.after(0, self.handle_playlist, info)
                    else:
                        self.video_info = info
                        self.root.after(0, self.log_message, f"Successfully fetched info for: {info.get('title', 'Unknown')}")
                        # Update GUI in main thread
                        self.root.after(0, self.update_video_info, info)
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                error_msg = f"Error fetching video info: {str(e)}\n{error_details}"
                self.root.after(0, self.handle_fetch_error, error_msg)
        
        # Run in separate thread
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def handle_playlist(self, playlist_info):
        """Handle playlist information - Open Advanced Playlist Manager Window"""
        try:
            from advanced_playlist_manager import AdvancedPlaylistManager
            
            self.is_playlist = True
            playlist_entries = playlist_info.get('entries', [])
            # Save entries for plugins and other features
            self.playlist_entries = playlist_entries or []
            playlist_title = playlist_info.get('title', 'Playlist')
            playlist_count = len(playlist_entries)
            
            # Determine if it's a channel or playlist
            uploader = playlist_info.get('uploader', '')
            channel_id = playlist_info.get('channel_id', '')
            
            if uploader or channel_id:
                source_type = "📺 Channel"
                self.log_message(f"📺 Channel detected: {playlist_title}")
            else:
                source_type = "📑 Playlist"
                self.log_message(f"📑 Playlist detected: {playlist_title}")
            
            self.log_message(f"📊 Found {playlist_count} videos")
            self.log_message(f"🎯 Opening Advanced Playlist Manager...")
            
            # Open Advanced Playlist Manager Window
            AdvancedPlaylistManager(self.root, playlist_info, playlist_entries, self.log_message)
            
            # Reset main window
            self.fetch_btn.config(state="normal")
            self.status_var.set(f"{source_type} loaded - {playlist_count} videos")
            
        except Exception as e:
            import traceback
            self.log_message(f"❌ Error opening playlist manager: {str(e)}")
            self.log_message(traceback.format_exc())
            self.fetch_btn.config(state="normal")
    def fetch_playlist_formats(self):
        """Fetch video formats from first video in playlist to populate quality options"""
        try:
            if not self.playlist_entries:
                self.root.after(0, self.log_message, "⚠️ No videos in playlist")
                return
            
            # Get first video URL
            first_video = self.playlist_entries[0]
            video_url = first_video.get('url') or first_video.get('webpage_url') or first_video.get('id')
            
            if not video_url:
                self.root.after(0, self.log_message, "⚠️ Could not get video URL for format detection")
                return
            
            # If we only have ID, construct YouTube URL
            if not video_url.startswith('http'):
                video_url = f"https://www.youtube.com/watch?v={video_url}"
            
            self.root.after(0, self.log_message, f"🔍 Detecting formats from: {first_video.get('title', 'first video')[:50]}...")
            
            # Fetch full info for first video to get formats
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'no_check_certificate': True,
                'socket_timeout': 30,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if not info or 'formats' not in info:
                    self.root.after(0, self.log_message, "⚠️ No formats found")
                    return
                
                # Parse video formats (same logic as single video)
                video_formats = []
                for fmt in info['formats']:
                    if fmt.get('vcodec') != 'none':  # Video formats only
                        height = fmt.get('height')
                        fps = fmt.get('fps')
                        ext = fmt.get('ext', 'mp4')
                        format_note = fmt.get('format_note', '')
                        filesize = fmt.get('filesize')
                        
                        if height:
                            quality_str = f"{height}p"
                            if fps:
                                quality_str += f" {fps}fps"
                            if format_note:
                                quality_str += f" ({format_note})"
                            if filesize:
                                size_mb = filesize / (1024 * 1024)
                                quality_str += f" - {size_mb:.1f}MB"
                            quality_str += f" [{ext}]"
                            
                            video_formats.append((quality_str, fmt['format_id']))
                
                # Sort by quality (height)
                def get_height(fmt_tuple):
                    try:
                        height_match = re.search(r'(\d+)p', fmt_tuple[0])
                        return int(height_match.group(1)) if height_match else 0
                    except:
                        return 0
                
                video_formats.sort(key=get_height, reverse=True)
                
                # Update GUI in main thread
                self.root.after(0, self.update_playlist_formats, video_formats)
                
        except Exception as e:
            error_msg = f"⚠️ Could not fetch formats: {str(e)}"
            self.root.after(0, self.log_message, error_msg)
    
    def update_playlist_formats(self, video_formats):
        """Update video format dropdown with fetched formats"""
        try:
            if video_formats:
                self.video_format_combo['values'] = [fmt[0] for fmt in video_formats]
                self.video_format_options = {fmt[0]: fmt[1] for fmt in video_formats}
                self.video_format_combo.current(0)
                self.log_message(f"✅ Loaded {len(video_formats)} video quality options")
                self.log_message(f"📹 Default: {video_formats[0][0]}")
            else:
                self.log_message("⚠️ No video formats available")
        except Exception as e:
            self.log_message(f"❌ Error updating formats: {str(e)}")
    
    def open_video_window(self, event=None):
        """Open a new window for individual video from playlist"""
        try:
            # Get selected item index
            selection = self.playlist_listbox.curselection()
            if not selection:
                return
            
            idx = selection[0]
            if idx >= len(self.playlist_entries):
                return
            
            video_entry = self.playlist_entries[idx]
            video_title = video_entry.get('title', 'Unknown')
            video_id = video_entry.get('id') or video_entry.get('url')
            
            if not video_id:
                messagebox.showerror("Error", "Could not get video URL")
                return
            
            # Construct video URL
            if not video_id.startswith('http'):
                video_url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                video_url = video_id
            
            self.log_message(f"🔍 Opening video window: {video_title[:50]}...")
            
            # Create new window
            video_window = tk.Toplevel(self.root)
            video_window.title(f"Download: {video_title[:60]}")
            video_window.geometry("700x600")
            video_window.resizable(True, True)
            
            # Create VideoWindow instance
            VideoWindow(video_window, video_url, video_title, self.log_message)
            
        except Exception as e:
            self.log_message(f"❌ Error opening video window: {str(e)}")
            messagebox.showerror("Error", f"Could not open video window: {str(e)}")
        
    def update_video_info(self, info):
        """Update the GUI with video information"""
        try:
            self.log_message("Updating video information in GUI...")
            
            # Mark as single video (not playlist)
            self.is_playlist = False
            self.playlist_frame.grid_remove()  # Hide playlist frame
            
            # Update video info labels
            self.title_var.set(info.get('title', 'N/A'))
            self.log_message(f"Title: {info.get('title', 'N/A')}")
            
            duration = info.get('duration')
            if duration:
                # Convert to int to handle float values from yt-dlp
                duration_int = int(duration)
                minutes, seconds = divmod(duration_int, 60)
                hours, minutes = divmod(minutes, 60)
                if hours:
                    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    duration_str = f"{minutes:02d}:{seconds:02d}"
                self.duration_var.set(duration_str)
            else:
                self.duration_var.set("N/A")
                
            self.uploader_var.set(info.get('uploader', 'N/A'))
            
            # Update view count
            view_count = info.get('view_count')
            if view_count:
                if view_count >= 1_000_000:
                    views_str = f"{view_count / 1_000_000:.1f}M views"
                elif view_count >= 1_000:
                    views_str = f"{view_count / 1_000:.1f}K views"
                else:
                    views_str = f"{view_count} views"
                self.views_var.set(views_str)
            else:
                self.views_var.set("N/A")
            
            # Load thumbnail
            thumbnail_url = info.get('thumbnail')
            if thumbnail_url:
                # Load thumbnail in a separate thread to avoid blocking
                threading.Thread(target=self.load_thumbnail, args=(thumbnail_url,), daemon=True).start()
            else:
                self.thumbnail_label.configure(text="No thumbnail\navailable")
            
            # Populate VIDEO format options only
            self.log_message("Parsing available video formats...")
            video_formats = []
            if 'formats' in info:
                self.log_message(f"Found {len(info['formats'])} total formats")
                for fmt in info['formats']:
                    if fmt.get('vcodec') != 'none':  # Video formats only
                        height = fmt.get('height')
                        fps = fmt.get('fps')
                        ext = fmt.get('ext', 'mp4')
                        format_note = fmt.get('format_note', '')
                        filesize = fmt.get('filesize')
                        
                        if height:
                            quality_str = f"{height}p"
                            if fps:
                                quality_str += f" {fps}fps"
                            if format_note:
                                quality_str += f" ({format_note})"
                            if filesize:
                                size_mb = filesize / (1024 * 1024)
                                quality_str += f" - {size_mb:.1f}MB"
                            quality_str += f" [{ext}]"
                            
                            video_formats.append((quality_str, fmt['format_id']))
            
            # Sort video formats by quality (height)
            def get_height(fmt_tuple):
                try:
                    height_match = re.search(r'(\d+)p', fmt_tuple[0])
                    return int(height_match.group(1)) if height_match else 0
                except:
                    return 0
                    
            video_formats.sort(key=get_height, reverse=True)
            
            self.log_message(f"Found {len(video_formats)} video formats")
            
            # Update VIDEO combobox
            self.video_format_combo['values'] = [fmt[0] for fmt in video_formats]
            self.video_format_options = {fmt[0]: fmt[1] for fmt in video_formats}
            
            if video_formats:
                self.video_format_combo.current(0)
                self.download_btn.config(state="normal")
                self.log_message(f"Default quality: {video_formats[0][0]}")
            else:
                self.log_message("WARNING: No video formats found!")
            
            self.status_var.set("Video information loaded successfully")
            self.log_message("Video information loaded successfully")
            
            # Show the Video Information section now that we have data
            self.info_frame.grid()
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.handle_fetch_error(f"Error processing video info: {str(e)}\n{error_details}")
        finally:
            self.fetch_btn.config(state="normal")
            
    def handle_fetch_error(self, error_msg):
        """Handle errors during video info fetching"""
        # Log the full error to the log text
        self.log_message("="*50)
        self.log_message("ERROR DETAILS:")
        self.log_message(error_msg)
        self.log_message("="*50)
        
        self.status_var.set("Error fetching video information")
        
        # Hide the Video Information section on error
        self.info_frame.grid_remove()
        
        # Show simplified error to user
        if "traceback" in error_msg.lower():
            # Extract just the main error message
            lines = error_msg.split('\n')
            main_error = lines[0] if lines else error_msg
        else:
            main_error = error_msg
            
        messagebox.showerror("Fetch Error", f"{main_error}\n\nCheck the log for more details.")
        self.fetch_btn.config(state="normal")
        
    def download_ffmpeg_gui(self):
        """Download portable FFmpeg with GUI feedback"""
        import subprocess
        import zipfile
        import urllib.request
        
        result = messagebox.askyesno(
            "Download FFmpeg",
            "FFmpeg is required for MP3 conversion.\n\n"
            "Download portable FFmpeg (~100MB)?\n"
            "It will be installed to the app folder only.\n\n"
            "This may take a few minutes..."
        )
        
        if not result:
            return
        
        self.log_message("=" * 50)
        self.log_message("Starting FFmpeg download...")
        
        # Disable buttons during download
        if hasattr(self, 'ffmpeg_btn'):
            self.ffmpeg_btn.config(state="disabled", text="Downloading...")
        self.download_btn.config(state="disabled")
        
        def download_thread():
            try:
                # Get app directory
                if getattr(sys, 'frozen', False):
                    app_dir = os.path.dirname(sys.executable)
                else:
                    app_dir = os.path.dirname(os.path.abspath(__file__))
                
                ffmpeg_dir = os.path.join(app_dir, "ffmpeg", "bin")
                os.makedirs(ffmpeg_dir, exist_ok=True)
                
                # Download URL
                url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
                zip_path = os.path.join(app_dir, "ffmpeg_temp.zip")
                
                self.root.after(0, self.log_message, "Downloading FFmpeg from gyan.dev...")
                self.root.after(0, self.status_var.set, "Downloading FFmpeg...")
                
                # Download with progress
                def reporthook(count, block_size, total_size):
                    if total_size > 0:
                        percent = int(count * block_size * 100 / total_size)
                        if percent <= 100:
                            self.root.after(0, self.progress_var.set, percent)
                            self.root.after(0, self.status_var.set, 
                                          f"Downloading FFmpeg... {percent}%")
                
                urllib.request.urlretrieve(url, zip_path, reporthook)
                
                self.root.after(0, self.log_message, "Download complete! Extracting...")
                self.root.after(0, self.status_var.set, "Extracting FFmpeg...")
                self.root.after(0, self.progress_var.set, 0)
                
                # Extract
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Find ffmpeg.exe and ffprobe.exe in the zip
                    for file in zip_ref.namelist():
                        if file.endswith(('ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe')):
                            # Extract just these files
                            file_data = zip_ref.read(file)
                            file_name = os.path.basename(file)
                            target_path = os.path.join(ffmpeg_dir, file_name)
                            with open(target_path, 'wb') as f:
                                f.write(file_data)
                            self.root.after(0, self.log_message, f"Extracted: {file_name}")
                
                # Clean up
                os.remove(zip_path)
                
                self.root.after(0, self.log_message, "✅ FFmpeg installed successfully!")
                self.root.after(0, self.log_message, f"Location: {ffmpeg_dir}")
                self.root.after(0, self.log_message, "You can now download MP3 audio! 🎵")
                self.root.after(0, self.status_var.set, "FFmpeg ready!")
                self.root.after(0, self.progress_var.set, 100)
                
                # Update FFmpeg status and reload audio options
                self.root.after(0, self._update_after_ffmpeg_install)
                
                self.root.after(0, messagebox.showinfo, "Success", 
                              "FFmpeg installed successfully!\nYou can now download MP3 audio.")
                
            except Exception as e:
                error_msg = f"Failed to download FFmpeg: {str(e)}"
                self.root.after(0, self.log_message, f"❌ {error_msg}")
                self.root.after(0, self.status_var.set, "FFmpeg download failed")
                self.root.after(0, self.progress_var.set, 0)
                
                # Re-enable button
                if hasattr(self, 'ffmpeg_btn'):
                    self.root.after(0, self.ffmpeg_btn.config, 
                                  {"state": "normal", "text": "📥 Get FFmpeg (for MP3)"})
                
                self.root.after(0, messagebox.showerror, "Download Failed", error_msg)
        
        # Start download in background thread
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def _update_after_ffmpeg_install(self):
        """Update UI after FFmpeg is installed"""
        # Hide the FFmpeg button
        if hasattr(self, 'ffmpeg_btn'):
            self.ffmpeg_btn.pack_forget()
        
        # Re-check FFmpeg availability
        self.ffmpeg_available = check_ffmpeg()
        
        # Update audio format options to include MP3
        if self.ffmpeg_available:
            audio_options = [
                ("Best Audio (m4a/webm)", "bestaudio"),
                ("MP3 (Best Quality)", "bestaudio[ext=m4a]/bestaudio"),
                ("MP3 (320kbps)", "bestaudio[ext=m4a]/bestaudio"),
                ("MP3 (192kbps)", "bestaudio[ext=m4a]/bestaudio"),
                ("MP3 (128kbps)", "bestaudio[ext=m4a]/bestaudio"),
                ("High Quality (128kbps+)", "bestaudio[abr>=128]"),
                ("Medium Quality (64-128kbps)", "bestaudio[abr>=64][abr<128]"),
            ]
            self.log_message("✅ MP3 formats are now available!")
        else:
            audio_options = [
                ("Best Audio (m4a/webm)", "bestaudio"),
                ("High Quality (128kbps+)", "bestaudio[abr>=128]"),
                ("Medium Quality (64-128kbps)", "bestaudio[abr>=64][abr<128]"),
            ]
        
        # Update combobox
        self.audio_format_combo['values'] = [opt[0] for opt in audio_options]
        self.audio_format_options = {opt[0]: opt[1] for opt in audio_options}
        self.audio_format_combo.current(0)
        
        # Re-enable download button if video info is loaded
        if self.video_info:
            self.download_btn.config(state="normal")
        
        self.log_message("Audio format options updated!")
    
    def browse_path(self):
        """Browse for download directory"""
        path = filedialog.askdirectory(initialdir=self.download_path)
        if path:
            self.download_path = path
            self.path_var.set(path)
            
    def start_download(self):
        """Start the download process"""
        # Check if it's a playlist download
        if self.is_playlist:
            return self.start_playlist_download()
        
        if not self.video_info:
            messagebox.showerror("Error", "Please fetch video information first")
            return
        
        dtype = self.download_type.get()
        # Get the selected format based on download type
        if dtype == "video":
            selected_format = self.video_format_var.get()
            format_id = self.video_format_options.get(selected_format)
            if not selected_format:
                messagebox.showerror("Error", "Please select a video quality first")
                return
        elif dtype == "audio":
            selected_format = self.audio_format_var.get()
            format_id = self.audio_format_options.get(selected_format)
            if not selected_format:
                messagebox.showerror("Error", "Please select an audio quality first")
                return
        elif dtype == "thumbnail":
            selected_format = "thumbnail"
            format_id = None
        elif dtype == "subtitles":
            selected_format = "subtitles"
            format_id = None
            
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_var.set(0)
        
        self.log_message(f"Starting download: {selected_format}")
        self.status_var.set("Downloading...")
        
        def download():
            try:
                # Re-check FFmpeg availability right before download
                self.ffmpeg_available = check_ffmpeg()
                
                ydl_opts = {
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                }
                
                if dtype == "thumbnail":
                    # Only download thumbnail in best available quality
                    ydl_opts.update({
                        'skip_download': True,
                        'writethumbnail': True,
                    })
                    if self.thumb_convert_jpg.get():
                        ydl_opts['convert_thumbnails'] = 'jpg'
                    self.root.after(0, self.log_message, "🖼️ Saving thumbnail only")
                elif dtype == "subtitles":
                    # Only download subtitles
                    ydl_opts.update({
                        'skip_download': True,
                        'writesubtitles': True,
                        # Base throttling
                        'retries': lambda: int(self.subs_backoff_max_attempts.get()) if hasattr(self, 'subs_backoff_max_attempts') else 8,
                        'extractor_retries': 4,
                        'sleep_requests': lambda: float(self.subs_backoff_base_sleep.get()) if hasattr(self, 'subs_backoff_base_sleep') else 2.0,
                        'http_headers': {'Accept-Language': 'en-US,en;q=0.9'}
                    })
                    # Decide language strategy:
                    all_langs = self.subs_all_var.get()
                    auto_gen = self.subs_auto_var.get()
                    langs_raw = [s.strip() for s in self.subs_langs_var.get().split(',') if s.strip()]
                    # If both all languages and auto subtitles selected, log warning and prefer explicit list + auto
                    if all_langs and auto_gen:
                        self.root.after(0, self.log_message, "⚠️ Both 'all languages' and 'auto-generated' selected. Limiting to provided list + auto to avoid HTTP 429.")
                        all_langs = False  # override to reduce requests
                        if not langs_raw:
                            langs_raw = ['en']
                    if all_langs:
                        ydl_opts['allsubtitles'] = True
                    else:
                        # Filter obvious malformed codes (allow patterns like en-*)
                        valid_langs = []
                        for code in langs_raw:
                            if re.match(r'^[a-zA-Z]{2}(?:-[a-zA-Z0-9*]+)?$', code):
                                valid_langs.append(code)
                            else:
                                self.root.after(0, self.log_message, f"🚫 Ignoring invalid subtitle language code: {code}")
                        if valid_langs:
                            ydl_opts['subtitleslangs'] = valid_langs
                    if auto_gen:
                        ydl_opts['writeautomaticsub'] = True
                    subfmt = self.subs_format_var.get()
                    if subfmt and subfmt != 'best':
                        ydl_opts['subtitlesformat'] = subfmt
                    self.root.after(0, self.log_message, "💬 Saving subtitles only")
                elif dtype == "audio":
                    # Check if user selected MP3 format
                    is_mp3_requested = "MP3" in selected_format
                    if is_mp3_requested:
                        if self.ffmpeg_available:
                            if "320" in selected_format or "Best Quality" in selected_format:
                                quality = '320'
                            elif "192" in selected_format:
                                quality = '192'
                            elif "128" in selected_format:
                                quality = '128'
                            else:
                                quality = '320'
                            ydl_opts.update({
                                'format': 'bestaudio/best',
                                'postprocessors': [{
                                    'key': 'FFmpegExtractAudio',
                                    'preferredcodec': 'mp3',
                                    'preferredquality': quality,
                                }],
                            })
                            self.root.after(0, self.log_message, f"✅ Using FFmpeg to convert to MP3 ({quality} kbps)")
                        else:
                            ydl_opts['format'] = 'bestaudio/best'
                            self.root.after(0, self.log_message, 
                                            "⚠️ FFmpeg not available - Downloading audio in original format (webm/m4a)")
                            self.root.after(0, self.log_message, 
                                            "Click 'Get FFmpeg' button for MP3 conversion")
                    else:
                        ydl_opts['format'] = format_id
                else:
                    # Video
                    ydl_opts['format'] = format_id
                
                # Use adaptive backoff for subtitles to reduce HTTP 429
                self.ydl_download_with_backoff(
                    ydl_opts,
                    self.video_info['webpage_url'],
                    is_subtitles=(dtype == "subtitles"),
                    context='single'
                )
                
                self.root.after(0, self.download_complete)
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                
                # Check if it's an FFmpeg error
                if 'ffmpeg' in str(e).lower() or 'postprocessing' in str(e).lower():
                    error_msg = ("FFmpeg Error: Audio conversion failed!\n\n"
                               "FFmpeg is not installed or not accessible.\n\n"
                               "To fix this:\n"
                               "1. Download FFmpeg: https://ffmpeg.org/download.html\n"
                               "2. Extract and add to system PATH\n"
                               "3. Restart the application\n\n"
                               f"Technical details: {str(e)}")
                else:
                    error_msg = f"Download error: {str(e)}\n\n{error_details}"
                    
                self.root.after(0, self.download_error, error_msg)
        
        self.download_thread = threading.Thread(target=download, daemon=True)
        self.download_thread.start()
    
    def start_playlist_download(self):
        """Download selected playlist items"""
        # Get selected indices
        selected_indices = self.playlist_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select at least one video to download")
            return
        
        # Get selected entries
        selected_entries = [self.playlist_entries[i] for i in selected_indices]
        total_count = len(selected_entries)
        
        self.log_message(f"📑 Starting playlist download: {total_count} videos")
        
        # Get format settings
        dtype = self.download_type.get()
        if dtype == "video":
            selected_format = self.video_format_var.get()
            format_id = self.video_format_options.get(selected_format)
        elif dtype == "audio":
            selected_format = self.audio_format_var.get()
            format_id = self.audio_format_options.get(selected_format)
        else:
            selected_format = dtype
            format_id = None
        
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        
        def download_playlist():
            try:
                for idx, entry in enumerate(selected_entries, 1):
                    video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    video_title = entry.get('title', 'Unknown')
                    
                    self.root.after(0, self.log_message, f"[{idx}/{total_count}] Downloading: {video_title}")
                    self.root.after(0, self.status_var.set, f"Downloading {idx}/{total_count}: {video_title[:50]}...")
                    
                    # Re-check FFmpeg availability
                    self.ffmpeg_available = check_ffmpeg()

                    ydl_opts = {
                        'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                        'progress_hooks': [lambda d: self.root.after(0, self.playlist_progress_hook, d, idx, total_count)],
                    }

                    if dtype == "thumbnail":
                        ydl_opts.update({'skip_download': True, 'writethumbnail': True})
                        if self.thumb_convert_jpg.get():
                            ydl_opts['convert_thumbnails'] = 'jpg'
                    elif dtype == "subtitles":
                        ydl_opts.update({
                            'skip_download': True,
                            'writesubtitles': True,
                            'retries': lambda: int(self.subs_backoff_max_attempts.get()) if hasattr(self, 'subs_backoff_max_attempts') else 8,
                            'extractor_retries': 4,
                            'sleep_requests': lambda: float(self.subs_backoff_base_sleep.get()) if hasattr(self, 'subs_backoff_base_sleep') else 2.0,
                            'http_headers': {'Accept-Language': 'en-US,en;q=0.9'}
                        })
                        all_langs = self.subs_all_var.get()
                        auto_gen = self.subs_auto_var.get()
                        langs_raw = [s.strip() for s in self.subs_langs_var.get().split(',') if s.strip()]
                        if all_langs and auto_gen:
                            self.root.after(0, self.log_message, "⚠️ Both 'all languages' and 'auto-generated' selected. Limiting to provided list + auto to avoid HTTP 429.")
                            all_langs = False
                            if not langs_raw:
                                langs_raw = ['en']
                        if all_langs:
                            ydl_opts['allsubtitles'] = True
                        else:
                            valid_langs = []
                            for code in langs_raw:
                                if re.match(r'^[a-zA-Z]{2}(?:-[a-zA-Z0-9*]+)?$', code):
                                    valid_langs.append(code)
                                else:
                                    self.root.after(0, self.log_message, f"🚫 Ignoring invalid subtitle language code: {code}")
                            if valid_langs:
                                ydl_opts['subtitleslangs'] = valid_langs
                        if auto_gen:
                            ydl_opts['writeautomaticsub'] = True
                        subfmt = self.subs_format_var.get()
                        if subfmt and subfmt != 'best':
                            ydl_opts['subtitlesformat'] = subfmt
                    elif dtype == "audio":
                        is_mp3_requested = "MP3" in selected_format
                        if is_mp3_requested:
                            if self.ffmpeg_available:
                                quality = '320'
                                if "192" in selected_format:
                                    quality = '192'
                                elif "128" in selected_format:
                                    quality = '128'
                                ydl_opts.update({
                                    'format': 'bestaudio/best',
                                    'postprocessors': [{
                                        'key': 'FFmpegExtractAudio',
                                        'preferredcodec': 'mp3',
                                        'preferredquality': quality,
                                    }],
                                })
                            else:
                                ydl_opts['format'] = 'bestaudio/best'
                        else:
                            ydl_opts['format'] = format_id
                    else:
                        ydl_opts['format'] = format_id
                    
                    # Adaptive backoff for subtitles entries
                    self.ydl_download_with_backoff(
                        ydl_opts,
                        video_url,
                        is_subtitles=(dtype == "subtitles"),
                        context=f'playlist item {idx}/{total_count}'
                    )
                    
                    self.root.after(0, self.log_message, f"✅ [{idx}/{total_count}] Completed: {video_title}")
                
                self.root.after(0, self.playlist_download_complete, total_count)
                
            except Exception as e:
                error_msg = f"Playlist download error: {str(e)}"
                self.root.after(0, self.download_error, error_msg)
        
        threading.Thread(target=download_playlist, daemon=True).start()
    
    def playlist_progress_hook(self, d, current, total):
        """Handle playlist download progress"""
        if d['status'] == 'downloading':
            try:
                if 'total_bytes' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    return
                
                self.progress_var.set(progress)
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / (1024 * 1024)
                    self.status_var.set(f"[{current}/{total}] Downloading... {progress:.1f}% @ {speed_mb:.2f} MB/s")
            except:
                pass
        elif d['status'] == 'finished':
            self.progress_var.set(100)
    
    def playlist_download_complete(self, count):
        """Handle playlist download completion"""
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.progress_var.set(100)
        self.status_var.set(f"✅ Playlist complete! {count} videos downloaded")
        self.log_message(f"🎉 Playlist download complete! Downloaded {count} videos")
        messagebox.showinfo("Success", f"Playlist download complete!\n\n{count} videos downloaded successfully.")
    
    def progress_hook(self, d):
        """Handle download progress updates"""
        if d['status'] == 'downloading':
            try:
                if 'total_bytes' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    return
                    
                self.root.after(0, self.update_progress, progress, d)
            except:
                pass
        elif d['status'] == 'finished':
            self.root.after(0, self.update_progress, 100, d)
            
    def update_progress(self, progress, d):
        """Update progress bar and status"""
        self.progress_var.set(progress)
        
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        speed = d.get('speed', 0)
        
        if speed:
            speed_str = f"{speed / 1024 / 1024:.1f} MB/s"
        else:
            speed_str = "0 MB/s"
            
        if total:
            downloaded_mb = downloaded / 1024 / 1024
            total_mb = total / 1024 / 1024
            status = f"Downloading... {downloaded_mb:.1f}/{total_mb:.1f} MB ({progress:.1f}%) - {speed_str}"
        else:
            status = f"Downloading... {progress:.1f}% - {speed_str}"
            
        self.status_var.set(status)
        
    def download_complete(self):
        """Handle download completion"""
        self.progress_var.set(100)
        self.status_var.set("Download completed successfully!")
        self.log_message("Download completed successfully!")
        
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        
        messagebox.showinfo("Success", "Download completed successfully!")
        
    def download_error(self, error_msg):
        """Handle download errors"""
        self.log_message(error_msg)
        self.status_var.set("Download failed")
        
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        
        messagebox.showerror("Download Error", error_msg)
        
    def cancel_download(self):
        """Cancel the current download"""
        self.log_message("Download cancelled by user")
        self.status_var.set("Download cancelled")
        
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        
    def monitor_clipboard(self):
        """Monitor clipboard for YouTube URLs"""
        if not self.clipboard_monitor_enabled.get():
            # Check again in 1 second
            self.root.after(1000, self.monitor_clipboard)
            return
        
        try:
            # Get current clipboard content
            current_clipboard = pyperclip.paste()
            
            # Check if clipboard changed and contains a YouTube/video URL
            if current_clipboard != self.last_clipboard_url and current_clipboard:
                # Check if it's a valid URL
                url_pattern = r'(https?://)?(www\.)?(youtube|youtu|vimeo|dailymotion|twitch)\.(com|be)/'
                if re.search(url_pattern, current_clipboard, re.IGNORECASE):
                    # Valid video URL detected
                    self.last_clipboard_url = current_clipboard
                    
                    # Show notification in status bar
                    self.status_var.set(f"📋 URL detected in clipboard!")
                    self.log_message(f"📋 Clipboard: Video URL detected!")
                    
                    # Auto-paste to URL field if it's empty
                    if not self.url_var.get().strip():
                        self.url_var.set(current_clipboard.strip())
                        self.log_message("✅ URL auto-pasted from clipboard")
                        
                        # Auto-focus on the fetch button
                        self.fetch_btn.focus_set()
                    else:
                        # URL field already has content - just notify
                        self.log_message("ℹ️ New URL detected, but URL field is not empty")
        
        except Exception as e:
            # Silently ignore clipboard errors
            pass
        
        # Check again in 1 second
        self.root.after(1000, self.monitor_clipboard)
    
    def toggle_clipboard_monitor(self):
        """Toggle clipboard monitoring on/off"""
        if self.clipboard_monitor_enabled.get():
            self.log_message("✅ Clipboard monitor enabled - Auto-detecting URLs")
            self.status_var.set("Clipboard monitor: ON")
        else:
            self.log_message("⏸️ Clipboard monitor paused")
            self.status_var.set("Clipboard monitor: OFF")
    
    def select_all_playlist(self):
        """Select all playlist items"""
        self.playlist_listbox.selection_set(0, tk.END)
        self.log_message(f"✅ Selected all {len(self.playlist_entries)} playlist items")
    
    def select_none_playlist(self):
        """Deselect all playlist items"""
        self.playlist_listbox.selection_clear(0, tk.END)
        self.log_message("⏹️ Cleared playlist selection")
    
    def clear_all(self):
        """Clear all fields and reset the interface"""
        self.url_var.set("")
        self.title_var.set("")
        self.duration_var.set("")
        self.uploader_var.set("")
        self.views_var.set("")
        self.video_format_var.set("")
        self.video_format_combo['values'] = []
        self.audio_format_combo.current(0)  # Reset to default audio quality
        self.progress_var.set(0)
        self.status_var.set("Ready")
        self.log_text.delete(1.0, tk.END)
        
        # Reset thumbnail
        self.thumbnail_label.configure(image='', text="No thumbnail")
        self.thumbnail_label.image = None
        
        # Reset playlist
        self.is_playlist = False
        self.playlist_entries = []
        self.playlist_frame.grid_remove()
        self.playlist_listbox.delete(0, tk.END)
        self.playlist_info_var.set("")
        
        # Hide Video Information section
        self.info_frame.grid_remove()
        
        self.video_info = None
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = VideoDownloader(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()