```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the independent round-3 changes; amendment 51 needs a lead ruling before the sweep and acceptance report can be completed.",
  "workspace": {
    "base_requested": "49d77c74",
    "base_mode": "exact",
    "head_start": "49d77c7404c991ab3cc7dca87cff73db2ed3eb01",
    "head_end": "49d77c7404c991ab3cc7dca87cff73db2ed3eb01",
    "upstream_end": null,
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": [
    "joulewise/aggregate.py",
    "joulewise/analysis_engine/inputs.py",
    "joulewise/bundle_read.py",
    "joulewise/floor_extraction.py",
    "joulewise/scored_reduce.py",
    "joulewise/whole_window.py",
    "joulewise/window_duration_margins.py",
    "scripts/extract_detection_floors.py",
    "scripts/mint_floor_artifact.py",
    "scripts/run_campaign.py",
    "tests/test_bfgs_calibration_bracketing.py",
    "tests/test_bfgs_window_consumers.py",
    "tests/test_bundle_read.py",
    "tests/test_controller.py",
    "tests/test_scored_reduce.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_controller tests.test_bundle_read tests.test_reduce tests.test_revision_five_b_readers tests.test_scored_reduce tests.test_bfgs_calibration_bracketing tests.test_bfgs_window_consumers tests.test_bfgs_consumer_sweep tests.test_bfgs_publication_privacy tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": [
          "               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^",
          "  File \"/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/json/decoder.py\", line 361, in raw_decode",
          "    obj, end = self.scan_once(s, idx)",
          "               ~~~~~~~~~~~~~~^^^^^^^^",
          "KeyboardInterrupt"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "......",
          "----------------------------------------------------------------------",
          "Ran 316 tests in 466.499s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 316 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "builder-1",
      "kind": "build",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "forward check: byte-identical entries=69"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "forward check: byte-identical entries=69"
      }
    },
    {
      "id": "builder-2",
      "kind": "build",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "listed_population sw7bfloor-df-ph-decode-abs-r07 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r08 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r09 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "listed_population sw7bfloor-df-ph-decode-abs-r10 /Users/edr/code/JouleWise/runs_window_7bfloor_20260729 file_digest",
          "forward check: byte-identical entries=69"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "forward check: byte-identical entries=69"
      }
    },
    {
      "id": "current-sweep",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_bfgs_consumer_sweep",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 3 tests in 1.505s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in .*\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Amendment 51 reports gate-internal and reader reads, but none of its four allowlist classes fits them.",
      "needs": "Rule a gate-implementation class or a precise detector exemption, then resume amendment 51."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Section 9 requests the N-1 comment fix in tests/test_battery_float_consumers.py, while the prompt restricts that path to amendment 36's round-2 rule.",
      "needs": "Clarify whether the N-1 comment edit is authorized in that path."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "V1 is not green; the unchanged amendment-51 sweep fails, and the full V1 run was interrupted in the 200-night differential test after about 21 minutes.",
      "needs": "Complete amendment 51 and rerun V1."
    }
  ]
}
```

## Change

The independent changes cover recorded-digest custody checks, field-valid supersession records, missing finalized members, AXI attempt recovery, collection and closing-analysis gate placement, reducer evidence binding, exception pass-through, and the amendment 54 tests. The protected `battery_float.py` and provenance checker were unchanged. No commit or out-of-scope repository write was made.

| Amendment | Files and functions | Rows and evidence |
|---|---|---|
| 49 | `run_campaign` whole-window gate; `whole_window` and analysis-input member lists | Superseded members enter the same gate with recorded digests. A mutation omitting them made the targeted tests RED; production charging, altered, and deleted-quarantine probes were GREEN. Full row-by-row evidence remains incomplete. |
| 50 | `scored_reduce._check_battery_evidence`; fixture producer | No-bundle markers now refuse; fresh no-window verdict digests are bound; all nonpass statuses are considered. Loading the old reducer made the focused test RED; the updated focused tests were GREEN. |
| 51 | `tests/test_bfgs_consumer_sweep.py` | **Blocked before editing.** The current sweep is RED. The read-only prototype reports **120 distinct sites in 89 functions**, but it lacks parts of the ruled detector, so this is not the required final sweep count. |
| 52 | `GATE_EXCEPTIONS` in `bundle_read` and the eight consumers | Guard suite GREEN within V2. Mutations that swallowed a gate exception, imported `battery_float` into a consumer, or added a ninth unguarded module made targeted checks RED. The named `analysis_manifest_v3.py` residual remains outside S1. |
| 53 | `evaluate_member`; `run_campaign` final gate | A charging bundle can complete collection evaluation; the final gate includes evaluated bundles whose directories were later deleted. The collection test is GREEN. Production rows R53-1, R53-2, and R53-4 still need full counterfactual evidence. |
| 54 | `tests/test_bundle_read.py` | Both R47-4 forms are GREEN. Skipping unparseable candidates made R47-4 RED. |
| 55 | `authenticate_window_members`; `supersession_record_field_valid` | Recorded digest mismatch, absent files, symlinks, and custody priority pass focused tests. Mutations ignoring the third tuple element or replacing the existing strict validator made tests RED; R55-8’s unchanged-validator behavior remains GREEN. |
| 56 | `recorded_member_paths`; AXI ledger recovery; three window consumers | A production analysis-loader fixture with a deleted recorded member now raises labelled `CustodyUnreadable`; the old behavior returned `bundle_missing`. The focused window-consumer class passed **31 tests**. Production R56-4 and R56-5 counterfactual runs remain outstanding. |

The required allowlist cannot be supplied under amendment 51’s current four classes. These reported prototype rows establish the conflict:

| Site | Required class | Why no permitted class fits |
|---|---|---|
| `joulewise/battery_float.py::authenticate_bundle`, `direct:_required_object`, `metadata.json` | None | Returns a `PairVerdict` containing battery measurements; it performs authentication itself and `battery_float.py` must remain byte-identical. |
| `joulewise/bundle_read.py::BundleReader.metadata`, `direct:_strict_json`, `metadata.json` | None | Returns full metadata to claim consumers and is itself the reader-form gate. |
| `joulewise/bundle_read.py::BundleReader.raw_summary`, `direct:_tolerant_json`, `summary_metrics.json` | None | Returns energy-bearing summary content and is callable without a preceding gate. |

## Verification notes

V2 passed, both builder checks printed `forward check: byte-identical entries=69`, focused tests passed, `py_compile` passed, and `git diff --check` was clean. The exact final five lines for V1, V2, and both builder runs are in the envelope. V1 was interrupted while executing `test_differential_oracle_200_nights`; the separately run sweep already fails because its old allowlist no longer matches the new gate placement.

## Residual risk

**NEEDS_RULING — Question:** How should amendment 51 classify reads performed by authentication and reader functions that fail all four stated allowlist conditions?

**Options considered:** Add a tightly defined `gate_implementation` class, exempt specific gate-internal reads from reporting, or change those functions and their contracts. **Recommendation:** Add the narrow class with named functions and reasons so the reads remain inventoried. **Blocked work:** The ruled detector, complete allowlist with per-row reasons, final sweep count, remaining RED/GREEN rows, and green V1.

A second ruling is needed on whether §9’s N-1 comment correction is authorized in `tests/test_battery_float_consumers.py` under the prompt’s amendment-36-only restriction.