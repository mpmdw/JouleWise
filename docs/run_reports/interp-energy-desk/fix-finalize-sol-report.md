Committed locally on `fix-finalize`; working tree clean, no push or lane changes.

- `cf2db8c67`: F-L1 adds three retries with backoff, then fails closed naming the file. F-L2 disables reuse outside APFS or with coarse timestamps.
- `d3a4a8b95`: documents F-L3’s interruption delay, tests F-L4’s thread isolation, and adds the unapplied [v4 port note](/Users/edr/code/CapstoneProject/jw-wt/sol-fix-finalize/docs/perf/eng-finalize-port-to-v4-lane.md), benchmark and handoff.

Tests used `TMPDIR=/private/tmp python3.13 -B -m unittest`, one module per process:

- `tests.test_finalize_hashes`: **23 passed**
- `tests.test_harvest_window`: **39 passed**
- `tests.test_run_night.NightDriverTests tests.test_run_night.CourierDeliveryBoundaryTests`: **151 passed**

Compile and diff checks passed.

F-M1’s harvest route is confirmed. Member assessment supports parallelism, but the pinned desk caller defaults to one worker; archive hashing remains serial. Four workers improved the synthetic archive experiment **1.82× (45%)**. Real turnaround savings remain unknown.

The [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-fix-finalize/docs/run_reports/2026-11-08-fix-finalize.md) lists all seven changed files and verification details. Next: review the commits, then port after the permitted R1 close and run native `tests.test_run_night`, including `HazardPackPrimitiveTests`, outside this sandbox.