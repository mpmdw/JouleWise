"""Counterfactual and parity checks for the shared campaign-generator core."""

from __future__ import annotations

from contextlib import nullcontext
import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import campaign_generator_core as core
from scripts.check_campaign_generator_core_parity import (
    GENERATOR_CASES,
    configure_generator,
    generate,
    load_source,
)


ROOT = Path(__file__).resolve().parents[1]
# Generation-time bytes from a816036f4ea278fcc746b1220896b4b6bd084855:
# git show a816036f:configs/calibration/calibration_ledger_head.json
GENERATION_LEDGER_HEAD_BYTES = (
    b'{\n'
    b'  "sequence": 76,\n'
    b'  "head_digest": "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",\n'
    b'  "ledger_schema": "joulewise.calibration_observation_ledger.v1"\n'
    b'}\n'
)
GENERATION_LEDGER_HEAD_SHA256 = (
    "6bbe26258165bbd11ca996324a5862c2e6e34faae7999b6c06f5e12f27ac2902"
)
D117_GENERATORS = tuple(
    sorted((ROOT / "configs/campaigns").glob("d117_*/generate_configs.py"))
)
LIVE_V5_GENERATORS = tuple(
    ROOT / "configs/campaigns" / pack_id / "generate_configs.py"
    for pack_id in (
        "d117_contrast_v5",
        "d117_floor_qwen3-1p7b_v5",
        "d117_floor_qwen3-8b_v5",
    )
)
HISTORICAL_GENERATORS = tuple(
    ROOT / "configs/campaigns" / pack_id / "generate_configs.py"
    for pack_id in (
        "d117_contrast_qwen25_1p5b_vs_7b_v1",
        "d117_contrast_qwen25_1p5b_vs_7b_v2",
        "d117_contrast_qwen25_1p5b_vs_7b_v3",
        "d117_floor_qwen25_1p5b_v1",
        "d117_floor_qwen25_1p5b_v2",
        "d117_floor_qwen25_1p5b_v3",
        "d117_floor_qwen25_7b_v1",
        "d117_floor_qwen25_7b_v2",
        "d117_floor_qwen25_7b_v3",
    )
)
DIRECT_SHARED_FUNCTIONS = (
    "actual_pack_paths",
    "make_render_json",
    "sha256_bytes",
    "sidecar_bytes",
    "validate_generation_write_boundary",
)


def load_generator(path: Path):
    module_name = f"test_generator_core_{path.parent.name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module


class CampaignGeneratorCoreTests(unittest.TestCase):
    maxDiff = None

    def assert_generation_uses_shared_write_boundary(
        self,
        cases=GENERATOR_CASES,
        *,
        source_overrides: dict[Path, bytes] | None = None,
    ) -> None:
        from tests.test_d117_floor_qwen3_v5_generate import fixture_prefill_pin

        overrides = source_overrides or {}
        with tempfile.TemporaryDirectory(prefix="generator-core-calls-") as temp:
            temporary = Path(temp)
            fixture_root = temporary / "fixture"
            fixture_root.mkdir()
            pin = fixture_prefill_pin(fixture_root)
            for label, generator_rel, _ in cases:
                generator_path = ROOT / generator_rel
                source = overrides.get(generator_rel)
                generator = (
                    load_source(
                        f"generator_core_mutation_{label.lower()}",
                        source,
                        generator_path,
                    )
                    if source is not None
                    else load_generator(generator_path)
                )
                if source is not None:
                    generator.embedded_generator_bytes = (
                        lambda source=source: source
                    )
                configure_generator(label, generator, pin)
                head_fixture = nullcontext()
                # GENERATOR-HEAD-FILE-BYTE-PIN-01 is registered for the cold
                # gate: the production byte pin on an append-advancing file
                # remains unchanged. Exercise the generator as a function of
                # its declared inputs, for normal and mutated source alike.
                if label in ("ALPHA", "BETA"):
                    fixture_digest = hashlib.sha256(
                        GENERATION_LEDGER_HEAD_BYTES
                    ).hexdigest()
                    self.assertEqual(fixture_digest, GENERATION_LEDGER_HEAD_SHA256)
                    real_sha256_file = generator.sha256_file
                    head_path = generator.REPO_ROOT / generator.LEDGER_HEAD_REL

                    def fixture_sha256_file(
                        path, *, head_path=head_path,
                        real_sha256_file=real_sha256_file,
                        fixture_digest=fixture_digest,
                    ):
                        if path == head_path:
                            return fixture_digest
                        return real_sha256_file(path)

                    head_fixture = mock.patch.object(
                        generator, "sha256_file", side_effect=fixture_sha256_file
                    )
                output_root = temporary / label.lower()
                calls: list[tuple[Path, tuple[Path, ...]]] = []
                with head_fixture, mock.patch.object(
                    core,
                    "_generation_write_boundary_observer",
                    side_effect=lambda root, outputs: calls.append(
                        (root, outputs)
                    ),
                ):
                    generate(generator, label, output_root)

                final_calls = [
                    outputs
                    for observed_root, outputs in calls
                    if observed_root == output_root.absolute()
                ]
                self.assertEqual(
                    len(final_calls),
                    1,
                    f"{label} did not invoke the shared write boundary for its "
                    "final output root exactly once",
                )
                emitted = {
                    path.relative_to(output_root)
                    for path in output_root.rglob("*")
                    if path.is_file()
                }
                for _, observed_outputs in calls:
                    self.assertEqual(len(observed_outputs), len(emitted))
                    self.assertEqual(set(observed_outputs), emitted)

    def test_d117_generator_census_requires_explicit_live_or_historical_custody(
        self,
    ) -> None:
        self.assertEqual(
            set(D117_GENERATORS),
            set(LIVE_V5_GENERATORS) | set(HISTORICAL_GENERATORS),
        )

    def test_counterfactual_local_write_boundary_cannot_bypass_shared_core(
        self,
    ) -> None:
        """Every live production path reports its complete emitted inventory."""

        self.assert_generation_uses_shared_write_boundary()

    def test_exact_alpha_local_validator_evasion_is_detected(self) -> None:
        """The refuter's same-signature local ALPHA redirect fails the contract."""

        alpha = GENERATOR_CASES[0]
        label, generator_rel, _ = alpha
        self.assertEqual(label, "ALPHA")
        source = (ROOT / generator_rel).read_text(encoding="utf-8")
        insertion_point = (
            "render_json = make_render_json(thread_generation_identity)\n"
        )
        production_call = (
            "    validate_generation_write_boundary(output_root, outputs)\n"
        )
        local_call = (
            "    _local_validate_generation_write_boundary(output_root, outputs)\n"
        )
        self.assertEqual(source.count(insertion_point), 1)
        self.assertEqual(source.count(production_call), 1)
        mutated = source.replace(
            insertion_point,
            insertion_point
            + "\n\ndef _local_validate_generation_write_boundary(\n"
            + "    output_root: Path, outputs: Iterable[Path]\n"
            + ") -> None:\n"
            + "    return None\n",
            1,
        ).replace(production_call, local_call, 1)
        with tempfile.TemporaryDirectory(prefix="generator-core-mutation-") as temp:
            mutation = Path(temp) / "generate_configs.py"
            mutation.write_text(mutated, encoding="utf-8")
            with self.assertRaisesRegex(
                AssertionError,
                "ALPHA did not invoke the shared write boundary for its final "
                "output root exactly once",
            ):
                self.assert_generation_uses_shared_write_boundary(
                    (alpha,),
                    source_overrides={generator_rel: mutation.read_bytes()},
                )

    def test_live_generators_import_shared_mechanics(self) -> None:
        """The behavioral boundary proof complements helper object identity."""

        for path in LIVE_V5_GENERATORS:
            with self.subTest(generator=path.parent.name):
                generator = load_generator(path)
                for name in DIRECT_SHARED_FUNCTIONS:
                    self.assertIs(getattr(generator, name), getattr(core, name))
                self.assertIs(
                    generator.render_json.shared_implementation,
                    core.render_json,
                )

    def test_frozen_generators_remain_self_contained_custody_snapshots(self) -> None:
        """The extraction must not rewrite hash-pinned historical evidence."""

        self.assertEqual(len(HISTORICAL_GENERATORS), 9)
        for path in HISTORICAL_GENERATORS:
            with self.subTest(generator=path.parent.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("joulewise.campaign_generator_core", source)
                self.assertIn("def validate_generation_write_boundary", source)

    def test_shared_boundary_refuses_a_symlinked_ancestor_before_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generator-core-boundary-") as temp:
            root = Path(temp)
            outside = root / "outside"
            outside.mkdir()
            (root / "pack").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "write ancestor is a symlink"):
                core.validate_generation_write_boundary(
                    root, (Path("pack/calibration_plan.json"),)
                )
            self.assertEqual(list(outside.iterdir()), [])

    def test_shared_boundary_accepts_an_absent_closed_tree_without_writing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generator-core-boundary-") as temp:
            root = Path(temp)
            relative = Path("pack/calibration_plan.json")
            core.validate_generation_write_boundary(root, (relative,))
            self.assertFalse((root / relative).exists())


if __name__ == "__main__":
    unittest.main()
