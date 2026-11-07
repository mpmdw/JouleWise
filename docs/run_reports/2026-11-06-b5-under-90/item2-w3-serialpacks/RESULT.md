# Item 2 — workers 3, serial packs

- **Host:** `nproc` = 3; Python 3.12.13.
- **Outcome:** joined driver exit 2 after 1722.720 s; the requested `--stop-after 5` closed the record with the expected step 8 `synthetic_stop_after` refusal (`unclassified_refusal`). Steps 6, 9, 9b, 10, and 11 were not run.
- **Step wall time/status:** 0 — 16.415 s, ok; 1 — 324.865 s, ok; 2 — 18.100 s, ok; 3 — 0.754 s, ok; 3b — 294.634 s, ok; 4 alpha/beta — 180.869 s, ok; 5 — 885.469 s, ok; 8 — 0.080 s, `unclassified_refusal` (`synthetic_stop_after`).
- **Step 4 note:** both extraction subprocesses exited 1 after fail-closed refusals for the two alpha and two beta `d117` cells recorded in `failure-logs/0529-4-alpha.stderr.log` and `failure-logs/0530-4-beta.stderr.log`; the joined driver nevertheless classifies both step-4 windows as `ok`. The refusal is emitted when extraction finds refused cells (`scripts/extract_detection_floors.py:278`). No step before 4 refused.
- **L4 calibration bracket counters:** `L4_calibration_bracket:fill` = 3; `L4_calibration_bracket:hit` = 6; `L4_calibration_bracket:miss` = 6.
