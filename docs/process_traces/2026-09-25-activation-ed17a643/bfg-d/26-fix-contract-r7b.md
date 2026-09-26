# BFG-D round 7b: integration-replay regressions (lead contract)

The integration replay of main + BFG-D at `80753b97` (7,347 tests; the tail is on the bookkeeping branch at `docs/process_traces/2026-09-25-activation-ed17a643/31-integ-137cc9ee/tail.txt`) found regressions that no focused sweep caught. Close each at its cause. Paste RED output at `346e373f`, then GREEN.

**H-1: `tests.test_t0_rehearsal`.**
- The test `test_rehearsal_t0_liveness_bound_refuses_at_600s_plus_1ns` and its siblings still pin 600 s.
- Move all three boundary tests to 610 s, exactly as the lead did for `tests.test_arm_readiness` at `3e984ecc`: refuse at +1 ns, pass at −1 ns, pass exactly at 610 s. Rename them to match.
- Then grep all of `tests/` for any other `600_000_000_00` liveness boundary and fix every one the same way. List each one.

**H-2: `tests.test_calibration_exits` `PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes` (MATERIAL; determinism).**
- Under the logical test clock, `instrument_evidence.json` is no longer byte-identical between runs. The writer's battery observations carry real monotonic and wall stamps, and possibly real ioreg bytes.
- Required fix: the writer's slot battery observations take every stamp from the writer's own clock abstraction, which is the logical clock in tests. In logical-clock and fixture modes they use the injected fixture probe runner, so evidence bytes are deterministic.
- In production the real clock and the real ioreg are used, unchanged.
- The fix must not move either observation into the clock-anchor interval. Test 9, anchor non-overlap, must stay green.
- The fix must not change the frozen grammar.
- Do not change the failing test's assertion.

**H-3: `tests.test_git_fixture_maintenance`.** `tests/test_battery_float.py` around line 415 initializes git directly. Route it through the shared git-fixture helper that the maintenance test requires. Run the maintenance test and `tests.test_battery_float`.

**H-4: `tests.test_paper_round7_artifacts` (3 failures: registry pinned files, producers byte-identical, appendix derive).**
- Cause: round 6b's C-2(b) edited `scripts/paper_anchor_correction_quantified.py`. That file's sha256 is pinned in `docs/paper/results-fill-registry.md` ("AS = …") and it is a claim-bearing paper producer.
- **Revert C-2(b) exactly**, so the file is byte-identical to `c6814dd8`, and remove its C-2(b) test from `tests/test_revision_five_b_readers.py`.
- Disposition, recorded in the sweep inventory row: the tool is pinned by sha in the results registry and reads only the retained historical corpora named in `docs/paper/round7/anchor-correction-quantified.md`. It is outside the Revision-5 path, and a Revision-5 root is never one of its inputs. Do not change a paper pin.
- If `tests.test_battery_float_sweep` asserts a gate for this row, change that row to the pinned-historical-corpus disposition and cite this contract.

**H-5: sweep.**
- After H-1..H-4, run every module named in the tail's FAIL lines, apart from the known load-timing flake `test_sample_quiet_predicate_evidence`.
- Also run every module that imports a file changed in this round.
- Paste all their tails.

**Rules.**
- WRITE_SCOPE is given in the prompt.
- Never weaken an assertion.
- Pin proof: `git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs scripts/paper_anchor_correction_quantified.py` must be empty. That list now includes the paper tool.
- No full discovery.
- One foreground session.
