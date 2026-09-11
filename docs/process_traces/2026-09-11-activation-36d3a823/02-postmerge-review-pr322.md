```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "No cross-unit integration defect found; generator and kernel checks pass, but temporary-directory restrictions block the focused replay and GitHub access blocks reading the PR body.",
  "workspace": {
    "base_requested": "18ab2cc4",
    "base_mode": "exact",
    "head_start": "18ab2cc42efc4b6e75b59aa4b54326e805bd1ca3",
    "head_end": "18ab2cc42efc4b6e75b59aa4b54326e805bd1ca3",
    "upstream_end": "18ab2cc42efc4b6e75b59aa4b54326e805bd1ca3",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "FOLLOW-UP NEEDED",
    "findings": [],
    "lanes": [
      "Focused integration replay with writable /tmp",
      "PR #322 body retrieval and review"
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "gh pr view 322 --repo mpmdw/JouleWise --json body --jq .body",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "error connecting to api.github.com",
          "check your internet connection or https://githubstatus.com"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".+"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff 4c06b3b4..18ab2cc4 --stat; git diff 4c06b3b4..18ab2cc4",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "5 files changed, 178 insertions(+), 16 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5 files changed, 178 insertions\\(\\+\\), 16 deletions\\(-\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS generated derivation-night wrapper region matches"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated derivation-night wrapper region matches$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
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
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate tests.test_launch_window tests.test_write_derivation_night_inputs tests.test_issue_calibration_acceptance_generation tests.test_install_night_agent tests.test_arm_readiness tests.test_run_night tests.test_night_plan_writer tests.test_magistrate_watchdog_cli",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 383 tests in 1.259s",
          "FAILED (errors=316)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_derivation_night.GeneratedRegionTests tests.test_night_gate.RegistrationSeamTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 9 tests in 0.442s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "rg -l 'night_gate|gen_derivation_night' tests -g 'test_*.py' | sort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_arm_readiness.py",
          "tests/test_gen_derivation_night.py",
          "tests/test_install_night_agent.py",
          "tests/test_issue_calibration_acceptance_generation.py",
          "tests/test_launch_window.py",
          "tests/test_magistrate_watchdog_cli.py",
          "tests/test_night_gate.py",
          "tests/test_night_plan_writer.py",
          "tests/test_run_night.py",
          "tests/test_write_derivation_night_inputs.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_write_derivation_night_inputs.py"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The sandbox denies temporary-file creation, including under /tmp. The requested 383-test replay produced 316 error records; a compact per-module rerun classified every error as FileNotFoundError: No usable temporary directory found. These are environment errors, not established repository defects.",
      "needs": "Lead reruns V5 at 18ab2cc4 with writable /tmp; no full-suite run is requested."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The requested gh command could not reach api.github.com, so the PR body was not read. The supplied terminal review and full merged diff were read.",
      "needs": "Retrieve and review the PR #322 body before closing this integration gate."
    }
  ]
}
```

## Findings

No **BLOCKER**, **SHOULD_FIX**, or **NIT** integration defect established.

1. **Runbook coherence:** Read end to end. The two merges preserve consistent instructions:
   - `docs/phase_2/derivation_night_runbook.md:506`, `:801`, `:1279`, and `:1349` select D-166 for `registration_path`.
   - `:301`, `:1289`, and `:1374` consistently select `$MEASUREMENT_ROOT/.venv/bin/python` through `$PY` and installer `--python "$PY"`.
   - `:1296` correctly distinguishes the chain interpreter from the installer’s driver selection.
   - `:1461`, `:1794`, and `:1858` retain the separate scientific pre-registration digest requirements.
   - No merge-induced duplication, orphaned paragraph, or broken step numbering found. The arm block remains steps 1–7.

2. **Gate → writer → generator:** The constant at `joulewise/night_gate.py:39` equals the runbook literal:
   ```
   configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json
   ```
   `joulewise/night_plan_writer.py:17` preserves the top-level field through `dataclasses.asdict`; `write_night_plan` at `:45` publishes that serialization. `NightPlan.from_mapping` reads it at `joulewise/night_gate.py:336`, and C1 consumes it at `:1302`. The generator agrees at `scripts/gen_derivation_night.py:687`.

   An in-memory serialization/parser/gate check, using real registration bytes and fixture machine probes, produced:
   ```
   sha256=dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265
   example_plan=PASS
   DIAGNOSTIC_NO_PACK: writer_serialization=PASS gate_C1=PASS
   REHEARSAL_STUB: writer_serialization=PASS gate_C1=PASS
   ```

   Generator command V3:
   ```
   PASS generated derivation-night wrapper region matches
   ```
   Exit **0**.

3. **Handback:** The actual file is `docs/process/NIGHT_HANDBACK.md`; the supplied `docs/phase_2/` path does not exist. Its plan-authoring instruction at `:122–126` names the canonical writer but **does not mention `registration_path` anywhere**. It supplies no conflicting path. Its interpreter instructions at `:132–138` and `:160–165` agree with the runbook.

4. **Kernel drift:** `.github/workflows/ci.yml:33–34` defines `python scripts/gen_state.py --check`. V4 ran the same script with `python3`: **exit 0, empty output**.

5. **Focused tests:** The search in V7 selected ten modules, including the two touched modules. V5 attempted all of them; no full suite ran.

   | Module (`tests/test_*.py`) | Tests | Error records |
   |---|---:|---:|
   | gen_derivation_night | 40 | 35 |
   | night_gate | 58 | 3 |
   | launch_window | 38 | 39 |
   | write_derivation_night_inputs | 16 | 12 |
   | issue_calibration_acceptance_generation | 36 | 42 |
   | install_night_agent | 25 | 25 |
   | arm_readiness | 71 | 63 |
   | run_night | 85 | 85 |
   | night_plan_writer | 8 | 8 |
   | magistrate_watchdog_cli | 6 | 4 |
   | **Total** | **383** | **316** |

   Zero assertion failures; zero skips. Subtests can produce multiple error records per test. Every error was classified as:
   ```
   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/tmp', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-postmerge-322']
   ```

   The independently runnable generated-region and registration-seam classes passed: **9 tests, OK**.

6. **Process-doc sweep:** No matching document in the requested scope still binds the equivalence-night `registration_path` to the calibration pre-registration markdown or declares this C1 seam unresolved. The alternative paths at `docs/process/MAGISTRATE_WATCHDOG.md:365` and `:455` belong to explicitly fake watchdog rehearsal plans, not equivalence-night instructions.

## Residual risk

The review cannot close its verification gate until F1 and F2 are resolved. The next step is to retrieve the PR body and rerun V5 with writable `/tmp` at the same head. No repository changes, HEAD movement, or live measurement occurred.

**VERDICT: FOLLOW-UP NEEDED — focused integration replay; PR #322 body review.**
## Lead disposition (magistrate 36d3a823, 2026-09-11 10:5x PDT)

No BLOCKER, SHOULD_FIX or NIT integration defect established; runbook coherence, gate constant vs plan writer vs generator, NIGHT_HANDBACK agreement and kernel check reported clean by the reviewer. Its two lanes were sandbox artefacts, both DISCHARGED at the bench in `JouleWise-wt-postmerge-322` at 18ab2cc4: (1) `python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate` → `Ran 98 tests in 12.040s / OK` and `python3 scripts/gen_derivation_night.py --check` → `PASS generated derivation-night wrapper region matches`; (2) the PR body the reviewer could not fetch is `/tmp/magistrate-36d3a823/pr322-body.md` (the 3dab9c89 draft with row 9 = e18a51d6), which the magistrate wrote and read. Row 11 second half for PR #322: satisfied, no follow-up lane.
