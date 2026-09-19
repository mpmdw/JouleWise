```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All ten original counterfactuals are fixed; two follow-up findings concern Markdown group identity and passing-suite runtime. Both 44-test runs passed, and all eleven mutations were killed.",
  "workspace": {
    "base_requested": "46d310eba1fa43a5ca898364302db90392fcd757",
    "base_mode": "exact",
    "head_start": "46d310eba1fa43a5ca898364302db90392fcd757",
    "head_end": "46d310eba1fa43a5ca898364302db90392fcd757",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 1},
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "summary": "Markdown summary omits the newly required boot/build group identity.",
        "call_site": "scripts/sample_quiet_predicate_evidence.py:1065-1077",
        "counterfactual": "Two idle rows with identical repeat/census condition, boot A at 1 W and boot B at 9 W, produce separate JSON groups but indistinguishably labelled Markdown rows.",
        "recommendation": "Render boot_id and available os_build in all three Markdown tables and pin their identity with a regression."
      },
      {
        "id": "R2",
        "severity": "nit",
        "summary": "The passing module now unconditionally consumes the full five-second cleanup grace in its injected stuck-child regression.",
        "call_site": "tests/test_sample_quiet_predicate_evidence.py:652-671; scripts/sample_quiet_predicate_evidence.py:925",
        "counterfactual": "On correct HEAD, the rendezvous test takes 7.421370 s versus 0.001564 s before the round; its exit_delay=60 subtest spends 5.002057 s in join(timeout=5).",
        "recommendation": "Consider deterministic escalation coverage while retaining the real one-second clean-exit regression and the production five-second grace."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit4-232/bench.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tracked_files_checked 8053 byte_changed []",
          "status_identical True",
          "All 11 mutations killed; worktree byte-identical."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "All 11 mutations killed; worktree byte-identical\\."}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit4-232/timing.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 45 tests in 5.776s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit4-232/edge_probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "E7 unused imports []",
          "E7 top-level callables without internal Name use []",
          "EDGE PROBES PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "EDGE PROBES PASS"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit4-232/final_checks.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["real_load_ast_identical True", "FINAL CHECKS PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "FINAL CHECKS PASS"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This bounded delta review ran the requested module, probes, mutations and timing comparisons; canonical full discovery was not run.",
      "needs": "Lead completes the downstream full sharded replay required by record 13a."
    }
  ]
}
```

## Findings

**R1 — should_fix: Markdown loses the new group identity.** At [the summary renderer](/Users/edr/code/JouleWise-wt-reaudit4-d0b83820/scripts/sample_quiet_predicate_evidence.py:1065), all three tables still identify groups using only state, repeat and census condition. Executed counterfactual:

```text
| idle | 1 / True | cpu_w | 1 | 10 | 0 | 9.6 |
| idle | 1 / True | cpu_w | 9 | 10 | 0 | 9.6 |
```

These rows belong to different boots. JSON correctly emits `boot_id: A` and `boot_id: B`; Markdown emits neither identity. The same omission affects OS-build splits. Thus S5’s original pooling defect is fixed, but its newly separated groups are ambiguous in the human-readable output. Add the identifying columns and a rendering assertion. Evidence: [edge probe log](/tmp/jw-reaudit4-232/edge_probes.log).

**R2 — nit: the passing suite waits through the entire production grace.** The [expanded rendezvous test](/Users/edr/code/JouleWise-wt-reaudit4-d0b83820/tests/test_sample_quiet_predicate_evidence.py:652) introduces a child that sleeps 60 seconds after reporting. Correct production code therefore spends five seconds waiting before terminating it on every successful module run. This is intentional fault injection, **not an unexpected delay in normal worker cleanup**. It nevertheless creates the requested runtime finding on the passing-suite path. Deterministic escalation coverage could avoid that repeated wait.

**E1 — disposition audit**

Here, `P` denotes `scripts/sample_quiet_predicate_evidence.py`; `T` denotes its test module.

| Item | Verdict against record 13 | Final implementation and executed evidence |
|---|---|---|
| S1 | **FIXED** | `P:934–937` folds bad cleanup rows into an otherwise-null error, naming PID and exit code. The sleeping-child regression returns exit 1; `cleanup-silent` fails it. |
| S2 | **FIXED** | `P:925` uses five seconds. Adapted Probe C’s one-second shutdown exits 0; the actual `load()` regression also passes. The real-load clean-exit assertion remains. |
| S3 | **FIXED** | `P:702–704` counts error rows and sets the session error only when errors exist without a completed round. Bounded cases below pass. |
| S4 | **FIXED** | `P:1054–1056` removes both resolved-sibling reasons. Adapted Probe A and persisted-summary assertions pass. |
| S5 | **FIXED** | `P:996–1042` separates means and references by census condition, boot and optional OS build. Probe D yields two groups at 1 W and 9 W. New rendering defect R1 remains. |
| S6 | **FIXED** | `T:695–717` performs Darwin native readback in a subprocess: background `0x09`, user-initiated `0x19`. Constant-swap mutation fails this test. |
| S7 | **FIXED** | `stop_process` and exactly its two tests are deleted. AST inventory confirms 45 − 2 + 1 = 44 tests. |
| N1 | **FIXED** | `T:19–21` now describes startup/unreported CPU headroom on the kernel ceiling, with the ruled measurements and 0.5-second floor. |
| N2 | **FIXED** | `P:975–978` uses safe lookup and explicit `ValueError`. Missing metrics and empty metrics both produce the handled CLI refusal, exit 2. |
| N3 | **FIXED** | `P:889–894` closes both pipe ends when `Process.start()` raises. The real-pipe regression verifies closure and no join of the unstarted process. |

The complete diff contains only the two expected files. **No change outside the ten dispositions was found.** The real-load test’s AST is unchanged.

Original probes were rerun from adapted `/tmp` copies against HEAD. Probe A needed `.get()` for reason fields intentionally removed by S4; Probe C needed its hard-coded `.5` ladder updated to `5`. Its adaptation was supplemented by the actual `load()` regression. Sources and outputs: [scratch directory](/tmp/jw-reaudit4-232).

**E2 — bounded collection behavior**

| Returned round statuses | Session error | Exit | `error_rounds` |
|---|---|---:|---:|
| `complete, error, complete` | `None` | 0 | 1 |
| `error, error, error` | `no round completed successfully` | 1 | 3 |
| `partial` only | `None` | 0 | 0 |

The partial-only probe used duration `0.5 s` and interval `1 s`; its recorded monotonic end remained clipped to `0.5 s`. Production’s success literal is `complete`, corresponding to the ruling’s “ok.”

**E3 — summary identity and null paths**

- Two boots never pooled; two builds within one boot also remained separate. Matching-reference Δ was `−1920 J`; removing that reference produced a reasoned null instead of borrowing another boot/build.
- JSON groups emit `state`, `repeat`, `sessions`, `census_clean`, `boot_id`, and `os_build` when any input row carries that field. Reference objects use the same comparison identity.
- With mixed build presence, the missing-build group emits `os_build: null` plus a reason. When every row lacks the field, it is omitted. Both cases summarize successfully. Missing boot identity likewise remains reasoned null.
- Empty-directory output remains `status: no_rounds`, `reference: null`, empty groups/references, and `PROVISIONAL`. Compared with the base, its only removed key is the correctly deleted `alignment_model_reason`; reference/aggregation descriptions now mention boots/builds. No top-level identity keys are added because there are no groups.

**E4 — measured runtime attribution**

Two ordinary module runs: **44 OK in 14.154 s and 13.609 s**.

A separate per-test timing replay passed at HEAD and at a `/tmp` copy of `d74b1be5`:

| Test | Base seconds | HEAD seconds |
|---|---:|---:|
| `test_load_worker_runs_its_window_after_the_rendezvous` | 0.001564 | 7.421370 |
| `test_native_qos_classes_read_back_in_subprocess` | absent | 0.468539 |
| `test_real_load_tracks_point_one_core_and_guards_worker_budget` | 3.879410 | 3.745660 |
| `test_real_collect_no_power_reaps_all_recorded_workers` | 1.696734 | 1.610270 |
| Entire module | 5.776 | 13.457 |

The increase is overwhelmingly the S1/S2 slow-exit regression, including spawn costs, the one-second successful shutdown and the full five-second escalation wait. S6 adds approximately half a second.

Measured joins at HEAD:

- One-second delayed clean exit: **1.150994 s**, exit 0.
- Deliberately stuck child: **5.002057 s**, then TERM/reap in **0.001105 s**.
- Normal real-load child: **0.012919 s**, exit 0.

Thus the production happy path does **not** incur a five-second delay. R2 concerns the unconditional wait in the passing regression suite. [Timing evidence](/tmp/jw-reaudit4-232/timing-summary.log).

**E5 — mutations**

Every mutation exited 1 with assertion failures and **zero test errors**. No incidental real-load failures occurred.

| Mutation | Failure count | Failing test names |
|---|---:|---|
| `cores` | 1 | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `alignment` | 2 | `test_absolute_anchor_endpoints_reject_known_arrival_offset`; `test_real_production_rate_anchor_and_clock_step_refusal` |
| `observer` | 1 | `test_observer_cost_includes_known_reaped_child_delta` |
| `clock` | 1 | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `catchup-capped` | 3 | `test_cpu_budget_overshoot_and_frozen_duty`; `test_late_initial_scheduling_never_catches_up`; `test_preempted_burn_exits_on_the_wall_deadline` |
| `burn-noop` | 1 | `test_burn_profiles_advance_their_generator` |
| `window-skip` | 1 | `test_load_worker_runs_its_window_after_the_rendezvous` |
| `cleanup-silent` | 1 | `test_load_worker_runs_its_window_after_the_rendezvous` (`exit_delay=60`) |
| `pool-across-boots` | 1 | `test_summary_never_pools_census_conditions_or_reference` (`field='boot_id'`) |
| `qos-swap` | 1 | `test_native_qos_classes_read_back_in_subprocess` |
| `all-error-exit-0` | 1 | `test_one_recorder_for_all_rounds_and_cleanup_on_round_failure` (three errors) |

[Complete mutation results](/tmp/jw-reaudit4-232/results.json). Hash comparison covered **8,053 tracked files**, all byte-identical; Git status before and after was exactly `## HEAD (no branch)`. Final checks after supplementary testing also passed. All writes were under `/tmp`.

**E6 — every real-load assertion**

| Test line | Assertion | Classification |
|---:|---|---|
| 727 | Configured worker share equals `.1` | Configuration |
| 739 | Report error is `None` | Lifecycle-bounded |
| 748 | Claimed CPU fraction ≤ `.14` | Upper bound on a starvation-lowered quantity |
| 750 | Period CPU ≤ budget + measured overshoot allowance | Upper bound on a starvation-lowered quantity |
| 756 | Kernel charge ≥ claimed CPU − `.01` | Kernel lower bound relaxed by starvation |
| 758 | Kernel charge ≤ `.14 × duration + STARTUP_CPU_S` | CPU upper bound, with empirical startup headroom |
| 760 | Cleanup list is nonempty | Lifecycle-bounded structure |
| 762 | Child is not alive | Lifecycle-bounded |
| 763 | Child exit code equals zero | Lifecycle-bounded |
| 764 | PID lookup raises `ProcessLookupError` | Lifecycle-bounded reaping |

Both requested same-signature statements:

- **“real-load assertion fails on correct code under scheduler starvation”**: still possible when starvation exceeds finite startup/result/cleanup deadlines. The one-second post-result witness is fixed. The injected long shutdown demonstrates escalation, not an actual scheduler-starvation experiment.
- **“assertion keyed to a quantity starvation destroys”**: **not found in the CPU-delivery failing direction**. No positive delivery floor remains; reduced claimed CPU relaxes the kernel lower bound. Timely lifecycle completion remains scheduler-dependent, explicitly retained by 13a with the larger grace.

**E7 — production prune**

No further dead top-level callable or unused import was found. No remaining reference/comment attributes termination to deleted `stop_process`; `PowerRecorder` still owns its termination ladder. All four docstring citation ranges resolve to the described production logic:

- `run_night.py:2603–2712`
- `quiet_admission.py:231–278`
- `powermetrics.py:1775–1785`
- `powermetrics.py:2009–2025`

Next exact step: lead dispositions R1/R2, then the required downstream full sharded replay and final verification.

## Residual risk

This review establishes no quiet-machine or power-measurement evidence. PROVISIONAL labels remain appropriate.

The fixed startup CPU allowance remains empirical. Seat 18’s reported ceiling excursions were not reproduced here; their cause remains unestablished. Full repository replay remains lead-owned under record 13a.