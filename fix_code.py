#!/usr/bin/env python3
"""
Quick fix script to remove duplicate broken code
"""

# Read the file
with open('video_downloader.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 649-697 (0-indexed: 648-696)
fixed_lines = lines[:648] + lines[697:]

# Write back
with open('video_downloader.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed! Removed duplicate code from lines 649-697")
