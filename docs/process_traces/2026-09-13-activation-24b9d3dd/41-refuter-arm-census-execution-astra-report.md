```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No execution defect found: fidelity holds and M1–M9 are killed; one documentation nit remains.",
  "workspace": {
    "base_requested": "4b9a3411",
    "base_mode": "descendant",
    "head_start": "4cd8929886256f1e36556732a2598e598d04e1e3",
    "head_end": "4cd8929886256f1e36556732a2598e598d04e1e3",
    "upstream_end": "4b9a34111d33a04727a09127a1c1fbd8aab87052",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "nit",
        "file": "tests/test_arm_readiness_evidence_t0.py",
        "line": 2549,
        "summary": "The four regression docstrings lack the requested ruling pointer and complete terminology glosses.",
        "detail": "Lines 2549, 2556, 2586 and 2628 name M1–M10 without identifying ruling 10 Q3 and synthesis 13's addendum. G4 also leaves decoy and dialect implicit."
      }
    ],
    "fidelity": "Constants at joulewise/arm_readiness_evidence_t0.py:57 match the ruled strings byte-for-byte. Reversing only the comment/constants addition and two call-site replacements restores the entire base module byte-for-byte. Exactly four _fresh_probe calls remain, ordered and labelled keep-awake, agent, browser, monitor. Keep-awake/agent argv, _expect_absent and derived are unchanged.",
    "contract": "NOT a contract change. The requested configs/, joulewise/arm_readiness.py and docs/contracts diff is empty; registry t0.no_stray_keepawake rows and derived fields are untouched.",
    "g3": "Lines 2585–2622 follow the existing test_named_refusal_matrix_covers_every_distinct_kind authoring-fixture pattern. Agent, browser and monitor hits each require T0EvidenceAuthoringError with kind PROCESS_CENSUS and no source/evidence directory. The empty-output control requires PASS. Every case checks all four commands in order. M8 fails because the expected exception disappears; M9 produces three command-list assertion failures plus an error in the PASS control.",
    "g4": "Lines 2639–2658 spawn only owned /bin/sleep children with marker argv0. Real pgrep output must contain that child's PID line and satisfy the pattern; Python re alone cannot supply the line. Exit 1 with no output fails at line 2646; exit 0 with no output fails at line 2648. Ordinary assertion failures execute terminate and wait in finally. Instrumented runs confirmed both children were reaped with returncode -15.",
    "writing": "The module comment at line 55 states the changed browser interpretation plainly. The remaining writing issue is F1."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 -k g1 -k g2 -k g3 -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 13.018s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/ref-arm-census-review.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M1 exit=1",
          "FAIL: test_g1_ruled_census_patterns_ignore_recorded_macos_services",
          "M2 exit=1",
          "FAIL: test_g1_ruled_census_patterns_ignore_recorded_macos_services",
          "M3 exit=1",
          "FAIL: test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors",
          "M4 exit=1",
          "FAIL: test_g1_ruled_census_patterns_ignore_recorded_macos_services",
          "M5 exit=1",
          "FAIL: test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors",
          "M6 exit=1",
          "FAIL: test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors",
          "M7 exit=1",
          "FAIL: test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors",
          "M8 exit=1",
          "FAIL: test_g3_browser_and_monitor_probes_gate_the_row",
          "M9 exit=1",
          "FAIL: test_g3_browser_and_monitor_probes_gate_the_row",
          "FAILED (failures=3, errors=1)",
          "CONTROL PASS; M1-M9 KILLED"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "CONTROL PASS; M1-M9 KILLED"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 -k argv -k fresh_probe -k census -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 3 != 0 : sysmon request failed with error: sysmond service not found",
          "pgrep: Cannot get process list",
          "Ran 10 tests in 7.865s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_real_process_census_executes_pgrep_and_binds_output tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.112s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/ref-arm-census-fidelity.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Constants match ruling byte-for-byte; reversing only authorized hunks restores complete base module byte-for-byte.",
          "Exactly four _fresh_probe calls: keep-awake, agent, browser, monitor; keep-awake/agent argv, _expect_absent, derived unchanged.",
          "Contract diff empty; registry t0.no_stray_keepawake untouched. NOT a contract change."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "NOT a contract change"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/ref-arm-census-cleanup.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "real-pgrep: two assertion failures; both OWN decoys terminated and reaped (returncode=-15).",
          "exit-1-empty: two assertion failures; both OWN decoys terminated and reaped (returncode=-15).",
          "exit-0-empty: two assertion failures; both OWN decoys terminated and reaped (returncode=-15).",
          "Cleanup and non-vacuity checks PASS; mocked cases are not live regex validation."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Cleanup and non-vacuity checks PASS"}
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check 4b9a3411..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "This sandbox cannot list processes: both G4 subtests receive pgrep exit 3. V3's only failures are those subtests. Record 40 independently reports the exact reviewed head passing all 75 module tests, G1–G4 and related modules at the lead bench, with decoys absent afterward.",
      "needs": "Retain record 40 as lead-owned live evidence; this review does not independently establish Darwin regex behavior or the agent-free desk acceptance proof."
    }
  ]
}
```

## Findings

**F1 — nit:** Add a shared pointer to packet 34, ruling 10 Q3 and synthesis 13’s addendum. Define *probe* as one recorded command execution, *decoy* as the test-owned sleep child carrying a marker command line, and *dialect* as the regular-expression syntax interpreted by `pgrep`.

Mutation copies and logs are under `/tmp/ref-arm-census-rgewvyr_/`. M1–M9 respectively exercised the old alternation, missing `( |$)`, Safari-only name, bare `watch`, missing `/Contents/MacOS/`, missing `tail -f`, uppercase `Firefox`, unchecked browser output, and removed monitor probe.

## Residual risk

G4 catches M10 constructs that invalidate the expression (`(?:…)` → exit 2, per the authority) or prevent its required decoy match (`\b`/`\d` → missing decoy line). It does **not** prove every alternative has identical Python/pgrep semantics: replacing only `firefox` with `\bfirefox\b` could leave the Safari decoy passing while losing Firefox detection. No independent live M10 kill is claimed here.

Assertion failures cannot bypass the cleanup block; abrupt runner termination or an OS cleanup failure remains outside that guarantee. The argv-binding test passes even with unavailable process enumeration, so its success is not live census acceptance.

**What the lead should double-check:** resolve F1, retain record 40 against this exact HEAD, and keep the lane open until the separately required agent-free, browser-free desk proof produces the actual source receipt. The canonical full suite was not rerun in this bounded review.