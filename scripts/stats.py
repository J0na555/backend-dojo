#!/usr/bin/env python3
"""Dojo dashboard: solves, streaks, weekly rhythm, and a full problem ledger."""
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"
JOURNAL = Path(__file__).resolve().parent.parent / "journal"


def parse_iso(iso):
    if not iso:
        return None
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def load():
    problems = []
    for meta_path in sorted(ROOT.glob("*/meta.json")):
        d = json.loads(meta_path.read_text())
        d["_folder"] = meta_path.parent.name
        d["_retro"] = d.get("retro") or (JOURNAL / f"{d['slug']}.md").exists()
        d["_solved"] = parse_iso(d.get("solved_at"))
        d["_started"] = parse_iso(d.get("started_at"))
        problems.append(d)
    return problems


def streak(day_set, today):
    cur, day = 0, today
    while day in day_set:
        cur += 1
        day -= timedelta(days=1)
    return cur


def longest(day_set):
    best = run = prev = None
    for d in sorted(day_set):
        if prev is not None and (d - prev).days == 1:
            run += 1
        else:
            run = 1
        best = max(best or 0, run)
        prev = d
    return best or 0


def main():
    problems = load()
    done = [d for d in problems if d.get("status") in ("solved", "gave_up")]
    solved = [d for d in done if d.get("status") == "solved"]
    gave_up = [d for d in done if d.get("status") == "gave_up"]
    queued = sum(1 for d in problems if d.get("status") == "queued")
    in_progress = sum(1 for d in problems if d.get("status") == "in_progress")

    total = len(problems)
    print("=============== dojo dashboard ===============")
    print(f"problems {total:<4} solved {len(solved):<4} gave-up {len(gave_up):<4} "
          f"queued {queued:<4} in-progress {in_progress}")
    if total:
        print(f"solve rate {len(solved)/total:.0%}   avg time "
              f"{round(sum(d.get('time_spent_min') or 0 for d in solved)/len(solved), 1) if solved else '-'} min   "
              f"retro {sum(1 for d in solved if d['_retro'])}/{len(solved)}   "
              f"avg hints {round(sum(d.get('hints_used', 0) for d in done)/len(done), 1) if done else '-'}")

    print("\n-- by category --")
    by_cat = defaultdict(lambda: {"solved": 0, "gave": 0, "mins": []})
    for d in done:
        c = d.get("category", "?")
        if d.get("status") == "solved":
            by_cat[c]["solved"] += 1
            if d.get("time_spent_min"):
                by_cat[c]["mins"].append(d["time_spent_min"])
        else:
            by_cat[c]["gave"] += 1
    print(f"{'category':<13} {'solved':<7} {'gave':<5} {'avg min':<9}")
    for c, s in sorted(by_cat.items()):
        avg = round(sum(s["mins"]) / len(s["mins"]), 1) if s["mins"] else "-"
        print(f"{c:<13} {s['solved']:<7} {s['gave']:<5} {avg}")

    print("\n-- by difficulty --")
    by_diff = defaultdict(lambda: {"solved": 0, "mins": []})
    for d in solved:
        by_diff[d.get("difficulty", "?")]["solved"] += 1
        if d.get("time_spent_min"):
            by_diff[d.get("difficulty", "?")]["mins"].append(d["time_spent_min"])
    print(f"{'difficulty':<11} {'solved':<8} {'avg min':<9}")
    for c, s in sorted(by_diff.items()):
        avg = round(sum(s["mins"]) / len(s["mins"]), 1) if s["mins"] else "-"
        print(f"{c:<11} {s['solved']:<8} {avg}")

    solve_days = {d["_solved"].date() for d in solved if d.get("_solved")}
    today = datetime.now(timezone.utc).date()
    print("\n------------- streak -------------")
    if not solve_days:
        print("no solves yet")
    else:
        print(f"current streak {streak(solve_days, today)} day(s)")
        print(f"longest streak {longest(solve_days)} day(s)")
        last = max(solve_days)
        print(f"last solve {last} ({(today - last).days} day(s) ago)")

    if solve_days:
        print("\n---------- weekly rhythm ----------")
        wd_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        wd = [0] * 7
        weeks = Counter()
        for d in solved:
            s = d["_solved"]
            wd[s.weekday()] += 1
            weeks[(s.isocalendar().year, s.isocalendar().week)] += 1
        for name, count in zip(wd_names, wd):
            print(f"{name} {'█' * count} {count}")

        print("\n-- solves per week (last 8) --")
        for (year, week), count in sorted(weeks.items())[-8:]:
            print(f"{year}-W{week:<2} {'█' * count} {count}")

    print("\n------------ ledger -------------")
    print(f"{'id':<4} {'slug':<24} {'stack':<8} {'category':<13} {'diff':<7} "
          f"{'status':<11} {'min':<7} {'hints':<6} {'retro':<5} solved")
    for d in problems:
        solved_at = d["_solved"].strftime("%Y-%m-%d") if d.get("_solved") else "-"
        print(f"{d.get('id', '?'):<4} {d['_folder']:<24} {str(d.get('stack')):<8} "
              f"{str(d.get('category')):<13} {str(d.get('difficulty')):<7} "
              f"{d.get('status'):<11} {str(d.get('time_spent_min') or '-'):<7} "
              f"{str(d.get('hints_used', 0)):<6} {str(d['_retro']):<5} {solved_at}")


if __name__ == "__main__":
    main()