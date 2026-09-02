```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented V5-PREFILL-REALIZED-IDS-CHECK-01 within the exhaustive scope; acceptance is blocked only because the mandatory new kernel IDs require updating the out-of-scope live-ID fixture.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "49cc86d0125172606f3c7672827a60ea62031cbf",
    "head_end": "49cc86d0125172606f3c7672827a60ea62031cbf",
    "upstream_end": null,
    "branch": "feat/2026-09-01-realized-prefill"
  },
  "pathspec": [
    "TASK_QUEUE.md",
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "docs/process/state_kernel.json",
    "joulewise/bundle_read.py",
    "joulewise/publication_privacy.py",
    "joulewise/schemas.py",
    "scripts/run_campaign.py",
    "tests/goldens/config_schema.json",
    "tests/test_bundle_read.py",
    "tests/test_d117_contrast_v5_pack.py",
    "tests/test_publication_privacy.py",
    "tests/test_run_campaign.py",
    "tests/test_schemas.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_schemas tests.test_bundle_read tests.test_run_campaign tests.test_publication_privacy tests.test_d117_contrast_v5_pack tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: Items in the first set but not the second:",
          "'V5-PREFILL-REALIZED-IDS-CHECK-01'",
          "'V5-PREFILL-REALIZED-PROJECTION-02'",
          "Ran 456 tests in 176.543s",
          "FAILED (failures=1, skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_schemas tests.test_bundle_read tests.test_run_campaign tests.test_publication_privacy tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 417 tests in 179.573s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_schemas.BenchmarkConfigTests.test_prompt_token_expectation_is_closed_typed_and_exported tests.test_schemas.BenchmarkConfigTests.test_prompt_token_expectation_rejects_malformed_registration tests.test_schemas.BenchmarkConfigTests.test_prompt_token_expectation_requires_prompt_text_source tests.test_schemas.BenchmarkConfigTests.test_legacy_config_to_dict_bytes_remain_golden_identical tests.test_bundle_read.PromptRealizationExpectationTests tests.test_run_campaign.RunCampaignTests.test_prompt_realization_mismatch_stops_before_second_child tests.test_run_campaign.RunCampaignTests.test_prompt_realization_reader_codes_are_unwaivable_including_any tests.test_publication_privacy.PublicationPrivacyTests.test_prompt_token_expectation_is_allowlisted_and_retained tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_prefill_configs_close_candidate_family_and_tree_registration tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_distinct_arm_pins_project_to_each_arms_own_configs tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_closed_pack_prompt_registration_refusals_are_defect_shaped",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 20 tests in 4.066s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "build",
      "cmd": "python3 scripts/gen_state.py --check",
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
      "id": "V5",
      "kind": "lint",
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
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c 'import hashlib,importlib.util,json; from pathlib import Path; p=Path(\"configs/campaigns/d117_contrast_v5/generate_configs.py\"); s=importlib.util.spec_from_file_location(\"g\",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); b=json.dumps(m.dominance_criterion_registration(),ensure_ascii=False,sort_keys=True,separators=(\",\",\":\")).encode(); print(hashlib.sha256(b).hexdigest())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b$"
      }
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "python3 -c 'import hashlib,json; from pathlib import Path; from joulewise.cli import validate_bundle; root=Path(\"/Users/edr/code/JouleWise/runs_window_c_20260726\"); rows=[(p.name,validate_bundle(p)) for p in sorted(root.iterdir()) if p.is_dir() and (p/\"config.json\").is_file()]; payload=json.dumps(rows,sort_keys=True,separators=(\",\",\":\")); print(f\"bundles={len(rows)} problems={sum(len(v) for _,v in rows)} sha256={hashlib.sha256(payload.encode()).hexdigest()}\"); print(\"tail=\"+json.dumps(rows[-2:],sort_keys=True))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "bundles=47 problems=0 sha256=75e8157632a0dbada5ece28d55a2061e8278db1c690c92b87bc7e3b665419b10",
          "tail=[[\"p2015-df-cmp-abba-ph-decode-b10-b1\", []], [\"p2015-df-cmp-abba-ph-decode-b10-b2\", []]]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "bundles=47 problems=0 sha256=75e8157632a0dbada5ece28d55a2061e8278db1c690c92b87bc7e3b665419b10"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state.TestRefreshedStateFidelity.test_exact_live_id_set",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: Items in the first set but not the second:",
          "'V5-PREFILL-REALIZED-PROJECTION-02'",
          "'V5-PREFILL-REALIZED-IDS-CHECK-01'",
          "Ran 1 test in 0.001s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "tests/test_gen_state.py hard-codes EXPECTED_IDS and len(self.tasks) == 110. The two mandated live kernel rows make the requested suite fail, but that test file is outside WRITE_SCOPE; it was not modified.",
      "needs": "Authorize tests/test_gen_state.py so the two IDs can be added and the expected live count changed from 110 to 112."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The branch lacks 44-sol-consult-realized.md, 44c-RULING-realized-prefill-check.md, and 44d-fable-blind-consult-realized-prefill.md. They were read read-only from the clean main checkout; kernel authority uses the branch-present 44b seat as an explicitly labelled placeholder.",
      "needs": "Land the ratified 44c trace and retarget the two kernel authority pointers during lead integration."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "A pre-edit canonical discover run was stopped after becoming no longer probative; the requested focused suite covers the implementation and has only F1's deterministic fixture failure.",
      "needs": "After authorizing the fixture repair, rerun the requested focused command and the canonical discovery suite."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_gen_state.py"
    ],
    "reason": "The mandated two live state-kernel rows must be reflected in the test's exact live-ID registry.",
    "blocked_work": "A fully green requested verification command and acceptance-ready handoff.",
    "minimal_change": "Add V5-PREFILL-REALIZED-IDS-CHECK-01 and V5-PREFILL-REALIZED-PROJECTION-02 to EXPECTED_IDS, update the documented arithmetic, and change the exact live count from 110 to 112."
  }
}
```

## Change

Implemented the ruled closed expectation schema, arm-derived `_v5` generator projection, closed-pack refusals, succeeded-bundle realized-evidence checks, runner classification and non-waivability, privacy projection, and both kernel rows. `RUN_STATE.md` and `TASK_QUEUE.md` were regenerated; only `TASK_QUEUE.md` changed bytes.

`UNWAIVABLE_COLLECTION_INTEGRITY_FLAGS` is the mechanism that prevents all three reader codes from waiver recovery before the `scope == "any"` branch.

No retained bundle, frozen paper file, frozen dominance registration, out-of-scope module, or other unlisted path was modified.

## Ruling trace

| 44c clause | Implementation hunk | Defect-shaped test |
|---|---|---|
| Closed optional expectation schema; prompt-text-only; omission serialization | [schemas.py](/Users/edr/code/JouleWise-wt-realized/joulewise/schemas.py:70), [schemas.py](/Users/edr/code/JouleWise-wt-realized/joulewise/schemas.py:843), [schemas.py](/Users/edr/code/JouleWise-wt-realized/joulewise/schemas.py:1137), [schemas.py](/Users/edr/code/JouleWise-wt-realized/joulewise/schemas.py:1298) | `test_prompt_token_expectation_is_closed_typed_and_exported`, `test_prompt_token_expectation_rejects_malformed_registration`, `test_prompt_token_expectation_requires_prompt_text_source`, `test_legacy_config_to_dict_bytes_remain_golden_identical` |
| Config-key and publication allowlists | [schemas.py](/Users/edr/code/JouleWise-wt-realized/joulewise/schemas.py:185), [publication_privacy.py](/Users/edr/code/JouleWise-wt-realized/joulewise/publication_privacy.py:89) | `test_prompt_token_expectation_is_closed_typed_and_exported`, `test_prompt_token_expectation_is_allowlisted_and_retained` |
| Per-arm generator projection, without tokenizer/model calls | [generate_configs.py](/Users/edr/code/JouleWise-wt-realized/configs/campaigns/d117_contrast_v5/generate_configs.py:1405) | `test_prefill_configs_close_candidate_family_and_tree_registration`, `test_distinct_arm_pins_project_to_each_arms_own_configs` |
| Closed-pack missing/invalid/inconsistent refusals; decode omission | [generate_configs.py](/Users/edr/code/JouleWise-wt-realized/configs/campaigns/d117_contrast_v5/generate_configs.py:3260), [generate_configs.py](/Users/edr/code/JouleWise-wt-realized/configs/campaigns/d117_contrast_v5/generate_configs.py:3287) | `test_closed_pack_prompt_registration_refusals_are_defect_shaped` |
| Named reader evidence and mismatch outcomes | [bundle_read.py](/Users/edr/code/JouleWise-wt-realized/joulewise/bundle_read.py:128), [bundle_read.py](/Users/edr/code/JouleWise-wt-realized/joulewise/bundle_read.py:930) | `test_coherent_count_mutation_is_one_mismatch`, `test_equal_counts_different_hash_names_hash_mismatch`, `test_count_and_hash_mutation_is_one_problem_naming_both`, `test_domain_mutation_is_mismatch`, `test_one_count_surface_mutation_is_evidence_inconsistent`, `test_changed_prompt_text_without_updated_hash_is_inconsistent`, `test_missing_provenance_and_marker_are_never_a_pass` |
| Legacy zero-impact and consumer neither-branch propagation | [bundle_read.py](/Users/edr/code/JouleWise-wt-realized/joulewise/bundle_read.py:930) | `test_legacy_config_without_expectation_gets_zero_new_problems`, `test_real_validate_bundle_preserves_exact_named_refusal`, `test_mismatch_reaches_floor_and_analysis_admission_as_neither_branch` |
| Runner flags, failure classification, and waiver exclusion | [run_campaign.py](/Users/edr/code/JouleWise-wt-realized/scripts/run_campaign.py:224), [run_campaign.py](/Users/edr/code/JouleWise-wt-realized/scripts/run_campaign.py:452), [run_campaign.py](/Users/edr/code/JouleWise-wt-realized/scripts/run_campaign.py:2779), [run_campaign.py](/Users/edr/code/JouleWise-wt-realized/scripts/run_campaign.py:2843), [run_campaign.py](/Users/edr/code/JouleWise-wt-realized/scripts/run_campaign.py:5325) | `test_prompt_realization_reader_codes_are_unwaivable_including_any` |
| First mismatch stops a max-failures-one campaign before child two | Existing strict-attempt exit plus the new reader code propagation above | `test_prompt_realization_mismatch_stops_before_second_child` |
| Kernel implementation and council-trigger follow-up | [state_kernel.json](/Users/edr/code/JouleWise-wt-realized/docs/process/state_kernel.json:4782), [state_kernel.json](/Users/edr/code/JouleWise-wt-realized/docs/process/state_kernel.json:4814) | `scripts/gen_state.py --check`; exact-live-ID test is the scope blocker |
| Ruling 49b: `workload_for()` signature/prefill branch | `workload_for`, [generate_configs.py](/Users/edr/code/JouleWise-wt-realized/configs/campaigns/d117_contrast_v5/generate_configs.py:1405) | Per-arm generator tests above |
| Ruling 49b: authorized call sites | `build_plan` call at [generate_configs.py](/Users/edr/code/JouleWise-wt-realized/configs/campaigns/d117_contrast_v5/generate_configs.py:1844); `config_for` call at line 1977; `build_tree` calls at lines 2677, 2679, 2682 | Per-arm generator tests above |
| Closed-pack hookup/function hunks | `_generate` hook at line 3260; `validate_prompt_realization_registration` at line 3287 | Closed-pack refusal test above |

The frozen dominance registration remained byte-identical: `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`.

## Surfaces table

Retained succeeded single-prompt bundle used for the audit:

`/Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-a2`

| Realized surface | Retained evidence | Decision |
|---|---|---|
| `metadata.workload_provenance.prompt.realized_token_count` | Present, `128` | Enabled |
| `metadata.workload_provenance.prompt.token_ids_sha256` | Present, `75644f38…feaf706` | Enabled |
| `metadata.workload_provenance.prompt.token_hash_domain` | Present, `joulewise.prompt_token_ids.v1` | Enabled |
| `metadata.workload_provenance.prompt.text_sha256` | Key present but null in this legacy bundle | Mandatory only when the new expectation is present; legacy remains gated out |
| Tokenize `end_metadata.prompt_tokens` | [events.jsonl](/Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-a2/events.jsonl:13): `128` | Enabled |
| Prefill `start_metadata.prompt_tokens` | [events.jsonl](/Users/edr/code/JouleWise/runs_window_c_20260726/p2015-df-cmp-abba-ph-decode-b04-a2/events.jsonl:16): `128` | Enabled |
| `workload_observed.token_count − output_token_count` | `640 − 512 = 128` | Enabled |

The whole retained-corpus result was byte-for-byte stable before and after:

```text
bundles=47 problems=0 sha256=75e8157632a0dbada5ece28d55a2061e8278db1c690c92b87bc7e3b665419b10
tail=[["p2015-df-cmp-abba-ph-decode-b10-b1", []], ["p2015-df-cmp-abba-ph-decode-b10-b2", []]]
```

## Verification notes

The sole requested-suite failure is mechanical baseline drift in `tests/test_gen_state.py`: it expects 110 live IDs and does not include the two rows the task required. The implementation and all in-scope tests pass.

The branch does not contain three commanded trace files. Their clean-main copies were used read-only, and the kernel explicitly labels its 44b authority link as a branch-local placeholder.

## Full diff: `tests/test_d117_contrast_v5_pack.py`

```diff
diff --git a/tests/test_d117_contrast_v5_pack.py b/tests/test_d117_contrast_v5_pack.py
index 5e8b8940..dfb2cf4a 100644
--- a/tests/test_d117_contrast_v5_pack.py
+++ b/tests/test_d117_contrast_v5_pack.py
@@ -20,6 +20,7 @@ from joulewise.analysis_manifest_v3 import (
 )
 from joulewise.aggregate import student_t_critical_95
 from joulewise.provenance import prompt_token_ids_sha256
+from joulewise.schemas import BenchmarkConfig
 
 
 ROOT = Path(__file__).resolve().parents[1]
@@ -265,6 +266,14 @@ class D117ContrastV5PackTests(unittest.TestCase):
         self.generator.generate(root, self.generator.GenerationIdentity())
         return root / "configs/campaigns" / PACK_ID
 
+    @staticmethod
+    def science_config_paths(pack: Path) -> list[Path]:
+        return sorted(
+            path
+            for path in pack.glob("[0-9][0-9]_*/*.json")
+            if path.name != "order_manifest.json"
+        )
+
     def test_unresolved_prefill_has_no_default_and_refuses_before_panel_load(self) -> None:
         args = self.generator.parse_args(
             [
@@ -467,6 +476,196 @@ class D117ContrastV5PackTests(unittest.TestCase):
             self.assertEqual(second, first)
             self.assertEqual(list(root.glob(".d117-v5-stage-*")), [])
 
+    def test_prefill_configs_close_candidate_family_and_tree_registration(self) -> None:
+        with tempfile.TemporaryDirectory(prefix="d117-v5-realization-") as temporary:
+            root = Path(temporary)
+            self.configure(self.write_prefill_pin(root))
+            pack = self.generate_pack(root)
+            candidate = json.loads(
+                (pack / "prefill_prompt_candidate.json").read_text(
+                    encoding="utf-8"
+                )
+            )
+            candidate_by_model = {
+                row["model_id"]: row
+                for row in candidate["token_count_basis"]["per_model"]
+            }
+            tree = json.loads(
+                (pack / "plan_tree.json").read_text(encoding="utf-8")
+            )
+            units = {
+                row["identity_unit_id"]: row
+                for row in tree["arm_attachments"]["identity_pin_projection"][
+                    "identity_units"
+                ]
+            }
+
+            prefill_count = 0
+            decode_count = 0
+            for config_path in self.science_config_paths(pack):
+                raw = json.loads(config_path.read_text(encoding="utf-8"))
+                workload = raw["workload_profile"]
+                arm = next(
+                    arm
+                    for arm in ("A", "B")
+                    if raw["model"]["name"] == self.generator.MODELS[arm]["name"]
+                )
+                if workload.get("prompt_text") is None:
+                    decode_count += 1
+                    self.assertNotIn("prompt_token_expectation", workload)
+                    continue
+                prefill_count += 1
+                expectation = workload["prompt_token_expectation"]
+                candidate_row = candidate_by_model[self.generator.MODEL_IDS[arm]]
+                family = json.loads(
+                    (
+                        pack
+                        / self.generator.family_relpath(
+                            self.generator.PREFILL_ARM, arm
+                        )
+                    ).read_text(encoding="utf-8")
+                )
+                self.assertEqual(
+                    expectation["token_ids_sha256"],
+                    candidate_row["token_ids_sha256"],
+                )
+                self.assertEqual(
+                    expectation["token_count"], candidate_row["token_count"]
+                )
+                self.assertEqual(
+                    expectation["token_count"],
+                    family["workload_profile"]["prompt_tokens"],
+                )
+                self.assertEqual(
+                    units[f"{arm}/{self.generator.PREFILL_ARM}"][
+                        "declared_identity"
+                    ]["workload_profile"],
+                    BenchmarkConfig.from_mapping(raw).to_dict()[
+                        "workload_profile"
+                    ],
+                )
+
+        self.assertEqual(prefill_count, 40)
+        self.assertEqual(decode_count, 40)
+
+    def test_distinct_arm_pins_project_to_each_arms_own_configs(self) -> None:
+        with tempfile.TemporaryDirectory(prefix="d117-v5-realization-arms-") as temporary:
+            root = Path(temporary)
+            self.configure(self.write_prefill_pin(root))
+            self.generator.PREFILL_TOKEN_IDS["B"] = [8] * self.generator.PREFILL_LENGTH
+            self.generator.PREFILL_TOKEN_IDS_SHA256["B"] = prompt_token_ids_sha256(
+                self.generator.PREFILL_TOKEN_IDS["B"]
+            )
+            pack = self.generate_pack(root)
+            observed: dict[str, set[str]] = {"A": set(), "B": set()}
+            for config_path in self.science_config_paths(pack):
+                raw = json.loads(config_path.read_text(encoding="utf-8"))
+                expectation = raw["workload_profile"].get(
+                    "prompt_token_expectation"
+                )
+                if expectation is None:
+                    continue
+                arm = next(
+                    arm
+                    for arm in ("A", "B")
+                    if raw["model"]["name"] == self.generator.MODELS[arm]["name"]
+                )
+                observed[arm].add(expectation["token_ids_sha256"])
+
+        self.assertEqual(
+            observed,
+            {
+                "A": {self.generator.PREFILL_TOKEN_IDS_SHA256["A"]},
+                "B": {self.generator.PREFILL_TOKEN_IDS_SHA256["B"]},
+            },
+        )
+        self.assertNotEqual(observed["A"], observed["B"])
+
+    def test_closed_pack_prompt_registration_refusals_are_defect_shaped(self) -> None:
+        with tempfile.TemporaryDirectory(prefix="d117-v5-realization-refuse-") as temporary:
+            root = Path(temporary)
+            self.configure(self.write_prefill_pin(root))
+            pack = self.generate_pack(root)
+            configs = self.science_config_paths(pack)
+            prefill_path = next(
+                path
+                for path in configs
+                if json.loads(path.read_text())["workload_profile"].get(
+                    "prompt_text"
+                )
+                is not None
+            )
+            decode_path = next(
+                path
+                for path in configs
+                if json.loads(path.read_text())["workload_profile"].get(
+                    "prompt_text"
+                )
+                is None
+            )
+            original_prefill = prefill_path.read_text(encoding="utf-8")
+            original_decode = decode_path.read_text(encoding="utf-8")
+            base = json.loads(original_prefill)
+            expectation = base["workload_profile"]["prompt_token_expectation"]
+
+            missing = copy.deepcopy(base)
+            missing["workload_profile"].pop("prompt_token_expectation")
+            prefill_path.write_text(json.dumps(missing), encoding="utf-8")
+            with self.assertRaisesRegex(
+                ValueError, "prompt_realization_registration_missing"
+            ):
+                self.generator.validate_prompt_realization_registration(pack)
+            prefill_path.write_text(original_prefill, encoding="utf-8")
+
+            invalid_expectations = (
+                {key: value for key, value in expectation.items() if key != "token_count"},
+                {**expectation, "token_hash_domain": "wrong.domain"},
+                {**expectation, "token_count": True},
+                {**expectation, "token_ids_sha256": "A" * 64},
+            )
+            for invalid in invalid_expectations:
+                changed = copy.deepcopy(base)
+                changed["workload_profile"]["prompt_token_expectation"] = invalid
+                prefill_path.write_text(json.dumps(changed), encoding="utf-8")
+                with self.subTest(invalid=invalid), self.assertRaisesRegex(
+                    ValueError, "prompt_realization_registration_invalid"
+                ):
+                    self.generator.validate_prompt_realization_registration(pack)
+                prefill_path.write_text(original_prefill, encoding="utf-8")
+
+            decode = json.loads(original_decode)
+            decode["workload_profile"]["prompt_token_expectation"] = expectation
+            decode_path.write_text(json.dumps(decode), encoding="utf-8")
+            with self.assertRaisesRegex(
+                ValueError, "prompt_realization_registration_invalid"
+            ):
+                self.generator.validate_prompt_realization_registration(pack)
+            decode_path.write_text(original_decode, encoding="utf-8")
+
+            inconsistent = copy.deepcopy(base)
+            inconsistent["workload_profile"]["prompt_token_expectation"] = {
+                **expectation,
+                "token_count": expectation["token_count"] + 1,
+            }
+            prefill_path.write_text(json.dumps(inconsistent), encoding="utf-8")
+            with self.assertRaisesRegex(
+                ValueError, "prompt_realization_registration_inconsistent"
+            ):
+                self.generator.validate_prompt_realization_registration(pack)
+            prefill_path.write_text(original_prefill, encoding="utf-8")
+
+            family_path = pack / self.generator.family_relpath(
+                self.generator.PREFILL_ARM, "A"
+            )
+            original_family = family_path.read_text(encoding="utf-8")
+            family = json.loads(original_family)
+            family["workload_profile"]["prompt_tokens"] += 1
+            family_path.write_text(json.dumps(family), encoding="utf-8")
+            with self.assertRaisesRegex(
+                ValueError, "prompt_realization_registration_inconsistent"
+            ):
+                self.generator.validate_prompt_realization_registration(pack)
+
     def test_member_model_config_refuses_missing_runtime_identity_pin(self) -> None:
         with tempfile.TemporaryDirectory(prefix="d117-v5-pin-") as temporary:
             self.configure(self.write_prefill_pin(Path(temporary)))
```

The diff is add-only: `199 insertions, 0 deletions`; pinned dominance bytes and every existing golden/common-mode test remain untouched.

## `git diff --stat`

```text
 TASK_QUEUE.md                                      |   4 +
 .../campaigns/d117_contrast_v5/generate_configs.py | 187 +++++++++++++-
 docs/process/state_kernel.json                     |  73 ++++++
 joulewise/bundle_read.py                           | 183 +++++++++++++
 joulewise/publication_privacy.py                   |   1 +
 joulewise/schemas.py                               | 125 +++++++++
 scripts/run_campaign.py                            |  19 +-
 tests/goldens/config_schema.json                   |  57 +++++
 tests/test_bundle_read.py                          | 284 +++++++++++++++++++++
 tests/test_d117_contrast_v5_pack.py                | 199 +++++++++++++++
 tests/test_publication_privacy.py                  |  25 ++
 tests/test_run_campaign.py                         | 137 +++++++++-
 tests/test_schemas.py                              |  96 +++++++
 13 files changed, 1378 insertions(+), 12 deletions(-)
```

## Residual risk

`NEEDS_SCOPE`: authorize only `tests/test_gen_state.py` for the exact-ID/count repair described in `scope_expansion`. After that, regenerate/check state and rerun the focused and canonical suites.