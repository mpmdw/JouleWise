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
from tests.cadence import look_minirepo


def i34_sha(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

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


def stream(name="stream-0001.jsonl", start_s=-10, end_s=230, poll_s=0.2, sps=50, stop="signal 15", skip=None,
           header=True, trailer=True, status="streaming", empty=None):
    """A stream as read_meter_stream returns it: polls every poll_s, each carrying sps * poll_s samples; polls in
    ``skip`` (a, b) seconds are absent; polls in ``empty`` (a, b) seconds carry n = 0."""
    step = round(poll_s * NS)
    stamps = [T0 + start_s * NS + i * step for i in range(int((end_s - start_s) / poll_s) + 1)]
    if skip:
        stamps = [t for t in stamps if not (T0 + round(skip[0] * NS) <= t < T0 + round(skip[1] * NS))]
    per = round(sps * poll_s)
    polls = [(t, 0 if empty and T0 + round(empty[0] * NS) <= t < T0 + round(empty[1] * NS) else per) for t in stamps]
    return {"name": name,
            "header": {"k": "h", "status": status, "poll_s": poll_s, "sps": sps, "start_real_ns": T0 + start_s * NS}
            if header else None,
            "trailer": {"k": "t", "polls": len(stamps), "empties": 3, "bad": 1, "usb_errors": 0, "stop_reason": stop}
            if trailer else None,
            "polls": polls}


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
        two = i34.rule4(INTERVAL, [stream(skip=(100.1, 101.9), sps=60)])      # stamps 100.0 and 102.0; samples kept
        self.assertAlmostEqual(two["max_gap_s"], 2.0)
        self.assertTrue(two["pass"], two)
        sparse = i34.rule4(INTERVAL, [stream(skip=(50.1, 51.9)), ] )
        self.assertTrue(sparse["pass"])
        many = dict(stream())
        many["polls"] = [p for i, p in enumerate(many["polls"]) if i % 60 != 0]     # ~1.7 % missing
        r = i34.rule4(INTERVAL, [many])
        self.assertLess(r["coverage_fraction"], 0.99)
        self.assertIn("meter samples under 99 % of the nominal rate", r["reasons"])
        short = dict(stream())
        short["polls"] = [(t, n - 1) for t, n in short["polls"]]                        # 9 of 10 samples a poll
        self.assertIn("meter samples under 99 % of the nominal rate", i34.rule4(INTERVAL, [short])["reasons"])

    def test_empty_polls_cover_nothing(self):
        """Sol cold seat N5: a stretch of polls with n = 0 is a gap, and its samples are missing, however regular
        the poll stamps are."""
        r = i34.rule4(INTERVAL, [stream(empty=(60, 160))])
        self.assertFalse(r["pass"])
        self.assertIn("meter gap over 2 s", r["reasons"])
        self.assertIn("meter samples under 99 % of the nominal rate", r["reasons"])
        self.assertAlmostEqual(r["max_gap_s"], 100.2, places=3)            # the last full poll before 60 s to 160 s
        ok = i34.rule4(INTERVAL, [stream(empty=(60, 61))])                      # one second of empty polls
        self.assertLessEqual(ok["max_gap_s"], 2.0)

    def test_two_streams_and_a_stream_outside_the_interval(self):
        first = stream(name="stream-0001.jsonl", start_s=-10, end_s=100, stop="signal 15")
        second = stream(name="stream-0002.jsonl", start_s=100, end_s=230, stop="signal 15")
        second["polls"] = second["polls"][1:]
        old = stream(name="stream-0000.jsonl", start_s=-500, end_s=-300, stop="consecutive USB errors")
        r = i34.rule4(INTERVAL, [old, first, second])
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["streams"], ["stream-0001.jsonl", "stream-0002.jsonl"])
        first["trailer"]["stop_reason"] = "consecutive USB errors"
        self.assertFalse(i34.rule4(INTERVAL, [old, first, second])["pass"])

    def test_sample_rate_must_agree(self):
        self.assertIn("the header's nominal sample rate (sps) is missing or differs between streams",
                      i34.rule4(INTERVAL, [stream(start_s=-10, end_s=100),
                                           stream(name="b", start_s=100, end_s=230, sps=10)])["reasons"])
        no_sps = stream()
        del no_sps["header"]["sps"]
        self.assertIn("the header's nominal sample rate (sps) is missing or differs between streams",
                      i34.rule4(INTERVAL, [no_sps])["reasons"])


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
        self.assertEqual(s["polls"], [(T0 + i * 200_000_000, 1) for i in range(6)])
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

    def test_rich_telemetry_value_fields_are_never_parsed(self):
        """Sol cold seat 1: only the two stamps are taken; no value field of a rich-telemetry line is parsed.
        The energy fields are written as bytes no JSON parser accepts: any decode of such a line raises."""
        b = self.make_bundle()
        good = [json.loads(l) for l in (b / "rich_telemetry.jsonl").read_text().splitlines()]
        lines = []
        for r in good:
            lines.append('{"index": %d, "timestamp_s": %r, "elapsed_ns": %d, "gpu": {"gpu_energy": NOT_JSON_4242, '
                         '"dvfm_states": [{"freq": 1380, "used_ns": BAD}]}, "processor_combined_power_w": 31.5x}'
                         % (r["index"], r["timestamp_s"], r["elapsed_ns"]))
        (b / "rich_telemetry.jsonl").write_text("\n".join(lines) + "\n")
        decoded = []
        real = json.loads

        def spy(s_, *a, **k):
            decoded.append(s_ if isinstance(s_, str) else s_.decode())
            return real(s_, *a, **k)
        with unittest.mock.patch.object(i34.json, "loads", spy):
            supports = i34.read_pm_supports(b)
        self.assertEqual(len(supports), len(good))
        self.assertEqual(supports[0]["end_ns"] - supports[0]["start_ns"], good[0]["elapsed_ns"])
        self.assertEqual(decoded, [])                                         # json.loads never called
        self.assertNotIn("4242", json.dumps(supports))

    def test_rich_telemetry_line_without_exactly_one_stamp_gives_no_support(self):
        b = self.make_bundle()
        (b / "rich_telemetry.jsonl").write_text(
            '{"timestamp_s": 1.0, "elapsed_ns": 5, "gpu": {"timestamp_s": 2.0}}\n{"elapsed_ns": 5}\n')
        self.assertEqual(i34.read_pm_supports(b), [])

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
        (sdir / "runner_receipt.json").write_text(json.dumps({"roster": ["L001", "L002", "L003"], "started": {"epoch_s": 1.0},
                                                              "synthetic": True}))
        (sdir / "legs" / "L003").mkdir(parents=True)
        (sdir / "legs" / "L003" / "leg_record.json").write_text(json.dumps({"result": {}}))
        meter = sdir / "hazards" / "meter"
        meter.mkdir(parents=True)
        s = stream()
        lines = [json.dumps(s["header"], sort_keys=True)]
        lines += ['{"k":"b","tx":1,"rx":2,"rt":%d,"n":%d,"p":"%s","smc":{"PDTR":1.5}}' % (t, n, self.SENTINEL_HEX)
                  for t, n in s["polls"]]
        lines.append(json.dumps(s["trailer"], sort_keys=True))
        (meter / "stream-0001.jsonl").write_text("\n".join(lines) + "\n")
        roster = root / "roster.json"
        roster.write_text(json.dumps([{"span_id": "dev-03-s01", "block_id": "dev-03", "role": "fit",
                                       "t0_local_date": "2026-11-16"}]))
        return root, roster

    def test_main_writes_the_interface_shape(self):
        mini = look_minirepo.mini_repo(self)
        root, roster = self.make_span()
        out, det = root / "v.json", root / "d.json"
        r = look_minirepo.py(mini, "joulewise/cadence_looks/inclusion_34.py", "--roster", roster, "--custody", root,
                             "--manifest", mini / look_minirepo.MANIFEST, "--allow-draft", "--out", out,
                             "--detail-out", det)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        v = json.loads(out.read_text())
        self.assertEqual(v, {"dev-03-s01/L001": {"sidecar_coverage": True, "km003c_clean": True},
                             "dev-03-s01/L002": {"sidecar_coverage": False, "km003c_clean": False},
                             "dev-03-s01/L003": {"sidecar_coverage": False, "km003c_clean": False}})
        d = json.loads(det.read_text())
        self.assertEqual(d["span_trailers"][0]["stop_reason"], "signal 15")
        self.assertEqual(d["pins"]["runtime_config_sha256"],
                         i34_sha(mini / "configs/align/v4/r1_runtime.json"))
        self.assertNotIn(self.SENTINEL_HEX, out.read_text() + det.read_text())

    def test_allow_draft_refuses_custody_that_is_not_synthetic(self):
        """Mythos N2: --allow-draft is for synthetic custody only, and the detail records it."""
        mini = look_minirepo.mini_repo(self)
        root, roster = self.make_span()
        out, det = root / "v.json", root / "d.json"
        rec = root / "dev-03-s01" / "runner_receipt.json"
        doc = json.loads(rec.read_text())
        del doc["synthetic"]
        rec.write_text(json.dumps(doc))
        r = look_minirepo.py(mini, "joulewise/cadence_looks/inclusion_34.py", "--roster", roster, "--custody", root,
                             "--manifest", mini / look_minirepo.MANIFEST, "--allow-draft", "--out", out)
        self.assertEqual(r.returncode, 1)
        self.assertIn("--allow-draft on custody that is not synthetic: dev-03-s01", r.stdout)
        self.assertFalse(out.exists())
        doc["synthetic"] = True
        rec.write_text(json.dumps(doc))
        r = look_minirepo.py(mini, "joulewise/cadence_looks/inclusion_34.py", "--roster", roster, "--custody", root,
                             "--manifest", mini / look_minirepo.MANIFEST, "--allow-draft", "--out", out,
                             "--detail-out", det)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        d = json.loads(det.read_text())
        self.assertIs(d["allow_draft"], True)
        self.assertIn("joulewise/cadence_looks/inclusion_34.py", d["pins"]["code_sha256"])

    def test_main_verifies_the_pins_before_opening_custody(self):
        """Mythos 3 / Sol 9 and Mythos 12: a changed pinned file (here the sensor policy) refuses the run, and
        no custody file is touched; a committed manifest needs its LOOKS.json row; the roster is a list."""
        mini = look_minirepo.mini_repo(self)
        root, roster = self.make_span()
        out = root / "v.json"
        cfg = mini / "configs/align/v4/r1_runtime.json"
        cfg.write_text(cfg.read_text().replace('"Tf08"', '"TV1h"', 1))
        r = look_minirepo.py(mini, "joulewise/cadence_looks/inclusion_34.py", "--roster", roster, "--custody", root,
                             "--manifest", mini / look_minirepo.MANIFEST, "--allow-draft", "--out", out)
        self.assertEqual(r.returncode, 1)
        self.assertIn("r1_runtime.json sha256 differs from the pin", r.stdout)
        self.assertFalse(out.exists())
        mini = look_minirepo.mini_repo(self)
        r = look_minirepo.py(mini, "joulewise/cadence_looks/inclusion_34.py", "--roster", roster, "--custody", root,
                             "--manifest", mini / look_minirepo.MANIFEST, "--out", out)          # no --allow-draft
        self.assertEqual(r.returncode, 1)
        self.assertIn("needs status 'committed'", r.stdout)
        self.assertIn("LOOKS.json lists this look as 'draft', not committed", r.stdout)
        self.assertFalse(out.exists())
        wrapped = root / "roster-dict.json"
        wrapped.write_text(json.dumps({"roster": json.loads(roster.read_text())}))
        r = look_minirepo.py(mini, "joulewise/cadence_looks/inclusion_34.py", "--roster", wrapped, "--custody", root,
                             "--manifest", mini / look_minirepo.MANIFEST, "--allow-draft", "--out", out)
        self.assertEqual(r.returncode, 1)
        self.assertIn("the roster is a JSON list", r.stdout)

    def test_type_t_legs_are_never_opened(self):
        """Sol 2 / Mythos 12: a type-T leg (spec.leg_type) is never opened; a legacy spec.type is not a selector."""
        root, roster = self.make_span()
        sdir = root / "dev-03-s01"
        rec = sdir / "legs" / "L001" / "leg_record.json"
        rec.write_text(json.dumps({"spec": {"leg_type": "T"}, "result": {"bundle": "b"}}))
        opened = []
        real_open = builtins.open

        def spy(file, *a, **k):
            opened.append(str(file))
            return real_open(file, *a, **k)
        with unittest.mock.patch.object(builtins, "open", spy), unittest.mock.patch.object(io, "open", spy):
            v, d = i34.judge_custody(json.loads(roster.read_text()), i34.span_dirs(root), KEYS)
        self.assertEqual(v["dev-03-s01/L001"], {"sidecar_coverage": False, "km003c_clean": False})
        self.assertEqual(d["legs"]["dev-03-s01/L001"]["rule3"]["reasons"], ["type T: never read (RL-166 Q14)"])
        self.assertFalse([p for p in opened if "/legs/L001/runtime/" in p], opened)
        rec.write_text(json.dumps({"spec": {"leg_type": "A", "type": "T"}, "result": {"bundle": "b"}}))
        v, _ = i34.judge_custody(json.loads(roster.read_text()), i34.span_dirs(root), KEYS)
        self.assertTrue(v["dev-03-s01/L001"]["sidecar_coverage"])            # the legacy field selects nothing

    def test_the_sensor_policy_resolves_from_the_module_not_the_working_directory(self):
        self.assertEqual(i34.REPO, REPO)
        self.assertTrue((i34.REPO / i34.RUNTIME_CONFIG).is_file())

    def test_span_dir_override(self):
        root, roster = self.make_span()
        moved = self.tmp() / "elsewhere"
        shutil.move(str(root / "dev-03-s01"), str(moved))
        v, _ = i34.judge_custody(json.loads(roster.read_text()), i34.span_dirs(root, [f"dev-03-s01={moved}"]), KEYS)
        self.assertTrue(v["dev-03-s01/L001"]["sidecar_coverage"])



class SoakRetries(CustodyVerdictFile):
    """RL-171 and RL-172a: the soak-retry print, from receipt fields only. A retried-then-accepted soak is no stop."""

    REFUSED = "soak exit 5: the idle soak failed its settle or quiet check"

    def set_receipt(self, sdir, attempts, rcs=None):
        """soak_attempts and the matching soak steps (rc 2 for a refused attempt unless ``rcs`` says otherwise)."""
        rec = sdir / "runner_receipt.json"
        doc = json.loads(rec.read_text())
        doc.pop("soak_attempts", None)
        doc["steps"] = [{"name": "frozen", "rc": 0}, {"name": "soak-blackout-wait", "rc": 0}]
        if attempts is not None:
            doc["soak_attempts"] = attempts
            if isinstance(attempts, list):
                for i, a in enumerate(attempts):
                    rc = rcs[i] if rcs else (2 if isinstance(a, dict) and a.get("refused") else 0)
                    doc["steps"].append({"name": "soak" if i == 0 else f"soak.a{i + 1}", "rc": rc,
                                         **({"error": f"SoakRefusal: {self.REFUSED}"} if rc else {})})
        rec.write_text(json.dumps(doc))
        return doc

    def two(self, **first):
        return [{"attempt": 1, "refused": self.REFUSED, "output_dir": "soak.rejected1", **first},
                {"attempt": 2, "refused": None, "output_dir": "soak"}]

    def test_absent_field_is_one_attempt(self):
        root, _ = self.make_span()
        out = i34.soak_retries({"dev-03-s01": root / "dev-03-s01"})
        self.assertEqual(out["spans"]["dev-03-s01"],
                         {"attempts": 1, "field_present": False, "accepted": True, "retried": []})
        self.assertEqual((out["spans_with_retry"], out["accepted_after_retry"], out["stopped_by_soak"]), (0, 0, 0))

    def test_kind_not_recorded_unless_a_receipt_field_names_it(self):
        root, _ = self.make_span()
        sdir = root / "dev-03-s01"
        self.set_receipt(sdir, self.two())
        (sdir / "soak.stderr.log").write_text("soak refused: idle soak has unresolved slope\n")   # never opened
        out = i34.soak_retries({"dev-03-s01": sdir})
        self.assertEqual(out["spans"]["dev-03-s01"]["retried"],
                         [{"attempt": 1, "kind": "kind not recorded", "read_from": None}])
        self.assertEqual(out["retried_by_kind"], {"slope": 0, "load": 0, "kind not recorded": 1})
        self.assertEqual((out["spans_with_retry"], out["accepted_after_retry"], out["stopped_by_soak"]), (1, 1, 0))
        self.set_receipt(sdir, self.two(refusal_kind="load"))
        out = i34.soak_retries({"dev-03-s01": sdir})
        self.assertEqual(out["spans"]["dev-03-s01"]["retried"],
                         [{"attempt": 1, "kind": "load", "read_from": "receipt soak_attempts[].refusal_kind"}])

    def test_no_log_or_soak_file_is_opened(self):
        root, _ = self.make_span()
        sdir = root / "dev-03-s01"
        self.set_receipt(sdir, self.two())
        opened = []
        real_open = Path.open

        def spy(self, *a, **k):
            opened.append(self.name)
            return real_open(self, *a, **k)
        with unittest.mock.patch.object(Path, "open", spy), \
                unittest.mock.patch("builtins.open", side_effect=AssertionError("builtins.open")):
            i34.soak_retries({"dev-03-s01": sdir})
        self.assertEqual(set(opened), {"runner_receipt.json"})

    def test_a_soak_refused_twice_or_interrupted_stopped_the_span(self):
        root, _ = self.make_span()
        sdir = root / "dev-03-s01"
        self.set_receipt(sdir, [{"attempt": 1, "refused": self.REFUSED}, {"attempt": 2, "refused": self.REFUSED}])
        out = i34.soak_retries({"dev-03-s01": sdir})
        self.assertEqual((out["spans_with_retry"], out["accepted_after_retry"], out["stopped_by_soak"]), (1, 0, 1))
        self.set_receipt(sdir, self.two(), rcs=[2, 143])                # the retry interrupted: refused None, rc 143
        out = i34.soak_retries({"dev-03-s01": sdir})
        self.assertEqual((out["spans_with_retry"], out["accepted_after_retry"], out["stopped_by_soak"]), (1, 0, 1))

    def test_attempts_that_disagree_with_the_steps_refuse(self):
        root, _ = self.make_span()
        sdir = root / "dev-03-s01"
        for bad in ({"attempt": 1}, [{"attempt": 2, "refused": None}],
                    [{"attempt": 1, "refused": None}, {"attempt": 2, "refused": None}], [{"attempt": 1, "refused": 5}]):
            self.set_receipt(sdir, bad)
            with self.assertRaises(ValueError):
                i34.soak_retries({"dev-03-s01": sdir})
        doc = self.set_receipt(sdir, self.two())
        doc["steps"] = [st for st in doc["steps"] if st["name"] != "soak.a2"]   # an attempt with no step
        (sdir / "runner_receipt.json").write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            i34.soak_retries({"dev-03-s01": sdir})
        self.set_receipt(sdir, self.two(), rcs=[0, 0])                   # a refused attempt whose step was rc 0
        with self.assertRaises(ValueError):
            i34.soak_retries({"dev-03-s01": sdir})

    def test_a_retried_then_accepted_soak_is_not_a_stop(self):
        """Every verdict equals the same span's without a retry; the stage journal's soak rc 2 is never read."""
        root, roster = self.make_span()
        sdir = root / "dev-03-s01"
        base, _ = i34.judge_custody(json.loads(roster.read_text()), i34.span_dirs(root), KEYS)
        self.set_receipt(sdir, self.two())
        (sdir / "soak.rejected1").mkdir()
        (sdir / "chain-stages.jsonl").write_text(json.dumps({"stage": "soak", "rc": 2}) + "\n" +
                                                 json.dumps({"stage": "soak.a2", "rc": 0}) + "\n")
        v, d = i34.judge_custody(json.loads(roster.read_text()), i34.span_dirs(root), KEYS)
        self.assertEqual(v, base)
        self.assertEqual(d["soak_retries"]["accepted_after_retry"], 1)
        self.assertEqual(d["soak_retries"]["stopped_by_soak"], 0)
        from joulewise.cadence_looks import schema_check as sc                    # the shape level D carries
        s1 = json.loads((REPO / "docs/process/cadence/looks/lm-interim-01.stage1.schema.json").read_text())
        self.assertEqual(sc.errors(d["soak_retries"], s1["properties"]["soak_retries"]), [])

if __name__ == "__main__":
    unittest.main()
