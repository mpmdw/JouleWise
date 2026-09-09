```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Authored all four artifacts and recorded dry-validation rc 0; NEEDS_RULING remains for production identity, custody, T0 and duration.",
  "workspace": {
    "base_requested": "main ac092ccd",
    "base_mode": "exact",
    "head_start": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "head_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "upstream_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "branch": "feat/2026-09-08-g2a-first-window-plan"
  },
  "pathspec": [
    "docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/night_plan.draft.json",
    "docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/README.md",
    "docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/validate_plan.py",
    "docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/preflight.log"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/.venv/bin/python -B docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/validate_plan.py --t0 2026-09-10T02:56:00-07:00 --window-max-s 10800 --plan-id DRY-ONLY-g2a-20260910 --custody-root /Users/edr/night-custody/DRY-ONLY-g2a-20260910 --authored-at 2026-09-10T01:56:00-07:00",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS dry validation only; magistrate inputs are not approved and no live gate was evaluated"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS dry validation only; magistrate inputs are not approved and no live gate was evaluated$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/.venv/bin/python -B docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/validate_plan.py --t0 2026-09-10T02:56:00-07:00 --window-max-s 14340 --plan-id DRY-ONLY-g2a-20260910 --custody-root /Users/edr/night-custody/DRY-ONLY-g2a-20260910 --authored-at 2026-09-10T01:56:00-07:00",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "FAIL window plus 300-second courier budget must end strictly before dead-man"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAIL window plus 300-second courier budget must end strictly before dead-man"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the runbook leaves PLAN_ID, NIGHT_ROOT, actual local T0/date and WINDOW_MAX_S to the magistrate. Explicit placeholders remain; logged sample inputs are non-authorizing.",
      "needs": "Rule these inputs together after rehearsal acceptance and custody/runtime review."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Real readiness remains blocked: clone has pre-existing untracked joulewise.egg-info/, normalized lock comparison includes extra joulewise==0.1.0, and the ledger loader reports calibration_ledger_missing and calibration_ledger_rollback. Clone preserved read-only.",
      "needs": "Magistrate resolves these prerequisites under separate clone write authority before real arming."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Full preflight was not run because it invokes sudo and MLX imports; the safe independent subset and its failures are logged. No hardware, measurement, custody publication or installation occurred.",
      "needs": "Lead owns live prerequisite verification, rehearsal acceptance, handback/head reconciliation and email-then-arm."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "preflight.log exists but matches the repository ignore rule.",
      "needs": "Explicitly include this exact evidence file in any later lead-owned commit."
    }
  ]
}
```

## Change

Created the complete-key draft, clone-backed validator, evidence log and magistrate procedure. Only authorized paths changed; no commit or arm occurred.

## Verification notes

Focused checks replaced the full suite for this trace-tooling task. The validator also rejects timezone-less T0 values. README shell and embedded Python syntax passed inspection.

## Residual risk

**NEEDS_RULING:** Which production identity, custody root, T0 and duration should replace the placeholders?

**Options considered:** assume the sample schedule, or await reviewed magistrate inputs. **Recommendation:** retain placeholders until ruled. **Blocked work:** final production values and arm-readiness certification.