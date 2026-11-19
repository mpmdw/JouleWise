"""Exercise the description rail U1 limit on invented native-format rows."""

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from joulewise.cadence_looks import description as reader
from tests import test_desc_looks_acceptance as fixture


def _omit_ane(directory, start, stop, *, announced, poison=False):
    path = directory / "power_trace.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        csv_reader = csv.DictReader(stream)
        fields = csv_reader.fieldnames
        rows = []
        omitted = []
        for row in csv_reader:
            stamp = float(row["interval_start_s"])
            if row["source"] == "powermetrics":
                if row["rail"] == "ane_power" and start <= stamp < stop:
                    omitted.append(float(row["interval_end_s"]) - stamp)
                    continue
                if poison and stamp == stop:
                    row["power_w"] = "DO_NOT_PARSE"
            rows.append(row)
    fixture.put(path, fixture.csvbytes([fields, *(row.values() for row in rows)]))
    support_path = directory / "support.json"
    support = fixture.read(support_path)
    if announced:
        support["rail_missing"] = {"ane_power": [[start, stop]]}
        fixture.put(support_path, support)
    return support, omitted


class RailGapPeriodTests(unittest.TestCase):
    def test_four_second_ane_decode_gap_nulls_turn_and_plateau(self):
        # The round-two witness has sixteen missing 250 ms ANE rows.
        for look in fixture.IDS:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                world = fixture.World(Path(temporary).resolve() / "world", look)
                key = next(iter(world.good))
                directory = world.copy / key
                support = fixture.read(directory / "support.json")
                _, omitted = _omit_ane(directory, support["first_token_s"],
                                       support["last_token_s"], announced=True)
                self.assertEqual(omitted, [0.25] * 16)
                fixture.copy_attestation(world)

                admitted = reader.Snapshot(world.repo, look, "stage1")
                census, _ = reader.census(admitted)
                self.assertEqual(census["counts"]["n_legs"], len(world.good))
                fixture.put(world.stage, reader.canonical(census))
                world.bind()

                snapshot = reader.Snapshot(world.repo, look, "stage2")
                census, qualified = reader.census(snapshot)
                snapshot.check_stage1(census)
                public = snapshot.public_record(census)
                self.assertEqual(public, world.public_truth())
                prints = reader.score(snapshot, reader.verify_gates(snapshot, qualified),
                                      qualified, lambda: None)

                gap = {"value": None, "reason": "rail_gap"}
                energy = prints["turn"][key]["energy_j"]
                self.assertEqual(energy["rail_sum"], gap)
                self.assertIsInstance(energy["gpu_rail"], float)
                self.assertIsInstance(energy["dc_in"], float)
                self.assertEqual(prints["hold"][key]["rail_sum"]["mean_w"], 24.0)
                if world.inst:
                    self.assertEqual(prints["gain"][key]["decode_w"]["rail_sum"], gap)
                else:
                    self.assertEqual(prints["context"]["19458/rail_sum/turn_j"][key]["value"], gap)
                    self.assertEqual(
                        prints["date_spreads"]["19458/rail_sum/turn_j"]["missing"], {"rail_gap": 1},
                    )

    def test_stamp_and_row_checks_share_the_inclusive_phase_limit(self):
        cases = (
            ("hold", 0, 10, 2, 6, False),
            ("turn at limit", 606, 610, 606, 607.25, False),
            ("turn above limit", 606, 610, 606, 607.50, True),
        )
        for name, start, stop, gap_start, gap_stop, wide in cases:
            for announced in (True, False):
                with self.subTest(interval=name, announced=announced), TemporaryDirectory() as tmp:
                    directory = Path(tmp).resolve()
                    fixture.traces(directory, 1, 0)
                    support, _ = _omit_ane(directory, gap_start, gap_stop, announced=announced,
                                           poison=wide)
                    opens = []
                    signal = reader.Signals(support, {"power_trace.csv": directory / "power_trace.csv"},
                                            lambda: opens.append("rail"), None)
                    result = signal.pieces("rail_sum", start, stop)
                    if wide:
                        self.assertEqual(result, {"value": None, "reason": "rail_gap"})
                        self.assertEqual(opens, [] if announced else ["rail"])
                    else:
                        self.assertIsInstance(result, list)
                        self.assertEqual(opens, ["rail"])


if __name__ == "__main__":
    unittest.main()
