from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.b5_analysis.archive import open_attempt_record
from joulewise.b5_analysis.windows import (AnalysisRefusal, IndexEntry, SealPins, WindowIndex, governing_pin,
                                          load_window_index, select_analysed_attempts)
from tests.b5_analysis import fixtures as fx


class WindowsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s0-windows-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pins = SealPins.load()

    def record(self, pack, **kwargs):
        entry = fx.structural_archive(self.root / (pack + str(len(list(self.root.iterdir())))), pack=pack, **kwargs)
        return open_attempt_record(entry, seal_pins=self.pins)

    def history(self):
        records = [self.record("alpha"), self.record("gamma")]
        first = open_attempt_record(fx.archived_entry("pin1", "NOT_USABLE", pack="alpha"), seal_pins=self.pins)
        records.append(first)  # first-seal history never participates in selection
        records.append(open_attempt_record(fx.archived_entry("pin2", "STD", pack="beta", claim_usable=True), seal_pins=self.pins))
        # Make the pin2 first BETA unusable using the exported removed-repeat window
        # only if its full document is unusable; the committed NOT_USABLE input
        # is provided separately by the pin2 export command.
        records[-1] = open_attempt_record(fx.archived_entry("pin2", "NOT_USABLE", pack="beta"), seal_pins=self.pins)
        for n, variant in enumerate(("NOT_USABLE", "NO_COLLECTION", "NULL", "UNAVAILABLE"), 2):
            record = open_attempt_record(fx.archived_entry("pin3", variant), seal_pins=self.pins)
            # Repeated fixture attempts are history inputs; identity was checked
            # before their public attempt ordinals are assigned for selection.
            self.assertEqual(record.entry.attempt, n)
            records.append(record)
        entry = replace(records[-1].entry, attempt=7, entry_kind="no_archive", archive_root=None,
                        harvest_record_sha256=None, claim_usable=False, record_citation="synthetic-window.md:12")
        records.append(open_attempt_record(entry, seal_pins=self.pins))
        record = self.record("beta")
        records.append(replace(record, entry=replace(record.entry, attempt=6)))
        return records

    def select(self, records):
        return select_analysed_attempts(WindowIndex(tuple(record.entry for record in records)), records)

    def test_beta_history_selects_attempt6(self):
        result = self.select(self.history())
        self.assertEqual(set(result), {"alpha", "beta", "gamma"})
        self.assertEqual(result["beta"].attempt, 6)
        self.assertEqual(result["beta"].record.record_shape, "pin4")

    def test_release_blocked_earlier_attempt_is_undecided(self):
        records = [self.record("alpha"), self.record("gamma"), self.record("beta", release_blocked=True)]
        later = self.record("beta")
        records.append(replace(later, entry=replace(later.entry, attempt=6)))
        with self.assertRaisesRegex(AnalysisRefusal, "^analysed_attempt_undecided$"):
            self.select(records)

    def test_missing_release_blocked_is_undecided(self):
        records = [self.record("alpha"), self.record("gamma"), self.record("beta")]
        earlier = records[-1]
        relative = "derived/exclusions.json"
        path = earlier.entry.archive_root / relative
        row = json.loads(path.read_bytes()); del row["release_blocked"]; fx.put(path, row)
        path = earlier.entry.archive_root / "harvest.json"
        row = json.loads(path.read_bytes()); row["outputs"][relative] = fx.sha(earlier.entry.archive_root / relative); fx.put(path, row)
        records[-1] = open_attempt_record(replace(earlier.entry, harvest_record_sha256=fx.sha(path)), seal_pins=self.pins)
        later = self.record("beta")
        records.append(replace(later, entry=replace(later.entry, attempt=6)))
        with self.assertRaisesRegex(AnalysisRefusal, "^analysed_attempt_undecided$"):
            self.select(records)

    def test_governing_pin_strict_epoch_boundaries(self):
        p = self.pins
        for t0, shape in ((p.erratum_2_epoch_s, "pin2"), (p.erratum_2_epoch_s + .5, "pin3"),
                          (p.erratum_3_epoch_s, "pin3"), (p.erratum_3_epoch_s + .5, "pin4")):
            self.assertEqual(governing_pin(t0, "second"), p.pins[shape]["head"])
            self.assertEqual(governing_pin(t0, "first"), p.pins["pin1"]["head"])
        for t0 in (True, float("nan"), float("inf"), "1791738001", None):
            with self.subTest(t0=t0), self.assertRaises(AnalysisRefusal):
                governing_pin(t0, "second")

    def test_pin4_with_pin2_epoch_is_rejected_at_load(self):
        record = self.record("beta")
        data = {field: getattr(record.entry, field) for field in record.entry.__dataclass_fields__}
        for key, value in tuple(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
        data["t0_epoch_s"] = self.pins.erratum_2_epoch_s
        path = self.root / "index.json"
        fx.put(path, {"schema": "joulewise.b5_window_index.v1", "attempts": [data]})
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_pin_mismatch$"):
            load_window_index(path)

    def test_no_archive_requires_citation_at_load(self):
        record = self.record("beta")
        data = {field: getattr(record.entry, field) for field in record.entry.__dataclass_fields__}
        data.update(entry_kind="no_archive", archive_root=None, harvest_record_sha256=None, claim_usable=False)
        for key, value in tuple(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
        path = self.root / "index.json"
        fx.put(path, {"schema": "joulewise.b5_window_index.v1", "attempts": [data]})
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_record_citation_required$"):
            load_window_index(path)
        data["record_citation"] = "synthetic.md:7"
        fx.put(path, {"schema": "joulewise.b5_window_index.v1", "attempts": [data]})
        entry = load_window_index(path).entries[0]
        record = open_attempt_record(entry, seal_pins=self.pins)
        self.assertEqual((record.kind, record.claim_usable, record.census), ("no_archive", False, ()))

    def test_malformed_pack_is_a_tooling_refusal(self):
        record = self.record("beta")
        data = {field: getattr(record.entry, field) for field in record.entry.__dataclass_fields__}
        for key, value in tuple(data.items()):
            if isinstance(value, Path):
                data[key] = str(value)
        data["pack"] = {"malformed": True}
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
            IndexEntry.from_mapping(data)

    def test_duplicate_attempt_is_refused(self):
        record = self.record("beta")
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_duplicate_attempt$"):
            self.select([record, record])

    def test_block_incomplete_is_refused(self):
        with self.assertRaisesRegex(AnalysisRefusal, "^block_incomplete$"):
            self.select([self.record("alpha"), self.record("beta")])
