```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented P1–P8 within WRITE_SCOPE; the named 453-test acceptance suite passed.",
  "workspace": {
    "base_requested": "702afd8d",
    "base_mode": "exact",
    "head_start": "702afd8d80a440d8a549dea1a3fff87fe8c9fa0b",
    "head_end": "702afd8d80a440d8a549dea1a3fff87fe8c9fa0b",
    "upstream_end": null,
    "branch": "feat/2026-09-23-a280-kind-table"
  },
  "pathspec": [
    "joulewise/night_kinds.py",
    "joulewise/evidence_night.py",
    "joulewise/night_gate.py",
    "joulewise/quiet_predicate_campaign.py",
    "scripts/gen_evidence_night.py",
    "tests/test_night_kinds.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_kinds tests.test_night_gate tests.test_evidence_night tests.test_quiet_predicate_campaign tests.test_gen_evidence_night tests.test_arm_retry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 453 tests in 422.705s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 453 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
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
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff 702afd8d --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/evidence_night.py",
          "joulewise/night_gate.py",
          "joulewise/night_kinds.py",
          "joulewise/quiet_predicate_campaign.py",
          "scripts/gen_evidence_night.py",
          "tests/test_night_kinds.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^(joulewise/(evidence_night|night_gate|night_kinds|quiet_predicate_campaign)\\.py|scripts/gen_evidence_night\\.py|tests/test_night_kinds\\.py)(\\n|$)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The two process-list tests named in the brief are outside the authorized named acceptance modules.",
      "needs": "Magistrate reruns those two tests at the bench."
    }
  ]
}
```

## Change

- **P1:** [night_kinds.py:41](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/night_kinds.py:41) marks payload rows; [night_gate.py:150](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/night_gate.py:150) probes any registered payload kind. Regression: `test_probe_accepts_a_registered_third_payload_kind`.
- **P2:** [evidence_night.py:1362](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/evidence_night.py:1362) scopes the two arm checks by their separate row flags. Regression: `test_arm_flags_match_t0_scoping_when_flags_differ`.
- **P3:** [test_night_kinds.py:228](/Users/edr/code/wt-d8cc9c0a-a280a/tests/test_night_kinds.py:228) runs K3 through real `prepare` and candidate-head sealing. Regressions: `test_prepare_authors_row_paths_and_seals_candidate_at_head` and `test_k3_kills_prefix_and_suffix_mutations`.
- **P4:** [quiet_predicate_campaign.py:167](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/quiet_predicate_campaign.py:167) reads the row kind; [gen_evidence_night.py:23](/Users/edr/code/wt-d8cc9c0a-a280a/scripts/gen_evidence_night.py:23) reads the calibration basename stem. Regressions: `test_manifest_verifier_uses_row_kind` and `test_generator_uses_calibration_basename_from_row`.
- **P5:** [quiet_predicate_campaign.py:161](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/quiet_predicate_campaign.py:161) checks the protocol window without imposing the Python row default. Regression: `test_manifest_window_follows_protocol_not_row_default`.
- **P6:** [night_kinds.py:73](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/night_kinds.py:73) uses `None` for calibration path identity; [evidence_night.py:162](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/evidence_night.py:162) refuses its use in preparation paths. Regressions: `test_rows_and_unknown_kind` and `test_calibration_cannot_supply_preparation_paths`.
- **P7:** [test_night_kinds.py:171](/Users/edr/code/wt-d8cc9c0a-a280a/tests/test_night_kinds.py:171) creates a unique `mkdtemp` fixture and restores `TZ` in teardown. Regression: `test_fixture_is_unique_and_local_to_one_run`. Golden replay rebuilds the `cdc05e9b` archive in that fixture, relocates the retained base bytes to its paths, recomputes the wrapper sidecar digest, then compares the current manifest addition and downstream bytes.
- **P8:** [gen_evidence_night.py:16](/Users/edr/code/wt-d8cc9c0a-a280a/scripts/gen_evidence_night.py:16) again re-exports `manifest_for`. Regression: `test_generator_exports_manifest_for`.

## Verification notes

The exact named acceptance command passed: **453 tests, OK**. `git diff --check` passed, and `git diff 702afd8d --name-only` lists only the six allowed paths. No commit was made.

## Residual risk

The magistrate should double-check the final diff and rerun `test_real_collect_no_power_reaps_all_recorded_workers` and `test_cleanup_refusal_reports_the_failure_it_interrupted` at the bench; both are outside this round’s named acceptance modules.