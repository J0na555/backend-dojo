#!/usr/bin/env python3
"""Print solve rate, give-up rate, and average time by category."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"

by_cat = defaultdict(lambda: {"solved": 0, "gave_up": 0, "minutes": []})

for meta_path in sorted(ROOT.glob("*/meta.json")):
    d = json.loads(meta_path.read_text())
    if d.get("status") not in ("solved", "gave_up"):
        continue
    cat = d.get("category", "uncategorized")
    if d["status"] == "solved":
        by_cat[cat]["solved"] += 1
        if d.get("time_spent_min"):
            by_cat[cat]["minutes"].append(d["time_spent_min"])
    else:
        by_cat[cat]["gave_up"] += 1

print(f"{'Category':<14} {'Solved':<8} {'Gave up':<9} {'Avg min':<8}")
for cat, s in sorted(by_cat.items()):
    avg = round(sum(s["minutes"]) / len(s["minutes"]), 1) if s["minutes"] else "-"
    print(f"{cat:<14} {s['solved']:<8} {s['gave_up']:<9} {avg}")

if not by_cat:
    print("No completed problems yet.")
