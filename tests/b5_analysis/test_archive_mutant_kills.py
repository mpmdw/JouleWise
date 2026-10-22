"""Tiny fabricated source inventories exercise the public census seam."""
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from joulewise.b5_analysis.archive import ArchiveHandle


class OriginalCensusTests(unittest.TestCase):
    def handle(self, *, nested=False):
        tmp = tempfile.TemporaryDirectory(prefix="l9-census-")
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        custody = root / "custody"
        claim = custody / "requests" if nested else root / "claim"
        claim.mkdir(parents=True)
        archive = root / "archive"
        prefix = "night-custody/requests/" if nested else "claim-runs/"
        relative = prefix + "one.json"
        target = archive / "sources" / relative
        target.parent.mkdir(parents=True)
        raw = b'{"synthetic":true}\n'
        (claim / "one.json").write_bytes(raw)
        target.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        (archive / "sources/SHA256SUMS").write_text(digest + "  " + relative + "\n")
        # Byte-adapter seam only: compare_runs_root authenticates the source
        # manifest and original bytes. This does not claim full S0 selection.
        window = SimpleNamespace(archive_root=archive, claim_runs_root=claim,
            custody_root=custody, record=SimpleNamespace(record_shape="pin4"))
        return ArchiveHandle(window, {"outputs": {}}, {}), claim, digest

    def test_two_unlisted_files_have_an_integer_count(self):
        """The census counts both extras as an integer. Kills M00140."""
        handle, claim, _digest = self.handle()
        (claim / "extra-one.json").write_bytes(b"synthetic extra one")
        (claim / "extra-two.json").write_bytes(b"synthetic extra two")
        flags = handle.compare_runs_root()
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["code"], "runs_root_has_unlisted_file")
        self.assertIs(type(flags[0]["count"]), int)
        self.assertEqual(flags[0]["count"], 2)

    def test_nested_claim_root_uses_custody_inventory(self):
        """Claims below custody match night-custody/requests. Kills M00397, M00398."""
        handle, _claim, digest = self.handle(nested=True)
        self.assertEqual(handle.compare_runs_root(), ())
        original = next(row for row in handle.census() if row.path == "original/claim-runs/one.json")
        self.assertEqual((original.sha256, original.check), (digest, "sources_sha256sums"))

    def test_repeated_census_preserves_result_and_records(self):
        """An unchanged original can be censused twice on one handle. Kills M00409."""
        handle, _claim, _digest = self.handle()
        first = handle.compare_runs_root()
        census = handle.census()
        self.assertEqual(first, ())
        self.assertEqual(handle.compare_runs_root(), first)
        self.assertEqual(handle.census(), census)
