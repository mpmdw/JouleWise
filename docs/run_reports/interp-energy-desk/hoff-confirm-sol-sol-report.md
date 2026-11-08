**HOLD.** The four original failure cases are repaired, but an unchanged external alias pointing through a session symlink now fails restore. The prior revision accepted it.

- Added the [confirmation report](/Volumes/JW-EXT/jw-wt/sol-hoff-confirm-sol/docs/align/v4/HARVEST-OFF-CONFIRM-sol.md) and [regression tests](/Volumes/JW-EXT/jw-wt/sol-hoff-confirm-sol/tests/align/test_hoff_confirm_sol.py).
- Verification: **73 passed, 1 failed**, about 101 seconds. The 177-file equality, memo and dwell-order checks pass. Exact commands are in the report.
- Committed locally as `c167ac7e5` on `align/2026-11-08-hoff-confirm-sol`. Tree clean; nothing pushed.

Next: repair staged-namespace link resolution and replay the witness. Native use of this alias layout is unknown; native gates remain pending. The fixture census was unavailable because the sandbox denied `ps`.