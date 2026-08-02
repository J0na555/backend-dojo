## Purpose

This repo is a personal backend-debugging practice environment ("the dojo").
Every problem in `problems/<slug>/` is a small, realistic app with exactly one
deliberately injected bug. The point is to build real debugging instinct, not to
be helped through it.

## Hard rules for every agent working in this repo

- Never explain what the injected bug is, where it is, or why the tests fail, in
  any `README.md`, commit message, code comment, or chat response — unless the
  problem has `status: "solved"` or `status: "gave_up"` in its `meta.json`.
- The only sanctioned place to hint at the bug is `problems/<slug>/hints.json`,
  authored by dojo-gen at generation time (three escalating levels, never naming
  the exact fix). It stays forbidden everywhere else.
- Run `python3 scripts/audit.py` before generating a new problem; it must exit 0.
- Never touch the `solutions` branch except through `scripts/reveal.py`.
- Never mark a problem `solved` based on the user's claim — only
  `scripts/complete.py` re-running the real test suite may do that.
- `dojo-gen` is the only agent allowed to write into `problems/`. `dojo-runner`
  may only execute the three scripts in `scripts/` and must never open, read, or
  reason about files in `problems/*/src/`.

## Stack ratio for generated problems

Roughly 70% Python (split between FastAPI-style async/dependency-injection bugs
and Django-style ORM/middleware/migration bugs) and 30% Node/TypeScript (Express
or Nest). Balance over time using the `stack` field already present across
`problems/*/meta.json` — don't just default to whichever is easiest to generate.

## Category rotation

Never repeat the same `category` two problems in a row. Categories in use:
`logic-data`, `concurrency`, `system-infra`. See the `problem-generation` skill
for the full breakdown and generation rules.
