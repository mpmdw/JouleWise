# 23 — A210 bench error classified: environmental (magistrate b0ae8462, 2026-09-16 00:45 PDT)

`tests.test_arm_readiness_evidence_t0.test_g4_real_ruled_census_pgrep_dialect` errored once at the bench on the A210
branch: `ValueError: invalid literal for int(): 'WRITE_SCOPE:'` at tests/test_arm_readiness_evidence_t0.py:2746. The
test runs a REAL `pgrep -lf 'powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)'` and parses each line as
`<pid> <command>`; my running Codex seats carry their whole brief as argv (multi-line), and the brief text contains
`run_campaign`, so pgrep printed continuation lines that are not `<pid> …`. Same weakness A173 cured for the arm census
(PID-only discovery). Not an A210 defect; it would fail identically on main while such seats run. Registered for the
queue as a nit lane (TEST-PGREP-DIALECT-MULTILINE-01): parse `pgrep -f` PID-only output, or tolerate non-PID lines.
