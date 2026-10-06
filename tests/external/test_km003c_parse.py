"""KM003C stream parsing: unwrap, duplicates, drops, the clock fit, energy and the meter.* flags.

Recorded fixtures (tests/fixtures/km003c, provenance.json) are slices of the
2026-10-06 wall-meter probe and one desk recording made with
scripts/km003c_monitor.py; synthetic streams are built here when a test needs
a known answer.
"""
from __future__ import annotations

import json
import struct
import tempfile
import unittest
from pathlib import Path

from joulewise.external import km003c_parse as kp

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "km003c"
NS = 1_000_000_000
MS = 1_000_000


def fixture(name: str) -> kp.Stream:
    return kp.parse(FIXTURES / name)


def sample(seq: int, vbus_v: float, ibus_a: float) -> bytes:
    return struct.pack("<HHiiHHHH", seq % 65536, 0x4B9C, round(vbus_v * 1e6), round(ibus_a * 1e6),
                       0, 0, 0, 0)


class Synthetic:
    """A stream file built poll by poll: 50 SPS (20 ms device step), 200 ms polls."""

    def __init__(self, *, rate_idx: int = 2, start_ns: int = 1_000_000 * NS, seq0: int = 1000,
                 b_ns_per_ms: float = 1e6, latency_ms: float = 1.0) -> None:
        self.rate_idx = rate_idx
        self.step = kp.STEP_MS[rate_idx]
        self.start_ns = start_ns
        self.seq = seq0
        self.dev_ms = 0
        self.b = b_ns_per_ms
        self.latency_ms = latency_ms
        self.lines: list[dict] = [{"k": "h", "schema": "joulewise.km003c_stream.v1",
                                   "status": "streaming", "rate_idx": rate_idx,
                                   "sps": 1000 // self.step, "poll_s": 0.2}]

    def host(self, dev_ms: float) -> int:
        return int(self.start_ns + self.b * dev_ms)

    def poll(self, count: int, *, watts: float = 60.0, vbus: float = 27.46, smc: dict | None = None,
             extra_latency_ms: float = 0.0, rtt_ms: float = 0.5, skip: int = 0,
             seqs: list[int] | None = None) -> None:
        """``count`` new samples (after ``skip`` dropped ones); the answer arrives
        latency_ms + extra_latency_ms after the newest sample."""

        self.seq += skip * self.step
        self.dev_ms += skip * self.step
        payload = b""
        newest = self.dev_ms
        for k in range(count):
            seq = seqs[k] if seqs is not None else self.seq
            payload += sample(seq, vbus, watts / vbus)
            newest = self.dev_ms
            self.seq += self.step
            self.dev_ms += self.step
        rx = self.host(newest) + int((self.latency_ms + extra_latency_ms) * MS)
        line = {"k": "b", "tx": rx - int(rtt_ms * MS), "rx": rx, "rt": rx, "n": count,
                "p": payload.hex(), "smc": smc if smc is not None else
                {"B0AC": 0, "B0AV": 12155, "PDTR": watts, "PSTR": watts, "PPBR": 0.4}}
        self.lines.append(line)

    def raw_line(self, line: dict) -> None:
        self.lines.append(line)

    def write(self, directory: Path, name: str = "s.jsonl", tail: str = "") -> Path:
        path = Path(directory) / name
        path.write_text("".join(json.dumps(line) + "\n" for line in self.lines) + tail)
        return path


class RecordedFixtureTests(unittest.TestCase):
    def test_plain50_slice_unwraps_across_the_16_bit_wrap(self):
        stream = fixture("plain50_slice.jsonl")
        raw = [seq for b in stream.batches
               for (seq, *_rest) in struct.iter_unpack("<HHiiHHHH", bytes.fromhex(b["p"]))]
        self.assertTrue(any(b < a for a, b in zip(raw, raw[1:])), "the slice must contain a wrap")
        dev = stream.samples.dev_ms
        self.assertEqual(len(dev), 1500)
        self.assertEqual({b - a for a, b in zip(dev, dev[1:])}, {20})
        self.assertEqual(kp.drops(stream.samples)["dropped"], 0)
        self.assertEqual(stream.samples.duplicates, 0)

    def test_recorded_re_delivery_is_dropped_and_counted(self):
        stream = fixture("redelivery1000_slice.jsonl")
        self.assertEqual(stream.samples.duplicates, 27)
        dev = stream.samples.dev_ms
        self.assertTrue(all(b > a for a, b in zip(dev, dev[1:])))
        self.assertEqual(kp.drops(stream.samples)["dropped"], 0)
        codes = [f["code"] for f in kp.flags(stream)]
        self.assertIn("meter.duplicates", codes)
        self.assertNotIn("meter.duplicates", [f["code"] for f in kp.flags(fixture("repo_live_50sps.jsonl"))])

    def test_clock_fit_on_recorded_slice_is_tight(self):
        stats = fixture("plain50_slice.jsonl").fit.stats
        self.assertTrue(stats["filtered"])
        self.assertGreater(stats["fraction_used"], 0.9)
        self.assertLess(abs(stats["clock_rate_ppm"]), 50)
        self.assertLess(stats["excess_latency_ms_max"], 2 * 20)
        self.assertGreater(stats["excess_latency_ms_min"], -1.0)
        self.assertLess(stats["excess_latency_ms_p50"], 10)

    def test_repo_recording_is_clean_and_agrees_with_pdtr(self):
        stream = fixture("repo_live_50sps.jsonl")
        self.assertEqual(stream.header["firmware_version"], "2.0.5")
        self.assertEqual(kp.flags(stream, [(stream.host_ns[0], stream.host_ns[-1])]), [])
        gain = kp.pdtr_gain(stream)
        self.assertGreaterEqual(gain["bins"], 15)
        self.assertTrue(0.95 <= gain["median"] <= 1.02, gain)

    def test_worked_example_numbers(self):
        stream = fixture("repo_live_50sps.jsonl")
        t0 = stream.host_ns[0]
        result = kp.delta_machine_energy(stream, (t0 + 12 * NS, t0 + 17 * NS), (t0, t0 + 10 * NS))
        self.assertEqual((result["meter"]["n"], result["meter"]["n_baseline"]), (250, 500))
        self.assertAlmostEqual(result["meter"]["baseline_W"], 69.258, places=3)
        self.assertAlmostEqual(result["meter"]["energy_J"], 364.540, places=3)
        self.assertAlmostEqual(result["meter"]["delta_J"], 18.252, places=3)
        self.assertEqual((result["battery"]["n"], result["battery"]["n_baseline"]), (25, 50))
        self.assertEqual(result["battery"]["delta_J"], 0.0)
        self.assertTrue(result["battery_term_available"])
        self.assertAlmostEqual(result["delta_J"], 18.252, places=3)
        self.assertAlmostEqual(kp.rho(9.1, result["delta_J"]), 0.4986, places=3)


class UnwrapAndDropTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_synthetic_wrap_keeps_device_time_increasing(self):
        s = Synthetic(seq0=65536 - 100)
        for _ in range(4):
            s.poll(10)
        stream = kp.parse(s.write(self.tmp.name))
        self.assertEqual(stream.samples.dev_ms, list(range(0, 40 * 20, 20)))

    def test_stall_longer_than_half_a_wrap_uses_host_time(self):
        s = Synthetic()
        s.poll(10)
        s.poll(10, skip=(70_000 // 20) - 1)  # 70 s stall: the counter wrapped once
        stream = kp.parse(s.write(self.tmp.name))
        dev = stream.samples.dev_ms
        self.assertEqual(dev[10] - dev[9], 70_000)  # signed steps alone would give 4464
        self.assertEqual(kp.drops(stream.samples)["dropped"], 70_000 // 20 - 1)

    def test_re_delivered_batch_is_dropped(self):
        s = Synthetic()
        s.poll(10)
        s.poll(10)
        repeat = dict(s.lines[-1])
        repeat["rx"] += 5 * MS
        repeat["tx"] += 5 * MS
        s.raw_line(repeat)
        s.poll(10)
        stream = kp.parse(s.write(self.tmp.name))
        self.assertEqual(stream.samples.duplicates, 10)
        self.assertEqual(len(stream.samples.dev_ms), 30)
        self.assertEqual(kp.drops(stream.samples)["dropped"], 0)

    def test_drops_are_counted_and_flagged_above_half_a_percent(self):
        def build(skips: int) -> kp.Stream:
            s = Synthetic()
            for k in range(100):
                s.poll(10, skip=1 if 1 <= k <= skips else 0)
            return kp.parse(s.write(self.tmp.name, f"d{skips}.jsonl"))

        five, six = build(5), build(6)
        self.assertEqual(kp.drops(five.samples)["dropped"], 5)   # 5 / 1005 = 0.497 %
        self.assertEqual(kp.drops(six.samples)["dropped"], 6)    # 6 / 1006 = 0.596 %
        self.assertNotIn("meter.drops_excess", [f["code"] for f in kp.flags(five)])
        self.assertIn("meter.drops_excess", [f["code"] for f in kp.flags(six)])

    def test_truncated_last_line_is_ignored(self):
        s = Synthetic()
        for _ in range(3):
            s.poll(10)
        stream = kp.parse(s.write(self.tmp.name, tail='{"k":"b","tx":1,"rx'))
        self.assertEqual(len(stream.samples.dev_ms), 30)


class ClockFitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def build(self, *, ppm: float, outlier_ms: float = 0.0) -> kp.Stream:
        s = Synthetic(b_ns_per_ms=1e6 * (1 + ppm * 1e-6), latency_ms=1.0)
        for k in range(600):  # 120 s of polls
            jitter = (k * 7919 % 13) * 0.5  # 0 to 6 ms above the minimum latency
            s.poll(10, extra_latency_ms=jitter + (outlier_ms if k == 300 else 0.0))
        return kp.parse(s.write(self.tmp.name, f"fit{ppm}-{outlier_ms}.jsonl"))

    def test_fit_recovers_rate_and_minimum_latency_line(self):
        stream = self.build(ppm=50.0)
        self.assertAlmostEqual(stream.fit.stats["clock_rate_ppm"], 50.0, delta=0.5)
        # The envelope sits on the minimum-latency points: newest sample + 1 ms.
        self.assertLess(abs(stream.fit.host_ns(0) - (1_000_000 * NS + 1 * MS)), 0.2 * MS)
        self.assertLess(stream.fit.stats["excess_latency_ms_max"], 6.5)
        self.assertNotIn("meter.clock_fit_residual", [f["code"] for f in kp.flags(stream)])

    def test_residual_above_two_sample_periods_is_flagged(self):
        stream = self.build(ppm=0.0, outlier_ms=45.0)
        self.assertGreater(stream.fit.stats["excess_latency_ms_max"], 40)
        self.assertIn("meter.clock_fit_residual", [f["code"] for f in kp.flags(stream)])

    def test_capped_and_slow_polls_are_left_out_of_the_fit(self):
        s = Synthetic()
        for k in range(100):
            s.poll(10, extra_latency_ms=80.0 if k % 10 == 0 else 0.0,
                   rtt_ms=10.0 if k % 10 == 0 else 0.5)
        stream = kp.parse(s.write(self.tmp.name))
        self.assertEqual(stream.fit.stats["points_used"], 90)
        self.assertLess(stream.fit.stats["excess_latency_ms_max"], 1.0)

    def test_capped_answers_are_left_out_even_when_fast(self):
        # A capped answer (63 samples) returns the oldest backlog: its newest
        # sample is old even though the round trip was quick.
        s = Synthetic()
        for k in range(100):
            capped = k % 10 == 0
            s.poll(63 if capped else 10, extra_latency_ms=80.0 if capped else 0.0, rtt_ms=0.5)
        stream = kp.parse(s.write(self.tmp.name, "capped.jsonl"))
        self.assertEqual(stream.fit.stats["points_used"], 90)
        self.assertLess(stream.fit.stats["excess_latency_ms_max"], 1.0)


class EnergyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_integrate_constant_power_is_exact(self):
        times = [k * 20 * MS for k in range(1000)]
        energy, n = kp.integrate(times, [50.0] * 1000, 2 * NS, 7 * NS)
        self.assertEqual(n, 250)
        self.assertAlmostEqual(energy, 250.0, places=9)
        self.assertEqual(kp.integrate(times, [50.0] * 1000, 30 * NS, 31 * NS), (None, 0))
        with self.assertRaises(ValueError):
            kp.integrate(times, [50.0] * 1000, 5, 5)

    def stream(self, window_b0ac: int | None) -> tuple[kp.Stream, tuple, tuple]:
        s = Synthetic()
        for k in range(150):  # 30 s: baseline 0-10 s at 60 W, window 15-25 s at 80 W
            t = k * 0.2
            in_window = 15 <= t < 25
            smc = {"B0AC": (window_b0ac if in_window else 0), "B0AV": 12000, "PDTR": 60.0}
            if window_b0ac is None:
                smc = {}
            s.poll(10, watts=80.0 if in_window else 60.0, smc=smc)
        stream = kp.parse(s.write(self.tmp.name, f"e{window_b0ac}.jsonl"))
        base = stream.fit.host_ns(0)
        return stream, (base + 15 * NS, base + 25 * NS), (base, base + 10 * NS)

    def test_delta_machine_energy_adds_the_battery_term(self):
        stream, window, baseline = self.stream(-500)  # 0.5 A out of a 12 V battery: 6 W
        result = kp.delta_machine_energy(stream, window, baseline)
        self.assertAlmostEqual(result["meter"]["delta_J"], 20.0 * 10, delta=0.5)
        self.assertAlmostEqual(result["battery"]["delta_J"], 6.0 * 10, delta=0.5)
        self.assertAlmostEqual(result["delta_J"], 26.0 * 10, delta=1.0)
        self.assertTrue(result["battery_term_available"])
        codes = [f["code"] for f in kp.flags(stream, [window])]
        self.assertIn("meter.battery_activity", codes)
        self.assertNotIn("meter.battery_activity", [f["code"] for f in kp.flags(stream, [baseline])])

    def test_charging_is_battery_activity_too(self):
        stream, window, baseline = self.stream(300)  # charging: power flows into the battery
        result = kp.delta_machine_energy(stream, window, baseline)
        self.assertAlmostEqual(result["battery"]["delta_J"], -3.6 * 10, delta=0.5)
        self.assertIn("meter.battery_activity", [f["code"] for f in kp.flags(stream, [window])])

    def test_without_battery_activity_machine_equals_meter(self):
        stream, window, baseline = self.stream(0)
        result = kp.delta_machine_energy(stream, window, baseline)
        self.assertEqual(result["battery"]["delta_J"], 0.0)
        self.assertEqual(result["delta_J"], result["meter"]["delta_J"])
        self.assertNotIn("meter.battery_activity", [f["code"] for f in kp.flags(stream, [window])])

    def test_missing_smc_leaves_the_battery_term_unavailable(self):
        stream, window, baseline = self.stream(None)
        result = kp.delta_machine_energy(stream, window, baseline)
        self.assertFalse(result["battery_term_available"])
        self.assertEqual(result["delta_J"], result["meter"]["delta_J"])

    def test_rho(self):
        self.assertEqual(kp.rho(5.0, 10.0), 0.5)
        self.assertIsNone(kp.rho(5.0, 0.0))
        self.assertIsNone(kp.rho(5.0, -3.0))
        self.assertIsNone(kp.rho(None, 10.0))
        self.assertIsNone(kp.rho(5.0, None))
        self.assertEqual(kp.rho(-2.0, 10.0), -0.2)  # reported as computed; the band judges it


class OffsetTests(unittest.TestCase):
    def stream(self, header: dict, trailer: dict | None) -> kp.Stream:
        return kp.Stream(header, trailer, [], [], None, None, [], [], [], [])

    def test_offset_from_the_start_and_end_pairs(self):
        header = {"start_raw_ns": 5_000_000_000, "start_mono_ns": 1_000_000_000}
        self.assertEqual(kp.raw_offset_ns(self.stream(header, {"end_raw_ns": 9_000_000_000,
                                                                "end_mono_ns": 5_000_000_500})), 4_000_000_000)
        # A sleep moves the clocks apart: no single offset.
        self.assertIsNone(kp.raw_offset_ns(self.stream(header, {"end_raw_ns": 9_000_000_000,
                                                                 "end_mono_ns": 4_000_000_000})))
        self.assertIsNone(kp.raw_offset_ns(self.stream(header, None)))


class FlagTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def codes(self, s: Synthetic, name: str) -> list[str]:
        return [f["code"] for f in kp.flags(kp.parse(s.write(self.tmp.name, name)))]

    def test_every_flag_is_disclose_and_named(self):
        s = Synthetic()
        for _ in range(50):
            s.poll(10, vbus=20.0, smc={"B0AC": 0, "B0AV": 12000, "PDTR": 40.0})
        found = kp.flags(kp.parse(s.write(self.tmp.name)))
        self.assertTrue(found)
        for item in found:
            self.assertEqual(item["effect"], "DISCLOSE")
            self.assertIn(item["code"], kp.CODES)

    def test_absent_header(self):
        path = Path(self.tmp.name) / "absent.jsonl"
        path.write_text(json.dumps({"k": "h", "status": "absent", "reason": "no USB device"}) + "\n"
                        + json.dumps({"k": "t", "polls": 0}) + "\n")
        found = kp.flags(kp.parse(path))
        self.assertEqual([f["code"] for f in found], ["meter.absent"])
        self.assertIn("no USB device", found[0]["detail"])

    def test_streaming_without_samples_is_absent(self):
        s = Synthetic()
        s.poll(0)
        self.assertEqual(self.codes(s, "empty.jsonl"), ["meter.absent"])

    def test_pdtr_gain_band(self):
        for pdtr_scale, expected in ((0.98, False), (0.90, True), (1.05, True)):
            s = Synthetic()
            for _ in range(50):
                s.poll(10, watts=70.0, smc={"B0AC": 0, "B0AV": 12000, "PDTR": 70.0 * pdtr_scale})
            with self.subTest(scale=pdtr_scale):
                self.assertEqual("meter.pdtr_gain_out_of_band" in self.codes(s, f"g{pdtr_scale}.jsonl"),
                                 expected)

    def test_pdtr_never_read_is_flagged(self):
        s = Synthetic()
        for _ in range(50):
            s.poll(10, smc={"B0AC": 0, "B0AV": 12000})
        self.assertIn("meter.pdtr_gain_out_of_band", self.codes(s, "nopdtr.jsonl"))

    def test_vbus_contract(self):
        for vbus, expected in ((27.46, False), (26.0, True), (30.0, True)):
            s = Synthetic()
            for _ in range(20):
                s.poll(10, vbus=vbus, watts=60.0, smc={"B0AC": 0, "B0AV": 12000, "PDTR": 60.0})
            with self.subTest(vbus=vbus):
                self.assertEqual("meter.vbus_out_of_contract" in self.codes(s, f"v{vbus}.jsonl"), expected)


if __name__ == "__main__":
    unittest.main()


class ReviewRegressionTests(unittest.TestCase):
    """Sol 6.1 review of 10-06 (F3, F4)."""

    def test_a_malformed_interior_line_is_a_protocol_error_and_a_truncated_last_line_is_not(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "km003c" / "repo_live_50sps.jsonl"
        lines_ = fixture.read_text().splitlines()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "s.jsonl"
            path.write_text("\n".join(lines_[:5] + ['{"k":"b","tx":1,'] + lines_[5:]) + "\n" + '{"k":"b","t')
            header, trailer, batches, errors = kp.load(path)
        self.assertEqual([e.get("line") for e in errors if "parse_error" in e], [6])
        self.assertEqual(len(batches), len([l for l in lines_ if '"k":"b"' in l]))

    def test_samples_without_a_clock_fit_are_disclosed_as_unfitted_not_absent(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "km003c" / "repo_live_50sps.jsonl"
        lines_ = fixture.read_text().splitlines()
        first_sample = next(i for i, l in enumerate(lines_) if '"k":"b"' in l and '"n":0,' not in l)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "s.jsonl"
            path.write_text("\n".join([lines_[0], lines_[first_sample]]) + "\n")
            stream = kp.parse(path)
        self.assertTrue(stream.present)
        self.assertFalse(stream.aligned)
        codes = [f["code"] for f in kp.flags(stream)]
        self.assertNotIn("meter.absent", codes)
        self.assertIn("meter.clock_fit_residual", codes)

