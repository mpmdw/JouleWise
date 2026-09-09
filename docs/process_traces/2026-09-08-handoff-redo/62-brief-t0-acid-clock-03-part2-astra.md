WRITE_SCOPE: ["tests/test_launch_window.py"]

# Seat brief — T0-ACID-CLOCK-03 part 2: verify the deterministic regression under the magistrate's ruling (gpt-6-astra, medium)

HEAD of this worktree = part 1 (committed): the consult's four-case deterministic regression
`test_mint_keeps_raw_anchors_separate_from_sequence_clock` is implemented in tests/test_launch_window.py with fixed
readers, receipt/capture assertions, and a sentinel that stops before ARM (expected-value table in the part-1
report). Part 1 returned NEEDS_RULING on two points; the interactive magistrate rules:

R1. The historical (pre-3c366db7) helper may FAIL all four cases, including zero offset. The counterfactual proof
    is that the new test rejects the old helper (its author anchor was fixture_now, off by _MIN_IDLE_NS + 1000 ns);
    no zero-offset positive control against the old helper is required. Record which assertion fails per case.
R2. The full fixture runtime (~200 s per run) is ACCEPTED. Determinism beats speed here. The "seconds not minutes"
    requirement is withdrawn; do not redesign the setup.

Now do the verification that was blocked: (1) counterfactual — in a $TMPDIR copy restore the pre-3c366db7
`_mint_v4_arm` author-anchor derivation (`git show e4ce8b3b:tests/test_launch_window.py`, read-only history) and
run the new test: record the failing assertion per case; also remove the capture floor in a second copy and confirm
the (60e9, −2h) case fails; (2) run the new test three times back-to-back on HEAD and once with a CPU burner
running (`yes > /dev/null &`, kill it by pid afterwards): all must pass; record wall times; (3) run the whole module
(`python3 -m unittest tests.test_launch_window`) to a log with rc. No production change; no `git commit`; never the
repository-wide suite; header < 8192 bytes; genre implementation verdict keys; body = counterfactual table, the
four timings, module rc. If any run fails, do not patch around it: report the failing assertion and stop.
