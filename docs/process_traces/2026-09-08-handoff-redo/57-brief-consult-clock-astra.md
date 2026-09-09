WRITE_SCOPE: []

# CONSULT (rule-11 same-signature escalation) — the T-0 clock regression in tests/test_launch_window.py is flaky across hosts and wall time (gpt-6-astra, high, read-only)

History (all today, 2026-09-08): T0-ACID-CLOCK-02 changed `_mint_v4_arm` in tests/test_launch_window.py so the
fixture's R0 anchor derives from the author's RAW clock (mixed clock families failed on this Mac at 5+ days
uptime), and added `test_mint_keeps_raw_anchors_separate_from_sequence_clock` with subcases
ordinary_minus_raw_ns = ±7_200_000_000_000. Round 1 (Linux follow-up): the −2 h subcase errored on fresh Linux
runners with "clock-reference command capture fields are invalid or stale" because the synthetic capture origin
went negative; cured by flooring the capture origin at zero (main 019f9bba, CI green once). Round 2 signature:
the SAME regression now fails non-deterministically — on this Mac under load (both subcases; the same test alone
on an idle machine passes in ~200 s) and on GitHub Linux CI (+2 h subcase, job log
docs/process_traces/2026-09-08-handoff-redo/56-ci-launch-window-flake-log.txt) — always with the ARM step
refusing `readiness_clock_preflight_refused` (`_mint_v4_arm` line ~793: `armed.returncode` 1) rather than an
authoring error. Production code is untouched by all of this; only the test fixture/regression moved.

Your charge (read-only; scratch under $TMPDIR): (1) find the exact refusal path — which check in the arm-side
readiness clock preflight (grep `readiness_clock_preflight` in joulewise/) compares what against what, with which
bounds, and how the fixture's synthetic anchors/offsets plus REAL elapsed wall time between mint and arm interact
with it; state the inequality that fails under load or on the +2 h subcase; (2) explain why the −2 h and +2 h
subcases are asymmetric and why the idle-Mac run passes; (3) design a DETERMINISTIC regression for the property
"R0 and the author anchor share the RAW clock family; sequence timing stays ordinary-monotonic" that does not
depend on real clocks or elapsed time (e.g. inject both clock readers for mint AND arm, or assert on the authored
evidence fields directly without running the arm preflight), and prove it still fails against the pre-3c366db7
helper (revert the helper in a $TMPDIR copy); (4) say whether the current regression should be deleted or
rewritten, and whether the two `_mint_v4_arm` fixture edits (RAW-derived R0; floored capture origin) are
themselves correct or merely masking. Run only tests.test_launch_window (never the repository-wide suite).
Report (genre review): `verdict` = {counts, findings}; header < 8192 bytes; body = the failing inequality with
file:line, the deterministic-regression design (exact code sketch), and the counterfactual proof.
