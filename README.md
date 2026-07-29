# backend-dojo

A personal backend-debugging practice environment for opencode.

My goal with this project is to up my backend debugging game — one injected
bug at a time. Every problem is a small, realistic app with exactly one flaw
to find. No fluff, no toy scenarios. The more I grind through these, the
faster I spot the real thing in production.

This is about building genuine instinct, not just getting green tests. I
work every problem in my own editor with no agent help, and only reach for
the reference fix when I'm properly stuck.

## Daily loop

- Switch to the `dojo-gen` agent (Tab) when you want to top up the queue
  with new problems — keep 3-5 sitting at `status: "queued"`.
- `/next-problem` to pull one, then solve it entirely in your own
  IDE/terminal — no agent involvement.
- `/complete` to actually re-run the tests and mark it solved.
- `/reveal` only if you're genuinely stuck — checks out the reference fix
  from `solutions` and logs it as a give-up, not a solve.
- `python3 scripts/stats.py` anytime to see solve/give-up rate by category.
