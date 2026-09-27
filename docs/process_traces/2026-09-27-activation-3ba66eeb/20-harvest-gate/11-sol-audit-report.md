```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Commit c5088b87 passes independent pin, battery-verdict, history, cadence, and dry-run checks; two pre-existing validator gaps warrant follow-up.",
  "workspace": {
    "base_requested": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "base_mode": "exact",
    "head_start": "c5088b871dac4a3e75773f645c6293ffde1568b9",
    "head_end": "c5088b871dac4a3e75773f645c6293ffde1568b9",
    "upstream_end": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "location": "joulewise/battery_float.py:457",
        "text": "validate_window ignores recorded probe_error and passed fields; a synthetic digest-consistent failed probe with valid raw stdout replayed as pass. All 24 actual W1 readings record probe_error=false and passed=true."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "joulewise/battery_float.py:654",
        "text": "compare_verdict omits attempt_id, reasons, update ages, and delta_q_mah, so authentication alone can accept incorrect ancillary fields. The committed W1 file passed this audit's full-field comparison."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/.venv/bin/python -B /tmp/sol-harvest-audit-3ba66eeb/audit.py",
      "cwd": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "TAIL 50 session_rows 25 control_rows 25 other_rows 0",
          "FINALIZED 12 declared 12 last_slot d12",
          "WINDOW pass slot_fields_equal True",
          "VERDICT all_fields_equal True exact_file_bytes True prereg_sha 81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1 module_sha 4b4d7bb206250cc0078d2a6b0b34d4e7e6305ff1d3a8b72f93528016d935e7e5 tool_commit 97082508f3648ff8575c94b0cdfcf657ba440142",
          "AUTHENTICATE pass c5088b871dac4a3e75773f645c6293ffde1568b9 12 07bcc13b6f476c72280a74e21bfc2499b9085f5bf380cf891afa7f341fa535a2"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AUTHENTICATE pass c5088b87.* 12 "
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/.venv/bin/python -B scripts/calibration_cadence_report.py --window 'W=/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-*' --calibration-ledger /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/runs/calibration_observation_ledger.jsonl --head-pin /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/configs/calibration/calibration_ledger_head.json --session W=d079-epoch-25g83-derivation-w1-20260927 --preregistration-sha256 81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1",
      "cwd": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "\"median_native_frame_ms\": 128.4634165,",
          "\"max_native_frame_ms\": 141.644583,",
          "\"r5_n_verdict\": \"CONTINUE\""
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"r5_n_verdict\": \"CONTINUE\""
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/.venv/bin/python -B scripts/issue_calibration_acceptance_generation.py check --session-ids d079-epoch-25g83-derivation-w1-20260927 --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md --preregistration-sha256 81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1",
      "cwd": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d079-epoch-25g83-derivation-w1-20260927: battery=pass recorded=pass",
          "d079-epoch-25g83-derivation-w1-20260927: kind=derivation state=finalized terminal=yes declared=12 filled=12 valid=6 excluded=none",
          "prefix pending or unresolved rows: 0",
          "registration admissible for prepare-candidate: yes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "registration admissible for prepare-candidate: yes"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch; shasum -a 256 runs/calibration_observation_ledger.jsonl; git rev-parse HEAD",
      "cwd": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "b03be93867ceffe69bbd277fc83829600414d9cc5d53b0a28ced2d5a56abc63f  runs/calibration_observation_ledger.jsonl",
          "c5088b871dac4a3e75773f645c6293ffde1568b9"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "c5088b871dac4a3e75773f645c6293ffde1568b9"
      }
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The dry run exited 0 and printed the expected result, followed by an atexit Metal-device warning in this sandbox.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — SHOULD-FIX.** [`validate_window`](/Users/edr/code/JouleWise-wt-harvest-audit-3ba66eeb/joulewise/battery_float.py:457) checks `exit_code` and `timed_out`, then reparses stdout, but does not check the evidence’s `probe_error` or `passed` fields. A scratch-only replay with a digest-consistent evidence file produced:
  ```text
  recorded_probe_error True recorded_passed False
  replayed_status pass slot_verdict pass
  ```
  This is a possible false pass in the validator. **It did not occur in W1:** all 24 actual readings had exit code 0, `timed_out=false`, `probe_error=false`, and `passed=true`.

- **F2 — SHOULD-FIX.** [`compare_verdict`](/Users/edr/code/JouleWise-wt-harvest-audit-3ba66eeb/joulewise/battery_float.py:654) compares status and four slot fields, leaving other recorded fields unchecked by authentication alone. A scratch comparison with altered age and `delta_q_mah` returned `None`. The committed W1 verdict nevertheless matched a full-field reconstruction byte for byte.

The [read-only audit script](/tmp/sol-harvest-audit-3ba66eeb/audit.py) parsed and rehashed every JSONL receipt, called `terminal_head_pin_for_session`, and compared the exact pin bytes the writer emits. Its decisive output was:

```text
OLD_HEAD 176 0f7609aeaecd9ef191947b91ebb2b7d12bef9fb7bf4b95b690bbedfeaede2512
TAIL 50 session_rows 25 control_rows 25 other_rows 0
TAIL_EVENTS {'append-intent': 25, 'bracket-session-open': 1, 'bracket-session-slot-claim': 12, 'bracket-session-slot-finalization': 12}
FINALIZED 12 declared 12 last_slot d12
MANUAL_PIN {'sequence': 226, 'head_digest': 'bd7aee7ab969e58d4c08992a3af0b0a1fed88cc9a911a65d1200ed0220a46693', 'ledger_schema': 'joulewise.calibration_observation_ledger.v1'}
TOOL_PIN {'sequence': 226, 'head_digest': 'bd7aee7ab969e58d4c08992a3af0b0a1fed88cc9a911a65d1200ed0220a46693', 'ledger_schema': 'joulewise.calibration_observation_ledger.v1'} EXACT_FILE_BYTES True
WINDOW pass slot_fields_equal True
VERDICT all_fields_equal True exact_file_bytes True
AUTHENTICATE pass c5088b871dac4a3e75773f645c6293ffde1568b9 12 07bcc13b6f476c72280a74e21bfc2499b9085f5bf380cf891afa7f341fa535a2
```

Every slot’s evidence-file SHA matched its ledger row; every pre/post raw SHA matched its evidence file. Direct reads of the 24 ioreg files found `ExternalConnected=Yes`, `IsCharging=No`, and fresh `UpdateTime` values (ages 22.851–44.004 s). Instant current was **0 mA in 23 readings and −11 mA in d10 post**, all within the registered ±200 mA limit. The verdict’s registration SHA, module SHA, parent `tool_commit`, ledger head, slot fields, and serialized bytes matched. Its recorded computation time was 9.68 s before the adding commit.

The single-commit rule also held:

```text
$ git log --full-history --no-merges --no-renames --format='%H %s' -- configs/calibration/battery_float_verdicts/d079-epoch-25g83-derivation-w1-20260927.json
c5088b871dac4a3e75773f645c6293ffde1568b9 Harvest d079-epoch-25g83-derivation-w1-20260927: ledger head pin and battery-float verdict
```

The same commit was the sole result with `--diff-filter=A`. The cadence and dry-run replay commands and their observed outputs are recorded in V2–V3 above. Both the measurement checkout and audit checkout remained clean; the ledger SHA remained `b03be93867ceffe69bbd277fc83829600414d9cc5d53b0a28ced2d5a56abc63f`, also matching the archive copy.

## Residual risk

No incorrect pin or verdict was found in this commit. The recorded `computed_wall_time_s` cannot be reconstructed exactly from raw battery bytes; its timing is consistent with the commit. The registered endpoint readings also cannot detect a charging excursion wholly between pre and post, as [A-R5b discloses](/Users/edr/code/JouleWise-wt-harvest-audit-3ba66eeb/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:664).

Reading slot-disposition lines before runbook step (iii) departed from its prescribed order. It did **not** supply an input to either result: [`battery-verdict`](/Users/edr/code/JouleWise-wt-harvest-audit-3ba66eeb/scripts/issue_calibration_acceptance_generation.py:1573) derives its record from the ledger, registered digest, and raw evidence; [`terminal_head_pin_for_session`](/Users/edr/code/JouleWise-wt-harvest-audit-3ba66eeb/joulewise/calibration_ledger.py:5197) derives the pin from ledger receipts. Neither reads `derivation-chain.log` or accepts an operator-selected slot disposition.

AUDIT: PASS