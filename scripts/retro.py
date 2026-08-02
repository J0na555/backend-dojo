#!/usr/bin/env python3
"""Write a retro journal entry for the most recent solved / gave_up problem."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"
JOURNAL = Path(__file__).resolve().parent.parent / "journal"

SOLVED_Q = [
    "What symptom did you start from?",
    "How did you narrow it down? (logs, tests, reading models, ...)",
    "What was the root cause, in your own words?",
    "Which technique helped the most?",
    "One thing to do differently next time:",
]
GAVE_UP_Q = [
    "Where did you get stuck?",
    "What did the reveal teach you?",
    "One thing to do differently next time:",
]


def latest_done():
    best = None
    for meta_path in sorted(ROOT.glob("*/meta.json")):
        d = json.loads(meta_path.read_text())
        if d.get("status") not in ("solved", "gave_up"):
            continue
        key = d.get("solved_at") or ""
        if best is None or key > best[0]:
            best = (key, meta_path, d)
    return best


def main():
    record = latest_done()
    if record is None:
        print("Nothing solved or given up yet. Solve a problem first.")
        return

    _, meta_path, data = record
    slug = data["slug"] if data.get("slug") else meta_path.parent.name
    journal_path = JOURNAL / f"{slug}.md"

    if journal_path.exists():
        answer = input(f"{slug} already has a journal entry. Overwrite? [y/N] ").strip().lower()
        if answer != "y":
            print("Cancelled.")
            return

    questions = SOLVED_Q if data.get("status") == "solved" else GAVE_UP_Q

    lines = [
        f"# {slug}",
        "",
        f"id: {data.get('id')} | stack: {data.get('stack')} | category: "
        f"{data.get('category')} | difficulty: {data.get('difficulty')}",
        f"status: {data.get('status')}",
        f"date: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for q in questions:
        lines.append(f"## {q}")
        lines.append(input(q + " "))
        lines.append("")

    JOURNAL.mkdir(parents=True, exist_ok=True)
    journal_path.write_text("\n".join(lines))

    data["retro"] = True
    meta_path.write_text(json.dumps(data, indent=2))

    print(f"\nJournal written: {journal_path}")


if __name__ == "__main__":
    main()