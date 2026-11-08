Completed on `receipts-fix`; working tree clean, nothing pushed.

- Commits: `a25c77966` merges latest local v4 r11; `ed9fd3ca1` applies fixes; `bec6c8ae3` records handoff.
- Fixed event ordering, driver journal ownership, closure/lint, reader attribution, and requested turnaround/dwell markers.
- All 20 synthetic bundles validate with zero structural problems. Cross-tree capture and desk comparisons pass; unattributed in-member time is ≤1 ms.
- Fifteen targeted modules pass. Three night-driver process-group failures also reproduce on untouched `1a2574b49`. Compile checks pass; no full suite ran.

[Run report](/Users/edr/code/CapstoneProject/jw-wt/sol-receipts-fix/docs/run_reports/2026-11-08-receipts-fix.md) lists every receipt-bound file, test command/result, and limitations. Delta review, STRICT re-registration, and native checks remain lead gates. Coordination files are untouched.