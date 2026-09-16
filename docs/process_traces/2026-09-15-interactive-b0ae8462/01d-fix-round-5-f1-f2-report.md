```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "F1 and F2 implemented and verified; F3 requires a ruling for refusals before handler installation. No commit created.",
  "workspace": {
    "base_requested": "0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa",
    "base_mode": "exact",
    "head_start": "0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa",
    "head_end": "0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa",
    "upstream_end": "0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa",
    "branch": "feat/2026-09-15-install-windows-transactional"
  },
  "pathspec": [
    "tests/test_night_agent_install.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md"
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
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r5-mut",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 3 != 0 : ",
          "",
          "----------------------------------------------------------------------",
          "Ran 36 tests in 625.071s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r5-mut",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 36 tests in 601.965s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 36 tests in [0-9.]+s\\n\\nOK"
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
          "Ran 36 tests in 625.375s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 36 tests in [0-9.]+s\\n\\nOK"
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
          "Ran 47 tests in 54.796s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 47 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V5",
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
    }
  ],
  "flags": [
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: run() always calls _unwind(), including validation/admission refusals before _install_handlers(). Capturing entry_mask only in _install_handlers() and restoring it unconditionally would raise AttributeError on those refusals, including F1. Options: initialize entry_mask in Transaction.__init__ and recapture at handler installation; or add a separate early-refusal unwind branch. Recommend constructor initialization. No F3 production changes, regression cell, or mutation proof were made.",
      "needs": "Approve initializing self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ()) in Transaction.__init__, while retaining the dictated recapture in _install_handlers(), or dictate the early-refusal branch. Then resume F3 implementation and verification."
    }
  ]
}
```

## Change

- **F1:** [test module](/Users/edr/code/JouleWise-wt-iw-txn/tests/test_night_agent_install.py:9), hunks at lines 9, 635, 729 and 931: must-die entry, shared sidecar assertions, and one regression checking exit 3, verbatim diagnostic, no publication or launchctl calls, and unchanged bytes/mtime.
- **F2:** [runbook](/Users/edr/code/JouleWise-wt-iw-txn/docs/phase_2/derivation_night_runbook.md:1413), hunks at lines 1413, 1429, 1440, 1452 and 1670; [handback](/Users/edr/code/JouleWise-wt-iw-txn/docs/process/NIGHT_HANDBACK.md:405), hunk at line 405: sidecars require manual copying; successful uninstall deletes them.
- **F3:** No diff. The conflict is between unconditional [unwind](/Users/edr/code/JouleWise-wt-iw-txn/joulewise/night_agent_install.py:408) and handler installation after validation/admission.

## Verification notes

V1 deleted only the three-line retained-prior refusal in the authorized `cp -R` copy. Its sole failure was the new F1 test. V2 restored the source byte-for-byte before the GREEN run. Both worktree modules ran in foreground; existing repeat-signal tests passed.

Baseline digest, HEAD and index matched. Final scope contains only the three listed paths.

## Residual risk

F3’s signal window remains. Next step: lead ruling on entry-mask initialization, then resume F3.