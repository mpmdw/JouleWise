# 115 — Ed authorizes the GitHub-issue directive channel (2026-09-10 ~03:05 PDT)

Interactive magistrate (session `01MrRehZWopqKNDv5Uy466AC`), bench in the linked worktree `JouleWise-wt-directives` cut from
origin/main `b501f08c`.

## Ed's words (verbatim, this session, 2026-09-10 ~03:00 PDT)

> Re your recommendation - im ok with it

The recommendation (this session, ~21:10 PDT 09-09): the magistrate reads open GitHub issues labelled `directive` before every work
slice, acts on those authored by the repository owner, replies on the issue and closes it; the `ops/stop-magistrate` branch stays the
emergency stop; observation is RUN_STATE.md and the durable pointer on GitHub plus the magistrate's own emails. Ed's stated goal:
"the point of this is to have you run the whole pipeline of experiments, but still be reachable/steerable in the easiest way possible."

## Why this shape

The relaunch prompt's tool allowlist has Gmail send only (scripts/magistrate_watchdog.py, `--allowedTools`), so the resident session
cannot read replies; adding Gmail read would add a prompt-injection surface and need a sender filter. `gh` already works under its Bash
tool. An issue is written from GitHub mobile, needs no process on the measurement machine, and lands in the repository record.

## Change

- `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`: line 24 (the template stays within the test's 25-line bound; line 19 unmoved).
- `docs/process/MAGISTRATE_WATCHDOG.md`: new section "Directive channel" between the kill switch and exit classification.
- `tests/test_magistrate_watchdog.py`: three prompt assertions and one document test (counterfactual: any author's issue read as
  an instruction).
- GitHub label `directive` created on `mpmdw/JouleWise` (03:06 PDT).

Takes effect at the next headless relaunch; activation 7ce7af2a (launched 20:52 PDT 09-09 with the previous prompt) is unaffected.

## Machine state at write

03:03 PDT: activation 7ce7af2a ACTIVE (pid 18817), waiting on its own monitor (deadline 06:05 PDT) for the two interactive `claude`
sessions (pids 16371, 17047) to close before running runbook 67; nothing armed; no plan directory; AC power, AC profile sleep 0.
