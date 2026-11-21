"""Check per-print DC sample admission with invented, byte-attested streams."""

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import description as reader
from tests import test_desc_looks_acceptance as fixture
from tests.fixtures.description_worlds import DescriptionWorld


def _select_meter_points(directory, keep, *, poison=None):
    path = directory / "dc_points.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        rows = csv.DictReader(stream)
        selected = [rows.fieldnames]
        stamps = []
        for row in rows:
            stamp = float(row["epoch_s"])
            if keep(stamp):
                stamps.append(stamp)
                if stamp == poison:
                    row["watts"] = "DO_NOT_PARSE"
                selected.append(list(row.values()))
    fixture.put(path, fixture.csvbytes(selected))

    support_path = directory / "support.json"
    support = fixture.read(support_path)
    support["meter_times"] = stamps
    support["meter_counts"]["decoded"] = len(stamps)
    fixture.put(support_path, support)
    return support


class DCCoverageTests(unittest.TestCase):
    def test_dc_recording_detects_omitted_stamp_even_when_decoder_count_disagrees(self):
        with TemporaryDirectory() as temporary:
            leg = fixture.TraceLeg(Path(temporary))
            leg.meta["meter_times"].remove(50)
            self.assertNotEqual(leg.meta["meter_counts"]["decoded"], len(leg.meta["meter_times"]))
            with patch.object(reader, "_sample", side_effect=AssertionError("value parsed before reconciliation")):
                reports = fixture.print_one(leg.signal(), fixture.IDS[0])
            self.assertEqual(reports, dict.fromkeys(("hold", "turn", "gain", "edges"),
                                                    fixture.null("interval_ledger_mismatch")))

    def test_sparse_clean_stream_reports_interval_coverage_before_value_access(self):
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            paths = {fixture.DC_FILE: directory / fixture.DC_FILE}
            for count in (0, 1, 2):
                with self.subTest(decoded=count):
                    fixture.traces(directory, 1, 0)
                    support = _select_meter_points(directory, lambda t: 0 <= t < count, poison=0)
                    self.assertEqual(support["meter_counts"]["decoded"], count)
                    self.assertTrue(support["meter_present"] and support["meter_clean"])
                    for clean in (True, False):
                        with self.subTest(clean=clean):
                            support["meter_clean"] = clean
                            opens = []
                            signal = reader.Signals(support, paths, lambda: opens.append(True), None)
                            reason = "coverage" if clean else "meter_contaminated"
                            self.assertEqual(signal.average("dc_in", 0, 100), fixture.null(reason))
                            self.assertEqual(opens, [])

    def test_span_trailer_fault_counts_do_not_contaminate_clean_dc_intervals(self):
        for look in fixture.IDS[:2]:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                world = DescriptionWorld(Path(temporary).resolve() / "world", look)
                expected = {}
                for key, counter in zip(world.good, ("bad", "usb_errors")):
                    path = world.copy / key / "support.json"
                    support = fixture.read(path)
                    stamps = [t for t in support["meter_times"] if 0 <= t < 600]
                    self.assertEqual(stamps, list(range(600)))
                    self.assertTrue(support["meter_present"] and support["meter_clean"])
                    self.assertEqual(support["meter_counts"][counter], 0)
                    support["meter_counts"][counter] = 1
                    fixture.put(path, support)
                    expected[key] = 40 * world.good[key][0]
                fixture.copy_attestation(world)
                world.commit_stage1(self)
                snapshot = reader.Snapshot(world.repo, look, "stage2")
                census, qualified = reader.census(snapshot)
                snapshot.check_stage1(census)
                sources = reader.verify_gates(snapshot, qualified)
                report = reader.score(snapshot, sources, qualified, lambda: None)
                report = world.full_roster_prints(report)
                for key, watts in expected.items():
                    with self.subTest(key=key):
                        mean = report["hold"][key]["dc_in"]["mean_w"]
                        self.assertIsInstance(mean, (int, float))
                        self.assertAlmostEqual(mean, watts)
                        self.assertEqual(report["hold"][key]["dc_in"]["dropped"], [0, 0, 0])

    def test_sparse_decode_nulls_dc_turn_and_plateau_even_with_short_gaps(self):
        for look in fixture.IDS:
            with self.subTest(look=look), TemporaryDirectory() as directory:
                world = DescriptionWorld(Path(directory).resolve() / "world", look)
                key = next(iter(world.good))
                copy = world.copy / key
                original = fixture.read(copy / "support.json")
                first, last = original["first_token_s"], original["last_token_s"]
                support = _select_meter_points(
                    copy, lambda t: t < first or t > last or (2 * t).is_integer(),
                )
                turn_start = support["turn_start_s"]
                stamps = support["meter_times"]
                decode = [t for t in stamps if first <= t <= last]
                self.assertEqual(sum(first <= t < last for t in stamps), 8)
                self.assertEqual(sum(turn_start <= t < last + 1 for t in stamps), 108)
                self.assertEqual(max(b - a for a, b in zip(decode, decode[1:])), 0.5)
                fixture.copy_attestation(world)
                world.commit_stage1(self)

                snapshot = reader.Snapshot(world.repo, look, "stage2")
                census, qualified = reader.census(snapshot)
                snapshot.check_stage1(census)
                self.assertEqual(snapshot.public_record(census), world.public_truth())
                prints = reader.score(snapshot, reader.verify_gates(snapshot, qualified),
                                      qualified, lambda: None)
                prints = world.full_roster_prints(prints)

                missing = {"value": None, "reason": "coverage"}
                self.assertEqual(prints["hold"][key]["dc_in"]["mean_w"], 40.0)
                energy = prints["turn"][key]["energy_j"]
                if world.inst:
                    self.assertEqual(prints["gain"][key]["decode_w"]["dc_in"], missing)
                else:
                    cell = "19458/dc_in/turn_j"
                    self.assertEqual(prints["context"][cell][key]["value"], missing)
                    self.assertEqual(prints["date_spreads"][cell]["missing"], {"coverage": 1})
                self.assertEqual(energy["dc_in"], missing)
                self.assertIsInstance(energy["gpu_rail"], float)
                self.assertIsInstance(energy["rail_sum"], float)

    def test_half_open_sample_count_uses_nominal_cadence_before_value_access(self):
        cases = (
            ("hold at 99%", 0, 100, {50}, 99, True),
            ("hold below 99%", 0, 100, {50, 60}, 98, False),
            ("turn at 99%", 602, 607, {604}, 99, True),
            ("turn below 99%", 602, 607, {604, 605}, 98, False),
            ("mixed at nominal rate", 600, 606, set(), 82, True),
            ("mixed below 99%", 600, 606, {604}, 81, False),
        )
        for name, start, stop, omitted, count, admitted in cases:
            with self.subTest(interval=name), TemporaryDirectory() as temporary:
                directory = Path(temporary).resolve()
                fixture.traces(directory, 1, 0)
                support = _select_meter_points(directory, lambda t: t not in omitted,
                                               poison=None if admitted else start)
                stamps = support["meter_times"]
                self.assertIn(stop, stamps)  # Available to bracket the end, outside [start, stop).
                self.assertEqual(sum(start <= t < stop for t in stamps), count)
                opens = []
                signal = reader.Signals(support, {"dc_points.csv": directory / "dc_points.csv"},
                                        lambda: opens.append("meter"), None)
                if admitted:
                    self.assertIsInstance(signal.energy("dc_in", start, stop), float)
                    self.assertEqual(opens, ["meter"])
                else:
                    self.assertEqual(signal.energy("dc_in", start, stop),
                                     {"value": None, "reason": "coverage"})
                    self.assertEqual(opens, [])


if __name__ == "__main__":
    unittest.main()
