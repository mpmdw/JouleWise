```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented F1–F3 and X1–X4; counterfactuals reproduce the defects. Remaining verification failures are sandbox limitations reproduced at base.",
  "workspace": {
    "base_requested": "328c7e3bc4867d5947098128d052eb4fd4a21500",
    "base_mode": "exact",
    "head_start": "328c7e3bc4867d5947098128d052eb4fd4a21500",
    "head_end": "328c7e3bc4867d5947098128d052eb4fd4a21500",
    "upstream_end": "328c7e3bc4867d5947098128d052eb4fd4a21500",
    "branch": "feat/2026-09-16-reserve-hang-transport"
  },
  "pathspec": [
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_COURIER_PROMPT.md",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
    "joulewise/night_agent_install.py",
    "scripts/gen_derivation_night.py",
    "scripts/night_chains/calibration_derivation_only.zsh",
    "scripts/run_night.py",
    "tests/test_install_night_agent.py",
    "tests/test_run_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "pending_verification"},
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "set -o pipefail\nTMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night tests.test_night_gate tests.test_night_agent_install tests.test_install_night_agent tests.test_gen_derivation_night tests.test_issue_calibration_acceptance_generation 2>&1 | tail -4",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["----------------------------------------------------------------------", "Ran 448 tests in 768.181s", "", "FAILED (failures=1, skipped=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "set -o pipefail\nPYTHONDONTWRITEBYTECODE=1 python3 scripts/quick_suite.py --tier quick --workers 4 2>&1 | tail -5",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["PASS tests.test_ssh_transport seconds=0.098", "STALE WEIGHT tests.test_ssh_transport seconds=0.098 weight=0.001 ratio=97.50", "PASS tests.test_reauthor_clean seconds=32.072", "STALE WEIGHT tests.test_reauthor_clean seconds=32.072 weight=0.334 ratio=96.02", "QUICK SUMMARY tier=quick modules=153 excluded=82 failures=1 seconds=79.224 result=FAIL"]},
      "expected": {"exit_code": 0, "tail_regex": "failures=0.*result=PASS"}
    },
    {
      "id": "V3",
      "kind": "build",
      "cmd": "PYTHONPYCACHEPREFIX=/tmp/rh-fix1-pycache python3 -m compileall -q scripts joulewise\necho compile_rc=$?\nzsh -n scripts/night_chains/calibration_derivation_only.zsh\necho zsh_rc=$?\nTMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/gen_derivation_night.py --check\ngit diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["compile_rc=0", "zsh_rc=0", "PASS generated derivation-night wrapper region matches"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS generated derivation-night wrapper region matches"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rh-scope2-invariants.py --written",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS generator numeric constants and non-prose assignments unchanged", "PASS generated executable lines unchanged except approved chain digest", "PASS historical prose outside generated region byte-identical"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS historical prose outside generated region byte-identical"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_refuter_round.Install.test_install_rejects_each_changed_or_missing_reservation_input tests.test_refuter_round.Install.test_missing_input_digests_refuses_install tests.test_refuter_round.Probe.test_execute_chain_carries_pre_reserve_strict_flag tests.test_refuter_round.Probe.test_receipt_checks_mtime_and_finished_clock_bounds tests.test_refuter_round.Probe.test_probe_deadline_covers_blocked_binding_read tests.test_refuter_round.Driver.test_driver_census_abort_keeps_precedence_over_calibration_document tests.test_refuter_round.Driver.test_calibration_document_exit_code_must_match_self_exit",
      "cwd": "/tmp/rh-transport-fix1-base",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["----------------------------------------------------------------------", "Ran 7 tests in 12.765s", "", "FAILED (failures=15, errors=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short\ngit diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/phase_2/derivation_night_runbook.md",
          " M docs/process/NIGHT_COURIER_PROMPT.md",
          " M docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
          " M joulewise/night_agent_install.py",
          " M scripts/gen_derivation_night.py",
          " M scripts/night_chains/calibration_derivation_only.zsh",
          " M scripts/run_night.py",
          " M tests/test_install_night_agent.py",
          " M tests/test_run_night.py",
          " docs/phase_2/derivation_night_runbook.md           |  32 ++--",
          " docs/process/NIGHT_COURIER_PROMPT.md               |   7 +-",
          " .../2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md |  13 +-",
          " joulewise/night_agent_install.py                   |  41 ++++-",
          " scripts/gen_derivation_night.py                    |  15 +-",
          " .../night_chains/calibration_derivation_only.zsh   |  23 ++-",
          " scripts/run_night.py                               | 187 +++++++++++++++------",
          " tests/test_install_night_agent.py                  |  61 ++++++-",
          " tests/test_run_night.py                            | 122 +++++++++++++-",
          " 9 files changed, 414 insertions(+), 87 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "9 files changed"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "V1's sole failure is the live OS-build probe: sysctl is denied and os_build is None. V2's two failures in tests.test_axi_controller_events report campaign start identity unavailable. Both failures reproduce at 328c7e3b. Three real process-census tests skip because pgrep is unavailable.",
      "needs": "Lead rerun in the normal environment, including the skipped process-census tests."
    },
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Seat A's strict reservation behavior is exercised through a fake CLI boundary here; no Seat A modules were imported.",
      "needs": "Lead integrate Seat A and replay the interrupted-claim strictness case."
    }
  ]
}
```

## Change

`reservation_input_paths()` uses `_chain_environment()` and the chain’s expanded `reservation_call` arguments to discover inputs. Receipts bind all six current input files; validation rejects changed or missing files and missing digest maps. Render-only exposes the bindings. The entire probe now runs under one supervised deadline, including binding reads. Driver aborts retain their established verdict, reason and exit code; calibration documents remain evidence.

The chain requests `--pre-reserve-strict`, preserving refusal before retry, recovery or append with one bounded custody pass. The separate advisory JSON report—including pin, claim and custody diagnostics—is gone; Seat A’s compact `pre_reserve_readiness` line supplies frozen-plan bindings and elapsed time instead. Timing, settle, slot and capture blocks remain byte-identical. The regenerated region pins the new chain digest; future plans must re-pin. No commits or repository Git writes were made.

## Verification notes

Counterfactuals used the requested `/tmp` copy, restored production and existing fixtures with read-only `git show 328c7e3b:<path>`, and overlaid only seven new regression methods. Confirmed failures:

- F1: changed/missing calibration-plan, identity and T1 inputs admitted: `AssertionError: 2 != 0`.
- F2: `AssertionError: '--pre-reserve-strict' not found in [...]`.
- X2: `AssertionError: 4 != 3`; exit mismatch also yielded `'document_invalid' != 'calibration_ledger_custody_timeout'`.
- X3: stale mtime admitted: `AssertionError: Refused not raised`. Base additionally rejects the newly permitted 30-second future skew.
- X4: `AssertionError: probe exceeded whole deadline during binding read`.

The focused run passed: `Ran 13 tests in 9.428s`, `OK (skipped=3)`. The fixed FIFO case produces a timeout receipt within tolerance and leaves no worker survivor. Production process-group termination policy is unchanged.