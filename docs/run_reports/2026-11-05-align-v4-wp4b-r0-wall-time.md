# ALIGN v4 WP4b — R0 wall-time reduction, 2026-11-05

Local implementation commit: `610bcb228` (`fix(align): fail fast and record R0 phase budgets`). This report and `answer.md` land in the following `docs: record WP4b R0 scheduling verification` commit. Branch continues `lane/2026-11-05-align-v4-wp4-r0` from clean head `4727f2d01`. No push or merge.

## Intake and authority

Read the supplied/repository AGENTS instructions, CLAUDE conventions, Mission M0, generated stop-card/global-gate intake, targeted current-status/workspace/next-work and queue/do-not-do sections, orchestration guidance, D-050, the current R0 implementation/tests/runbook, and the step-test ruling. No active stop card or global work-selection gate was present. The explicit user WP4b brief selects this bounded [AGENT] work; the historical kernel lane heads were not treated as authorization to do unrelated work.

The owning authority is `/private/tmp/jwsol/v4-plan-synth.md`, its Rulings section, WP4 context, and the final **Ed (2026-11-05): R0 wall time** section. The supplied plan does not name separate readable paths for its underlying CI/merge/gap survey reports; no such paths were invented or followed. No scientific thresholds were re-decided.

Standing overrides: no full suite, network, real study data, external user-directory inspection or native capture; no writes to RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json or tests/test_gen_state.py; no task registration. Shared Git objects and this clone's .git were used as authorized. Only repository code/docs/tests and the supplied plan were inspected. All test backends and filesystem fixtures were synthetic. Temporary fixtures used the preconfigured resolved `/private/tmp/jwsol/v4-wp4b/tmp` root. No subagents, model consults, external integrations or quiet-machine work were launched.

## Changes

- `joulewise/align/r0_runner.py`: canonical selection order is host, disk, load, template, generated, memory, SMC, ladder, long decode. Host identity and backend load remain prerequisites; generated checkpoint receipts retain their original criterion. Caller subset order cannot move long generations before the early checks. A failed check saves JSON/Markdown and unwinds by default; `--keep-going` continues eligible diagnostic checks. Refusals still stop unconditionally. Existing accepted outcomes (diagnostic template/disk, checkpoint required/not_required, ladder pass/fallback) remain accepted; unsuccessful/inconclusive checks still prevent completion.
- The backend closes before SMC to preserve its original unloaded baseline and reloads lazily before later selected model checks. Both load receipts are retained. Cleanup remains in a finally block on failures/refusals. This adds a second model load to the full run; its real cost is unmeasured.
- `joulewise/align/r0.py`: existing xhigh-first/first-pass selection is preserved; lower D rungs are recorded with no episodes and reason `not run: higher rung passed`. Existing long-decode success already stopped after one attempt; the new bounded `max_attempts` control and `--long-decode-attempts {1,2}` allow disabling the metadata retry. Default maximum is two, with the second executed only after a failed verdict. A passing retry still requires actually evaluated metadata to establish mitigation, as before. Exceptions/timeouts continue to fail the check without retry; this is explicitly documented.
- Measured phase `check_seconds` is now saved during progress and on success/failure/refusal. Run `total_seconds` includes setup and cleanup through finalization; serialization of the final report itself is outside that final measurement. Both durations are visible in Markdown. No fake timings are used in production; deterministic test clocks only verify accounting.
- `docs/align/r0_desk_runbook.md`: 3–4 h all-pass target, failure behavior, flags, unloaded SMC baseline, duration fields, and worst-case budget. The full-budget estimate is `(12*4096 + 6*16384 + 2*38912 + 6144 + 3*4096)/10/3600 + 0.5 = 7.27 h`, before prefill, hashing and setup. This is a planning estimate, not measured hardware evidence or a fixed upper bound. Native delivery delays/slow hosts mean the per-unit alarms do not establish a total-run deadline.
- `tests/align/test_r0_scheduling.py`: 12 new tests. Coverage includes reversed-subset ordering, unloading before SMC and reload afterward, ten early failure/inconclusive cases, saved failure reports, keep-going continuation, prerequisite and refusal preservation, SMC-only subsets, deterministic phase/total durations including cleanup, CLI retry configuration, xhigh skip receipts, and one/two decode attempts with separate unchanged deadlines.
- `answer.md`: current handoff prepended; prior WP4 handoff preserved because the earlier run report cites its historical counts.

`scripts/align_r0_checks.py` delegates directly to runner.main, so the new CLI behavior needs no wrapper edit. No backend generation logic, thresholds, seeds, token budgets, SMC profile, or checks' pass criteria changed. The aggregate tool-envelope check still consumes the original load/generated/ladder evidence after those checks; it was not narrowed to early evidence.

## Verification

Each module was run in its own interpreter, sequentially, with **`python3.13 -B -m unittest MODULE`**. Final per-module results:

| MODULE | Ran | Passed | Failed | Skipped | Reported time |
|---|---:|---:|---:|---:|---:|
| tests.align.test_r0_scheduling | 12 | 12 | 0 | 0 | 0.738 s |
| tests.align.test_r0_checks | 28 | 28 | 0 | 0 | 0.493 s |
| tests.align.test_r0_progress | 3 | 3 | 0 | 0 | 0.099 s |
| tests.align.test_r0_integration | 3 | 3 | 0 | 0 | 0.003 s |
| tests.align.test_r0_mlx | 5 | 5 | 0 | 0 | 0.095 s |
| tests.align.test_r0_host | 20 | 20 | 0 | 0 | 0.465 s |
| tests.align.test_r0_step | 12 | 12 | 0 | 0 | 0.493 s |
| tests.align.test_r0_documentation | 3 | 3 | 0 | 0 | 0.001 s |
| **Total** | **86** | **86** | **0** | **0** | **2.387 s** |

Baseline/iterative repeats excluded from that distinct-test total: test_r0_checks ran 28 tests three additional times (1.199, 0.648 and 0.940 s), and the initial scheduling module ran 11 tests (1.057 s) before adding refusal coverage. All passed. Cumulative: 181 passing test executions, 0 failures, 0 skips, 6.231 s reported unittest time. Expected fake CLI `fail:` output exercises a failing synthetic long-decode result; the unittest module itself passes.

Other commands:

- `python3.13 -m compileall -q joulewise tests`: PASS, exit 0.
- `git diff --check`: PASS, exit 0.
- Protected coordination-path diff: empty.
- `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans`: exit 2, `{"error": "PermissionError: [Errno 1] Operation not permitted: 'ps'"}`. Census rows and count are unknown; no clean census is claimed. No escalation or permission bypass attempted.

The full suite and automatic touched/quick expansion were deliberately omitted under the user's bounded-module and machine-load rules. Native MLX/Metal tests were not invoked (rather than recording an unobserved skip). No measurement-Mac checks were performed. No production R0 or block-5 analysis was run.

## Review, limits and next step

Reviewed the local diff against `4727f2d01`; status/outcome bars remain unchanged, all SMC/generation scheduling follows the supplied ruling, and cleanup/failure receipts remain present. Lead independent executing review, native validation and merge authority are outstanding. No cross-model advice or independent verification is claimed.

Next exact step: lead reviews/applies `610bcb228` after WP4 on the integration lane, obtains the planned executing review, reruns the focused modules on the combined head and runs **`python -B -m unittest tests.align.test_r0_mlx_native`** outside this sandbox in the pinned MLX/Metal environment. Lead owns native unload/reload checks, real SMC and R0 wall-time confirmation, and a fresh fixture census outside the sandbox. Live R0 requires a clean session without agents. Linux/CI and Python 3.11 remain unverified here.

Open risks/uncertainties: the 3–4 h target has no live demonstration; full token budgets can exceed the old 6.5 h estimate; loading twice has native cost/lifecycle risk; signal delivery can delay timeouts. Default max_attempts=2 means one ordinary attempt plus one conditional metadata retry, not two unconditional probes. Timeout/exception retries were not broadened beyond the existing failed-verdict path. No new Ed/lead ruling is requested. WP2 default repair, WP10/WP11 launcher/fence/measurement facts and WP14 sensor-policy reconciliation remain lead-owned integration gates; current SMC selections stay PROVISIONAL.

Mechanism yield: focused synthetic tests verify scheduling/receipts/criteria and caught no outstanding code failure; compileall and diff checks caught no issue; fixture census exposed unavailable observation. No prior three-session yield history was adjudicated in this bounded implementation seat. No coordination-state or process-policy changes were made.
