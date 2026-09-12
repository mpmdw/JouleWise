```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented portable bootstrap and both regressions; V1 requires an out-of-scope no-courier fixture adjustment.",
  "workspace": {
    "base_requested": "1b893ec4",
    "base_mode": "exact",
    "head_start": "1b893ec46240424da478888a344fb2e159888de1",
    "head_end": "1b893ec46240424da478888a344fb2e159888de1",
    "upstream_end": "1b893ec46240424da478888a344fb2e159888de1",
    "branch": "fix/2026-09-11-night-interpreter-pin"
  },
  "pathspec": [
    "scripts/install_night_agent.sh",
    "tests/test_install_night_agent.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "export TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1\npython3 -m unittest tests.test_install_night_agent tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAIL: test_installer_refuses_when_command_lookup_has_no_courier (tests.test_run_night.NightDriverTests.test_installer_refuses_when_command_lookup_has_no_courier)",
          "AssertionError: 'courier unavailable' not found in 'cannot derive measurement_root/.venv/bin/python from /private/tmp/tmpi8yh9120/no-courier/install-plan.json; pass --python ABS_PATH\\n'",
          "----------------------------------------------------------------------",
          "Ran 108 tests in 34.422s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 108 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "/bin/zsh -n scripts/install_night_agent.sh",
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
    },
    {
      "id": "V3",
      "kind": "build",
      "cmd": "export TMPDIR=/tmp PYTHONPYCACHEPREFIX=/tmp/night-interpreter-pin-round3-pycache\npython3 -m compileall -q scripts joulewise",
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
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "export TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1\npython3 /tmp/night-interpreter-pin-round3-render.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "stdout:",
          "{\"preflight\": \"ok\", \"python\": \"/opt/homebrew/opt/python@3.14/bin/python3.14\", \"version\": \"3.14.7\", \"modules\": [\"scripts.run_night\", \"joulewise.arm_readiness\", \"joulewise.arm_readiness_evidence_t0\", \"joulewise.t0_rehearsal\", \"joulewise.night_gate\", \"joulewise.measurement_liveness\"]}",
          "validated pins: repo_head=1b893ec46240424da478888a344fb2e159888de1 measurement_root=/private/tmp/tmpvokv9oe3/measurement checkout measurement_head=08a608ca3cd61fbdf03c3333722fc3c99d999d93",
          "stderr:",
          "git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead",
          "git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead",
          "rc: 0",
          "com.joulewise.night.deadman.plist: ProgramArguments[0] == /private/tmp/tmpvokv9oe3/measurement checkout/.venv/bin/python",
          "com.joulewise.night.plist: ProgramArguments[0] == /private/tmp/tmpvokv9oe3/measurement checkout/.venv/bin/python"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "rc: 0[\\s\\S]*ProgramArguments\\[0\\] == .*measurement checkout/\\.venv/bin/python"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "grep -c plutil scripts/install_night_agent.sh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["0"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^0\\n?$"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "export TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1\npython3 -m unittest tests.test_install_night_agent.InstallNightAgentTests.test_installer_has_no_plutil_dependency tests.test_install_night_agent.InstallNightAgentTests.test_default_python_derivation_with_only_path_python3",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 2 tests in 1.093s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests[\\s\\S]*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Scope expansion required; no out-of-scope edit performed. tests/test_run_night.py:1571 supplies an empty PATH and expects courier unavailable, conflicting with the required refusal when PATH provides no python3.",
      "needs": "Authorize tests/test_run_night.py or have the lead adjust its no-courier fixture, then rerun V1."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Local checks ran on macOS Python 3.14.7; Ubuntu CI was not executed. Full discovery was not run for this bounded installer tooling fix.",
      "needs": "Lead reruns the Linux CI oracle after resolving F1."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_run_night.py"],
    "reason": "The no-courier regression must provide the newly required bootstrap python3 while keeping courier absent.",
    "blocked_work": "V1 cannot pass with the existing empty-PATH fixture and the required no-python3 refusal semantics.",
    "minimal_change": "Add (empty_path / \"python3\").symlink_to(sys.executable) after creating empty_path in test_installer_refuses_when_command_lookup_has_no_courier; preserve its assertions."
  }
}
```

## Change

Replaced the bootstrap with ambient `python3 -B -S` using only stdlib JSON parsing. Added the compatibility comment and empty-result refusal. Preserved every existing test and added both requested regressions. No commits or real installations.

## Verification notes

Against `1b893ec4`, the text tripwire fails because the installer contains `plutil`; the restricted-PATH regression fails on Linux because `/usr/bin/plutil` is absent. The latter would still pass on macOS, so it does not independently detect the defect there.

Additional manual checks confirmed exact refusal text and rc 2 for malformed JSON, missing or empty `measurement_root`, and no PATH `python3`. `git diff --check` passed. V4’s stderr contains only Git temporary-directory warnings.

The next step is the one-line fixture adjustment requested in `scope_expansion`, followed by V1 and Linux CI.