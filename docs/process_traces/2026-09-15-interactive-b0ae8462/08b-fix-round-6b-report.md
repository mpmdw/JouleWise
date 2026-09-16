```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Applied the independent signal cures; both modules pass, but teardown exception handling requires NEEDS_RULING.",
  "workspace": {
    "base_requested": "6d4c2fc0f9e004f3cb3039d7ad9e22baada8987c",
    "base_mode": "exact",
    "head_start": "6d4c2fc0f9e004f3cb3039d7ad9e22baada8987c",
    "head_end": "6d4c2fc0f9e004f3cb3039d7ad9e22baada8987c",
    "upstream_end": "6d4c2fc0f9e004f3cb3039d7ad9e22baada8987c",
    "branch": "feat/2026-09-15-install-windows-transactional"
  },
  "pathspec": [
    "joulewise/night_agent_install.py",
    "tests/test_night_agent_install.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6b-mut/must_die.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "raised-once RED rc=1\njoulewise.night_agent_install.Signalled: 143\n\n----------------------------------------------------------------------\nRan 1 test in 0.522s\n\nFAILED (errors=1)",
          "raised-once GREEN rc=0\n.\n----------------------------------------------------------------------\nRan 1 test in 0.562s\n\nOK",
          "outer-catch RED rc=1\njoulewise.night_agent_install.Signalled: 143\n\n----------------------------------------------------------------------\nRan 3 tests in 1.370s\n\nFAILED (errors=3)",
          "outer-catch GREEN rc=0\n...\n----------------------------------------------------------------------\nRan 3 tests in 1.520s\n\nOK",
          "restore-order RED rc=1\n----------------------------------------------------------------------\nRan 1 test in 0.828s\n\nFAILED (failures=2)",
          "restore-order GREEN rc=0\n.\n----------------------------------------------------------------------\nRan 1 test in 0.814s\n\nOK",
          "teardown-finally RED rc=1\n----------------------------------------------------------------------\nRan 1 test in 0.472s\n\nFAILED (failures=1)",
          "teardown-finally GREEN rc=0\n.\n----------------------------------------------------------------------\nRan 1 test in 0.437s\n\nOK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "teardown-finally GREEN rc=0[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6b-mut/ix_exit.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "result=None escaped=RuntimeError: teardown witness",
          "mask_restored=True dispositions_restored=True",
          "FAIL: ruling 10 exact run() does not translate an exception raised by its finally to exit 1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "result=1 escaped=None"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 48 tests in 599.274s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 48 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 51 tests in 51.716s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests[\\s\\S]*OK"
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
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: requirement (ix) conflicts with routing the exception through ruling 10's existing BaseException branch. That branch cannot catch an exception from the inner finally's _unwind(). The exact dictated run() is preserved. V2 proves restoration succeeds but RuntimeError escapes. The fourth mutation GREEN covers restoration only, not the required exit-1 translation.",
      "needs": "Rule where teardown exceptions should be translated: add a catch inside _unwind (recommended to preserve the printed run), or amend run's printed outer handling. Blocked work: complete (ix), its exit-code regression, and acceptance."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: item 3 refers to wrapping _teardown() in uninstall's finally, but uninstall has no _teardown() call at BASE_HEAD. Its inline cleanup already sits inside try/except/finally. Only the prescribed disposition-before-mask order was applied there.",
      "needs": "Confirm that the existing uninstall try/finally satisfies the restoration requirement (recommended), or explicitly direct introduction of a new _teardown call."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The synthesis Q5 fresh execution lens under both interpreters, delta re-audit, and lead full-suite replay remain outstanding.",
      "needs": "Lead-owned verification after the rulings and completion."
    }
  ]
}
```

## Change

Installer hunks at lines 334, 353, 417, 442, and 542 add the guards, dictated outer catch, guaranteed restoration, and restore order. Test hunks at lines 1106 and 1114 add the deterministic regressions.

Terminal-state `_teardown()` already does nothing; no change was needed. Baseline digest verified, scope checker returned `SCOPE_OK`, and no commit was made.

## Verification notes

The initial simultaneous-unblock test let the guard mutant survive. Delivering the two queued signals across successive unwind entries made the probe deterministic and produced RED then GREEN.

Next step: resolve F1 and F2, then resume within the same two-file scope.