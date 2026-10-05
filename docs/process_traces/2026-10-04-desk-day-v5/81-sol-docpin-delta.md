```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — two guard gaps accept six contradictory clock instructions; the requested pytest suite passes.",
  "workspace": {
    "base_requested": "3180dafb",
    "base_mode": "exact",
    "head_start": "dd46b1a72eda15652e84e82c5d48aef68200dd60",
    "head_end": "dd46b1a72eda15652e84e82c5d48aef68200dd60",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "path": "joulewise/arm_readiness_evidence.py",
        "line": 960,
        "title": "Restore and resync instructions still bypass the contradiction guard",
        "evidence": "The earlier probe's restore_2 and extended probe's new_1 through new_4 evaluate clock.network_time_policy as PASS, emitting restore_on_after_window:false and resync_only_in_arm_step:true.",
        "recommendation": "Restore rejection of implicit clock references and reject unapproved toggle/resync/restart instructions; add these five regressions."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "path": "joulewise/arm_readiness_evidence.py",
        "line": 964,
        "title": "The allowed ON command is not bound to the cold-credential exercise",
        "evidence": "Appending a new After both backups, execute: fenced block in section 5A containing /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on derives a PASS clock-policy row with restore_on_after_window:false.",
        "recommendation": "Bind the command exception to its governed exercise context, rather than permitting the exact command anywhere in section 5A."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env TMPDIR=/tmp/dd5-dprev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-dprev2/probe.py > /tmp/dd5-dprev2/probe.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["SUMMARY: 25 cases; 1 unexpected PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^SUMMARY: 25 cases; 0 unexpected PASS$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env TMPDIR=/tmp/dd5-dprev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-dprev2/extended-probe.py > /tmp/dd5-dprev2/extended-probe.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["SUMMARY: 30 cases; 4 mismatches"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^SUMMARY: 30 cases; 0 mismatches$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env TMPDIR=/tmp/dd5-dprev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-dprev2/command-context-probe.py > /tmp/dd5-dprev2/command-context-probe.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["SUMMARY: 1 cases; 1 mismatches"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^SUMMARY: 1 cases; 0 mismatches$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --quiet 85d67b12 dd46b1a7 -- configs/arm_readiness/d117_row_registry_v1.json configs/campaigns 'tests/fixtures/histsem*'",
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
      "kind": "lint",
      "cmd": "env TMPDIR=/tmp/dd5-dprev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "env TMPDIR=/tmp/dd5-dprev2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-dprev2/pc tests/test_arm_readiness_evidence.py tests/test_check_window_provenance.py tests/test_docs_freshness.py tests/test_receipt_histsem.py > /tmp/dd5-dprev2/pytest.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["159 passed, 1 skipped, 9 warnings, 660 subtests passed in 3386.99s (0:56:26)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^159 passed, 1 skipped, .*660 subtests passed"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --quiet 85d67b12 dd46b1a7 -- tests/fixtures/historical_clock_restore_5a.md configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json",
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
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "dd46b1a72eda15652e84e82c5d48aef68200dd60"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)\\ndd46b1a72eda15652e84e82c5d48aef68200dd60$"
      }
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The shell has no python alias; the generator check was rerun successfully using the existing repository virtualenv interpreter.",
      "needs": ""
    }
  ]
}
```

## Findings

REVIEW: FAIL

**F1 — blocker:** The [contradiction guard](/Users/edr/code/JouleWise-wt-dd5-dprev2/joulewise/arm_readiness_evidence.py:960) accepts these §5A additions while certifying the clock-policy row as PASS:

- “After the whole-window verdict, and the backup, re-enable it.”
- “After both backups, toggle network time.”
- “After close-out, let timed resync.”
- “After both backups, re-sync the clock from time.apple.com.”
- “After the verdict, restart timed to synchronize the clock.”

The first regresses from the earlier guard. The others miss its topic or enabling-word patterns. Evidence: [original probe results](/tmp/dd5-dprev2/probe-results.json), [extended results](/tmp/dd5-dprev2/extended-results.json).

**F2 — blocker:** The [command exception](/Users/edr/code/JouleWise-wt-dd5-dprev2/joulewise/arm_readiness_evidence.py:964) permits the exact ON command anywhere in §5A. A newly added “After both backups, execute:” fenced block containing that command still produces PASS. Bind the exception to the cold-credential exercise. Evidence: [context probe](/tmp/dd5-dprev2/command-context-probe.py), [results](/tmp/dd5-dprev2/command-context-results.json).

All 16 Fable lines and three weakening edits refuse correctly. Current runbook and pure re-wrap pass. The §12 fenced restore, malformed backup counts, required-backups value 3, and frozen `systemsetup` command refuse. Archival bytes and generator checks pass; pytest reports **159 passed, 1 skipped, 660 subtests passed**.

Checkout remains clean at `dd46b1a7`. All launched commands exited.

## Residual risk

Adversarial probes used synthetic committed packs; no live hardware validation was performed.