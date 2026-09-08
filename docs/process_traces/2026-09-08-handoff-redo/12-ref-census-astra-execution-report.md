```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "No execution findings: all eight supplied process shapes classify correctly, 90 scoped tests pass, and both targeted mutations are caught.",
  "workspace": {
    "base_requested": "d8ad6c15",
    "base_mode": "exact",
    "head_start": "898e530519a14f1e97b40f84ae835ca7ebfe20f2",
    "head_end": "898e530519a14f1e97b40f84ae835ca7ebfe20f2",
    "upstream_end": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 90 tests in 21.296s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 \"$TMPDIR/refuter_execution_probe.py\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PS_PARSER 8 rows classified identically",
          "DEAD_LOCK HOLD_UNSAFE dead_lock_resumed_twin: pids=[71607] lock preserved",
          "LOCK_CENSUS live resident fails; leaked stub alone passes",
          "ALL_EXECUTION_PROBES_PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "ALL_EXECUTION_PROBES_PASS"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "/bin/zsh -n \"$TMPDIR/refuter-execution-artifacts/reaper.zsh\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Concurrent main moved from d8ad6c15d48a41ad9e562ce9845bf8fb874826bb to e4ce8b3bece33db40de68b6c407a514fbaed9a26. Detached review HEAD and its parent remained unchanged.",
      "needs": "Apply this review to the pinned landing; assess subsequent integration separately."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "zsh -n returned 0 with a sandbox nice(5) operation-not-permitted warning for the background command.",
      "needs": ""
    }
  ]
}
```

## Findings

None.

| PID | Role | Interactive |
|---|---|---|
| 71607 | `resumed_twin` | Yes |
| 71596 | `bg_pty_host` | No |
| 71666 | `daemon` | No |
| 71682 | `bg_pty_host` | No |
| 71687 | `bg_spare` | No |
| 83953 | None; selected interactive root | Yes |
| 84232 | None; headless resident | No |
| 48645 | None; headless test stub | No |

The production process-table parser preserved these classifications. Inventory included 83953 and its synthetic Codex child as owned, with the five resume-machinery processes as candidates.

The installer, exercised through its temporary shadow fixture, **refused with exit 1** for each supplied daemon/host/spare shape before creating a plist or lock.

The documented reaper was extracted inclusively from `watchdog_checkout=` through `   PY`, stripping three spaces. Its Python ran with injected process tables:

- Alive before TERM, then exits → `term_exited`.
- Absent before TERM → `already_gone`, no signal.
- Requires KILL → `kill_exited`.

Both independent temporary-copy mutations failed their named regression:

- Removing lock-owner inclusion failed `test_handoff_census_ignores_unrelated_claude_but_requires_owned_and_lock_absence`.
- Removing preservation of TERM evidence failed `test_reaper_preserves_signal_time_evidence_and_passes_with_unrelated_claude`, producing `already_gone` instead of `term_exited`.

Replay script and evidence: `$TMPDIR/refuter_execution_probe.py` and `$TMPDIR/refuter-execution-artifacts/probe.log`.

## Residual risk

This verifies supplied command shapes and fake process transitions, not live daemon retirement or signal delivery.

The next handoff must still resolve the existing resident: a live lock owner such as 84232 correctly fails the scoped census. A dead lock with 71607 present correctly returns `HOLD_UNSAFE` and preserves the lock. The leaked stub alone does not fail the scoped handoff; machine-wide night census semantics remain unchanged.