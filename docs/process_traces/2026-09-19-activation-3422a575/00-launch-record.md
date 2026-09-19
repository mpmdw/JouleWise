# Activation 3422a575 — launch and close-out (2026-09-19 03:27–03:3x PDT), pre-t0 bookkeeping only

Launched 2026-09-19 03:27:08 PDT (watchdog attempt 60, backoff-usage expiry; `state.json` labelled 4ca26e9c's deliberate post-arm exit `usage_exhausted`, the known mislabel). Heartbeat written (pid 27159); launch email `1a0b936988a653a6` sent to `claude.ai.copper531@passmail.net` (cc `claude2.glaring610@passmail.net`) at 03:29; `notice.ack` written. Pending notices: none. Open directive issues: none. No `standdown.request`, no `STOP`. No NO on the notice thread `1a0b9295e7b733be`.

## State verified at launch (read-only)

- Night `d079-epoch-25g83-derivation-n2-20260919` ARMED and untouched: t0 05:00:00 PDT 09-19, window end 07:30, courier 07:35, dead-man 08:35. Launch was 93 minutes before t0.
- Measurement root `/Users/edr/JouleWise-measurement-20260919-derivation-n2` at `22b92ec7` (frozen triple head), `git status --porcelain` empty.
- Plan directory `~/night-custody/d079-epoch-25g83-derivation-n2-20260919/` complete (calibration_plan.json, chain.zsh + both sha256 files, identity-epoch.json, night_plan.json, night_probe_receipt.json, t1-bindings.json, empty `night/`).
- `launchctl list`: `com.joulewise.night`, `com.joulewise.night.deadman`, `com.joulewise.magistrate` loaded, all status 0; night plist `StartCalendarInterval` = 2026-09-19 05:00, `WorkingDirectory` = the clone.
- `origin/main` = `e224ffae` (4ca26e9c's arm record); bookkeeping worktree `wt-mag-e82f29ac` at the same head. Canonical root untouched at `422cdebb`.

## What this activation did and did not do

Bookkeeping only, per 4ca26e9c's durable pointer: this record, a RUN_STATE block, one push. No Codex seat, no child, no lane work, no git operation in the canonical root or the clone. Exited cleanly well before the 04:20 pre-t0 boundary so the 05:00 census is clean.

Relaunch cadence note (queue data, not a proposal — rule 11): this is another no-op relaunch inside an armed span (03:27 after 4ca26e9c's 03:18 exit; the watchdog re-enters `BACKOFF_USAGE` for ≈5 minutes, then relaunches). Each costs a launch email and a record. The candidate lane named by 8b6be206 and ebec14b5 — a watchdog quiet-hold for "armed night within N minutes" — remains for Ed or the cold gate.

## Successor's next exact action

Unchanged from 4ca26e9c: a relaunch before 05:00 with < 40 min to t0, or between 05:00 and 07:35, is bookkeeping only. After 07:35:00 PDT and `night/courier.sent`: harvest per runbook §2.0–§2.5 from the clone at H (byte-exact archive + SHA256SUMS first), uninstall both agents FROM the clone (capture rc on the first call), desk pin commit if the session appended, `epoch_equivalence_check` from two checkouts; PASS → D-102 continuation addendum through the normal gate then real G2-a; FAIL or second INCONCLUSIVE → email Ed for a written answer (issue 316 fixes nothing further), no §3 action. Then lane 232 fix round 2 (e82f29ac record 01a).
