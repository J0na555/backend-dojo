#!/usr/bin/env python3
"""Reveal the next escalating hint for the in-progress problem."""
import json
import sys
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
        print("No problem is currently in_progress. Run /next-problem first.")
        sys.exit(1)

    folder = meta_path.parent
    hints_path = folder / "hints.json"
    if not hints_path.exists():
        print(f"No hints written for {folder.name}.")
        print("Open the code and reason from the tests.")
        return

    hints = json.loads(hints_path.read_text()).get("hints", [])
    used = data.get("hints_used", 0)

    if used >= len(hints):
        print("That was the last hint. Still stuck? Run /reveal to log a give-up.")
        return

    print(f"Hint {used + 1}/{len(hints)}:")
    print(hints[used])

    data["hints_used"] = used + 1
    meta_path.write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()