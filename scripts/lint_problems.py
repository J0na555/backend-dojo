#!/usr/bin/env python3
"""Reject dojo problems that leak the injected bug or spoil the exercise."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "problems"
SRC_HINTS = re.compile(r"\bBUG\b|\bTODO\b|\bFIXME\b")
# Mechanism words that must never appear in a README.
README_LEAKS = [
    "string comparison",
    "lexicographic",
    "x-forwarded-for",
    "client-supplied",
    "not atomic",
    "non-atomic",
    "balance check",
    "race window",
    "localecompare",
    "lost update",
    "trusts client",
]


def main():
    ok = True
    for p in sorted(ROOT.glob("*/")):
        for f in p.rglob("*"):
            if f.suffix not in (".py", ".js", ".ts"):
                continue
            if "node_modules" in f.parts or any(part.startswith(".") for part in f.parts):
                continue
            for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                if SRC_HINTS.search(line):
                    ok = False
                    print(f"{f.relative_to(ROOT)}:{i}: {line.strip()}")

        readme = p / "README.md"
        if readme.exists():
            text = readme.read_text().lower()
            for kw in README_LEAKS:
                if kw in text:
                    ok = False
                    print(f"{p.name}: README leaks mechanism ({kw!r})")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
