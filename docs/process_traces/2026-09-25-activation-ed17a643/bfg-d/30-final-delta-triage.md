# BFG-D final delta triage (magistrate ed17a643)

The final deltas on `3ad48d1e` were run by Sol 6.0 xhigh (`11-review/08`) and Astra 6 xhigh (`11-review/09`). **Neither found a behavioural BLOCKER.** Both confirmed parity with executed probes on P3, P4, P5 and F1 (deletion and tampering), shared-collector use, H-2 determinism, the fixture flag refusing outside logical mode, and the paper tool byte-identical to `c6814dd8`. The consumer re-grep found no verdict-deciding path outside the seam.

**Dispositions:**

| Finding | Tier as filed | Disposition |
|---|---|---|
| Sol R1 / Astra R2: the pin proof is non-empty (the registration file) | BLOCKER / MATERIAL | **Baseline artefact, no change.** The diff is the #418 seal plus the #423 A-R5b append, both merged to main and brought in by the main merge `a9c40d4c`. Proof taken against main instead: `git diff --stat cab01506 3ad48d1e -- <all pinned paths incl. configs and the paper tool>` is **empty** (lead, executed). BFG-D changes no pinned byte. |
| Astra R1: relative imports (`from . import battery_float`) bypass the AST guard | MATERIAL | **Fixed at the bench.** `_absolute_module` resolves relative `ImportFrom`, with regression `test_self_test_relative_imports_are_resolved`: RED with the resolution mutated out, GREEN at the fix. |
| Sol R2: `importlib.import_module("joulewise.battery_" + "float")` plus `getattr` bypasses the guard | MATERIAL | **Recorded limitation, no change.** The guard catches drift, i.e. an honest consumer calling a primitive directly. A computed module name is deliberate evasion by the code author, an operator-only adversary outside the threat model (D-161). The behavioural parity tests still catch the two drift shapes that matter (caught-and-continued, divergent session set), as both deltas' mutants showed. |
| Astra R3: the loader accepts a record that omits the digest when the caller passes `None` | NIT | **Fixed at the bench.** `load_committed_verdict` validates the caller's digest on its own (64 lowercase hex). Regression `test_v_b_a_record_without_a_digest_never_loads_against_none`. |
| Sol R3 / Astra R4: obligations §4.5 reissue not landed | MATERIAL / NIT | **Landed** as `29-obligations-4.5-reissued.md`. |
| Sol R4: two sandbox-environment failures (`sysctl` not permitted; the 8 s subprocess watchdog) | MATERIAL (verification gap) | **Environment.** The lead's local runs pass the live identity test (`test_issue_calibration_acceptance_generation`, 156 OK in this triage's run). `test_run_night`'s watchdog case is covered by the full-suite replay. |

**Bench verification after the fixes:** `tests.test_battery_float`, `tests.test_battery_float_consumers`, `tests.test_issue_calibration_acceptance_generation` and `tests.test_calibration_cadence_report` ran **231 tests, OK**, including the grammar freeze pin.
