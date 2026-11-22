"""One registered, durable reservation for each invented controls look."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import controls_release as release

from . import test_ctl_print as fixtures


def reservation_fixture(root, name, mode):
    scratch = root / name
    scratch.mkdir()
    worker = release.run_controls_worker
    reserve = release._reserve_at

    def run(**kwargs):
        frozen = kwargs["freeze_inputs"]["working"]["manifest"]
        (scratch / "manifest.sha256").write_text(sha256(frozen).hexdigest())
        reader = kwargs["first_read"]

        def read(bindings):
            positions = reader(bindings)
            (scratch / "read-complete").touch()
            if mode == "fail":
                raise ValueError("invented failure after reading")
            return positions

        def race(private, public):
            (scratch / "ready").touch()
            deadline = time.monotonic() + 45
            while not all((root / peer / "ready").exists() for peer in ("left", "right")):
                if time.monotonic() > deadline:
                    raise RuntimeError("synthetic race did not reach the reservation")
                time.sleep(0.02)
            return reserve(private, public)

        kwargs["first_read"] = read
        if mode == "alternate":
            alternate = root / "alternate" / "lm-ctl-01" / "synthetic-output"
            try:
                worker(**kwargs, restricted=alternate)
            except TypeError as error:
                if "unexpected keyword argument 'restricted'" not in str(error):
                    raise
            else:
                raise AssertionError("worker accepted an alternate private root")
        if mode == "replaced_root":
            path = Path(json.loads(frozen)["release_layout"]["private"]["path"])
            path.rename(path.with_name("old-private-root"))
            path.mkdir()
        if mode == "concurrent":
            with patch.object(release, "_reserve_at", side_effect=race):
                worker(**kwargs)
        elif mode == "sync_failure":
            with patch.object(release.os, "fsync", side_effect=OSError("invented directory sync failure")):
                worker(**kwargs)
        else:
            worker(**kwargs)

    with patch.object(release, "run_controls_worker", side_effect=run):
        fixtures.worker_fixture(scratch, "ok", synthetic_path=True, registered_root=root)


class TestControlsReservation(unittest.TestCase):
    def _prepare(self, directory):
        root = Path(directory).resolve()
        for side in ("private", "public", "alternate"):
            (root / side / "lm-ctl-01").mkdir(parents=True)
        return root

    def _command(self, root, name, mode):
        launcher = ("import sys; from pathlib import Path; from tests.contracts.cadence_looks."
                    "test_ctl_print_reservation_acceptance import reservation_fixture; "
                    "reservation_fixture(Path(sys.argv[1]), sys.argv[2], sys.argv[3])")
        return [sys.executable, "-B", "-c", launcher, str(root), name, mode]

    def _run(self, root, name, mode):
        return subprocess.run(self._command(root, name, mode), cwd=fixtures.ROOT, capture_output=True)

    def _first_reads(self, root, names):
        return [(root / name / "first-read").exists() for name in names]

    def _assert_same_manifest(self, root, names):
        self.assertEqual(len({(root / name / "manifest.sha256").read_bytes() for name in names}), 1)

    def test_concurrent_workers_race_on_one_registered_reservation(self):
        with TemporaryDirectory() as directory:
            root = self._prepare(directory)
            names = ("left", "right")
            children = [subprocess.Popen(self._command(root, name, "concurrent"), cwd=fixtures.ROOT,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE) for name in names]
            outputs = [child.communicate() for child in children]
            self.assertEqual(sorted(child.returncode for child in children), [0, 2], outputs)
            self._assert_same_manifest(root, names)
            self.assertEqual(self._first_reads(root, names), [child.returncode == 0 for child in children])
            self.assertTrue((root / "public" / "lm-ctl-01" / "PUBLIC.json").exists())
            self.assertFalse((root / "alternate" / "lm-ctl-01" / "synthetic-output").exists())

    def test_retry_at_alternate_root_refuses_after_post_read_failure(self):
        with TemporaryDirectory() as directory:
            root = self._prepare(directory)
            attempts = (("initial", "fail", 1), ("same", "ok", 2), ("elsewhere", "alternate", 2))
            for name, mode, status in attempts:
                with self.subTest(name=name):
                    result = self._run(root, name, mode)
                    self.assertEqual((result.returncode, result.stdout), (status, b""), result.stderr)
                    self.assertFalse((root / "public" / "lm-ctl-01" / "PUBLIC.json").exists())
            names = tuple(name for name, _, _ in attempts)
            self._assert_same_manifest(root, names)
            self.assertEqual(self._first_reads(root, names), [True, False, False])
            self.assertTrue((root / "initial" / "read-complete").exists())
            self.assertTrue((root / "private" / "lm-ctl-01" / "synthetic-output").is_dir())
            self.assertFalse((root / "alternate" / "lm-ctl-01" / "synthetic-output").exists())

    def test_replaced_root_and_unsynced_reservation_refuse_before_read(self):
        for mode in ("replaced_root", "sync_failure"):
            with self.subTest(mode=mode), TemporaryDirectory() as directory:
                root = self._prepare(directory)
                result = self._run(root, "candidate", mode)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (2, b"", b"REFUSE controls look before read\n"))
                self.assertEqual(self._first_reads(root, ("candidate",)), [False])
                self.assertFalse((root / "public" / "lm-ctl-01" / "PUBLIC.json").exists())

    def test_new_manifest_cannot_move_a_previously_registered_look(self):
        artifacts = dict.fromkeys(fixtures.manifest.CODE_PATHS, b"invented code fixture")
        artifacts["restricted_schema"] = b"invented private schema fixture"
        artifacts.update(fixtures.adapter.instrument_artifacts())
        original = fixtures.instrument_freeze_fixture(dict(artifacts), "ok")
        layout = json.loads(original["working"]["manifest"])["release_layout"]
        layout["private"] = dict(path="/invented/alternate/lm-ctl-01", device=1, inode=3)
        moved = fixtures.instrument_freeze_fixture(dict(artifacts), "ok", layout=layout)
        prior_revision = "a" * 40
        moved["committed"][prior_revision] = original["working"]
        original["history"][-1]["revision"] = prior_revision
        moved["history"] = original["history"] + moved["history"][1:]
        with self.assertRaisesRegex(ValueError, "controls_layout_change"):
            fixtures.manifest.verify_freeze(**moved)
