# Activation 62527c24 — launch and close-out (2026-09-19 03:37–03:4x PDT), pre-t0 bookkeeping only

Launched 2026-09-19 03:37:10 PDT (watchdog attempt 61, backoff-usage expiry after 3422a575's clean exit at 03:31; `state.json` again labels that deliberate exit `usage_exhausted`, the known mislabel). Heartbeat written (resident pid 27427); launch email `1a0b93f6f7893895` sent to `claude.ai.copper531@passmail.net` (cc `claude2.glaring610@passmail.net`) at 03:40; `notice.ack` written. Pending notices: none. Open directive issues: none. No `standdown.request`, no `STOP`. No NO on the notice thread `1a0b9295e7b733be`.

## State verified at launch (read-only)

- Night `d079-epoch-25g83-derivation-n2-20260919` ARMED and untouched: t0 05:00:00 PDT 09-19 (`t0_epoch_s` 1789819200), window 9000 s, courier 07:35, dead-man 08:35. Launch was 83 minutes before t0.
- Measurement root `/Users/edr/JouleWise-measurement-20260919-derivation-n2` at `22b92ec7` (frozen triple head), `git status --short` empty.
- Plan directory `~/night-custody/d079-epoch-25g83-derivation-n2-20260919/` complete (calibration_plan.json, chain.zsh + both sha256 files, identity-epoch.json, night_plan.json schema v2, night_probe_receipt.json, t1-bindings.json, empty `night/`).
- `launchctl list`: `com.joulewise.night`, `com.joulewise.night.deadman`, `com.joulewise.magistrate` loaded, status 0; both night agents `runs = 0`, program = the clone's `.venv/bin/python`.
- `origin/main` = `132b1f9c` (3422a575's record); bookkeeping worktree `wt-mag-e82f29ac` at the same head. Canonical root untouched at `422cdebb`.

## What this activation did and did not do

Bookkeeping only, per the 4ca26e9c durable pointer: this record, a RUN_STATE block, one push. No Codex seat, no child, no lane work, no git operation in the canonical root or the clone. Exited cleanly well before the 04:54 ladder TERM so the 05:00 census is clean.

Judgment note: the pointer's literal boundary is "< 40 min to t0"; this launch was at t0−83 min, as was 3422a575 (t0−93 min). Lane 232 fix round 2 is a multi-round seat pipeline (seat + bench mutations + delta re-audit) that cannot finish and be stopped cleanly inside ~65 minutes, and a live Codex child at t0 would sit in the census. The two pre-t0 relaunches therefore took the same no-seat reading. Queue data, not a proposal (rule 11): the pointer could state the boundary as "no seat whose pipeline cannot close 30 min before t0" instead of a fixed 40 minutes.

Relaunch cadence note (queue data, again): third no-op relaunch inside this armed span (03:07 arm, 03:27, 03:37). The watchdog quiet-hold candidate for "armed night within N minutes" (named by 8b6be206, ebec14b5, 3422a575) remains for Ed or the cold gate.

## Successor's next exact action

Unchanged from 4ca26e9c: a relaunch before 05:00, or between 05:00 and 07:35, is bookkeeping only. After 07:35:00 PDT and `night/courier.sent`: harvest per runbook §2.0–§2.5 from the clone at H (byte-exact archive + lstat inventory + SHA256SUMS first), uninstall both agents FROM the clone (capture rc on the first call), desk pin commit if the session appended (`recover_calibration_ledger.py advance-head-pin`), `epoch_equivalence_check` from two checkouts; PASS → D-102 continuation addendum through the normal gate then real G2-a; FAIL or second INCONCLUSIVE → email Ed for a written answer (issue 316 fixes nothing further), no §3 action. Then lane 232 fix round 2 (e82f29ac record 01a).
