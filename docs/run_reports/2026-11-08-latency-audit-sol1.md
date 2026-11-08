# Latency audit sol1 — source-only handoff

Date: 2026-11-08 UTC. Branch: `perf/2026-11-08-latency-audit-sol1`.
Starting tree was clean on that already provisioned branch, at
`4e7e878a151d919faf56bb9131af1fcca4b7be75`. No branch belonging to the other
latency-audit seat was inspected. No delegation or external consult was used.

## Delivered

- [LATENCY-AUDIT-sol1.md](../perf/LATENCY-AUDIT-sol1.md): 47 inventory rows,
  26 source entries, ranked fixes using explicit weekly-cadence assumptions,
  prospective design investigations and outstanding timing measurements.
- [LATENCY-AUDIT-sol1-evidence.json](../perf/LATENCY-AUDIT-sol1-evidence.json):
  fixed Git revisions and source SHA-256s, recorded CI weights, pure R1 phase
  bounds, SSD schedule decomposition and metadata-only CI packing projections.
- This handoff report. No production code, tests, coordination state, decision
  log, measurement artifacts or advisor-facing status changed.

Audit/evidence commit: `743dca54d` —
`docs(perf): inventory pipeline latency and rank process fixes`.
The subsequent handoff commit contains this report; local Git history records
its exact SHA. Nothing was pushed.

## Findings

The strongest recurring opportunities are the CI simulation/fixture bottleneck
and terminal desk/harvest. Hosted timing metadata reports BYTES analysis at
9,121.794 s, including a 5,741.949 s indivisible method. The pending split alone
therefore leaves a 95.7-minute floor. The audit's 55–65-minute CI target requires
further independent campaign/fixture work, not just more shards. Two ALIGN
terminal desks took 98 and 103 minutes; their proposed 30–45-minute target still
requires a stage profile and full equivalence checks.

R1's 56,206.96 s no-redo figure is reproduced schedule arithmetic, excluding
brackets and harvest. With one batch wait it is 61,606.96 s; with all listed
G0 retries and that wait, 90,662.94 s. These are bounds, not observed walls.
The SSD's 6.83 h is also a planned schedule: 2 h of gaps, 50 min settling,
2 h idle observations and 2 h decode guesses. Shortening acquisition, gaps or
registered warmups/idle requires the lead's prospective design decision.

Existing R0 ordering, display and contention fixes, the earlier ~37 h → 100 min
analysis improvement, parallel release input hashing and adaptive thermal
gates are explicitly identified as existing work. They are not counted again as
new savings. Same-Mac offload during acquisition remains inadmissible under
the current external-volume/quiet rules.

## Verification

Commands were run one at a time; no full or quick suite ran.

1. `nice -n 10 python3.13 -B -m unittest tests.test_shard_tests.NestedPackageDiscoveryTests tests.test_shard_tests.ShardExitStatusTests`
   — **PASS: 3 tests, 0.005 s**. This is a small synthetic runner check, not
   whole-suite or native hardware evidence. The broad discovery invariant
   class was deliberately excluded because it imports every test module.
2. `nice -n 10 python3.13 -B -` with a source-only arithmetic script — **PASS**.
   The script reads fixed-revision code/timing text with `git show`; it parses
   the R1 driver AST, selects only `phase_plan`, `rearmed_member_bound_s`,
   `segment_bounds`, `release_segment_bound_s`, `aba_leg_bound_s` and
   `night_worst_case_s`, removes imports from those selected functions and
   supplies the source config's literal caps (1,500 / 1,200 / 1,580 s), contract
   kind sets and factor 1.13544. No runtime module or data reader is imported.
   It sums SSD defaults and uses deterministic longest-first packing over
   tracked test-module names and the CI timing map. The JSON stores the exact
   phase rows, revisions and results. The projection does not execute test
   discovery, establish split addressability, or prove new split independence.
3. `python3.13 -B -` with document/evidence assertions — **PASS**: all 22 local
   links resolve within this clone; all 26 source identifiers resolve; all 47
   inventory rows have consistent table columns and duration labels; R1 phase
   sums, wait/retry arithmetic, SSD total, source hashes and rank-1 arithmetic
   agree. The R1-lane projection finds 594 modules / 592 ordinary and explicitly
   lists 27 untimed modules assigned the conservative 26.98 s weight.
4. `git diff --cached --check` — **PASS** before the audit commit.

The sandbox printed `nice: setpriority: Operation not permitted` for both tiny
commands; they continued and completed. No claim of reduced scheduling priority
is made. Total executed unittest time was 0.005 s, far below the brief's budget.
No MLX/native test ran, and none is needed for this docs-only change. Relevant
later native qualification modules are listed in the audit for the lead.

## Boundaries, uncertainties and next step

Only this clone's source and allowed Git objects were read. Runbooks containing
absolute paths were read as text; none of those paths was followed. No network,
model download, real measurement-data reader, Block-5 pipeline, active-job
inspection/control, external-volume operation or measurement command ran.
The user-owned `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json` and `tests/test_gen_state.py` are unchanged;
no kernel task was registered, as required by the brief.

Weekly counts and most proposed new durations are estimates, not recovered
facts. Standalone hashing/offload/finalisation, kit generation, actual complete
R0/R1, live release stages, BYTES fit/export and a current comparable full-local
suite still need timing. The brief's ~3,400 s MoE figure was not substantiated;
the inspected hosted weights are ~1,377–1,451 s. Different hosts/trees and
partial failure paths are not equated. These limits are explicit in the audit.

No blocker prevents reviewing this inventory. **Next exact step:** the lead
compares the independent audits, then selects rank 1's CI timing/campaign work
and rank 2's synthetic desk stage profiling for bounded implementation. Any
change to scientific timing, state admission, replication, model precision,
blinding or custody requires the authority identified in the audit; this
report installs no such ruling.
