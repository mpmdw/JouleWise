"""Window API boundaries using fabricated, citation-only attempts."""
from dataclasses import replace
from pathlib import Path
import unittest

from joulewise.b5_analysis.archive import open_attempt_record
from joulewise.b5_analysis.windows import AnalysisRefusal, IndexEntry, SealPins, governing_pin


PACK_TABLE = {"alpha": {"synthetic-alpha": "synthetic-alpha-plan"}}


class WindowBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.pins = SealPins.load()

    def mapping(self, **changes):
        row = dict(pack="alpha", pack_id="synthetic-alpha", plan_id="synthetic-alpha-plan", attempt=1,
            t0_epoch_s=self.pins.erratum_3_epoch_s + 2, seal="second", entry_kind="no_archive",
            archive_root=None, harvest_record_sha256=None, superseded_archive_roots=[],
            claim_runs_root="/synthetic/claim", bound_runs_root="/synthetic/bound",
            custody_root="/synthetic/custody", measurement_root="/synthetic/measurement",
            harvest_pin=self.pins.pins["pin4"]["head"], verdict="NO_COLLECTION", claim_usable=False,
            record_citation="synthetic-window.md:1")
        return {**row, **changes}

    def parse(self, **changes):
        return IndexEntry.from_mapping(self.mapping(**changes), seal_pins=self.pins, pack_table=PACK_TABLE)

    def test_attempts_start_at_one(self):
        """Attempt 1 accepts; zero and negative attempts refuse. Kills M05516."""
        self.assertEqual(self.parse(attempt=1).attempt, 1)
        for attempt in (0, -1):
            with self.subTest(attempt=attempt), self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
                self.parse(attempt=attempt)

    def test_requested_g10_allows_zero_and_one_redraws(self):
        """G10 redraws are nonnegative, including zero. Kills M05590, M05591."""
        for count in (0, 1):
            with self.subTest(count=count):
                entry = self.parse(g10_requested=True, g10_redraw_cycles=count)
                self.assertEqual(entry.g10_redraw_cycles, count)
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
            self.parse(g10_requested=True, g10_redraw_cycles=-1)

    def test_record_reader_revalidates_superseded_paths_on_typed_entries(self):
        """The public typed-entry reader refuses relative superseded roots. Kills M05640."""
        entry = self.parse(superseded_archive_roots=["/synthetic/old-archive"])
        record = open_attempt_record(entry, seal_pins=self.pins, pack_table=PACK_TABLE)
        self.assertEqual(record.kind, "no_archive")
        # IndexEntry is also constructed/replaced directly by public callers;
        # open_attempt_record revalidates it without going through from_mapping.
        invalid = replace(entry, superseded_archive_roots=(Path("relative-archive"),))
        with self.assertRaisesRegex(AnalysisRefusal, "^window_index_invalid$"):
            open_attempt_record(invalid, seal_pins=self.pins, pack_table=PACK_TABLE)

    def test_positive_epoch_api_includes_the_first_second(self):
        """Positive epoch .5 and 1.0 select the historical pins. Kills M05490."""
        # governing_pin and its index callers define a finite, strictly positive
        # epoch domain; no registration or caller imposes a >=2 s lower bound.
        for stamp in (.5, 1.):
            for seal, shape in (("first", "pin1"), ("second", "pin2")):
                with self.subTest(stamp=stamp, seal=seal):
                    self.assertEqual(governing_pin(stamp, seal, seal_pins=self.pins),
                                     self.pins.pins[shape]["head"])
