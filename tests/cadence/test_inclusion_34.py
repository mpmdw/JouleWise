"""Inclusion rules 3 and 4 at the look (RL-166 Q7). Synthetic bundles and streams only.

* Equality with the registered U1 evaluator: the copied source matches ``thermal.py`` and the
  ``thermal_desk.member_record`` pm_gap lines, and the copies give the same results on fixtures.
* Boundary tests at every threshold (99 %, 2 s, max(1 s, 5 periods)). These kill the obvious mutants.
* Spy tests: no sample line is decoded and no value key is retained; no energy file is opened."""
from __future__ import annotations

import builtins
import inspect
import io
import json
from pathlib import Path
import shutil
import tempfile
import textwrap
import unittest
import unittest.mock

from joulewise.align.apple import thermal
from joulewise.cadence_looks import inclusion_34 as i34

REPO = Path(__file__).resolve().parents[2]
NS = 1_000_000_000
T0 = 1_800_000_000 * NS                     # wall-clock ns, synthetic
KEYS = ("TV0h", "TV1h", "F0Ac", "F1Ac", "Tf08")
GOOD = {"TV0h": 50.0, "TV1h": 49.0, "F0Ac": 1200.0, "F1Ac": 1180.0, "Tf08": 40.0}


def sidecar(start_s, end_s, skip=()):
    """1 Hz readings at start + k s (+ 30 ms reading time), skipping the k in ``skip``."""
    return [(T0 + k * NS, T0 + k * NS + 30_000_000, {"sensors": dict(GOOD), "errors": {}})
            for k in range(start_s, end_s + 1) if k not in skip]


def pm(start_s, end_s, period_s, holes=()):
    """Contiguous powermetrics supports of ``period_s``; a hole (a, b) in seconds removes the supports that
    overlap it."""
    out, t = [], T0 + start_s * NS
    step = round(period_s * NS)
    while t < T0 + end_s * NS:
        s = {"start_ns": t, "end_ns": t + step}
        if not any(T0 + round(a * NS) < s["end_ns"] and s["start_ns"] < T0 + round(b * NS) for a, b in holes):
            out.append(s)
        t += step
    return out


def stream(name="stream-0001.jsonl", start_s=-10, end_s=230, poll_s=0.2, stop="signal 15", skip=None,
           header=True, trailer=True, status="streaming"):
    step = round(poll_s * NS)
    stamps = [T0 + start_s * NS + i * step for i in range(int((end_s - start_s) / poll_s) + 1)]
    if skip:
        stamps = [t for t in stamps if not (T0 + round(skip[0] * NS) <= t < T0 + round(skip[1] * NS))]
    return {"name": name,
            "header": {"k": "h", "status": status, "poll_s": poll_s, "start_real_ns": T0 + start_s * NS} if header else None,
            "trailer": {"k": "t", "polls": len(stamps), "empties": 3, "bad": 1, "usb_errors": 0, "stop_reason": stop}
            if trailer else None,
            "stamps": stamps}


INTERVAL = (T0, T0 + 200 * NS)


class Base(unittest.TestCase):
    def tmp(self):
        d = Path(tempfile.mkdtemp(prefix="i34-"))
        self.addCleanup(lambda: shutil.rmtree(d, ignore_errors=True))
        return d


class EqualToRegisteredU1(Base):
    def test_copied_source_is_byte_identical(self):
        for name in ("Coverage", "valid_value", "keys"):
            self.assertEqual(inspect.getsource(getattr(i34, name)), inspect.getsource(getattr(thermal, name)), name)

    def registered_pm_gap(self):
        src = (REPO / "joulewise/align/apple/thermal_desk.py").read_text(encoding="utf-8")
        start, end = "    pm_gap = 0\n", "        pm_gap = max(pm_gap, b-cursor)\n"
        self.assertEqual(src.count(start), 1)
        self.assertEqual(src.count(end), 1)
        block = src[src.index(start):src.index(end) + len(end)]
        return textwrap.dedent(block)

    def test_pm_gap_equals_the_registered_lines(self):
        block = self.registered_pm_gap()
        mine = textwrap.dedent(inspect.getsource(i34.pm_max_gap_ns)).splitlines()[1:-1]
        self.assertEqual("\n".join(l[4:] for l in mine) + "\n", block)        # same lines, one indent deeper
        fixtures = [([(0, 10)], []), ([(0, 10)], [{"start_ns": 2, "end_ns": 5}]),
                    ([(0, 100), (200, 300)], [{"start_ns": 10, "end_ns": 40}, {"start_ns": 35, "end_ns": 90},
                                               {"start_ns": 250, "end_ns": 310}]),
                    ([(INTERVAL)], pm(0, 200, 0.25, holes=[(50, 51.3)]))]
        for spans, samples in fixtures:
            ns = {"spans": spans, "pm_samples": samples}
            exec(block, {}, ns)                                                # the registered lines
            self.assertEqual(i34.pm_max_gap_ns(spans, samples), ns["pm_gap"])

    def test_coverage_reports_equal_on_fixtures(self):
        for rows in (sidecar(0, 200), sidecar(0, 200, skip={50, 120}), sidecar(0, 200, skip={50, 51}), sidecar(5, 190)):
            a, b = INTERVAL
            mine, reg = i34.Coverage(a, KEYS), thermal.Coverage(a, KEYS)
            for s, f, v in rows:
                mine.observe(s, f, v)
                reg.observe(s, f, v)
            self.assertEqual(mine.report(b), reg.report(b))


class Rule3(Base):
    def test_full_coverage_passes(self):
        r = i34.rule3(INTERVAL, sidecar(0, 200), KEYS, pm(0, 200, 0.25), 0.25)
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["sample_fraction"], 1.0)
        self.assertEqual(r["pm_gap_limit_s"], 1.25)

    def test_sidecar_fraction_boundary(self):
        r = i34.rule3(INTERVAL, sidecar(0, 200, skip={20, 100}), KEYS, pm(0, 200, 0.25), 0.25)
        self.assertEqual(r["sample_fraction"], 0.99)
        self.assertTrue(r["pass"], r)                                         # exactly 99 % passes
        r = i34.rule3(INTERVAL, sidecar(0, 200, skip={20, 100, 150}), KEYS, pm(0, 200, 0.25), 0.25)
        self.assertFalse(r["pass"])
        self.assertIn("sidecar coverage under 99 %", r["reasons"])

    def test_sidecar_gap(self):
        r = i34.rule3(INTERVAL, sidecar(0, 200, skip={100, 101}), KEYS, pm(0, 200, 0.25), 0.25)
        self.assertIn("sidecar gap over 2 s", r["reasons"])
        bad = sidecar(0, 200)
        bad[10] = (bad[10][0], bad[10][1], {"sensors": {**GOOD, "TV0h": None}, "errors": {}})
        r = i34.rule3(INTERVAL, bad, KEYS, pm(0, 200, 0.25), 0.25)
        self.assertLess(r["sample_fraction"], 1.0)                            # an invalid key empties its cell

    def test_pm_gap_boundary(self):
        exact = i34.rule3(INTERVAL, sidecar(0, 200), KEYS, pm(0, 200, 0.25, holes=[(50.01, 51.24)]), 0.25)
        self.assertEqual(exact["pm_max_gap_s"], 1.25)
        self.assertTrue(exact["pass"], exact)                                 # gap == 5 periods passes
        over = i34.rule3(INTERVAL, sidecar(0, 200), KEYS, pm(0, 200, 0.25, holes=[(50.01, 51.26)]), 0.25)
        self.assertEqual(over["pm_max_gap_s"], 1.5)
        self.assertIn("powermetrics gap over max(1 s, 5 periods)", over["reasons"])
        floor = i34.rule3(INTERVAL, sidecar(0, 200), KEYS, pm(0, 200, 0.1, holes=[(50.05, 50.95)]), 0.1)
        self.assertEqual(floor["pm_gap_limit_s"], 1.0)                        # max(1 s, 0.5 s)
        self.assertTrue(floor["pass"], floor)
        slow = i34.rule3(INTERVAL, sidecar(0, 200), KEYS, pm(0, 200, 0.5, holes=[(50.1, 52.4)]), 0.5)
        self.assertEqual(slow["pm_gap_limit_s"], 2.5)
        self.assertTrue(slow["pass"], slow)

    def test_no_interval_or_period(self):
        self.assertIn("no leg interval (G0 start or last stamped token missing)",
                      i34.rule3(None, sidecar(0, 200), KEYS, pm(0, 200, 0.25), 0.25)["reasons"])
        self.assertIn("powermetrics period unknown",
                      i34.rule3(INTERVAL, sidecar(0, 200), KEYS, pm(0, 200, 0.25), None)["reasons"])
        r = i34.rule3(INTERVAL, sidecar(0, 200), KEYS, [], 0.25)
        self.assertEqual(r["pm_max_gap_s"], 200.0)
        self.assertFalse(r["pass"])


class Rule4(Base):
    def test_clean_stream_passes(self):
        r = i34.rule4(INTERVAL, [stream()])
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["streams"], ["stream-0001.jsonl"])

    def test_normal_and_abnormal_stops(self):
        for stop in ("signal 15", "signal 2", "duration", "stop file"):
            self.assertTrue(i34.rule4(INTERVAL, [stream(stop=stop)])["pass"], stop)
        for stop in ("consecutive USB errors", "absent", "exception", None):
            r = i34.rule4(INTERVAL, [stream(stop=stop)])
            self.assertFalse(r["pass"], stop)

    def test_header_and_trailer_present(self):
        self.assertIn("stream-0001.jsonl: no trailer", i34.rule4(INTERVAL, [stream(trailer=False)])["reasons"])
        self.assertFalse(i34.rule4(INTERVAL, [stream(status="absent")])["pass"])
        self.assertIn("no meter stream covers the leg's interval", i34.rule4(INTERVAL, [])["reasons"])

    def test_trailer_counts_decide_nothing(self):
        s = stream()
        s["trailer"].update(bad=40, usb_errors=4, empties=900)
        self.assertTrue(i34.rule4(INTERVAL, [s])["pass"])                    # RL-166 Q7 refused that clause

    def test_coverage_and_gap_boundaries(self):
        exact = i34.rule4(INTERVAL, [stream(skip=(100, 102))])                # a 2.2 s hole at 0.2 s polls
        self.assertGreater(exact["max_gap_s"], 2.0)
        self.assertIn("meter gap over 2 s", exact["reasons"])
        two = i34.rule4(INTERVAL, [stream(skip=(100.1, 101.9))])              # stamps 100.0 and 102.0
        self.assertAlmostEqual(two["max_gap_s"], 2.0)
        self.assertTrue(two["pass"], two)
        sparse = i34.rule4(INTERVAL, [stream(skip=(50.1, 51.9)), ] )
        self.assertTrue(sparse["pass"])
        many = dict(stream())
        many["stamps"] = [t for i, t in enumerate(many["stamps"]) if i % 60 != 0]   # ~1.7 % missing
        r = i34.rule4(INTERVAL, [many])
        self.assertLess(r["coverage_fraction"], 0.99)
        self.assertIn("meter coverage under 99 % of the nominal rate", r["reasons"])

    def test_two_streams_and_a_stream_outside_the_interval(self):
        first = stream(name="stream-0001.jsonl", start_s=-10, end_s=100, stop="signal 15")
        second = stream(name="stream-0002.jsonl", start_s=100, end_s=230, stop="signal 15")
        second["stamps"] = second["stamps"][1:]
        old = stream(name="stream-0000.jsonl", start_s=-500, end_s=-300, stop="consecutive USB errors")
        r = i34.rule4(INTERVAL, [old, first, second])
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["streams"], ["stream-0001.jsonl", "stream-0002.jsonl"])
        first["trailer"]["stop_reason"] = "consecutive USB errors"
        self.assertFalse(i34.rule4(INTERVAL, [old, first, second])["pass"])

    def test_poll_period_must_agree(self):
        self.assertIn("the header's nominal poll period is missing or differs between streams",
                      i34.rule4(INTERVAL, [stream(start_s=-10, end_s=100),
                                           stream(name="b", start_s=100, end_s=230, poll_s=0.25)])["reasons"])


class Readers(Base):
    SENTINEL_HEX = "deadbeef" * 5

    def write_stream(self, d):
        lines = [json.dumps({"k": "h", "status": "streaming", "poll_s": 0.2, "start_real_ns": T0, "sps": 50,
                             "start_raw_ns": 5, "start_mono_ns": 6}, sort_keys=True)]
        for i in range(5):
            lines.append('{"k":"b","tx":%d,"rx":%d,"rt":%d,"n":%d,"p":"%s","smc":{"PDTR":123.45,"PSTR":67.8}}'
                         % (100 + i, 200 + i, T0 + i * 200_000_000, 1, self.SENTINEL_HEX))
        lines.append(json.dumps({"k": "e", "rx": 999, "raw": self.SENTINEL_HEX}))
        lines.append(json.dumps({"k": "b", "tx": 1, "rx": 2, "rt": T0 + 5 * 200_000_000, "n": 1, "p": self.SENTINEL_HEX,
                                 "smc": {"PDTR": 1.0}}))                     # spaced JSON: stamp taken, never decoded
        lines.append(json.dumps({"k": "t", "polls": 5, "empties": 0, "bad": 1, "usb_errors": 0, "elapsed_s": 1.0,
                                 "stop_reason": "signal 15"}, sort_keys=True))
        p = d / "stream-0001.jsonl"
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return p

    def test_meter_stream_takes_stamps_only(self):
        p = self.write_stream(self.tmp())
        decoded = []
        real = json.loads

        def spy(s, *a, **k):
            decoded.append(s if isinstance(s, str) else s.decode())
            return real(s, *a, **k)
        with unittest.mock.patch.object(i34.json, "loads", spy):
            s = i34.read_meter_stream(p)
        self.assertEqual(s["stamps"], [T0 + i * 200_000_000 for i in range(6)])
        self.assertEqual(s["header"]["poll_s"], 0.2)
        self.assertEqual(s["trailer"]["stop_reason"], "signal 15")
        self.assertEqual(len(decoded), 2)                                     # header and trailer only
        for text in decoded:
            self.assertNotIn('"k":"b"', text)
            self.assertNotIn(self.SENTINEL_HEX, text)
            self.assertNotIn("PDTR", text)
        self.assertNotIn(self.SENTINEL_HEX, json.dumps(s))
        self.assertEqual(i34.span_trailers("dev-01-s01", [s]),
                         [{"span_id": "dev-01-s01", "stream": "stream-0001.jsonl", "polls": 5, "empties": 0, "bad": 1,
                           "usb_errors": 0, "stop_reason": "signal 15"}])

    def make_bundle(self):
        b = self.tmp() / "runtime"
        (b / "outputs").mkdir(parents=True)
        (b / "config.json").write_text(json.dumps({"sampling": {"power_hz": 4}, "model": {"path": "/x"}}))
        ev = [{"event_type": "phase_start", "phase": "align_thermal_gate", "timestamp_s": T0 / NS,
               "metadata": {"kind": "G0", "reference": {"fast_c": 50}}},
              {"event_type": "phase_end", "phase": "align_thermal_gate", "timestamp_s": T0 / NS + 30,
               "metadata": {"kind": "G0"}}]
        ev += [{"event_type": "token", "timestamp_s": T0 / NS + 40 + 0.04 * i, "metadata": {"index": i}}
               for i in range(4000)]
        (b / "events.jsonl").write_text("\n".join(json.dumps(e) for e in ev) + "\n")
        rows = [{"module": "temperature", "kind": "reading", "started": {"wall_ns": s, "monotonic_ns": s - T0},
                 "finished": {"wall_ns": f, "monotonic_ns": f - T0},
                 "values": {"sensors": v["sensors"], "errors": {}, "status": {"os_level": 0, "pm_state": "Nominal"}}}
                for s, f, v in sidecar(0, 210)]
        rows.append({"module": "hazard", "kind": "reading", "started": {"wall_ns": T0}, "finished": {"wall_ns": T0}})
        (b / "outputs" / "align_thermal.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        rich = [{"index": i, "timestamp_s": (s["end_ns"]) / NS, "elapsed_ns": s["end_ns"] - s["start_ns"],
                 "gpu": {"gpu_energy": 4242.0, "dvfm_states": [{"freq": 1380, "used_ns": 5}]},
                 "processor_combined_power_w": 31.5}
                for i, s in enumerate(pm(0, 210, 0.25))]
        (b / "rich_telemetry.jsonl").write_text("\n".join(json.dumps(r) for r in rich) + "\n")
        (b / "power_trace.csv").write_text("SENTINEL energy file\n")
        (b / "raw").mkdir()
        (b / "raw" / "powermetrics.plist").write_text("SENTINEL\n")
        return b

    def test_g0_falls_back_to_the_runtime_event_log(self):
        b = self.make_bundle()
        lines = (b / "events.jsonl").read_text().splitlines()
        gate = [l for l in lines if "align_thermal_gate" in l]
        (b / "events.jsonl").write_text("\n".join(l for l in lines if "align_thermal_gate" not in l) + "\n")
        self.assertIsNone(i34.read_leg_interval(b))
        (b / "outputs" / "align_runtime_events.jsonl").write_text("\n".join(gate) + "\n")
        self.assertEqual(i34.read_leg_interval(b)[0], T0)

    def test_interval_and_period(self):
        b = self.make_bundle()
        a, z = i34.read_leg_interval(b)
        self.assertEqual(a, T0)
        self.assertAlmostEqual((z - T0) / NS, 40 + 0.04 * 3999, places=5)
        self.assertEqual(i34.pm_period_s(b), 0.25)
        (b / "events.jsonl").write_text(json.dumps({"event_type": "token", "timestamp_s": 1.0}) + "\n")
        self.assertIsNone(i34.read_leg_interval(b))

    def test_rich_telemetry_keeps_two_keys(self):
        b = self.make_bundle()
        kept = []
        real_keep = i34._keep

        def keep(allowed):
            hook = real_keep(allowed)

            def spy(pairs):
                out = hook(pairs)
                kept.append(dict(out))
                return out
            return spy
        with unittest.mock.patch.object(i34, "_keep", keep):
            supports = i34.read_pm_supports(b)
        self.assertTrue(supports)
        self.assertEqual(set().union(*(d.keys() for d in kept)), {"timestamp_s", "elapsed_ns"})
        self.assertEqual(set().union(*(s.keys() for s in supports)), {"start_ns", "end_ns"})
        self.assertNotIn("4242", json.dumps(supports))

    def test_judge_leg_opens_no_energy_file(self):
        b = self.make_bundle()
        opened = []
        real_open = builtins.open

        def spy(file, *a, **k):
            opened.append(Path(str(file)).name)
            return real_open(file, *a, **k)
        with unittest.mock.patch.object(builtins, "open", spy), unittest.mock.patch.object(io, "open", spy):
            v = i34.judge_leg(b, [stream()], KEYS)
        self.assertTrue(v["rule3"]["pass"], v["rule3"])
        self.assertTrue(v["rule4"]["pass"], v["rule4"])
        self.assertEqual(set(opened), {"events.jsonl", "align_thermal.jsonl", "rich_telemetry.jsonl", "config.json"})

    def test_keys_from_the_registered_policy(self):
        cfg = json.loads((REPO / "configs/align/v4/r1_runtime.json").read_text())
        self.assertEqual(i34.keys(cfg["sensors"]), KEYS)


class CustodyVerdictFile(Readers):
    """The verdict file the stage-1 CLI reads (interface section 7): exact shape, one entry per roster leg."""

    def make_span(self):
        root = self.tmp()
        sdir = root / "dev-03-s01"
        (sdir / "legs" / "L001" / "runtime").mkdir(parents=True)
        (sdir / "legs" / "L002").mkdir(parents=True)
        bundle = self.make_bundle()
        shutil.move(str(bundle), str(sdir / "legs" / "L001" / "runtime" / "b"))
        (sdir / "legs" / "L001" / "leg_record.json").write_text(json.dumps({"result": {"bundle": "b"}}))
        (sdir / "runner_receipt.json").write_text(json.dumps({"roster": ["L001", "L002", "L003"], "started": {"epoch_s": 1.0}}))
        (sdir / "legs" / "L003").mkdir(parents=True)
        (sdir / "legs" / "L003" / "leg_record.json").write_text(json.dumps({"result": {}}))
        meter = sdir / "hazards" / "meter"
        meter.mkdir(parents=True)
        s = stream()
        lines = [json.dumps(s["header"], sort_keys=True)]
        lines += ['{"k":"b","tx":1,"rx":2,"rt":%d,"n":1,"p":"%s","smc":{"PDTR":1.5}}' % (t, self.SENTINEL_HEX)
                  for t in s["stamps"]]
        lines.append(json.dumps(s["trailer"], sort_keys=True))
        (meter / "stream-0001.jsonl").write_text("\n".join(lines) + "\n")
        roster = root / "roster.json"
        roster.write_text(json.dumps([{"span_id": "dev-03-s01", "block_id": "dev-03", "role": "fit",
                                       "t0_local_date": "2026-11-16"}]))
        return root, roster

    def test_main_writes_the_interface_shape(self):
        root, roster = self.make_span()
        out, det = root / "v.json", root / "d.json"
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
            rc = i34.main(["--roster", str(roster), "--custody", str(root), "--out", str(out), "--detail-out", str(det),
                           "--runtime-config", str(REPO / "configs/align/v4/r1_runtime.json")])
        self.assertEqual(rc, 0)
        v = json.loads(out.read_text())
        self.assertEqual(v, {"dev-03-s01/L001": {"sidecar_coverage": True, "km003c_clean": True},
                             "dev-03-s01/L002": {"sidecar_coverage": False, "km003c_clean": False},
                             "dev-03-s01/L003": {"sidecar_coverage": False, "km003c_clean": False}})
        d = json.loads(det.read_text())
        self.assertEqual(d["span_trailers"][0]["stop_reason"], "signal 15")
        self.assertNotIn(self.SENTINEL_HEX, out.read_text() + det.read_text())

    def test_span_dir_override(self):
        root, roster = self.make_span()
        moved = self.tmp() / "elsewhere"
        shutil.move(str(root / "dev-03-s01"), str(moved))
        v, _ = i34.judge_custody(json.loads(roster.read_text()), i34.span_dirs(root, [f"dev-03-s01={moved}"]), KEYS)
        self.assertTrue(v["dev-03-s01/L001"]["sidecar_coverage"])


if __name__ == "__main__":
    unittest.main()
