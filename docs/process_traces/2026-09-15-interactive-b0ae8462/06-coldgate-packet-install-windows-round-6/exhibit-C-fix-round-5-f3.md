# Exhibit C — fix round 5 (0ba6ce54 → ccce8a61): seat report for F3 and the production diff

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented F3 only; RED/GREEN mutation proof, both modules, and early-refusal probe verified; baseline F1/F2 edits preserved.",
  "workspace": {
    "base_requested": "0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa",
    "base_mode": "exact",
    "head_start": "0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa",
    "head_end": "0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa",
    "upstream_end": "0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa",
    "branch": "feat/2026-09-15-install-windows-transactional"
  },
  "pathspec": [
    "joulewise/night_agent_install.py",
    "tests/test_night_agent_install.py"
  ],
  "unowned_dirty": [
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md",
    "tests/test_night_agent_install.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "git -C /Users/edr/code/JouleWise-wt-iw-txn show 0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa:joulewise/night_agent_install.py > joulewise/night_agent_install.py && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install.CapabilityTests.test_signal_handler_masks_before_unwind_and_restores_entry_state",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r5c-mut",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          " : handler must block all transaction signals before unwinding",
          "",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.781s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "handler must block all transaction signals before unwinding[\\s\\S]*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cp /Users/edr/code/JouleWise-wt-iw-txn/joulewise/night_agent_install.py joulewise/night_agent_install.py && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install.CapabilityTests.test_signal_handler_masks_before_unwind_and_restores_entry_state",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r5c-mut",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.683s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
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
          "Ran 37 tests in 588.989s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 37 tests[\\s\\S]*OK"
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
          "Ran 47 tests in 49.744s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 47 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nimport io\nimport signal\nfrom tests.test_night_agent_install import CapabilityTests, LABELS\nfrom joulewise import night_agent_install as engine\ncase = CapabilityTests()\ncase.setUp()\noriginal_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())\ndispositions = {number: signal.getsignal(number) for number in engine.SIGNALS}\ntry:\n    entry_mask = (original_mask - set(engine.SIGNALS)) | {signal.SIGUSR1, signal.SIGHUP}\n    signal.pthread_sigmask(signal.SIG_SETMASK, entry_mask)\n    sidecar = case.target.sidecar(LABELS[0])\n    payload = b'retained prior refusal probe\\n'\n    sidecar.write_bytes(payload)\n    sink = io.StringIO()\n    machine = engine.Transaction(case.adapter, lambda: None, stderr=sink)\n    assert signal.pthread_sigmask(signal.SIG_BLOCK, ()) == entry_mask\n    assert machine.run() == 3, sink.getvalue()\n    assert machine.state is engine.State.REFUSED\n    assert machine.handlers == {}\n    assert signal.pthread_sigmask(signal.SIG_BLOCK, ()) == entry_mask\n    assert {number: signal.getsignal(number) for number in engine.SIGNALS} == dispositions\n    assert sink.getvalue() == 'retained prior plist: {}; re-run --uninstall\\n'.format(sidecar)\n    assert sidecar.read_bytes() == payload\n    assert case.fake.calls() == []\n    print('PASS: retained-prior refusal rc=3 before handler installation; no AttributeError')\n    print('PASS: constructor and early unwind preserve nonempty entry mask and dispositions')\nfinally:\n    for number, handler in dispositions.items():\n        signal.signal(number, handler)\n    signal.pthread_sigmask(signal.SIG_SETMASK, original_mask)\n    case.doCleanups()\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS: retained-prior refusal rc=3 before handler installation; no AttributeError",
          "PASS: constructor and early unwind preserve nonempty entry mask and dispositions"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS: retained-prior refusal[\\s\\S]*PASS: constructor and early unwind preserve nonempty entry mask and dispositions"
      }
    }
  ],
  "flags": []
}
```

## Change

- [Production hunks](/Users/edr/code/JouleWise-wt-iw-txn/joulewise/night_agent_install.py:334): constructor capture at 334, handler recapture/block at 350, unwind restoration at 411, uninstall restoration at 488. Existing `SIG_IGN` drain preserved.
- [Regression cell](/Users/edr/code/JouleWise-wt-iw-txn/tests/test_night_agent_install.py:1088): directly invokes the handler, observes all three signals blocked before unwind, and verifies install-time mask and disposition restoration.

Baseline F1/F2 bytes preserved; final scope check returned `SCOPE_OK`; `git diff --check` passed. No commit made. Next step: lead review.

## Verification notes

V1 is the expected RED failure in the fresh `cp -R` copy, reverting only F3 production changes. The copy was restored to GREEN afterward. Both modules ran in the foreground; existing repeat-signal tests passed.

All requested checks completed. The full repository suite and live launchd validation were not run.
## Production diff, joulewise/night_agent_install.py
```diff
diff --git a/joulewise/night_agent_install.py b/joulewise/night_agent_install.py
index a1e48330..77e9343c 100644
--- a/joulewise/night_agent_install.py
+++ b/joulewise/night_agent_install.py
@@ -331,6 +331,7 @@ class Transaction:
         self.state = State.PARSED
         self.result = 1
         self.handlers = {}
+        self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
         self.prepared = None
         self.selected_span_close = None
 
@@ -347,7 +348,9 @@ class Transaction:
         self.state = state
 
     def _install_handlers(self):
+        self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
         def raised(number, frame):
+            signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
             raise Signalled(128 + number)
         for number in SIGNALS:
             self.handlers[number] = signal.getsignal(number)
@@ -406,13 +409,13 @@ class Transaction:
                     self._warn("restore failed; retained prior sidecars: {}: {}".format(type(exc).__name__, exc))
 
     def _unwind(self):
-        old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
+        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
         self._teardown()
         # Discard queued repetitions while blocked. They must not re-enter the
         # transaction or replace its result after the unwind has completed.
         for number in self.handlers:
             signal.signal(number, signal.SIG_IGN)
-        signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
+        signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
         for number, handler in self.handlers.items():
             signal.signal(number, handler)
 
@@ -489,7 +492,7 @@ def uninstall(adapter, stderr=None):
     sink = stderr or sys.stderr
     machine = Transaction(adapter, None, stderr=sink)
     machine._install_handlers()
-    old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
+    signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
     try:
         proofs, unresolved = verified_bootout(adapter, adapter.target.labels)
         if unresolved:
@@ -507,7 +510,7 @@ def uninstall(adapter, stderr=None):
     finally:
         for number in machine.handlers:
             signal.signal(number, signal.SIG_IGN)
-        signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
+        signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
         for number, handler in machine.handlers.items():
             signal.signal(number, handler)
 
```
