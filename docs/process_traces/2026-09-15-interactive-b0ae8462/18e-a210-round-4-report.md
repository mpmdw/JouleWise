```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented Ed's ratified 8/8/6/5 ladder across all nine authorized files; 197 focused tests pass; canonical verification requires process-inspection access.",
  "workspace": {
    "base_requested": "4ee42850483a43e893932b0628dbb8f2705abb73",
    "base_mode": "exact",
    "head_start": "4ee42850483a43e893932b0628dbb8f2705abb73",
    "head_end": "4ee42850483a43e893932b0628dbb8f2705abb73",
    "upstream_end": "4ee42850483a43e893932b0628dbb8f2705abb73",
    "branch": "feat/2026-09-15-lead-margin"
  },
  "pathspec": [
    "scripts/run_night.py",
    "scripts/magistrate_watchdog.py",
    "tests/test_run_night.py",
    "tests/test_magistrate_watchdog.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/process/MAGISTRATE_RELAUNCH_PROMPT.md",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/decision_log.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 197 tests in 21.049s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 197 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_generated_gamma_roots_pass_and_legacy_keys_are_refused",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 2 tests in 1.572s", "FAILED (failures=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
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
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-a210d-20260916.json --expect-digest sha256:2d6b46d4bc3039fc718fffc20f961bb370dc2a7773646b695aeecc8f3cb1969a --lease-id lease-e745440a8a024e9d827fef8b2dfdaaac --scope scripts/run_night.py scripts/magistrate_watchdog.py tests/test_run_night.py tests/test_magistrate_watchdog.py docs/phase_2/derivation_night_runbook.md docs/process/NIGHT_HANDBACK.md docs/process/MAGISTRATE_RELAUNCH_PROMPT.md docs/process/MAGISTRATE_WATCHDOG.md docs/decision_log.md | python3 -c 'import json,sys; result=json.load(sys.stdin); print(result[\"verdict\"]); sys.exit(result[\"verdict\"] != \"SCOPE_OK\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["SCOPE_OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^SCOPE_OK$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "rg -n '(^|[^0-9])[532] \\* 60|t0 − 7|seven-minute|two minutes of the request|5/5/3/2' scripts/run_night.py scripts/magistrate_watchdog.py tests/test_run_night.py tests/test_magistrate_watchdog.py docs/phase_2/derivation_night_runbook.md docs/process/NIGHT_HANDBACK.md docs/process/MAGISTRATE_RELAUNCH_PROMPT.md docs/process/MAGISTRATE_WATCHDOG.md docs/decision_log.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/magistrate_watchdog.py:88:KILL_LEAD_S = 5 * 60",
          "scripts/magistrate_watchdog.py:90:REMOTE_STOP_PROBE_CADENCE_S = 5 * 60",
          "tests/test_magistrate_watchdog.py:397:            t0=self.base.timestamp() + 5 * 60 * 60,",
          "tests/test_magistrate_watchdog.py:912:        self.harness.clock.mono += 5 * 60",
          "docs/decision_log.md:11010:**RATIFIED by Ed 2026-09-16 00:20 PDT ('do whichever is safest first quick second'): the conservative 8/8/6/5 chain; the 5/5/3/2 variant is recorded as the quick alternative for a later ruling**",
          "scripts/run_night.py:75:INSTALL_CLOSE_MARGIN_S = 2 * 60"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "KILL_LEAD_S = 5 \\* 60"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Canonical suite produced two failing subtests in test_g4_real_ruled_census_pgrep_dialect: pgrep exited 3 with 'sysmon request failed with error: sysmond service not found' and 'pgrep: Cannot get process list'. Reproduced separately; the generated-gamma-roots test passed. Canonical run was then intentionally interrupted, so no full-suite pass is claimed.",
      "needs": "Lead rerun python3 -m unittest discover -s tests in an environment permitting process inspection, then perform final review."
    }
  ]
}
```

## Change

Every changed site:

- **Watchdog implementation:** timing rationale, four constants, and `standdown.request.exit_within_s = 300`.
- **Night driver:** ten-minute installation-floor comment; pad remains 120 seconds.
- **Watchdog tests:** boundary pins, disjoint/touching epochs, ladder/order/poll assertions, courtesy/deadline regression, drain-test timing/name, and prompt assertion. Retained `KILL + SETTLE ≥ 600`.
- **Night-driver tests:** fixed installation epoch updated to `1799999400`.
- **Derivation runbook:** fence definition, §0.6 deadlines, §1.3 timing/ratification/decay arithmetic, worked schedule, exit boundary, installation assertion, handback/evidence instructions, source tables, and glossary.
- **Night handback:** timeline, ladder/decay explanation, interactive exit instruction, rehearsal allowance, four schedule rows, and notice-template boundaries.
- **Relaunch prompt:** five-minute courtesy; absolute TERM/KILL at −6/−5.
- **Watchdog guide:** state descriptions, fence/deadline table, timing/decay/ratification explanation, replacement-drain instructions, dry-run example at `now + 8`, and adoption rehearsal at `now + 13`.
- **Decision log:** requested ratification text, revised idle/decay budget, and both later A210 boundary references.

## Verification notes

The five-minute courtesy does not extend TERM: an on-time request still reaches TERM after two minutes.

The scan’s six hits are listed in V6: required new KILL timing, unchanged installation/probe timers, unrelated test intervals, and the explicitly retained historical quick alternative. No `t0 − 7`, `seven-minute`, or `two minutes of the request` remains.

The allowlist contains five documentation files; all five were swept. Canonical verification remains blocked by the reproduced process-inspection limitation. Next step: lead reruns the canonical suite and reviews the final diff.