#!/usr/bin/env python3
"""
factory3.py — ContentReel Production Pipeline
=============================================
One command to generate scripts, produce avatar videos, add b-rolls,
add captions, and manage the script queue — with resume/skip logic.

Usage:
    python factory3.py swipe_files/scripts.json              # Process existing scripts
    python factory3.py --generate 5                          # Generate + process 5 scripts
    python factory3.py --generate 10 --hook curiosity         # Mixed hook styles
    python factory3.py --status                               # Show pipeline state
    python factory3.py --retry failed                         # Retry failed scripts
    python factory3.py --reset 2                              # Reset script ID 2
"""

import sys
import subprocess
import json
import os
import argparse
from pathlib import Path
from datetime import datetime
from pipeline_state import PipelineState

# ─── Configuration ────────────────────────────────────────────────
HEYGEN_SCRIPT = "heygen6.py"
BROLL_SCRIPT = "broll2.py"
PYCAPS_SCRIPT = "pycaps2.py"
SCRIPT_GEN = "script_generator.py"

REQUIRED_FOLDERS = ["brolls", "media", "output", "swipe_files"]


def run_cmd(cmd, description=""):
    """Run a shell command and return output. Exit on failure."""
    label = f" → {description}" if description else ""
    print(f"\nRunning{' ' + ' '.join(cmd)}{label}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print("  ERROR:")
        for line in result.stderr.strip().splitlines()[-5:]:
            print(f"  | {line}")
        return None
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            print(f"  | {line}")
    return result.stdout


def get_output_path(stdout):
    """Extract OUTPUT_PATH= from command stdout."""
    if stdout is None:
        return None
    for line in stdout.splitlines():
        if line.startswith("OUTPUT_PATH="):
            return line.split("=", 1)[1].strip()
    return None


def ensure_folders():
    """Create required folders if they don't exist."""
    for folder in REQUIRED_FOLDERS:
        Path(folder).mkdir(exist_ok=True)
    print(f"✓ Folders ready: {', '.join(REQUIRED_FOLDERS)}")


def check_brolls():
    """Warn if brolls folder is empty."""
    brolls = list(Path("brolls").glob("*.mp4"))
    if not brolls:
        print("⚠ WARNING: brolls/ folder is empty! The b-roll step will fail.")
        print("  Add some .mp4 clips to brolls/ before running the pipeline.")
        return False
    print(f"✓ Found {len(brolls)} b-roll clips")
    return True


def generate_scripts(count=5, hook="auto", body="auto", cta="hard",
                     niche="content automation", provider="openai"):
    """Generate scripts using the script generator module."""
    print(f"\n{'='*60}")
    print(f"  Generating {count} AI scripts ({hook} hooks, {provider})")
    print(f"{'='*60}")

    cmd = [
        sys.executable, SCRIPT_GEN,
        "--count", str(count),
        "--hook", hook,
        "--body", body,
        "--cta", cta,
        "--niche", niche,
        "--provider", provider,
    ]
    stdout = run_cmd(cmd, description="AI Script Generation")
    if stdout is None:
        print("  ❌ Script generation failed. Check your API key in .env")
        return None

    # Find the generated file path from output
    for line in stdout.splitlines():
        if "Saved" in line and ".json" in line:
            parts = line.strip().split()
            for p in parts:
                if p.startswith("swipe_files/") and p.endswith(".json"):
                    print(f"  ✓ Generated scripts saved to {p}")
                    return p
    return None


def process_single_script(script_file, script_entry, state, voice_id=None, title=None):
    """Process one script through the full pipeline with resume/skip."""
    script_id = script_entry.get("id")
    script_text = script_entry.get("script", "").strip()
    niche = script_entry.get("niche", "unknown")

    if script_id is None:
        print("\n⚠ Script has no 'id' field — cannot track state. Processing fresh.")
        script_id = f"unnamed_{datetime.now().timestamp()}"

    if not script_text:
        print(f"\n⚠ Script ID {script_id} has empty content. Skipping.")
        return False

    print(f"\n{'='*60}")
    print(f"  Processing Script ID {script_id} [{niche}]")
    print(f"{'='*60}")

    status = state.get_status(script_id)
    print(f"  State: {status}")

    # ─── Check if already fully completed ────────────────────────
    if status == "completed":
        final = state.data.get(str(script_id), {}).get("final_output")
        if final and Path(final).exists():
            print(f"  ✓ Already completed → {final}")
            return True
        else:
            print(f"  State says completed but file missing. Re-processing...")
            state.reset_script(script_id)

    # ─── Step 1: HeyGen Avatar Video ─────────────────────────────
    heygen_path = None
    if state.needs_heygen(script_id):
        print("\n  1. Generating avatar video with HeyGen...")

        # Check if media file already exists (belt-and-suspenders)
        existing = state.get_step_output(script_id, "heygen")
        if existing and Path(existing).exists():
            print(f"     ✓ Found existing HeyGen video: {existing}")
            heygen_path = existing
            state.set_heygen_done(script_id, existing)
        else:
            # Run heygen6.py directly via subprocess with the script text
            # We'll call heygen6.py with --json pointing to a temp file for this script
            temp_script = Path(f"swipe_files/_temp_{script_id}.json")
            try:
                with open(temp_script, "w") as f:
                    json.dump([script_entry], f)

                cmd = [sys.executable, HEYGEN_SCRIPT, "--json", str(temp_script)]
                if voice_id:
                    cmd.extend(["--voice", voice_id])
                if title:
                    cmd.extend(["--title", title])

                stdout = run_cmd(cmd, description="HeyGen API")
                if stdout is None:
                    state.set_failed(script_id, "heygen", "HeyGen API call failed")
                    return False

                heygen_path = get_output_path(stdout)
                if heygen_path and Path(heygen_path).exists():
                    state.set_heygen_done(script_id, heygen_path)
                else:
                    state.set_failed(script_id, "heygen", "Output path not found")
                    return False
            finally:
                if temp_script.exists():
                    temp_script.unlink()
    else:
        # Resume from previous state
        heygen_path = state.get_step_output(script_id, "heygen")
        if heygen_path and Path(heygen_path).exists():
            print(f"  ✓ HeyGen step already done → {Path(heygen_path).name}")
        else:
            print("  ⚠ State says HeyGen done but file missing. Re-running...")
            state.reset_script(script_id)
            return process_single_script(script_file, script_entry, state, voice_id, title)

    # ─── Step 2: B-Rolls ──────────────────────────────────────────
    if state.needs_broll(script_id):
        print("\n  2. Adding b-rolls...")

        existing = state.get_step_output(script_id, "broll")
        if existing and Path(existing).exists():
            print(f"     ✓ Found existing b-roll video: {existing}")
            state.set_broll_done(script_id, existing)
        else:
            # Ensure brolls directory has files
            if not list(Path("brolls").glob("*.mp4")):
                print("  ❌ No b-rolls found in brolls/ folder. Skipping b-roll step.")
                state.set_broll_done(script_id, heygen_path)  # Skip, use HeyGen video as-is
            else:
                stdout = run_cmd([
                    sys.executable, BROLL_SCRIPT,
                    "--input", str(heygen_path),
                ], description="B-Roll Processing")
                if stdout is None:
                    state.set_failed(script_id, "broll", "B-roll processing failed")
                    return False

                broll_path = get_output_path(stdout)
                if broll_path and Path(broll_path).exists():
                    state.set_broll_done(script_id, broll_path)
                else:
                    state.set_failed(script_id, "broll", "B-roll output not found")
                    return False
    else:
        broll_path = state.get_step_output(script_id, "broll") or heygen_path
        if broll_path and Path(broll_path).exists():
            print(f"  ✓ B-roll step already done → {Path(broll_path).name}")
        else:
            broll_path = heygen_path
            print(f"  → Using HeyGen video for captions (b-rolls unavailable)")

    # ─── Step 3: Captions (PyCaps) ───────────────────────────────
    # Get the actual broll output path
    broll_path = state.get_step_output(script_id, "broll") or heygen_path

    if state.needs_captions(script_id):
        print("\n  3. Adding captions...")

        existing = state.get_step_output(script_id, "captions")
        if existing and Path(existing).exists():
            print(f"     ✓ Found existing captioned video: {existing}")
            state.set_captions_done(script_id, existing)
            return True

        # Check if captioned output already exists (naming convention)
        captioned_name = Path(str(broll_path)).stem + "_captioned.mp4"
        captioned_path = Path("output") / captioned_name
        if captioned_path.exists():
            print(f"     ✓ Captioned file already exists: {captioned_path}")
            state.set_captions_done(script_id, str(captioned_path))
            return True

        stdout = run_cmd([
            sys.executable, PYCAPS_SCRIPT,
            "--input", str(broll_path),
            "--template", "templates/centered",
        ], description="Caption Rendering")

        if stdout is None:
            state.set_failed(script_id, "captions", "PyCaps failed")
            return False

        # Find the output file
        for line in stdout.splitlines():
            if "Final video" in line or "captioned" in line:
                for part in line.split():
                    if "_captioned.mp4" in part:
                        state.set_captions_done(script_id, part)
                        return True

        # Fallback: check if file was created
        if captioned_path.exists():
            state.set_captions_done(script_id, str(captioned_path))
            return True

        state.set_failed(script_id, "captions", "Could not find captioned output")
        return False
    else:
        print(f"  ✓ Captions step already done")
        return True


def show_status(state):
    """Show the pipeline state summary."""
    summary = state.get_summary()
    failed = state.get_failed()

    print(f"\n{'='*60}")
    print(f"  ContentReel Pipeline Status")
    print(f"{'='*60}")
    print(f"  Completed:  {summary['completed']}")
    print(f"  B-Roll Done: {summary['broll_done']}")
    print(f"  HeyGen Done: {summary['heygen_done']}")
    print(f"  Failed:     {summary['failed']}")
    print(f"  New/Untracked: {summary['new']}")
    if failed:
        print(f"\n  Failed Scripts:")
        for sid, info in failed.items():
            print(f"    ID {sid}: failed at '{info.get('failed_at', '?')}' — {info.get('error', 'no error')}")
    print()


def retry_failed(state, script_file):
    """Retry all failed scripts."""
    failed = state.get_failed()
    if not failed:
        print("  No failed scripts to retry.")
        return

    # Load the original script file
    if not Path(script_file).exists():
        print(f"  ❌ Script file not found: {script_file}")
        return

    with open(script_file) as f:
        scripts = json.load(f)

    script_map = {str(s.get("id")): s for s in scripts}

    for sid in failed:
        if sid in script_map:
            print(f"\n  Retrying script ID {sid}...")
            state.reset_script(sid)
            process_single_script(script_file, script_map[sid], state)
        else:
            print(f"  ⚠ Script ID {sid} not found in {script_file}. Removing from state.")
            state.remove_script(sid)


def main():
    parser = argparse.ArgumentParser(
        description="ContentReel Production Pipeline — Generate, process, and manage video scripts"
    )
    parser.add_argument("script_file", nargs="?", type=str,
                        help="Path to scripts JSON file (e.g. swipe_files/scripts.json)")
    parser.add_argument("--generate", "-g", type=int, default=0, metavar="N",
                        help="Generate N scripts first, then process them")
    parser.add_argument("--hook", "-k", type=str, default="auto",
                        help="Hook style for generation (auto, problem, curiosity, etc.)")
    parser.add_argument("--body", "-b", type=str, default="auto",
                        help="Body structure for generation")
    parser.add_argument("--cta", type=str, default="hard",
                        help="CTA style (soft, hard, proof)")
    parser.add_argument("--niche", "-n", type=str, default="content automation",
                        help="Content niche for generation")
    parser.add_argument("--provider", type=str, default="deepseek",
                        help="AI provider (deepseek, openai, anthropic)")
    parser.add_argument("--voice", type=str,
                        help="Voice ID override for HeyGen")
    parser.add_argument("--title", type=str, default="",
                        help="Title override for videos")
    parser.add_argument("--status", "-s", action="store_true",
                        help="Show pipeline state and exit")
    parser.add_argument("--retry", "-r", type=str, nargs="?", const="failed",
                        help="Retry failed scripts (optional: specify script ID)")
    parser.add_argument("--reset", type=str,
                        help="Reset script state by ID (to reprocess)")
    parser.add_argument("--setup", action="store_true",
                        help="Create folders and check dependencies, then exit")

    args = parser.parse_args()

    # Ensure folders exist
    ensure_folders()
    state = PipelineState()

    # ─── Setup Only Mode ─────────────────────────────────────────
    if args.setup:
        check_brolls()
        print("\n✓ Setup complete. Ready to run.")
        print(f"  Run: python factory3.py swipe_files/your_scripts.json")
        return

    # ─── Status Only Mode ────────────────────────────────────────
    if args.status:
        show_status(state)
        return

    # ─── Retry Mode ─────────────────────────────────────────────
    if args.retry:
        if args.script_file:
            retry_failed(state, args.script_file)
        else:
            print("  Please provide the script file to retry from.")
            print("  Usage: python factory3.py scripts.json --retry")
        return

    # ─── Reset Mode ─────────────────────────────────────────────
    if args.reset:
        state.reset_script(args.reset)
        print(f"  ✓ Reset state for script ID {args.reset}")
        return

    # ─── Generate Scripts ────────────────────────────────────────
    generated_file = None
    if args.generate > 0:
        generated = generate_scripts(
            count=args.generate,
            hook=args.hook,
            body=args.body,
            cta=args.cta,
            niche=args.niche,
            provider=args.provider,
        )
        if generated:
            generated_file = generated
            # If no script_file specified, use the generated one
            if not args.script_file:
                args.script_file = generated
        else:
            print("\n❌ Script generation failed.")
            sys.exit(1)

    # ─── Process Scripts ─────────────────────────────────────────
    if not args.script_file:
        print("\nNo script file provided. Use:")
        print("  python factory3.py swipe_files/scripts.json         — process existing")
        print("  python factory3.py --generate 5                     — generate + process")
        print("  python factory3.py --status                         — check state")
        print("  python factory3.py --setup                          — setup only")
        sys.exit(1)

    script_file = Path(args.script_file)
    if not script_file.exists():
        print(f"❌ Script file not found: {script_file}")
        sys.exit(1)

    # Load and process the queue
    try:
        with open(script_file, "r") as f:
            scripts = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {script_file}: {e}")
        sys.exit(1)

    if not isinstance(scripts, list) or len(scripts) == 0:
        print("❌ Script file must contain a non-empty array.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  ContentReel Pipeline — {len(scripts)} scripts in queue")
    if generated_file:
        print(f"  (generated fresh — {args.generate} scripts)")
    print(f"{'='*60}")

    check_brolls()

    # Process each script
    success_count = 0
    fail_count = 0

    for i, script_entry in enumerate(scripts):
        script_id = script_entry.get("id", f"idx_{i}")
        status = state.get_status(script_id)

        if status == "completed":
            # Check if output actually exists
            final = state.data.get(str(script_id), {}).get("final_output")
            if final and Path(final).exists():
                print(f"\n  [{i+1}/{len(scripts)}] Script ID {script_id} — already completed ✓")
                success_count += 1
                continue

        print(f"\n  [{i+1}/{len(scripts)}] Processing script ID {script_id}...")
        ok = process_single_script(script_file, script_entry, state,
                                   voice_id=args.voice, title=args.title or None)

        if ok:
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"  Pipeline Complete")
    print(f"{'='*60}")
    if success_count > 0:
        print(f"  ✅ {success_count} scripts completed successfully")
    if fail_count > 0:
        print(f"  ❌ {fail_count} scripts failed")
    print(f"  📍 Check output/ folder for finished videos")
    print(f"  📍 Run 'python factory3.py --status' to see detailed state")
    if fail_count > 0:
        print(f"  📍 Run 'python factory3.py {args.script_file} --retry' to retry failures")
    print()


if __name__ == "__main__":
    main()
