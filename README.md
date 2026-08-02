# backend-dojo

A personal backend-debugging practice environment for opencode.

My goal with this project is to up my backend debugging game. Every problem is a
small, realistic app with exactly one flaw to find.

its all abt learning by fixing bugs,

## Daily loop

- Switch to the `dojo-gen` agent (Tab) when you want to top up the queue with
  new problems — keep 3-5 sitting at `status: "queued"`.
- `/next-problem` to pull one, then solve it entirely in your own IDE/terminal —
  no agent involvement.
- `/hint` (up to 3) when you're stuck but don't want to give up yet.
- `/complete` to actually re-run the tests and mark it solved.
- `/retro` after any solve or give-up to log what you learned to `journal/`.
- `/reveal` only if you're genuinely stuck — checks out the reference fix from
  `solutions` and logs it as a give-up, not a solve.
- `/suggest-topic` before generating to get the next gap-filled problem shape.
- `python3 scripts/audit.py` anytime to validate the whole repo.
- `python3 scripts/stats.py` anytime to see solve/give-up rate by category.

## Future plans

- multi-bug problems as an explicit opt-in tier (`"bugs": 2`)
- run concurrency suites N times in `/complete` before marking solved
- solution tags revealed only after solved, so stats show what you practiced
