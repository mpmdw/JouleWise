from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import joulewise.analysis_manifest as analysis_manifest_module
from joulewise.analysis_engine import estimate_manifest_observations
from joulewise.analysis_engine.estimators import RatioObservation
from joulewise.analysis_engine.inputs import load_manifest as load_analysis_manifest
from joulewise.analysis_engine.sensitivity import randomization_check
from joulewise.analysis_manifest import (
    AnalysisManifestError,
    build_slice_2m_analysis_manifest,
    calculate_manifest_id,
    extract_analysis_plan_row,
    sha256_bytes,
    validate_analysis_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_matrix.py"
BASE_CONFIGS = (
    (ROOT / "configs" / "examples" / "mac_mlx_local.json", "qwen25-1p5b"),
    (ROOT / "configs" / "examples" / "mac_mlx_qwen35_122b.json", "qwen35-122b"),
)
METRIC_TAGS = ("gross_request", "idle_request", "gross_prefill", "gross_decode")
PAIRS = (
    ("short_short", "long_short"),
    ("short_short", "short_long"),
    ("short_short", "mid_mid"),
    ("long_short", "short_long"),
    ("long_short", "mid_mid"),
    ("short_long", "mid_mid"),
)


def run_generator(base: Path, tag: str, out_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--base",
            str(base),
            "--model-tag",
            tag,
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )


def load_manifest(out_dir: Path) -> dict:
    return json.loads((out_dir / "analysis_manifest.json").read_text(encoding="utf-8"))


def reidentify(manifest: dict) -> None:
    manifest["manifest_id"] = calculate_manifest_id(manifest)


def ratio_estimand(form: object) -> dict[str, object]:
    return {
        "form": form,
        "numerator_metric": "energy_request_j",
        "denominator": "runtime_observed_output_tokens",
        "denominator_unit": "token",
        "tokenizer_scope": "same_identity_required",
        "output_policy_scope": "same_policy_required",
    }


def named_strata(block_ids: list[str]) -> dict[str, object]:
    return {
        "scheme": "stratified_paired_label_swap",
        "exchangeability": "within_named_strata",
        "named_strata": [
            {"stratum_id": "early", "block_ids": block_ids[:3]},
            {"stratum_id": "late", "block_ids": block_ids[3:]},
        ],
    }


class AnalysisManifestTests(unittest.TestCase):
    def _generated_manifest(self, out_dir: Path) -> dict:
        result = run_generator(*BASE_CONFIGS[0], out_dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        return load_manifest(out_dir)

    def test_dispatcher_preserves_v1_loading_without_schema_coercion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            expected = self._generated_manifest(out_dir)
            manifest_path = out_dir / "analysis_manifest.json"
            expected_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            loaded, digest = load_analysis_manifest(manifest_path)
        self.assertEqual(loaded, expected)
        self.assertEqual(loaded["schema_version"], "joulewise.analysis_manifest.v1")
        self.assertEqual(digest, expected_digest)

    @staticmethod
    def _set_ratio(manifest: dict, form: object) -> dict:
        metrics = [contrast["metric"] for contrast in manifest["contrasts"][6:12]]
        for metric in metrics:
            metric["unit"] = "J/token"
            metric["ratio_estimand"] = ratio_estimand(form)
        reidentify(manifest)
        return metrics[0]

    def test_installed_layout_default_root_refuses_with_actionable_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "out"
            manifest = self._generated_manifest(out_dir)
            installed_root = tmp_path / "site-packages"
            installed_root.mkdir()

            with mock.patch.object(analysis_manifest_module, "ROOT", installed_root):
                errors = validate_analysis_manifest(manifest, manifest_dir=out_dir)
                with self.assertRaises(AnalysisManifestError) as raised:
                    build_slice_2m_analysis_manifest(out_dir)

            message = str(raised.exception)
            self.assertEqual(errors, [message])
            self.assertIn("configs/analysis_registry/slice_2m_ap2.v1.json", message)
            self.assertIn("docs/contracts/analysis_plans.md", message)
            self.assertIn("repository_root=Path(...)", message)

    def test_explicit_root_works_when_package_default_is_not_a_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "out"
            manifest = self._generated_manifest(out_dir)
            installed_root = tmp_path / "site-packages"
            installed_root.mkdir()

            with mock.patch.object(analysis_manifest_module, "ROOT", installed_root):
                rebuilt = build_slice_2m_analysis_manifest(
                    out_dir,
                    repository_root=ROOT,
                )
                errors = validate_analysis_manifest(
                    manifest,
                    manifest_dir=out_dir,
                    repository_root=ROOT,
                )

            self.assertEqual(rebuilt, manifest)
            self.assertEqual(errors, [])

    def test_checkout_default_root_works_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            generated = self._generated_manifest(out_dir)

            default_build = build_slice_2m_analysis_manifest(out_dir)
            explicit_build = build_slice_2m_analysis_manifest(
                out_dir,
                repository_root=ROOT,
            )

            self.assertEqual(default_build, generated)
            self.assertEqual(default_build, explicit_build)
            self.assertEqual(
                validate_analysis_manifest(default_build, manifest_dir=out_dir),
                [],
            )

    def test_one_and_two_model_shape_and_entry_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            first = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(first.returncode, 0, first.stderr)
            one = load_manifest(out_dir)

            self.assertEqual(one["schema_version"], "joulewise.analysis_manifest.v1")
            self.assertEqual(one["freeze_status"], "frozen")
            self.assertEqual(
                (len(one["entries"]), len(one["sentinel_links"]), len(one["families"]), len(one["contrasts"])),
                (30, 5, 4, 24),
            )
            for entry in one["entries"]:
                self.assertIsInstance(entry["cell_id"], str)
                self.assertIsInstance(entry["block_id"], str)
                self.assertIsInstance(entry["condition_id"], str)

            second = run_generator(*BASE_CONFIGS[1], out_dir)
            self.assertEqual(second.returncode, 0, second.stderr)
            two = load_manifest(out_dir)
            self.assertEqual(
                (len(two["entries"]), len(two["sentinel_links"]), len(two["families"]), len(two["contrasts"])),
                (60, 10, 8, 48),
            )
            self.assertEqual(validate_analysis_manifest(two, manifest_dir=out_dir), [])

    def test_exact_one_model_contrast_enumeration_matches_hand_built_cross_product(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            tag = BASE_CONFIGS[0][1]
            expected = [
                f"ctr-ap2-{tag}-{metric_tag}-{condition_b}-minus-{condition_a}"
                for metric_tag in METRIC_TAGS
                for condition_a, condition_b in PAIRS
            ]

            manifest = load_manifest(out_dir)

            self.assertEqual([row["contrast_id"] for row in manifest["contrasts"]], expected)
            self.assertEqual(
                [contrast_id for family in manifest["families"] for contrast_id in family["contrast_ids"]],
                expected,
            )

    def test_sentinel_and_family_linkage_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            entries = {entry["entry_id"]: entry for entry in manifest["entries"]}

            for link in manifest["sentinel_links"]:
                start = entries[link["start_entry_id"]]
                end = entries[link["end_entry_id"]]
                linked = [entries[entry_id] for entry_id in link["linked_condition_entry_ids"]]
                self.assertEqual(start["role"], "drift_sentinel_start")
                self.assertEqual(end["role"], "drift_sentinel_end")
                self.assertEqual(start["block_id"], link["block_id"])
                self.assertEqual(end["block_id"], link["block_id"])
                self.assertEqual(
                    [entry["condition_id"] for entry in linked],
                    ["cond-2m-short_short", "cond-2m-long_short", "cond-2m-short_long", "cond-2m-mid_mid"],
                )
                self.assertTrue(all(entry["block_id"] == link["block_id"] for entry in linked))
            for family in manifest["families"]:
                self.assertEqual(family["multiplicity"]["m"], len(family["contrast_ids"]))
                self.assertEqual(family["multiplicity"]["m"], 6)

    def test_analysis_manifest_bytes_are_identical_across_double_run_and_reverse_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            forward = tmp_path / "forward"
            reverse = tmp_path / "reverse"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, forward)
                self.assertEqual(result.returncode, 0, result.stderr)
            first_bytes = (forward / "analysis_manifest.json").read_bytes()
            rerun = run_generator(*BASE_CONFIGS[1], forward)
            self.assertEqual(rerun.returncode, 0, rerun.stderr)
            self.assertEqual((forward / "analysis_manifest.json").read_bytes(), first_bytes)
            for base, tag in reversed(BASE_CONFIGS):
                result = run_generator(base, tag, reverse)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((reverse / "analysis_manifest.json").read_bytes(), first_bytes)

    def test_semantic_block_ids_do_not_follow_mutable_numeric_block_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            first = run_generator(*BASE_CONFIGS[1], out_dir)
            self.assertEqual(first.returncode, 0, first.stderr)
            one = load_manifest(out_dir)
            tag = BASE_CONFIGS[1][1]
            before = {
                entry["run_id"]: entry["block_id"]
                for entry in one["entries"]
                if entry["model_tag"] == tag
            }
            second = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(second.returncode, 0, second.stderr)
            two = load_manifest(out_dir)
            after = {
                entry["run_id"]: entry["block_id"]
                for entry in two["entries"]
                if entry["model_tag"] == tag
            }
            self.assertEqual(after, before)

    def test_validation_rejects_dropped_cell_id_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            del mutated["entries"][0]["cell_id"]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("missing key(s): cell_id" in error for error in errors), errors)

    def test_validation_rejects_duplicated_contrast_id_across_families_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            mutated["families"][1]["contrast_ids"][0] = mutated["families"][0]["contrast_ids"][0]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("appears in more than one family" in error for error in errors), errors)

    def test_validation_rejects_cross_block_end_sentinel_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            mutated["sentinel_links"][0]["end_entry_id"] = mutated["sentinel_links"][1]["end_entry_id"]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("does not link this block's end sentinel" in error for error in errors), errors)

    def test_validation_rejects_removed_contrast_with_frozen_m(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            del mutated["families"][0]["contrast_ids"][0]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("does not equal contrast_ids length" in error for error in errors), errors)

    def test_real_validator_rejects_reidentified_fixed_n_reduction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            mutated["design"]["sampling_plan"]["planned_n_blocks"] = 1
            for contrast in mutated["contrasts"]:
                contrast["block_ids"] = contrast["block_ids"][:1]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("expected frozen n of 5 or 10" in error for error in errors), errors)

    def test_post_freeze_n_mutation_detected_by_validator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            manifest = self._generated_manifest(out_dir)
            manifest["design"]["sampling_plan"]["planned_n_blocks"] = 10
            reidentify(manifest)

            errors = validate_analysis_manifest(manifest, manifest_dir=out_dir)

            self.assertTrue(
                any("post-freeze n mutation differs from frozen registry" in error for error in errors),
                errors,
            )

    def test_mixed_n_composition_rejected_for_inconsistent_block_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, out_dir)
                self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            expanded_tag = BASE_CONFIGS[1][1]
            extra_entries = []
            for entry in manifest["entries"]:
                if entry["model_tag"] != expanded_tag:
                    continue
                copy_entry = copy.deepcopy(entry)
                old_rep = copy_entry["planned_rep_index"]
                new_rep = old_rep + 5
                copy_entry["planned_rep_index"] = new_rep
                old_tag = f"r{old_rep:02d}"
                new_tag = f"r{new_rep:02d}"
                for key in ("entry_id", "block_id", "sentinel_link_id"):
                    copy_entry[key] = copy_entry[key].replace(old_tag, new_tag)
                extra_entries.append(copy_entry)
            manifest["entries"].extend(extra_entries)
            reidentify(manifest)

            errors = validate_analysis_manifest(manifest)

            self.assertIn(
                "manifest.entries: mixed n=5/n=10 or inconsistent frozen block authority",
                errors,
            )

    def test_real_validator_rejects_duplicate_contrast_block_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            mutated["contrasts"][0]["block_ids"][1] = mutated["contrasts"][0][
                "block_ids"
            ][0]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(
                any("invalid semantic block linkage" in error for error in errors),
                errors,
            )

    def test_real_validator_rejects_same_cell_contrast_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            mutated["contrasts"][0]["cell_b_id"] = mutated["contrasts"][0][
                "cell_a_id"
            ]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(
                any("differs from frozen registry enumeration" in error for error in errors),
                errors,
            )

    def test_validation_rejects_non_frozen_status_and_ap_snapshot_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            mutations = (
                ("freeze", lambda value: value.__setitem__("freeze_status", "draft"), "must be 'frozen'"),
                (
                    "ap_hash",
                    lambda value: value["source"]["ap_rows"][0].__setitem__("section_sha256", "0" * 64),
                    "AP snapshot mismatch",
                ),
            )
            for name, mutate, expected in mutations:
                with self.subTest(name=name):
                    mutated = copy.deepcopy(manifest)
                    mutate(mutated)
                    reidentify(mutated)
                    errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)
                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_validation_accepts_each_adjudicated_ratio_estimand(self) -> None:
        for form in ("mean_of_request_ratios", "ratio_of_totals"):
            with self.subTest(form=form), tempfile.TemporaryDirectory() as tmp:
                out_dir = Path(tmp) / "out"
                manifest = self._generated_manifest(out_dir)
                self._set_ratio(manifest, form)

                self.assertEqual(
                    validate_analysis_manifest(manifest, manifest_dir=out_dir),
                    [],
                )

    def test_validation_accepts_adjudicated_named_strata_randomization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            manifest = self._generated_manifest(out_dir)
            block_ids = manifest["contrasts"][0]["block_ids"]
            manifest["design"]["randomization"] = named_strata(block_ids)
            reidentify(manifest)

            self.assertEqual(validate_analysis_manifest(manifest, manifest_dir=out_dir), [])

    def test_validation_rejects_unknown_ratio_and_randomization_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            original = self._generated_manifest(out_dir)
            mutations = (
                (
                    "ratio",
                    lambda value: self._set_ratio(value, "ratio_selected_after_observation"),
                    "ratio_estimand.form",
                ),
                (
                    "ratio_wrong_type",
                    lambda value: self._set_ratio(value, ["ratio_of_totals"]),
                    "ratio_estimand.form",
                ),
                (
                    "randomization",
                    lambda value: value["design"].__setitem__(
                        "randomization",
                        {"scheme": "global_label_shuffle", "exchangeability": "global"},
                    ),
                    "unsupported randomization design",
                ),
            )
            for name, mutate, expected in mutations:
                with self.subTest(name=name):
                    manifest = copy.deepcopy(original)
                    mutate(manifest)
                    reidentify(manifest)

                    errors = validate_analysis_manifest(manifest, manifest_dir=out_dir)

                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_named_strata_ratio_manifest_flows_from_validator_to_engine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            manifest = self._generated_manifest(out_dir)
            block_ids = manifest["contrasts"][0]["block_ids"]
            manifest["design"]["randomization"] = named_strata(block_ids)
            metric = self._set_ratio(manifest, "ratio_of_totals")

            self.assertEqual(validate_analysis_manifest(manifest, manifest_dir=out_dir), [])
            sensitivity = randomization_check(
                [1.0] * len(block_ids),
                manifest["design"]["randomization"],
                block_ids=block_ids,
            )
            observations = tuple(
                RatioObservation(
                    block_id=block_id,
                    energy_a_j=10.0,
                    energy_b_j=20.0,
                    output_tokens_a=100,
                    output_tokens_b=100,
                    token_count_source_a="runtime_observed",
                    token_count_source_b="runtime_observed",
                    stop_reason_a="requested_tokens_emitted",
                    stop_reason_b="requested_tokens_emitted",
                    output_policy_a="fixed-100",
                    output_policy_b="fixed-100",
                    tokenizer_identity_a="tok-a",
                    tokenizer_identity_b="tok-a",
                )
                for block_id in block_ids
            )
            estimate = estimate_manifest_observations(metric, observations)

            self.assertEqual(sensitivity["status"], "not_run")
            self.assertEqual(estimate.ratio_estimand, "ratio_of_totals")

    def test_validation_rejects_tampered_config_and_order_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            config_path = out_dir / manifest["entries"][0]["config"]
            config_path.write_bytes(config_path.read_bytes() + b" ")
            errors = validate_analysis_manifest(manifest, manifest_dir=out_dir)
            self.assertTrue(any("does not match config bytes" in error for error in errors), errors)

            config_path.write_bytes(config_path.read_bytes()[:-1])
            order_path = out_dir / "order_manifest.json"
            order_path.write_bytes(order_path.read_bytes() + b" ")
            errors = validate_analysis_manifest(manifest, manifest_dir=out_dir)
            self.assertTrue(any("order_manifest.sha256: source hash mismatch" in error for error in errors), errors)

    def test_validation_fails_closed_on_wrong_typed_identity_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            mutations = (
                ("entry", lambda value: value["entries"][0].__setitem__("run_id", []), "entries[0].run_id"),
                (
                    "sentinel_link",
                    lambda value: value["sentinel_links"][0].__setitem__("sentinel_link_id", []),
                    "sentinel_links[0].sentinel_link_id",
                ),
                (
                    "family",
                    lambda value: value["families"][0].__setitem__("family_instance_id", []),
                    "families[0].family_instance_id",
                ),
                (
                    "contrast",
                    lambda value: value["contrasts"][0].__setitem__("contrast_id", []),
                    "contrasts[0].contrast_id",
                ),
            )
            for name, mutate, expected in mutations:
                with self.subTest(layer=name):
                    mutated = copy.deepcopy(manifest)
                    mutate(mutated)
                    reidentify(mutated)

                    errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

                    self.assertTrue(any(expected in error and "must be a string" in error for error in errors), errors)

    def test_validation_rejects_coherent_semantic_run_id_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            entry = manifest["entries"][1]
            wrong_run_id = entry["run_id"] + "-renamed"
            entry["run_id"] = wrong_run_id

            config_path = out_dir / entry["config"]
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["run_id"] = wrong_run_id
            config_path.write_text(
                json.dumps(config, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            entry["config_sha256"] = sha256_bytes(config_path.read_bytes())

            order_path = out_dir / "order_manifest.json"
            order = json.loads(order_path.read_text(encoding="utf-8"))
            order["executed_order"][1]["run_id"] = wrong_run_id
            order_path.write_text(
                json.dumps(order, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            manifest["source"]["order_manifest"]["sha256"] = sha256_bytes(order_path.read_bytes())
            reidentify(manifest)

            errors = validate_analysis_manifest(manifest, manifest_dir=out_dir)

            self.assertTrue(any("entries[1].run_id: expected semantic run_id" in error for error in errors), errors)
            self.assertFalse(any("source hash mismatch" in error for error in errors), errors)
            self.assertFalse(any("disagrees with config" in error for error in errors), errors)
            self.assertFalse(any("disagrees with order manifest" in error for error in errors), errors)

    def test_ap_section_hash_preserves_crlf_bytes(self) -> None:
        section = (
            b"### AP-2: fixture\r\n"
            b"\r\n"
            b"| Field | Value |\r\n"
            b"|---|---|\r\n"
            b"| Plan ID / RQ consumer | AP-2 / fixture |\r\n"
            b"| family_id | FAM-2M-SHAPE-CONTRASTS |\r\n"
            b"| claim_role | primary |\r\n"
            b"| selection_scope | fixture |\r\n"
            b"| multiplicity_rule | Holm |\r\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "analysis_plans.md"
            path.write_bytes(section + b"\r\n### AP-3: next\r\n")

            row = extract_analysis_plan_row(path)

            self.assertEqual(row.raw_section, section)
            self.assertEqual(sha256_bytes(row.raw_section), hashlib.sha256(section).hexdigest())


if __name__ == "__main__":
    unittest.main()
