# R7-2 refusal fix (`0aa014307`) and six stale R1 expectations (`ops/2026-11-11-r1-kit-stale-b`)

Interim lane lead (Opus 5.5), 2026-11-11.

## The fix (condition-13 file; Fable 5.2 delta review commissioned by the orchestrator)

`scripts/align_r1_rehearsal.py`: `a85ee8ec6` read the RL-72 E2 span bound (`night_worst_case_s(args.runtime)`) before `run()`'s
refusal handler, so a runtime config without `g0_timeout_s` exited 1 with a traceback and no `r1_result.json`. `0aa014307`
moves the read inside the handler, right after the output directory is created and before any prepare-packet, power-mode or
runtime work; the teardown's span check tolerates the unset bound. Witness
`test_r1_round7_science...test_a_runtime_config_without_the_timeout_refuses_at_t0`: red before, green after, red again under the
mutant that moves the call back out. No other runtime-config read precedes the handler.

## The six stale expectations: independent Opus cold review, ADMIT

All six match the code at presign and the cited rulings (RL-59 "1,200 s stays, for every R1 gate"; RL-72 E2 whole-unit redos and
window 126,480 s; RL-72 E3 step-kind dispatch; the follow-up contract's "No G0-only retry occurs"). The reviewer recomputed the
admission-unit arithmetic (subtotal 58,711.9616 s; floor 99,768 s; span 108,768 s). No still-applicable check dropped;
FakeWorld caps match production (1,200 s; 600 s only for the sensors-only helper); the R7-2 witness is byte-unchanged.
Non-blocking notes: two assertions only re-check fixture-emitted values (as before); `release_segment_bound_s() == 665` and a
test name refer to a helper production no longer calls; and comments/docstrings in `scripts/align_r1_rehearsal.py` (lines 84-88,
the `segment_bounds` docstring, the `G0_RELEASE_BOUND_S` comment) and `docs/align/r1_runtime_contract.md` (lines ~100-182) still
say "step-30b keeps 600 s". The driver comments are condition-13 bytes and are left for the next registration; the contract
text is a follow-up.

## Native runs on the Air at `95a189b9c` (merge of both), TMPDIR on JW-EXT

`test_r1_round7_science` 18 OK; `test_r1_round8` 21 OK (the seat's 5 extra failures were its sandbox's denied process census);
`test_r1_rehearsal` 77 OK; `test_r1_followup` 12 OK; `test_r1_round2` 14 OK; `test_r1_round3` 8 OK; `test_r1_round4` 10 OK;
`test_v4_executed_closure` 6 OK; `test_v4_dynamic_closure` 10 OK; `test_v4_registration` 24 OK.
