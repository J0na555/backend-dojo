---
name: problem-generation
description: Rules for generating a new backend debugging problem into problems/. Use whenever creating a new dojo problem.
---

# Problem generation rules

## Stack ratio

Target roughly 70% Python / 30% Node-TS across all problems, and within
Python roughly split FastAPI vs Django. Before generating, check the
`stack` field across existing `problems/*/meta.json` and pick whichever
stack is currently underrepresented relative to the ratio.

## Category rotation

Pick from these three buckets, weighted toward whichever has fewest
existing problems, and never repeat the previous problem's category:

- **logic-data**: off-by-one/boundary errors, incorrect Django ORM usage
  (`.filter()` vs `.get()` misuse, missing `select_related`/
  `prefetch_related` causing N+1), wrong Pydantic validation, bad SQL
  joins or a broken migration, incorrect serialization.
- **concurrency**: race conditions from shared mutable state across async
  FastAPI handlers, missing `await`, Node event-loop blocking calls,
  deadlocks on DB transactions, non-atomic read-modify-write sequences.
- **system-infra**: Django settings precedence bugs, broken middleware
  ordering, misconfigured CORS/JWT expiry/auth dependency injection, env
  var load-order bugs, cache invalidation bugs, wrong HTTP status/error
  handling.

Occasionally (roughly 1 in 6) generate a "smell" problem instead of a hard
bug: a flaky test from non-deterministic ordering, a timezone bug, etc.
Tag these with category `smell`.

## What makes a good problem

- Enough surface area that the bug isn't obvious from file size alone —
  scaffold a small realistic app (a handful of files: routes/views,
  models, a service layer), not a single 15-line snippet.
- Exactly one injected bug. Resist the urge to make it "interesting" by
  adding a second one.
- The bug must be reachable and provable by a test suite — write tests
  that fail because of the bug and pass once it's correctly fixed. Tests
  should not merely check the bug is "gone" in some superficial way; they
  should exercise the actual behavior the bug breaks.
- No comments, naming, or commit messages that hint at the fix. The bug
  should look like an honest mistake a competent developer made, not a
  puzzle with a wink in it.

## Folder + file contract

Create `problems/<NNN>-<kebab-case-title>/` where `NNN` is the next
zero-padded id, containing:

- `README.md` — one to two sentences max. State only the observable
  symptom (e.g. "Checkout occasionally double-charges under load.") —
  never the mechanism, location, or category.
- `meta.json`:
  ```json
  {
    "id": "NNN",
    "slug": "NNN-kebab-case-title",
    "stack": "fastapi | django | node",
    "category": "logic-data | concurrency | system-infra | smell",
    "difficulty": "easy | medium | hard",
    "status": "queued",
    "started_at": null,
    "solved_at": null,
    "time_spent_min": null,
    "gave_up": false
  }
  ```
- `src/` — the app code, with the bug injected.
- `tests/` — a runnable test suite (`pytest` for Python, `npm test` for
  Node) that fails on the current `src/` and passes once fixed.

## Solutions branch

After the problem folder is committed to `main` with the bug in place,
switch to the orphan `solutions` branch, write the **pre-bug** (working)
version of the same files at the same paths, commit, and switch back to
`main`. Never leave `main` on the `solutions` branch. Never merge
`solutions` into `main`.
