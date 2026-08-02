#!/usr/bin/env python3
"""Pick the next queued problem (sequentially), or a specific one by name."""
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


def resolve(metas, arg):
    """Return (folder, meta), or (None, reason) with reason in
    {'not_found', 'ambiguous'}."""
    needle = arg.strip().lower()
    exact = []
    fuzzy = []
    for meta_path, data in metas:
        name = meta_path.parent.name
        if needle == name.lower() or needle == data.get("slug", "").lower():
            exact.append((meta_path, data))
        elif len(needle) >= 2 and (needle in name.lower() or needle in name.lower().split("-", 1)[-1]):
            fuzzy.append((meta_path, data))

    candidates = exact or fuzzy
    if not candidates:
        return None, "not_found"
    if len(candidates) > 1:
        return None, "ambiguous"
    return candidates[0], "ok"


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    metas = load_all()

    in_progress = [d.get("slug") for _, d in metas if d.get("status") == "in_progress"]
    if in_progress:
        print(f"Already in progress: {in_progress[0]}. Run /complete or /reveal first.")
        sys.exit(1)

    if not arg:
        queued = [(p, d) for p, d in metas if d.get("status") == "queued"]
        if not queued:
            print("No queued problems left. Generate more with the dojo-gen agent.")
            sys.exit(1)
        meta_path, data = queued[0]
        header = f"Folder: {meta_path.parent}"
        suffix = ""
    else:
        match, reason = resolve(metas, arg)
        if match is None:
            if reason == "ambiguous":
                print(f"Ambiguous match for {arg!r}; be more specific.")
            else:
                queued_slugs = ", ".join(d.get("slug") for _, d in metas if d.get("status") == "queued")
                print(f"No problem matched {arg!r}. Queued: {queued_slugs or '(none, generate more)'}")
            sys.exit(1)

        meta_path, data = match
        status = data.get("status")
        if status != "queued":
            print(f"{meta_path.parent.name} is {status}, not queued. "
                  "Run /retro to review it; it can't be started again.")
            sys.exit(1)

        seq_first = next((d for _, d in metas if d.get("status") == "queued"), None)
        header = f"Folder: {meta_path.parent} (picked)"
        suffix = ""
        if seq_first is not None and seq_first is not data:
            suffix = (f"\n(Sequential pick would have been {seq_first.get('slug')} "
                      f"({seq_first.get('category')}/{seq_first.get('difficulty')}).)")

    data["status"] = "in_progress"
    data["started_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(data, indent=2))

    readme = (meta_path.parent / "README.md").read_text().strip()
    print(header)
    print()
    print(readme)
    if suffix:
        print()
        print(suffix.strip())


if __name__ == "__main__":
    main()