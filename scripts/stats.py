#!/usr/bin/env python3
"""Print solve rate, give-up rate, avg time, hint use, and retro rate by category."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"
JOURNAL = Path(__file__).resolve().parent.parent / "journal"

by_cat = defaultdict(lambda: {
    "solved": 0, "gave_up": 0, "minutes": [], "hints": [], "retro": 0,
})

for meta_path in sorted(ROOT.glob("*/meta.json")):
    d = json.loads(meta_path.read_text())
    if d.get("status") not in ("solved", "gave_up"):
        continue
    cat = d.get("category", "uncategorized")
    by_cat[cat]["hints"].append(d.get("hints_used", 0))
    if d.get("status") == "solved":
        by_cat[cat]["solved"] += 1
        if d.get("time_spent_min"):
            by_cat[cat]["minutes"].append(d["time_spent_min"])
    else:
        by_cat[cat]["gave_up"] += 1
    if d.get("retro") or (JOURNAL / f"{d['slug']}.md").exists():
        by_cat[cat]["retro"] += 1

print(f"{'Category':<14} {'Solved':<8} {'Gave up':<9} {'Avg min':<9} {'Avg hints':<10} {'Retro':<6}")
for cat, s in sorted(by_cat.items()):
    avg = round(sum(s["minutes"]) / len(s["minutes"]), 1) if s["minutes"] else "-"
    avg_hints = round(sum(s["hints"]) / len(s["hints"]), 1) if s["hints"] else "-"
    done = sum(s[c] for c in ("solved", "gave_up"))
    print(f"{cat:<14} {s['solved']:<8} {s['gave_up']:<9} {avg:<9} {avg_hints:<10} "
          f"{s['retro']}/{done}")

if not by_cat:
    print("No completed problems yet.")