#!/usr/bin/env python3
"""Verify the in-progress problem's tests actually pass before marking it solved."""
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


def run_tests(folder: Path, stack: str):
    cmd = ["npm", "test", "--silent"] if stack == "node" else ["pytest", "-q"]
    result = subprocess.run(cmd, cwd=folder, capture_output=True, text=True)
    return result.returncode == 0, (result.stdout + result.stderr)


def main():
    meta_path, data = find_in_progress()
    if meta_path is None:
        print("No problem is currently in_progress. Run /next-problem first.")
        sys.exit(1)

    folder = meta_path.parent
    passed, output = run_tests(folder, data.get("stack", "python"))
    print(output)

    if not passed:
        print(f"\n\u2717 Tests still failing in {folder.name}. Keep going.")
        sys.exit(1)

    started = datetime.fromisoformat(data["started_at"])
    now = datetime.now(timezone.utc)
    data["status"] = "solved"
    data["solved_at"] = now.isoformat()
    data["time_spent_min"] = round((now - started).total_seconds() / 60, 1)
    meta_path.write_text(json.dumps(data, indent=2))

    journal = ROOT.parent / "journal" / f"{data['slug']}.md"
    print(
        f"\n\u2713 Solved! {folder.name} \u2014 {data['time_spent_min']} min. "
        f"Category: {data['category']}, difficulty: {data['difficulty']}."
    )
    if not journal.exists():
        print("Run /retro while it's fresh to capture what you learned.")


if __name__ == "__main__":
    main()
