import os
import random
import argparse
from pathlib import Path
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, vfx


def reel_with_solid_broll_middle(
    main_video_path,
    broll_folder="brolls",
    output_path=None,
    max_broll_duration=28,
    intro_percent=0.13,
    outro_percent=0.10,
    seed=None
):
    random.seed(seed)

    main = VideoFileClip(main_video_path)
    TARGET = (1080, 1920)
    if main.size != TARGET:
        main = main.with_effects([vfx.Resize(TARGET)])

    total_dur = main.duration
    intro_end = total_dur * intro_percent
    middle_dur = total_dur * (1 - intro_percent - outro_percent)

    print(f"Duration: {total_dur:.1f}s | Intro: {intro_end:.1f}s | B-roll block: {middle_dur:.1f}s")

    # Load b-rolls
    broll_paths = [p for p in Path(broll_folder).rglob("*") if p.suffix.lower() in {".mp4"}]
    if not broll_paths:
        raise ValueError(f"No b-rolls found in {broll_folder}")
    random.shuffle(broll_paths)
    print(f"Found {len(broll_paths)} b-roll clips")

    # Build middle section
    middle_clips = []
    needed = middle_dur
    i = 0

    while needed > 0.2:
        if i >= len(broll_paths):
            print("Not enough unique b-rolls → looping")
            i = 0

        broll_path = broll_paths[i]
        print(f"Using b-roll: {broll_path.name}")

        raw = VideoFileClip(str(broll_paths[i])).without_audio()

        # Smart letterbox/pillarbox — never crop content
        if raw.w / raw.h > 1080 / 1920:  # landscape → fit to width
            clip = raw.with_effects([vfx.Resize(width=1080)])
        else:
            clip = raw.with_effects([vfx.Resize(height=1920)])
        
        # v2 replacement for on_color: Composite on a black background
        from moviepy import ColorClip, CompositeVideoClip
        bg = ColorClip(size=(1080, 1920), color=(0,0,0)).with_duration(clip.duration)
        clip = CompositeVideoClip([bg, clip.with_position('center')])

        dur = min(clip.duration, max_broll_duration, needed)
        middle_clips.append(clip.subclipped(0, dur))
        needed -= dur
        i += 1
        raw.close()

    # Adjust outro start time
    actual_middle_dur = sum(c.duration for c in middle_clips)
    outro_start = intro_end + actual_middle_dur

    # Assemble
    final_clips = [
        main.subclipped(0, intro_end),
        *middle_clips,
        main.subclipped(outro_start, total_dur)
    ]

    final_video = concatenate_videoclips(final_clips, method="compose")
    
    # --- SFX INJECTION START ---
    sfx_path = "assets/sfx/whoosh.mp3"
    if os.path.exists(sfx_path):
        print(f"Adding SFX from: {sfx_path}")
        try:
            sfx_clip = AudioFileClip(sfx_path)
            # Calculate cut timestamps
            # 1. Intro -> Middle
            timestamps = [intro_end]
            
            # 2. Middle clips internal cuts
            current_time = intro_end
            for clip in middle_clips[:-1]: # All middle clips represent a cut at their end, except the last one which transitions to outro
                current_time += clip.duration
                timestamps.append(current_time)
                
            # 3. Middle -> Outro
            # outro_start is already calculated above as intro_end + actual_middle_dur
            timestamps.append(outro_start)
            
            audio_layers = [main.audio]
            for t in timestamps:
                # Add SFX at time t
                # We start the SFX slightly before the cut for better feeling (optional, but let's keep it simple for now)
                audio_layers.append(sfx_clip.with_start(t))
                
            final_audio = CompositeAudioClip(audio_layers)
            final_video = final_video.with_audio(final_audio)

        except Exception as e:
            print(f"Failed to add SFX: {e}")
            final_video = final_video.with_audio(main.audio)
    else:
        print(f"No SFX found at {sfx_path} — skipping sound effects.")
        final_video = final_video.with_audio(main.audio)
    # --- SFX INJECTION END ---

    final_video = final_video.with_duration(main.audio.duration)

    # Auto output path
    if output_path is None:
        output_path = f"output/broll_{Path(main_video_path).stem}.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Export
    final_video.write_videofile(
        output_path,
        fps=30, codec="libx264", audio_codec="aac",
        preset="medium", bitrate="20000k", threads=os.cpu_count(),
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )

    print(f"B-ROLLS ADDED → {output_path}")
    print(f"OUTPUT_PATH={output_path}")   # ← Master script reads this line!

    main.close()
    final_video.close()
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Step 2: Add beautiful b-rolls to HeyGen video")
    parser.add_argument("--input", type=str, help="Input video path (e.g. media/abc123.mp4)")
    parser.add_argument("--broll-folder", type=str, default="brolls", help="Folder with b-roll clips")
    parser.add_argument("--output", type=str, help="Output path (optional)")
    args = parser.parse_args()

    # Auto-detect latest HeyGen video if no input given
    if not args.input:
        media_files = list(Path("media").glob("*.mp4"))
        if not media_files:
            print("No video in media/ folder. Run heygen5.py first!")
            return
        input_path = str(max(media_files, key=os.path.getctime))
        print(f"Auto-detected latest video → {Path(input_path).name}")
    else:
        input_path = args.input
        if not os.path.exists(input_path):
            print(f"File not found: {input_path}")
            return

    reel_with_solid_broll_middle(
        main_video_path=input_path,
        broll_folder=args.broll_folder,
        output_path=args.output
    )


if __name__ == "__main__":
    main()