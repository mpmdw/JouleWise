# 00 — Launch record, headless activation `83d93f5a` (2026-09-16 02:44:17 PDT)

Activation `83d93f5a-a79e-42c9-b7e8-b3a5ffcb576a`, watchdog attempt 36, claude
pid 8275 (supervisor 8271), spawned 02:44:17 PDT by `com.joulewise.magistrate`
after activation `736e2aed` exited cleanly at ~02:38 on the interactive
session's GO (events.jsonl sequence 148 "clean activation exit"; `state.json`
again labels the last exit `usage_exhausted`, the stale-field defect A197).
The watchdog held in `BACKOFF_USAGE` until 02:44 ("all launch predicates
clear"); fixture-orphan census 0 rows.

Heartbeat written 02:44:27 (shell pid 8350 first, corrected to `{"pid":8275,…}`
at 02:44:38). Pending notices queued by the watchdog: none. No
`standdown.request`, no `STOP`, remote stop `CLEAR`. Open owner-authored
`directive` issue: #349 (notice transport fallback; "tonight: re-plan the stub
to the earliest whole-minute t0 the margins allow, send the notice by issue,
arm"). NOTHING ARMED at launch; launchctl = magistrate only. No git operation
in the canonical root (read-only `status`/`log`/`ls-remote`; the handback
worktree `JouleWise-wt-hb-83d93f5a` was added from it).

## Launch email: SENT (the connector probe passed)

Gmail `send_message` accepted the launch email at 02:46 PDT (message
`1a0a99b8a07eee6d`); the claude.ai Gmail connector Ed repaired at ~02:36 works
in this process. `notice.ack` written with this activation id. The interactive
session `joulewise-95` (Ed's restart, Fable, `uds:/tmp/cc-socks/7066.sock`)
messaged at launch: no detached seats from it until the stub is published;
#349 is on the repo. Replied at 02:47: Gmail works, re-planning by email.

## Work done

1. Re-plan of the lapsed stub as `rehearsal-20260916c` (record 01): handback
   commit H `be221f6a` pushed to main 02:49; clone, ledger, stage, preflight
   02:49:16–02:49:44 all rc 0; notice by EMAIL accepted 02:50:06; ARMED
   02:50:45 (publication 1789552244.97, install rc 0, both agents loaded).
2. Lane NOTICE-TRANSPORT-FALLBACK-01 registered in the state kernel from
   directive #349 (record 02); #349 commented and closed.
3. Durable pointer and this record pushed to main; arm-confirmation email on
   the notice thread; exit before the REQUEST boundary 03:17:00 PDT.
