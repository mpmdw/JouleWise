# Harvest PR gate — rows 1 + 2 (execution lens): independent re-derivation audit of commit 722f7bd1

ROLE: independent, non-author auditor. You did not produce this commit. Read-only.
WRITE_SCOPE: []
Write nothing in any repository; scratch only under /tmp/sol-harvest-audit-77b1bee2/.
Bridge depth is one hop: do not call Claude by any route.

## The candidate
Commit `722f7bd161f1a1d0ae2ef624f7f29aac3e347d82` (parent `a71a5e79`; origin/main is `670756f3`, which adds only test-only #433), checked out detached in your working dir
`/Users/edr/code/JouleWise-wt-harvest-audit-77b1bee2`. It changes exactly:
- `configs/calibration/calibration_ledger_head.json` (pin 226/bd7aee7a…6693 -> 276/476e2ae8…9737)
- adds `configs/calibration/battery_float_verdicts/d079-epoch-25g83-derivation-w2-20260927.json` (battery=pass)

It was produced by the harvest of derivation window W2 following `docs/phase_2/derivation_night_runbook.md` §2.0–§2.2a
(read those sections first). Inputs (DO NOT MODIFY any of them):
- Measurement root (the clone the night ran from, now holding 722f7bd1 as HEAD): `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`, python `$M/.venv/bin/python`
- Ledger: `$M/runs/calibration_observation_ledger.jsonl` (sha256 23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d; byte copy at `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/measurement-runs/`)
- Night custody root: `/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927` (RUNS_ROOT = `<that>/runs`)
- SESSION_ID = `d079-epoch-25g83-derivation-w2-20260927`; PREREGISTRATION_SHA256 = `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`

## Verify independently, with executed evidence (paste commands + outputs)
1. The pin: recompute the session's terminal head with `joulewise.calibration_ledger.terminal_head_pin_for_session` AND independently by hand (parse the JSONL; the last row's sequence/receipt digest; confirm the W2 session's rows are exactly the tail after row 226 and the session is finalized 12/12). Confirm the pin file bytes are exactly what the tool would write.
2. The verdict: recompute from raw bytes with `joulewise.battery_float.validate_window` (or whatever the committed `battery-verdict` path calls — trace it in `scripts/issue_calibration_acceptance_generation.py`) and compare every field of the committed verdict JSON. Check each slot's `raw/battery_float.pre.ioreg`/`post.ioreg` sha256 against `instrument_evidence.json`, and each `instrument_evidence.json` sha against its ledger row. Independently read the ioreg fields (ExternalConnected, IsCharging, InstantAmperage) per slot and confirm the pass predicate (|InstantAmperage| <= 200 mA, not charging, external connected — check the exact predicate in code and in registration amendment A-R5b) holds for all 12 slots, pre and post.
3. `authenticate_committed_verdict` passes at 722f7bd1 in the measurement root (it is read-only), and the single-commit rule (exactly one commit touches the verdict path and it added it) holds.
4. Re-run (read-only) from the measurement root: the §2.2a (vi) cadence report and (vii) `check --session-ids` exactly as the runbook writes them, and confirm: cadence R5(n) CONTINUE, median 128.47 ms, max 141.39 ms; dry run `battery=pass recorded=pass`, `state=finalized terminal=yes declared=12 filled=12 valid=6`, admissible yes. Confirm nothing in the measurement root or ledger changed (git status clean, ledger sha unchanged) after your runs.
5. Execution-lens question: is there any way the committed verdict or pin could be wrong while all of the above pass (e.g. a slot whose ioreg read failed but was recorded as pass; a ledger row outside the session)? Name it or say none found.
6. Also run `check` with BOTH sessions named (`--session-ids d079-epoch-25g83-derivation-w1-20260927 --session-ids d079-epoch-25g83-derivation-w2-20260927`, the flag repeats) and confirm rc 0 / admissible yes with 6+6 valid; confirm the W2-only rc 5 is exactly the addendum A-7 blocker the runbook §2.2 predicts. Confirm the W2 ledger rows 227..276 are exactly the W2 session and that rows 1..226 are byte-identical to the W1-harvested 226-row ledger (`/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/measurement-runs/calibration_observation_ledger.jsonl`).
7. The manual cross-check (lane BATTERY-VALIDATOR-PROBE-ERROR-01): independently confirm all 24 readings have `probe_error=false` and `passed=true` in `instrument_evidence.json` and match their raw ioreg bytes.

## Report (claude-codex-report/v1 envelope, review genre)
Findings tiered BLOCKER / SHOULD-FIX / NIT, each with file:line or command evidence. Final line: `AUDIT: PASS` or `AUDIT: FAIL`.
