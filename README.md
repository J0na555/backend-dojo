# backend-dojo

A personal backend-debugging practice environment for opencode.

## Setup

1. `cd backend-dojo && git init && git add . && git commit -m "scaffold"`
2. Run `/init` in opencode to generate the base `AGENTS.md`, then append
   the contents of `AGENTS.md.append` into it (delete `AGENTS.md.append`
   once merged).
3. Create the orphan solutions branch:
   ```
   git checkout --orphan solutions
   git rm -rf .
   git commit --allow-empty -m "init solutions branch"
   git checkout main
   ```
4. Verify the command directory name matches your opencode version
   (`.opencode/command/` vs `.opencode/commands/` — check
   `opencode.ai/docs/commands` and rename if needed).
5. Requires `python3` on PATH. Node problems require `npm`.

## Daily loop

- Switch to the `dojo-gen` agent (Tab) when you want to top up the queue
  with new problems — keep 3-5 sitting at `status: "queued"`.
- `/next-problem` to pull one, then solve it entirely in your own
  IDE/terminal — no agent involvement.
- `/complete` to actually re-run the tests and mark it solved.
- `/reveal` only if you're genuinely stuck — checks out the reference fix
  from `solutions` and logs it as a give-up, not a solve.
- `python3 scripts/stats.py` anytime to see solve/give-up rate by category.
