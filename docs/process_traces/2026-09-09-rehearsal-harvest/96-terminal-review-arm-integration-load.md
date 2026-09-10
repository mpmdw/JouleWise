# Magistrate terminal review — ARM-INTEGRATION-LOAD-01 (PR #311), merge candidate 0290311a (9dbacb40 + merge of main 6d55bb96); content head 9dbacb40

Reviewer: headless magistrate, activation 2145630c (Fable), full session context, not delegated. Diff read at the bench in
`/Users/edr/code/JouleWise-wt-arm-load` (`git diff 0fda6d95..17843715`: tests/fixtures/arm_clock.py new; tests/test_arm_readiness_evidence_t0.py,
tests/test_arm_readiness_integration.py, tests/test_arm_readiness_lifecycle.py, tests/test_launch_window.py; production diff empty).

## Forcing defects (primary evidence)

Replays 54 and 83: under four-shard concurrency with 3.3–3.7× timer slack, integration/launch fixtures that sample the live clock
intermittently REFUSE `readiness_clock_preflight_refused` (≤1 ms read skew, ≤5 ms drift predicates at arm_readiness.py:6823–6835), and the
launch-capability race test's eight consumers (~91 s CPU) overran `join(timeout=30)` before any property assertion ran. Consult 99gn
(option (a), selected by the T38c directive) and cold gate 56 ADDENDUM-2 / Opus refuter 57 (the timeout branch recorded no discriminating
evidence) are the lane's authority.

## Design-level questions (row 7)

1. **Observation seam or predicate mock?** Seam. `coherent_clock_anchor` returns a ClockAnchor with specified RAW/REALTIME/skew; every
   predicate (`_predicate_passes`, `_clock_probe_predicate_passes`), threshold, binding and deadline is untouched production code, and the
   new subTests prove it with one-nanosecond counterfactuals: PASS at skew 1_000_000 / drift 5_000_000, REFUSE at 1_000_001 / 5_000_001
   with `reason_codes == ['readiness_clock_preflight_refused']` and the row verdict — a PASS-returning mock could not produce that pair
   (Opus 90 §1; Astra 89 in-memory predicate probes).
2. **Any live sample left on the audited path?** The seams replace `_sample_live_clock_anchor` / `clock_reference.sample_anchor` in the
   parent and the subprocess (the fixture is carried into the copied repository because production executes a focused unittest suite by
   test id inside it — `joulewise/arm_readiness_evidence.py` `_execute_unittest_suite_subprocess`; Opus 90 SF-2 proposed dropping the copy
   and execution refuted it: 'focused suite could not be loaded'). Machine readiness is NOT proven by synthetic anchors — the docstring says
   so; live validation stays gated on a quiet machine (99gn).
3. **Race test.** The exactly-one-consumer property, the O_EXCL linearization point and the 30 s join are unchanged; each consumer still
   re-runs GO admission, ARM verification, receipt re-read, binding reconciliation and the real go_bounds deadline before the claim (Opus 90
   verified per clause); only the caller-side assembly of immutable launch inputs is done once (measured CPU 96.1 s → 59.1 s). The timeout
   branch now records alive count, named threads, completed consumers, execve.call_count and partial outcomes (refuter 57's asks).
4. **Far-future REALTIME offset.** Admissible because every consumer compares REALTIME − MONOTONIC_RAW (arm_readiness.py 6782–6788 and
   6828–6835; arm_readiness_evidence_t0.py 1166–1171; t0_rehearsal.py 643–644); no predicate reads absolute realtime against now (Opus 90
   §4; N-2 recorded in the docstring). Prophylactic N-1: the fixture takes the seam's positional argument so a side_effect patch cannot
   TypeError into a fail-closed refusal.
5. **Refusal criteria (kernel row).** No relaxed thresholds, no retries, no skipped rows, no deleted tests (184 → 187 methods), no
   production switch, no env var read by production (grep clean).
6. **What is NOT proven here.** Under-load determinism evidence from the seat's brief (burner run) was never produced (seat 85 timed out at
   report capture); the four-shard replay on the integration tree is the evidence of record (row 9) and the ruling-56 ADDENDUM-2
   observation for the race test.

## Overbuild / merge-ability prune (row 8)

Nothing to prune: one 30-line fixture, seam wiring in four test modules, three added tests, the evidence-recording join branch. The deleted
block that rewrote captured R0 evidence bytes post hoc is a soundness improvement (Opus 90).

## Fix rounds (at the bench)

Round 1 (17843715; Opus 90 SF-1/N-1/N-2 applied; SF-2 applied then REVERTED on execution evidence with the rationale in the comment).
Delta 95 (Astra): clean; same signature: none.
Linux CI at 0661d1d2 then ERRORed `test_specified_census_observations_refuse_before_publication` (`T0EvidenceAuthoringError: clock-reference
command capture fields are invalid or stale`) while the Mac replay was green. Root-cause consult 99 (Astra high, before any fix): the
integration class froze ordinary time at the HOST `time.monotonic_ns()` and the census fixture subtracts `_MIN_IDLE_NS` (600 s), so a fresh
runner (< 10 min uptime) drove `started_monotonic_ns` negative; the synthetic RAW anchor was not the failing comparison. Round 2 (9dbacb40):
setUp freeze = `coherent_clock_anchor().monotonic_raw_ns`; regression `ArmReadinessIntegrationClockPortabilityTests` runs the complete census
test under simulated host readings 1e11/5e11/8e11/5e14 (the first two failed before). Delta 101: clean; the host-calibrated class is
closed in this lane's integration path; consult 99's three extra T0 refusal tests are a recorded coverage follow-up (helpers exist). CI green
on 9dbacb40 (run 34412303408).

## Bench execution (lead)

Focused modules `test_arm_readiness_integration + test_launch_window + test_arm_readiness_lifecycle + test_arm_readiness_evidence_t0`:
187 tests OK (1 skipped) at 6881709d (1305 s) and again at 17843715 (1351 s).

## Replay (row 9)

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4` in
`/Users/edr/code/JouleWise-wt-arm-load` at 0290311a (contains origin/main 6d55bb96), started 15:52:41 PDT, alone in-process (four shards
concurrent; no seat, reviewer or other test process launched by this session; timer probe 3.41× at start). Verbatim (102-replay-311-final-0290311a-tail.txt):

```
WORKERS SUMMARY shards=4 modules=221 tests=5650 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```

Replay 1 at 0661d1d2 (97): 5649 tests rc 0 (before round 2).

## Verdict

CLEAN for merge at 0290311a: refuters 89 (Astra execution) and 90 (Opus contract; 0 blockers); two fix rounds each delta-audited (95, 101,
both clean); root cause of the Linux CI failure established by consult 99 before the fix; CI green on 9dbacb40 and to be confirmed on the
merge head; full-suite replay alone rc 0 with zero failures twice (5649 at 0661d1d2, 5650 at 0290311a). Not proven: live machine readiness
(synthetic observations by design, per 99gn); the seat's burner-run evidence was never produced — the four-shard replays are the evidence
of record.

## Addendum (2026-09-09 ~17:05 PDT, consistency sweep 106 F4)

Counts at the final content head 9dbacb40: 184 → 188 test methods (four added: the two integration refusal/skew tests, the launch-window subprocess test, and round 2's ArmReadinessIntegrationClockPortabilityTests); tests/fixtures/arm_clock.py is 37 lines after N-1/N-2. The prune section's "three added tests" and "30-line fixture" describe 6881709d.
