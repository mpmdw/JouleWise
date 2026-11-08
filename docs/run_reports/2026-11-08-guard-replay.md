# Guard-replay handoff — 2026-11-08

Implemented on the task branch `ops/2026-11-08-guard-replay`, initially clean at
`dcfa4c59351615cdf3879a0ef68c5800f56f53a7` (origin/main). Local commit only; no push.
The commit containing this report is identified by
`git log -1 --format='%h %s' -- docs/run_reports/2026-11-08-guard-replay.md`.

## Scope and intake

Mission M0: read repository AGENTS/CLAUDE, the inactive stop card, status/workspace/
restart pointers, queue/do-not-do-yet sections, playbook, source map, orchestration,
Quiet Guard contract, and targeted D-009/D-161 authority. Ed's explicit guard-replay
request selects this AGENT task ahead of normal queue work. His standing rules
override coordination-state updates and the canonical full-suite instruction.
RUN_STATE.md, TASK_QUEUE.md, state_kernel.json and tests/test_gen_state.py were
preserved, with no task registration. No delegates, cross-model consults or
network tools were used.

Reads stayed in the clone and committed repository Git objects (including the
permitted shared object store). No real restricted directory, sealed Block-5
outcome, external study/archive/custody path, measurement pipeline or model weight
was opened. Receipt locators were text only. No live recorder, native host probe,
window, installation or configuration change was started; the existing job was
not controlled. Production guard files are unchanged.

## Deliverables and files

- `joulewise/guard_replay.py`: virtual Tape/Decision protocol; imported historical
  QuietGuard and SMC rules with neutral non-CPU samplers; raw-counter CpuQuietProbe,
  current contention arm/request, display and thermal adapters; run-level rates,
  95% Wilson intervals, explicit unsupported/unmeasured/incomplete coverage, source
  hashes and conservative qualification screen. Historical dependencies must match
  executable ASTs; immutable code blobs are cached, guard instances are fresh.
- `joulewise/guard_replay_corpus.py`: explicit local-Git receipt/fixture projection.
  Mixed-report numeric tokens are opaque until selected as host fields. No arbitrary
  check output or data locator is retained/followed. Fixture revision is pinned.
- `scripts/guard_replay.py`: collect/list/run CLI, no-follow clone-local corpus reads,
  generic trusted repository adapter import, optional qualification exit status.
- `tests/test_guard_replay.py` and
  `tests/fixtures/guard_replay/synthetic.json`: synthetic regression, positive controls,
  boundaries, clock/startup scheduling, union/gap accounting, missing observations,
  scope/source checks and coverage qualification tests.
- `docs/process/GUARD-REPLAY.md`: pinned file:line inventory of host-state refusal
  families, replay requirement, proposed5% per-run idle bound, corpus limitations,
  adapter contract and idle-MBP recorder specification with explicit cost limits.
- `docs/process/guard_replay/corpus.json`, `recorded-report.json`, `synthetic-report.json`:
  reviewable host-only evidence and exact source/corpus/implementation provenance.
- This dated handoff report. No advisor-visible scientific status changed.

The local main tree lacks ALIGN implementation files; historical adapters import
the original definitions from pinned local kit commits rather than adding or
altering those guards. prewindow dependencies are byte-identical; contention
dependencies differ only in comments, with executable AST equality checked.

## Findings

Twelve matching records refs yielded eleven committed reports, 546 census frames
and six SMC CPU diagnostic dictionaries (552 frames total). Rerun11 has a NOTE
but no committed report at the expected path. The separate FakeMac fixture
stratum contributes41 contention intervals and84 thermal readings. The bounded
R0 records inventory found only SMC journal digests in rerun5/6/7, with no raw
SMC journal or full display timeline. Absolute locators were never followed.

Selected, Ed-labelled engineering-benign incidents give:

| Imported predicate | Refusals | Descriptive95% Wilson |
|---|---:|---:|
| pre-#691 QuietGuard | 2/5 (40%) | 11.8–76.9% |
| pre-#691 SMC admission | 1/1 (100%) | 20.7–100% |
| pre-R0-L3 SMC admission | 3/3 (100%) | 43.9–100% |
| R0-L3 SMC redo | 0/3 | 0–56.1% |

Both requested old-rule regressions are ABOVE_BOUND. These are sparse,
failure-selected CPU decisions, not estimates from independent complete idle
runs. Other attempts stay unlabelled. Neutral custody/agent/LaunchAgent samples
mean the historical CPU report does not validate the rest of the census.
Synthetic controls still detect sustained single-process contention, display
wakes and OS thermal pressure. No guard is qualified for a live run by this corpus.

## Verification

Final focused commands, one module at a time:

| Command | Result |
|---|---|
| `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.test_guard_replay` | 34 tests PASS,8.298 s final rerun |
| `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.hazards.test_contention` | 48 tests PASS,3 live tests skipped,5.942 s |
| `python3.13 -B -m compileall -q joulewise/guard_replay.py joulewise/guard_replay_corpus.py scripts/guard_replay.py tests/test_guard_replay.py` | PASS |
| Documented collect + recorded/synthetic replay commands | PASS; requested historical regressions flagged |
| Repeat collect and compare canonical JSON bytes; verify report corpus/implementation hashes | PASS, byte-reproducible |
| Recorded replay with `--run-seconds 23400 --require-qualified` | exit2, expected insufficient representative coverage |
| `git diff --exit-code -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py` | PASS, protected paths unchanged |

An early synthetic test exposed missing injected receipt metadata in my L3
adapter; corrected without changing the guard. One follow-on test command was
launched before collecting the previous exec's completion; final module checks
were repeated sequentially. Cumulative focused test time remained well below
20 min. Full suite and pytest were not run, per Ed's explicit restriction. No
MLX code changed or MLX import attempted. Python3.11 execution is deferred to CI;
the implementation uses stdlib APIs available there.

## Uncertainty, native checks and exact next step

The5% bound is a proposal requiring lead acceptance. Its per-whole-run rationale
and zero-failures73-independent-runs Wilson requirement are documented. A sparse
passing trace, synthetic label or missing input cannot earn qualification.
Labels mean engineering-benign as directed by the brief, not proof of zero
physical load. Wilson intervals on selected/correlated incidents are descriptive.

Full battery/night/external-volume/privileged-census/ALIGN thermal-session
adapters and representative observations are not delivered as passing claims.
The generic injected adapter interface supports adding them; the inventory names
their seams and missing coverage. The recorder is specified, not implemented or
installed. CPU/RSS/storage budgets are proposed limits, not measured performance.
The external-volume code inspected in the kit calls its activation a draft;
this task does not resolve or activate that authority.

Next: the lead reviews this diff and bound, then commissions the specified
model-free recorder overhead check and independently labelled, non-overlapping
run-length corpus **after** the current job and agent load have ended. No new
live gate should be approved solely from this report.

Native sampler parity remains for a clean, lead-controlled Mac outside this
sandbox. With `JW_B5_SYNTHETIC_ONLY` unset and `JW_LIVE_HW=1`, run these individual
tests one at a time, when no measurement/analysis job is active:

```sh
JW_LIVE_HW=1 python3.13 -B -m unittest tests.hazards.test_contention.HostAggregateTests.test_live_host_ticks_read_without_privileges
JW_LIVE_HW=1 python3.13 -B -m unittest tests.hazards.test_contention.PsFormatTests.test_parse_equals_parse_ps_on_live_ps_output
JW_LIVE_HW=1 python3.13 -B -m unittest tests.hazards.test_contention.PsFormatTests.test_live_snapshot_parses_and_this_process_is_in_the_tree
```

These are necessary sampler parity checks before using newly recorded raw
counter traces; they are not a substitute for representative guard replay or the
recorder cost check. No MLX-native test is required by this change because no
MLX/model implementation was modified.
