# Round 10 Astra audit, Builder D

The explicit Builder D assignment selected this desk work. Mission M0 found
no active stop card. The branch starts from main at
`2f82fb8f164993511f7d557844a8cd0638c6b052`. That base already regenerates
the earlier stale CURRENT pointer to item 394.

| Audit item | Implementation | Regression evidence |
| --- | --- | --- |
| Astra ops 9 | `805617dba` | Failed notifier CLI status and persistent NOTICE/ALARM retries in `tests.test_air_watch_agent`. CI and watcher exit alarms also stay pending until delivery. |
| Astra ops 12 | `3ab533d55` | `tests.test_gen_current.RenderTests` rejects reordered pointer collisions and heading collisions, and accepts only the commit-qualified historical 387 pair. |
| Astra design 2 | `6cec8ffcc` and `3babaf05a` on the main PR, `bdb1d232f` on W1 | On the old F0 pin, the new `tests.align.test_rl145_part_c.EvaluatorFailureTests` cases pass malformed evidence through the verdict. On the candidate, they refuse missing, duplicate or unreleased G1 records and understated durations, including missing or inconsistent evidence when X_G runs. The main suite exercises the identical gate logic in `tests.test_part_c_gate_evidence`. |
| Astra ops throughput 3 | `d0ad35088` | `tests.test_magistrate_watchdog.StopAndDecisionTests` checks one advertisement with the exact positive control and matching stop refs. `tests.test_magistrate_watchdog_span` checks the in-flight fence crossing. |

The focused Python 3.13 checks cover the Air watcher, the state generators,
the watchdog and the Part C evaluator. The regressions reproduced failures
before the implementation changes. The real-process watchdog CLI module
was excluded from local testing. Evaluation used synthetic facts and fake
transports. The end-of-work fixture census could not obtain a process
snapshot because the runner denied `ps`. The first final-head CI attempt caught the new
test module's missing shard timing entry. Both branches now register its
standard pending-hosted-timing exemption in `scripts/test_timings.json`.

## Standing F0 rebind

RL-145 addendum §6 and RL-149 §1.2 require the G1 release samples and a duty
budget verdict. The workload at
[`b2e01464d`](https://github.com/mpmdw/JouleWise/blob/b2e01464d6d4fbf2901ff4d4154df9455104a12a/joulewise/align/apple/workload.py#L545-L552)
calls G1 before each later turn. The rebind requires exactly one released
G1 at each such admitted index, checks the recorded G0/G1/H seconds against
the episode-monotonic interval bounds, and uses the reconciled durations
for the existing 40% test. The episode's own-stop exception stays in the
existing evaluator and the released G1 requirement still applies to every
later D_bank turn that actually ran. When X_G runs, its later turns also
need one G1 record and reconciled timing. Its no-timeout rule still accepts
the workload's unobserved outcome.

Main carries the same evaluator source as the W1 candidate. The next
STANDING-F0 renewal should move from `b2e01464d6d4fbf2901ff4d4154df9455104a12a`
to `4d7dd28cc93bb02f6f6782dacd7af04abd6eda8e` on the W1 line after lead review
and admission. Candidate tree `39a465bdf30da9b05c889b4cff882b837326c1a1`.
The evaluator SHA-256 moves from
`b2c91c77ef9f1c227c5c172690fadf5f36cff22b4874d0eeaa66798ca9ef12b8` to
`238ab79c72e2540ff2ce0522b6bf6864bca9602fa94685fc082c9d999907cfe3`.
It is the sole executable path changed on the candidate. Item 346's
W1-head and renewal checks still govern adoption. Lead-owned review, the
applicable source binding, W1 CI and the renewal remain pending.
