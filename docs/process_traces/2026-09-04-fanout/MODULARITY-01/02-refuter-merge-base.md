```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The refreshed mission delta is in scope and its claimed tests pass, but fail-open campaign generation and mutable frozen registry identities make it not landable.",
  "workspace": {
    "base_requested": "git merge-base origin/main HEAD = b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "99155bb4d00c95d494b508fb37ae1fa8ab79017f",
    "head_end": "99155bb4d00c95d494b508fb37ae1fa8ab79017f",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-MODULARITY-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/MODULARITY-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "MOD-R2-001",
        "severity": "blocker",
        "location": "configs/campaigns/p2_015_floors/generate_configs.py:135,177-190,325-388",
        "text": "CampaignSpec validation accepts n below the governed floor minimum and arbitrary non-ABBA arity/labels, then emits primary_claim_gate cells labelled comparative_abba. Executed inputs n=1 and X1/Y1/Z1 both generated successfully, although floor extraction requires n>=5 and exactly A1/B1/B2/A2.",
        "counterfactual": "A spec with campaign.n=1, or block_pattern=[X1,Y1,Z1], must be refused before output; it currently emits 30 or 232 runnable configs respectively."
      },
      {
        "id": "MOD-R2-002",
        "severity": "blocker",
        "location": "configs/campaigns/p2_015_floors/generate_configs.py:752-828",
        "text": "The generator accepts an occupied --out-dir, overwrites matching files, preserves stale JSON, and exits 0. That produces a mixed tree which downstream campaign discovery refuses as configs absent from the manifest, so a reported-success generation can be unusable.",
        "counterfactual": "Place stale.json in a fresh output directory before generation; the CLI exits 0 and stale.json survives."
      },
      {
        "id": "MOD-R2-003",
        "severity": "blocker",
        "location": "joulewise/detection_floor_registry.py:89-194; tests/test_modularity.py:195-244",
        "text": "The detection-floor registry's fixed v1/frozen identity is not bound to an immutable trust anchor or carried into floor artifacts. Updating both the JSON and adjacent checksum admits new claim metrics/scopes under the same identity; the new test explicitly blesses this. Historical validation therefore depends on mutable checkout state rather than the registry bytes that governed the artifact.",
        "counterfactual": "Keep registry_id=detection_floor_closed_sets_v1 and freeze_status=frozen, add phase_energy_j.score and successor_window, then update the adjacent checksum; the loader and both validators accept them."
      },
      {
        "id": "MOD-R2-004",
        "severity": "blocker",
        "location": "joulewise/analysis_manifest.py:522-583",
        "text": "The AP-2 registry validator now permits its frozen four-profile family to shrink while retaining registry_id=slice_2m_ap2_v1, plan_id=AP-2, and freeze_status=frozen. Even when supplied the real AP-2 row, it does not compare condition declarations with AP-2's explicit four-profile selection scope.",
        "counterfactual": "Replace the six AP-2 pairs with only short_short versus long_short and validate against the real AP-2 row; validation_errors is []."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "mb=$(git merge-base origin/main HEAD); git diff --name-only \"$mb\"..HEAD | sort; git diff --quiet \"$mb\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["tests/test_floor_extraction.py", "tests/test_modularity.py"]},
      "expected": {"exit_code": 0, "tail_regex": "tests/test_modularity.py$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_modularity tests.test_analysis_manifest tests.test_generate_matrix tests.test_detection_floor tests.test_floor_extraction",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 378 tests in 17.770s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 378 tests[\\s\\S]*OK \\(skipped=1\\)$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "tmp=$(mktemp -d); git archive HEAD joulewise configs tests/test_modularity.py docs/contracts/analysis_plans.md | tar -x -C \"$tmp\"; git archive $(git merge-base origin/main HEAD) configs/campaigns/p2_015_floors/generate_configs.py | tar -x -C \"$tmp\"; (cd \"$tmp\" && PYTHONPATH=\"$tmp\" python3 -m unittest tests.test_modularity.CampaignSpecificationTests.test_model_n_profiles_block_pattern_suite_and_prefix_come_from_one_spec)",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["FileNotFoundError: .../generated/calibration_plan.json", "FAILED (errors=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(errors=1\\)$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "tmp=$(mktemp -d); git archive HEAD joulewise configs tests/test_modularity.py docs/contracts/analysis_plans.md | tar -x -C \"$tmp\"; git archive $(git merge-base origin/main HEAD) joulewise/analysis_manifest.py | tar -x -C \"$tmp\"; (cd \"$tmp\" && PYTHONPATH=\"$tmp\" python3 -m unittest tests.test_modularity.ClosedSetRegistryTests.test_analysis_condition_pairs_are_validated_as_registry_declarations)",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["registry.condition_pairs: must contain the six frozen AP-2 pairs", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "tmp=$(mktemp -d); git archive HEAD joulewise configs tests/test_modularity.py docs/contracts/analysis_plans.md | tar -x -C \"$tmp\"; git archive $(git merge-base origin/main HEAD) joulewise/detection_floor.py | tar -x -C \"$tmp\"; (cd \"$tmp\" && PYTHONPATH=\"$tmp\" python3 -m unittest tests.test_modularity.ClosedSetRegistryTests.test_changed_detection_floor_declaration_requires_matching_digest)",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["ImportError: cannot import name 'calibration_scope_is_registered'", "FAILED (errors=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(errors=1\\)$"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "tmp=$(mktemp -d); touch \"$tmp/stale.json\"; python3 configs/campaigns/p2_015_floors/generate_configs.py --campaign-spec configs/campaigns/p2_015_floors/campaign_spec.json --out-dir \"$tmp\"; rc=$?; if test -f \"$tmp/stale.json\"; then stale=yes; else stale=no; fi; printf 'EXIT_CODE=%s STALE_SURVIVES=%s\\n' \"$rc\" \"$stale\"; exit \"$rc\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["generated 282 runnable configs; model_tag=qwen25-1p5b-mlx; plan_id=p2-015-window-a-m3max-qwen25-1p5b-v1; calibration_plan_sha256=e529a0624b7618edaade511dd610ae0837f31de299dde642a055974c382681ab", "EXIT_CODE=0 STALE_SURVIVES=yes"]},
      "expected": {"exit_code": 0, "tail_regex": "EXIT_CODE=0 STALE_SURVIVES=yes$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check $(git merge-base origin/main HEAD)..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

1. `MOD-R2-001` — blocker. The configuration boundary is not yet a governed boundary. `n=1` is accepted even though generated claim cells carry `minimum_claim_n=1` and artifact validation requires at least five. A three-member `X/Y/Z` pattern is also accepted and emitted as `comparative_abba`, while the extant extractor requires exactly `A1/B1/B2/A2`. This is the deferred-estimator seam escaping into the supposedly usable generator rather than being refused.

2. `MOD-R2-002` — blocker. An occupied output-root CLI replay returned `EXIT_CODE=0 STALE_SURVIVES=yes`. `scripts/run_campaign.py` discovers every JSON config and rejects extras absent from the order manifest, so the generator can report success while leaving a tree that cannot pass campaign admission. Generate into a fresh staging directory and publish atomically, or refuse any non-default occupied root before the first write; add the executed stale-file case.

3. `MOD-R2-003` — blocker. The adjacent SHA-256 detects a one-file edit but does not authenticate the registry identity: changing both files is accepted under the same `v1`/`frozen` identifiers, and no resulting floor artifact records `DetectionFloorClosedSets.sha256`. Bind the governing registry digest/version into artifact provenance and validate it on replay, or install an equivalent immutable authority. A same-ID registry rewrite must not silently widen accepted claim vocabulary.

4. `MOD-R2-004` — blocker. The real AP-2 row says “Frozen four-profile 2M matrix,” but a one-pair registry with the unchanged frozen AP-2 identity validates with no errors. Registry-driven enumeration should remove duplicate Python tuples, not permit a new scientific family under an already-frozen identity. Require a new registry/plan identity for changed declarations, and test the real `ap_row` linkage rather than only `validate_analysis_registry(registry)`.

The declared implementation scope exactly matches the 13-path mission delta. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta. The claimed focused command passes all 378 tests. No prior refuter file is present in this directory. Re-tests of the named non-staleness classes are: accepted occupied root — OPEN (`MOD-R2-002`); trusted mutable identity — OPEN (`MOD-R2-003`/`004`); false counterfactual — CLOSED because each implementation-area revert makes its new test fail; spoofable CLI-only oracle — not present, because the main positive test inspects generated bytes and semantic fields rather than trusting stdout.

Behavioural counterfactuals were executed in isolated `mktemp` archive copies. Reverting the campaign generator made the multi-axis Qwen3/n=2/prefix/suite/pattern test fail before producing the requested output. Reverting `analysis_manifest.py` made the reduced-pair registry test fail on the old six-pair oracle. Reverting `detection_floor.py` made the successor metric/scope test fail at import because the registry-backed APIs do not exist. These are discriminating reversion failures; no repository file was mutated for counterfactual testing.

## Residual risk

The focused suite does not exercise a full custom-spec campaign through collection and floor extraction. That missing integration is material chiefly through `MOD-R2-001`; once the generator refuses unsupported semantics, a supported custom-spec end-to-end dry-run should be added. No whole-suite or quiet-machine work was run, per the preflight rule.
