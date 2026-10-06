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


if __name__ == "__main__":
    unittest.main()
