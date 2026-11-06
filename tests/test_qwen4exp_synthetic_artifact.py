"""Synthetic canonical artifact tests; no released weights are ever used."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import align_convert_qwen4_exp as converter
from scripts import qwen4exp_mbp_live as live
from scripts import qwen4exp_mbp_report as report
from scripts import qwen4exp_synthetic_artifact as synthetic


HAS_MLX = importlib.util.find_spec("mlx") is not None and importlib.util.find_spec("mlx_lm") is not None


class ModeAndReportTests(unittest.TestCase):
    def test_synthetic_real_flag_must_match_both_directions(self):
        for manifest, flag in (({"synthetic": True}, False), ({}, True)):
            with self.subTest(manifest=manifest, flag=flag), self.assertRaisesRegex(ValueError, "must match"):
                live.verify_artifact_mode(manifest, argparse.Namespace(synthetic=flag, command="memory"))
        self.assertTrue(live.verify_artifact_mode(
            {"synthetic": True}, argparse.Namespace(synthetic=True, command="performance")))

    def test_quality_benchmark_and_hosted_refuse_synthetic(self):
        for command in ("quality", "benchmark", "hosted"):
            with self.subTest(command=command), self.assertRaises(SystemExit):
                live.parse_args([command, "--synthetic"])

    def test_report_stamps_synthetic_rows(self):
        reports = {"memory.json": {"synthetic": True, "results": {"runs": [{
            "context": 4096, "prompt_tokens": 4095, "metal": {"peak_bytes": 1},
            "ple_after": {},
        }]}}}
        rendered = report.render(report.TEMPLATE.read_text(), reports, "synthetic-test")
        self.assertIn("| SYNTHETIC | 4096 |", rendered)


@unittest.skipUnless(HAS_MLX, "MLX required; lead runs in the pinned native Mac environment")
class SyntheticArtifactTests(unittest.TestCase):
    def setUp(self):
        from tests.align import test_qwen4_exp_canonical as canonical
        reason = canonical._skip_reason()
        if reason:
            self.skipTest(reason)
        self.canonical = canonical

    @staticmethod
    def _inventory(directory):
        tensors, files = {}, {}
        for path in sorted(Path(directory).glob("*.safetensors")):
            header, _ = converter.tensor_header(path)
            for name, spec in header.items():
                if name != "__metadata__":
                    tensors[name] = (tuple(spec["shape"]), spec["dtype"], path.name)
            files[path.name] = path.stat().st_size
        for path in Path(directory).glob("ngram-*.bin"):
            files[path.name] = path.stat().st_size
        return tensors, files

    def test_tiny_inventory_file_sizes_and_manifest_match_real_conversion(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                self.canonical, "WORK_ROOT", Path(tmp) / "canonical"):
            fixture = self.canonical.Fixture()
            real = fixture.converted("maxfit")
            source = fixture.reference.ckpt
            made = Path(tmp) / "synthetic"
            manifest = synthetic.build(source / "config.json", source, made, "maxfit", 0)
            self.assertEqual(self._inventory(made), self._inventory(real))
            self.assertTrue(manifest["synthetic"])
            self.assertEqual(manifest["seed"], 0)
            verified = converter._verify(made, known_digests=manifest["files"])[0]
            self.assertTrue(verified["synthetic"])
            self.assertEqual(json.loads((made / "config.json").read_text())["ngram_tables"]["io"], "mmap")

    def test_official_config_prediction_is_within_half_percent_of_size_model(self):
        path = os.environ.get("JW_QWEN4EXP_OFFICIAL_CONFIG")
        if not path:
            self.skipTest("set JW_QWEN4EXP_OFFICIAL_CONFIG to pinned de4b8e4d config.json on the Mac")
        config = json.loads(Path(path).read_text())
        # Converter planning is exact; these are the Saturday size-model
        # targets (decimal bytes) for six- and five-bit routed experts.
        targets = {"maxfit": 211e9, "maxfit5": 203e9}
        for profile, target in targets.items():
            actual = synthetic.predicted_bytes(config, profile)
            self.assertLess(abs(actual - target) / target, 0.005)

    def test_native_metal_load_and_one_forward(self):
        import mlx.core as mx
        if os.environ.get("JW_RUN_METAL_SYNTHETIC") != "1":
            self.skipTest("set JW_RUN_METAL_SYNTHETIC=1 on the Metal Mac")
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                self.canonical, "WORK_ROOT", Path(tmp) / "canonical"):
            fixture = self.canonical.Fixture()
            fixture.reference.build_checkpoint()
            source = fixture.reference.ckpt
            made = Path(tmp) / "synthetic"
            manifest = synthetic.build(source / "config.json", source, made, "maxfit", 0)
            pin = converter.sha256(made / "manifest.json")
            model, _ = converter.load_verified_model(made, pin)
            logits = model(mx.array([[1, 2, 3]]))
            mx.eval(logits)
            self.assertEqual(logits.shape[:2], (1, 3))


if __name__ == "__main__":
    unittest.main()
