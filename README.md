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
- `/complete` to actually re-run the tests and mark it solved.
- `/reveal` only if you're genuinely stuck — checks out the reference fix from
  `solutions` and logs it as a give-up, not a solve.
- `python3 scripts/stats.py` anytime to see solve/give-up rate by category.

## Future plans

- adding multiple bugs in one problem
- adding a problem generation suggestion topics
- status optimizatin type shit
