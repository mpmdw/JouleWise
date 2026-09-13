```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Installed ruled census patterns and G1–G4; M1–M9 killed, but M10 protection requires a ruling and live verification remains blocked.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "informational",
    "head_start": "4b9a34111d33a04727a09127a1c1fbd8aab87052",
    "head_end": "4b9a34111d33a04727a09127a1c1fbd8aab87052",
    "upstream_end": "4b9a34111d33a04727a09127a1c1fbd8aab87052",
    "branch": "fix/2026-09-13-arm-census-system-services"
  },
  "pathspec": [
    "joulewise/arm_readiness_evidence_t0.py",
    "tests/test_arm_readiness_evidence_t0.py"
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
      "cmd": "python3 -m unittest tests.test_arm_readiness_evidence_t0",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": []
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/arm-census-safe-suite.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 3 not found in (0, 1) : sysmon request failed with error: sysmond service not found",
          "pgrep: Cannot get process list",
          "Ran 75 tests in 397.569s",
          "FAILED (failures=1, skipped=2)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.045s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_integration tests.test_arm_readiness_registry tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 69 tests in 305.548s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "/usr/bin/pgrep -lf '/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 3,
        "tail": ["sysmon request failed with error: sysmond service not found", "pgrep: Cannot get process list"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "/usr/bin/pgrep -lf 'powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 3,
        "tail": ["sysmon request failed with error: sysmond service not found", "pgrep: Cannot get process list"]
      },
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/arm-census-dialect-check.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "'(?:firefox)' exit=0 stdout='firefox\\n'",
          "'\\\\bwatch\\\\b' exit=0 stdout='watch\\n'",
          "'\\\\d+' exit=0 stdout='574\\n'"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "exit=0"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check; git diff --stat; git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " joulewise/arm_readiness_evidence_t0.py  |   8 +-",
          " tests/test_arm_readiness_evidence_t0.py | 140 +++++++++++++++++++++++++++++++-",
          " 2 files changed, 144 insertions(+), 4 deletions(-)",
          " M joulewise/arm_readiness_evidence_t0.py",
          " M tests/test_arm_readiness_evidence_t0.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": " M tests/test_arm_readiness_evidence_t0.py"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: local /usr/bin/grep -E accepts all three Python-only constructs named by A2. M10 variants add no failure beyond the unmutated G4 pgrep environment failure. The specified positive controls do not establish the required fail-closed property.",
      "needs": "May G4 explicitly reject Python-only regex syntax? Options: add a portable-syntax assertion (recommended), or approve a different dialect validator. M10 completion is blocked pending this ruling."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "Both live pgrep probes return exit 3 because the process list is unavailable. G4 fails on this condition; no live census result is established.",
      "needs": "Replay G4 and both probes in a lead-controlled environment with process-list access."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The requested unmodified module conflicts with 'never signal any process': its existing caffeinate test cleanup calls process.terminate() at tests/test_arm_readiness_evidence_t0.py:2361. A /tmp runner explicitly skipped that test; no repository skip was added.",
      "needs": "Resolve the no-signal/full-module conflict before the unmodified module replay."
    }
  ]
}
```

## Change

- **FIX-1:** Constants at `joulewise/arm_readiness_evidence_t0.py:57`; browser/monitor use at `:1729`. AST comparison confirms probe count, order, labels, absence checks, and `derived` fields are preserved.
- **FIX-2:** Updated argv pins at `tests/test_arm_readiness_evidence_t0.py:2529`; G1–G4 at `:2548`, `:2555`, `:2585`, and `:2627`. Reused existing authoring fixtures. Recorded inputs preserve Exhibit C’s truncation: ten Apple service lines representing eight executables, plus watchdogd.

## Verification notes

`rg -l "_fresh_probe" tests/` returned only `tests/test_arm_readiness_evidence_t0.py`; its AST test passed separately.

The safe module replay’s sole failure was G4’s unavailable process list. The final G4 rerun likewise failed with exit 3. Its grep controls passed:

```text
BSD grep -E controls: 27/27 PASS (5 positives; 22 service negatives)
```

Browser probe exits 0 **or** 1 are valid depending on browser state; observed exit 3 establishes neither.

Mutation copies and logs are under `/tmp/arm-census-mutations/`. Replay scripts: `/tmp/arm-census-mutations.py` and `/tmp/arm-census-m10.py`. Each M1–M9 variant exited 1 in the named regression:

| Mutation | Failing test |
|---|---|
| M1 old browser | `test_g1_ruled_census_patterns_ignore_recorded_macos_services` |
| M2 remove tail | `test_g1_ruled_census_patterns_ignore_recorded_macos_services` |
| M3 one browser | `test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors` |
| M4 bare watch | `test_g1_ruled_census_patterns_ignore_recorded_macos_services` |
| M5 remove path anchor | `test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors` |
| M6 remove tail / remove watch | `test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors` |
| M7 Firefox case | `test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors` |
| M8 unchecked browser / monitor | `test_g3_browser_and_monitor_probes_gate_the_row` |
| M9 reorder / drop probe | `test_g3_browser_and_monitor_probes_gate_the_row` |
| M10 `(?:…)`, `\b`, `\d`, `\bwatch\b` | **No distinct failure demonstrated**; only baseline G4 environment failure |

Deviations: added two watch dialect positives to exercise A2’s concrete counterexample. The full module used an explicitly disclosed skip wrapper. No commit, network request, process signal, or desk-proof authoring occurred.

## Residual risk

**What the lead should double-check:** rule on M10’s portable-syntax guard, resolve the full-module cleanup conflict, and replay live probes/G4 with process-list access. The Ed-hands desk proof remains outstanding. The unchanged browser-family limitation includes Edge/Brave; Chrome for Testing matches the ruled pattern.