```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FAIL: the current 2,440-test suite partitions exactly and propagates ordinary failures, but two zero-test paths exit 0 and can silently lose coverage.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "13745c47fe5ca5f3acc3d19b6bc8df0b9e6aab4b",
    "head_end": "13745c47fe5ca5f3acc3d19b6bc8df0b9e6aab4b",
    "upstream_end": "2441d0c8ef3bb8a78ebfc4898e4ddf3f3a88310f",
    "branch": "impl/test-speed"
  },
  "pathspec": [],
  "unowned_dirty": [
    ".github/workflows/ci.yml",
    "scripts/shard_tests.py",
    "scripts/test_timings.json",
    "tests/test_shard_tests.py"
  ],
  "verdict": {
    "overall": "fail",
    "blocker_present": true,
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "scripts/shard_tests.py",
        "line": 194,
        "scenario": "unittest discover calls a module load_tests hook with pattern='test*.py', while loadTestsFromName calls it with pattern=None",
        "evidence": "An in-memory module contributed 1 test under discover semantics but the shard ran 0 tests, printed PASS, and returned 0.",
        "impact": "A future pattern-sensitive load_tests module can be discovered and assigned exactly once while all of its tests are silently omitted.",
        "recommendation": "Load selected modules with the same loadTestsFromModule(..., pattern='test*.py') semantics as discovery and add a regression."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "scripts/shard_tests.py",
        "line": 190,
        "scenario": "successful starts true and lines 212-218 return PASS without requiring a nonempty module/test count",
        "evidence": "--shards 95 --index 95 reported modules=0 tests=0 result=PASS and exited 0.",
        "impact": "An over-high or miswired shard can execute nothing while satisfying the CI step.",
        "recommendation": "Fail nonzero when a selected shard has zero modules or zero tests; add direct CLI regressions."
      }
    ],
    "proofs": {
      "coverage": {
        "discover_modules": 94,
        "discover_tests": 2440,
        "partition_N": [1, 2, 3, 4, 8],
        "all_unions_exact": true,
        "all_partitions_disjoint": true,
        "unmeasured_module": "tests.test_shard_tests",
        "unmeasured_memberships_per_N": 1
      },
      "aggregate": {
        "sharded_tests": 2440,
        "plain_discover_tests": 2440,
        "sharded_skips": 85,
        "plain_skips": 85,
        "both_passed": true
      },
      "failure_propagation": {
        "assertion_failure_rc": 1,
        "runtime_error_rc": 1,
        "unimportable_module_rc": 1
      },
      "determinism": {
        "two_process_outputs_identical": true,
        "hash_seeds": [1, 987654],
        "serialized_bytes": 14286
      },
      "stdlib_only": {
        "pass": true,
        "imports": ["__future__", "argparse", "fnmatch", "json", "math", "os", "pathlib", "re", "statistics", "subprocess", "sys", "tempfile", "time", "unittest"]
      },
      "timing_map": {
        "entries": 93,
        "stale_entries": 0,
        "wrong_positive_map_preserved_coverage_for_all_N": true,
        "correctness_effect": "balance_only"
      },
      "ci_wiring": {
        "matrix_cells": 8,
        "python_versions": ["3.11", "3.14"],
        "shards": [1, 2, 3, 4],
        "fetch_depth_zero_preserved": true,
        "gen_state_check_preserved": true,
        "compileall_preserved": true,
        "continue_on_error": false
      }
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python - <<'PY'\nimport os,sys,unittest\nfrom pathlib import Path\nsys.path.insert(0,os.fspath(Path.cwd()/'scripts'))\nimport shard_tests as s\nL=unittest.TestLoader(); Q=L.discover('tests')\ndef flat(q):\n for x in q:\n  yield from flat(x) if isinstance(x,unittest.TestSuite) else (x,)\nD={'tests.'+t.__class__.__module__.removeprefix('tests.') for t in flat(Q)}\nM=s.discover_test_modules(); T=s.load_timing_map()\nprint(f'discover={len(D)} cases={Q.countTestCases()} runner={len(M)} errors={len(L.errors)} unknown={sorted(set(M)-set(T))}')\nfor n in (1,2,3,4,8):\n P=s.partition_modules(M,T,n); A=[m for p in P for m in p]\n print(f'N={n} exact={set(A)==D} disjoint={len(A)==len(set(A))} flat={len(A)} sizes={[len(p) for p in P]} unknown_hits={A.count(\"tests.test_shard_tests\")}')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "discover=94 cases=2440 runner=94 errors=0 unknown=['tests.test_shard_tests']",
          "N=1 exact=True disjoint=True flat=94 sizes=[94] unknown_hits=1",
          "N=2 exact=True disjoint=True flat=94 sizes=[47, 47] unknown_hits=1",
          "N=3 exact=True disjoint=True flat=94 sizes=[29, 32, 33] unknown_hits=1",
          "N=4 exact=True disjoint=True flat=94 sizes=[1, 28, 33, 32] unknown_hits=1",
          "N=8 exact=True disjoint=True flat=94 sizes=[1, 1, 14, 13, 17, 16, 16, 16] unknown_hits=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "N=8 exact=True disjoint=True.*unknown_hits=1"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'import os,sys,types,unittest;from pathlib import Path;sys.path.insert(0,os.fspath(Path.cwd()/\"scripts\"));import shard_tests as s;m=types.ModuleType(\"audit_pattern\");m.C=type(\"C\",(unittest.TestCase,),{\"__module__\":m.__name__,\"test_x\":lambda self:None});m.load_tests=lambda loader,suite,pattern:suite if pattern==\"test*.py\" else unittest.TestSuite();sys.modules[m.__name__]=m;print(\"discover_semantics_tests=\",unittest.TestLoader().loadTestsFromModule(m,pattern=\"test*.py\").countTestCases());print(\"shard_rc=\",s.run_shard((m.__name__,),1,1))'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "discover_semantics_tests= 1",
          "SHARD SUMMARY index=1/1 modules=1 tests=0 failures=0 errors=0 skipped=0 result=PASS",
          "shard_rc= 0"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "SHARD SUMMARY.*tests=1.*result=FAIL"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/shard_tests.py --shards 95 --index 95",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["SHARD SUMMARY index=95/95 modules=0 tests=0 failures=0 errors=0 skipped=0 result=PASS"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "result=FAIL"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/shard_tests.py --workers 4 > /private/tmp/test-speed-audit-workers.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["WORKERS SUMMARY shards=4 modules=94 tests=2440 failures=0 errors=0 skipped=85 failed_shards=none result=PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "WORKERS SUMMARY shards=4 modules=94 tests=2440.*result=PASS"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest discover -s tests > /private/tmp/test-speed-audit-discover.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tests": 2440,
        "tail": ["OK (skipped=85)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2440 tests[\\s\\S]*OK \\(skipped=85\\)"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'import os,sys;from pathlib import Path;sys.path.insert(0,os.fspath(Path.cwd()/\"scripts\"));import shard_tests as s;raise SystemExit(s.run_shard((\"audit_definitely_unimportable_xyz\",),1,1))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["SHARD SUMMARY index=1/1 modules=1 tests=1 failures=0 errors=1 skipped=0 result=FAIL"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "errors=1.*result=FAIL"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_shard_tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 0.884s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests.*OK"
      }
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The specified local interpreter is Python 3.13.1; local execution cannot establish the real Python 3.11 and 3.14 matrix result.",
      "needs": "After fixing F1/F2 and updating the branch, confirm all eight PR matrix cells execute and pass and remain required for merge."
    },
    {
      "id": "G2",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "origin/main advanced during the audit to 2441d0c and includes test changes; audited HEAD 13745c4 is its ancestor.",
      "needs": "Update the branch and rerun the aggregate-count proof on the integrated PR head."
    },
    {
      "id": "G3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "strategy.fail-fast is omitted and therefore defaults true; one failure may cancel sibling cells and hide additional failures, but cannot turn that workflow run green.",
      "needs": "Set fail-fast: false only if complete failure diagnostics on red runs are required."
    }
  ]
}
```

## Findings

- **F1 — blocker:** [scripts/shard_tests.py:194](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/testspeed/scripts/shard_tests.py:194) does not reproduce `unittest discover`’s `load_tests` contract. The independent probe proved `discover_semantics_tests=1`, followed by `Ran 0 tests`, `result=PASS`, and return code 0. This is a genuine future silent-drop path even when module partition membership is complete and disjoint.

- **F2 — blocker:** [scripts/shard_tests.py:190](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/testspeed/scripts/shard_tests.py:190) initializes success to true, and [the return path](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/testspeed/scripts/shard_tests.py:218) has no zero-module or zero-test guard. The real CLI accepted shard 95/95 with no work and exited 0.

Everything else requested passed: N={1,2,3,4,8} had exact/disjoint 94-module coverage; the unmeasured new module appeared once per partition; wrong positive timing data changed only placement; assertion failures, runtime errors, and import errors returned nonzero; two-process partition output was byte-identical across different hash seeds; imports were stdlib-only; and sharded versus serial execution both produced exactly 2,440 tests with 85 skips.

## Residual risk

The workflow creates all eight Python×shard combinations and preserves `fetch-depth: 0`, `gen_state --check`, and `compileall` at [.github/workflows/ci.yml:11](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/testspeed/.github/workflows/ci.yml:11). There is no `continue-on-error` or conditional skip.

GitHub documents that matrix `fail-fast` defaults to true and cancels queued/in-progress siblings after one failure. That can conceal additional diagnostics, but the triggering failure keeps the workflow red; it cannot create a false green. [GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)

The lead must fix F1/F2, update from current `origin/main`, then confirm the actual PR shows all eight 3.11/3.14 matrix cells green and that repository protection still requires the resulting checks before merge.