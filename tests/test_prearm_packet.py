"""Fail-closed, relocatable static packets built from synthetic inputs only."""

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from tests.git_fixture import init_git_fixture


class PrearmPacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "laptop"
        self.root.mkdir()
        init_git_fixture(self.root, "-q")
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Synthetic",
                        "-c", "user.email=synthetic@example.invalid", "commit", "--allow-empty", "-qm", "fixture"],
                       check=True, capture_output=True)
        head = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        (self.root / "scripts").mkdir()
        (self.root / "kit").mkdir()
        (self.root / "kit/input.json").write_text('{"synthetic": true}\n')
        # Each original validator does actual deterministic CPU work, returns
        # stable bytes and validates its inputs; there are no sleeps/weights.
        (self.root / "scripts/check.py").write_text(
            "import hashlib,json,pathlib,sys\n"
            "raw=pathlib.Path('kit/input.json').read_bytes()\n"
            "assert json.loads(raw)['synthetic'] is True\n"
            "for _ in range(3000): raw=hashlib.sha256(raw).digest()\n"
            "print(sys.argv[1]+':'+raw.hex())\n")
        self.plan = {"plan_id": "synthetic-plan", "repo_head": head,
                     "measurement_head": head, "authored_epoch_s": 90}
        (self.root / "plan.json").write_text(json.dumps(self.plan))
        (self.root / "receipt.json").write_text('{"valid_until_epoch_s": 200}')
        self.recipe = {"schema": "joulewise.prearm_recipe.v1", "plan": "plan.json",
                       "identity": {k: self.plan[k] for k in ("plan_id", "repo_head", "measurement_head")},
                       "files": ["plan.json", "receipt.json"], "trees": ["scripts", "kit"],
                       "receipts": [{"path": "receipt.json", "expires_field": "valid_until_epoch_s"}],
                       "not_after_epoch_s": 190,
                       "checks": [{"name": name, "argv": ["{python}", "-B", "{root}/scripts/check.py", name],
                                   "timeout_s": 10} for name in (
                                       "kit_regeneration", "plan_identity", "receipt_validation", "static_config")]}
        self.path = self.base / "packet.json"

    def build(self, **kwargs):
        from joulewise.prearm_packet import build
        return build(self.root, self.recipe, self.path, now=100, **kwargs)

    def verify(self, digest, **kwargs):
        from joulewise.prearm_packet import verify
        return verify(self.root, self.recipe, self.path, digest, now=101, **kwargs)

    def test_original_and_packet_results_are_exact_and_verify_runs_no_validators(self):
        from joulewise.prearm_packet import run_checks
        original = run_checks(self.root, self.recipe)
        digest = self.build()
        from unittest.mock import patch
        with patch("joulewise.prearm_packet.run_checks", side_effect=AssertionError("recomputed")):
            self.assertEqual(original, self.verify(digest))
        self.assertEqual(0, self.path.stat().st_mode & 0o222)

    def test_changed_inputs_including_new_tree_member_refuse(self):
        from joulewise.prearm_packet import PacketError
        digest = self.build()
        for relative in ("kit/input.json", "scripts/check.py", "plan.json", "receipt.json", "kit/new.json"):
            path = self.root / relative
            prior = path.read_bytes() if path.exists() else None
            path.write_bytes(b"changed")
            with self.subTest(path=relative), self.assertRaises(PacketError):
                self.verify(digest)
            if prior is None:
                path.unlink()
            else:
                path.write_bytes(prior)

    def test_digest_corruption_and_recipe_drift_refuse(self):
        from joulewise.prearm_packet import PacketError
        digest = self.build()
        with self.assertRaises(PacketError):
            self.verify("0" * 64)
        self.recipe["checks"][0]["argv"].append("extra")
        with self.assertRaises(PacketError):
            self.verify(digest)
        self.recipe["checks"][0]["argv"].pop()
        self.path.chmod(0o600)
        self.path.write_bytes(self.path.read_bytes() + b" ")
        with self.assertRaises(PacketError):
            self.verify(digest)

    def test_stale_future_and_exact_expiry_refuse(self):
        from joulewise.prearm_packet import verify, PacketError
        digest = self.build()
        for now in (99, 190, 201, float("nan"), True):
            with self.subTest(now=now), self.assertRaises(PacketError):
                verify(self.root, self.recipe, self.path, digest, now=now)

    def test_receipt_expiry_and_plan_age_bound_packet(self):
        from joulewise.prearm_packet import build, PacketError
        for modification in ("receipt", "plan"):
            with self.subTest(modification=modification):
                if modification == "receipt":
                    (self.root / "receipt.json").write_text('{"valid_until_epoch_s": 99}')
                else:
                    (self.root / "receipt.json").write_text('{"valid_until_epoch_s": 200}')
                    self.plan["authored_epoch_s"] = -200000
                    (self.root / "plan.json").write_text(json.dumps(self.plan))
                with self.assertRaises(PacketError):
                    build(self.root, self.recipe, self.path, now=100)
                self.assertFalse(self.path.exists())

    def test_failing_validator_mutation_or_missing_check_never_publishes(self):
        from joulewise.prearm_packet import PacketError
        for source in ("raise SystemExit(7)", "from pathlib import Path; Path('kit/input.json').write_text('changed')"):
            (self.root / "scripts/check.py").write_text(source)
            with self.assertRaises(PacketError):
                self.build()
            self.assertFalse(self.path.exists())
        self.recipe["checks"].pop()
        with self.assertRaises(PacketError):
            self.build()

    def test_relocation_and_changed_git_head(self):
        from joulewise.prearm_packet import verify, PacketError
        digest = self.build()
        host = self.base / "synthetic-mbp"
        shutil.copytree(self.root, host)
        self.assertEqual(self.verify(digest), verify(host, self.recipe, self.path, digest, now=101))
        subprocess.run(["git", "-C", str(host), "-c", "user.name=Synthetic", "-c", "user.email=x@y.invalid",
                        "commit", "--allow-empty", "-qm", "changed head"], check=True, capture_output=True)
        with self.assertRaises(PacketError):
            verify(host, self.recipe, self.path, digest, now=101)

    def test_existing_packet_is_never_replaced(self):
        self.build()
        before = self.path.read_bytes()
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(before, self.path.read_bytes())

    def test_new_empty_directory_or_executable_mode_change_refuses(self):
        from joulewise.prearm_packet import PacketError
        digest = self.build()
        added = self.root / "kit/new-directory"
        added.mkdir()
        with self.assertRaises(PacketError):
            self.verify(digest)
        added.rmdir()
        (self.root / "scripts/check.py").chmod(0o755)
        with self.assertRaises(PacketError):
            self.verify(digest)

    def test_atomic_publication_failure_leaves_no_packet_or_temporary(self):
        from unittest.mock import patch
        with patch("joulewise.prearm_packet.os.link", side_effect=OSError("synthetic interruption")):
            with self.assertRaises(OSError):
                self.build()
        self.assertFalse(self.path.exists())
        self.assertFalse(list(self.base.glob(".prearm-*")))

    def test_paths_cannot_escape_or_follow_symlinks(self):
        from joulewise.prearm_packet import PacketError
        external = self.base / "outside"
        external.write_text("synthetic")
        (self.root / "alias").symlink_to(external)
        for name in ("../outside", str(external), "alias", "restricted/never-open"):
            recipe = copy.deepcopy(self.recipe)
            recipe["files"].append(name)
            with self.subTest(name=name), self.assertRaises(PacketError):
                from joulewise.prearm_packet import build
                build(self.root, recipe, self.path, now=100)

    def test_cli_requires_both_independent_pins_and_preserves_results(self):
        now = time.time()
        self.plan["authored_epoch_s"] = now - 1
        (self.root / "plan.json").write_text(json.dumps(self.plan))
        (self.root / "receipt.json").write_text(json.dumps({"valid_until_epoch_s": now + 600}))
        self.recipe["not_after_epoch_s"] = now + 300
        recipe_path = self.base / "recipe.json"
        raw = json.dumps(self.recipe).encode()
        recipe_path.write_bytes(raw)
        argv = [sys.executable, "-B", str(Path(__file__).resolve().parents[1] / "scripts/prearm_packet.py"),
                "build", "--root", str(self.root), "--recipe", str(recipe_path),
                "--recipe-sha256", hashlib.sha256(raw).hexdigest(), "--packet", str(self.path)]
        built = subprocess.run(argv, capture_output=True, text=True)
        self.assertEqual(0, built.returncode, built.stderr)
        argv[3] = "verify"
        missing = subprocess.run(argv, capture_output=True, text=True)
        self.assertEqual(2, missing.returncode)
        digest = json.loads(built.stdout)["packet_sha256"]
        verified = subprocess.run(argv + ["--packet-sha256", digest], capture_output=True, text=True)
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertEqual(json.loads(self.path.read_bytes())["results"], json.loads(verified.stdout)["results"])
        recipe_path.write_bytes(raw + b" ")
        refused = subprocess.run(argv + ["--packet-sha256", digest], capture_output=True, text=True)
        self.assertEqual(2, refused.returncode)


if __name__ == "__main__":
    unittest.main()
