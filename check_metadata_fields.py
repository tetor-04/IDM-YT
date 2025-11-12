#!/usr/bin/env python3
"""
Check all available metadata fields from yt-dlp for a YouTube video
"""
import yt_dlp
import json

# Test with a sample video URL (you can change this)
test_url = input("Enter a YouTube video URL (or press Enter for default): ").strip()
if not test_url:
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Sample video

print(f"\n🔍 Fetching metadata from: {test_url}\n")

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(test_url, download=False)
        
        if info:
            print("=" * 80)
            print("ALL AVAILABLE METADATA FIELDS:")
            print("=" * 80)
            
            # Get all top-level keys
            all_keys = sorted(info.keys())
            
            # Categorize fields
            basic_info = []
            technical_info = []
            engagement_info = []
            channel_info = []
            timestamp_info = []
            content_info = []
            other_info = []
            
            for key in all_keys:
                value = info[key]
                value_type = type(value).__name__
                
                # Get sample value (truncate if too long)
                if value is None:
                    sample = "None"
                elif isinstance(value, (list, dict)):
                    sample = f"<{value_type} with {len(value)} items>"
                elif isinstance(value, str) and len(value) > 60:
                    sample = f"{value[:60]}..."
                else:
                    sample = str(value)
                
                field_info = f"  • {key:30s} [{value_type:10s}] = {sample}"
                
                # Categorize
                if key in ['id', 'title', 'description', 'uploader', 'channel', 'display_id']:
                    basic_info.append(field_info)
                elif key in ['view_count', 'like_count', 'comment_count', 'average_rating', 'repost_count']:
                    engagement_info.append(field_info)
                elif key in ['channel_id', 'uploader_id', 'uploader_url', 'channel_url', 'channel_follower_count']:
                    channel_info.append(field_info)
                elif key in ['timestamp', 'upload_date', 'release_timestamp', 'modified_timestamp', 'release_date']:
                    timestamp_info.append(field_info)
                elif key in ['duration', 'width', 'height', 'fps', 'vcodec', 'acodec', 'resolution', 'format', 'formats', 'filesize', 'tbr', 'abr', 'vbr']:
                    technical_info.append(field_info)
                elif key in ['tags', 'categories', 'chapters', 'subtitles', 'automatic_captions', 'language', 'age_limit', 'is_live', 'was_live', 'live_status']:
                    content_info.append(field_info)
                else:
                    other_info.append(field_info)
            
            # Print categorized
            if basic_info:
                print("\n📌 BASIC INFO:")
                print("\n".join(basic_info))
            
            if engagement_info:
                print("\n💬 ENGAGEMENT:")
                print("\n".join(engagement_info))
            
            if channel_info:
                print("\n📺 CHANNEL INFO:")
                print("\n".join(channel_info))
            
            if timestamp_info:
                print("\n📅 TIMESTAMPS:")
                print("\n".join(timestamp_info))
            
            if technical_info:
                print("\n⚙️ TECHNICAL:")
                print("\n".join(technical_info))
            
            if content_info:
                print("\n📝 CONTENT INFO:")
                print("\n".join(content_info))
            
            if other_info:
                print("\n🔧 OTHER:")
                print("\n".join(other_info))
            
            print("\n" + "=" * 80)
            print(f"TOTAL FIELDS: {len(all_keys)}")
            print("=" * 80)
            
            # Suggest useful fields not yet used
            print("\n💡 SUGGESTED ADDITIONAL FIELDS FOR GUI:")
            suggestions = []
            
            if 'like_count' in info and info['like_count']:
                suggestions.append(f"  • like_count: {info['like_count']:,} likes")
            if 'comment_count' in info and info['comment_count']:
                suggestions.append(f"  • comment_count: {info['comment_count']:,} comments")
            if 'tags' in info and info['tags']:
                suggestions.append(f"  • tags: {len(info['tags'])} tags available")
            if 'chapters' in info and info['chapters']:
                suggestions.append(f"  • chapters: {len(info['chapters'])} chapters")
            if 'description' in info and info['description']:
                suggestions.append(f"  • description: {len(info['description'])} characters")
            if 'age_limit' in info:
                suggestions.append(f"  • age_limit: {info['age_limit']} (age restriction)")
            if 'language' in info and info['language']:
                suggestions.append(f"  • language: {info['language']}")
            if 'live_status' in info:
                suggestions.append(f"  • live_status: {info['live_status']} (is_live, was_live, etc)")
            if 'channel_follower_count' in info and info['channel_follower_count']:
                suggestions.append(f"  • channel_follower_count: {info['channel_follower_count']:,} subscribers")
            if 'availability' in info:
                suggestions.append(f"  • availability: {info['availability']}")
            
            if suggestions:
                print("\n".join(suggestions))
            else:
                print("  (Check the fields above for more options)")
            
            print("\n")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
