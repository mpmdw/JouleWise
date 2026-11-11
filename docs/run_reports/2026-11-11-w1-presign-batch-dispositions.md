# W1 pre-signing + RL-53 batch + host guard: findings dispositioned

Opus 5.5, interim state-machine lane lead, 2026-11-11. One row per finding from the reviews merged in this PR.

| Source | Finding | Disposition |
|---|---|---|
| Fable armcheck review A-1 (pre-install identification) | Blocking in round 3 | Fixed in round 4 (`c5b87a582`); Fable delta ADMIT |
| Fable armcheck review A-2, A-3 | Unbounded streams; plist template untested | Fixed in round 4 |
| Fable round-4 delta: surviving `deadman_epoch` mutant | Test owed | Briefed into prepare-holds round 1 (`w1-prepare-holds.prompt.md:65`) |
| Fable prepare-holds review PH-1 | W1 and development windows skipped by the hold check | Fixed in round 3 (`785d94436`); Opus ADMIT, 4 of 4 mutants killed. Found unmerged at intake; merged here |
| Fable unstrand review (round 1 findings) | Restore retry, ownership refusal | Fixed in round 2; Fable delta ADMIT |
| Unstrand follower test `test_follow_prints_a_new_launch_transition_without_payload` | Pre-existing timing failure | Deferred: fails identically on the W1 line `b4a6c217f`; not changed here |
| Unstrand native-ps tests (3) under load on the Air | `a chain, driver or window process is still present` | Environment: live chain-like processes from other lanes on the Air; fail identically on `b4a6c217f` |
| batch-tests: four modules repaired, `harvest_off_review_sol2` and others not reached | Partial | `harvest_off_review_sol2` EligibilityTests and `v4_next_arm_packet` ArmOrderWitness repaired in `510ac023a` (same missing `plan_path`); the rest is covered by this PR's CI |
| ci-debt-2 | Three stale expectations | Fixed; Opus ADMIT, 3 of 3 mutants killed |
| Host guard F-1 | launchctl verbs tested through the guard's own set | Fixed (`eac8c2b8d`) |
| Host guard F-3 | Wrappers and shell grouping escaped | Fixed (`eac8c2b8d`); residuals documented in the review |
| Host guard F-4 | caffeinate native witness made synthetic | Accepted; native case moves to the post-install native checks |
| Host guard F-5 | Seat's leak scan incomplete | This PR's CI runs the whole suite with the guard installed |
| Host guard F-6 / NEEDS_RULING | `PYTHONPATH` already used by production | Lead decision, orchestrator concurred: ban only the guard's own variable and site directory |
| Merged tree: ten new command sites from the batch | Allowlist stale after merge | Added with reviewed seams (`53c0f488d`) |
| RL-71 "five acceptance-only codes" | Count needs confirmation | PARKED for the research lead |
| RL-72 `workload.py` callback row | Change not on this branch | PARKED until the follow-up kit lands |
| RL-81 F-1 condition-13 registration test | Signing gate | Open; built by the follow-up kit seat |
| ci-debt-3: watchdog span, s0 enumeration, physics coverage | Pre-existing line CI failures | Stale expectations of admitted commits; fixed in tests/test data (`276d02c02`); Opus ADMIT |
| `tests.test_battery_float_sweep` `topup_log` phase not in `battery_float.PHASES` | Pre-existing; possibly a registration gap | PARKED for the research lead; by reading no classification changes (review `2026-11-11-w1-ci-debt-3-opus-coldreview.md`) |
