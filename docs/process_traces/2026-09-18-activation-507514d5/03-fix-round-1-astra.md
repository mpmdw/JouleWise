```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented R1, R2, R4–R7 and F1/F2; 41 tests pass and all three mutations fail as intended. R3's 0.2-core case needs a guardrail ruling.",
  "workspace": {
    "base_requested": "d066d271",
    "base_mode": "exact",
    "head_start": "d066d271b37849c3fcaf67807044d5b5b326e81e",
    "head_end": "d066d271b37849c3fcaf67807044d5b5b326e81e",
    "upstream_end": "d066d271b37849c3fcaf67807044d5b5b326e81e",
    "branch": "feat/2026-09-18-quiet-predicate-evidence-harness"
  },
  "pathspec": [
    "scripts/sample_quiet_predicate_evidence.py",
    "tests/test_sample_quiet_predicate_evidence.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 41 tests in 5.376s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B - <<'PY'\nimport subprocess, sys\nwrapper = r'''\nimport importlib.machinery, importlib.util, pathlib, sys\nname = sys.argv[1]\npath = pathlib.Path.cwd() / 'scripts/sample_quiet_predicate_evidence.py'\nsource = path.read_text()\nedits = {\n 'alignment': ('endpoint = anchor[\"first_sample_end_point_epoch_s\"]', 'endpoint = getattr(stamps.get(\"first_parse\"), \"epoch_s\", anchor[\"first_sample_end_point_epoch_s\"])'),\n 'observer': ('resource.getrusage(resource.RUSAGE_CHILDREN)', 'type(\"ZeroUsage\", (), {\"ru_utime\": 0, \"ru_stime\": 0})()'),\n 'cores': ('\"share\": args.cores / count', '\"share\": 1.0 / count')}\nold, new = edits[name]\nassert source.count(old) == 1\nsource = source.replace(old, new)\noriginal = importlib.util.spec_from_file_location\nclass Loader(importlib.machinery.SourceFileLoader):\n def get_code(self, fullname): return compile(source, str(path), 'exec')\ndef spec(fullname, location, *args, **kwargs):\n if fullname == 'scripts.sample_quiet_predicate_evidence':\n  return original(fullname, path, loader=Loader(fullname, str(path)))\n return original(fullname, location, *args, **kwargs)\nimportlib.util.spec_from_file_location = spec\nrunner = pathlib.Path('/tmp/mag-507514d5/mutations.py')\nsys.argv = [str(runner), name]\nexec(compile(runner.read_text(), str(runner), 'exec'), {'__name__': 'mutation_runner', '__file__': str(runner)})\n'''\nfor name, count in [('alignment', 2), ('observer', 1), ('cores', 1)]:\n result = subprocess.run([sys.executable, '-B', '-c', wrapper, name], capture_output=True, text=True, timeout=30)\n print('CASE', name, 'EXIT', result.returncode)\n print('\\n'.join(result.stderr.splitlines()[-20:]))\n print(result.stdout.strip())\n assert result.returncode == 1\n assert f'failures {count} errors 0' in result.stdout, result.stdout\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CASE alignment EXIT 1",
          "FAILED (failures=2)",
          "MUTATION alignment run 41 failures 2 errors 0",
          "CASE observer EXIT 1",
          "FAILED (failures=1)",
          "MUTATION observer run 41 failures 1 errors 0",
          "CASE cores EXIT 1",
          "FAILED (failures=1)",
          "MUTATION cores run 41 failures 1 errors 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MUTATION cores run 41 failures 1 errors 0$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check; git status --short --branch; git rev-parse HEAD; git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M scripts/sample_quiet_predicate_evidence.py",
          " M tests/test_sample_quiet_predicate_evidence.py",
          "d066d271b37849c3fcaf67807044d5b5b326e81e",
          "d066d271b37849c3fcaf67807044d5b5b326e81e"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "d066d271b37849c3fcaf67807044d5b5b326e81e$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: R3 requests a real 0.2-core run, but the same prompt caps load experiments at 0.1 cores. Completed the independent 0.1-core regression and killed the cores mutation before worker launch. The 0.2-core case remains unimplemented and unrun.",
      "needs": "Choose an explicit 3-second 0.2-core exception or accept 0.1-core coverage for this round. Recommendation: retain the cap until the lead explicitly authorizes the exception."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The supplied mutations.py has no sibling alignment.py, observer.py or cores.py. V2 executes that runner unchanged with an in-memory loader applying the three original mutations to the current source; no mutation files were written.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A 3-second, 100-ms-period run achieved 0.0578857 cores for a 0.1 request, with observed wake delays around 150 ms. The final regression uses 500-ms periods and the unchanged absolute tolerance of 0.04 cores. It validates this short calibration window, not default-period accuracy or post-calibration stationarity.",
      "needs": "Retain this limitation when interpreting load evidence."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No live power collection or canonical discovery suite was run. The no-power integration uses a one-second duration and one-second interval: the interval is the minimum legal value; duration accepts any positive value and therefore has no smallest legal value.",
      "needs": "Lead retains successful live observation, hardware validation and final diff review."
    }
  ]
}
```

## Change

Only the two files in `pathspec` were modified; no commit was made. The schema remains `joulewise.quiet_predicate_evidence.v1`.

| Item | Result and regression | Mutation result |
|---|---|---|
| R1 | **DONE** — `test_absolute_anchor_endpoints_reject_known_arrival_offset`; strengthened `test_real_production_rate_anchor_and_clock_step_refusal` | Alignment killed: 2 failures |
| R2 | **DONE** — `test_observer_cost_includes_known_reaped_child_delta` | Observer killed: 1 failure |
| R3 | **NOT DONE in full** — `test_real_load_tracks_point_one_core_and_guards_worker_budget` covers 0.1 cores; 0.2 requires ruling | Cores killed before worker launch |
| R4 | **DONE** — `test_real_collect_no_power_reaps_all_recorded_workers` checks rows, missing-power reasons and worker PID absence | No supplied mutation |
| R5 | **DONE** — `test_empty_directory_cli_writes_reasoned_null_summary` | No supplied mutation |
| R6 + F2 | **DONE** — `test_summary_preserves_exact_session_provenance` | No supplied mutation |
| R7 | **DONE** — `test_smoke_temporary_journal_writes_stay_under_output`, plus filesystem auditing in the real collection test | No supplied mutation |
| F1 | **DONE** — `test_partial_round_retains_concurrent_census_and_marks_contamination`, `test_round_without_completed_census_is_reasoned_unknown`, `test_summary_never_pools_census_conditions_or_reference` | No supplied mutation |

## Verification notes

All 31 existing tests remain, with 10 additions. No existing assertion was weakened or deleted.

The initial filesystem audit incorrectly classified `/dev/null` and directory-relative cleanup as outside writes; that test instrumentation was corrected. The final mutation replay has only the intended failures and zero errors.

Next exact step: lead rules on the 0.2-core exception, then reviews the two-file diff.