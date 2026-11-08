Implemented on `ops/2026-11-08-air-offload`; working tree clean, nothing pushed.

Added the offload client, restricted Air receiver, background second-disk worker, 35 synthetic tests, [operator guide](docs/ops/AIR-OFFLOAD.md), canonical pointer, and [handoff report](docs/run_reports/2026-11-08-air-offload.md). Local deletion requires two verified remote copies. Armed-state, deadline, digest, interruption and recovery checks are covered.

Commits:

- `5e870361b` — implementation, tests and operator documentation
- `247216dad` — verification and deployment handoff

Verification:

- `python3.13 -B -m unittest tests.test_offload_to_air` — **35 passed**
- Targeted `compileall` and Git diff checks — **passed**

No network, hardware, study-data access or full suite was used. Coordination files remain unchanged.

Transfer-only estimates for 18.6–26.4 GB are **6:12–8:48 at 50 MB/s**, **3:06–4:24 at 100 MB/s**, and **1:02–1:28 at 300 MB/s**. Verification adds time; everything must fit within cool-down before a fresh dwell.

Deployment remains **PROVISIONAL**: the lead must integrate the shared lock/lease, provision the Air, and rehearse real SSH/rrsync using synthetic records. Actual throughput and physical disk independence remain unverified. The implemented second-copy path uses a second disk; iCloud confirmation is not implemented.