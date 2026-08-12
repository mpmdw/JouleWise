from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from joulewise.arm_readiness import (
    PACK_DIGEST_DOMAIN,
    ArmReadinessError,
    committed_pack_tree_sha256,
    gnu_sidecar,
    render_json,
)
from tests.test_arm_readiness_schemas import sample_arm


class CommittedPackDigestTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        repo = Path(temporary.name) / "repo"
        pack = repo / "pack"
        (pack / "sub").mkdir(parents=True)
        (pack / "a.txt").write_bytes(b"alpha\n")
        script = pack / "sub/run.sh"
        script.write_bytes(b"#!/bin/sh\nexit 0\n")
        script.chmod(0o755)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "tests@joulewise.invalid"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "JouleWise tests"], cwd=repo, check=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repo, check=True)
        return temporary, repo, pack

    def test_byte_exact_domain_nul_lf_framing_and_determinism(self) -> None:
        temporary, _repo, pack = self.make_repo()
        self.addCleanup(temporary.cleanup)
        expected = bytearray(PACK_DIGEST_DOMAIN)
        for relative, mode, raw in (
            (b"a.txt", b"100644", b"alpha\n"),
            (b"sub/run.sh", b"100755", b"#!/bin/sh\nexit 0\n"),
        ):
            expected.extend(relative + b"\0" + mode + b"\0")
            expected.extend(str(len(raw)).encode() + b"\0")
            expected.extend(hashlib.sha256(raw).hexdigest().encode() + b"\n")
        digest = hashlib.sha256(expected).hexdigest()
        self.assertEqual(committed_pack_tree_sha256(pack), digest)
        self.assertEqual(committed_pack_tree_sha256(pack), digest)

    def test_pack_mutations_refuse_bytes_path_mode_missing_extra_untracked_symlink(self) -> None:
        cases = {
            "byte": lambda pack: (pack / "a.txt").write_bytes(b"changed\n"),
            "path": lambda pack: (pack / "a.txt").rename(pack / "renamed.txt"),
            "mode": lambda pack: (pack / "a.txt").chmod(0o755),
            "missing": lambda pack: (pack / "a.txt").unlink(),
            "extra": lambda pack: (pack / "extra.txt").write_text("extra"),
            "untracked": lambda pack: (pack / "sub/untracked.txt").write_text("untracked"),
            "empty-directory": lambda pack: (pack / "empty-untracked").mkdir(),
            "symlink": lambda pack: (pack / "link").symlink_to("a.txt"),
        }
        for name, mutate in cases.items():
            with self.subTest(case=name):
                temporary, _repo, pack = self.make_repo()
                try:
                    mutate(pack)
                    with self.assertRaises(ArmReadinessError):
                        committed_pack_tree_sha256(pack)
                finally:
                    temporary.cleanup()

    def test_non_utf8_path_and_git_symlink_modes_refuse(self) -> None:
        temporary, repo, pack = self.make_repo()
        self.addCleanup(temporary.cleanup)
        bad = os.fsencode(pack) + b"/bad-\xff"
        try:
            descriptor = os.open(bad, os.O_CREAT | os.O_WRONLY, 0o644)
        except OSError:
            # The fixture cannot exist everywhere: bare APFS refuses
            # undecodable name bytes with EILSEQ (errno 92), and some managed
            # macOS sandboxes reject them earlier with PermissionError.  The
            # validator branch remains exercised on filesystems that admit
            # the fixture (Linux CI); the symlink-mode case below is
            # independent and must still run everywhere.
            descriptor = None
        if descriptor is not None:
            os.write(descriptor, b"bad")
            os.close(descriptor)
            subprocess.run([b"git", b"add", b"--", bad], cwd=os.fsencode(repo), check=True)
            subprocess.run(["git", "commit", "-qm", "non utf8"], cwd=repo, check=True)
            with self.assertRaisesRegex(ArmReadinessError, "non-UTF-8"):
                committed_pack_tree_sha256(pack)

        temporary2, repo2, pack2 = self.make_repo()
        self.addCleanup(temporary2.cleanup)
        (pack2 / "tracked-link").symlink_to("a.txt")
        subprocess.run(["git", "add", "."], cwd=repo2, check=True)
        subprocess.run(["git", "commit", "-qm", "symlink"], cwd=repo2, check=True)
        with self.assertRaisesRegex(ArmReadinessError, "mode/type"):
            committed_pack_tree_sha256(pack2)

    def test_governed_namespace_anomaly_refuses_and_external_arm_has_no_hash_cycle(self) -> None:
        temporary, _repo, pack = self.make_repo()
        self.addCleanup(temporary.cleanup)
        before = committed_pack_tree_sha256(pack)
        custody = Path(temporary.name) / "custody/pack/arm_readiness.receipts"
        custody.mkdir(parents=True)
        arm = sample_arm(temporary.name)
        raw = render_json(arm)
        (custody / "arm-0001.json").write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        (custody / "arm-0001.json.sha256").write_bytes(
            gnu_sidecar(digest, "arm-0001.json")
        )
        after = committed_pack_tree_sha256(pack)
        self.assertEqual(before, after)

        (pack / "arm_readiness.freeze.receipts").mkdir()
        (pack / "arm_readiness.freeze.receipts/not-a-receipt.txt").write_text("x")
        with self.assertRaises(ArmReadinessError):
            committed_pack_tree_sha256(pack)


if __name__ == "__main__":
    unittest.main()
