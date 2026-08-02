#!/usr/bin/env python3
"""Suggest the shape of the next problem to generate, from current gaps."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"
TOPICS = Path(__file__).resolve().parent / "topics.json"

TARGET_PYTHON = 0.7
TARGET_SMELL = 1 / 6


def main():
    metas = []
    for meta_path in sorted(ROOT.glob("*/meta.json")):
        metas.append(json.loads(meta_path.read_text()))
    topics = json.loads(TOPICS.read_text())

    if not metas:
        print("Pick a new problem from the pool below — nothing exists yet.")
        for t in topics:
            print(f"  {t['stack']:<7} {t['category']:<12} {t['difficulty']:<6} {t['topic']}")
        return

    total = len(metas)
    by_stack = Counter(d.get("stack") for d in metas)
    by_cat = Counter(d.get("category") for d in metas)
    python = sum(n for s, n in by_stack.items() if s in ("fastapi", "django"))
    smell_count = sum(1 for d in metas if d.get("category") == "smell")

    last_cat = metas[-1].get("category")
    last_stack = metas[-1].get("stack")

    # Pick the least-used stack, broken ties by the 70/30 target.
    python_deficit = TARGET_PYTHON * total - python
    node_total = by_stack.get("node", 0)
    candidates_stack = []
    if python_deficit > 0 or node_total / max(total, 1) > 0.3:
        candidates_stack = ["fastapi", "django"]
    else:
        candidates_stack = ["node"]
    stack = min(candidates_stack, key=lambda s: by_stack.get(s, 0))

    # Pick the least-used category, but never repeat the last one.
    candidates_cat = [c for c in ("logic-data", "concurrency", "system-infra", "smell")
                      if c != last_cat]
    if len(metas) >= 5 and by_cat.get("smell", 0) < TARGET_SMELL * total:
        candidates_cat.insert(0, "smell")
    category = min(candidates_cat, key=lambda c: by_cat.get(c, 0))

    pool = [t for t in topics
            if (t["stack"] == stack or t["stack"] == "any")
            and t["category"] == category]
    if not pool:
        pool = [t for t in topics if t["category"] == category]
    if not pool:
        print(f"No topic for {stack}/{category}; check scripts/topics.json.")
        sys.exit(0)

    difficulty = {}
    pools = [t for t in pool if (t["stack"] == stack or t["stack"] == "any")]
    pick = pools[0]

    print("Suggested next problem")
    print(f"  stack: {pick['stack']}")
    print(f"  category: {pick['category']}")
    print(f"  difficulty: {pick['difficulty']}")
    print(f"  topic: {pick['topic']}")
    print()
    print(f"Rationale: stack {pick['stack']} is least-used (current balance "
          f"{dict(by_stack)}), category {pick['category']} has the fewest "
          f"problems, and it isn't a repeat of {last_cat}.")
    print("Give this to the dojo-gen agent (Tab).")


if __name__ == "__main__":
    main()