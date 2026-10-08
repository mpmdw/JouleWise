"""PLAN2 row 9: a retried lineage publication completes (idempotent writes).

Publication writes every record create-once.  Before this change a
publication that failed part way (an EIO on the bound locator, say) left its
first records behind, and a retry refused on the first existing file, so the
driver could only run a chain whose every tagged member is then refused.  Now
an existing file holding exactly the bytes the retry would write counts as
written; any other existing content still refuses and is never replaced.
"""

from __future__ import annotations

import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import window_lineage
from tests.test_window_lineage import build_window, publish_lineage


class IdempotentPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.w = build_window(Path(tmp.name), publish=False)
        self.real_write = window_lineage._write_once

    def _fail_at(self, name: str, *, torn: bool = False):
        def write(path: Path, raw: bytes) -> None:
            if path.name == name:
                if torn:
                    with open(path, "wb") as handle:
                        handle.write(raw[: len(raw) // 2])
                raise OSError(5, "Input/output error", str(path))
            self.real_write(path, raw)

        return patch.object(window_lineage, "_write_once", side_effect=write)

    def test_a_retry_after_a_failed_locator_write_completes(self) -> None:
        with self._fail_at(window_lineage.LOCATOR_BASENAME + ".sha256"), \
                self.assertRaisesRegex(window_lineage.LineagePublicationError, "locator"):
            publish_lineage(self.w)
        self.assertFalse(window_lineage.is_hazard_runs_root(self.w.bound))
        published = publish_lineage(self.w)
        for root in (self.w.claim, self.w.bound):
            self.assertTrue(window_lineage.is_hazard_runs_root(root))
            locator, _sha = window_lineage.read_locator(root / window_lineage.LOCATOR_BASENAME)
            self.assertEqual(locator["launch_lineage"], published["launch_lineage"])
        sidecar = self.w.claim / (window_lineage.LOCATOR_BASENAME + ".sha256")
        self.assertTrue(sidecar.is_file())

    def test_a_torn_record_from_the_failed_attempt_still_refuses(self) -> None:
        with self._fail_at("launch.json", torn=True), \
                self.assertRaises(window_lineage.LineagePublicationError):
            publish_lineage(self.w)
        launch = self.w.custody / window_lineage.RECORDS_DIRNAME / "launch.json"
        torn = launch.read_bytes()
        with self.assertRaisesRegex(window_lineage.LineagePublicationError, "records"):
            publish_lineage(self.w)
        self.assertEqual(launch.read_bytes(), torn)
        self.assertFalse(window_lineage.is_hazard_runs_root(self.w.claim))

    def test_an_existing_symlink_is_never_accepted_as_the_record(self) -> None:
        records = self.w.custody / window_lineage.RECORDS_DIRNAME
        records.mkdir()
        target = self.w.base / "elsewhere.json"
        with self._fail_at("go.json"), self.assertRaises(window_lineage.LineagePublicationError):
            publish_lineage(self.w)
        authorization = records / window_lineage.AUTHORIZATION_RECORD_NAME
        target.write_bytes(authorization.read_bytes())
        authorization.unlink()
        os.symlink(target, authorization)
        with self.assertRaisesRegex(window_lineage.LineagePublicationError, "records"):
            publish_lineage(self.w)



class ExistingRecordEdgeTests(unittest.TestCase):
    """Review F1 and F3: what ``_write_once`` does with an existing path."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def test_a_record_replaced_while_being_compared_is_not_acknowledged(self) -> None:
        record = self.dir / "authorization.json"
        record.write_bytes(b'{"authorized":true}\n')
        replacement = self.dir / "replacement.json"
        replacement.write_bytes(b'{"unauthorized":true}\n')

        def replaced_after(read):
            def wrapper(*args, **kwargs):
                value = read(*args, **kwargs)
                os.replace(replacement, record)
                return value
            return wrapper

        hooks = [(name, getattr(window_lineage, name)) for name in
                 ("_read_descriptor", "_read_regular_nofollow") if hasattr(window_lineage, name)]
        with patch.multiple(window_lineage, **{name: replaced_after(fn) for name, fn in hooks}), \
                self.assertRaises(FileExistsError):
            window_lineage._write_once(record, b'{"authorized":true}\n')
        self.assertEqual(record.read_bytes(), b'{"unauthorized":true}\n')

    def test_an_existing_fifo_is_refused_without_blocking(self) -> None:
        fifo = self.dir / "authorization.json"
        os.mkfifo(fifo)
        outcome: list[BaseException | None] = []

        def attempt() -> None:
            try:
                window_lineage._write_once(fifo, b"{}\n")
                outcome.append(None)
            except BaseException as exc:  # noqa: BLE001 - recorded for the assertion
                outcome.append(exc)

        thread = threading.Thread(target=attempt, daemon=True)
        thread.start()
        thread.join(timeout=5.0)
        if thread.is_alive():
            # Unblock the hung open so the test process can exit.
            os.close(os.open(fifo, os.O_WRONLY | os.O_NONBLOCK))
            thread.join(timeout=5.0)
            self.fail("_write_once blocked on an existing FIFO")
        self.assertEqual(len(outcome), 1)
        self.assertIsInstance(outcome[0], FileExistsError)


if __name__ == "__main__":
    unittest.main()
