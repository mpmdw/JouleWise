"""Exercise the description rail U1 limit on invented native-format rows."""

import csv
from decimal import Decimal
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import description as reader
from tests import test_desc_looks_acceptance as fixture
from tests.fixtures.description_worlds import DescriptionWorld


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


def _with_rail_intervals(directory, rows):
    fixture.put(directory / fixture.RAIL_FILE, fixture.csvbytes([
        fixture.RAIL_HEADER, *(tuple(row[field] for field in fixture.RAIL_HEADER) for row in rows),
    ]))
    support_path = directory / "support.json"
    support = fixture.read(support_path)
    bounds = sorted({(Decimal(row["interval_start_s"]), Decimal(row["interval_end_s"]))
                     for row in rows if row["source"] == "powermetrics"})
    support["rail_intervals"] = [[float(left), float(right)] for left, right in bounds]
    fixture.put(support_path, support)
    return support


class RailGapPeriodTests(unittest.TestCase):
    def test_authenticated_scorers_refuse_support_that_omits_a_recorded_interval(self):
        with patch.object(reader.socket, "gethostname", return_value=fixture.FIXTURE_BOARD), \
                patch.dict(os.environ, R190_NODENAME=fixture.FIXTURE_BOARD):
            for look in fixture.IDS[:2]:
                with self.subTest(look=look), TemporaryDirectory() as temporary:
                    world = DescriptionWorld(Path(temporary).resolve() / "world", look)
                    key = sorted(world.good)[0]
                    folder = world.copy / key
                    path = folder / fixture.RAIL_FILE
                    with path.open(newline="") as stream:
                        rows = list(csv.DictReader(stream))
                    for row in rows:
                        start = Decimal(row["interval_start_s"])
                        if row["source"] == "powermetrics" and 0 <= start < 600:
                            row["power_w"] = "601" if start == 50 else "1"
                    support = _with_rail_intervals(folder, rows)
                    clean = reader.Signals(support, {fixture.RAIL_FILE: path}, lambda: None,
                                           fixture.fixture_step3())
                    self.assertEqual(clean.average("gpu_rail", 0, 600), 2)
                    self.assertEqual(clean.average("rail_sum", 0, 600), 6)

                    support["rail_intervals"].remove([50, 51])
                    fixture.put(folder / "support.json", support)
                    fixture.copy_attestation(world)
                    world.commit_stage1(self)
                    snapshot = reader.Snapshot(world.repo, look, "stage2")
                    census, qualified = reader.census(snapshot)
                    snapshot.check_stage1(census)
                    sources = reader.verify_gates(snapshot, qualified)
                    with self.assertRaisesRegex(reader.Refusal, "recorded rail interval contradicts support"):
                        reader.score(snapshot, sources, qualified, lambda: None)

    def test_recorded_rail_evidence_rejects_omit_duplicate_shift_and_false_gap(self):
        with TemporaryDirectory() as temporary:
            folder = Path(temporary)
            fixture.traces(folder, 1, 0)
            paths = {fixture.RAIL_FILE: folder / fixture.RAIL_FILE}
            support = fixture.read(folder / "support.json")
            bounds = support["rail_intervals"]
            # The first admitted rail window must validate all recorded rail
            # metadata, including the intervals used by later prints.
            for start in (-15, 50, 603.25, 607.25, 610.25):
                index = next(i for i, pair in enumerate(bounds) if pair[0] == start)
                left, right = bounds[index]
                replacements = {
                    "omitted": [],
                    "duplicate": [[left, right], [left, right]],
                    "shifted": [[left, right - 0.000000001]],
                }
                for name, replacement in replacements.items():
                    with self.subTest(start=start, change=name):
                        edited = bounds[:index] + replacement + bounds[index + 1:]
                        message = ("invalid support interval ledger" if name == "duplicate"
                                   else "recorded rail interval contradicts support")
                        with self.assertRaisesRegex(reader.Refusal, message):
                            signal = reader.Signals(dict(support, rail_intervals=edited), paths,
                                                    lambda: None, None)
                            signal.average("gpu_rail", 0, 600)
                for rail in fixture.COLS:
                    with self.subTest(start=start, rail=rail, change="false gap"):
                        edited = dict(support, rail_missing={rail: [[left, right]]})
                        signal = reader.Signals(edited, paths, lambda: None, None)
                        with self.assertRaisesRegex(reader.Refusal, "recorded rail interval contradicts support"):
                            signal.average("gpu_rail", 0, 600)

    def test_rail_sum_joins_exact_intervals_at_the_coverage_boundary(self):
        with TemporaryDirectory() as temporary:
            folder = Path(temporary)
            fixture.traces(folder, 1, 0)
            paths = {fixture.RAIL_FILE: folder / fixture.RAIL_FILE}
            pinned = fixture.fixture_step3()
            for changed in (0, 1, 2):
                with self.subTest(changed=changed):
                    rows = []
                    for i in range(100):
                        for rail, watts in zip(fixture.COLS, (1, 2, 3)):
                            end = Decimal(i + 1)
                            if rail == "ane_power" and 50 <= i < 50 + changed:
                                end -= Decimal("0.000000001")
                            rows.append(dict(zip(fixture.RAIL_HEADER,
                                                 (i, end, end, "powermetrics", rail, watts))))
                    support = _with_rail_intervals(folder, rows)
                    signal = reader.Signals(support, paths, lambda: None, pinned)
                    self.assertEqual(signal.average("gpu_rail", 0, 100), 2)
                    self.assertEqual(signal.average("rail_sum", 0, 100),
                                     (6, 5.94, fixture.null("coverage"))[changed])

            # A single rail may not contribute overlapping intervals.
            rows.append(dict(zip(fixture.RAIL_HEADER,
                                 (50, "51", "51", "powermetrics", "ane_power", "DO_NOT_PARSE"))))
            support = _with_rail_intervals(folder, rows)
            signal = reader.Signals(support, paths, lambda: None, pinned)
            with self.assertRaisesRegex(reader.Refusal, "overlapping intervals for one rail"):
                signal.average("rail_sum", 0, 100)

    def test_authenticated_scorers_keep_gpu_when_rail_intervals_do_not_join(self):
        with patch.object(reader.socket, "gethostname", return_value=fixture.FIXTURE_BOARD), \
                patch.dict(os.environ, R190_NODENAME=fixture.FIXTURE_BOARD):
            for look in fixture.IDS[:2]:
                with self.subTest(look=look), TemporaryDirectory() as temporary:
                    world = DescriptionWorld(Path(temporary).resolve() / "world", look)
                    key = sorted(world.good)[0]
                    folder = world.copy / key
                    with (folder / fixture.RAIL_FILE).open(newline="") as stream:
                        rows = list(csv.DictReader(stream))
                    changes = {50, 120, 190, 260, 330, 400, 470}
                    for row in rows:
                        if ((row["source"], row["rail"]) == ("powermetrics", "ane_power")
                                and Decimal(row["interval_start_s"]) in changes):
                            end = Decimal(row["interval_end_s"]) - Decimal("0.000000001")
                            row["interval_end_s"] = row["timestamp_s"] = str(end)
                    _with_rail_intervals(folder, rows)
                    fixture.copy_attestation(world)
                    world.commit_stage1(self)
                    snapshot = reader.Snapshot(world.repo, look, "stage2")
                    census, qualified = reader.census(snapshot)
                    snapshot.check_stage1(census)
                    self.assertEqual(snapshot.public_record(census), world.public_truth())
                    sources = reader.verify_gates(snapshot, qualified)
                    hold = reader.score(snapshot, sources, qualified, lambda: None)["hold"][key]
                    self.assertEqual(hold["gpu_rail"]["mean_w"], 12 * world.good[key][0])
                    self.assertEqual(hold["rail_sum"]["mean_w"], fixture.null("coverage"))

    def test_four_second_ane_decode_gap_nulls_turn_and_plateau(self):
        # The round-two witness has sixteen missing 250 ms ANE rows.
        for look in fixture.IDS:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                world = DescriptionWorld(Path(temporary).resolve() / "world", look)
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
                prints = world.full_roster_prints(prints)

                gap = {"value": None, "reason": "coverage"}
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
                        prints["date_spreads"]["19458/rail_sum/turn_j"]["missing"], {"coverage": 1},
                    )

    def test_stamp_and_row_checks_reject_undercount_before_decoding(self):
        cases = (
            ("hold", 0, 10, 2, 6),
            ("turn at gap limit", 606, 610, 606, 607.25),
            ("turn above gap limit", 606, 610, 606, 607.50),
        )
        for name, start, stop, gap_start, gap_stop in cases:
            for announced in (True, False):
                with self.subTest(interval=name, announced=announced), TemporaryDirectory() as tmp:
                    directory = Path(tmp).resolve()
                    fixture.traces(directory, 1, 0)
                    support, _ = _omit_ane(directory, gap_start, gap_stop, announced=announced,
                                           poison=True)
                    opens = []
                    signal = reader.Signals(support, {"power_trace.csv": directory / "power_trace.csv"},
                                            lambda: opens.append("rail"), None)
                    result = signal.interval_values("rail_sum", (start, stop))
                    self.assertEqual(result, {"value": None, "reason": "coverage"})
                    self.assertEqual(opens, [] if announced else ["rail"])

    def test_full_sample_count_still_requires_the_turn_gap_limit(self):
        for gap, accepted in ((1.25, True), (1.50, False)):
            with self.subTest(gap=gap), TemporaryDirectory() as temporary:
                directory = Path(temporary).resolve()
                fixture.traces(directory, 1, 0)
                support = fixture.read(directory / "support.json")
                span = (4 - gap) / 2
                # Sixteen starts satisfy the count while packing the intervals
                # into two groups leaves the requested gap between them.
                intervals = [(start + i * span / 8, start + (i + 1) * span / 8)
                             for start in (606, 606 + span + gap) for i in range(8)]
                support["rail_intervals"] = intervals
                path = directory / "power_trace.csv"
                fixture.put(path, fixture.csvbytes([
                    ("interval_start_s", "interval_end_s", "timestamp_s", "source",
                     "rail", "power_w"),
                    *((a, b, b, "powermetrics", rail, 1)
                      for a, b in intervals for rail in fixture.COLS),
                ]))
                opens = []
                signal = reader.Signals(support, {"power_trace.csv": path},
                                        lambda: opens.append(True), fixture.fixture_step3())
                value = signal.interval_values("rail_sum", (606, 610))
                self.assertEqual(opens, [True])  # Verify observed identities before the gap.
                if accepted:
                    self.assertEqual(len(value), 16)
                else:
                    self.assertEqual(value, {"value": None, "reason": "meter_gap"})


if __name__ == "__main__":
    unittest.main()
