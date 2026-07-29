#!/usr/bin/env python3
"""Give up on the in-progress problem: check out the reference solution and log it."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"


def find_in_progress():
    for meta_path in sorted(ROOT.glob("*/meta.json")):
        data = json.loads(meta_path.read_text())
        if data.get("status") == "in_progress":
            return meta_path, data
    return None, None


def main():
    meta_path, data = find_in_progress()
    if meta_path is None:
        print("No problem is currently in_progress.")
        sys.exit(1)

    folder = meta_path.parent
    confirm = input(f"Reveal solution for {folder.name}? This logs as a give-up. [y/N] ")
    if confirm.strip().lower() != "y":
        print("Cancelled.")
        return

    subprocess.run(
        ["git", "checkout", "solutions", "--", str(folder.relative_to(ROOT.parent))],
        check=True,
    )

    data["status"] = "gave_up"
    data["gave_up"] = True
    data["solved_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(data, indent=2))
    print(f"Reference solution for {folder.name} checked out. Logged as gave_up.")


if __name__ == "__main__":
    main()
