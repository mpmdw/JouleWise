Committed `83e3f3450` on `align/2026-11-08-b3-sim-sol1`. Working tree clean; no push.

[Report](docs/align/v4/b3-sim/B3-SIM-sol1.md) includes roster citations, simulator, saved outputs, all 36 scenarios, and Monte Carlo intervals.

- **Count stopping can exceed nominal FPR targets.** One hot-window scenario gives maximum-threshold FPR **2.841% [2.826, 2.856]**, versus fixed-eight **2.141% [2.130, 2.152]**.
- Fixed eight also fails under modeled forward drift. Minimum seven alone is insufficient.
- Minimum seven plus a **0.5 s_r margin** meets mean targets throughout this grid, but requires scientific qualification and detection-power assessment.

Verification: simulator `--check` passed six checks; `python3.13 -B -m unittest tests.align.test_v4_estimands` passed 15 tests; output audits and whitespace checks passed. No full suite, product changes, coordination edits, network, or measurement-data access.

The report discloses an aborted preflight and NumPy arithmetic workaround. Before W1, the lead should reproduce using supported Python 3.11/3.13 + NumPy and resolve the scorer, fit-slot bill, eligibility semantics, and defensible drift envelope.