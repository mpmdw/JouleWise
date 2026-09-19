```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "E1–E6 completed: 45 tests passed twice, all twelve mutations were killed, and one rendering discrepancy remains: missing os_build displays None instead of null.",
  "workspace": {
    "base_requested": "46d310eba1fa43a5ca898364302db90392fcd757",
    "base_mode": "descendant",
    "head_start": "9ae6715ba79f7c626add564e6af3d6d46a97848a",
    "head_end": "9ae6715ba79f7c626add564e6af3d6d46a97848a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 0},
    "findings": [
      {
        "id": "R3",
        "severity": "should_fix",
        "summary": "Missing os_build renders as None in all three Markdown tables, contrary to E2's required null spelling.",
        "call_site": "scripts/sample_quiet_predicate_evidence.py:1061,1066; tests/test_sample_quiet_predicate_evidence.py:861",
        "counterfactual": "Summarize two idle rows, boot A without os_build and boot B with os_build=25G83. JSON emits null for A, but every Markdown table emits None. A direct null-rendering check fails in all three tables.",
        "recommendation": "Render missing identity values as null and change the mixed-build regression to expect that literal instead of interpolating Python None."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit5-232/bench.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tracked_files_checked 8053 byte_changed []",
          "status_identical True",
          "All 12 mutations killed; worktree byte-identical."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "All 12 mutations killed; worktree byte-identical\\."}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit5-232/probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "unused imports []",
          "top-level functions without internal name uses []",
          "PROBES COMPLETE: E2 null spelling discrepancy reproduced"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PROBES COMPLETE:"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit5-232/join_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["JOIN PROBE PASS: clean exit uses default 5.0; stuck child alone overrides 0.2"]
      },
      "expected": {"exit_code": 0, "tail_regex": "JOIN PROBE PASS:"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit5-232/null_check.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1 test in 0.002s", "FAILED (failures=3)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit5-232/final_checks.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tracked_files_checked 8053 byte_changed []",
          "status_identical True",
          "## HEAD (no branch)",
          "FINAL PRESERVATION PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "FINAL PRESERVATION PASS"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^\\[\\]$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This bounded delta review completed module replays, twelve mutations, rendering probes and preservation checks; canonical full discovery was not run.",
      "needs": "Lead performs the planned full sharded replay after disposition and any fix."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The required session-end orphan census could not observe processes because the sandbox denied ps. No clean census is claimed.",
      "needs": "Lead reruns the observational fixture census in an authorized environment."
    }
  ]
}
```

## Findings

**R3 — should_fix: missing build renders `None`, not `null`.** The [identity renderer](/Users/edr/code/JouleWise-wt-reaudit5-d0b83820/scripts/sample_quiet_predicate_evidence.py:1066) passes missing values through `str()`. The [new regression](/Users/edr/code/JouleWise-wt-reaudit5-d0b83820/tests/test_sample_quiet_predicate_evidence.py:861) interpolates the same Python `None`, so it preserves the discrepancy. A separate check of E2’s required spelling produced **three assertion failures**, one per table. JSON remains correct; boot identities remain distinguishable.

**E1 — delta scope and ASTs**

`git diff 46d310eb HEAD` contains exactly the two expected files: **46 insertions, 10 deletions**. Changes are confined to the R1 renderer/regression and R2 grace parameter/regression. No unrelated change found.

- All **43 other existing test ASTs** are unchanged.
- The real-load test’s AST is unchanged.
- One Markdown test was added, bringing the module to 45.
- Production changes affect only `load()` and `summarize()`, including its new nested `identity_cells()`.
- `main()` and `parser()` ASTs are unchanged. Diff whitespace checks pass.

**E2 — executed Markdown rendering**

With no `os_build` anywhere, the column is absent. Selected actual rows from all three tables:

```text
| State | Repeat / census_clean | boot_id | Metric | min | p10 | p50 | p90 | max |
|---|---|---|---|---:|---:|---:|---:|---:|
| idle | 1 / True | A | busy_cores | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 |
| idle | 1 / True | B | busy_cores | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 |

| State | Repeat / census_clean | boot_id | Rail | Mean W | Coverage s | ΔJ / 480 s | Alignment bound J |
|---|---|---|---|---:|---:|---:|---:|
| idle | 1 / True | A | cpu_w | 1 | 10 | 0 | 9.6 |
| idle | 1 / True | B | cpu_w | 9 | 10 | 0 | 9.6 |

| State | Repeat / census_clean | boot_id | Complete | Partial | Error | Load disagreements / compared |
|---|---|---|---:|---:|---:|---:|
| idle | 1 / True | A | 1 | 0 | 0 | 0 / 1 |
| idle | 1 / True | B | 1 | 0 | 0 | 0 / 1 |
```

With mixed build presence, the column appears, but the missing case exposes R3:

```text
| State | Repeat / census_clean | boot_id | os_build | Metric | min | p10 | p50 | p90 | max |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| idle | 1 / True | A | None | busy_cores | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 |
| idle | 1 / True | B | 25G83 | busy_cores | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 |

| State | Repeat / census_clean | boot_id | os_build | Rail | Mean W | Coverage s | ΔJ / 480 s | Alignment bound J |
|---|---|---|---|---|---:|---:|---:|---:|
| idle | 1 / True | A | None | cpu_w | 1 | 10 | 0 | 9.6 |
| idle | 1 / True | B | 25G83 | cpu_w | 9 | 10 | 0 | 9.6 |

| State | Repeat / census_clean | boot_id | os_build | Complete | Partial | Error | Load disagreements / compared |
|---|---|---|---|---:|---:|---:|---:|
| idle | 1 / True | A | None | 1 | 0 | 0 | 0 / 1 |
| idle | 1 / True | B | 25G83 | 1 | 0 | 0 | 0 / 1 |
```

Every header, separator and data row has the correct column count: **9/8/7** without builds; **10/9/8** with builds. Both-builds-present also passed. No malformed table found. [Complete rendered evidence](/tmp/jw-reaudit5-232/probes.log).

**E3 — R2 execution**

| Run | Tests | unittest time | Wall time |
|---|---:|---:|---:|
| Module 1 | 45 OK | 8.004 s | 8.459 s |
| Module 2 | 45 OK | 7.687 s | 8.140 s |

The instrumented rendezvous regression passed:

- One-second shutdown: no explicit keyword supplied; `join(timeout=5.0)` completed in **1.120865 s**, child exit **0**.
- Stuck child: explicit `join_grace_s=0.2`; first join took **0.202038 s**, followed by termination and reaping, exit **−15**.
- Signature is `(args, *, join_grace_s: float = 5.0)`.
- `main()` calls only `load(args)`; no CLI flag exists.

[Join evidence](/tmp/jw-reaudit5-232/join_probe.log).

**E4 — twelve mutations**

Every mutant exited **1**, with assertion failures and **zero test errors**. No incidental real-load failures occurred.

| Mutation | Failures | Failing test names |
|---|---:|---|
| `cores` | 1 | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `alignment` | 2 | `test_absolute_anchor_endpoints_reject_known_arrival_offset`; `test_real_production_rate_anchor_and_clock_step_refusal` |
| `observer` | 1 | `test_observer_cost_includes_known_reaped_child_delta` |
| `clock` | 1 | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `catchup-capped` | 3 | `test_cpu_budget_overshoot_and_frozen_duty`; `test_late_initial_scheduling_never_catches_up`; `test_preempted_burn_exits_on_the_wall_deadline` |
| `burn-noop` | 1 | `test_burn_profiles_advance_their_generator` |
| `window-skip` | 1 | `test_load_worker_runs_its_window_after_the_rendezvous` |
| `cleanup-silent` | 1 | `test_load_worker_runs_its_window_after_the_rendezvous` (`exit_delay=60`) |
| `pool-across-boots` | 4 | `test_summary_markdown_distinguishes_boots_and_optional_builds` (three subcases); `test_summary_never_pools_census_conditions_or_reference` (`boot_id`) |
| `qos-swap` | 1 | `test_native_qos_classes_read_back_in_subprocess` |
| `all-error-exit-0` | 1 | `test_one_recorder_for_all_rounds_and_cleanup_on_round_failure` (three errors) |
| `markdown-identity-drop` | 3 | `test_summary_markdown_distinguishes_boots_and_optional_builds` (three subcases) |

[Exact results and failing subtest names](/tmp/jw-reaudit5-232/results.json).

All mutations ran on `/tmp` copies. Before and after status was exactly `## HEAD (no branch)`. Hash checks covered **8,053 tracked files**, with **zero byte changes**, including a final check after supplementary probes. HEAD remained unchanged.

**E5 — same-signature statements**

- **“real-load assertion fails on correct code under scheduler starvation”**: the previously acknowledged finite-lifecycle case remains. Starvation beyond startup/result/cleanup deadlines can still fail the error-null assertion at test line **742** or clean-exit assertion at **766**. Production deadlines remain at lines **899–900, 911–914 and 925–931**. This is unchanged from record 20; no new CPU-delivery failure site was found.
- **“assertion keyed to a quantity starvation destroys”**: none found among the CPU-delivery assertions. They impose upper bounds, and reduced claimed CPU relaxes the kernel-accounting lower bound. Timely lifecycle completion remains scheduler-dependent as above.
- **“human-readable summary loses an identity the JSON carries”**: no surviving boot/build omission found in the requested cases. All three tables carry the comparison identities. R3 concerns the missing-value spelling.

**E6 — PR-review notes**

No additional false comment, obsolete table-layout claim, unused import or unused top-level callable was found. The script docstring at lines **29–33** describes census separation correctly, though it does not enumerate boot/build separation. No README references this harness. The changed cleanup comment accurately describes the short test-only grace.

Next exact step: lead dispositions R3, applies any accepted fix with its rendering regression, then performs the final delta check and planned full sharded replay.

## Residual risk

Canonical full-suite replay remains lead-owned. The orphan census was unavailable because the sandbox denied `ps`; no clean census is claimed. These checks establish no quiet-machine or power-measurement validation, and PROVISIONAL labels remain appropriate.