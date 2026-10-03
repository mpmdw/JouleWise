You are an independent reviewer with an EXECUTING lens for JouleWise PR #460 (head b39d7015, base 4205713c). You did not write it. 
WRITE_SCOPE: []
(no repository edits; scratch only under /tmp).

Change: `scripts/gen_g2_phase_d.py` `integrated_g2a_chain` now renames the runsheet window id inside every `G2A_*` export BEFORE pinning CALIBRATION_LEDGER, LEDGER_HEAD_PIN and G2A_ROOT (previously after, which doubled the plan-id suffix of a real root `/Users/edr/night-g2a/<plan_id>` because the plan id begins with the runsheet id). New test `tests/test_gen_g2a_window.py::G2aInspectionTests::test_root_containing_the_plan_id_is_exported_unchanged`. Recipe `docs/process_traces/2026-10-02-design-block2/40-g2a-arm-recipe.md` step2 argv-only line now passes `MEASUREMENT_HEAD="$H"`.

Do, executing code (python: /Users/edr/night-custody/measurement/JouleWise-measurement-20261003T0742Z-g2a-w1/.venv/bin/python, run from this worktree with `-B -m unittest`):
1. `git diff 4205713c b39d7015`. Run tests.test_gen_g2a_window and tests.test_gen_g2_phase_d.
2. Generate a chain with emit_g2a_night_chain for night_date 20261003, plan_id d117-g2a-prefill-probe-20261003T0742Z, g2a_root /tmp/x/night-g2a/d117-g2a-prefill-probe-20261003T0742Z (and a few adversarial ids: plan id equal to the runsheet id; root not containing the id; root containing the id twice) into /tmp; diff every `export` line against the pre-fix generator (`git show 4205713c:scripts/gen_g2_phase_d.py`). Confirm that only G2A_ROOT changes, and only where the old code doubled it; every other export (window id, session id, attempt ids, evidence root id, plan id, ledger paths) must be byte-identical between old and new.
3. Check whether any other G2A_* export, or the CALIBRATION_LEDGER/LEDGER_HEAD_PIN pins, could now be rewritten wrongly by the new order (e.g. a measurement_root containing the runsheet id).
4. Check that the recipe change matches what `scripts/run_night.py` `_chain_environment` supplies, and whether any other driver-supplied variable that the chain reads before the argv-only branch is still missing from the bench inspection.
Verdict line at the end, exactly one of: `VERDICT: PASS` or `VERDICT: FAIL`, then findings as BLOCKER/MAJOR/MINOR/NIT with file:line and the executed evidence.
