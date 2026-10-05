# Block-4 lane X9 (Sol 6.1 xhigh): G10 placement and scheduling by measured offset (memo 1.4)

Worktree: /Users/edr/code/JouleWise-wt-dd5-x9 (branch `lane/2026-10-05-b4-x9` at bda1c180 = PR #483 head with origin/main merged). Scratch /tmp/dd5-x9/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics, systemsetup or Metal. Never touch the four pinned estimator files. Lane X7 is editing `scripts/write_v5_qualification_plan.py` and `joulewise/v5_qualification.py` in parallel (attempt-history pointer, `s2`, NULL restore). Keep your edits there small and local to the G10 checks so the merge is clean.

## The defect (`~/night-archive/ia-0a40/MEMO.md` lines 145-158)

Every T-0 preparation's arm reference (`scripts/capture_t0_step.py::_arm_reference`) turns network time ON when the sntp reference quorum's bound exceeds 0.5 s (`joulewise/arm_readiness_evidence_t0.py::_reference_agreement`). The wall clock is now about 1.15 s off, so G10's own input preparation resyncs. G10's ON then sees only the small error accrued since that resync, and the control may not move the anchor by more than 5 ms. A failed G10 is safe, but each attempt costs Ed's presence and hours.

## Lead ruling (addendum D, item 3; binding)

1. **Placement.** The G10 physical control runs after `a2`'s expiry check and before `s1`'s first T-0 boundary, on the same boot as `a1`, `a2` and `s1`. It no longer precedes `a1`. `a1`'s own arm reference does the one resync the block needs. By the time G10 runs, at least an hour or two of drift has accrued (about 11 ms per hour at today's −3.17 ppm).
   - Change the ordering checks that bind G10 to `a1`'s first T-0 boundary:
     - `scripts/write_v5_qualification_plan.py` around line 466;
     - `joulewise/v5_qualification.py::replay_g10_custody` around line 201.
   - The new bounds:
     - G10's whole custody (its last stamp and its OFF receipt) lies after `a2`'s `checked_monotonic_ns`, and before `s1`'s first T-0 boundary (the harvester has it) or the `s1` writer's own time (the writer runs before `s1`'s T-0);
     - same boot.
2. **Offset preflight.** Before it spends anything (no ON, no author inputs), the helper `scripts/ed_session/capture_t0_anchor_positive_control.py` runs the existing fixed clock-reference collector, the same argv as T-0's R0 capture. Reuse the code; do not write a new sntp parser. It computes the quorum agreement exactly as `_reference_agreement` does, and proceeds only if `0.020 s ≤ |midpoint|` and `bound ≤ 0.400 s`. Otherwise it exits with a distinct non-spending status: `g10_preflight_offset_too_small`, or `g10_preflight_offset_too_large`. That status tells the operator to wait (too small), or that the clock has drifted past the reference limit (too large: lead). The preflight record (argv, stdout, stderr, rc, stamps, the computed midpoint and bound) goes into the G10 custody and is verified by `verify_g10_custody`.
3. **Refuse to spend on a resync.** If the helper's input preparation would turn network time ON (any path through `_arm_reference` that reaches the resync), the helper stops before G10's own ON. It writes `g10_prep_resynced` as a non-spending outcome and preserves its custody. This attempt does not count as a G10 attempt. Today's code may not route the helper's preparation through `_arm_reference` at all; establish which, with file:line. If the helper never runs the arm reference, item 2 already covers the hazard: say so and add a test that proves the helper's preparation cannot reach the resync ON.
4. Recipe 46 (`docs/process_traces/2026-10-04-desk-day-v5/46-*`, if present) is human prose: do not edit it. List in your report what in it must change; the lead rewrites it.

## Tests

Add `tests/test_v5_block4_x9.py`. Kill-tests:

- G10 before `a2`'s check refuses in both the writer and the harvester replay;
- G10 after `s1`'s first T-0 boundary refuses;
- a different boot refuses;
- preflight 19 ms → too small, no ON executed (an injected runner records zero ON argv);
- preflight bound 0.41 s → too large;
- 20 ms passes;
- a tampered preflight record fails `verify_g10_custody`;
- the resync path refuses to spend.

Update the existing G10 tests (`tests/test_capture_t0_anchor_positive_control*.py`, `tests/test_v5_*`) that encode the old placement. Run the focused tests plus `tests.test_v5_qualification_plan tests.test_v5_s1_qualification tests.test_harvest_v5_qualification tests.test_v5_block4_composed tests.test_v5_block4_clock`.

Finish in this turn; FLAG what you cannot close.

WRITE_SCOPE: ["scripts/ed_session/capture_t0_anchor_positive_control.py", "scripts/write_v5_qualification_plan.py", "joulewise/v5_qualification.py", "joulewise/t0_rehearsal.py", "tests/test_v5_block4_x9.py", "tests/test_capture_t0_anchor_positive_control.py", "tests/test_capture_t0_anchor_positive_control_g10.py", "tests/test_v5_qualification_plan.py", "tests/test_v5_s1_qualification.py", "tests/test_harvest_v5_qualification.py", "tests/test_v5_block4_composed.py", "tests/test_v5_block4_clock.py", "tests/fixtures/v5_qualification/**"]
