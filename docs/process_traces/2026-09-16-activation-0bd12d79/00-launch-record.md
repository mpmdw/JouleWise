# 00 — Launch record, headless activation `0bd12d79` (2026-09-16 03:49:31 PDT)

Activation `0bd12d79-673d-4b10-852c-f90d999a11fc`, watchdog attempt 39, claude
pid 12557 (supervisor 12553), spawned 03:49:31 PDT by `com.joulewise.magistrate`
after activation `100ac5da` exited cleanly at 03:16:23 (events.jsonl sequence
160 "clean activation exit") ahead of the stub's t0−6 TERM. The watchdog then
held `IDLE → HOLD_CENSUS` from 03:19:23 (sequence 161, "production census
non-empty inside plan span": Ed's interactive session 7066 with its codex MCP
pair 7086/7094) through the plan span and relaunched at 03:49:31 ("all launch
predicates clear", sequence 162); fixture-orphan census 0 rows. `state.json`
again labelled the last exit `usage_exhausted` (stale field, see record 01 F2).

Heartbeat written 03:49:44 (first act; shell pid 12611, corrected to the lock
pid 12557 at 04:04). Pending notice queued by the watchdog and relayed in the
launch email: `transition-161-hold_census`. No `standdown.request`, no `STOP`,
remote stop `CLEAR`. Open owner-authored `directive` issues: none (checked
03:50 and 03:55). `launchctl list` at launch: `com.joulewise.night` (last
exit 3), `com.joulewise.night.deadman`, `com.joulewise.magistrate`. No git
operation in the canonical root (read-only `log`, `status`, `worktree list`;
the canonical checkout is stale at `11ea57db`, origin/main was `92e3a4e7`);
this record was written from the linked worktree `JouleWise-wt-hb-0bd12d79`
(branch `bookkeeping/2026-09-16-activation-0bd12d79` from `origin/main`
`92e3a4e7`, added from `JouleWise-wt-register`).

## Launch email: SENT

Gmail `send_message` accepted the launch email on the night notice thread
`1a0a99fa2717d749` at 03:5x PDT (message `1a0a9d89e054a0bc`): why launched,
the pending hold_census notice, the stub's outcome as read from disk, and the
resume plan (harvest → uninstall → retire → register findings → equivalence
night). `notice.ack` written with this activation id; the watchdog logged
`notice_acknowledged ["transition-161-hold_census"]` at 1789555963 (03:52:43).
The interactive session `joulewise-95` (pid 7066, `uds:/tmp/cc-socks/7066.sock`)
was told the stub is complete and nothing is armed; it replied with three lane
candidates from an article Ed sent at 03:48 (record 01) and, asked for its exit
estimate, answered "exits by 05:00 PDT; plan t0 no earlier than 05:15", with
the caveat that Ed is awake and talking to it.

## Work

1. Record 01: `rehearsal-20260916c` harvested (acceptance MET on all three
   clauses), both night agents uninstalled from the clone (rc 0), plan root
   and the lapsed `rehearsal-20260916` staging retired to `~/night-archive`
   with checksums, stub clones retained (delete refused by the classifier),
   the unused `3c8bd220` derivation clone moved out of the inventoried path.
2. Kernel: WATCHDOG-STALE-EXIT-CLASS-01 and NIGHT-HANDBACK-GLOSS-01 carry the
   two peer findings as evidence; PHASE-PARTITION-INVARIANT-01 registered at
   rank 218.
3. Record 02 (in progress at this write): the equivalence night
   `d079-epoch-25g83-derivation-n1-20260916`, t0 2026-09-16 05:40:00 PDT
   (1789562400), under NIGHT_HANDBACK email-then-arm; the notice is held until
   the interactive session's exit message (its t0 census has no interactive
   exemption for this class).
