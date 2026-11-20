Committed locally as `6a3899361` on `fix/2026-11-10-agent-identity-flake`. Working tree is clean; no push performed.

- Restored F1’s foreign-group orphan fixture and verified it kills the mutant.
- Replaced live sleep fixtures with ready-signaled Python waiters; readiness failures now fail and clean up.
- Corrected the diagnosis and desk-report links.

Verification: **50/50 serial and 50/50 concurrent runs passed**, each with 13 passes and the existing sandbox `pgrep` skip. Compile, cleanup fault checks, and diff checks passed.

Ubuntu-26.04’s multicall hypothesis remains unverified. Native Darwin ancestor coverage and Python 3.11 validation remain for the lead.

Changed files, commands, receipts, and next steps are recorded in the [round-2 report](/Volumes/JW-EXT/jw-wt/sol-flake-r2/docs/run_reports/2026-11-10-agent-identity-flake-r2.md).