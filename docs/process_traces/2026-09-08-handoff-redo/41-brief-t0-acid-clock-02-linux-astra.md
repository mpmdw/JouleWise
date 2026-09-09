WRITE_SCOPE: ["tests/test_launch_window.py"]

# Seat brief — T0-ACID-CLOCK-02 regression fails on Linux CI (gpt-6-astra, medium)

Main 3c366db7 merged T0-ACID-CLOCK-02: `tests/test_launch_window.py` `_mint_v4_arm` now derives R0 from the
author's RAW anchor, plus regression `test_mint_keeps_raw_anchors_separate_from_sequence_clock` with subcases
`ordinary_minus_raw_ns` = ±7_200_000_000_000. It passes on this Mac (26 OK). On GitHub Linux CI (ubuntu, Python
3.11 and 3.14) the −2 h subcase ERRORS:
  ERROR: test_mint_keeps_raw_anchors_separate_from_sequence_clock (...) (ordinary_minus_raw_ns=-7200000000000)
  joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: clock-reference command capture fields are invalid or stale
(the +2 h subcase passed). The check that raises lives in joulewise/arm_readiness_evidence_t0.py (grep "capture
fields are invalid or stale"): read it and determine why a −2 h ordinary-minus-RAW offset makes the synthetic
capture look stale on Linux but not on Darwin (likely the fixture's `started_monotonic_ns`/`finished_monotonic_ns`
or the realtime fields cross a bound that depends on the REAL machine clocks — on this Mac the real RAW/monotonic
offset is large after 5 days of uptime, on a fresh CI VM it is ~0). Cure in the TEST ONLY: make the regression
independent of the host's real clock offset (e.g. synthesize both anchors and the capture timestamps from one
explicit base, or choose offsets that stay inside every staleness bound in both directions), keeping it a genuine
counterfactual (it must still fail if `_mint_v4_arm` reverts to the pre-3c366db7 ordinary-monotonic R0; prove that
by reverting the helper in a $TMPDIR copy). Simulate the CI condition locally by patching the real clock sampling
so ordinary and RAW are equal (offset 0) — the test must pass under offset 0, under the Mac's real offset, and under
±2 h. Production code must not change (NEEDS_RULING otherwise). Acceptance = the module to a log with rc; do NOT
run the repository-wide suite; no `git commit`; header < 8192 bytes; genre implementation verdict keys; body =
root cause with file:line, the counterfactual proof, the three-condition results.
