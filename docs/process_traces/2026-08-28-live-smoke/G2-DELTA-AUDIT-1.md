```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "HOLD: R-2 and R-6 are damaged, S11-A2 now ignores extra collected members, and R-8 has an unresolved pre-mint sequencing loop.",
  "workspace": {
    "base_requested": "397638af98175f154abbf1094077b9c4dae31f2c",
    "base_mode": "exact",
    "head_start": "b1d0e336f4bb1454f1f9682de53ab47ed824f96a",
    "head_end": "b1d0e336f4bb1454f1f9682de53ab47ed824f96a",
    "upstream_end": "b1d0e336f4bb1454f1f9682de53ab47ed824f96a",
    "branch": "feat/window-provenance-check"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "HOLD",
    "rulings": {
      "R-1": "INSTALLED",
      "R-2": "DAMAGED",
      "R-3": "INSTALLED",
      "R-5": "INSTALLED",
      "R-6-RATIFIED": "DAMAGED",
      "R-8": "PARTIAL"
    },
    "test_claim_assessment": "The module discovers 30 tests, but they do not cover the R-2 settle mutation, extra-member false acceptance, ratified R-6 sequencing, or R-8 pre-mint dependency.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "R-2's alleged mechanical comparison is filtered through copied constants",
        "locations": [
          "tests/test_check_window_provenance.py:367",
          "tests/test_check_window_provenance.py:407",
          "tests/test_check_window_provenance.py:440"
        ],
        "refutation_path": "The test extracts functions, then retains only hand-written required_lines/exact_step constants; it never compares settle() or screening bodies. In-memory mutation of /bin/sleep \"$SETTLE_S\" to /bin/sleep 999 in either the runbook or runsheet left the test PASS."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The runsheet and checker still require the forbidden in-night ledger-pin advance",
        "locations": [
          "docs/process_traces/2026-08-28-live-smoke/G2-CHECKER-MAGISTRATE-RULING.md:104",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:626",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:799",
          "scripts/check_window_provenance.py:771",
          "scripts/check_window_provenance.py:818",
          "joulewise/calibration_ledger.py:2046"
        ],
        "refutation_path": "The ratified text says STOP after post-bracket finalization, then desk review/advance/commit/regenerate/re-freeze/re-attest. The runsheet instead continues through completion, binding, verdict, and checker before its unchanged NEEDS-RULING pin section. Both checker loader calls require ledger/pin equality; require_committed_pin=False skips Git authentication only, while a physical-ahead ledger still receives calibration_ledger_head_mismatch."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "S11-A2 and all dependent checks silently ignore extra collected members",
        "locations": [
          "scripts/check_window_provenance.py:617",
          "scripts/check_window_provenance.py:624",
          "scripts/check_window_provenance.py:634",
          "scripts/check_window_provenance.py:749",
          "tests/test_check_window_provenance.py:598",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:620"
        ],
        "refutation_path": "A2 checks expected_ids minus cooldown keys but never cooldown keys minus expected_ids, then sets selected_ids=expected_ids. A fifth or block-2 bundle is excluded from A3/F5-1..4; F5-2 likewise checks only missing expected verdict IDs. The delete-one regression passes through the real path, but there is no add-one regression. This permits checker PASS despite the runsheet declaring any fifth science bundle ABORT."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "R-8's concrete count commands depend on the frozen pack whose prefill length they are meant to decide",
        "locations": [
          "docs/decision_log.md:193",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:68",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:632",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:681"
        ],
        "refutation_path": "D-166 requires the G2-selected length to be pre-registered before mint. The live gate requires all real _v5 packs and freeze/mint supply first, while D2 expects frozen diagnostic stages inside that pack and says the pack is not cut if no candidate qualifies. A separately authenticated pre-mint diagnostic artifact or an explicit draft-to-mint boundary is missing."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "bash -n docs/process_traces/2026-08-28-live-smoke/preflight.sh && git diff --check HEAD^ HEAD",
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
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; s=Path(\"tests/test_check_window_provenance.py\").read_text(); b=s[s.index(\"    def test_runsheet_phase_d_chain_is_mechanically_bound_to_runbook\"):s.index(\"    def test_runsheet_pins_ruled_termination_and_governed_chain\")]; assert \"/bin/sleep\" not in b; print(\"PASS R2 test omits settle implementation\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS R2 test omits settle implementation"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS R2 test omits settle implementation"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import unittest; import tests.test_check_window_provenance as m; print(unittest.defaultTestLoader.loadTestsFromModule(m).countTestCases())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "30"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^30$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 30 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": [
          "Read-only sandbox caused widespread temporary-file errors; run terminated with KeyboardInterrupt."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Do not merge HEAD while review findings F1-F3 remain.",
      "needs": "Repair and rerun the delta audit."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The enforced read-only sandbox provided no writable temporary directory, so neither the focused 30-test module nor the canonical suite could execute.",
      "needs": "Replay both commands in the writable CI/lead runner."
    }
  ]
}
```

## Findings

### F1 — Blocker: R-2 is hand-transcription in disguise

The test at [test_check_window_provenance.py:407](/Users/edr/code/JouleWise-wt-g1/tests/test_check_window_provenance.py:407) extracts function bodies but filters them through hand-written `required_lines`; the screening and bound checks at [line 440](/Users/edr/code/JouleWise-wt-g1/tests/test_check_window_provenance.py:440) are likewise copied constants and presence tests.

Mandatory mutation result:

- Runbook settle changed to `/bin/sleep 999`: test still PASS.
- Runsheet settle changed to `/bin/sleep 999`: test still PASS.

Thus neither half of the required bidirectional drift detection holds. Screening implementation and chain ordering can similarly drift while the selected tokens remain present.

### F2 — Blocker: R-6 RATIFIED was appended but not installed

The ruling requires a post-bracket stop followed by the desk reviewed-refresh cycle at [G2-CHECKER-MAGISTRATE-RULING.md:104](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/G2-CHECKER-MAGISTRATE-RULING.md:104). The runsheet instead says the primary chain continues through completion at [SHAKEDOWN-G2-RUNSHEET.md:626](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:626), then retains the old `NEEDS-RULING` pin-advance section at [line 799](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:799).

The checker also still consumes the pin in F5-2 and F5-3 at [check_window_provenance.py:771](/Users/edr/code/JouleWise-wt-g1/scripts/check_window_provenance.py:771) and [line 818](/Users/edr/code/JouleWise-wt-g1/scripts/check_window_provenance.py:818). A physical-ahead ledger remains `calibration_ledger_head_mismatch` at [calibration_ledger.py:2046](/Users/edr/code/JouleWise-wt-g1/joulewise/calibration_ledger.py:2046). Therefore Phase F cannot pass in the documented order without advancing the pin before the desk cycle.

### F3 — Blocker: extra members can false-PASS

At [check_window_provenance.py:624](/Users/edr/code/JouleWise-wt-g1/scripts/check_window_provenance.py:624), A2 checks only for missing expected IDs. It never rejects extra cooldown keys, then narrows `selected_ids` to the four expected IDs at [line 634](/Users/edr/code/JouleWise-wt-g1/scripts/check_window_provenance.py:634). F5-2 repeats the subset-only check at [line 749](/Users/edr/code/JouleWise-wt-g1/scripts/check_window_provenance.py:749).

Consequently, a late SIGINT that permits a fifth member—or a whole additional block—can be ignored by A3 and F5-1..4. The only new regression deletes an expected directory at [test_check_window_provenance.py:598](/Users/edr/code/JouleWise-wt-g1/tests/test_check_window_provenance.py:598); no add-one-member regression exists.

### F4 — Should fix: R-8 has a sequencing loop

The count extraction and output locations are concrete at [SHAKEDOWN-G2-RUNSHEET.md:639](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:639) and [line 654](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:654). The `count − 3 ≥ 5` calculation is consistent with the repository’s sample-margin convention.

But D-166 requires selection before mint, while the runsheet blocks all live work until real `_v5` freeze/mint supply exists at [line 68](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:68), then expects the three frozen diagnostic stages inside that pack and says not to cut the pack if none qualifies at [line 681](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:681).

## Residual risk

The focused and canonical suites require writable temporary storage, which this read-only runner prohibited. The source-only checks completed, the worktree remained clean, and the focused module was confirmed to contain 30 tests; CI/lead replay is still required for executable regression evidence.