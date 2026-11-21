"""Audit 3 recovery-grid reproduction using only invented observations."""

import csv
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from joulewise.cadence_looks import description as reader
from tests import test_desc_looks_acceptance as fixture


class RegisteredRecoveryGridTests(unittest.TestCase):
    def test_dc_cleanliness_cannot_move_the_common_recovery_anchor(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            fixture.traces(folder, 1, 0)
            support = fixture.read(folder / "support.json")
            paths = {name: folder / name for name in (fixture.RAIL_FILE, fixture.DC_FILE)}
            with paths[fixture.DC_FILE].open(newline="") as stream:
                header, *rows = csv.reader(stream)
            fixture.put(paths[fixture.DC_FILE], fixture.csvbytes([
                header, *(row for row in rows if Fraction(row[0]) >= -10),
            ]))
            support["meter_times"] = [time for time in support["meter_times"] if time >= -10]
            support["meter_counts"]["decoded"] = len(support["meter_times"])
            for clean in (True, False):
                with self.subTest(clean=clean):
                    signal = reader.Signals(dict(support, meter_clean=clean), paths,
                                            lambda: None, fixture.fixture_step3())
                    self.assertEqual(signal.recovery_start(), -10 * reader.NS_PER_SECOND)
                    edges = fixture.print_one(signal, fixture.IDS[0])["edges"]
                    self.assertEqual(edges["unobserved_s"], 19)
                    for channel in ("gpu_rail", "rail_sum"):
                        self.assertEqual(edges["recovery_s"][channel], fixture.null("under", bound_s=19))
                    if not clean:
                        self.assertEqual(edges["recovery_s"]["dc_in"], fixture.null("hold_or_sd_undefined"))

    def test_rail_manifest_refusal_cannot_move_the_common_recovery_anchor(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            fixture.traces(folder, 1, 0)
            support = fixture.read(folder / "support.json")
            paths = {name: folder / name for name in (fixture.RAIL_FILE, fixture.DC_FILE)}
            with paths[fixture.RAIL_FILE].open(newline="") as stream:
                header, *rows = csv.reader(stream)
            fixture.put(paths[fixture.RAIL_FILE], fixture.csvbytes([
                header, *(row for row in rows if row[4] == "gpu_power" or Fraction(row[0]) >= -10),
            ]))
            for manifest in (fixture.COLS, fixture.COLS[::-1]):
                signal = reader.Signals(dict(support, rail_manifest=manifest), paths,
                                        lambda: None, fixture.fixture_step3())
                self.assertEqual(signal.recovery_start(), -10 * reader.NS_PER_SECOND)

    def _replay(self, marker):
        with TemporaryDirectory() as directory:
            world = fixture.World(Path(directory).resolve() / "world", fixture.IDS[0])
            key = "f2-inst-03/L002"
            folder = world.copy / key
            support = fixture.read(folder / "support.json")
            rail_file = folder / fixture.RAIL_FILE
            with rail_file.open(newline="") as stream:
                rows = [row for row in csv.DictReader(stream) if not (
                    (row["source"], row["rail"]) == ("powermetrics", "gpu_power")
                    and Fraction(row["interval_start_s"]) == -19
                )]
            fixture.put(rail_file, fixture.csvbytes([
                fixture.RAIL_HEADER, *(tuple(row[field] for field in fixture.RAIL_HEADER) for row in rows),
            ]))
            intervals = {
                name: {(Fraction(row["interval_start_s"]), Fraction(row["interval_end_s"]))
                       for row in rows if (row["source"], row["rail"]) == ("powermetrics", name)}
                for name in fixture.COLS
            }
            gpu = intervals["gpu_power"]
            rail_sum = set.intersection(*intervals.values())
            with (folder / fixture.DC_FILE).open(newline="") as stream:
                first_dc = min(Fraction(row["epoch_s"]) for row in csv.DictReader(stream))
            self.assertEqual((min(gpu)[0], min(rail_sum)[0], first_dc), (-20, -20, -20))
            self.assertEqual([sum(start <= lo < start + 10 for lo, _ in gpu) for start in (-20, -10)],
                             [9, 10])
            shift = support["clock"]["trace_anchor_s"] - support["clock"]["raw_anchor_s"]
            self.assertEqual(support["warmup_stage_raw_s"] + shift - 5, -29)
            self.assertEqual(support["sample_period_s"]["hold"], 1)
            support["sampling_started_raw_s"] = marker - shift
            fixture.put(folder / "support.json", support)
            fixture.copy_attestation(world)

            rc, out, err, events = fixture.invoke(world, "stage1")
            self.assertEqual((rc, out, err), (0, b"", b""))
            self.assertFalse(any(kind == "open" for kind, _ in events))
            world.bind()
            snapshot = reader.Snapshot(world.repo, world.look, "stage2")
            census, qualified = reader.census(snapshot)
            snapshot.check_stage1(census)
            sources = reader.verify_gates(snapshot, qualified)
            return reader.score(snapshot, sources, qualified, lambda: None)["edges"][key]

    def test_registered_grid_is_invariant_to_sampling_marker(self):
        for marker in (-35, -21, -20, -19.5, -15, -10, 0):
            with self.subTest(marker=marker):
                edges = self._replay(marker)
                self.assertEqual(edges["unobserved_s"], 9)
                self.assertEqual(edges["recovery_s"], {
                    "gpu_rail": 19, "rail_sum": 19, "dc_in": fixture.null("under", bound_s=9),
                })
                self.assertEqual(edges["recovery_skipped_windows"],
                                 {"gpu_rail": 1, "rail_sum": 1, "dc_in": 0})
                self.assertEqual(edges["recovery_skip_reasons"],
                                 {"gpu_rail": ["coverage"], "rail_sum": ["coverage"]})

    def test_sampling_marker_alone_cannot_supply_a_recovery_grid(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            fixture.traces(folder, 1, 0)
            support = fixture.read(folder / "support.json")
            support.update(rail_intervals=[], meter_times=[], meter_present=False)
            support["meter_counts"]["decoded"] = 0
            paths = {name: folder / name for name in (fixture.RAIL_FILE, fixture.DC_FILE)}
            fixture.put(paths[fixture.RAIL_FILE], fixture.csvbytes([fixture.RAIL_HEADER]))
            fixture.put(paths[fixture.DC_FILE], fixture.csvbytes([("epoch_s", "watts")]))
            signal = reader.Signals(support, paths, lambda: None, fixture.fixture_step3())
            self.assertIsNone(signal.recovery_start())
            edges = fixture.print_one(signal, fixture.IDS[0])["edges"]
            self.assertEqual(edges["unobserved_s"], 9)
            self.assertEqual(edges["recovery_s"],
                             dict.fromkeys(fixture.CHANNEL, fixture.null("hold_or_sd_undefined")))
            self.assertEqual(edges["recovery_skipped_windows"], dict.fromkeys(fixture.CHANNEL, 0))


if __name__ == "__main__":
    unittest.main()
