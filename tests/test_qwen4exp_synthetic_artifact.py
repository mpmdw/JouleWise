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

    def test_build_refuses_insufficient_free_space_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.json"
            config.write_text(json.dumps({"text_config": self.canonical.TEXT}))
            made = Path(tmp) / "nested" / "synthetic"
            payload = synthetic.predicted_bytes(json.loads(config.read_text()), "maxfit")
            usage = mock.Mock(free=payload)  # payload alone, without margin
            with mock.patch.object(synthetic.shutil, "disk_usage", return_value=usage) as du, \
                    self.assertRaisesRegex(ValueError, "GB free"):
                synthetic.build(config, tmp, made, "maxfit", 0)
            du.assert_called_once_with(Path(tmp))
            self.assertFalse(made.parent.exists())

    def test_every_payload_value_is_finite(self):
        # Raw random bytes as bf16 n-gram rows put a NaN/Inf in ~1/256 values,
        # poisoning every hidden state (and MoE routing) of a perf/paging run.
        import numpy as np
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                self.canonical, "WORK_ROOT", Path(tmp) / "canonical"):
            fixture = self.canonical.Fixture()
            fixture.reference.build_checkpoint()
            source = fixture.reference.ckpt
            made = Path(tmp) / "synthetic"
            manifest = synthetic.build(source / "config.json", source, made, "maxfit", 0)
            self.assertTrue(manifest["ngram_tables"])
            for descriptor in manifest["ngram_tables"].values():
                self.assertEqual(descriptor["format"], "bf16")
                bits = np.fromfile(made / descriptor["file"], dtype="<u2").astype("<u4") << 16
                self.assertTrue(np.isfinite(bits.view("<f4")).all(), descriptor["file"])
            for path in made.glob("*.safetensors"):
                header, _ = converter.tensor_header(path)
                for name, spec in header.items():
                    if name != "__metadata__" and spec["dtype"] == "BF16":
                        bits = np.asarray(converter.tensor_array(path, name)[0]).astype("<u4") << 16
                        self.assertTrue(np.isfinite(bits.view("<f4")).all(), name)

    def test_official_config_prediction_is_within_half_percent_of_size_model(self):
        path = os.environ.get("JW_QWEN4EXP_OFFICIAL_CONFIG")
        if not path:
            self.skipTest("set JW_QWEN4EXP_OFFICIAL_CONFIG to pinned de4b8e4d config.json on the Mac")
        config = json.loads(Path(path).read_text())
        # Converter planning is exact; these are the Saturday size-model
        # targets (decimal bytes): 108.0 / 92.9 GB of weights plus the
        # 102.4 GB bf16 PLE table.  (An earlier 203 GB maxfit5 target was
        # wrong: 5-bit/g64 is 5.5 bits per routed-expert weight against
        # 6.5, so maxfit5 is 15.1 GB, not 8 GB, smaller than maxfit.)
        targets = {"maxfit": 210.4e9, "maxfit5": 195.3e9}
        actual = {profile: synthetic.predicted_bytes(config, profile) for profile in targets}
        for profile, target in targets.items():
            self.assertLess(abs(actual[profile] - target) / target, 0.005, profile)
        # Independent cross-check: only routed experts change, so the size
        # delta is the memory model's peak delta (112.7 - 97.6 GB).
        peak = live.PREDICTED_PEAK
        self.assertAlmostEqual((actual["maxfit"] - actual["maxfit5"]) / 1e9,
                               (peak["maxfit"] - peak["maxfit5"]) / 1e9, delta=0.15)

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
            self.assertTrue(mx.all(mx.isfinite(logits)).item())


if __name__ == "__main__":
    unittest.main()
