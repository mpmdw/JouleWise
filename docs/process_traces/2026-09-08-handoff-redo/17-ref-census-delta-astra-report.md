```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One blocker: corrupt-lock recovery can unlink while an unrecorded headless owner remains alive; 95 scoped tests pass.",
  "workspace": {
    "base_requested": "898e530519a14f1e97b40f84ae835ca7ebfe20f2",
    "base_mode": "exact",
    "head_start": "b3eeee9a7dc57db1c56b19a288930d542523dfb7",
    "head_end": "b3eeee9a7dc57db1c56b19a288930d542523dfb7",
    "upstream_end": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 1, "should_fix": 0, "nit": 0},
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "file": "docs/process/MAGISTRATE_WATCHDOG.md",
        "line": 191,
        "title": "Saved inventory does not establish absence of the corrupt lock's owner",
        "demonstrating_command": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/watchdog_delta_audit.py",
        "evidence": "With corrupt/{}/non-object lock bytes, saved owned pair (100,T) absent, and live unrecorded PID 84232 running claude -p with the resident launch options, the extracted block prints HANDOFF_DEAD_LOCK_REMOVED and unlinks. HEAD~1 refuses the same input.",
        "impact": "A stale inventory permits removal of ownership protection while a headless magistrate remains alive, enabling overlapping ownership.",
        "recommendation": "Keep corrupt-lock recovery fail-closed unless evidence establishes coverage of the actual prior owner; an arbitrary saved owned list plus resumed-twin detection is insufficient."
      }
    ]
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
        "tail": ["Ran 95 tests in 21.136s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 95 tests in .*\\s+OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/watchdog_delta_audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MUTATION test_c1_reused_pid_disappears_before_kill FAIL AS EXPECTED 1 failures",
          "MUTATION test_c2_corrupt_lock_recovery_checks_saved_owned_pairs FAIL AS EXPECTED 3 failures",
          "DELTA PROBES PASS; C2 UNSAFE CLEAR REPRODUCED"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "DELTA PROBES PASS; C2 UNSAFE CLEAR REPRODUCED"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch; git diff --exit-code; git rev-parse HEAD origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "b3eeee9a7dc57db1c56b19a288930d542523dfb7",
          "e4ce8b3bece33db40de68b6c407a514fbaed9a26"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "b3eeee9a7dc57db1c56b19a288930d542523dfb7"}
    }
  ],
  "flags": []
}
```

## Findings

**R1 — blocker — `docs/process/MAGISTRATE_WATCHDOG.md:191`.** “Saved ownership inventory” means step 3’s `handoff-NNN.json`. Missing files and malformed inventory fail closed, but a structurally valid stale inventory passes without any binding to the corrupted lock’s owner.

The injected matrix confirms matching owned pairs, resumed twins, and daemons refuse removal. Absent or reused recorded pairs allow removal. Unrelated interactive Claude also allows removal, as intended—but so does an **unrecorded live headless magistrate**, which could own the corrupted lock. The service lock does not resolve that case when its supervisor has exited. HEAD~1 retained the corrupt lock.

Exact reproduction: `PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/watchdog_delta_audit.py`.

The remaining checks passed: C3’s extracted block signals only the selected matching twin and refuses token/role mismatches before the affected signal; C1 preserves the other three labels; extraction, `zsh -n`, `compile()`, and install ordinals 0–6 remain intact. Both requested mutations make their named regressions fail.

## Residual risk

Process behavior was injected; no live processes were signalled. The reproduction script is retained under `/private/tmp`, outside the repository.