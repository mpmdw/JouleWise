Implemented and committed locally on `align/2026-11-08-harvest-off-sol`; tree clean, nothing pushed.

- `95e5ec8b7`: parser reuse, parallel hashing, verified streaming raw transport and profiling.
- `9daa9c8fc`: [design](/Users/edr/code/CapstoneProject/jw-wt/sol-harvest-off-sol/docs/align/v4/HARVEST-OFF-sol.md), profiles and [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-harvest-off-sol/docs/run_reports/2026-11-08-harvest-off-sol.md).

All targeted commands passed (`python3.13 -B -m unittest`):

| Module | Passed |
|---|---:|
| `tests.test_harvest_off` | 7 |
| `tests.test_harvest_parse_cache` | 5 |
| `tests.test_powermetrics` | 61 |
| `tests.align.test_v4_cadence` | 16 |

Compileall and diff checks passed. Both 18.6/26.4 GB synthetic I/O workloads passed equality; complete harvest equality covered 177 files under a fixed canonical namespace and provenance context.

**Key constraint:** thermal triage cannot establish final eligibility. Current R12 gates require critical Air adjudication before the next arm. Estimated savings are **88–100 MBP compute minutes/window**; **30–45 minute turnaround remains conditional and unverified**.

Next: Sol/Opus agreement, production replay-envelope/receiver integration, then native smoke and timing. No sealed data, network, model downloads or full suite used.