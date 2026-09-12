```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "No blocker found: focused regression passes, scratch-copy killed cut fails as intended, and generic witness tests pass.",
  "workspace": {
    "base_requested": "ace4cc3c",
    "base_mode": "descendant",
    "head_start": "7014dd0e0d5a13fce0762e91f0f7541ae8a91d1d",
    "head_end": "7014dd0e0d5a13fce0762e91f0f7541ae8a91d1d",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": "fix/2026-09-12-recover-window-exhausted"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_session_refusal_reports_window_exhausted_derivation_abort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.544s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport os, pathlib, shutil, subprocess, tempfile\nroot = pathlib.Path.cwd()\nwith tempfile.TemporaryDirectory(prefix='a184-killed-cut-', dir='/tmp') as temp:\n    scratch = pathlib.Path(temp)\n    source = root / 'scripts/recover_calibration_ledger.py'\n    cut = scratch / source.name\n    shutil.copy2(source, cut)\n    text = cut.read_text()\n    entry = '    \"window_exhausted\": RefusalCode.WINDOW_EXHAUSTED,\\n'\n    assert text.count(entry) == 1\n    cut.write_text(text.replace(entry, ''))\n    (scratch / 'sitecustomize.py').write_text(\n        'import pathlib, shutil\\n'\n        '_copy = shutil.copy2\\n'\n        'def copy(src, dst, *a, **kw):\\n'\n        f'    if pathlib.Path(src) == pathlib.Path({str(source)!r}):\\n'\n        f'        src = {str(cut)!r}\\n'\n        '    return _copy(src, dst, *a, **kw)\\n'\n        'shutil.copy2 = copy\\n'\n    )\n    env = dict(os.environ, PYTHONPATH=str(scratch), TMPDIR='/tmp')\n    result = subprocess.run(['python3', '-m', 'unittest', 'tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_session_refusal_reports_window_exhausted_derivation_abort'], env=env)\n    raise SystemExit(result.returncode)\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'calibration_session_not_open' != 'calibration_window_exhausted'",
          "Ran 1 test in 0.604s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_enum_inventory_and_discovered_executed_witnesses_are_exact_sets_per_class tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_parameterized_durable_public_cli_witnesses tests.test_calibration_exits.RefusalInventoryTests.test_generated_contract_projection_and_runbook_anchors_are_fresh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CASE PASS calibration_window_exhausted",
          "Ran 3 tests in 388.821s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short; git rev-parse HEAD; git rev-parse origin/main; git diff --check ace4cc3c..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "7014dd0e0d5a13fce0762e91f0f7541ae8a91d1d",
          "ace4cc3cf545728e7327c14ba1084cbabb47e3ad"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad"
      }
    }
  ],
  "flags": []
}
```

## Findings

**No blocker found. No should-fix or nit findings.**

1. **The regression detects the intended defect.** The constructor opens a derivation session and executes `abort-session --reason window_exhausted` (`tests/test_calibration_exits.py:4599`). The test then executes `session-refusal` and checks code, terminal result, process exit, and durable abort reason (`:5980`). V2 replaced only the script copied into the temporary fixture with a `/tmp` mutant missing the map entry. It failed at the code assertion:
   ```
   AssertionError: 'calibration_session_not_open' != 'calibration_window_exhausted'
   Ran 1 test in 0.604s
   FAILED (failures=1)
   ```
   The unchanged implementation passed:
   ```
   Ran 1 test in 0.544s
   OK
   ```

2. **The execution paths are distinct and verified.** In `scripts/recover_calibration_ledger.py:66`, `"window_exhausted": RefusalCode.WINDOW_EXHAUSTED` supplies the lookup at `:377`. An aborted session reaches `emit_refusal(code, ..., terminal_result="session_aborted")` at `:380`, producing `calibration_window_exhausted`. Without that entry, the lookup returns `None`; `:379` raises `CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)`—line 378 at base `ace4cc3c`. The handler at current `:538` emits that error code.

3. **Exit and membership match the automatic-abort siblings.** The registry default is exactly `process_exit: int = 2` (`joulewise/calibration_exits.py:161`). Runtime inspection confirmed `DISPLAY_ARM_FAILED`, `SAMPLER_NEVER_READY`, `ROLLOVER_GATE_TIMEOUT`, and `WINDOW_EXHAUSTED` all have `'process_exit': 2`. All routing fields match, excluding their deliberately different code, description, and witness ID.

   The complete registry-set census found rollover in `_ABORT` (`:280`) and `_WRITER_COMPONENT` (`:353`); both contain window exhausted. All four are absent from `_REPAIR`, `_ABANDON`, `_RESUME`, `_ADVANCE`, `_PREFLIGHT`, `_RECOVERY_COMPONENT`, `_RESERVATION_COMPONENT`, and `_CORRUPTION_BACKSTOPS`. They share the operational default, writer component, pre-slot-or-capture phase, and session-aborted terminal result.

   The other explicit enum-containing set is the automatic-abort test branch (`tests/test_calibration_exits.py:5579`); window exhausted is included. It also appears alongside rollover in `_DESCRIPTIONS`, `_AUTOMATIC_ABORT_REFUSALS`, `WITNESS_CASES`, and the test’s durable-reason dictionary (`:5597`). Inventory generation covers every enum (`joulewise/calibration_exits.py:556`); witness IDs use `f"witness.{code.value}"` (`:180`). The new contract row is present at `docs/contracts/calibration_ledger_append.md:345`; freshness and exact-set tests passed.

   Separately, the literal rollover string belongs to `analysis_engine/claims.py`’s `REDUCER_REASON_CODES` (`:40`) and its derived `REASON_CODES` (`:141`) and `_NOT_RESOLVABLE` (`:158`). Window exhausted is absent, as are display-arm and sampler-never-ready. These are reducer/claim vocabularies, not the automatic-abort registry family; this pre-existing distinction does not require adding the new desk refusal.

4. **The observer does real work; sibling assertions are preserved.** The dispatcher at `tests/test_calibration_exits.py:5249` calls `_run("session-refusal", ...)`. It is not merely a label bypassing execution. Common process-exit and code assertions run before the new terminal-result branch. Later, the case independently checks durable aborted status and reason, then invokes a fresh `session-refusal` (`:5578`).

   Base has 71 witnesses and zero `session-refusal` observers; HEAD has 72 and exactly one. The original sibling assertion body remains byte-identical after changing `if` to `elif` (`:5462`). Every existing case therefore retains its previous behavior. Both generic corpus consumers passed, together with contract freshness:
   ```
   CASE PASS calibration_window_exhausted
   Ran 3 tests in 388.821s
   OK
   ```

5. **Night-chain literal and scope are correct.** `scripts/night_chains/calibration_derivation_only.zsh:121` contains `abort-session`; line 124 is exactly `--reason window_exhausted`. That reason matches the map key byte-for-byte. The requested harvest sentence appears at `docs/phase_2/derivation_night_runbook.md:1665`. Reviewing `git diff ace4cc3c..HEAD` found no unrelated behavior change among the five files, +53/−1.

No repository files were modified. HEAD remained unchanged and the worktree remained clean. Next step: lead final review of `7014dd0e`.

## Residual risk

Verification used temporary fixtures and public CLI subprocesses. The full module and hardware/night-chain execution were not run; both fenced directories remained untouched.