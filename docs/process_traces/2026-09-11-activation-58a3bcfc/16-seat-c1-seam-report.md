```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented and verified the C1 registration correction; committing is blocked by sandbox access to linked-worktree Git metadata.",
  "workspace": {
    "base_requested": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "base_mode": "exact",
    "head_start": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "head_end": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "upstream_end": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "branch": "fix/2026-09-11-c1-registration-seam"
  },
  "pathspec": [
    "docs/phase_2/derivation_night_runbook.md",
    "scripts/gen_derivation_night.py",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
    "tests/test_gen_derivation_night.py",
    "tests/test_night_gate.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 97 tests in 23.027s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 97 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "build",
      "cmd": "PYTHONPYCACHEPREFIX=/private/tmp/joulewise-c1-registration-pycache python3 -m compileall -q scripts joulewise",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["updated docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(updated|unchanged).*SHAKEDOWN-G2-RUNSHEET.md"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated derivation-night wrapper region matches"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS generated derivation-night wrapper region matches$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_derivation_night.GeneratedRegionTests.test_the_example_plan_is_one_the_driver_would_accept tests.test_night_gate.RegistrationSeamTests -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 0.002s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 4 tests[\\s\\S]*OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "grep -n registration_path docs/phase_2/derivation_night_runbook.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "500:`registration_path` is `night_gate.D166_REGISTRATION_PATH`, the D-166 literal",
          "778:| `registration_path` | `night_gate.D166_REGISTRATION_PATH` — the fixed D-166 registration path required for this receipt class by the night gate (§0.5), `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` |",
          "1256:`registration_path` equal to `night_gate.D166_REGISTRATION_PATH`, the fixed",
          "1305:assert plan.registration_path == night_gate.D166_REGISTRATION_PATH",
          "1416:| 1. Frozen plan and gate registration | `plan_id`, the night's identifier; the frozen plan's SHA-256, equal to the wrapper's `PLAN_SHA256` literal (its recorded plan digest); and the plan's `registration_path` verbatim, equal to `night_gate.D166_REGISTRATION_PATH` (the fixed D-166 registration path required by the gate), with that file's SHA-256 inside `$MEASUREMENT_ROOT` (the measurement clone): `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265` expected. |",
          "2113:`night_refused_registration` (the `registration_path` did not hash to the D-166",
          "2204:| v2 plan required keys, `night_plan_overruns_deadman`, `registration_path`, the 36-hour authoring age | `joulewise/night_gate.py`: `_PLAN_KEYS`, `NightPlan.from_mapping`, `NIGHT_GATE_REASON_CODES`, `NIGHT_DRIVER_REASON_CODES`, `PLAN_MAX_AGE_S` |"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "D166_REGISTRATION_PATH"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "git add and git commit both exited 128: unable to create /Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-c1-seam/index.lock: Operation not permitted. No commits were created.",
      "needs": "Lead: review the five-file diff, then stage and commit it on the existing branch from an authorized environment."
    }
  ]
}
```

## Change

Implemented revision 7, D-166 path/hash assertions, the five-item arm-record table, PASS-route digest binding, and FAIL-route re-hash/STOP instructions. The generator regenerated the runsheet region. Exactly the five authorized files changed.

## Verification notes

T1–T3 were run before implementation while the generator, runbook, gate, and registration files matched `origin/main`: all three failed; T4 passed. Output: `Ran 4 tests`, `FAILED (failures=7)`—T3 contributed five failing subtests.

A subsequent read-only replay loaded baseline generator/runbook content through `git show` into memory and reproduced `tests=4, failures=7, errors=0`. No stash or other checkout was used.

The full repository suite was not run: this is a documentation/example-only tooling change, covered by the required focused suite. Final wording changes were followed by the four seam tests. Compilation placed bytecode in `/private/tmp` to preserve repository scope.

Next step: lead review and commit; no push was attempted.