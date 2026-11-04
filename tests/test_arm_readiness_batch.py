"""D-188 SMALL-FIXES: committed_pack_tree_sha256 reads blobs with one cat-file --batch.

The batched read must give the same digest as the per-oid reads, and under any
Git anomaly the same refusal (reason code and message) at the same serial
position: every blob the batch did not return cleanly takes the original
per-oid ``_run_git`` call.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
from joulewise.arm_readiness import ArmReadinessError, committed_pack_tree_sha256
from tests.git_fixture import init_git_fixture


def _git(repo: Path, *args: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(("git", "-C", str(repo), *args), check=True, capture_output=True, **kwargs)


def _outcome(pack: Path):
    try:
        return ("ok", committed_pack_tree_sha256(pack))
    except ArmReadinessError as exc:
        return ("refused", exc.reason_code, str(exc))


class PackBlobBatchTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="d188-batch-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name).resolve() / "repo"
        self.pack = self.repo / "pack"
        (self.pack / "sub").mkdir(parents=True)
        files = {
            "a.txt": b"alpha\n",
            "b.bin": bytes(range(256)) * 3,
            # Payloads that look like batch headers and delimiters.
            "c.txt": b"0123456789012345678901234567890123456789 blob 5\nfake\n\n",
            "empty": b"",
            "nonl": b"no trailing newline",
            "sub/d.json": b'{"d": 1}\n',
            "sub/same-as-a.txt": b"alpha\n",
        }
        for relative, raw in files.items():
            (self.pack / relative).write_bytes(raw)
        script = self.pack / "sub/run.sh"
        script.write_bytes(b"#!/bin/sh\nexit 0\n")
        script.chmod(0o755)
        init_git_fixture(self.repo, "-q")
        _git(self.repo, "config", "user.email", "tests@joulewise.invalid")
        _git(self.repo, "config", "user.name", "JouleWise tests")
        _git(self.repo, "add", ".")
        _git(self.repo, "commit", "-qm", "fixture")

    def per_oid(self, pack: Path | None = None):
        """The pre-D-188 path: the batch returns nothing, every blob is read per oid."""
        with mock.patch.object(readiness, "_pack_blob_batch", return_value={}):
            return _outcome(pack or self.pack)

    def cat_file_calls(self):
        real = readiness._run_git
        calls = []

        def counted(root, *args):
            if args[:1] == ("cat-file",):
                calls.append(args)
            return real(root, *args)

        return calls, mock.patch.object(readiness, "_run_git", side_effect=counted)

    def oid(self, relative: str) -> str:
        return _git(self.repo, "rev-parse", f"HEAD:pack/{relative}").stdout.decode().strip()

    def test_batch_digest_equals_per_oid_digest_with_no_per_oid_calls(self) -> None:
        reference = self.per_oid()
        self.assertEqual(reference[0], "ok")
        calls, patch = self.cat_file_calls()
        with patch:
            self.assertEqual(_outcome(self.pack), reference)
        self.assertEqual(calls, [])

    def test_missing_blob_takes_the_per_oid_call_and_refusal(self) -> None:
        oid = self.oid("sub/d.json")
        loose = self.repo / ".git/objects" / oid[:2] / oid[2:]
        self.assertTrue(loose.is_file())
        loose.chmod(0o644)
        loose.unlink()
        reference = self.per_oid()
        self.assertEqual(reference[:2], ("refused", "readiness_pack_not_committed"))
        calls, patch = self.cat_file_calls()
        with patch:
            self.assertEqual(_outcome(self.pack), reference)
        # The batch stopped at the missing blob: it and every later blob went per oid.
        self.assertIn(("cat-file", "blob", oid), calls)

    def test_bad_batch_lines_fall_back_for_that_blob_onward(self) -> None:
        reference = self.per_oid()
        real_run = subprocess.run
        ordered = sorted(p.relative_to(self.pack).as_posix().encode() for p in self.pack.rglob("*") if p.is_file())
        third = self.oid(ordered[2].decode())

        def corruptions(output: bytes):
            lines = output.split(b"\n")
            yield output.replace(third.encode() + b" blob", third.encode() + b" tree", 1)
            yield output.replace(third.encode(), b"f" * 40, 1)
            yield output[: output.index(third.encode()) + 10]
            yield output.replace(third.encode() + b" blob ", third.encode() + b" blob x", 1)
            yield b"\n".join(lines[:1])
            yield b""
            yield output + b"trailing garbage\n"
            yield output.replace(third.encode(), third.encode() + b" missing", 1)

        captured = {}

        def capture(argv, *args, **kwargs):
            completed = real_run(argv, *args, **kwargs)
            if tuple(argv[-2:]) == ("cat-file", "--batch"):
                captured["output"] = completed.stdout
            return completed

        with mock.patch.object(readiness.subprocess, "run", side_effect=capture):
            committed_pack_tree_sha256(self.pack)
        for index, corrupted in enumerate(corruptions(captured["output"])):
            def fake(argv, *args, _corrupted=corrupted, **kwargs):
                completed = real_run(argv, *args, **kwargs)
                if tuple(argv[-2:]) == ("cat-file", "--batch"):
                    return subprocess.CompletedProcess(argv, 0, _corrupted, b"")
                return completed

            with self.subTest(case=index), mock.patch.object(readiness.subprocess, "run", side_effect=fake):
                self.assertEqual(_outcome(self.pack), reference)

    def test_process_failures_fall_back_entirely(self) -> None:
        reference = self.per_oid()
        real_run = subprocess.run
        for failure in (subprocess.TimeoutExpired("git", 20), OSError("no git"), 128):
            def fake(argv, *args, _failure=failure, **kwargs):
                if tuple(argv[-2:]) == ("cat-file", "--batch"):
                    if isinstance(_failure, int):
                        return subprocess.CompletedProcess(argv, _failure, b"", b"fatal")
                    raise _failure
                return real_run(argv, *args, **kwargs)

            calls, patch = self.cat_file_calls()
            with self.subTest(failure=failure), patch, \
                    mock.patch.object(readiness.subprocess, "run", side_effect=fake):
                self.assertEqual(_outcome(self.pack), reference)
            self.assertEqual(len(calls), 8)

    def test_batch_uses_run_git_invocation(self) -> None:
        real_run = subprocess.run
        seen = []

        def spy(argv, *args, **kwargs):
            if tuple(argv[-2:]) == ("cat-file", "--batch"):
                seen.append((tuple(argv), kwargs.get("timeout"), kwargs.get("env"), kwargs.get("check")))
            return real_run(argv, *args, **kwargs)

        with mock.patch.object(readiness.subprocess, "run", side_effect=spy):
            committed_pack_tree_sha256(self.pack)
        self.assertEqual(seen, [(("git", "-C", str(self.repo), "cat-file", "--batch"), 20, None, False)])

    def test_disk_mutations_refuse_identically(self) -> None:
        mutations = {
            "bytes": lambda: (self.pack / "b.bin").write_bytes(b"changed"),
            "mode": lambda: (self.pack / "a.txt").chmod(0o755),
            "missing": lambda: (self.pack / "nonl").unlink(),
            "untracked": lambda: (self.pack / "extra").write_bytes(b"x"),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                self.setUp()
                mutate()
                reference = self.per_oid()
                self.assertEqual(reference[0], "refused")
                self.assertEqual(_outcome(self.pack), reference)

    def test_replace_refs_and_no_replace_environment_agree(self) -> None:
        _git(self.repo, "replace", self.oid("a.txt"), self.oid("sub/d.json"))
        reference = self.per_oid()
        self.assertEqual(reference[:2], ("refused", "readiness_pack_digest_mismatch"))
        self.assertEqual(_outcome(self.pack), reference)
        with mock.patch.dict(os.environ, {"GIT_NO_REPLACE_OBJECTS": "1"}):
            reference = self.per_oid()
            self.assertEqual(reference[0], "ok")
            self.assertEqual(_outcome(self.pack), reference)

    def test_batch_helper_never_raises_and_skips_non_oids(self) -> None:
        good = self.oid("a.txt")
        self.assertEqual(readiness._pack_blob_batch(self.repo, []), {})
        self.assertEqual(readiness._pack_blob_batch(self.repo, ["not-an-oid", "a" * 39]), {})
        self.assertEqual(readiness._pack_blob_batch(self.repo, [good, good]), {good: b"alpha\n"})
        self.assertEqual(readiness._pack_blob_batch(self.repo / "absent", [good]), {})


if __name__ == "__main__":
    unittest.main()
