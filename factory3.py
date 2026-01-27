# factory3.py
# ONE COMMAND → FULL VIRAL REEL (with ID-based script queue management)
# Usage: python factory3.py path/to/scripts.json [--title "Title"] [--voice id]

import sys
import subprocess
import json
import os
from pathlib import Path

def run_cmd(cmd):
    print(f"\nRunning → {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR:")
        print(result.stderr)
        sys.exit(1)
    print(result.stdout)
    return result.stdout

def get_output_path(stdout):
    for line in stdout.splitlines():
        if line.startswith("OUTPUT_PATH="):
            return line.split("=", 1)[1].strip()
    return None

def remove_script_by_id(script_file: Path, script_id: int):
    """Remove the script with the given ID from the JSON file."""
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("Warning: JSON is not a list. Cannot remove script by ID.")
            return

        original_count = len(data)
        data = [item for item in data if item.get("id") != script_id]

        if len(data) == original_count:
            print(f"Warning: No script with ID {script_id} found. It may have already been removed.")
        else:
            print(f"\nSuccessfully REMOVED script ID {script_id} from queue.")
            print(f"Remaining scripts: {len(data)}")

        # Save updated queue
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Queue updated: {script_file}")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {script_file}. Could not remove script. ({e})")
    except Exception as e:
        print(f"Error updating script file: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python factory3.py path/to/scripts.json [--title \"Title\"] [--voice id]")
        sys.exit(1)

    script_file = Path(sys.argv[1])
    if not script_file.exists():
        print(f"Script file not found: {script_file}")
        sys.exit(1)

    print("FULLY AUTOMATED REEL FACTORY STARTED")
    print("=" * 60)
    print(f"Script queue: {script_file}")

    # Load and preview the next script
    current_id = None
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            scripts = json.load(f)

        if not isinstance(scripts, list) or len(scripts) == 0:
            print("No scripts left in the queue!")
            sys.exit(0)

        next_script = scripts[0]
        current_id = next_script.get("id")
        script_text = next_script.get("script", "").strip()

        if not script_text:
            print("Warning: First script has empty content.")
            sys.exit(1)

        first_line = script_text.splitlines()[0]
        preview = first_line[:80] + ("..." if len(first_line) > 80 else "")
        id_display = f"ID {current_id}" if current_id is not None else "ID ?? (no id field)"
        print(f"Next script → {id_display} | \"{preview}\"")

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {script_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Could not read script queue: {e}")
        sys.exit(1)

    # Build HeyGen command
    heygen_cmd = ["python", "heygen6.py", "--json", str(script_file)]
    use_mock = False

    # Forward --title and --voice args
    extra_args = sys.argv[2:]
    i = 0
    while i < len(extra_args):
        arg = extra_args[i]
        if arg == "--mock":
            use_mock = True
        elif arg in ["--title", "--voice"]:
            heygen_cmd.append(arg)
            if i + 1 < len(extra_args) and not extra_args[i + 1].startswith("--"):
                heygen_cmd.append(extra_args[i + 1])
                i += 1
        elif arg.startswith("--title=") or arg.startswith("--voice="):
            heygen_cmd.append(arg)
        elif arg == "--image-key":
            print("Note: --image-key is no longer used. Ignoring.")
            if i + 1 < len(extra_args) and not extra_args[i + 1].startswith("--"):
                i += 1
        i += 1

    # Step 1: HeyGen
    print("\n1. Generating avatar video with HeyGen...")
    if use_mock:
        print(" [MOCK MODE] Skipping HeyGen API. Using media/mock_avatar.mp4")
        heygen_path = "media/mock_avatar.mp4"
        if not os.path.exists(heygen_path):
            print("Mock video not found! Please run 'python create_mock_video.py' first.")
            sys.exit(1)
    else:
        stdout = run_cmd(heygen_cmd)
        heygen_path = get_output_path(stdout)
        
    if not heygen_path:
        print("Failed to get HeyGen output path")
        sys.exit(1)

    # Step 2: B-rolls
    print("\n2. Adding pro b-rolls...")
    stdout = run_cmd(["python", "broll2.py"])
    broll_path = get_output_path(stdout)
    if not broll_path:
        print("Failed to get b-roll output path")
        sys.exit(1)

    # Step 3: Captions
    print("\n3. Adding captions with PyCaps...")
    run_cmd([
        "python", "pycaps2.py",
        "--input", broll_path,
        "--template", "templates/centered"
    ])

    # Only remove the script after full success
    if current_id is not None:
        remove_script_by_id(script_file, current_id)
    else:
        print("\nNo 'id' field found in script — skipping removal (consider adding IDs for safety)")

    print("\n" + "=" * 60)
    print("ALL DONE! Your viral reel is ready")
    print(f"Final video → {Path(broll_path).stem}_captioned.mp4")
    print("Location → output/ folder")
    print("Go post it and dominate")
    print("=" * 60)

if __name__ == "__main__":
    main()