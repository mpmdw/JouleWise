```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The 69-entry set and reader admission held under real-bundle probes, but amendment 40's audit has a false pass and two required counterfactual tests survive.",
  "workspace": {
    "base_requested": "24b79db349706c9945ce42789b1be862a4400edc",
    "base_mode": "descendant",
    "head_start": "b859317c7ea9286a2131ab3dce2e0d4ca9348ba5",
    "head_end": "b859317c7ea9286a2131ab3dce2e0d4ca9348ba5",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Reverse witness passes a changed bundle whose run_id names an included historical entry",
        "production_call_site": "scripts/build_battery_float_historical_bundles.py:229-247",
        "closure": "Compare each encountered named bundle with its included digest even when neither recomputed digest matches; test a changed copy."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Text scanner silently drops a bundle_tree_sha256 candidate",
        "production_call_site": "scripts/build_battery_float_historical_bundles.py:141-165",
        "closure": "Scan non-JSON text for the full ruled key pattern; list or reject unclassified candidates and test this shape."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Wrong-tree-identity test survives removal of identity validation",
        "production_call_site": "joulewise/bundle_read.py:247",
        "closure": "Replace an existing tree row for the identity case; test duplicate digest separately."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "PINNED_BUNDLE_SHA256 classification test survives a complete-digest mutant",
        "production_call_site": "scripts/build_battery_float_historical_bundles.py:54-55",
        "closure": "Assert the listed file_digest class and reason directly, alongside the file-byte hash."
      },
      {
        "id": "F5",
        "severity": "nit",
        "title": "The second RPT001 v2 citation is reported as unnamed rather than duplicate",
        "production_call_site": "scripts/build_battery_float_historical_bundles.py:202-207",
        "closure": "Determine duplicate reason independently of source traversal order and assert the emitted reason."
      }
    ],
    "same_signature": {
      "custody_turned_into_status": "no",
      "reader_overreaching_ruled_binding": "no",
      "set_enumeration_miss": "yes: F2 silently misses a candidate class; no missing entry was found in the current 69-entry set"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_bundle_read.StrictAccessorTests.test_historical_sources_and_builder_forward_check tests.test_bundle_read.StrictAccessorTests.test_candidate_from_unnamed_source_is_listed_not_included tests.test_bundle_read.StrictAccessorTests.test_rpt001_tree_entry_and_mutation tests.test_bundle_read.StrictAccessorTests.test_historical_set_rejects_wrong_tree_identity_and_duplicate tests.test_bundle_read.StrictAccessorTests.test_status_refusals_are_typed_and_unreadable_metadata_is_not tests.test_bundle_read.StrictAccessorTests.test_nonmock_missing_key_config_binding_details tests.test_bundle_read.StrictAccessorTests.test_marker_config_digest_mismatch_has_not_bound_prefix tests.test_bfgs_window_consumers tests.test_battery_float_consumers.ConsumerGuardTests.test_controller_replace_forgery_self_test tests.test_battery_float_consumers.ConsumerGuardTests.test_controller_replaced_types_are_not_pair_verdicts tests.test_battery_float_consumers.ConsumerGuardTests.test_replace_rows_precede_s1 tests.test_controller.BatteryBracketTests.test_wall_meter_unavailable_sentinel_marks_span_without_drift_measurement tests.test_controller.BatteryBracketTests.test_mock_has_no_idle_drift_sentinel_event",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 23 tests in 12.667s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 23 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "build",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["forward check: byte-identical entries=69"]
      },
      "expected": {"exit_code": 0, "tail_regex": "forward check: byte-identical entries=69"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_battery_float_historical_bundles.py --check --witness /Users/edr/code/JouleWise/runs*",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "witness_count included complete df-ph-decode-floor-mint1.json 50",
          "witness_count included tree analysis/rpt001-v2/input_manifest.json 6"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "witness_count included tree analysis/rpt001-v2/input_manifest.json 6"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_reverse_probe.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "reader_before unobserved_historical",
          "reader_after battery_float_evidence_missing ('prospective bundle',)",
          "witness_exit 0",
          "witness_tail ['forward check: byte-identical entries=69', 'witness bundles=1']"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "witness_exit 1"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_text_candidate_probe.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["candidates []", "build ([], [])"]
      },
      "expected": {"exit_code": 0, "tail_regex": "candidates \\[.*bundle_tree_sha256"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONPATH=/tmp/bfgs_mutant_shadow:/Users/edr/code/JouleWise-wt-s1cg-92472459 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_bundle_read.StrictAccessorTests.test_historical_set_rejects_wrong_tree_identity_and_duplicate",
      "cwd": "/tmp",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.074s", "", "OK"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V7",
      "kind": "build",
      "cmd": "GIT_DIR=/Users/edr/code/JouleWise/.git PYTHONPATH=/tmp/bfgs_mutant41 PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_mutant41/scripts/build_battery_float_historical_bundles.py --check",
      "cwd": "/tmp",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "forward check: byte-identical entries=69",
          "listed scripts/issue_dg071_dg075_statistics.py PINNED_BUNDLE_SHA256 complete 6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9: source not named by amendment 40"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "file_digest|FAILED"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This read-only execution audit ran focused tests and mutants, not the canonical full suite.",
      "needs": ""
    }
  ]
}
```

## Findings

**BLOCKER — F1.** The mandated reverse check has a false pass. I copied the committed RPT001 bundle `example-mac-mlx-local__r1` under `/tmp`, changed one byte of `power_trace.csv`, and ran the real reader and builder. The reader changed from `unobserved_historical` to `prospective bundle`; the builder still exited zero with `witness bundles=1` and no mismatch. Replay: `PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_reverse_probe.py`; its exact tail is in V4. [witness()](/Users/edr/code/JouleWise-wt-s1cg-92472459/scripts/build_battery_float_historical_bundles.py:229) checks a named entry only after a digest hit. Compare encountered run IDs with included entries even when their digests miss.

**SHOULD-FIX — F2.** The text scan accepts only two literal keys in ordinary lines. Replay: `PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_text_candidate_probe.py` printed `candidates []` and `build ([], [])` for `bundle_tree_sha256: aaaa…`. [The scanner](/Users/edr/code/JouleWise-wt-s1cg-92472459/scripts/build_battery_float_historical_bundles.py:141) should apply the ruled key pattern to these lines, then list the candidate or fail on an unclassified pair. This is an enumeration miss in the scanner; I found no missing entry among the current 69.

**SHOULD-FIX — F3.** The identity test appends a changed copy of an existing row, so duplicate-digest rejection masks identity validation. With the identity condition removed in a `/tmp` reader copy, the test still ended `Ran 1 test … OK` (V6); that mutant loaded a standalone wrong-identity row when it replaced rather than appended the entry. The real [loader](/Users/edr/code/JouleWise-wt-s1cg-92472459/joulewise/bundle_read.py:247) rejects that row today. Split the test into independent identity and duplicate cases.

**SHOULD-FIX — F4.** Changing the builder’s `PINNED_BUNDLE_SHA256` class from `file_digest` to `complete` in a `/tmp` copy left `--check` green: `forward check: byte-identical entries=69` (V7). The current [classification row](/Users/edr/code/JouleWise-wt-s1cg-92472459/scripts/build_battery_float_historical_bundles.py:54) is correct, and the pin equals the SHA-256 of the named `power_trace.csv`; the test must assert the listed class and reason so this counterfactual dies.

**NIT — F5.** All six `analysis/rpt001-v2/artifact_manifest.json` values duplicate the included input-manifest values, but the builder reports `source not named by amendment 40`; for example:

```text
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 2888c9d205df62e1136a376997ea8a6947683e4311eedaee20e3135bd559e213: source not named by amendment 40
```

The [reason selection](/Users/edr/code/JouleWise-wt-s1cg-92472459/scripts/build_battery_float_historical_bundles.py:202) depends on visiting the artifact manifest before the input manifest. Determine duplicate citations after collecting included rows.

The current set has exactly **50 floor, 13 tracked-fixture, and 6 RPT001 tree entries**. Independent checks found all 50 floor `(bundle_id, digest)` pairs, all 13 fixture digests, and all six manifest tree values matched; the full 1,402-bundle witness reported the expected included counts. A modified RPT001 copy failed both historical digest checks, and a real wall-meter run with its pair removed was refused as prospective. A window with an earlier status refusal followed by deleted raw evidence raised the original `CustodyFailure` with the second member’s label. The guard’s forged `replace(verdict, status='pass')` and borrowed-call probes were both flagged.

The other targeted mutants died: refusal-label regression (37), removal of tree admission (39), broad inclusion of an unnamed source (40), status-to-custody catch regression (42), and removal of the unavailable sentinel (43). The controller has **no production diff in this fix round**; the existing span test and two-second-probe test passed. A before/after sentinel counterfactual produced identical power-trace bytes and sampling stamps; without the marker, authentication failed as intended. The three protected modules remain byte-identical to `1417c0c4`, and the worktree is clean.

**Same-signature statement:** custody turned into status — **no**; reader overreaching the ruled binding — **no**; set enumeration miss — **yes**, for F2’s silent candidate omission, while the present 69-entry set was verified intact.

## Residual risk

The canonical full suite was not rerun in this read-only audit.