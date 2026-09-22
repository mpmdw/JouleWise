# Activation ce7c57a9 — record 01: launch; third relaunch of the delta re-audit, this time detached

Activation `ce7c57a9-6ace-4a83-bb3d-9a99951db762` (attempt 70) launched 23:01:04 PDT
2026-09-21 by the watchdog after activation ca029491 exited at 22:52:35 PDT
(`last_exit_class: usage_exhausted`, transition 291 "clean activation exit").
Heartbeat written 23:01:19; launch email `1a0c7b5ac88bcec5` accepted by Gmail;
`notice.ack` written. Pending notices at launch: none. Directives: none open.
Canonical checkout clean at `ecefd46a` = `origin/main`; no `com.joulewise.night*`
label loaded, no such plist on disk. NOTHING ARMED.

## §1 What the ca029491 exit killed (second time, same signature)

ca029491 relaunched the two delta re-audit seats and the replay at 22:53 (its
record 01 §3). All three were children of the magistrate's shell and died with
the activation at 22:52:35 (clock: the seats were still writing their `.log`
at 22:52; `.status` files read `RUNNING`; `.stdout` and the report `.md` are
absent; the replay log is 0 bytes). Seat delta-2 was mid-way through its Q4
mutation script (`/tmp/retention2-mutations-bd671744.py`) when killed. No
`codex-run-v3` process survived; this time the scope locks were released
(only the 09-18 lock `87a3c185…` remains, untouched).

This is the SECOND consecutive loss of the same three jobs to the same cause
(activation exit on usage exhaustion). Rule 11's standing escalation trigger
applies to *fix rounds failing with the same signature*; this is not a fix
round and the structural cause is known and mechanical (job lifetime bound to
the activation's shell), so the cure is a launch-shape change, not a consult:

## §2 Relaunch, detached (executed 23:08 PDT)

Each job runs in its own process group via a double-fork + `setsid` wrapper
(`/tmp/magistrate-ce7c57a9/detach.py`, stdin `/dev/null`, output to
`<name>.detach.log`, exit code to `<name>.rc`), so a magistrate exit no longer
ends it. Verified after launch: pids 31139 / 31144 / 31158, each with a distinct
`pgid` and a wrapper parent that has exited. `scripts/fixture_orphan_census.py`
reports and never signals, so the successor's launch census will not kill them.

- Seat delta-2: `codex-run-v3 /tmp/magistrate-ce7c57a9/seats/delta-reaudit-2-sol.md --timeout 5400 -C /Users/edr/code/JouleWise-wt-retention2-29ea94df -s workspace-write --effort xhigh --genre review --write-scope '[]' <brief>` — brief byte-identical to ca029491's (`seats/brief-delta-2.md`), worktree detached at `bd671744`, clean.
- Seat delta-3: same shape, `-C …wt-retention3-29ea94df --effort high`, brief byte-identical to ca029491's corrected brief (`seats/brief-delta-3.md`), worktree detached at `af85b38a`, clean.
- Replay: `scripts/shard_tests.py --workers 4` then `scripts/quick_suite.py --tier touched --since 9e0a4995` in `wt-retention-29ea94df` at `af85b38a` (clean), logs `/tmp/magistrate-ce7c57a9/10-full-replay-af85b38a.log` and `11-quick-tier-af85b38a.log`, each terminated by an `rc=` line.

Codex 5 h window at launch: 0 sessions (quota clear).

## §3 Next exact action (successor, if this activation exits first)

The jobs keep running. Read `/tmp/magistrate-ce7c57a9/*.rc` (present = finished),
the two seat reports `seats/delta-reaudit-{2,3}-sol.md`, and the two replay logs.
Then: triage → record 02 (seat outcomes, replay verbatim tails, same-signature
statement, terminal review of `af85b38a`) → merge this bookkeeping branch into
`fix/2026-09-21-retained-root-terminal-markers` as the merge candidate → PR with
the twelve-row ledger (`/tmp/magistrate-29ea94df/pr-body.md`, row 12 = final
head) → `gh pr checks` gate ledger → merge on green local replay + quick tier
(D-072) → watch post-merge. Arm sequence only after Ed's interactive Claude
sessions (pids 67916 / 68088 at launch) are closed.
