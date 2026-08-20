```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Execution audit found one blocker: the generation registry is mutable and can accept a crosswired policy after poisoning.",
  "workspace": {
    "base_requested": "7d4454e",
    "base_mode": "exact",
    "head_start": "7d4454edde2dccd69207831498fc98aa22de47f4",
    "head_end": "6771924ba244e91379ce76f3d59bdb54a52a920b",
    "upstream_end": "6771924ba244e91379ce76f3d59bdb54a52a920b",
    "branch": "detached HEAD"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "Registry operatives are returned as a mutable shared dict.",
        "paths": ["joulewise/calibration_bracketing.py"],
        "evidence": "Fresh probe returned dict; mutating r4 bracket_screen_s from 0.009724 to 0.010818 changed later resolver output and made the r4+n19 crosswire accept.",
        "needs": "Return an immutable or defensive-copy mapping and add a mutation regression."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "Deleted V2 identifiers remain as active wrappers and consumers.",
        "paths": ["scripts/mint_floor_artifact_generalized.py", "tests/test_mint_floor_artifact_generalized.py"],
        "evidence": "V2_ALLOWANCE_RULE/V2_BRACKET_SCREEN_S remain defined and called in the script and throughout active tests; behavior is dynamic, but C4 specified replacement with the new resolver names.",
        "needs": "Remove the compatibility names or obtain an explicit ruling to retain them."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "summary": "Malformed nested operative containers fail open at the direct resolver boundary.",
        "paths": ["joulewise/calibration_bracketing.py"],
        "evidence": "r4 with ratified_operatives set to string, list, or null returned 0.009724 instead of refusing. Missing/non-string/Decimal bracket_screen_s leaf cases did refuse.",
        "needs": "Reject malformed decimal_derivation and ratified_operatives containers explicitly."
      },
      {
        "id": "F4",
        "severity": "nit",
        "summary": "New guard test has a blank line at EOF.",
        "paths": ["tests/test_mint_policy_resolver_guard.py"],
        "evidence": "git diff --check reported: new blank line at EOF.",
        "needs": "Remove the extra EOF blank line."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_mint_estimator",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 37 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=7, errors=6, skipped=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=7, errors=6, skipped=2\\)"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_detection_floor",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_mint_policy_resolver_guard",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "independent inline Python resolver matrix",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["RESOLVER_PROBES=PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "RESOLVER_PROBES=PASS"}
    },
    {
      "id": "V8",
      "kind": "smoke",
      "cmd": "independent inline Python schema_v2 matrix evaluator",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["SCHEMA_CONDITIONALS=BOUND"]},
      "expected": {"exit_code": 0, "tail_regex": "SCHEMA_CONDITIONALS=BOUND"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "one-at-a-time temp-copy literal mutation harness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["GUARD_THREE_OF_THREE=CATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "GUARD_THREE_OF_THREE=CATCH"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "genesis fixture pin and flipped-constant regression harness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["flipped_constant_test_success=False", "constant_restored=True"]},
      "expected": {"exit_code": 0, "tail_regex": "constant_restored=True"}
    },
    {
      "id": "V11",
      "kind": "inspection",
      "cmd": "rg -n --glob '!docs/process_traces/**' --glob '!docs/strategy/**' 'DEFAULT_ACCEPTANCE_BOUND_SHA256|_BRACKET_SCREEN|_ALLOWANCE_RULE|V2_ALLOWANCE_RULE|V2_BRACKET_SCREEN_S' .",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["scripts/mint_floor_artifact_generalized.py:650", "scripts/mint_floor_artifact_generalized.py:651"]},
      "expected": {"exit_code": 0, "tail_regex": "scripts/mint_floor_artifact_generalized.py:65[01]"}
    },
    {
      "id": "V12",
      "kind": "lint",
      "cmd": "git diff --check 7d4454e..6771924",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 2, "tail": ["tests/test_mint_policy_resolver_guard.py:22: new blank line at EOF."]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V13",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests -q",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["KeyboardInterrupt", "test_calibration_writer_crash_matrix.py"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "B1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "All 13 generalized-suite reds stopped at stale synthetic producer pin/set golden hashes; no other red class was observed.",
      "needs": ""
    },
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "jsonschema, fastjsonschema, ajv, and ruby json-schema were unavailable; schema_v2 was checked with an independent evaluator covering its used keywords.",
      "needs": "Repeat with a package-backed validator if required."
    },
    {
      "id": "E2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery was interrupted during the long crash-matrix test; all requested focused S0 suites completed.",
      "needs": "Rerun canonical discovery in a lead-controlled window if required."
    }
  ]
}
```

## Findings

F1 is a release blocker: the resolver registry can be poisoned in-process, after which an r4/n19 crosswire is accepted.

The generalized reds were exactly the expected stale chain: six named errors plus the aggregate hash failure with six mutation labels. The whole-window suite had only the known `embeds_allowance_once` red. All four generations routed correctly in normal probes: n17 r3/r4 → `0.009724`; n19/n19_r2 → `0.010818`. Schema crosswires failed validation, all three guard mutations were caught, and the genesis flip regression failed as intended.

Repo-wide active-code grep found no old genesis name or old estimator/detection literals. Remaining V2 aliases are covered by F2; other matches are historical immutable traces/transcripts.

## Residual risk

The full discovery suite was interrupted during the crash-matrix test, and schema validation used an independent evaluator because standard validator packages were unavailable.