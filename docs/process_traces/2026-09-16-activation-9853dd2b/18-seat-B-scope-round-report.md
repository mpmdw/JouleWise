```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Updated generator prose and regenerated only its runsheet region; constants and historical prose are unchanged.",
  "workspace": {
    "base_requested": "d1aadecccb397cdd5040cb252908c80290177def",
    "base_mode": "exact",
    "head_start": "d1aadecccb397cdd5040cb252908c80290177def",
    "head_end": "d1aadecccb397cdd5040cb252908c80290177def",
    "upstream_end": "d1aadecccb397cdd5040cb252908c80290177def",
    "branch": "feat/2026-09-16-reserve-hang-transport"
  },
  "pathspec": [
    "scripts/gen_derivation_night.py",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
  ],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "pending_verification"},
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "set -o pipefail; TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_gen_derivation_night tests.test_issue_calibration_acceptance_generation 2>&1 | tee /tmp/rh-scope2-fixtures.log | tail -4",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["----------------------------------------------------------------------", "Ran 154 tests in 86.688s", "", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "set -o pipefail; TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night tests.test_night_gate tests.test_night_agent_install tests.test_install_night_agent 2>&1 | tee /tmp/rh-scope2-focused.log | tail -5",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 285 tests in 678.585s", "OK (skipped=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 scripts/quick_suite.py --tier quick --workers 4 2>&1 | tee /tmp/rh-scope2-quick.log | tail -5",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "PASS tests.test_ssh_transport seconds=0.123",
          "STALE WEIGHT tests.test_ssh_transport seconds=0.123 weight=0.001 ratio=122.73",
          "PASS tests.test_reauthor_clean seconds=32.769",
          "STALE WEIGHT tests.test_reauthor_clean seconds=32.769 weight=0.334 ratio=98.11",
          "QUICK SUMMARY tier=quick modules=153 excluded=82 failures=1 seconds=88.818 result=FAIL"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "failures=0.*result=PASS"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "PYTHONPYCACHEPREFIX=/tmp/rh-scope2-pycache python3 -m compileall -q scripts joulewise; echo compile_rc=$?; zsh -n scripts/night_chains/calibration_derivation_only.zsh; echo zsh_rc=$?",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["compile_rc=0", "zsh_rc=0"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)compile_rc=0.*zsh_rc=0"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/rh-scope2-invariants.py --written; PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS generator numeric constants and non-prose assignments unchanged",
          "PASS generated executable lines unchanged except approved chain digest",
          "PASS historical prose outside generated region byte-identical",
          "PASS generated derivation-night wrapper region matches"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS generated derivation-night wrapper region matches"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short; git diff --stat; git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
          " M scripts/gen_derivation_night.py",
          " .../2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md | 28 +++++++-----",
          " scripts/gen_derivation_night.py                    | 51 ++++++++++++++--------",
          " 2 files changed, 50 insertions(+), 29 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "2 files changed"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "/usr/sbin/sysctl -n kern.osversion",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["sysctl: sysctl fmt -1 1024 1: Operation not permitted"]},
      "expected": {"exit_code": 0, "tail_regex": ".+"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Both generated-region failures are resolved. The required 154-test run is not fully green here: test_live_probes_report_this_machine_against_the_active_epoch fails because the sandbox denies kern.osversion. The identity test was not skipped or weakened.",
      "needs": "Lead rerun the two modules where sysctl is permitted."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Quick tier reproduces the two existing test_axi_controller_events failures (expected 1, got 2; campaign start identity unavailable), previously confirmed on 3015cb39.",
      "needs": "Lead environment verification."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Scope ruling applied only to generator explanatory text and its generated region. No Git write commands, commits, real launchctl, network, or measurement work.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Updated emitted comments change future wrapper digests; regenerate and pin wrappers. This round changes no timing, capture, slot or settle constants.",
      "needs": ""
    },
    {
      "id": "F5",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The four-module run retains three existing real-process probe skips because process census is unavailable in this sandbox.",
      "needs": "Lead rerun skipped process checks where pgrep is available."
    }
  ]
}
```

## Change

The preserved property is **refusal before any reservation or ledger write, and before settle or capture**. The removed `readiness --phase pre-reserve` command provided an early, non-authorizing check; under the adopted Seat A interface, reservation’s shared bounded enforcing preflight now provides that ordering. Removing the separate command loses its independent stdout JSON: the successful readiness report with `early_warning_only: true` and `frozen_plan` bindings, or its standalone refusal containing readiness context. Literal runsheet command and diagnostic-output parity is therefore lost, while refusal-before-write remains the required integration property.