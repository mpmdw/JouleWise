# Interim fit twin audit after RL-184

Audit round 1 blocked `04f35f2a3`. The regressions below use synthetic fixtures and the auditor's recorded primary outcomes. The implementation remains independent of the primary look code. The three earlier audit reports were checked against their existing focused regressions.

Tested `scripts/cadence_interim_twin.py` SHA-256 `eeb606baebc1c4b177f5b092b0d8ffed98bef8b30a871010060713e5b2e8ac48`.

| Finding | Root fix and regression | Result |
| --- | --- | --- |
| T05 | Thermal hold events validate their timestamps and malformed token metadata fails its leg. The bound child also runs a complete fixture with the missing hold timestamp on every Step 3 fit leg. | PASS |
| T07 | Read the journal start stamp only when there is an integer PM observation to age. With both freshness inputs absent the journal is usable for temperatures and the cell is unestimable. | PASS |
| T08 | Detect positive OS levels only on integer readings. A floating-point level midturn leaves the state cutoff unchanged. | PASS |
| T09 | Validate every pre-cut block's temperature before looking for matched blocks. A singleton with missing TV0h yields a cell failure. | PASS |
| T10 | Read frequency only for states with positive active time. Empty state objects have zero active time. | PASS |
| T11 | Default absent native elapsed to -1 and compare it with rich telemetry inside the pairing window. A mismatch still fails the leg. | PASS |
| T12 | Check the state vocabulary in the turn histogram. A paired out-of-turn frame has no histogram contribution. | PASS |
| T13 | Cut the window input at last token plus 30 seconds. The frequency reference still uses the whole member. | PASS |
| T14 | Validate provided GPU energy and the pre-cut denominator in the after/before diagnostic even when every full block has positive energy. | PASS |
| F03 | A recorded legacy soak with missing, null or failing return code is unaccepted. A legacy receipt with no explicit recorded attempt retains the historical fallback. | PASS |
| F04 | A failed or unfinished blackout wait bars any following attempt. A writer interruption between the final attempt append and its step is an unaccepted attempt. First attempts and retries exercise both cases. | PASS |
| Prior audit findings | Nested bundles and staged overrides, overlapping GPU intervals, dropped delta in main and marked fits and their folds, optional pressure, 4,095-token partial decode, connected GPU gap checks, missing turn index and empty soak arrays. | PASS |
| P01, P02 | The twin frame preserves matching GPU coverage of 1.5 and the two distinct valid Step 3 cell maps. The test parent returns the registered `yes` and `no`. The audited primary parent returned `not_evaluable` for both and needs its own correction. | PASS on twin frame and test parent |
| Private capture | The actual isolated child uses the approved private numeric frame. The outer digit scan and empty outer stderr check pass with the registered decoder and initializer. | PASS |

All 39 focused tests passed with the registered KM003C decoder and initializer. The working-tree diff passed `git diff --check`. P01/P02 production comparator fixes and Astra's paired census rerun remain release checks.
