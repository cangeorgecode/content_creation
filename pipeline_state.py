#!/usr/bin/env python3
"""
Pipeline State Manager — tracks progress so the factory can resume
after failures without wasting HeyGen API credits.

Each script in the queue gets a state record:
  "completed"  — all 3 steps done, script safe to remove
  "heygen_done"  — avatar video downloaded (DO NOT re-generate = save credits)
  "broll_done"   — b-rolls added
  "failed"       — something went wrong
  "new"          — not started yet

State file: .pipeline_state.json (auto-created in project root)
"""

import json
import os
from pathlib import Path
from datetime import datetime


class PipelineState:
    """Manages per-script pipeline state for resume/skip."""

    def __init__(self, state_path=".pipeline_state.json"):
        self.state_path = Path(state_path)
        self.data = self._load()

    def _load(self):
        if self.state_path.exists():
            try:
                with open(self.state_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                return {}
        return {}

    def _save(self):
        with open(self.state_path, "w") as f:
            json.dump(self.data, f, indent=2, sort_keys=True)

    def get_status(self, script_id):
        """Get status of a script by its ID."""
        entry = self.data.get(str(script_id), {})
        return entry.get("status", "new")

    def get_step_output(self, script_id, step):
        """Get the output file path from a previous step."""
        entry = self.data.get(str(script_id), {})
        return entry.get(f"{step}_output")

    def set_heygen_done(self, script_id, video_path, video_id=None):
        """Mark HeyGen step as complete, save output path."""
        key = str(script_id)
        if key not in self.data:
            self.data[key] = {}
        self.data[key].update({
            "status": "heygen_done",
            "heygen_output": str(video_path),
            "heygen_video_id": video_id or "",
            "updated_at": datetime.now().isoformat(),
        })
        self._save()

    def set_broll_done(self, script_id, output_path):
        """Mark b-roll step as complete."""
        key = str(script_id)
        if key not in self.data:
            self.data[key] = {}
        self.data[key].update({
            "status": "broll_done",
            "broll_output": str(output_path),
            "updated_at": datetime.now().isoformat(),
        })
        self._save()

    def set_captions_done(self, script_id, output_path):
        """Mark captions step as complete."""
        key = str(script_id)
        if key not in self.data:
            self.data[key] = {}
        self.data[key].update({
            "status": "completed",
            "captions_output": str(output_path),
            "final_output": str(output_path),
            "completed_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        })
        self._save()

    def set_failed(self, script_id, step, error=""):
        """Mark a script as failed at a specific step."""
        key = str(script_id)
        if key not in self.data:
            self.data[key] = {}
        self.data[key].update({
            "status": "failed",
            "failed_at": step,
            "error": error,
            "updated_at": datetime.now().isoformat(),
        })
        self._save()

    def reset_script(self, script_id):
        """Reset a script to 'new' status (e.g., after fixing an issue)."""
        key = str(script_id)
        if key in self.data:
            del self.data[key]
            self._save()

    def remove_script(self, script_id):
        """Remove a script's state (when the script is popped from queue)."""
        key = str(script_id)
        if key in self.data:
            del self.data[key]
            self._save()

    def get_summary(self):
        """Get a summary of all tracked scripts."""
        counts = {"new": 0, "heygen_done": 0, "broll_done": 0, "completed": 0, "failed": 0}
        for key, entry in self.data.items():
            status = entry.get("status", "new")
            counts[status] = counts.get(status, 0) + 1
        return counts

    def get_failed(self):
        """Get all failed scripts."""
        return {k: v for k, v in self.data.items() if v.get("status") == "failed"}

    def needs_heygen(self, script_id):
        """Returns True if the HeyGen step still needs to run."""
        status = self.get_status(script_id)
        return status in ("new", "failed")

    def needs_broll(self, script_id):
        """Returns True if the b-roll step still needs to run."""
        status = self.get_status(script_id)
        return status in ("new", "failed", "heygen_done")

    def needs_captions(self, script_id):
        """Returns True if the captions step still needs to run."""
        status = self.get_status(script_id)
        return status in ("new", "failed", "heygen_done", "broll_done")

    @staticmethod
    def file_exists(path_str):
        """Check if a file exists on disk (belt-and-suspenders check)."""
        if not path_str:
            return False
        return Path(path_str).exists()
