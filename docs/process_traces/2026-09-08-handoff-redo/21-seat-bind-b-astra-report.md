```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented disposition B: corrupt-lock recovery binds to durable resident_session ownership and preserves refusals with events and launch notices.",
  "workspace": {
    "base_requested": "7a18fddc",
    "base_mode": "exact",
    "head_start": "7a18fddc24d163a37bb194b5510b0508dec27645",
    "head_end": "7a18fddc24d163a37bb194b5510b0508dec27645",
    "upstream_end": null,
    "branch": "feat/2026-09-08-watchdog-census-daemon"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "tests/test_magistrate_watchdog.py",
    "tests/test_magistrate_watchdog_cli.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog.HandoffDefectTests.test_corrupt_lock_tick_matrix_binds_durable_resident tests.test_magistrate_watchdog.HandoffDefectTests.test_corrupt_lock_documented_matrix_binds_durable_resident tests.test_magistrate_watchdog_cli.HandoffCliDefectTests.test_corrupt_lock_cli_refusal_survives_unreadable_state_and_repeated_hold > /tmp/watchdog-bind-before.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=108, errors=18)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=108, errors=18\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog.HandoffDefectTests.test_corrupt_lock_tick_matrix_binds_durable_resident tests.test_magistrate_watchdog.HandoffDefectTests.test_corrupt_lock_documented_matrix_binds_durable_resident tests.test_magistrate_watchdog_cli.HandoffCliDefectTests.test_corrupt_lock_cli_refusal_survives_unreadable_state_and_repeated_hold > /tmp/watchdog-bind-after.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog > /tmp/watchdog-bind-acceptance.log 2>&1\nrc=$?\necho \"rc=$rc\" | tee -a /tmp/watchdog-bind-acceptance.log\ntail -14 /tmp/watchdog-bind-acceptance.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 97 tests in 19.709s", "", "OK", "rc=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 97 tests[\\s\\S]*OK\\nrc=0"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport re, subprocess, textwrap\ntext = Path('docs/process/MAGISTRATE_WATCHDOG.md').read_text()\nblocks = re.findall(r\"   ```zsh\\n(.*?)   ```\", text, re.S)\nfor i, block in enumerate(blocks):\n    source = textwrap.dedent(block)\n    result = subprocess.run(['zsh', '-n'], input=source, text=True, capture_output=True)\n    assert result.returncode == 0, (i, result.stderr)\npyblocks = re.findall(r\"<<'PY'.*?\\n(.*?)\\n   PY(?:\\n|$)\", text, re.S)\nfor i, source in enumerate(pyblocks):\n    compile(textwrap.dedent(source), f'<documented-python-{i}>', 'exec')\nreaper = text.split('   watchdog_checkout=', 1)[1].split('   PY\\n', 1)[0]\ncompile(textwrap.dedent(reaper.split(\"<<'PY' &\\n\", 1)[1]), '<extracted-reaper>', 'exec')\nprint(f'PASS: zsh -n ({len(blocks)} blocks), compile() ({len(pyblocks)} Python blocks), watchdog_checkout extraction')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: zsh -n (11 blocks), compile() (3 Python blocks), watchdog_checkout extraction"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS: zsh -n .*watchdog_checkout extraction"
      }
    },
    {
      "id": "V5",
      "kind": "lint",
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
    }
  ],
  "flags": []
}
```

## Change

The tick and extracted step-4 block share the durable-record recovery check. Corrupt-lock refusals preserve the lock and resident record, emit an event, and retain a next-launch notice. Drain adoption cannot discard that evidence. Valid-lock handling remains intact.

Regressions exercise `{torn`, `{}`, and `[]` against these counterfactuals:

- Live headless `claude -p` resident → HOLD, lock kept.
- Missing or malformed resident record → HOLD, lock kept.
- Recorded PID absent or reused with another start token → unlink.
- Recorded pair gone but resumed twin, daemon, host, or spare live → HOLD.
- Recorded pair still present as defunct → HOLD.
- Missing/torn state or repeated HOLD → refusal event and notice retained.

Manual Ed-hands recovery is documented only for the both-unreadable case.

## Verification notes

Tests were written and run before implementation. All three regression methods failed on the baseline; already-correct absent-PID/reused-PID cases remain controls. Baseline errors included unexpected documented refusals and CLI reads after unsafe lock deletion.

Evidence: [fail-before log](/tmp/watchdog-bind-before.log), [pass-after log](/tmp/watchdog-bind-after.log), [acceptance log with rc](/tmp/watchdog-bind-acceptance.log).

The brief says “FOUR” modules but supplies three; the exact supplied command was run. No repository-wide suite or commit was performed. Next step: lead final diff review; live verification remains lead-owned.