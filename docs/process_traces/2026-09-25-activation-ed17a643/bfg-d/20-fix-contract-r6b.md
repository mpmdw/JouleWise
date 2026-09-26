# BFG-D round 6b: completion of fix round 2 (lead contract)

The round-6 seat (report `19-fix-seat-report-r6.md`) closed R2-1..R2-4 and R2-8..R2-11. It left the following items open. None of them reopens the parser grammar.

**C-1 (MATERIAL): regression introduced by fix round 1.** `tests.test_validate_powermetrics_fiducial.ContinuedEpochPreflightTests` has 5 failures, with `_continuation_snapshot` refusing `calibration_ledger_head_mismatch`, `…_uncommitted` and `…_malformed`. Bisect: OK at `df33888f`, FAILED at `faf0ea01`. The failure lives in fix round 1's changes, most likely the fixture builder under `tests/fixtures/epoch_continuation/` or `epoch_bootstrap/` (FX-2's pin plus verdict commit).
- Closure: find the root cause and fix it at the cause, in fixture or code. Do not change the 5 tests' assertions.
- Show the module OK at the fix. Also run every test module that imports `tests/fixtures/epoch_continuation/build.py` or `tests/fixtures/epoch_bootstrap/build.py` (find them with grep) and paste their tails. This is the sweep that the fix-round-1 seat and both delta reviewers missed.

**C-2 (R2-5 completion, the ruled R2-2 shape): three ungated B readers the sweep found.** Each refuses, before reading any B, any evidence whose identity epoch equals `REVISION_FIVE_EPOCH` or that carries a `battery_float` key. Each prints a one-line refusal and exits non-zero (or raises its module's existing refusal type):
- (a) `scripts/calibration_ledger_backfill.py` (around `:78-80`);
- (b) `scripts/paper_anchor_correction_quantified.py` (around `:700-709`), with the refusal applied to every capture under the corpus root;
- (c) `joulewise/controller.py` (around `:438-490`), the instrument-calibration attachment, so that `scripts/run_campaign.py:2112` inherits it.

Revision 5 derivation observations never bracket endpoints, so no legitimate path is lost. Each needs a RED-at-`f5525aac`-then-GREEN test that uses a Revision-5 fixture, plus proof that the existing modules for those files still pass.

**C-3 (seat F6): runbook narrative.** In `docs/phase_2/derivation_night_runbook.md`, add one plain banner paragraph at the top of the equivalence-night PASS route (§2.4/§2.5 and the §4 continuation text). The banner says:
- epoch 25G83 under registration Revision 5 takes no equivalence look;
- `epoch_equivalence_check` and `issue_epoch_continuation` refuse its sessions;
- W1/W2 follow Revision 5's derivation procedure instead.

Keep the older text as the historical record. `tests.test_docs_freshness` must pass.

**Rules:**
- WRITE_SCOPE is given in the prompt.
- Never weaken an assertion.
- Pin proof: `git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs` must be empty.
- No full discovery.
- One foreground session; no subagents or background jobs.
