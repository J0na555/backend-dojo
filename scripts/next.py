#!/usr/bin/env python3
"""Pick the next queued problem, mark it in_progress, print title only."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"


def load_all():
    metas = []
    for meta_path in sorted(ROOT.glob("*/meta.json")):
        metas.append((meta_path, json.loads(meta_path.read_text())))
    return metas


def main():
    metas = load_all()

    in_progress = [d.get("slug") for _, d in metas if d.get("status") == "in_progress"]
    if in_progress:
        print(f"Already in progress: {in_progress[0]}. Run /complete or /reveal first.")
        sys.exit(1)

    queued = [(p, d) for p, d in metas if d.get("status") == "queued"]
    if not queued:
        print("No queued problems left. Generate more with the dojo-gen agent.")
        sys.exit(1)

    meta_path, data = queued[0]
    data["status"] = "in_progress"
    data["started_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(data, indent=2))

    folder = meta_path.parent
    readme = (folder / "README.md").read_text().strip()
    print(f"Folder: {folder}")
    print()
    print(readme)


if __name__ == "__main__":
    main()
