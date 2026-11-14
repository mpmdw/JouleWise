Applied RL-41/RL-42 and committed locally on `analysis/2026-11-10-b5-rederivation-p1-seat4-p3`.

- **Print authority:** `0b8763f0a`
- **Report commit:** `cea22ea8b`
- **Counts:** 261 exact + 256 within-rounding = **517**; 6 recorded-judgment; 14 single-source; 1 MISMATCH; **538 total**.

Updated the ledger, hand-check table, REDERIVATION.md, both readers, and focused tests. Added `paper1` and rounded residuals to two significant figures.

Verification passed:

- `python3.13 -B -m unittest tests.b5_analysis.test_hand_check_phase2` — **18 tests**
- Both readers with `--repo-only` — table equality, residuals, counts and placement checks passed
- Compilation and Git whitespace checks passed

Custody arithmetic was **not rerun**; no custody access, network, full suite or push occurred. Worktree is clean.

[Full handoff report](/Volumes/JW-EXT/jw-wt/sol-p1-seat4-p3/docs/run_reports/2026-11-10-p1-seat4-p3.md) records the full authority SHA and limitations. No count discrepancy remains. Next: the lead records that SHA in the gate ledger and gives Ed RL-42’s history notice.