```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Independent W2 pin, verdict, raw-evidence, cadence, and registration checks passed.",
  "workspace": {
    "base_requested": "a71a5e7999b5364e8477685b13c6a1e440fa7b27",
    "base_mode": "exact",
    "head_start": "722f7bd161f1a1d0ae2ef624f7f29aac3e347d82",
    "head_end": "722f7bd161f1a1d0ae2ef624f7f29aac3e347d82",
    "upstream_end": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "audit": "PASS"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/.venv/bin/python /tmp/sol-harvest-audit-77b1bee2/audit.py",
      "cwd": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PIN: tool and independent last-row candidate {'sequence': 276, 'head_digest': '476e2ae857d4d6279bfa3c59c39bb5bc6f983d282948ce0abb95e3df62d49737', 'ledger_schema': 'joulewise.calibration_observation_ledger.v1'} bytes exact True",
          "VERDICT: validate_window and verdict_record every field + serialized bytes exact; sha256 51f4961828a440cbab5c7cf504d7e4536b25243414441dab5fedfb6f28f946ec status pass slots 12",
          "EVIDENCE: 12 evidence SHA256=ledger, 24 raw SHA256=evidence, 24 probe_error=false/passed=true, 24 top-level fields match raw"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "24 probe_error=false/passed=true"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "\"$PY\" scripts/calibration_cadence_report.py --window \"W=$RUNS_ROOT/instrument_validation/$SESSION_ID-*\" --calibration-ledger \"$CALIBRATION_LEDGER\" --head-pin \"$LEDGER_HEAD_PIN\" --session \"W=$SESSION_ID\" --preregistration-sha256 \"$PREREGISTRATION_SHA256\"",
      "cwd": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "\"median_native_frame_ms\": 128.467625",
          "\"max_native_frame_ms\": 141.390208",
          "\"r5_n_verdict\": \"CONTINUE\""
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CONTINUE"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "\"$PY\" scripts/issue_calibration_acceptance_generation.py check --session-ids \"$SESSION_ID\" --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md --preregistration-sha256 \"$PREREGISTRATION_SHA256\"",
      "cwd": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2",
      "observed": {
        "result": "pass",
        "exit_code": 5,
        "tail": [
          "registration admissible for prepare-candidate: no",
          "blocker: valid same-epoch observations outside this registration: 6 rows owned by d079-epoch-25g83-derivation-w1-20260927 (ruling 46 addendum A-7)"
        ]
      },
      "expected": {
        "exit_code": 5,
        "tail_regex": "ruling 46 addendum A-7"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "\"$PY\" scripts/issue_calibration_acceptance_generation.py check --session-ids d079-epoch-25g83-derivation-w1-20260927 --session-ids d079-epoch-25g83-derivation-w2-20260927 --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md --preregistration-sha256 \"$PREREGISTRATION_SHA256\"",
      "cwd": "/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d079-epoch-25g83-derivation-w1-20260927: kind=derivation state=finalized terminal=yes declared=12 filled=12 valid=6 excluded=none",
          "d079-epoch-25g83-derivation-w2-20260927: kind=derivation state=finalized terminal=yes declared=12 filled=12 valid=6 excluded=none",
          "registration admissible for prepare-candidate: yes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "registration admissible for prepare-candidate: yes"
      }
    }
  ],
  "flags": []
}
```

## Findings

No BLOCKER, SHOULD-FIX, or NIT findings.

The [read-only audit script](/tmp/sol-harvest-audit-77b1bee2/audit.py) returned rc 0. It confirmed that ledger rows **227–276** belong to W2 (including their control rows), the session finalized all **12/12** slots, and rows 1–226 are byte-identical to the W1 harvested ledger. The full ledger matched its archive copy and retained SHA-256 `23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d`.

`terminal_head_pin_for_session` and the independent last-row check both yielded sequence **276**, digest `476e2ae857d4d6279bfa3c59c39bb5bc6f983d282948ce0abb95e3df62d49737`. The committed pin’s bytes exactly match the pin writer’s serialization. Recomputing `validate_window` and the full verdict record matched **every field and the serialized bytes** of the committed verdict. `authenticate_committed_verdict` passed; Git history shows exactly one commit touching the verdict path, `722f7bd1`, which added it alongside the pin update.

For all 12 slots, `instrument_evidence.json` hashes matched their ledger rows, and all 24 raw ioreg hashes matched their evidence records. Independently reading each raw file found `ExternalConnected=Yes`, `IsCharging=No`, `InstantAmperage=0 mA`, and `UpdateTime` ages below 180 seconds. All 24 evidence records had `probe_error=false` and `passed=true`. This matches the predicate in [A-R5b](/Users/edr/code/JouleWise-wt-harvest-audit-77b1bee2/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:652).

The runbook cadence command returned rc 0: **R5(n) CONTINUE**, median **128.467625 ms**, maximum **141.390208 ms**. The W2-only `check` returned rc 5 solely for the predicted A-7 blocker: W1’s six valid same-epoch rows lie outside a W2-only registration. Naming both sessions returned rc 0, **admissible yes**, with **6+6 valid**. After these runs, the measurement checkout remained clean at `722f7bd1`, and the ledger SHA-256 was unchanged.

## Residual risk

No way for this committed pin or verdict to be wrong **while the requested checks all pass** was found. The registered battery rule samples only each slot’s endpoints; a charging excursion entirely between those readings remains undetectable, as [A-R5b discloses](/Users/edr/code/JouleWise-wt-harvest-audit-77b1bee2/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:664).

AUDIT: PASS