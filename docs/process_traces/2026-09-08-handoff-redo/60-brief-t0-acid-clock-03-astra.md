WRITE_SCOPE: ["tests/test_launch_window.py"]

# Seat brief — T0-ACID-CLOCK-03: deterministic clock-family regression per the rule-11 consult (gpt-6-astra, medium)

Main 481df11c PRUNED `test_mint_keeps_raw_anchors_separate_from_sequence_clock` from tests/test_launch_window.py
(a comment at the top of `ProductionArmRelocationLaunchTests` records why). The consult report at
docs/process_traces/2026-09-08-handoff-redo/59-consult-clock-astra-report.md (read it in full; it is on main? — if
not present in this worktree, the same text is in this brief's companion file
/private/tmp/claude-501/-Users-edr-code-JouleWise/1d65b6ea-5518-4207-8f65-31f8bf376204/scratchpad/runs/consult-clock.md,
read-only) established: the old regression sampled ONE anchor outside the subcase loop while the ARM subprocess
samples live clocks, so the live checks `abs((W_arm − R_arm) − (W_author − R_author)) > 5 ms` and
`read_skew_arm > 1 ms` (joulewise/arm_readiness.py ~:6512-6515) fail with elapsed time and load; the ±2 h offset
never entered the live inequality. Its "Deterministic replacement" section gives a concrete code sketch: keep
`_mint_v4_arm`'s fixture fixes (RAW-derived R0; floored capture origin), inject fixed ordinary and RAW readers,
intercept the helper at its successful authoring boundary, assert on the authored CLOCK_ATTESTATION receipt
fields and the capture file (r0_anchor_monotonic_raw_ns = raw_now − _MIN_IDLE_NS − 980, anchor_monotonic_raw_ns
= raw_now, t0_span_ns = _MIN_IDLE_NS + 980, capture started_monotonic_ns = max(ordinary, 0) + 10, etc.), and STOP
before ARM (raise a sentinel exception the test catches), over the cases (raw_now, offset) =
(10e12, −2h), (10e12, 0), (10e12, +2h), (60e9, −2h) — the last exercising the capture floor.

Do: (1) implement that replacement test exactly in spirit (adapt names to the real receipt/field names you find;
every expected value derived from the injected readers, none from real clocks); (2) prove the counterfactual: in a
$TMPDIR copy, restore the pre-3c366db7 `_mint_v4_arm` author-anchor derivation (ordinary-derived R0; `git show
e4ce8b3b:tests/test_launch_window.py` is read-only history) and confirm the new test FAILS for the ±2 h cases and
passes for 0; also confirm it fails when the capture floor is removed (the 60e9/−2h case); (3) run the test three
times back-to-back and once under load (start a `yes > /dev/null &` burner for the run, then kill it by pid) — it
must pass every time and take seconds, not minutes; (4) run the whole module to a log with rc. Production code
must not change (NEEDS_RULING otherwise). Do NOT run the repository-wide suite; no `git commit`; header < 8192
bytes; genre implementation verdict keys; body = the expected-value table, counterfactual tails, timing of the
three runs, module rc.
