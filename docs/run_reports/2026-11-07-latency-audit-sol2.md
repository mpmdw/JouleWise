# Latency audit — independent Sol 2 seat

Task: `latency-audit-sol2`. Branch: `perf/2026-11-08-latency-audit-sol2`, already
checked out and clean at intake. Base: `4e7e878a151d919faf56bb9131af1fcca4b7be75`.
Report prepared November 7; the task's branch date and November 8 dates in
repository records are preserved as labels, not observations made this run.

## Delivered

- [Inventory and ranked fixes](../perf/LATENCY-AUDIT-sol2.md): measurement,
  turnaround, analysis/release, CI, local tests, kits, magistrate and review
  workflows. Durations distinguish MEASURED records from ESTIMATED caps,
  budgets and projections; classifications distinguish physics, design and
  process time. Includes sources, unchanged scientific obligations, weekly
  frequency/ease assumptions, conditional targets and missing measurements.
- [Source-metadata ledger](../perf/latency-audit-sol2-evidence.json): pinned
  source commits, eleven R0 timing records, CI scheduling projections, and
  independently expanded R1 phase-cap arithmetic. No study values.

Main findings:

- Eleven R0 records consumed 3.00 active hours inside a 34.63-hour calendar
  span. Repairs, reviews and scheduling account for much of the gap; it is
  not all recoverable time. SMC-first and the R0-L3 retry/flag change are
  already delivered, so the audit does not claim them as new work.
- The integrated R1 source reproduces 15.61 hours of no-redo phase bounds,
  17.11 with one batch wait, and 25.18 with specified G0 retries and the wait.
  Calibration, harvest and contention redos are additional. These are caps,
  not observed elapsed durations or evidence for a 1–5-hour valid design.
- Hosted BYTES test weights are 9,121.794 seconds. Existing splits project
  a 5,741.949-second floor; splitting the heavy method by world projects a
  3,379.853-second floor, preserving all sixty campaigns. Full-ALIGN ordinary
  work has an ideal twelve-runner lower bound of 49.18 minutes before setup;
  main-only 23-minute estimates do not describe that population.
- Moving the approximately 100-minute desk off the measurement Mac is the
  top availability saving under six windows/week. Numerical weekly savings
  are scenarios, not measurements of workload frequency. Hash/offload,
  generator-only time, production BYTES stage 1 and review queue time still
  need stage timing before a firm target is justified.

## Authority and scope

Read repository AGENTS/CLAUDE conventions, Mission M0, targeted restart,
stop-card/status/workspace/queue sections, orchestration, decision-log
D-186/D-188/D-189, current design amendments and relevant source records.
No active generated stop card was found. The user's audit brief selects this
bounded agent task and expressly overrides coordination-state updates and
the full-suite requirement. No kernel task was registered.

Only this clone's code/docs/Git objects were inspected, including allowed
shared-store Git objects through this clone. Absolute data paths appearing in
records/configs were treated only as text. No real restricted directory,
external user path, measurement data or other latency-audit seat's branch was
opened. No network, model download, measurement, production analysis,
full-suite execution, integration installation, subagent or consult occurred.
No command inspected or changed the running eight-worker job.

Exactly three repository files are delivered: the audit, the evidence JSON,
and this report. No implementation, scientific plan, raw evidence, generated
kit, RUN_STATE.md, TASK_QUEUE.md, state kernel, test_gen_state.py or advisor
status changed. No gate, hardware validation or merge readiness is claimed.

## Verification

- `nice -n 10 python3 -B /private/tmp/latency-audit-sol2-probe.py`: PASS, source
  metadata only; internally measured wall 0.295 s. The temporary script read
  JSON/Git objects and filenames, never imported test or pipeline code.
  Outputs are preserved in the committed ledger; the scheduling method and
  R1 formulas are documented in the audit. This is not a performance test of
  the pipeline or full suite.
- `nice -n 10 python3.13 -B -m unittest tests.test_shard_split.ConservativeUnknownWeightTests`:
  **3 tests, OK, 0.004 s**. This selected class checks unknown-weight policy
  using source JSON and synthetic files; it does not discover/import the
  full test suite. No broader module or suite was run.
- Both `nice` commands reported `setpriority: Operation not permitted` and
  nevertheless executed with exit 0. A successful priority change is not
  claimed. Both workloads were subsecond; no escalation or bypass was used.
- Source/ledger validation: **PASS** for all eleven R0 records, R1 arithmetic,
  CI projection values, local Markdown links and table widths. Protected-path
  diff: **empty**. `git diff --cached --check`: **PASS**. Docs-only work
  does not warrant compileall or a full suite, especially while the blinded
  job runs. No runtime speedup was implemented or timed by these checks.

## Open questions and next exact step

Lead should select F1/F2, verify the actual weekly recurrence and critical-path
dependencies, and commission final-head CI timings after a BYTES split that
preserves all campaigns and aggregate assertions. Existing S7 CI work must
land without importing unrelated unreleased B5 changes. Hash/offload targets
need a synthetic, destination-verified benchmark and interruption tests first.

Actual latest successful R0, integrated R1 phase times, v4 turnaround, storage
throughput, BYTES-stage1/release wall and generator-only cost remain unknown.
The brief's approximate 7,500-second BYTES and 3,400-second MoE figures were
not verified from an exact matching timing record; the audit uses the newer
sourced hosted observations instead. No universal 3–16-hour to 1–5-hour claim
is supported for thermal/registered capture work.

Native MLX/Metal checks remain outside this sandbox and after the current
job, under lead control: the relevant `tests.align.test_r0_mlx_native`,
`tests.align.test_thermal_mlx`, and `tests.align.test_cache_checkpoint_native`
on the exact pinned stack, followed by any authorized quiet hardware gate.
No new MLX code or tests were written. Final lead verification, prospective
design decisions and any merge/push are not this seat's work. This seat's
authorized final action is one local documentation commit; no push.
