Committed locally as `f999d99f3` on `ops/2026-11-11-computer-use-mcp`. Working tree is clean; no push.

- D1: Both drag endpoints are hit-tested in Python and Swift. Drags under 3 points execute and log as clicks.
- D2: Parser rejects invalid labels, matches the night prefix case-insensitively, and checks closing-brace indentation.
- D3: README explains why the MBP must keep `respect_remote_armed: true`.

Changed the server, Swift helper, README, two test modules, and [round-three report](/Volumes/JW-EXT/jw-wt/sol-cu-mcp3/docs/run_reports/2026-11-11-computer-use-mcp-r3.md). Timings and protected coordination files are unchanged.

Verification:
- `python3.13 -B -m unittest tests.tools.test_computer_use_mcp`: 69 passed.
- `python3.13 -B -m unittest tests.tools.test_computer_use_mcp_mutations`: all 38 mutants killed.
- In-memory Python compilation and `git diff --check`: passed.

No open implementation questions. Native macOS behavior remains unverified; the lead must build and smoke-test after the concurrent job ends, outside armed/quiet windows. No network, real screen/input, study-data access, or full suite run occurred.