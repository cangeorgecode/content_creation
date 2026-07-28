#!/usr/bin/env python3
"""
Multi-Platform Formatter — Takes a finished captioned video and produces
platform-optimized variants for YouTube (long-form), LinkedIn, and X/Twitter.

Usage:
    python platform_formatter.py output/my_video_captioned.mp4
    python platform_formatter.py output/my_video_captioned.mp4 --platforms linkedin,x
    python platform_formatter.py output/my_video_captioned.mp4 --all

Output:
    output/my_video_captioned_<platform>.mp4
"""

import os
import argparse
import subprocess
from pathlib import Path

# ─── Platform Configs ──────────────────────────────────────────────
PLATFORMS = {
    "youtube": {
        "label": "YouTube (Long Form)",
        "aspect": "16:9",
        "width": 1920,
        "height": 1080,
        "description": "Horizontal, 1920x1080. Best for long-form content.",
        "format_suffix": "_ytlong",
    },
    "linkedin": {
        "label": "LinkedIn",
        "aspect": "1:1",
        "width": 1080,
        "height": 1080,
        "description": "Square, 1080x1080. Best for feed posts.",
        "format_suffix": "_linkedin",
    },
    "x": {
        "label": "X / Twitter",
        "aspect": "16:9 (landscape)",
        "width": 1920,
        "height": 1080,
        "description": "Horizontal, 1920x1080. Best for X/Twitter video posts.",
        "format_suffix": "_x",
    },
    "portrait": {
        "label": "Instagram / TikTok / Shorts",
        "aspect": "9:16",
        "width": 1080,
        "height": 1920,
        "description": "Vertical, 1080x1920. The native format. (Just copies if already portrait)",
        "format_suffix": "",
    },
}


def get_video_info(video_path):
    """Get video dimensions using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        parts = result.stdout.strip().split(",")
        return int(parts[0]), int(parts[1])
    return None, None


def reformat_video(input_path, output_path, target_w, target_h):
    """Reformat video to target dimensions with smart letterboxing."""
    input_w, input_h = get_video_info(input_path)
    if input_w is None:
        print(f"  ⚠ Could not determine video dimensions for {input_path}")
        return False

    input_aspect = input_w / input_h
    target_aspect = target_w / target_h

    print(f"    Input: {input_w}x{input_h} | Target: {target_w}x{target_h}")

    if input_w == target_w and input_h == target_h:
        print(f"    → Already at target dimensions. Copying.")
        import shutil
        shutil.copy2(input_path, output_path)
        return True

    # Build ffmpeg filter for letterboxing
    if abs(input_aspect - target_aspect) < 0.01:
        # Same aspect ratio — just scale
        filter_chain = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"
    elif input_aspect > target_aspect:
        # Input is wider — pillarbox (black bars on sides)
        filter_chain = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"
    else:
        # Input is taller — letterbox (black bars on top/bottom)
        filter_chain = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", filter_chain,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"    → Created: {Path(output_path).name}")
        return True
    else:
        print(f"    ⚠ ffmpeg error: {result.stderr[-200:]}")
        return False


def format_for_platforms(input_path, platforms=None, all_flag=False):
    """Format a video for specified platforms."""
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"❌ Video not found: {input_path}")
        return []

    if all_flag:
        platforms = list(PLATFORMS.keys())
    elif not platforms:
        platforms = ["portrait"]  # Default: just confirm portrait

    results = []
    stem = input_path.stem
    if stem.endswith("_captioned"):
        stem = stem[:-10]  # Remove _captioned suffix for cleaner names

    for platform in platforms:
        if platform not in PLATFORMS:
            print(f"  ⚠ Unknown platform: {platform}")
            continue

        config = PLATFORMS[platform]
        suffix = config["format_suffix"]
        output_name = f"{stem}{suffix}.mp4"
        output_path = input_path.parent / output_name

        print(f"\n  📱 {config['label']} ({config['aspect']})")
        ok = reformat_video(input_path, output_path, config["width"], config["height"])
        if ok:
            results.append(str(output_path))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Platform Formatter — Create platform-optimized video variants"
    )
    parser.add_argument("input", nargs="?", type=str, help="Input video file (e.g. output/my_video_captioned.mp4)")
    parser.add_argument("--platforms", "-p", type=str, default="",
                        help="Comma-separated platforms: youtube,linkedin,x,portrait")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Generate all platform variants")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available platforms")

    args = parser.parse_args()

    if args.list:
        print(f"\nAvailable Platforms:")
        for name, config in PLATFORMS.items():
            print(f"  {name:15s} {config['label']:30s} {config['width']}x{config['height']}")
        print()
        return

    if not args.input:
        print("Please specify an input video or use --list to see available platforms.")
        parser.print_help()
        return

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()] if args.platforms else None

    results = format_for_platforms(args.input, platforms, args.all)

    if results:
        print(f"\n{'='*60}")
        print(f"  Platforms Created: {len(results)}")
        for r in results:
            size = Path(r).stat().st_size / (1024 * 1024)
            print(f"  ✅ {Path(r).name} ({size:.1f} MB)")
        print(f"{'='*60}")
    else:
        print("\n  No platforms were created.")


if __name__ == "__main__":
    main()
