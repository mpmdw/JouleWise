# Magistrate terminal review — WATCHDOG-CENSUS-01 + RESUME-DAEMON-01 series (interactive magistrate, 2026-09-08 ~02:40 PDT)

Merge candidate: branch `feat/2026-09-08-watchdog-census-daemon`, head named in the PR ledger row 12. Series on top
of main d8ad6c15: 898e5305 landing (Astra high) → b3eeee9a fix round 1 (Astra medium, Opus C1-C4/C7) → 7a18fddc
prune (Astra medium, delta re-audit R1 blocker) → 298da021 disposition B (Astra high, cold gate packet 2) →
2da5c62a Opus final-head F1 (bench, doc only) → the trace/terminal-review commit.

## Gauntlet record (rule 9)

| Layer | Seat | Report | Unique catches |
|---|---|---|---|
| Implementation | Astra high | 06 | — |
| Execution refuter | Astra medium | 12 | none (all eight live process shapes classify correctly; mutations caught) |
| Contract refuter | Opus | 13 | C1 reused-token relabel, C2 corrupt lock unrecoverable, C3 gesture not command, C4 WHO missing, C7 stale ordering; landing note's "four failures" understated (16 methods / 28 outcomes) |
| Fix round 1 | Astra medium | 14 | — |
| Delta re-audit 1 | Astra medium | 17 | BLOCKER R1: inventory-based corrupt-lock recovery unlinks under an unrecorded live headless resident |
| Prune | Astra medium | 19 | — |
| Cold gate (rule 11, second round on C2) | cold Fable + packet 16 | 16/10 | neither P nor F2; disposition B; the TICK ITSELF unlinks a corrupt lock on main (finding 2) |
| Disposition B | Astra high | 21 | — |
| Delta re-audit 2 | Astra medium | 24 | clean; residual: PID+lstart identity is seconds-resolution |
| Opus final-head counter-review | Opus | 23 | F1 escape-hatch predicate erased by the first tick (should-fix, cured at 2da5c62a); F2-F4 nits |
| Fresh eyes on the post-review doc edit | Opus | 25 | see file |

Same-signature statement: round 1 cured doc/label gaps; the delta blocker was a NEW defect introduced by the C2
cure, not a repeat, and it escalated to a consult (cold gate) rather than a round 3. No class survived two rounds.

## Apex code-reading gate (rule 1 / ledger row 7) — design-level questions, read from `git diff d8ad6c15 <head> -- scripts/`

1. **Is the night-time safety census untouched?** Yes: `production_census`, `agent_census`, `make_probes` have no
   hunk; `handoff_census` is reachable only from `reap_handoff` and the documented step-4 block (Opus 23 Q2 and my
   own read of the diff). The zero-agent fence of D-127 is byte-identical.
2. **Can any tick unlink `magistrate.lock` while a possible owner is alive?** No. The corrupt-lock branch of
   `decide` calls `corrupt_lock_refusal(state, snapshot)` first and returns `HOLD_UNSAFE` on: no valid
   `resident_session` record; the recorded (pid, start_time) pair present (defunct rows count as present); any
   `resumed_twin`; any daemon / bg-spare / bg-pty-host. The valid-lock dead-owner branch now also refuses on a
   live resumed twin. The drain-adoption path returns early on a corrupt current lock so the durable record is not
   erased ahead of the corrupt-lock branch (the guard Opus 23 mutation-tested: 33 failures + 3 errors when removed).
3. **Does the reaper receipt still require absence of every recorded pair?** Yes: `reap_handoff` keeps
   `expected`, snapshots before every signal (per-signal outcome labels), re-checks after TERM and KILL, and its
   verdict is `pass` only when no survivors, `handoff_census` empty, and no refusals; refusals include
   `handoff_daemon_not_retired` and `handoff_unowned_resumed_twin`, computed on the initial and the final snapshot.
4. **Classifier honesty.** `handoff_process_role` recognises `daemon run`, `bg-spare`, `bg-pty-host`, and a
   resumed twin only as an INTERACTIVE claude carrying both `--resume` and `--reply-on-resume`; a headless `-p`
   resident is never a twin (the live 84232 / 83086 shapes classify as none). A hand-launched `claude --resume`
   without `--reply-on-resume` is not a twin and stays an inventory candidate for explicit adoption — conservative,
   and the doc says so.
5. **Overbuild / prune (row 8).** Declined as optional for this merge, registered as follow-ups: Opus 23 F2
   (corrupt-lock refusal event appended every tick, ~288 rows/day while stalled; notice dedupe keyed on `reason`
   while ack keys on `id`), F3 (installer re-implements the daemon classifier inline; should call
   `magistrate_watchdog.py handoff-daemons`), F4 (step-4 block reads lock bytes before an existence check), C5/C6
   nits, and delta-2 residual (PID + seconds-resolution `lstart` identity; XNU's unique process id would be a
   stronger binding). None affects the fail-closed direction of any refusal.

## Live verification (lead-owned; rule 1)

- Scoped modules (`tests.test_magistrate_watchdog`, `_cli`, `test_install_magistrate_watchdog`) run unpiped at
  the bench on 898e5305 (90 OK), b3eeee9a (OK), 7a18fddc (95 OK), 298da021 (OK), 2da5c62a (OK); rc captured
  from the process, never a grep pipeline.
- T0-ACID-CLOCK-01 (separate branch, merged e4ce8b3b): the real acid test reproduced the RAW-span refusal on main
  and passed on the branch at the bench.
- NOT yet exercised live: the daemon retirement (`claude daemon stop --any`) and the twin stop; those run as the
  last act before this session stands down and are reported in the durable state, not assumed here.
- Full-suite replay on this head: ledger row 9 names the log and tail.

## Verdict

LAND after CI is green on the final head and the replay tail is recorded. The series makes the next handoff
receipt able to pass on a shared machine, retires the resume machinery explicitly, and closes a corrupt-lock
double-launch path that existed on main before this session.
