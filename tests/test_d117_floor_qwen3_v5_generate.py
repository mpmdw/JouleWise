"""Generation and consumer-linkage coverage for the D-117 Qwen3 v5 floors."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise import arm_readiness
from joulewise.provenance import prompt_token_ids_sha256


ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
WORKLOAD = ROOT / "configs/workloads/real_prompts_v1.json"
FLOORS = (
    (
        "ALPHA",
        "d117_floor_qwen3-1p7b_v5",
        "qwen3-1p7b",
        "Qwen3-1.7B-4bit",
        "plan-d117-floor-qwen3-1p7b-decode-prefill-p512-v5",
    ),
    (
        "BETA",
        "d117_floor_qwen3-8b_v5",
        "qwen3-8b",
        "Qwen3-8B-4bit",
        "plan-d117-floor-qwen3-8b-decode-prefill-p512-v5",
    ),
)
TOKENIZER_SHA256 = "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
CHAT_TEMPLATE_SHA256 = "87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5"
MODEL_PANEL_ROWS = {
    row["model_id"]: row
    for row in json.loads(PANEL.read_text(encoding="utf-8"))["entries"]
}


def load_generator(pack_id: str):
    path = ROOT / "configs/campaigns" / pack_id / "generate_configs.py"
    spec = importlib.util.spec_from_file_location(f"{pack_id}_generator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture_prefill_pin(root: Path) -> Path:
    contrast = load_generator("d117_contrast_v5")
    bundle = root / "authority"
    bundle.mkdir()
    selection_path = bundle / "selection-record.json"
    selection_path.write_text('{"fixture":"selection"}\n', encoding="utf-8")
    selection_sha = hashlib.sha256(selection_path.read_bytes()).hexdigest()

    def rung(token_count: int) -> dict[str, object]:
        closing = f"Fixture closing sentence for {token_count}."
        text = " ".join([contrast.PROMPT_SENTENCE, closing])
        token_ids = [token_count] * token_count
        return {
            "prefill_tokens": token_count,
            "repeat_count": 1,
            "closing_sentence": closing,
            "prompt_text": text,
            "prompt_text_utf8_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "prompt_token_ids": token_ids,
            "prompt_token_ids_sha256": prompt_token_ids_sha256(token_ids),
            "generation_method": (
                f"1 x '{contrast.PROMPT_SENTENCE}' + '{closing}' under tokenizer "
                f"sha256:{TOKENIZER_SHA256}"
            ),
        }

    target = rung(512)
    companion = rung(1024)
    ladder_path = bundle / "prompt-ladder.json"
    ladder_path.write_text(
        json.dumps(
            {
                "schema_version": "joulewise.g2a_prefill_prompt_ladder.v1",
                "prompt_sentence": contrast.PROMPT_SENTENCE,
                "tokenizer_json_sha256": TOKENIZER_SHA256,
                "panel_thinking_policy": {
                    "enable_thinking": "false",
                    "panel_sha256": hashlib.sha256(PANEL.read_bytes()).hexdigest(),
                },
                "rungs": [target, companion],
            }
        ),
        encoding="utf-8",
    )
    value = {
        "schema_version": "joulewise.prefill_prompt_pin.v2",
        "selection_authority": {
            "g2a_record": {
                "record_id": f"sha256:{selection_sha}",
                "path": selection_path.relative_to(root).as_posix(),
            },
            "ruling_trace_paths": list(contrast.PREFILL_RULING_TRACE_PATHS),
        },
        "ladder_prompt_tokens": [512, 1024, 2048, 4096],
        "min_small_model_members_per_rung": 5,
        "min_overlapping_power_interval_count": 5,
        "min_phase_samples_pinned": 3,
        "sample_count_margin_floor": 2,
        "selection_expression": contrast.PREFILL_SELECTION_EXPRESSION,
        "g2a_record_sha256": selection_sha,
        "selection_record": {
            "path": selection_path.relative_to(root).as_posix(),
            "sha256": selection_sha,
        },
        "prompt_ladder": {
            "path": ladder_path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(ladder_path.read_bytes()).hexdigest(),
        },
        "panel_sha256": hashlib.sha256(PANEL.read_bytes()).hexdigest(),
        "exhausted_ladder_branch": contrast.PREFILL_EXHAUSTED_LADDER_BRANCH,
        "prefill_length": 512,
        "tokenizer_json_sha256": TOKENIZER_SHA256,
        "special_token_policy": "add_special_tokens=true",
        "prompt_text": target["prompt_text"],
        "prompt_text_utf8_sha256": target["prompt_text_utf8_sha256"],
        "prompt_token_ids": target["prompt_token_ids"],
        "prompt_token_ids_sha256": target["prompt_token_ids_sha256"],
        "prompt_tokens": 512,
        "repeat_count": target["repeat_count"],
        "closing_sentence": target["closing_sentence"],
        "generation_method": target["generation_method"],
    }
    path = root / "prefill-pin.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def file_snapshot(pack: Path) -> dict[str, bytes]:
    return {
        path.relative_to(pack).as_posix(): path.read_bytes()
        for path in sorted(pack.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def family_marker(members: list[dict[str, object]]) -> dict[str, object]:
    """Build a schema-valid synthetic marker around generated roster identities.

    This exercises the production family-roster parser.  It deliberately does
    not pretend the generated draft packs have freeze-0004 receipts; those
    receipt fields are schema fixtures, while every roster and plan identity is
    read from the freshly generated pack trees.
    """

    sha = "0" * 64
    oid = "a" * 40
    tree_oid = "b" * 40
    return {
        "schema_version": arm_readiness.FAMILY_PUBLICATION_MARKER_SCHEMA,
        "marker_kind": "FAMILY_PUBLICATION",
        "family_id": "d117-v5",
        "family_generation": 5,
        "publication_state": "PUBLISHED",
        "publication_git": {
            "head_commit": oid,
            "head_tree_oid": tree_oid,
            "local_main_commit": oid,
            "origin_main_commit": oid,
            "clean": True,
            "exact_match": True,
        },
        "common_evidence_git": {"head_commit": oid, "head_tree_oid": tree_oid},
        "lifecycle_registry": {
            "path": arm_readiness.ROW_REGISTRY_RELATIVE_PATH.as_posix(),
            "schema_version": arm_readiness.R1_ROW_REGISTRY_SCHEMA,
            "registry_id": "d117-row-registry-v2",
            "sha256": sha,
            "lifecycle_registry_id": "d117-r1-lifecycle-v1",
            "family_publication_marker_schema": (
                arm_readiness.FAMILY_PUBLICATION_MARKER_SCHEMA
            ),
            "family_publication_refusal": {
                "role": "FAMILY_PUBLICATION",
                "code": "readiness_r1_family_publication",
                "type": "CUSTODY",
            },
        },
        "members": members,
        "terminal_review": {
            "evidence_kind": "TERMINAL_REVIEW",
            "head_tree_oid": tree_oid,
        },
        "publication_authority": {
            "confirmation_schema": arm_readiness.STEP6_CONFIRMATION_TABLE_SCHEMA,
            "required_decision": "YES",
        },
        "conditional_paths_deferred": {
            "gate": arm_readiness.R1_DIGEST_CONDITIONAL_GATE_ID,
            "deferred_paths": sorted(
                arm_readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS
            ),
            "enforced_at_entry_points": list(
                arm_readiness.R1_DIGEST_CONDITIONAL_ENTRY_POINTS
            ),
        },
        "authoring_context": {
            "transaction_id": f"d117-v5@{oid}",
            "source_commit_time_utc": "2026-09-02T00:00:00Z",
            "construction_phase": "POST_FREEZE_FAMILY_BOUNDARY",
            "custody_class": "TRANSACTION_EXTERNAL",
            "builder": {"path": "scripts/build_family_marker.py", "sha256": sha},
            "consumer": {"path": "scripts/verify_family_marker.py", "sha256": sha},
        },
        "assurance": arm_readiness.ASSURANCE,
    }


class D117FloorQwen3V5PackTests(unittest.TestCase):
    maxDiff = None

    def test_prefill_pin_requires_g2_record_hash_binding(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-floor-g2-binding-") as temporary:
            pin = fixture_prefill_pin(Path(temporary))
            value = json.loads(pin.read_text())
            value["g2a_record_sha256"] = "0" * 64
            value["selection_authority"]["g2a_record"]["record_id"] = (
                f"sha256:{value['g2a_record_sha256']}"
            )
            pin.write_text(json.dumps(value), encoding="utf-8")
            for _profile, pack_id, _model_id, _model_name, _plan_id in FLOORS:
                with self.subTest(pack_id=pack_id):
                    with self.assertRaisesRegex(
                        ValueError, "selection_record_sha256_mismatch"
                    ):
                        load_generator(pack_id).configure_prefill_pin(pin)

    def test_generators_do_not_synthesize_a_missing_g2a_prompt_pin(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-floor-no-pin-") as temporary:
            for _profile, pack_id, _model_id, _model_name, _plan_id in FLOORS:
                with self.subTest(pack_id=pack_id):
                    attempted = subprocess.run(
                        [
                            sys.executable,
                            str(
                                ROOT
                                / "configs/campaigns"
                                / pack_id
                                / "generate_configs.py"
                            ),
                            "--output-root",
                            temporary,
                        ],
                        cwd=ROOT,
                        env={"PYTHONDONTWRITEBYTECODE": "1"},
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertNotEqual(attempted.returncode, 0)
                    self.assertIn("prefill_prompt_pin_unresolved", attempted.stderr)

    def test_generators_are_deterministic_closed_and_checkable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-floor-v5-") as temporary:
            root = Path(temporary)
            pin = fixture_prefill_pin(root)
            for profile, pack_id, _model_id, model_name, plan_id in FLOORS:
                with self.subTest(pack_id=pack_id):
                    module = load_generator(pack_id)
                    module.configure_prefill_pin(pin)
                    first = root / f"{pack_id}-first"
                    second = root / f"{pack_id}-second"
                    count1, plan_sha1, tree_sha1 = module.generate(first)
                    count2, plan_sha2, tree_sha2 = module.generate(second)
                    self.assertEqual((count1, count2), (100, 100))
                    self.assertEqual((plan_sha1, tree_sha1), (plan_sha2, tree_sha2))
                    first_pack = first / "configs/campaigns" / pack_id
                    second_pack = second / "configs/campaigns" / pack_id
                    self.assertEqual(file_snapshot(first_pack), file_snapshot(second_pack))
                    self.assertEqual(
                        module.actual_pack_paths(first_pack),
                        set(module.expected_pack_paths()),
                    )
                    self.assertEqual(
                        module.validate_generation_output_inventory(
                            module.GenerationIdentity()
                        ),
                        {
                            Path("configs/campaigns") / pack_id / path
                            for path in module.expected_pack_paths()
                        },
                    )
                    checked = subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "configs/campaigns" / pack_id / "generate_configs.py"),
                            "--check",
                            "--output-root",
                            str(first),
                        ],
                        cwd=ROOT,
                        env={"PYTHONDONTWRITEBYTECODE": "1"},
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(checked.returncode, 0, checked.stderr)
                    self.assertIn("verified", checked.stdout)

                    plan = json.loads((first_pack / "calibration_plan.json").read_text())
                    self.assertEqual(plan["plan_id"], plan_id)
                    self.assertEqual(plan["fixed_n"], 10)
                    comparative = [
                        cell for cell in plan["floor_cells"]
                        if cell["kind"] == "comparative_abba"
                    ]
                    self.assertEqual(len(comparative), 3)
                    for cell in comparative:
                        criterion = cell["floor_estimator_registration"][
                            "dominance_criterion"
                        ]
                        self.assertEqual(criterion["threshold"], 2.0)
                        self.assertEqual(criterion["comparison"], "greater_than_or_equal")
                        self.assertTrue(criterion["all_must_pass"])
                        self.assertEqual(
                            criterion["component_dispositions"]["absolute_common_mode"][
                                "status"
                            ],
                            "not_applicable",
                        )
                        self.assertEqual(
                            criterion["component_dispositions"][
                                "comparative_common_mode"
                            ],
                            {
                                "status": "mandatory",
                                "withdrawal_comparison": "R_cm < 2.0",
                                "withdrawal_consequence": (
                                    "withdraw_dominance_sentence"
                                ),
                            },
                        )

                    configs = sorted(
                        path for path in first_pack.glob("[0-9][0-9]_*/d117*.json")
                    )
                    self.assertEqual(len(configs), 100)
                    decode_configs = configs[:50]
                    prefill_configs = configs[50:]
                    decode_manifest = json.loads(
                        (first_pack / "decode_prompt_manifest.json").read_text()
                    )
                    self.assertEqual(len(decode_manifest["items"]), 1)
                    self.assertEqual(
                        decode_manifest["source_manifest"]["subset_id"], "sky_color"
                    )
                    self.assertEqual(
                        decode_manifest["items"][0]["output_policy"],
                        "fixed_budget_exact",
                    )
                    decode_workloads = [
                        json.loads(path.read_text())["workload_profile"]
                        for path in decode_configs
                    ]
                    self.assertEqual(
                        {row["suite_manifest_ref"] for row in decode_workloads},
                        {f"configs/campaigns/{pack_id}/decode_prompt_manifest.json"},
                    )
                    self.assertEqual(
                        len({row["suite_manifest_sha256"] for row in decode_workloads}),
                        1,
                    )
                    prefill_workloads = [
                        json.loads(path.read_text())["workload_profile"]
                        for path in prefill_configs
                    ]
                    self.assertTrue(
                        all("suite_manifest_ref" not in row for row in prefill_workloads)
                    )
                    self.assertEqual(
                        {
                            row["prompt_token_expectation"]["token_count"]
                            for row in prefill_workloads
                        },
                        {512},
                    )
                    for path in configs:
                        config = json.loads(path.read_text())
                        self.assertEqual(config["model"]["name"], model_name)
                        self.assertEqual(
                            config["model"]["source"],
                            MODEL_PANEL_ROWS[_model_id]["source"],
                        )
                        self.assertEqual(
                            config["model"]["revision"],
                            MODEL_PANEL_ROWS[_model_id]["revision"],
                        )
                        self.assertEqual(
                            config["model"]["tokenizer_json_sha256"],
                            TOKENIZER_SHA256,
                        )
                        self.assertEqual(
                            config["model"]["chat_template_sha256"],
                            CHAT_TEMPLATE_SHA256,
                        )
                    tree = json.loads((first_pack / "plan_tree.json").read_text())
                    unit_prefix = profile.lower()
                    units = tree["arm_attachments"]["identity_pin_projection"][
                        "identity_units"
                    ]
                    self.assertEqual(
                        [unit["identity_unit_id"] for unit in units],
                        [unit_prefix, f"{unit_prefix}/prefill_p512"],
                    )
                    self.assertEqual(
                        [len(unit["config_inventory"]) for unit in units], [50, 50]
                    )
                    self.assertEqual(
                        units[0]["declared_identity"]["workload_profile"][
                            "suite_manifest_ref"
                        ],
                        f"configs/campaigns/{pack_id}/decode_prompt_manifest.json",
                    )
                    self.assertEqual(
                        units[1]["declared_identity"]["workload_profile"][
                            "prompt_token_expectation"
                        ]["token_count"],
                        512,
                    )
                    self.assertEqual(
                        tree["arm_attachments"]["arm_readiness"]["row_registry"][
                            "plan_profile"
                        ],
                        profile,
                    )
                    decode = json.loads(
                        (first_pack / "decode_workload_candidate.json").read_text()
                    )
                    self.assertEqual(
                        tree["decode_workload"]["sha256"],
                        hashlib.sha256(
                            (first_pack / "decode_workload_candidate.json").read_bytes()
                        ).hexdigest(),
                    )
                    self.assertEqual(
                        decode["rendering_policy"],
                        {
                            "messages": [
                                {"role": "user", "content": "<profile prompt text>"}
                            ],
                            "add_generation_prompt": True,
                            "chat_template_applied": True,
                            "enable_thinking": "false",
                            "output_policy": "greedy_forced_512_suppress_eos",
                        },
                    )
                    self.assertEqual(
                        decode["assignment"]["rule_id"],
                        "ruling-171a-floor-index-zero.v1",
                    )
                    rendered = decode["per_model"][0]
                    self.assertEqual(rendered["model_id"], _model_id)
                    self.assertEqual(
                        rendered["prompts"][0]["prompt_token_ids"][-4:],
                        [151667, 271, 151668, 271],
                    )

    def test_contrast_references_resolve_to_matching_floor_plan_digests(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-floor-link-") as temporary:
            output = Path(temporary)
            pin = fixture_prefill_pin(output)
            for _profile, pack_id, _model_id, _model_name, _plan_id in FLOORS:
                module = load_generator(pack_id)
                module.configure_prefill_pin(pin)
                module.generate(output)

            contrast = load_generator("d117_contrast_v5")
            contrast.configure_model_pair(
                PANEL,
                "qwen3-1p7b",
                "qwen3-8b",
                decode_workload_path=WORKLOAD,
                prefill_length=512,
                prefill_prompt_pin_path=pin,
            )
            contrast.generate(output, contrast.GenerationIdentity())
            gamma = (
                output
                / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
            )
            tree = json.loads((gamma / "plan_tree.json").read_text())
            units = tree["arm_attachments"]["identity_pin_projection"]["identity_units"]
            self.assertEqual(
                [unit["identity_unit_id"] for unit in units],
                ["A/decode", "A/prefill_p512", "B/decode", "B/prefill_p512"],
            )
            references = {
                unit["producer_plan_reference"]["path"]:
                unit["producer_plan_reference"]["plan_id"]
                for unit in units
            }
            self.assertEqual(len(references), 2)
            for reference, expected_plan_id in references.items():
                plan_path = gamma / reference
                self.assertTrue(plan_path.is_file(), reference)
                raw = plan_path.read_bytes()
                digest = hashlib.sha256(raw).hexdigest()
                plan = json.loads(raw)
                self.assertEqual(plan["plan_id"], expected_plan_id)
                sidecar = plan_path.with_suffix(".sha256").read_text()
                self.assertEqual(sidecar, f"{digest}  calibration_plan.json\n")
                floor_tree = json.loads((plan_path.parent / "plan_tree.json").read_text())
                self.assertEqual(floor_tree["plan"]["actual_sha256"], digest)

    def test_arm_registry_and_pack_record_accept_the_v5_floor_roster(self) -> None:
        with tempfile.TemporaryDirectory(prefix="d117-floor-roster-") as temporary:
            output = Path(temporary)
            pin = fixture_prefill_pin(output)
            registry, _raw = arm_readiness.load_registry(ROOT)
            installed = registry["freeze_evidence_lifecycle"]["successor_policy"][
                "successor_pack_ids"
            ]
            self.assertEqual(
                installed,
                {
                    "ALPHA": "d117_floor_qwen3-1p7b_v5",
                    "BETA": "d117_floor_qwen3-8b_v5",
                    "GAMMA": "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
                },
            )
            pack_roots: list[tuple[str, Path]] = []
            for profile, pack_id, _model_id, _model_name, _plan_id in FLOORS:
                module = load_generator(pack_id)
                module.configure_prefill_pin(pin)
                module.generate(output)
                pack = output / "configs/campaigns" / pack_id
                pack_roots.append((profile, pack))
                self.assertEqual(arm_readiness._plan_profile(pack, registry), profile)
                tree_raw = (pack / "plan_tree.json").read_bytes()
                tree = json.loads(tree_raw)
                sidecar_raw = (pack / "plan_tree.sha256").read_bytes()
                record = {
                    "pack_id": pack_id,
                    "plan_id": tree["plan"]["plan_id"],
                    "window_id": tree["window_identity"]["window_id"],
                    "pack_root": str(pack.resolve()),
                    "pack_digest_algorithm": arm_readiness.PACK_DIGEST_ALGORITHM,
                    "pack_sha256": "a" * 64,
                    "plan_tree_path": "plan_tree.json",
                    "plan_tree_sha256": hashlib.sha256(tree_raw).hexdigest(),
                    "plan_tree_sidecar_path": "plan_tree.sha256",
                    "plan_tree_sidecar_sha256": hashlib.sha256(sidecar_raw).hexdigest(),
                }
                arm_readiness._validate_pack(record, f"{profile} pack")

            contrast = load_generator("d117_contrast_v5")
            contrast.configure_model_pair(
                PANEL,
                "qwen3-1p7b",
                "qwen3-8b",
                decode_workload_path=WORKLOAD,
                prefill_length=512,
                prefill_prompt_pin_path=pin,
            )
            contrast.generate(output, contrast.GenerationIdentity())
            gamma = (
                output
                / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
            )
            pack_roots.append(("GAMMA", gamma))
            self.assertEqual(arm_readiness._plan_profile(gamma, registry), "GAMMA")

            marker_members = []
            for profile, pack in pack_roots:
                tree_raw = (pack / "plan_tree.json").read_bytes()
                tree = json.loads(tree_raw)
                plan_path = pack / tree["plan"]["path"]
                marker_members.append(
                    {
                        "profile": profile,
                        "pack_id": pack.name,
                        "pack_path": f"configs/campaigns/{pack.name}",
                        "pack_digest_algorithm": arm_readiness.PACK_DIGEST_ALGORITHM,
                        "pack_sha256": "0" * 64,
                        "plan_tree": {
                            "path": "plan_tree.json",
                            "sha256": hashlib.sha256(tree_raw).hexdigest(),
                            "sidecar_path": "plan_tree.sha256",
                            "sidecar_sha256": hashlib.sha256(
                                (pack / "plan_tree.sha256").read_bytes()
                            ).hexdigest(),
                        },
                        "frozen_plan": {
                            "plan_id": tree["plan"]["plan_id"],
                            "window_id": tree["window_identity"]["window_id"],
                            "path": tree["plan"]["path"],
                            "sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
                        },
                        "freeze_receipt": {
                            "schema_version": arm_readiness.FREEZE_RECEIPT_V2_SCHEMA,
                            "receipt_id": "freeze-0004",
                            "ordinal": 4,
                            "path": (
                                "arm_readiness.freeze.receipts/freeze-0004.json"
                            ),
                            "sha256": "0" * 64,
                            "sidecar_path": (
                                "arm_readiness.freeze.receipts/"
                                "freeze-0004.json.sha256"
                            ),
                            "sidecar_sha256": "0" * 64,
                            "status": "PASS",
                        },
                    }
                )
            accepted = arm_readiness.validate_family_publication_marker(
                family_marker(marker_members),
                first_generation=arm_readiness._family_first_generation(registry),
            )
            self.assertEqual(
                [(row["profile"], row["pack_id"]) for row in accepted["members"]],
                [(profile, pack.name) for profile, pack in pack_roots],
            )


if __name__ == "__main__":
    unittest.main()
