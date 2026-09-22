# 01 — Launch and resume record: activation 59857fe5 (headless, 10:02:46 PDT 2026-09-22, watchdog attempt 79, transition 329)

Authored by the magistrate. Everything below is executed evidence from this activation unless marked otherwise.

## Why launched

Watchdog relaunch after a backoff ladder. Pending notices (all reported in the launch email, Gmail `1a0ca13e91a26449`, sent 10:04 after the heartbeat; `notice.ack` written after acceptance):

| notice | PDT | activation | class |
|---|---|---|---|
| transition-318-launch_failure | 08:01:00 | e4b4ead6 | exit 1, generic_error |
| transition-321-usage_backoff | 08:07:24 | e373ce02 | exit 1, usage_exhausted (~10 s after spawn) |
| transition-324-usage_backoff | 08:27:29 | 41a83e27 | exit 1, usage_exhausted (~10 s after spawn) |
| transition-327-usage_backoff | 09:02:39 | 24491823 | exit 1, usage_exhausted (~10 s after spawn) |

The Claude usage window was exhausted from about 08:07 to at least 09:03. No night was affected.

## Launch checks

1. Heartbeat written first (pid 26621 = the `claude -p` session, matches `state.json.resident_session.pid`).
2. `standdown.request` and `STOP` absent at launch and at every slice boundary so far. Open directive issues: none.
3. `launchctl list`: only `com.joulewise.magistrate`; no `com.joulewise.night*` label, no such plist on disk. NOTHING ARMED.
4. Canonical `/Users/edr/code/JouleWise`: clean, `ecbc0fac` = `origin/main` at launch.

## Inherited state (from `bookkeeping/2026-09-22-activation-e4b4ead6` @ c8812172 and the worktrees)

- e4b4ead6 pushed fix-round-1 brief 06 at 07:56:52 and exited 08:01 (generic_error). No fix-round seat output exists in `~/.claude/jobs/e4b4ead6/tmp/` (last file 07:54); the feature worktree was clean → **fix round 1 was never executed**.
- Feature worktree `JouleWise-wt-a267-d9990b3c` (`feat/2026-09-22-a267-clock-anchor-v3_1`) was at `c5f4f9c6`, six commits ahead of origin (`447fd6bf`): A269 Parts A–D + two follow-ups by the Opus seat (883 insertions over `pilot_protocol_v2.json`, `night_gate.py`, `quiet_predicate_campaign.py`, `scripts/run_night.py`, two test modules). Clean tree → complete commits, unpushed.
- Scratch branch `scratch/r7-dryrun-e4b4ead6` at `ab836fe1` (dry-run steps 1–4a: r7 candidate bytes as a pure pin delta, live pins moved, live-generation test pins moved), local only.
- Untracked copies of already-sealed rulings remain in the detached judge worktrees (`coldgate-d9990b3c` ruling 14, `coldgate-e4b4ead6` ruling 10, both committed elsewhere: `6c2bb976`, `39d5e4b5`); left in place.

## Preservation acts (executed, in order)

1. 10:05 — pushed `feat/2026-09-22-a267-clock-anchor-v3_1` 447fd6bf..c5f4f9c6 and `scratch/r7-dryrun-e4b4ead6` (new remote branch).
2. 10:05 — `ecbc0fac..c8812172` verified fast-forward (`merge-base --is-ancestor`) and docs-only (27 files: `docs/**`, `RUN_STATE.md`, `TASK_QUEUE.md`; no code); pushed `c8812172:main`.
3. 10:06 — guard re-run (0 night labels, 0 night plists, canonical clean) → `git -C /Users/edr/code/JouleWise pull --ff-only` → canonical at `c8812172`. Docs-only move; resident supervisor not made stale (same reasoning as e4b4ead6's move).
4. Bookkeeping worktree `JouleWise-wt-mag-59857fe5`, branch `bookkeeping/2026-09-22-activation-59857fe5` from c8812172.
5. Baseline of the brief-06 exit-contract modules started on `c5f4f9c6` (seven modules; `test_night_agent_install` spawns a Python subprocess per test and dominates wall time).

## Slice plan (bounded; stand-down file polled before each)

1. Fix round 1 (brief 06) — Opus seat, feature worktree, no push; then magistrate diff review + mutation spot checks.
2. Delta re-audit of the fix round (Fable contract lens + Opus execution lens, read-only on a detached review worktree).
3. r7 re-issue by hand on the final bytes (deriver `uncertainty_evidence.py` frozen at 447fd6bf → its bytes are already final; the scratch dry run is the template) + neutrality proof; cold gate #3 on the single D-138 merge transaction.
4. PR with the twelve-row ledger → merge under the gates → NIGHT_HANDBACK for the next pilot night under registration v2. A268 waits on Ed.

Codex quota 17% → no Codex seats this activation (Ed's sparing rule); Fable/Opus seats only.
