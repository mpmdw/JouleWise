"""BYTES C7 custody and process-level synthetic release chain; no real inputs."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.b6 import blinding
from scripts import b6_release_subset
from tests.b6.support import write_json

ROOT = Path(__file__).resolve().parents[2]


class ReleaseSubsetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.records = self.root / "records"
        self.key_dir = self.records / "bytes/blinding"
        self.configs = [
            {"model": {"name": name}, "workload_profile": {"name": "decode", "output_tokens": 512}}
            for name in ("Qwen3-1.7B-4bit", "Qwen3-4B-4bit", "Qwen3-8B-4bit", "Qwen3-30B-A3B-4bit")]
        for i, config in enumerate(self.configs):
            write_json(self.root / "configs" / (str(i) + ".json"), config)
            blinding.factor(self.key_dir, blinding.configuration_key(config))
        blinding.factor(self.key_dir, "neg8_reference")
        write_json(self.root / "registrations/p1/registration.json", {
            "pack_id": "p1", "blinding_group": "bytes", "modules": [{"config_dirs": ["configs"]}]})

    def release(self, keys, stage="fit", out="released", commit=None):
        args = ["--pack-records-root", str(self.records), "--blinding-group", "bytes",
                "--registrations-root", str(self.root / "registrations"), "--project-root", str(self.root),
                "--stage", stage, "--out", str(self.root / out), "--keys", *keys]
        if commit:
            args += ["--stage1-commit", commit]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = b6_release_subset.main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_fit_release_is_exact_verbatim_subset_with_digests_and_stage(self):
        keys = ["neg8_reference", *(blinding.configuration_key(c) for c in self.configs[:3])]
        before = {p.name: p.read_bytes() for p in self.key_dir.iterdir()}
        with patch.object(blinding, "_draw", side_effect=AssertionError("release drew a key")):
            code, _, error = self.release(keys)
        self.assertEqual((code, error), (0, ""))
        out = self.root / "released"
        expected = {"pack.json", "release.json", *(blinding._config_filename(k) for k in keys)}
        self.assertEqual({p.name for p in out.iterdir()}, expected)
        self.assertFalse((out / blinding._config_filename(blinding.configuration_key(self.configs[-1]))).exists())
        record = json.loads((out / "release.json").read_text())
        self.assertEqual(record["keys"], sorted(keys))
        self.assertEqual(record["stage"], "fit")
        self.assertIn("+00:00", record["released_utc"])
        for name, digest in record["sha256"].items():
            self.assertEqual((out / name).read_bytes(), before[name])
            self.assertEqual(digest, hashlib.sha256(before[name]).hexdigest())
            self.assertEqual((out / name).stat().st_mode & 0o777, 0o600)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.key_dir.iterdir()})

    def test_refuses_undrawn_outside_group_heldout_fit_and_uncommitted_stage2(self):
        heldout = blinding.configuration_key(self.configs[-1])
        fit = blinding.configuration_key(self.configs[0])
        (self.key_dir / blinding._config_filename(fit)).unlink()
        for key, stage, commit, message in (
                (fit, "fit", None, "blinding key missing"),
                ("outside", "fit", None, "outside the group's registrations"),
                (heldout, "fit", None, "held-out key"),
                (heldout, "heldout", None, "stage-1 commit hash"),
                (heldout, "heldout", "not-a-hash", "stage-1 commit hash")):
            code, stdout, error = self.release([key], stage, commit=commit)
            self.assertEqual(code, 1)
            self.assertEqual(stdout, "")
            self.assertTrue(error.startswith("refused: "), error)
            self.assertIn(message, error)
            self.assertFalse((self.root / "released").exists())

    def test_stage2_releases_only_explicit_keys_after_hash_without_drawing(self):
        key = blinding.configuration_key(self.configs[-1])
        # This unit test checks the hash's exact syntax, not a science quantity.
        commit = "a" * 40
        code, _, error = self.release([key], "heldout", commit=commit)
        self.assertEqual((code, error), (0, ""))
        self.assertEqual({p.name for p in (self.root / "released").iterdir()},
                         {"pack.json", "release.json", blinding._config_filename(key)})
        self.assertEqual(json.loads((self.root / "released/release.json").read_text())["stage1_commit"], commit)
        self.assertEqual(self.release([key], "heldout", commit=commit)[0], 1)

    def test_current_twelve_registrations_resolve_ten_science_keys_plus_neg8(self):
        keys = blinding.registered_keys(ROOT / "configs/b6/packs", "bytes", ROOT)
        # R1: ten configurations; R5: three fit models; A3.1: NEG-8 joins fit.
        self.assertEqual(len(keys), 11)
        self.assertEqual(sum(stage == "fit" for stage in keys.values()), 4)
        self.assertEqual(keys["neg8_reference"], "fit")

