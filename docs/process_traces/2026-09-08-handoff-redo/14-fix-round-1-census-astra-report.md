```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Fixed C1-C4 and C7; required regressions failed before edits and pass afterward; scoped acceptance passes.",
  "workspace": {
    "base_requested": "898e5305",
    "base_mode": "exact",
    "head_start": "898e530519a14f1e97b40f84ae835ca7ebfe20f2",
    "head_end": "898e530519a14f1e97b40f84ae835ca7ebfe20f2",
    "upstream_end": null,
    "branch": "feat/2026-09-08-watchdog-census-daemon"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "tests/test_magistrate_watchdog.py"
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
      "cmd": "python3 -m unittest tests.test_magistrate_watchdog.HandoffDefectTests.test_c1_reused_pid_disappears_before_kill tests.test_magistrate_watchdog.HandoffDefectTests.test_c2_corrupt_lock_recovery_checks_saved_owned_pairs tests.test_magistrate_watchdog.HandoffDefectTests.test_c3_documented_twin_stop_revalidates_each_signal tests.test_magistrate_watchdog.HandoffDefectTests.test_c4_lock_recovery_is_interactive_operator_only",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=3, errors=3)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=3, errors=3\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_magistrate_watchdog.HandoffDefectTests.test_c1_reused_pid_disappears_before_kill tests.test_magistrate_watchdog.HandoffDefectTests.test_c2_corrupt_lock_recovery_checks_saved_owned_pairs tests.test_magistrate_watchdog.HandoffDefectTests.test_c3_documented_twin_stop_revalidates_each_signal tests.test_magistrate_watchdog.HandoffDefectTests.test_c4_lock_recovery_is_interactive_operator_only > /tmp/watchdog-fix-after.log 2>&1\nrc=$?\nprintf 'rc=%s\\n' \"$rc\" >> /tmp/watchdog-fix-after.log\ntail -n 6 /tmp/watchdog-fix-after.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 0.013s", "", "OK", "rc=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK\\nrc=0"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog > /tmp/watchdog-fix-acceptance.log 2>&1\nrc=$?\nprintf 'rc=%s\\n' \"$rc\" >> /tmp/watchdog-fix-acceptance.log\ntail -n 6 /tmp/watchdog-fix-acceptance.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 95 tests in 17.675s", "", "OK", "rc=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK\\nrc=0"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "zsh -n scripts/install_magistrate_watchdog.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport re, subprocess, textwrap\ns=Path('docs/process/MAGISTRATE_WATCHDOG.md').read_text()\nreaper=s.split('   watchdog_checkout=',1)[1].split('   PY\\n',1)[0]\ncompile(textwrap.dedent(reaper.split(\"<<'PY' &\\n\",1)[1]), '<reaper>', 'exec')\nfor block in re.findall(r\"<<'PY'.*?\\n(.*?)\\n\\s*PY$\",s,re.S|re.M):\n    compile(textwrap.dedent(block),'<documented-python>','exec')\nfor block in re.findall(r'```zsh\\n(.*?)\\n\\s*```',s,re.S):\n    subprocess.run(['zsh','-n'],input=textwrap.dedent(block),text=True,check=True)\nprint('PASS: reaper extraction, documented Python compile(), documented zsh -n')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: reaper extraction, documented Python compile(), documented zsh -n"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS: reaper extraction"
      }
    }
  ],
  "flags": []
}
```

## Change

- **C1:** Preserve `reused_skipped` when a changed-token PID disappears before KILL. Regression kills the counterfactual that this becomes `already_gone`.
- **C2:** Documented reconciliation can clear corrupt, non-object, or `{}` locks using a saved ownership inventory. It refuses live owned pairs, twins, and invalid inventory. Regression exercises three corrupt forms with absent owners, live owned processes, and late twins.
- **C3:** Added exact inventory and observer-Terminal stop commands. The stop block revalidates PID/start token and resumed-twin role before each signal, then checks absence. Regression rejects token replacement before TERM and before KILL.
- **C4:** Marked recovery **INTERACTIVE MAGISTRATE / OPERATOR ONLY**, explicitly barred headless execution, and cited relaunch-prompt line 19. Regression detects omission of that authority boundary.
- **C7:** Moved the stated digest-verification deadline before step 1 executes pinned code; added a regression.
- **C5/C6:** Optional changes deferred. Existing real-reaper execution coverage remains alongside the bounded detachment shadow fixture.

No commit or out-of-scope edits. Next step: lead diff review and final verification.

## Verification notes

The four required tests were written and run before implementation/documentation edits. [Before log](/tmp/watchdog-fix-before.log), rc **1**, records:

- C1: `AssertionError: 'reused_skipped' != 'already_gone'`
- C2: `SystemExit: handoff_lock_not_clear: CensusObservation(empty=False, exit_code=3, stdout='', stderr='handoff_lock_invalid') []`
- C3: `AssertionError: 1 != 0 : HANDOFF_TWIN_ABSENT`
- C4: missing `INTERACTIVE MAGISTRATE / OPERATOR ONLY`

C2 produced three subtest errors, hence the combined tail `FAILED (failures=3, errors=3)`. Pass-after and acceptance tails are recorded in V2/V3 and their logs. The repository-wide suite was not run.

The corrected original-landing figure is **16 methods / 28 attributable failing outcomes** against HEAD~1’s code, per the refuter’s measurement—not “four original failures.” That historical comparison was not rerun here.

The branch has no configured upstream. One shell invocation emitted a nonfatal `nice(5)` permission warning; standalone installer syntax verification subsequently returned rc 0.