"""Tests for the no-reconversion mmap-to-pread artifact derivation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import qwen4exp_ple_io_variant as variant


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tiny_artifact(root: Path):
    root.mkdir()
    config = {"ngram_tables": {"io": "mmap", "layers": {}}}
    (root / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (root / "payload.bin").write_bytes(b"canonical fixture payload")
    manifest = {"format": "fixture", "files": {"config.json": sha(root / "config.json"),
                                                 "payload.bin": sha(root / "payload.bin")}}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return sha(root / "manifest.json")


class VariantTests(unittest.TestCase):
    def test_tiny_canonical_artifact_derives_and_both_pins_verify(self):
        import scripts.align_convert_qwen4_exp as converter
        with tempfile.TemporaryDirectory() as tmp:
            source, destination = Path(tmp) / "mmap", Path(tmp) / "pread"
            pin = tiny_artifact(source)

            def copy_clone(src, dst):
                Path(dst).write_bytes(Path(src).read_bytes())

            with patch.object(variant, "_volume_identity", return_value="fixture-apfs"), \
                 patch.object(variant, "_clonefile", side_effect=copy_clone) as clone:
                new_pin = variant.derive(source, pin, destination)
            converter._verify(source, pin)
            derived, blobs, _ = converter._verify(destination, new_pin)
            self.assertEqual(json.loads(blobs["config.json"])["ngram_tables"]["io"], "pread")
            self.assertEqual(derived["derived_from"], {"pin": pin, "io": {"from": "mmap", "to": "pread"}})
            self.assertEqual((source / "payload.bin").read_bytes(), (destination / "payload.bin").read_bytes())
            clone.assert_called_once_with(source / "payload.bin", destination / "payload.bin")

    def test_refuses_clone_when_destination_is_not_same_apfs_volume(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, destination = Path(tmp) / "mmap", Path(tmp) / "pread"
            pin = tiny_artifact(source)
            with patch.object(variant, "_volume_identity", side_effect=["apfs-a", "apfs-b"]), \
                 patch.object(variant, "_clonefile") as clone:
                with self.assertRaisesRegex(ValueError, "same APFS"):
                    variant.derive(source, pin, destination)
            clone.assert_not_called()
            self.assertFalse(destination.exists())


HAS_NATIVE = importlib.util.find_spec("mlx") is not None and importlib.util.find_spec("mlx_lm") is not None


@unittest.skipUnless(HAS_NATIVE, "native MLX/Metal required; lead runs on Apple silicon")
class NativeVariantTests(unittest.TestCase):
    def test_both_pins_load_and_ple_gathers_match_for_same_ids(self):
        if not (importlib.util.find_spec("torch") and importlib.util.find_spec("transformers")):
            self.skipTest("native canonical fixture requires torch/transformers")
        import numpy as np
        from tests.align import test_qwen4_exp_canonical as canonical
        reason = canonical._skip_reason()
        if reason:
            self.skipTest(reason)
        with tempfile.TemporaryDirectory() as tmp, patch.object(canonical, "WORK_ROOT", Path(tmp)):
            fixture = canonical.Fixture()
            source = fixture.converted("maxfit")
            pin = fixture.manifest_pin("maxfit")
            destination = Path(tmp) / "pread"
            # Native check must exercise the real APFS clonefile and volume gate.
            new_pin = variant.derive(source, pin, destination)
            converter = fixture.converter()
            mmap_model, _ = converter.load_verified_model(source, pin)
            pread_model, _ = converter.load_verified_model(destination, new_pin)
            ids = np.array([0, 1, 1, 3], dtype=np.int64)
            try:
                for layer in sorted(mmap_model.ngram_tables()):
                    np.testing.assert_array_equal(mmap_model.ngram_tables()[layer].gather(ids),
                                                  pread_model.ngram_tables()[layer].gather(ids))
            finally:
                for model in (mmap_model, pread_model):
                    for table in model.ngram_tables().values():
                        table.close()


if __name__ == "__main__":
    unittest.main()
