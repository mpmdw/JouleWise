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


## Part C fail-closed fixes

2026-11-18, Sol builder for interim lead b7aad16d. **Partial: timeout hole
fixed; unreadable-X_G hole blocked on WRITE_SCOPE.** Merged `origin/main`
`2f9e8b6f6` first, merge commit `7cb6eb95a`. The merge was automatic,
including `scripts/gen_current.py`: PR #809's duplicate-pointer/heading
refusals and exact historical-387 exemption coexist with PR #810's typed
open-items projection. No manual merge-resolution edits were required.

The shared no-G1-timeout check now fails on either an interval timeout or
`thermal.gate_timeout` / `thermal.gate_timeout:<turn>` in episode_flags,
including a timeout on the next, unadmitted turn whose interval is absent.
Missing G1 evidence at an admitted index also fails this check rather than
printing no timeout. The writer is `ThermalSession.wait` in
`joulewise/align/apple/thermal_gates.py:624-625` at F0 `b2e01464d`;
`workload.py:664` copies its flags into the episode. G0's
`thermal.start_gate_timeout` and H's `thermal.hold_timeout:<turn>` retain
their distinct meanings. No tolerance, threshold or pass bar changed.

Regression evidence (all test invocations set `JW_B5_SYNTHETIC_ONLY=1` and
`PYTHONDONTWRITEBYTECODE=1`):

- Before: `PartCEvaluatorTimeoutTests.test_flag_only_timeout_on_next_unadmitted_turn_fails`
  ran through the real `evaluate` with three clean admissions and only
  `thermal.gate_timeout:3` recording the failed next G1. Both D_bank and
  X_G subtests FAILED: `AssertionError: True is not false`, verdict pass.
  The evaluator after the main merge was byte-identical to `bc4671106`
  (SHA-256 `238ab79c72e2540ff2ce0522b6bf6864bca9602fa94685fc082c9d999907cfe3`).
- Explicit baseline replay also loaded `git show bc4671106:scripts/align_r1_part_c.py`
  into an in-memory module and reran that test: 1 test, 2 expected subtest
  failures, no errors. For this replay, real `turn_check` and `stamp_fresh`
  code and their constants were AST-extracted in memory from immutable F0
  `b2e01464d6d4fbf2901ff4d4154df9455104a12a`; no W1 files were added.
- After: the same regression PASSED for both roles, with other_failure
  and the named timeout flag. The complete Part C module passed all 6
  tests both with those real F0 helpers and in main's synthetic world.
  Coverage also includes bare flags, interval-only timeouts, missing G1
  rows, and clean released/unobserved X_G evidence.
- Final scoped command:
  `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_part_c_gate_evidence tests.test_gen_current -v`
  — 61 tests PASS (6 Part C, 55 generator). `rg -l align_r1_part_c tests`
  found only `tests/test_part_c_gate_evidence.py`; no other existing Part C
  evaluator test module exists on this branch. Full-suite execution is
  left to CI, per the assignment.

The clean-shape assertion uses production-shaped synthetic facts through
all real Part C checks. Main lacks the W1 `align_r1_rehearsal` and
`rl145_prints` imports, so the standalone tests supply narrowly constrained
clean-input doubles for those two helpers only; the additional replay
above used their real F0 implementations. The nine real F0 bundles are not
available in this checkout and were not re-evaluated. This is synthetic
verification, not live validation.

**Scope blocker for hole 2:** F0's
`scripts/align_r1_followup_kit.py:521-535` records X_G in members, then wraps
both invocation and fact extraction in one catch. A read/parse failure
becomes the same `x_g=None, x_g_not_run_reason=...` evaluator arguments as
a genuinely unrun X_G. `evaluate` receives no run directory, runtime result
or ran bit. That runner file is absent from this PR branch and is outside
the exhaustive WRITE_SCOPE. It has not been added or modified. Scope was
requested for that exact path; no permission has yet been received.
An evaluator-only error-string heuristic would guess which runs count,
so it was not used. Hole 2 remains unfixed and has no pass-after claim.
The next step is the lead's scope expansion / runner-line assignment,
followed by an explicit ran/evidence-error handoff and a real-evaluator
regression for unreadable or malformed completed X_G evidence.

Decisions made: use one timeout-source check for D_bank and X_G; keep raw
flag evidence separately from interval-derived timeout-turn indices;
retain X_G's unobserved outcome; do not infer run status from exception
text. NEEDS_RULING: none on data-counting or printed-number policy; the
outstanding request is file-write authority only.

Final hygiene: `git diff --check` PASS; fixture orphan census
`python3 scripts/fixture_orphan_census.py --fail-on-orphans` returned
`[]` (0 rows), exit 0.
