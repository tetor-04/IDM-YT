#!/usr/bin/env python3
"""
IDM Video Downloader - Test Script
Simple test to verify yt-dlp is working correctly
"""

import yt_dlp
import sys

def test_yt_dlp():
    """Test basic yt-dlp functionality"""
    print("Testing yt-dlp functionality...")
    
    # Test URL (a short public domain video)
    test_url = "https://www.youtube.com/watch?v=RF_PlYkpUfI"  # Sample video
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        print("Extracting video information...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
            print(f"✓ Successfully extracted info for: {info.get('title', 'Unknown')}")
            print(f"✓ Duration: {info.get('duration', 'Unknown')} seconds")
            print(f"✓ Uploader: {info.get('uploader', 'Unknown')}")
            
            # Count available formats
            video_formats = 0
            if 'formats' in info:
                for fmt in info['formats']:
                    if fmt.get('vcodec') != 'none':
                        video_formats += 1
            
            print(f"✓ Available video formats: {video_formats}")
            print("\n✓ yt-dlp is working correctly!")
            return True
            
    except Exception as e:
        print(f"✗ Error testing yt-dlp: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("IDM Video Downloader - System Test")
    print("=" * 50)
    
    # Test Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python version: {python_version}")
    
    # Test yt-dlp
    if test_yt_dlp():
        print("\n🎉 All tests passed! The video downloader is ready to use.")
        print("\nTo run the GUI application:")
        print("  python video_downloader.py")
        print("\nTo run the CLI version:")
        print("  python cli_downloader.py <URL>")
    else:
        print("\n❌ Tests failed. Please check your yt-dlp installation.")
        print("Try: pip install --upgrade yt-dlp")

if __name__ == "__main__":
    main()