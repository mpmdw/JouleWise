# PR #454: cold Fable 5.1 final pass

Launched by activation b81a1c8f with `claude -p --model fable --effort high --allowedTools Read,Glob,Grep,Bash` in a fresh clone at `aaaf44ee`, no loop context. Verbatim answer, then the prompt.

FINAL PASS: MERGE

Commit aaaf44ee is a one-expression change to a refusal predicate in the issuer. The producer/consumer mismatch is real, the new binding keeps every authenticating check intact, nothing measured or counted changes, and the tests expose rather than hide the defect. The checkout is clean; I edited nothing.

**1. The mismatch is real.** CONFIRMED.

- `scripts/run_night.py:3180-3181` writes the start record with `plan_id = plan.plan_id`, where `plan` is the night plan (the derivation driver's own plan). `scripts/run_night.py:3001` writes the OFF receipt with the same id.
- `scripts/harvest_window.py:475` writes `harvest.json` with the same night `plan.plan_id`. `scripts/harvest_window.py:124-125` authenticates the wrapper's PLAN_ID against the *calibration* plan file, and `scripts/harvest_window.py:408-411` requires the ledger session's `plan_id`, `plan_sha256`, and `runs_root` to equal those calibration coordinates. So the ledger carries the calibration id, the window records carry the night id.
- Committed C1 bytes (identity keys only): `night/start_conditions.json` and `harvest.json` both carry plan id `d079-epoch-25g83-r6-derivation-c1-20261001T0617Z`. The C1 archive ledger at head 326 (the head `harvest.json` names) gives session `d079-epoch-25g83-r6-20261001T0617Z` plan id `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3`. The old comparison at `scripts/issue_calibration_acceptance_generation.py:1327` could never hold.
- Internal corroboration: the issuer already compares the OFF receipt's plan id with the start record's at `scripts/issue_calibration_acceptance_generation.py:1493`. With the old line 1327, both checks could pass only if the night id equalled the calibration id.
- Reproduced: against origin/main's issuer with the production-shaped fixtures, 10 tests error with "start-condition identity or result disagreement" (1 in the new module, 2 in test_harvest_window, 7 in test_acc_25g83_rev6).

**2. The new binding is sound.** No identity check is weakened.

- Unchanged anchors in `revision_six_records`: harvest names R9 by path plus sha256 (`:1310-1314`); `r9.session_id` must be a named ledger session and not repeated (`:1316-1317`); harvest names the start record by path plus sha256 (`:1322`); `start.session_id == sid` (`:1327`); both records must be committed at HEAD for a counting window (`:1333-1335`); prior-session manifests must follow ledger order (`:1356-1360`). For counting windows `revision_six_start_conditions` sha-authenticates evidence (a) to (g) and binds the OFF receipt plan id (`:1449`, `:1493`).
- The new check makes OFF receipt, start record, and harvest record agree on one night plan id. A wrong window's start record still fails on `session_id` and on the sha256 reference, and a counting window's bytes must be in HEAD's tree.
- MINOR (pre-existing, not introduced here): `harvest.json` is the operator-supplied locator and is only hashed (`:1342`), never commit-verified, so plan-id equality is a consistency check rather than an authentication. The authenticating binds remain session id, sha256, and committed bytes. Same status as `custody_root` and `window_end` already had.
- MINOR (pre-existing): `scripts/harvest_window.py:371-376` never compares the current window's start plan id with the night plan at harvest time. The issuer is the only place the equality is enforced.

**3. No byte, number, count, or pinned file changes.**

- `git diff --name-only origin/main..HEAD` lists only the issuer, the fixture, test_harvest_window, and the new test. The four pinned estimator files and the preregistration are untouched (empty diff stat).
- Preregistration Revision 6 §7 (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:1460-1463`) requires the record to be present with (a) to (g) evidence, matching digests, and the dwell. It never requires the start record's plan id to equal the calibration plan id. The records interface (`docs/process_traces/2026-09-29-interactive-ff50b201/120-revision6-records-interface.md:7-13`) names run_night.py's derivation path as producer and defines the field only as "plan id".
- The only decision that changes: a prior window whose start, OFF receipt, and harvest records agree on the night plan id is now admitted instead of refused. Counting arithmetic, timing, and B handling are untouched.

**4. Tests run, none weakened.**

| Module set | HEAD | origin/main issuer with new fixtures |
|---|---|---|
| test_rev6_prior_start_plan_id, test_harvest_window, test_acc_25g83_rev6, test_revision6_seal | 69 OK | 10 errors, all "start-condition identity" |
| test_land_window_records | 1 OK | not run |
| test_run_night | 255 ran, 8 failures | same 8 failures on a clean origin/main copy |

- The 8 run_night failures are all installer tests asserting "test interpreter must load the battery fixture in child Pythons". They fail identically on clean origin/main, so they are an environment precondition, not this diff.
- No assertion was deleted. `tests/test_harvest_window.py:137` swaps the calibration id for the night id in the current window's start record, which harvest never compares, so it is a shape correction only. The fixture's OFF receipt now uses the night id for both `plan_id` and `window_id`, matching `scripts/run_night.py:3001`.
- The new module's third case refuses a start record naming a different night plan id, and its first case asserts the real C1 bytes differ from the ledger id, which guards against fixtures masking this again.
- NIT: `tests/test_rev6_prior_start_plan_id.py:46` passes `require_committed=False`. The C1 bytes are committed, so `True` would also pass and bind more. With `finalized_slots={}` the start commit check is skipped anyway, so this is cosmetic.

## Prompt

Cold final pass (merge gate) on commit aaaf44ee, branch fix/2026-10-01-rev6-prior-start-plan-id, in this checkout. Base is origin/main 96e13107; see `git show aaaf44ee`. You are read-only: do not edit, commit or push anything. You may run code and tests (python: /Users/edr/code/JouleWise/.venv/bin/python -B). Never read a measured value (no B values, no chain-log slot lines).

Claim under review: scripts/issue_calibration_acceptance_generation.py revision_six_records refused every Revision 6 harvest that has a prior window, because it compared the prior window's night/start_conditions.json plan_id (written by scripts/run_night.py as the NIGHT plan id) with the calibration ledger session's plan_id (the CALIBRATION plan id, shared by all Revision 6 sessions). The fix compares the start record's plan_id with the prior harvest record's own plan_id (the night plan id). Test fixtures previously used the calibration id in both places, hiding the defect; they now use a distinct night plan id. tests/test_rev6_prior_start_plan_id.py replays window C1's real committed records in docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T0617Z/.

Verify independently and rule:
1. Is the producer/consumer mismatch real as described (cite run_night.py, harvest_window.py, the issuer, and the committed C1 bytes)?
2. Is the new binding sound: does it still tie the start record to the right window, and is the harvest record itself bound to the ledger session elsewhere (e.g. harvest-time checks on plan_id/plan_sha256/runs_root, committed-bytes checks)? Is any identity check weakened in a way that could admit a wrong window's records into the count?
3. Could this change alter any captured byte, any computed or counted number, any admit/refuse decision other than the intended one, the four pinned estimator files (joulewise/powermetrics_fiducial.py, joulewise/uncertainty_evidence.py, joulewise/adapters/powermetrics.py, joulewise/reduce.py), or disagree with the sealed registration configs/calibration/preregistration_d079_epoch_25g83_rev1.md (Revision 6)?
4. Run the affected tests (tests.test_rev6_prior_start_plan_id tests.test_harvest_window tests.test_acc_25g83_rev6 tests.test_revision6_seal) and check that no test was weakened.

First line of your answer: "FINAL PASS: MERGE" or "FINAL PASS: REFUSE". Then numbered findings with file:line evidence, each tagged BLOCKER / MAJOR / MINOR / NIT.
