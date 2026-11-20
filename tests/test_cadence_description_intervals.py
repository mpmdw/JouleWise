"""Audit the shared value-access boundary with invented sample streams."""

import ast
import csv
from decimal import Decimal
from fractions import Fraction
import io
from itertools import product
import json
from pathlib import Path
from random import Random
import re
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

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


def _score_world(world):
    fixture.copy_attestation(world)
    fixture.Checks().stage1(world)
    snapshot = reader.Snapshot(world.repo, world.look, "stage2")
    census, qualified = reader.census(snapshot)
    snapshot.check_stage1(census)
    sources = reader.verify_gates(snapshot, qualified)
    return reader.score(snapshot, sources, qualified, lambda: None)


class DescriptionIntervalTests(unittest.TestCase):
    def test_flat_gpu_has_zero_above_hold_and_no_gain(self):
        with TemporaryDirectory() as temporary:
            leg = fixture.TraceLeg(Path(temporary))
            for row in leg.rows[fixture.RAIL_FILE]:
                if row["source"] == "powermetrics" and row["rail"] == "gpu_power":
                    row["power_w"] = "2.042"
            printed = fixture.print_one(leg.signal(), fixture.IDS[0])
            self.assertEqual(printed["turn"]["energy_j"]["gpu_rail"], 0)
            self.assertEqual(printed["gain"]["decode_w"]["gpu_rail"], 0)
            self.assertEqual(printed["gain"]["long_prefill_w"]["gpu_rail"], 0)
            ratio = printed["gain"]["decode_gain"]["gpu_rail"]
            self.assertGreater(ratio["numerator"], 0)
            self.assertEqual(ratio["denominator"], 0)
            self.assertIsNone(ratio["value"])
            self.assertEqual(ratio["reason"], "nonpositive_denominator")

    def test_flat_power_identity_over_permitted_gap_patterns(self):
        random = Random(191)
        levels = [2.042, *(random.uniform(-1000, 1000) for _ in range(199))]
        hold = [(i / 2, (i + 1) / 2) for i in range(8)]
        turn = [(i / 2, (i + 1) / 2) for i in range(8, 16)]
        periods = dict.fromkeys(("hold", "rail_edge", "dc_edge"), 0.5)
        masks = list(product((False, True), repeat=3))
        with TemporaryDirectory() as temporary:
            folder = Path(temporary)
            for level, rail_mask, dc_mask in product(levels, masks, masks):
                with self.subTest(level=level, rail_mask=rail_mask, dc_mask=dc_mask):
                    leading, middle, trailing = rail_mask
                    spans = turn.copy()
                    if leading:
                        spans[0] = (4.125, 4.5)
                    if middle:
                        spans[4] = (6.125, 6.5)
                    if trailing:
                        spans[-1] = (7.5, 7.875)
                    stamps = [i / 2 for i in range(17)]
                    for flag, i in zip(dc_mask, (8, 12, 16)):
                        if flag:
                            stamps[i] += 0.125
                    signal, _ = fixture.raw_fixture(
                        folder, {rail: [(a, b, level) for a, b in hold + spans] for rail in fixture.COLS},
                        [(stamp, level) for stamp in stamps], [i / 2 for i in range(17)],
                        turn_start_s=4, sample_period_s=periods,
                    )
                    levels_above_hold = {}
                    for channel in fixture.CHANNEL:
                        reference = signal.average(channel, 0, 4, exact=True)
                        self.assertEqual(reference, Fraction(level) * (3 if channel == "rail_sum" else 1))
                        energy = reader._above_hold(signal, channel, reference, 4_000_000_000,
                                                    8_000_000_000, average=False)
                        self.assertIsInstance(energy, Fraction)
                        self.assertEqual(energy, 0)
                        levels_above_hold[channel] = energy
                    for ratio in reader._ratios(levels_above_hold).values():
                        self.assertEqual(ratio, dict(fixture.null("nonpositive_denominator"),
                                                     numerator=0, denominator=0))

    def test_rail_return_uses_capture_end_when_scored_rails_drop_out(self):
        for sparse in (False, True):
            with self.subTest(sparse=sparse), TemporaryDirectory() as temporary:
                leg = fixture.TraceLeg(Path(temporary))
                for row in leg.rows[fixture.RAIL_FILE].copy():
                    if row["source"] != "powermetrics":
                        continue
                    start = float(row["interval_start_s"])
                    if start == 610.25:
                        row["power_w"] = "0"
                    if row["rail"] == "gpu_power" and start in (610.5, 610.75):
                        leg.rows[fixture.RAIL_FILE].append(dict(row, rail="dram_power", power_w="1"))
                if sparse:
                    for rail in fixture.COLS:
                        leg.omit(rail, [610.5, 610.75])
                edges = fixture.print_one(leg.signal(), fixture.IDS[0])["edges"]
                expect = fixture.null("coverage", bound_s=1) if sparse else 0.25
                self.assertEqual(edges["rail_return_censor_s"], dict.fromkeys(fixture.CHANNEL[:2], expect))

    def test_stability_keeps_a_date_with_only_refused_observations(self):
        with TemporaryDirectory() as temporary:
            world = fixture.World(Path(temporary).resolve() / "world", fixture.IDS[1])
            key = "f2-stab-06/L001"
            path = world.copy / key / "support.json"
            support = fixture.read(path)
            support["sidecar_times"] = [stamp for stamp in support["sidecar_times"] if stamp not in range(10, 80, 10)]
            fixture.put(path, support)
            output = _score_world(world)
            cell, day = "19458/gpu_rail/mean_w", "2026-11-03"
            refused = fixture.null("coverage")
            context = output["context"][cell]
            self.assertEqual([leg for leg, item in context.items() if item["date"] == day], [key])
            self.assertEqual(context[key]["value"], refused)
            summary = output["date_spreads"][cell]
            self.assertEqual(summary["dates"].keys(), {item["date"] for item in context.values()})
            self.assertEqual(summary["dates"][day], dict.fromkeys(("n", "mean", "sd"), refused))
            self.assertEqual(summary["missing"], {"coverage": 1})

    def test_prefill_level_preserves_a_half_nanosecond_midpoint(self):
        for offset, omit, expected in ((0, True, None), (1, False, None),
                                       (1, True, "coverage"), (2, True, "coverage")):
            with self.subTest(offset=offset, omit=omit), TemporaryDirectory() as temporary:
                leg = fixture.TraceLeg(Path(temporary))
                leg.meta["first_token_s"] = Decimal(606) + Decimal(offset).scaleb(-9)
                if omit:
                    leg.omit("gpu_power", [606])
                edges = fixture.print_one(leg.signal(), fixture.IDS[0])["edges"]
                for channel in fixture.CHANNEL[:2]:
                    fixture.assert_scalar(self, edges["rise_s"][channel], expected)
                    fixture.assert_scalar(self, edges["onset_lag_s"][channel], expected)

    def test_stability_calendar_gate_respects_the_exact_receipt_epoch(self):
        class LastDateReceipt(fixture.World):
            def leg(self, kit, pos, v, day, ordinal, status):
                refs = super().leg(kit, pos, v, day, ordinal, status)
                if day == 13 and status == "qualified":
                    path = self.repo / refs["receipt"]
                    receipt = fixture.read(path)
                    receipt["t0_epoch_s"] = "EXACT_EPOCH"
                    fixture.put(path, fixture.wire(receipt).replace(b'"EXACT_EPOCH"', self.epoch))
                    self.witness = refs["key"]
                return refs

        check = fixture.Checks()
        for stamp, due in ((b"1794643199.9999998", False), (b"1794643199.999999999", False),
                           (b"1794643200", True), (b"1794643200.000000001", True)):
            with self.subTest(stamp=stamp), TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                LastDateReceipt.epoch = stamp
                world = LastDateReceipt(root / "world", fixture.IDS[1])
                self.assertEqual(world.witness, "f2-stab-13/L002")
                if not due:
                    check.refused(world, "stage1")
                    self.assertFalse(world.stage.exists())
                    continue

                check.stage1(world)
                record = world.public_truth()
                self.assertEqual(record["n_local_dates"], 14)
                candidate = root / "candidate.json"
                fixture.put(candidate, record)
                rc, stdout, stderr, events = fixture.invoke(world, "validate-public", "--candidate", str(candidate))
                self.assertEqual((rc, stdout, stderr), (0, b"", b""))
                self.assertFalse(any(event in {"open", "write"} for event, _ in events))
                fixture.put(candidate, dict(record, n_local_dates=13))
                check.refused(world, "validate-public", extra=("--candidate", str(candidate)))

    def test_crossing_span_coverage_precedes_a_nonpositive_level(self):
        for missing_search, expected in ((False, "nonpositive_level"), (True, "coverage")):
            with self.subTest(missing_search=missing_search), TemporaryDirectory() as temporary:
                leg = fixture.TraceLeg(Path(temporary))
                if missing_search:
                    leg.omit("gpu_power", [602.25, 610.25])
                for row in leg.rows[fixture.RAIL_FILE]:
                    if (row["source"] == "powermetrics" and row["rail"] == "gpu_power"
                            and 604 <= float(row["interval_start_s"]) < 610):
                        row["power_w"] = "0"
                edges = fixture.print_one(leg.signal(), fixture.IDS[0])["edges"]
                for field in ("rise_s", "onset_lag_s", "decode_end_lag_s"):
                    self.assertEqual(edges[field]["gpu_rail"], fixture.null(expected))

    def test_hold_admission_uses_the_recorded_span_even_with_a_support_offset(self):
        for look in fixture.IDS[:2]:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                world = fixture.World(Path(temporary).resolve() / "world", look)
                keys = list(world.good)[:2]
                missing_stamps = {581, 583, 585, 587, 589, 591, 593}
                for key, projected_start in zip(keys, (None, -20)):
                    references = next(row for row in world.rows if row["key"] == key)
                    op = fixture.read(world.repo / references["leg_record"])
                    self.assertEqual(op["quiet_spans_ns"], [[0, 600_000_000_000]])
                    path = world.copy / key / "support.json"
                    support = fixture.read(path)
                    support["sidecar_times"] = [t for t in support["sidecar_times"]
                                                if t not in missing_stamps]
                    recorded = [t for t in support["sidecar_times"] if 0 <= t < 600]
                    self.assertEqual(len(recorded), 593)
                    self.assertEqual(max(b - a for a, b in zip(recorded, recorded[1:])), 2)
                    if projected_start is not None:
                        support["quiet_start_s"] = projected_start
                    fixture.put(path, support)
                report = _score_world(world)
                for key in keys:
                    for channel in fixture.CHANNEL:
                        self.assertEqual(report["hold"][key][channel]["mean_w"],
                                         {"value": None, "reason": "coverage"})
                    if world.inst:
                        self.assertEqual(report["gain"][key]["mean_fan_rpm"],
                                         {"value": None, "reason": "coverage"})

    def test_decode_end_lag_requires_a_qualifying_in_span_dc_sample(self):
        with TemporaryDirectory() as temporary:
            world = fixture.World(Path(temporary).resolve() / "world", fixture.IDS[0])
            key = next(iter(world.good))
            path = world.copy / key / "dc_points.csv"
            with path.open(encoding="utf-8", newline="") as stream:
                header, *rows = csv.reader(stream)
            in_span = [row for row in rows if 610 <= float(row[0]) <= 611]
            after_span = [row for row in rows if float(row[0]) > 611]
            self.assertEqual(len(in_span), 20)
            self.assertEqual(float(after_span[0][0]), 611.025)
            for row in in_span:
                row[1] = "60"
            for row in after_span:
                row[1] = "40"
            fixture.put(path, fixture.csvbytes([header, *rows]))
            report = _score_world(world)
            baseline = report["hold"][key]["dc_in"]["mean_w"]
            plateau = report["gain"][key]["decode_w"]["dc_in"]
            self.assertEqual(baseline + plateau / 2, 49.6875)
            for channel in fixture.CHANNEL[:2]:
                self.assertEqual(report["edges"][key]["decode_end_lag_s"][channel],
                                 {"value": None, "reason": "over 1 s", "bound_s": 1.0})

    def test_dc_crossing_uses_in_span_sample_pairs_at_both_boundaries(self):
        rows = [(-0.1, 0.4, 20.0, 0.0), (0.4, 0.8, 0.0, 20.0)]
        self.assertAlmostEqual(reader._dc_crossing(rows, 0, 1, 10, False), 0.6)
        rows = [(0.0, 0.5, 20.0, 18.0), (0.5, 1.0, 18.0, 2.0)]
        self.assertAlmostEqual(reader._dc_crossing(rows, 0, 1, 10, True), 0.75)
        rows = [(-0.1, 0.1, 20.0, 2.0), (0.1, 1.1, 2.0, 20.0)]
        self.assertEqual(reader._dc_crossing(rows, 0, 1, 10, True),
                         {"value": None, "reason": "crossed_before_span"})

    def test_dependent_turn_decode_and_floor_keep_the_interval_refusal(self):
        with TemporaryDirectory() as temporary:
            world = fixture.World(Path(temporary).resolve() / "world", fixture.IDS[0])
            key = next(iter(world.good))
            _filter_csv(world.copy / key / "power_trace.csv", lambda row: not (
                row["source"] == "powermetrics" and row["rail"] == "gpu_power"
                and float(row["interval_start_s"]) == 607
            ))
            report = _score_world(world)
            refused = {"value": None, "reason": "coverage"}
            turn, gain = report["turn"][key], report["gain"][key]
            for channel in fixture.CHANNEL[:2]:
                self.assertEqual(turn["energy_j"][channel], refused)
                self.assertEqual(gain["decode_w"][channel], refused)
                for ratio in (turn["ratios"][channel], gain["decode_gain"][channel]):
                    self.assertEqual(ratio["reason"], "coverage")
                    self.assertEqual(ratio["denominator"], refused)
                    self.assertIsInstance(ratio["numerator"], float)
                self.assertEqual(gain["floor_tokens"][channel], [refused] * 3)
            self.assertTrue(all(isinstance(value, float) for value in gain["floor_tokens"]["dc_in"]))

    def test_support_projection_handles_escaped_keys_and_nested_delimiters(self):
        readings = br'[{"label":"a\"b,[}]","temperature":37.8125}]'
        beginning = br'{"clock":{"note":"sensors: [,}]"},"sens\u006frs":'
        end = ',"fan_label":"ventilateur été"}'.encode()
        payload = beginning + readings + end
        metadata, span = reader._support_metadata(io.BytesIO(payload))
        self.assertEqual(metadata, {
            "clock": {"note": "sensors: [,}]"}, "sensors": None, "fan_label": "ventilateur été",
        })
        self.assertEqual(payload[slice(*span)], readings)
        duplicate = beginning + readings + b',"sensors":[]}'
        with self.assertRaisesRegex(reader.Refusal, "duplicate JSON field"):
            reader._support_metadata(io.BytesIO(duplicate))

    def test_file_backed_fan_and_sensor_values_decode_only_after_hold_admission(self):
        for look in fixture.IDS[:2]:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                world = fixture.World(Path(temporary).resolve() / "world", look)
                omitted = (set(range(1, 600, 2)), {100, 101}, set())
                readings = ((37.8125, 901.125), (37.9375, 902.125), (38.0625, 903.125))
                keys = list(world.good)[:3]
                for key, missing_stamps, (temperature, fan) in zip(keys, omitted, readings):
                    path = world.copy / key / "support.json"
                    support = fixture.read(path)
                    support["sidecar_times"] = [t for t in support["sidecar_times"]
                                                if t not in missing_stamps]
                    support["sensors"][0]["TV0h"] = temperature
                    support["sensors"][0]["fan_keys"]["left"] = fan
                    fixture.put(path, support)
                observed = []
                watched = {value for pair in readings for value in pair}
                original_loads = json.loads
                original_refusal = reader.Signals._interval_refusal

                def observe_number(raw):
                    value = float(raw)
                    if value in watched:
                        observed.append(value)
                    return value

                def observe_loads(payload, **kwargs):
                    parser = kwargs.pop("parse_float", float)
                    def read_number(raw):
                        observe_number(raw)
                        return parser(raw)
                    return original_loads(payload, parse_float=read_number, **kwargs)

                def observe_gate(signal, channel, a, b, rails):
                    reason = original_refusal(signal, channel, a, b, rails)
                    if channel == "sidecar":
                        observed.append(("sidecar", a, b, reason))
                    return reason

                with (patch.object(reader.json, "loads", observe_loads),
                      patch.object(reader.Signals, "_interval_refusal", observe_gate)):
                    report = _score_world(world)
                if world.inst:
                    self.assertEqual(observed[:3], [
                        ("sidecar", 0, 600, "coverage"), ("sidecar", 0, 600, "meter_gap"),
                        ("sidecar", 0, 600, None),
                    ])
                    self.assertCountEqual(observed[3:], readings[2])
                    self.assertEqual(report["gain"][keys[0]]["mean_fan_rpm"],
                                     {"value": None, "reason": "coverage"})
                    self.assertEqual(report["gain"][keys[2]]["mean_start_c"]["TV0h"],
                                     (readings[2][0] + 39) / 2)
                else:
                    self.assertEqual(observed, [])

    def test_turn_coverage_takes_precedence_over_failed_hold(self):
        for look in fixture.IDS[:2]:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                world = fixture.World(Path(temporary).resolve() / "world", look)
                key = next(iter(world.good))
                source = world.copy / key
                support_path = source / "support.json"
                support = fixture.read(support_path)
                support["sidecar_times"] = [t for t in support["sidecar_times"] if t not in (100, 101)]
                fixture.put(support_path, support)
                _filter_csv(source / "power_trace.csv", lambda row: not (
                    row["source"] == "powermetrics" and row["rail"] == "gpu_power"
                    and float(row["interval_start_s"]) == 607
                ))
                report = _score_world(world)
                self.assertEqual(report["hold"][key]["gpu_rail"]["mean_w"],
                                 {"value": None, "reason": "meter_gap"})
                turn = report["turn"][key]["energy_j"]
                self.assertEqual(turn["gpu_rail"], {"value": None, "reason": "coverage"})
                self.assertEqual(turn["rail_sum"], {"value": None, "reason": "coverage"})
                self.assertEqual(turn["dc_in"], {"value": None, "reason": "meter_gap"})

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
                        # At passing declared coverage, inspect rail identities
                        # even when the interval ultimately fails its gap check.
                        self.assertEqual(opens, [True] if channel in RAIL_FOR_CHANNEL
                                         and present >= 990 else [])
                    else:
                        self.assertIsInstance(value, Fraction if channel == "sidecar" else (int, float))
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
        raw = re.compile(r'\b(?:_rail_values|_meter_values|_sensor_source|load_gpu_trace)\b'
                         r'|\[["\'](?:power_w|watts|sensors)["\']\]')
        stamps = re.compile(r'\.(?:sidecar_ns|meter_ns)\b|\[["\'](?:sidecar_times|meter_times)["\']\]')
        io = re.compile(r'\b(?:open|read_bytes|read_text)\(')
        structural_io = {
            "description.py": {"working", "validate_manifest", "_step3_code",
                               "_validate_executables", "_open_signal"},
            "description_worker.py": {"_candidate", "_write_private"},
        }
        for source in sources:
            body = source.read_text()
            functions = [node for node in ast.walk(ast.parse(body))
                         if isinstance(node, ast.FunctionDef)]
            def enclosing_function(line_number):
                scope = min((node for node in functions
                             if node.lineno <= line_number <= node.end_lineno),
                            key=lambda node: node.end_lineno - node.lineno, default=None)
                return scope.name if scope else ""

            for node in ast.walk(ast.parse(body)):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr in {"_admitted_rails", "_admitted_meter"}:
                    self.assertEqual(enclosing_function(node.lineno), "interval_values")

            for line_no, line in enumerate(body.splitlines(), 1):
                owner = enclosing_function(line_no)
                with self.subTest(file=source.name, line=line_no):
                    if raw.search(line):
                        permitted = (owner in {"interval_values", "_admitted_rails", "_admitted_meter"}
                                     or owner == "__init__" and line.strip().endswith(
                                         (" = {}", " = sensor_source")))
                        self.assertTrue(permitted, line)
                    if stamps.search(line):
                        self.assertIn(owner, {"__init__", "_coverage_passes", "_interval_refusal",
                                              "_admitted_meter", "recovery_start", "stream_end"}, line)
                    if io.search(line):
                        support_only = owner == "score" and line.strip() == (
                            'with paths["support.json"].open("rb") as stream:'
                        )
                        self.assertTrue(owner == "interval_values" or support_only
                                        or owner in structural_io.get(source.name, ()), line)


if __name__ == "__main__":
    unittest.main()
