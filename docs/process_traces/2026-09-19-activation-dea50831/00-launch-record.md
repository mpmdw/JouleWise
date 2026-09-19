# Activation dea50831 — launch and close-out (2026-09-19 03:47–≈04:49 PDT), pre-t0 bookkeeping only, held to the fence

Launched 2026-09-19 03:47:13 PDT (watchdog attempt 62, backoff expiry after 62527c24's clean exit at ≈03:47; `state.json` again labels that deliberate exit `usage_exhausted`, the known mislabel). Heartbeat written 03:47:21 (resident pid 27741); launch email `1a0b948eae6638bd` sent to `claude.ai.copper531@passmail.net` (cc `claude2.glaring610@passmail.net`) at 03:49; `notice.ack` written 03:49:27. Pending notices: none. Open directive issues: none. No `standdown.request`, no `STOP`. No NO on the notice thread `1a0b9295e7b733be`.

## State verified at launch (read-only)

- Night `d079-epoch-25g83-derivation-n2-20260919` ARMED and untouched: t0 05:00:00 PDT 09-19 (`t0_epoch_s` 1789819200), window 9000 s, courier 07:35, dead-man 08:35. Launch was 73 minutes before t0.
- Measurement root `/Users/edr/JouleWise-measurement-20260919-derivation-n2`: `.git/HEAD` = `22b92ec7` (frozen triple head), read by file, no git command run there.
- Plan directory `~/night-custody/d079-epoch-25g83-derivation-n2-20260919/` complete and unchanged since 03:15 (calibration_plan.json, chain.zsh + both sha256 files, identity-epoch.json, night_plan.json, night_probe_receipt.json, t1-bindings.json, empty `night/`).
- `launchctl list`: `com.joulewise.night`, `com.joulewise.night.deadman`, `com.joulewise.magistrate` loaded, status 0.
- `origin/main` = `293bfb32` (62527c24's record); bookkeeping worktree `wt-mag-e82f29ac` at the same head. Canonical root untouched at `422cdebb`.
- The three `usage_exhausted` events in `events.jsonl` all date from 09-09; no live quota problem.

## What this activation did and did not do

Bookkeeping only, per the 4ca26e9c durable pointer: this record, a RUN_STATE block, one push. No Codex seat, no child, no lane work, no git operation in the canonical root or the clone.

One deliberate difference from 3422a575 and 62527c24: instead of exiting immediately, this activation held alive (bounded waits, polling `standdown.request` every few minutes, no work) and exited at ≈04:49 PDT. Reason, from the watchdog source read this session (`scripts/magistrate_watchdog.py`): the plan span begins at t0 − `PLAN_LEAD_S` (8 min, 04:52:00) and launches are FENCED from then until courier; before that, every clean exit is followed by a relaunch ≈220–400 s later (generic backoff + poll), each costing Ed one launch email and one fresh context load. Exiting at ≈04:49 puts the earliest possible relaunch inside the fence, so no further pre-t0 activation spawns; the four earlier ones (03:07, 03:27, 03:37, 03:47) were pure churn. The watchdog has no heartbeat-staleness rule, so the hold is safe; the REQUEST/TERM/KILL ladder (04:52/04:54/04:55) remains the backstop if the exit slipped. This is a scheduling choice inside the activation's own discretion, not a process change; the quiet-hold candidate for the watchdog itself stays queue data for Ed or the cold gate.

## Successor's next exact action

Unchanged from 4ca26e9c: a relaunch between 05:00 and 07:35 is bookkeeping only (the watchdog should not launch one; if it does, exit). After 07:35:00 PDT and `night/courier.sent`: harvest per runbook §2.0–§2.5 from the clone at H (byte-exact archive + lstat inventory + SHA256SUMS first), uninstall both agents FROM the clone (capture rc on the first call), desk pin commit if the session appended (`recover_calibration_ledger.py advance-head-pin`), `epoch_equivalence_check` from two checkouts; PASS → D-102 continuation addendum through the normal gate then real G2-a; FAIL or second INCONCLUSIVE → email Ed for a written answer (issue 316 fixes nothing further), no §3 action. Then lane 232 fix round 2 (e82f29ac record 01a).
