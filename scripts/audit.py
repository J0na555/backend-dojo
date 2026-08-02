#!/usr/bin/env python3
"""Validate the dojo repo: meta schema, category rotation, contracts, solutions sync."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"

REQUIRED = {
    "id", "slug", "stack", "category", "difficulty", "status",
    "started_at", "solved_at", "time_spent_min", "gave_up",
}
VALID = {
    "status": {"queued", "in_progress", "solved", "gave_up"},
    "stack": {"fastapi", "django", "node"},
    "category": {"logic-data", "concurrency", "system-infra", "smell"},
    "difficulty": {"easy", "medium", "hard"},
}


def check_solutions_branch(folder):
    if not Path(folder).is_relative_to(ROOT.parent):
        return True
    relative = folder.relative_to(ROOT.parent)
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "solutions", "--", str(relative)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  {folder.name}: could not inspect solutions branch")
        return False
    listed = [line for line in result.stdout.splitlines()
              if "/src/" in line and line.endswith((".py", ".js", ".ts"))]
    if not listed:
        print(f"  {folder.name}: reference missing on solutions branch")
        return False
    return True


def main():
    ok = True
    problems = []
    metas = []
    problems_root = sorted(ROOT.glob("*/"))
    for folder in problems_root:
        meta_path = folder / "meta.json"
        print(f"[{folder.name}]")
        if not meta_path.exists():
            print("  missing meta.json")
            ok = False
            continue

        try:
            data = json.loads(meta_path.read_text())
        except json.JSONDecodeError as e:
            print(f"  meta.json is invalid JSON ({e})")
            ok = False
            continue

        for field in sorted(REQUIRED):
            if field not in data:
                print(f"  missing meta field {field!r}")
                ok = False
        for field, allowed in VALID.items():
            value = data.get(field)
            if value not in allowed:
                print(f"  bad {field} {value!r} (allowed: {sorted(allowed)})")
                ok = False

        expected_prefix = str(data.get("id", "")).zfill(3) + "-"
        if data.get("id") and not folder.name.startswith(expected_prefix):
            print(f"  folder name does not start with its id ({expected_prefix!r})")
            ok = False

        status = data.get("status")
        if status == "solved" and not data.get("solved_at"):
            print("  solved but solved_at is missing")
            ok = False
        if status == "queued" and data.get("started_at"):
            print("  queued but started_at is set")
            ok = False

        for part in ("src", "tests", "README.md"):
            if not (folder / part).exists():
                print(f"  missing {part}")
                ok = False

        if not (folder / "hints.json").exists():
            print("  missing hints.json (recommended, not required)")

        if status in ("solved", "gave_up"):
            if not check_solutions_branch(folder):
                ok = False

        problems.append((folder, data))

    if problems:
        metas_only = [d for _, d in problems]
        print()
        print("Overall")
        print(f"  count: {len(problems)}")
        print("  stacks:", dict(Counter(d.get("stack") for d in metas_only)))
        print("  categories:", dict(Counter(d.get("category") for d in metas_only)))
        print("  difficulties:", dict(Counter(d.get("difficulty") for d in metas_only)))
        print("  smells:", sum(1 for d in metas_only if d.get("category") == "smell"))
        python = sum(1 for d in metas_only if d.get("stack") in ("fastapi", "django"))
        total = len(metas_only)
        ratio = python / total if total else 0
        print(f"  python share: {ratio:.0%} (target ~70%)")
        if total and ratio < 0.6:
            print("  WARNING: python under-represented; prefer a python stack next")
            ok = False

        categories = [d.get("category") for d in metas_only if d.get("category")]
        for prev, cur in zip(categories, categories[1:]):
            if prev == cur:
                print(f"  rotation break: {prev!r} repeated consecutively")
                ok = False

    print()
    subprocess.run(["python3", str(Path(__file__).with_name("lint_problems.py"))])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()