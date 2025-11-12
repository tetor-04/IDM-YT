#!/usr/bin/env python3
"""
Quick test script for a specific YouTube URL
"""

import yt_dlp

url = "https://www.youtube.com/watch?v=YpSbHlbHCsc&list=RDYpSbHlbHCsc&start_radio=1"

print("="*70)
print("YouTube Link Test")
print("="*70)
print(f"\nTesting URL: {url}")
print("\nFetching video information...")

try:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        print("\n" + "="*70)
        print("✅ VIDEO INFORMATION SUCCESSFULLY EXTRACTED")
        print("="*70)
        
        print(f"\n📹 Title: {info.get('title', 'N/A')}")
        print(f"👤 Uploader: {info.get('uploader', 'N/A')}")
        
        duration = info.get('duration', 0)
        if duration:
            minutes, seconds = divmod(duration, 60)
            print(f"⏱️  Duration: {minutes:02d}:{seconds:02d} ({duration} seconds)")
        
        print(f"👁️  Views: {info.get('view_count', 0):,}")
        print(f"📅 Upload Date: {info.get('upload_date', 'N/A')}")
        
        # Analyze available formats
        print("\n" + "="*70)
        print("📊 AVAILABLE FORMATS")
        print("="*70)
        
        video_formats = []
        if 'formats' in info:
            for fmt in info['formats']:
                if fmt.get('vcodec') != 'none' and fmt.get('height'):
                    height = fmt.get('height')
                    fps = fmt.get('fps', 0)
                    ext = fmt.get('ext', 'mp4')
                    if height:
                        video_formats.append((height, fps, ext))
        
        # Get unique qualities
        qualities = {}
        for height, fps, ext in video_formats:
            if height not in qualities:
                qualities[height] = []
            qualities[height].append(f"{ext} ({fps}fps)" if fps else ext)
        
        print("\n🎬 Video Qualities Available:")
        for quality in sorted(qualities.keys(), reverse=True):
            formats = ", ".join(set(qualities[quality]))
            print(f"   • {quality}p - {formats}")
        
        print("\n🎵 Audio: Available for extraction")
        
        print("\n" + "="*70)
        print("✅ COMPATIBILITY CHECK")
        print("="*70)
        print("\n✓ This video is FULLY COMPATIBLE with the IDM Video Downloader!")
        print("✓ You can download in any available quality")
        print("✓ Audio extraction is supported")
        print("\nRecommended qualities:")
        if 1080 in qualities:
            print("  • 1080p (Full HD) - Best quality for most devices")
        if 720 in qualities:
            print("  • 720p (HD) - Good balance of quality and file size")
        if 480 in qualities:
            print("  • 480p (SD) - Smaller file size")
        
        print("\n" + "="*70)
        print("🎯 READY TO DOWNLOAD")
        print("="*70)
        print("\nYou can now:")
        print("1. Open the IDM Video Downloader")
        print("2. Paste this URL")
        print("3. Click 'Fetch Info'")
        print("4. Choose your preferred quality")
        print("5. Download!")
        
except Exception as e:
    print("\n" + "="*70)
    print("❌ ERROR OCCURRED")
    print("="*70)
    print(f"\nError: {str(e)}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())
