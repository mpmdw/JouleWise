"""Block-5 identity pins: ``scripts/write_b5_identity_pins.py`` and the draft it writes.

The harvest recomputes each bundle's model and runtime identity with
``identity_pins.derive_model_runtime_config_from_metadata`` and compares it
with ``identity_pins.json``; the arm collector reads the same file. These
tests drive the real MLX adapter (with a fake ``mlx_lm``, no model) to build
bundle-shaped metadata and check that the generated pins are exactly what the
harvest would recompute, for both execution paths the ``_v5`` units use.
"""

from __future__ import annotations

import copy
import hashlib
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.clock import FakeClock
from joulewise.flags.collect import read_identity_pins, runtime_versions_sha256
from joulewise.identity_pins import (
    derive_model_runtime_config_from_metadata,
    identity_unit_config_set_sha256,
    scientific_config_identity_sha256,
    stack_identity_sha256,
)
from joulewise.schemas import BenchmarkConfig

ROOT = Path(__file__).resolve().parents[1]
PACKS = ("d117_floor_qwen3-1p7b_v5", "d117_floor_qwen3-8b_v5", "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5")
DRAFT = ROOT / "configs/campaigns/v5_claim_25g83/identity_pins.json"
ALPHA = ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5"
ALPHA_DECODE = "01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r01.json"
ALPHA_DECODE_2 = "01_phase_decode_absolute/d117fq31p7-df-ph-decode-abs-r02.json"
ALPHA_PREFILL = "04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r01.json"
ALPHA_PREFILL_2 = "04_phase_prefill_p2048_absolute/d117fq31p7-df-ph-prefill-p2048-abs-r02.json"
VERSIONS = {"python": "3.13.1", "packages": {"mlx": "0.31.2", "mlx-lm": "0.31.3", "mlx-metal": "0.31.2",
                                             "numpy": "2.5.1", "safetensors": "0.8.0", "tokenizers": "0.22.2",
                                             "transformers": "5.12.1"}}
PLATFORM = "macOS-26.6.2-arm64-arm-64bit-Mach-O"


def load_script() -> Any:
    spec = importlib.util.spec_from_file_location("write_b5_identity_pins_under_test",
                                                  ROOT / "scripts/write_b5_identity_pins.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W = load_script()


class FakeTokenizer:
    def __init__(self, name_or_path: str) -> None:
        self.eos_token_ids = {99}
        self.bos_token_id = 1
        self.name_or_path = name_or_path
        self.vocab_size = 151643

    def encode(self, text: str, *, add_special_tokens: bool = True) -> list[int]:
        tokens = [index + 10 for index, _ in enumerate(text.split())]
        return [1, *tokens] if add_special_tokens else tokens


class FakeMlxLm:
    __version__ = "0.31.3"

    def __init__(self, tokenizer: FakeTokenizer) -> None:
        self.tokenizer = tokenizer

    def make_sampler(self, **kwargs: Any) -> dict[str, Any]:
        return {"sampler": kwargs}

    def load(self, source: str, revision: str | None = None, return_config: bool = True):
        return object(), self.tokenizer, {"model_type": "qwen3"}

    def stream_generate(self, model: object, tokenizer: FakeTokenizer, prompt: Any, max_tokens: int = 256,
                        sampler: object | None = None):
        for index in range(max_tokens):
            yield SimpleNamespace(text="a", token=200 + index, finish_reason=None)


def runnable(config: dict[str, Any], model_dir: Path) -> dict[str, Any]:
    """The config the fake runtime can prepare: the local model dir, no tokenizer-file pins."""

    result = copy.deepcopy(config)
    result["model"]["source"] = str(model_dir)
    result["model"].pop("tokenizer_json_sha256", None)
    result["model"].pop("chat_template_sha256", None)
    return result


def run_member(config: dict[str, Any], repo: Path) -> tuple[Any, Any]:
    """Prepare and run one member through the real MLX adapter; return (prepare, runtime result)."""

    typed = BenchmarkConfig.from_mapping(config)
    adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
    fake = FakeMlxLm(FakeTokenizer(config["model"]["source"]))
    adapter._import_mlx_lm = lambda: fake  # type: ignore[method-assign]
    adapter._memory_snapshot = lambda label: {"label": label}  # type: ignore[method-assign]
    prepare = adapter.prepare(typed)
    assert prepare.ok, prepare.message
    manifest = W.load_suite_manifest(config, repo)
    if manifest is not None:
        return prepare, adapter.run_suite(typed, manifest, order_seed="seed")
    return prepare, adapter.run_workload(typed)


def bundle_metadata(config: dict[str, Any], repo: Path, *, platform: str = PLATFORM) -> dict[str, Any]:
    """Bundle metadata in the fields the stack identity reads, from a real adapter run."""

    prepare, result = run_member(config, repo)
    prepare_metadata = dict(prepare.metadata)
    prepare_metadata.update(mlx_version=VERSIONS["packages"]["mlx"], mlx_lm_version=VERSIONS["packages"]["mlx-lm"],
                            transformers_version=VERSIONS["packages"]["transformers"])
    return {
        "platform": platform, "machine": "arm64", "python_version": VERSIONS["python"],
        "device": {"device": config["hardware_target"]["id"], "boundary": "Apple SoC CPU + GPU + ANE package power",
                   "rail_manifest": ["cpu_power", "gpu_power", "ane_power"]},
        "quantization": asdict(BenchmarkConfig.from_mapping(config).quantization),
        "adapters": {"runtime": {"name": "mlx", "prepare_metadata": prepare_metadata},
                     "telemetry": {"name": "powermetrics"}},
        "workload_provenance": result.workload_provenance,
    }


def write_json(path: Path, value: Any) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return raw


class SyntheticPack:
    """A temporary checkout with one pack of two identity units built from ALPHA's committed configs."""

    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.pack = self.repo / "configs/campaigns/pk"
        self.model = root / "jw_models/Qwen3-1.7B-4bit"
        self.model.mkdir(parents=True)
        (self.model / "model.safetensors").write_bytes(b"synthetic weights")
        manifest_raw = (ALPHA / "decode_prompt_manifest.json").read_bytes()
        (self.pack).mkdir(parents=True)
        (self.pack / "decode_prompt_manifest.json").write_bytes(manifest_raw)
        self.configs: dict[str, dict[str, Any]] = {}
        for relative in (ALPHA_DECODE, ALPHA_DECODE_2, ALPHA_PREFILL, ALPHA_PREFILL_2):
            config = runnable(json.loads((ALPHA / relative).read_bytes()), self.model)
            if config["workload_profile"].get("suite_manifest_ref"):
                config["workload_profile"]["suite_manifest_ref"] = "configs/campaigns/pk/decode_prompt_manifest.json"
            self.configs[relative] = config
        self.references = root / "refs"
        self.reference_config = copy.deepcopy(self.configs[ALPHA_PREFILL])
        self.reference_config["run_id"] = "ref-prefill-r01"
        self.write()
        self.add_reference("ref-prefill-r01", self.reference_config)

    def unit(self, unit_id: str, paths: tuple[str, ...]) -> dict[str, Any]:
        return {"identity_unit_id": unit_id,
                "declared_identity": {"model_source": str(self.model),
                                      "model_revision": self.configs[paths[0]]["model"]["revision"]},
                "config_inventory": [{"path": path, "sha256": hashlib.sha256((self.pack / path).read_bytes()).hexdigest()}
                                     for path in paths],
                "model_runtime_config": {"model_artifact_sha256": None, "runtime_identity_sha256": None,
                                         "config_set_sha256": None}}

    def write(self, frozen_model: str | None = None) -> None:
        for relative, config in self.configs.items():
            write_json(self.pack / relative, config)
        units = [self.unit("pk/decode", (ALPHA_DECODE, ALPHA_DECODE_2)),
                 self.unit("pk/prefill_p2048", (ALPHA_PREFILL, ALPHA_PREFILL_2))]
        units[0]["model_runtime_config"]["model_artifact_sha256"] = frozen_model
        write_json(self.pack / "plan_tree.json", {"arm_attachments": {"identity_pin_projection": {
            "state": "unprojected", "identity_units": units}}})

    def add_reference(self, run_id: str, config: dict[str, Any], **overrides: Any) -> Path:
        bundle = self.references / run_id
        metadata = bundle_metadata(config, self.repo, **overrides)
        write_json(bundle / "config.json", config)
        write_json(bundle / "metadata.json", metadata)
        return bundle

    def derive(self, *, probe: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
        return W.derive_document(repo_root=self.repo, packs=[self.pack], reference_roots=[self.references],
                                 runtime_probe=probe or {"versions": VERSIONS, "platform": PLATFORM,
                                                         "machine": "arm64"},
                                 runtime_python="/fake/python", **extra)

    def expected_identity(self, relative: str) -> dict[str, str]:
        """What the harvest recomputes from a bundle of this config (a real adapter run of it)."""

        config = self.configs[relative]
        return derive_model_runtime_config_from_metadata(config, bundle_metadata(config, self.repo))[1]


class DerivedPinsAreWhatTheHarvestRecomputes(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.fixture = SyntheticPack(self.root)

    def test_both_execution_paths_match_a_bundle_of_the_unit(self) -> None:
        document = self.fixture.derive()
        units = document["units"]
        for unit_id, relative, path in (("pk/decode", ALPHA_DECODE, "run_suite"),
                                        ("pk/prefill_p2048", ALPHA_PREFILL, "run_workload")):
            with self.subTest(unit_id):
                expected = self.fixture.expected_identity(relative)
                self.assertEqual(units[unit_id]["model_artifact_sha256"], expected["model_artifact_sha256"])
                self.assertEqual(units[unit_id]["runtime_identity_sha256"], expected["runtime_identity_sha256"])
                self.assertEqual(units[unit_id]["execution_path"], path)
                self.assertEqual(stack_identity_sha256(units[unit_id]["stack_identity"]),
                                 units[unit_id]["runtime_identity_sha256"])
        # The reference ran the single-prompt path, so only the decode unit's policy was predicted.
        self.assertNotEqual(units["pk/decode"]["runtime_identity_sha256"],
                            units["pk/prefill_p2048"]["runtime_identity_sha256"])
        self.assertEqual("suite_completed", units["pk/decode"]["output_policy"]["stop_condition"])

    def test_written_file_is_read_by_the_arm_collector_and_marked_unsealed(self) -> None:
        document = self.fixture.derive()
        path = self.root / "identity_pins.json"
        path.write_bytes(W.render(document))
        pins = read_identity_pins(path)
        self.assertEqual({unit: entry["model_artifact_sha256"] for unit, entry in document["units"].items()},
                         pins["model_artifact_sha256"])
        self.assertEqual(runtime_versions_sha256(VERSIONS), pins["runtime_versions_sha256"])
        self.assertEqual("UNSEALED_DRAFT", document["status"])
        self.assertIs(False, document["sealed"])

    def test_config_set_is_the_projection_fold_of_the_unit_configs(self) -> None:
        document = self.fixture.derive()
        expected = identity_unit_config_set_sha256(
            scientific_config_identity_sha256(self.fixture.configs[path]) for path in (ALPHA_DECODE, ALPHA_DECODE_2))
        self.assertEqual(expected, document["units"]["pk/decode"]["config_set_sha256"])

    def test_config_bytes_differing_from_the_inventory_refuse(self) -> None:
        (self.fixture.pack / ALPHA_PREFILL_2).write_bytes(b'{"tampered": true}\n')
        with self.assertRaisesRegex(W.IdentityPinsError, "the inventory says"):
            self.fixture.derive()

    def test_references_from_another_os_build_refuse(self) -> None:
        with self.assertRaisesRegex(W.IdentityPinsError, "another runtime"):
            self.fixture.derive(probe={"versions": VERSIONS, "platform": "macOS-26.7-arm64-arm-64bit-Mach-O",
                                       "machine": "arm64"})
        other = copy.deepcopy(VERSIONS)
        other["packages"]["mlx"] = "0.32.0"
        with self.assertRaisesRegex(W.IdentityPinsError, "mlx_version"):
            self.fixture.derive(probe={"versions": other, "platform": PLATFORM, "machine": "arm64"})

    def test_a_reference_whose_policy_the_rule_does_not_reproduce_refuses(self) -> None:
        metadata_path = self.fixture.references / "ref-prefill-r01/metadata.json"
        metadata = json.loads(metadata_path.read_bytes())
        metadata["workload_provenance"]["output_policy"]["stop_condition"] = "suite_completed"
        write_json(metadata_path, metadata)
        with self.assertRaisesRegex(W.IdentityPinsError, "positive control failed"):
            self.fixture.derive()

    def test_references_that_disagree_on_the_stack_refuse(self) -> None:
        bundle = self.fixture.add_reference("ref-prefill-r02", self.fixture.reference_config)
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        metadata["workload_provenance"]["tokenizer"]["vocab_size"] = 151936
        write_json(bundle / "metadata.json", metadata)
        with self.assertRaisesRegex(W.IdentityPinsError, "disagree on the runtime stack"):
            self.fixture.derive()

    def test_no_reference_of_the_model_refuses(self) -> None:
        other = copy.deepcopy(self.fixture.reference_config)
        other["model"]["revision"] = "0" * 40
        (self.fixture.references / "ref-prefill-r01/config.json").write_bytes(
            (json.dumps(other, indent=2, sort_keys=True) + "\n").encode())
        with self.assertRaisesRegex(W.IdentityPinsError, "no reference bundle ran"):
            self.fixture.derive()

    def test_a_frozen_model_pin_that_differs_refuses(self) -> None:
        self.fixture.write(frozen_model="1" * 64)
        with self.assertRaisesRegex(W.IdentityPinsError, "frozen model pin"):
            self.fixture.derive()

    def test_local_mirror_hash_is_checked_when_asked(self) -> None:
        document = self.fixture.derive(local_artifact=W.model_artifact_identity)
        self.assertIn("pk/decode", document["units"])
        with self.assertRaisesRegex(W.IdentityPinsError, "local model mirror"):
            self.fixture.derive(local_artifact=lambda source: {"status": "ok", "folded_sha256": "2" * 64})


class OutputPolicyRuleMatchesTheRealAdapter(unittest.TestCase):
    """For one config of every committed ``_v5`` identity unit, the rule equals what the adapter records."""

    def test_every_unit_of_the_three_packs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp)
            (model / "model.safetensors").write_bytes(b"w")
            for pack in PACKS:
                tree = json.loads((ROOT / "configs/campaigns" / pack / "plan_tree.json").read_bytes())
                for unit in tree["arm_attachments"]["identity_pin_projection"]["identity_units"]:
                    relative = unit["config_inventory"][0]["path"]
                    config = json.loads((ROOT / "configs/campaigns" / pack / relative).read_bytes())
                    with self.subTest(pack=pack, unit=unit["identity_unit_id"]):
                        predicted = W.predicted_output_policy(config, ROOT)
                        _prepare, result = run_member(runnable(config, model), ROOT)
                        recorded = result.workload_provenance["output_policy"]
                        self.assertEqual(predicted, {key: recorded[key] for key in W.OUTPUT_POLICY_KEYS})

    def test_suite_and_single_runs_share_sampler_and_tokenizer_identity(self) -> None:
        """Only the output policy differs between the paths, so the reference stack carries over."""

        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp)
            (model / "model.safetensors").write_bytes(b"w")
            decode = runnable(json.loads((ALPHA / ALPHA_DECODE).read_bytes()), model)
            prefill = runnable(json.loads((ALPHA / ALPHA_PREFILL).read_bytes()), model)
            _p, suite = run_member(decode, ROOT)
            _p, single = run_member(prefill, ROOT)
        for key in ("sampler", "tokenizer"):
            self.assertEqual(suite.workload_provenance[key], single.workload_provenance[key], key)


class CommittedDraft(unittest.TestCase):
    """The committed draft is consistent with the committed packs (no archive needed)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(DRAFT.read_bytes())

    def test_it_is_an_unsealed_pins_file_the_collector_reads(self) -> None:
        pins = read_identity_pins(DRAFT)
        self.assertEqual("UNSEALED_DRAFT", self.document["status"])
        self.assertIs(False, self.document["sealed"])
        self.assertEqual(runtime_versions_sha256(self.document["runtime_versions"]), pins["runtime_versions_sha256"])
        self.assertTrue(all(isinstance(entry.get("runtime_identity_sha256"), str)
                            for entry in self.document["units"].values()))

    def test_units_and_their_derivations_follow_the_committed_packs(self) -> None:
        seen = set()
        for pack in PACKS:
            pack_root = ROOT / "configs/campaigns" / pack
            tree = json.loads((pack_root / "plan_tree.json").read_bytes())
            for unit in tree["arm_attachments"]["identity_pin_projection"]["identity_units"]:
                unit_id = unit["identity_unit_id"]
                seen.add(unit_id)
                entry = self.document["units"][unit_id]
                configs = [json.loads((pack_root / row["path"]).read_bytes()) for row in unit["config_inventory"]]
                with self.subTest(unit=unit_id):
                    self.assertEqual(pack, entry["pack_id"])
                    self.assertEqual(unit["declared_identity"]["model_source"], entry["model_source"])
                    self.assertEqual(unit["declared_identity"]["model_revision"], entry["model_revision"])
                    self.assertEqual(identity_unit_config_set_sha256(map(scientific_config_identity_sha256, configs)),
                                     entry["config_set_sha256"])
                    self.assertEqual(W.predicted_output_policy(configs[0], ROOT), entry["output_policy"])
                    self.assertEqual(entry["output_policy"],
                                     entry["stack_identity"]["sampler_output_policy"]["output_policy"])
                    self.assertEqual(stack_identity_sha256(entry["stack_identity"]), entry["runtime_identity_sha256"])
                    self.assertEqual(entry["stack_identity"]["model_artifact_sha256"], entry["model_artifact_sha256"])
        self.assertEqual(seen, set(self.document["units"]))

    def test_one_model_has_one_artifact_pin(self) -> None:
        by_source: dict[str, set[str]] = {}
        for entry in self.document["units"].values():
            by_source.setdefault(entry["model_source"], set()).add(entry["model_artifact_sha256"])
        self.assertEqual(2, len(by_source))
        self.assertTrue(all(len(pins) == 1 for pins in by_source.values()))

    @unittest.skipUnless(all(Path(root).is_dir() for root in W.DEFAULT_REFERENCE_ROOTS)
                         and Path(W.DEFAULT_RUNTIME_PYTHON).is_file(),
                         "the block-3 reference archive and the measurement interpreter are on Ed's Mac only")
    def test_regenerating_from_the_archive_gives_the_same_bytes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, W.main(["--repo", str(ROOT), "--check"]))


if __name__ == "__main__":
    unittest.main()
