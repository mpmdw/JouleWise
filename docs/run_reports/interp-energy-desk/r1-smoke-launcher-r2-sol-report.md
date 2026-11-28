Implemented and committed locally on `ops/2026-11-11-r1-smoke-launcher`. Working tree is clean; no push.

- `4c27eba47` — launcher fixes.
- `a695857f6` — round-2 report.

A/B caps are now 1,920/4,520 s, with B derived from runtime budget arithmetic. Added deadline admission, foreign-marker protection, boundary-only volume census and the requested LOW fixes. R0 bytes, its 5 s terminate wait, protected sources and coordination state remain unchanged.

Changed: both launcher scripts, R1 tests, refusal/host-command inventories and the [report with all 43 refusal keys and guard digests](/Volumes/JW-EXT/jw-wt/sol-r1-smoke-launcher-r2/docs/run_reports/2026-11-11-r1-smoke-launcher.md:138).

Serial verification used `nice -n 10 python3.13 -B -m unittest MODULE`:

| Module | Result |
|---|---|
| `tests.align.test_r1_smoke_launcher` | 36 passed; 14 mutants killed |
| `tests.test_magistrate_desk_fence` | 42 passed |
| `tests.align.test_r1_followup` | 12 passed |
| `tests.test_host_command_sites` | 2 passed |
| `tests.hazards.test_refusal_allowlist` | 2 inherited failures, 1 skip; all owned keys match |

Compileall, condition 13 and diff checks passed.

Caveats: the sandbox denied `nice`’s priority change. An initial fixture invoked read-only `ps`; that callback is now faked. Startup-margin and terminal-census timing limits are documented.

Next: lead review, RL-86 reconciliation, then the agent-free native A/B smoke using the documented 9,000 s deadline. Native MLX/KM003C and sampler/Tf08 validation remain owed.