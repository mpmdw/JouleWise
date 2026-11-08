Completed on local branch `fix-timing`; working tree clean, nothing pushed.

Fixed mapped-clock drift, incomplete-bundle bounds, R1 wait/release placement, drift warning noise, lone chain exits, and decode labels. Requested sleeps remain explicitly **“requested, unmeasured.”**

Commits:

- `58f98632f` — reader fixes and regression tests.
- `dc684b308` — documentation and handoff.

Six files changed: the reader, two test modules, existing timing guide, [TIMING-RECEIPTS.md](/Users/edr/code/CapstoneProject/jw-wt/sol-fix-timing/docs/perf/TIMING-RECEIPTS.md), and [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-fix-timing/docs/run_reports/2026-11-08-fix-timing.md). The receipt note includes checked insertion points; capture code is unchanged.

Each module ran separately using `python3.13 -B -m unittest`:

| Module | Result |
|---|---:|
| `tests.align.test_window_timing_opus_witness` | 17 PASS |
| `tests.align.test_window_timing` | 25 PASS |
| `tests.align.test_window_timing_r0` | 14 PASS |
| `tests.align.test_records` | 4 PASS |

Both original witnesses failed before the fixes. AST and diff checks passed.

Python 3.11 is unavailable here; the lead should repeat those modules there. No new native MLX test is needed. The 20 ppm allowance is diagnostic, not calibrated. Capture instrumentation still requires review and registration.

No sealed data, network, full suite, coordination-state edits, or analysis-job interaction.