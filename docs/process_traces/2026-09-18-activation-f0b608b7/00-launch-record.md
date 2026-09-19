# Launch record — headless activation f0b608b7-c555-4377-83e2-938401b0e66b (2026-09-18 19:50:55 PDT)

Watchdog attempt 49, pid 33808, model Fable 5.1 (`--model fable --effort high`), binary 2.1.277. Previous activation d8ca3a36 ended its loop cleanly at 19:41:07 after arming the night; the watchdog recorded `clean activation exit` → IDLE → BACKOFF_USAGE (state.json `last_exit_class` still read `usage_exhausted`, the stale-label class of WATCHDOG-STALE-EXIT-CLASS-01) → LAUNCHING at 19:50:55 once the backoff expired. Its armed-plan fence (`PLAN_LEAD_S`, t0 − 8 min = 23:52:00 PDT) had not started, so a launch during the armed span before REQUEST is by design.

## Durable sources read (in order)

1. heartbeat written 19:51:06 (`{"pid":33808,"activation_id":"f0b608b7-…","ts":1789786274}`); no `standdown.request`, no `STOP`.
2. `state.json`: ACTIVE, `notice_pending: []`, `remote_stop CLEAR`, fenced checkouts = the canonical root and the triple (`d079-epoch-25g83-derivation-n1-20260919`, `/Users/edr/JouleWise-measurement-20260919-derivation`, `d595aa9f`).
3. `RUN_STATE.md` top block on origin/main `6ec5b460` (read from the linked worktree `JouleWise-wt-mag-d8ca3a36`; the canonical checkout sits at `422cdebb` and is not touched), arm record 21, `AGENTS.md`, the d8ca3a36 checkpoint memory.
4. Notice thread `1a0b78109400cce8`: two magistrate messages, no reply. `gh issue list --label directive --author mpmdw --state open` → `[]`.
5. Measurement clone HEAD `d595aa9f`, clean; `com.joulewise.night` (09-19 00:00) and `com.joulewise.night.deadman` (03:35) loaded, both pointing at the clone and the plan at `~/night-custody/d079-epoch-25g83-derivation-n1-20260919/night_plan.json`.

## Launch email

Gmail accepted `1a0b7952048a0d39` at 19:54 PDT to `claude.ai.copper531@passmail.net` cc `claude2.glaring610@passmail.net` (why launched; no pending notices; the night stays armed; desk work only; exit before 23:52). `notice.ack` written with this activation id after acceptance.

## Boundary

REQUEST 23:52:00 PDT (1789800720), TERM 23:54, KILL 23:55, t0 00:00:00 09-19. This activation ends its loop and exits before 23:40 PDT; the t0 census needs the magistrate, its supervisor and every Codex child gone. No `[QUIET-MAC]` work; no git operation in the canonical root; the measurement clone is never moved.

## Slice plan (bounded desk work, all agent-compatible)

1. Re-harvest the retained 09-16 plan root whose 09-16 harvest archive directory was empty (finding in arm record 21) — DONE 19:56, evidence in `01-harvest-0916-evidence/`.
2. TEST-LARGE-FRAME-ARGV-PORTABILITY-01: test-only fix per record 19 F4 on branch `fix/2026-09-18-large-frame-argv-portability` (worktree `JouleWise-wt-argv-f0b608b7`), refuter, PR under the twelve-row ledger; hosted CI on the PR is the only Linux execution of the counterfactual.
3. Registration seat: kernel rows for TEST-LARGE-FRAME-ARGV-PORTABILITY-01, NIGHT-GATE-CROSS-SEAM-TESTS-01, the lane 232 stage-B confirmation lane, plus status notes (A232 amendment per record 14 §7, courier.sent format, 09-16 harvest finding closed).
