# Block 6 loop wake: what to do when the loop wakes you

You were started by the block-6 collection loop (`com.joulewise.b6loop`) through `scripts/b6_wake.zsh`. The loop
woke you because something needs a decision it cannot make itself. The path of the wake record is given after this
brief. You are the orchestrator for this wake (Opus 5.5), with the doctrine in `CLAUDE.local.md` and
`~/.claude/CLAUDE.md`.

## The one rule that matters most here

While you are alive, the loop cannot start a measurement: its pre-session check waits while any `claude` or `codex`
process exists. Do what the wake needs, record it, and exit. Do not stay idle, do not poll, and do not start long
background work on this Mac. If the work is long (a code fix, a review), put it on a branch and exit; the loop waits.

## First, read (in this order)

1. The wake record (path below): `reason` and `ctx` (session id, packs, cause).
2. `<loop_root>/state.json`: the loop's state, `hold_reason`, `last_exception`, per-pack status and hold reasons,
   `wait` (a physics wait), `pending_sessions`.
3. The last lines of `<loop_root>/attempts.jsonl` (structure only: no energies are in it).
4. `/opt/homebrew/bin/python3.13 -B <measurement checkout>/scripts/b6_loop.py status --loop-root <loop_root>`.

The measurement checkout is the loop's repository root (named in the launchd plist `com.joulewise.b6loop`). Never
edit, pull or fetch in it: its only commits are the ledger pin advances the desk makes.

## Blinding

Block 5 is blinded until its release, and block 6's energies are blinded until block 6 closes. Never open, list or
run anything over `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`, `/Users/edr/night-g2a/`,
`/Users/edr/night-archive/harvest-v5-b5-*` or block-5 runs roots. A block-6 session's archive may be read for
structure (flags, counts, stage exit codes), never for energies or per-run numbers.

## What each reason asks of you

| Reason | What to do |
|---|---|
| `physics_wait_2h` (mail only) | A physical hazard (clock, battery, thermal, contention, sampler, disk) has kept the loop waiting 2 h. Find the cause from `state.json` `wait` and the pre-check's `precheck-*.json`. Fix it if it is fixable without sudo (disk: move or offload earlier archives to iCloud, never delete evidence); otherwise email Ed what you measured. |
| `certain_exclusion` | The pre-check found a condition that would remove the session before it starts (for example the model files differ from the pinned ones). Fix the cause, then `b6_loop.py resume --pack <pack>`. |
| `smoke_hold` | A pack's smoke failed on something that is not physics. Read `<staging>/<session>-smoke-*/smoke-result.json`. Fix the code on a branch, review it per doctrine, and leave the pack held until the fix is pinned. The same failure on two packs holds the whole loop. |
| `structure_defect` | A session's collection was structurally broken (design 13.1: fix before the next pack arms). Read the session line's `structure_defects`. Fix, then `resume`. |
| `harvest_fault` | The session harvest failed as a program. The raw bytes are kept. Fix the harvest, then `b6_loop.py reharvested <session_id>`. |
| `overrun` | A collection ran past its deadline plus an hour with no terminal record. Never kill it. Find out why from its custody records; email Ed if a process must be stopped. |
| `lane_missing:*` | A lane adapter is missing on the pinned commit. That is a build defect: fix on the integration branch. |
| `exception:*` | The loop itself raised. `state.json` `last_exception` names it. Fix, then `resume`. |
| `pack_paused`, `close`, `pack_not_open` | A pack reached its attempt limit, the campaign closed, or a registration is missing or invalid. Decide per the registration (§5); `close` means start the release work. |

## Before you exit

- Record what you found and did in one line of the session record (RUN_STATE, per doctrine) and, if state changed,
  email Ed once (only on a change of state, a question he must answer, or a fault).
- Run `b6_loop.py resume` only when the cause is fixed or the hold was wrong. A hold you leave in place is fine.
- Exit. The loop's next tick sees that no agent is alive and goes on.
