"""Audit the shared value-access boundary with invented sample streams."""

import ast
import csv
from itertools import product
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

from joulewise.cadence_looks import description as reader
from tests import test_desc_looks_acceptance as fixture


RAIL_FOR_CHANNEL = {
    "cpu_rail": "cpu_power", "gpu_rail": "gpu_power", "ane_rail": "ane_power",
    "rail_sum": "ane_power",
}
INTERVALS = {
    "turn": (700, 710), "decode": (704, 710), "hold": (0, 600), "recovery": (-10, 0),
}
SAMPLE_COUNT = 1000


def _interval_grid(start, stop, gap=False):
    def stamp(index):
        return start + (stop - start) * index / SAMPLE_COUNT

    if not gap:
        return [(stamp(i), stamp(i + 1)) for i in range(SAMPLE_COUNT)]
    # Pack the same number of points on either side of a deliberate gap.
    bounds = []
    for index in range(SAMPLE_COUNT):
        left = index / 2 + (500 if index >= 500 else 0)
        bounds.append((stamp(left), stamp(left + 0.5)))
    return bounds


def _matrix_signal(root, interval, channel, present, gap, pinned, *, losses=None):
    a, b = interval
    period = (b - a) / SAMPLE_COUNT
    common = _interval_grid(a, b)
    affected = _interval_grid(a, b, gap)
    removed = SAMPLE_COUNT - present
    omitted = {i * SAMPLE_COUNT // removed + 1 for i in range(removed)} if removed else set()
    kept = [bounds for i, bounds in enumerate(affected) if i not in omitted]
    rails = affected if channel in RAIL_FOR_CHANNEL else common
    if losses is None:
        target = RAIL_FOR_CHANNEL.get(channel)
        losses = {target: omitted} if target else {}
    missing = {rail: [rails[i] for i in sorted(indices)] for rail, indices in losses.items()}
    meter = kept if channel == "dc_in" else common
    sidecar = kept if channel == "sidecar" else common
    samples = [start for start, _ in meter] + [b]
    support = {
        "turn_start_s": 700, "sample_period_s": {"hold": period, "rail_edge": period,
                                               "dc_edge": period},
        "sidecar_times": [start for start, _ in sidecar] + [b],
        "meter_times": samples, "meter_present": True, "meter_clean": True,
        "meter_counts": {"decoded": len(samples), "bad": 0, "usb_errors": 0},
        "rail_intervals": rails, "rail_manifest": fixture.COLS, "rail_missing": missing,
        "sensors": [{"fan_keys": {"left": 900}, "TV0h": 35}],
    }
    paths = {file: root / file for file in ("power_trace.csv", "dc_points.csv")}
    fixture.put(paths["power_trace.csv"], fixture.csvbytes([
        ("interval_start_s", "interval_end_s", "timestamp_s", "source", "rail", "power_w"),
        *((start, stop, stop, "powermetrics", rail, 1)
          for i, (start, stop) in enumerate(rails) for rail in fixture.COLS
          if i not in losses.get(rail, ())),
    ]))
    fixture.put(paths["dc_points.csv"], fixture.csvbytes([
        ("epoch_s", "watts"), *((stamp, 1) for stamp in samples),
    ]))
    opens = []
    return reader.Signals(support, paths, lambda: opens.append(True), pinned), opens


def _filter_csv(path, keep):
    with path.open(encoding="utf-8", newline="") as stream:
        rows = csv.DictReader(stream)
        output = [rows.fieldnames, *(list(row.values()) for row in rows if keep(row))]
    fixture.put(path, fixture.csvbytes(output))
    return output[1:]


class DescriptionIntervalTests(unittest.TestCase):
    def test_channel_interval_and_fraction_matrix(self):
        pinned = reader.step3_reader()
        for channel, label, present, gap in product(
            (*RAIL_FOR_CHANNEL, "dc_in", "sidecar"), INTERVALS, (1000, 990, 989, 500), (False, True),
        ):
            with self.subTest(channel=channel, interval=label, present=present, gap=gap):
                with TemporaryDirectory() as temporary:
                    bounds = INTERVALS[label]
                    signals, opens = _matrix_signal(Path(temporary), bounds, channel, present, gap,
                                                    pinned)
                    if channel == "sidecar":
                        readings = signals.interval_values(channel, bounds)
                        value, _ = reader._sensors(["left"], readings)
                    else:
                        value = signals.average(channel, *bounds)
                    if present < 990 or gap:
                        reason = "coverage" if present < 990 else "meter_gap"
                        self.assertEqual(value, {"value": None, "reason": reason})
                        self.assertEqual(opens, [])
                    else:
                        self.assertIsInstance(value, (int, float))
                        self.assertEqual(opens, [] if channel == "sidecar" else [True])

    def test_rail_sum_requires_admitted_components_and_complete_groups(self):
        bounds = INTERVALS["turn"]
        with TemporaryDirectory() as temporary:
            signals, _ = _matrix_signal(
                Path(temporary), bounds, "rail_sum", 1000, False, reader.step3_reader(),
                losses={"cpu_power": set(range(10, 20)), "ane_power": set(range(30, 40))},
            )
            for channel in ("cpu_rail", "gpu_rail", "ane_rail"):
                self.assertIsInstance(signals.average(channel, *bounds), float)
            self.assertEqual(signals.average("rail_sum", *bounds),
                             {"value": None, "reason": "coverage"})

    def test_round_four_probe_on_instrument_and_stability(self):
        coverage = {"value": None, "reason": "coverage"}
        for look in fixture.IDS[:2]:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                world = fixture.World(Path(temporary).resolve() / "world", look)
                first, second = list(world.good)[:2]
                missing_rail = world.copy / first
                support = fixture.read(missing_rail / "support.json")
                point = support["first_token_s"] + 1
                rows = _filter_csv(missing_rail / "power_trace.csv", lambda row: not (
                    row["source"] == "powermetrics" and row["rail"] == "gpu_power"
                    and float(row["interval_start_s"]) == point
                ))
                self.assertEqual(sum(602 <= float(row[0]) < 611 and row[3:5] ==
                                     ["powermetrics", "gpu_power"] for row in rows), 35)
                support["rail_missing"] = {"gpu_power": [[point, point + 0.25]]}
                fixture.put(missing_rail / "support.json", support)

                sparse = world.copy / second
                support = fixture.read(sparse / "support.json")
                support["sidecar_times"] = [stamp for stamp in support["sidecar_times"]
                                            if not (0 <= stamp < 600 and int(stamp) % 2)]
                self.assertEqual(sum(0 <= stamp < 600 for stamp in support["sidecar_times"]), 300)
                rows = _filter_csv(sparse / "dc_points.csv",
                                   lambda row: not 606 <= float(row["epoch_s"]) < 609)
                support["meter_times"] = [float(row[0]) for row in rows]
                support["meter_counts"]["decoded"] = len(rows)
                self.assertEqual(sum(602 <= stamp < 611 for stamp in support["meter_times"]), 120)
                fixture.put(sparse / "support.json", support)
                fixture.copy_attestation(world)
                fixture.Checks().stage1(world)

                snapshot = reader.Snapshot(world.repo, look, "stage2")
                census, qualified = reader.census(snapshot)
                snapshot.check_stage1(census)
                self.assertEqual(snapshot.public_record(census), world.public_truth())
                sources = reader.verify_gates(snapshot, qualified)
                isolated = reader.Signals(support, sources[second],
                                          lambda: self.fail("rejected DC interval opened"), None)
                self.assertEqual(isolated.interval_values("dc_in", (602, 611)), coverage)
                output = reader.score(snapshot, sources, qualified, lambda: None)
                for channel in ("gpu_rail", "rail_sum"):
                    self.assertEqual(output["turn"][first]["energy_j"][channel], coverage)
                    if world.inst:
                        self.assertEqual(output["gain"][first]["decode_w"][channel], coverage)
                for channel in fixture.CHANNEL:
                    self.assertEqual(output["hold"][second][channel]["mean_w"], coverage)
                if world.inst:
                    self.assertEqual(output["gain"][second]["mean_fan_rpm"], coverage)

    def test_scoring_modules_grep_for_value_access_outside_interval_values(self):
        root = Path(__file__).resolve().parents[1]
        module = root / "joulewise/cadence_looks"
        sources = (module / "description.py", module / "description_worker.py",
                   root / "scripts/cadence_description_run.py")
        raw = re.compile(r'\b(?:_rail_tokens|_meter_tokens|_rail_rows|load_gpu_trace)\b'
                         r'|\[["\'](?:power_w|watts|sensors)["\']\]')
        stamps = re.compile(r'\.(?:sidecar|meter)\b|\[["\'](?:sidecar_times|meter_times)["\']\]')
        io = re.compile(r'\b(?:open|read_bytes|read_text)\(')
        structural_io = {
            "description.py": {"working", "validate_manifest", "_step3_code",
                               "_validate_executables"},
            "description_worker.py": {"_candidate", "_write_private"},
        }
        for source in sources:
            body = source.read_text()
            functions = [node for node in ast.walk(ast.parse(body))
                         if isinstance(node, ast.FunctionDef)]
            for line_no, line in enumerate(body.splitlines(), 1):
                scope = min((node for node in functions if node.lineno <= line_no <= node.end_lineno),
                            key=lambda node: node.end_lineno - node.lineno, default=None)
                owner = scope.name if scope else ""
                with self.subTest(file=source.name, line=line_no):
                    if raw.search(line):
                        permitted = (owner == "interval_values"
                                     or owner == "_rail_rows"  # Tokenizer called only by the gateway.
                                     or owner == "__init__" and line.strip().endswith(" = None"))
                        self.assertTrue(permitted, line)
                    if stamps.search(line):
                        self.assertIn(owner, {"__init__", "_interval_refusal", "interval_values"},
                                      line)
                    if io.search(line):
                        support_only = owner == "score" and line.strip() == (
                            'support = decode(paths["support.json"].read_bytes())'
                        )
                        self.assertTrue(owner == "interval_values" or support_only
                                        or owner in structural_io.get(source.name, ()), line)


if __name__ == "__main__":
    unittest.main()
