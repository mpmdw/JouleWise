"""The interim look's two-stage CLI on a synthetic custody copy (RL-166 Q8, Q15). Synthetic only: the custody
layout is written by scripts/cadence_look_synth.py, with energy files (power_trace.csv, meter streams, a level-E
file) planted beside everything stage 1 reads. Stage 1 must open none of them."""
from __future__ import annotations

import builtins
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import plistlib
import shutil
import struct
import tempfile
import unittest
import unittest.mock

try:  # the fit needs numpy; the dependency-free core shards run without it (CI's look-fit job installs it)
    from joulewise.cadence_looks import fit_interim as F
    from scripts import cadence_look_run as R
    from scripts import cadence_look_synth as synth
except ModuleNotFoundError as _exc:  # pragma: no cover
    if _exc.name != "numpy":
        raise
    _NUMPY_MISSING = str(_exc)
else:
    _NUMPY_MISSING = None


def load_tests(loader, tests, pattern):
    """Without numpy the module loads and reports one skip, so shard discovery does not error."""
    if _NUMPY_MISSING is None:
        return tests

    class NumpyMissing(unittest.TestCase):
        @unittest.skip("numpy is not installed; this module runs in CI's look-fit job")
        def test_needs_numpy(self):
            pass
    return loader.loadTestsFromTestCase(NumpyMissing)


STEP3_CANDIDATES = [os.environ.get("JW_STEP3_MODULE"), "/Volumes/JW-EXT/scratch/step3/step3_energy_ratios.py"]


def step3_path():
    """The committed step 3 module if this branch has it, else a byte-identical copy named by the environment."""
    spec = importlib.util.find_spec("joulewise.cadence_looks.step3_energy_ratios")
    if spec is not None:
        return spec.origin
    for p in STEP3_CANDIDATES:
        if p and os.path.isfile(p) and R.sha256_file(p) == R.STEP3_SHA256:
            return p
    return None


def rj(p):
    with open(p) as f:
        return json.load(f)


def wb(p, data):
    with open(p, "wb" if isinstance(data, bytes) else "w") as f:
        f.write(data)


ENERGY_MARKERS = ("power_trace.csv", "segment_energy.json")


class _Custody:
    tmp = None

    @classmethod
    def get(cls):
        if cls.tmp is None:
            cls.tmp = tempfile.mkdtemp(prefix="jw-look-run-")
            cls.tokens = {}
            cls.li, cls.en, cls.tr = synth.build("exact", tokens=cls.tokens)
            cls.paths = synth.write_custody(os.path.join(cls.tmp, "custody"), cls.li, cls.en, cls.tokens)
            cls.root = Path(cls.tmp) / "custody"
            # a level-E decoy beside the custody, as the twin comparison would have it
            with open(cls.root / "segment_energy.json", "wb") as f:
                f.write(synth.dump(cls.en))
        return cls


def tearDownModule():
    if _Custody.tmp:
        shutil.rmtree(_Custody.tmp, ignore_errors=True)


@contextlib.contextmanager
def spy_opens():
    opened = []
    real_open, real_io_open, real_os_open = builtins.open, io.open, os.open

    def rec(fn):
        def wrapper(file, *a, **k):
            if isinstance(file, (str, bytes, os.PathLike)):
                opened.append(os.fsdecode(file))
            return fn(file, *a, **k)
        return wrapper
    with unittest.mock.patch.object(builtins, "open", rec(real_open)), \
            unittest.mock.patch.object(io, "open", rec(real_io_open)), \
            unittest.mock.patch.object(os, "open", rec(real_os_open)):
        yield opened


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = R.main(argv)
    return rc, out.getvalue(), err.getvalue()


class Stage1Custody(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()

    def args(self, out):
        return ["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root),
                "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", out]

    def test_reader_rebuilds_level_r_exactly(self):
        got = R.read_look_input(rj(self.c.paths["roster.json"]), R.span_dirs(self.c.root, None),
                                rj(self.c.paths["rules_3_4.json"]))
        got["synthetic"] = True
        self.assertEqual(synth.dump(got), synth.dump(self.c.li))

    def test_stage1_opens_no_energy_file(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "s1.json")
            with spy_opens() as opened:
                rc, _, err = run_cli(self.args(out))
            self.assertEqual(rc, 0, err)
        self.assertTrue(any(p.endswith("events.jsonl") for p in opened))
        self.assertTrue(any(p.endswith("align_thermal.jsonl") for p in opened))
        bad = [p for p in opened if any(m in p.replace(os.sep, "/") for m in ENERGY_MARKERS)]
        self.assertEqual(bad, [])
        # the meter stream is opened for R-20's clock stamps only (no sample decoded: next test)
        self.assertTrue(all("/hazards/meter/stream-" in p.replace(os.sep, "/") for p in opened if "/hazards/" in p))
        # the decoys exist, so the absence is meaningful
        self.assertTrue(list(self.c.root.glob("*/legs/*/runtime/runs/*/power_trace.csv")))
        self.assertTrue(list(self.c.root.glob("*/hazards/meter/stream-*.jsonl")))

    def test_stage1_decodes_no_power_value(self):
        """rich_telemetry and the plist are read by pattern for stamps and state only: no JSON line of them and no
        plist frame is parsed, so their gpu_energy and gpu_power never become values."""
        real_loads = json.loads

        def loads(s, *a, **k):
            text = s.decode() if isinstance(s, (bytes, bytearray)) else s
            if "gpu_energy" in text or "gpu_power" in text or '"p":' in text:
                raise AssertionError("an energy-bearing line was parsed")
            return real_loads(s, *a, **k)
        with tempfile.TemporaryDirectory() as d, \
                unittest.mock.patch.object(json, "loads", loads), \
                unittest.mock.patch.object(plistlib, "loads", side_effect=AssertionError("plist parsed")), \
                unittest.mock.patch.object(plistlib, "load", side_effect=AssertionError("plist parsed")):
            rc, _, err = run_cli(self.args(os.path.join(d, "s1.json")))
        self.assertEqual(rc, 0, err)

    def test_r7_fan_null_when_a_key_is_missing(self):
        leg = next(leg for leg in self.c.li["legs"] if leg["turn"])
        sid, lid = leg["span_id"], leg["leg_id"]
        with tempfile.TemporaryDirectory() as d:
            bdir = Path(d) / "b"
            shutil.copytree(self.c.root / sid / "legs" / lid / "runtime" / "runs" / "cadence-leg", bdir,
                            ignore=shutil.ignore_patterns("power_trace.csv"))
            rows = [json.loads(x) for x in (bdir / "outputs/align_thermal.jsonl").read_text().splitlines() if x]
            for r in rows:
                if r.get("kind") == "reading":
                    del r["values"]["sensors"]["F1Ac"]
                    break
            with open(bdir / "outputs/align_thermal.jsonl", "w") as f:
                f.write("".join(json.dumps(r) + "\n" for r in rows))
            j = R.journal_readings(bdir, -1e18, 1e18, R.FAN_KEYS)
        self.assertIsNone(j[0]["fan_rpm"])
        self.assertIsNotNone(j[1]["fan_rpm"])

    def test_missing_rules_3_4_verdict_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            v = rj(self.c.paths["rules_3_4.json"])
            v.pop(next(iter(v)))
            p = os.path.join(d, "v.json")
            wb(p, json.dumps(v))
            a = self.args(os.path.join(d, "s1.json"))
            a[a.index("--rules-3-4") + 1] = p
            rc, _, err = run_cli(a)
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", err)


class Stage2Custody(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()
        cls.s3 = step3_path()

    def setUp(self):
        if self.s3 is None:
            self.skipTest("the committed step 3 module is not on this branch and no pinned copy is available")

    def s1(self):
        return F.stage1(self.c.li, hashlib.sha256(synth.dump(self.c.li)).hexdigest())

    def test_energy_reader_reproduces_level_e(self):
        s1 = self.s1()
        got = R.read_segment_energy(s1, R.span_dirs(self.c.root, None), self.s3)
        self.assertEqual(set(got["legs"]), set(self.c.en["legs"]))
        for k, e in got["legs"].items():
            want = self.c.en["legs"][k]
            for a, b in zip(e["gpu_rail"]["segments"], want["gpu_rail"]["segments"]):
                self.assertAlmostEqual(a / b, 1.0, delta=1e-12)
            for x in want["gpu_rail"]["prefix_tails"]:
                self.assertAlmostEqual(e["gpu_rail"]["prefix_tails"][x] / want["gpu_rail"]["prefix_tails"][x], 1.0,
                                       delta=1e-12)
            # DC-in: 2 samples/s against step changes at every boundary; the leg sum is within 0.2 %
            self.assertAlmostEqual(sum(e["dc_in"]["segments"]) / sum(want["dc_in"]["segments"]), 1.0, delta=2e-3)
            for a, b in zip(e["dc_in"]["segments"], want["dc_in"]["segments"]):
                self.assertAlmostEqual(a / b, 1.0, delta=0.03)

    def test_cli_both_stages_and_hash_gate(self):
        with tempfile.TemporaryDirectory() as d:
            s1p, fitp = os.path.join(d, "s1.json"), os.path.join(d, "fit.json")
            rc, out, err = run_cli(["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root),
                                    "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", s1p])
            self.assertEqual(rc, 0, err)
            h = out.split("sha256=")[1].strip()
            self.assertEqual(h, R.sha256_file(s1p))
            rc, _, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", "0" * 64, "--custody",
                                  str(self.c.root), "--step3-module", self.s3, "--out", fitp])
            self.assertEqual(rc, 2)
            self.assertFalse(os.path.exists(fitp))
            rc, out, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", h, "--custody", str(self.c.root),
                                    "--step3-module", self.s3, "--out", fitp])
            self.assertEqual(rc, 0, err)
            fit = rj(fitp)
        F.output_check(fit)
        self.assertEqual(fit["stage1_sha256"], h)
        for ch in F.CHANNELS:
            self.assertEqual(len(fit["channels"][ch]["coefficients"]), 9)

    def test_step3_module_must_be_the_pinned_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s3.py")
            shutil.copy(self.s3, p)
            with open(p, "a") as f:
                f.write("\n# edited\n")
            with self.assertRaises(F.LookInputError):
                R.load_step3(p)


class Meter(unittest.TestCase):

    def test_trapezoid_is_exact_on_a_linear_ramp_with_cuts(self):
        sample = struct.Struct("<HHiiHHHH")
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d)
            (sdir / "hazards/meter").mkdir(parents=True)
            raw0, off = 5 * 10**12, 1_790_000_000 * 10**9 - 5 * 10**12
            lines = [json.dumps({"k": "h", "status": "streaming", "rate_idx": 1, "start_raw_ns": raw0,
                                 "start_real_ns": raw0 + off})]
            for j in range(0, 600, 5):           # 10 samples/s for 60 s, 5 per poll
                raw = b""
                for i in range(j, j + 5):
                    w = 10.0 + 0.5 * (i * 0.1)                  # 10 W + 0.5 W/s
                    raw += sample.pack((i * 100) % 65536, 0, 20_000_000, int(round(w / 20 * 1e6)), 0, 0, 0, 0)
                rx = raw0 + (j + 4) * 100_000_000 + 200_000
                lines.append(json.dumps({"k": "b", "tx": rx - 1_000_000, "rx": rx, "rt": rx + off, "n": 5,
                                         "p": raw.hex(), "smc": {}}))
            lines.append(json.dumps({"k": "t", "polls": 120, "bad": 0, "usb_errors": 0}))
            (sdir / "hazards/meter/stream-0001.jsonl").write_text("\n".join(lines) + "\n")
            m = R.MeterSpan(sdir)
        t0 = m.t[0]
        a, b = t0 + 3.33, t0 + 41.07
        want = 10.0 * (b - a) + 0.25 * ((b - t0) ** 2 - (a - t0) ** 2)
        self.assertAlmostEqual(m.energy(a, b), want, delta=1e-3)
        with self.assertRaises(F.LookInputError):
            m.energy(t0 - 1.0, t0 + 1.0)


class LevelR(unittest.TestCase):

    def test_cli_level_r_round_trip_and_canonical_gate(self):
        li, en, _ = synth.build("exact")
        with tempfile.TemporaryDirectory() as d:
            ip, ep = os.path.join(d, "li.json"), os.path.join(d, "en.json")
            wb(ip, synth.dump(li))
            wb(ep, synth.dump(en))
            s1p, fitp = os.path.join(d, "s1.json"), os.path.join(d, "fit.json")
            with spy_opens() as opened:
                rc, out, err = run_cli(["stage1", "--input", ip, "--out", s1p])
            self.assertEqual(rc, 0, err)
            self.assertFalse([p for p in opened if p.endswith("en.json")])
            h = out.split("sha256=")[1].strip()
            # a re-serialised stage-1 file with the right hash of its new bytes is still refused: not canonical
            s1 = rj(s1p)
            pretty = os.path.join(d, "pretty.json")
            wb(pretty, json.dumps(s1, indent=1))
            rc, _, err = run_cli(["stage2", "--stage1", pretty, "--stage1-sha256", R.sha256_file(pretty),
                                  "--energy", ep, "--out", fitp])
            self.assertEqual(rc, 2)
            rc, _, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", h, "--energy", ep, "--out", fitp])
            self.assertEqual(rc, 0, err)


if __name__ == "__main__":
    unittest.main()


class CliGate(unittest.TestCase):

    def test_cli_refuses_a_wrong_stage1_hash_before_stage2(self):
        li, en, _ = synth.build("exact")
        with tempfile.TemporaryDirectory() as d:
            ip, ep, s1p = os.path.join(d, "li.json"), os.path.join(d, "en.json"), os.path.join(d, "s1.json")
            wb(ip, synth.dump(li))
            wb(ep, synth.dump(en))
            self.assertEqual(run_cli(["stage1", "--input", ip, "--out", s1p])[0], 0)
            with unittest.mock.patch.object(F, "stage2", return_value={}) as st2:
                rc, _, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", "0" * 64, "--energy", ep,
                                      "--out", os.path.join(d, "fit.json")])
            self.assertEqual(rc, 2)
            st2.assert_not_called()


class NoHpEnergy(unittest.TestCase):

    def test_stage2_opens_no_hp01_energy(self):
        c = _Custody.get()
        s3 = step3_path()
        if s3 is None:
            self.skipTest("no pinned step 3 module")
        s1 = F.stage1(c.li, hashlib.sha256(synth.dump(c.li)).hexdigest())
        with spy_opens() as opened:
            e = R.read_segment_energy(s1, R.span_dirs(c.root, None), s3)
        self.assertFalse([p for p in opened if "/hp-01-" in p.replace(os.sep, "/")])
        self.assertFalse([k for k in e["legs"] if k.startswith("hp-01")])


class Rules34Agree(unittest.TestCase):
    """The synthetic custody exercises inclusion_34.py: its verdicts equal the planted ones (type-T legs have no
    bundle in the synthetic custody and are not read at this look, so they are left out)."""

    def test_inclusion_34_verdicts_match_planted(self):
        try:
            from joulewise.cadence_looks import inclusion_34 as I
        except ImportError:
            self.skipTest("inclusion_34.py is not on this branch")
        c = _Custody.get()
        roster = rj(c.paths["roster.json"])
        sensors = rj(Path(R.ROOT) / "configs/align/v4/r1_runtime.json")["sensors"]
        verdicts, _ = I.judge_custody(roster, I.span_dirs(c.root), I.keys(sensors))
        planted = rj(c.paths["rules_3_4.json"])
        t_legs = {leg["leg_key"] for leg in c.li["legs"] if leg["leg_type"] == "T"}
        self.assertEqual({k: v for k, v in verdicts.items() if k not in t_legs},
                         {k: v for k, v in planted.items() if k not in t_legs})
        self.assertIn(False, [v["sidecar_coverage"] for v in planted.values()])
        self.assertIn(False, [v["km003c_clean"] for v in planted.values()])


class ColdSeatFixes(unittest.TestCase):
    """The Mythos and Sol cold seats on the combined look head (5ea1bdee9), in this package's files."""

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()
        cls.roster = rj(cls.c.paths["roster.json"])
        cls.rules = rj(cls.c.paths["rules_3_4.json"])

    def span_copy(self, d, span_id):
        dst = Path(d) / span_id
        shutil.copytree(self.c.root / span_id, dst, ignore=shutil.ignore_patterns("power_trace.csv"))
        return dst

    def entry(self, span_id):
        return next(e for e in self.roster if e["span_id"] == span_id)

    def g0_timeout_leg(self):
        leg = next(x for x in self.c.li["legs"] if x["leg_type"] == "A" and x["turn"] is None)
        self.assertFalse(leg["inclusion"]["g0_released"])
        return leg

    def test_m1_g0_timeout_absent_turns_is_an_exclusion(self):
        leg = self.g0_timeout_leg()
        bundle = self.c.root / leg["span_id"] / "legs" / leg["leg_id"] / "runtime/runs/cadence-leg"
        self.assertTrue((bundle / "events.jsonl").is_file())
        self.assertFalse((bundle / "outputs/align_turns.jsonl").exists())
        span, legs = R.read_span(self.c.root / leg["span_id"], self.entry(leg["span_id"]), self.rules, R.FAN_KEYS)
        got = next(x for x in legs if x["leg_key"] == leg["leg_key"])
        self.assertIsNone(got["turn"])
        self.assertFalse(got["inclusion"]["g0_released"])

    def test_m1_g0_timeout_empty_turns_is_an_exclusion(self):
        leg = self.g0_timeout_leg()
        with tempfile.TemporaryDirectory() as d:
            sdir = self.span_copy(d, leg["span_id"])
            (sdir / "legs" / leg["leg_id"] / "runtime/runs/cadence-leg/outputs/align_turns.jsonl").write_text("")
            _, legs = R.read_span(sdir, self.entry(leg["span_id"]), self.rules, R.FAN_KEYS)
        self.assertIsNone(next(x for x in legs if x["leg_key"] == leg["leg_key"])["turn"])

    def test_m1_included_leg_without_a_turn_refuses(self):
        leg = next(x for x in self.c.li["legs"] if x["turn"] and all(x["inclusion"].values()))
        with tempfile.TemporaryDirectory() as d:
            sdir = self.span_copy(d, leg["span_id"])
            (sdir / "legs" / leg["leg_id"] / "runtime/runs/cadence-leg/outputs/align_turns.jsonl").unlink()
            with self.assertRaisesRegex(F.LookInputError, "included leg"):
                R.read_span(sdir, self.entry(leg["span_id"]), self.rules, R.FAN_KEYS)

    def test_m7_capture_excluded_at_the_look_marks_the_span(self):
        span_id = next(s["span_id"] for s in self.c.li["spans"] if not s["marks"]
                       and any(x["g0_role"] == "consume" for x in self.c.li["legs"] if x["span_id"] == s["span_id"]))
        cap = next(x for x in self.c.li["legs"] if x["span_id"] == span_id and x["g0_role"] == "capture")
        span, _ = R.read_span(self.c.root / span_id, self.entry(span_id), self.rules, R.FAN_KEYS)
        self.assertEqual(span["marks"], [])
        rules = dict(self.rules)
        rules[cap["leg_key"]] = {"sidecar_coverage": True, "km003c_clean": False}      # rule 4 fails at the look
        span, _ = R.read_span(self.c.root / span_id, self.entry(span_id), rules, R.FAN_KEYS)
        self.assertEqual(span["marks"], ["reference from an excluded leg"])

    def test_m13_custody_carries_the_synthetic_flag(self):
        li = R.read_look_input(self.roster, R.span_dirs(self.c.root, None), self.rules)
        self.assertTrue(li["synthetic"])
        with tempfile.TemporaryDirectory() as d:
            sid = self.roster[0]["span_id"]
            sdir = self.span_copy(d, sid)
            rec = rj(sdir / "runner_receipt.json")
            rec.pop("synthetic")
            wb(sdir / "runner_receipt.json", json.dumps(rec))
            li = R.read_look_input([self.roster[0]], R.span_dirs(d, None), self.rules)
        self.assertFalse(li["synthetic"])

    def test_m14_unrun_leg_has_no_cell_and_cannot_be_included(self):
        with tempfile.TemporaryDirectory() as d:
            sid = self.roster[0]["span_id"]
            sdir = self.span_copy(d, sid)
            lid = rj(sdir / "runner_receipt.json")["roster"][-1]
            shutil.rmtree(sdir / "legs" / lid)
            _, legs = R.read_span(sdir, self.roster[0], self.rules, R.FAN_KEYS)
        leg = next(x for x in legs if x["leg_id"] == lid)
        self.assertEqual((leg["cell_prompt_tokens"], leg["turn"]), (None, None))
        self.assertFalse(any(leg["inclusion"].values()))
        li = copy.deepcopy(self.c.li)
        t = next(x for x in li["legs"] if x["turn"] and all(x["inclusion"].values()))
        t["turn"] = None
        with self.assertRaisesRegex(F.LookInputError, "R-21"):
            F.validate_input(li)

    def test_sol2_type_t_only_from_leg_type(self):
        leg = next(x for x in self.c.li["legs"] if x["turn"])
        with tempfile.TemporaryDirectory() as d:
            sdir = self.span_copy(d, leg["span_id"])
            p = sdir / "legs" / leg["leg_id"] / "leg_record.json"
            rec = rj(p)
            rec["spec"]["type"] = "T"                    # the legacy key is ignored (R-21)
            wb(p, json.dumps(rec))
            _, legs = R.read_span(sdir, self.entry(leg["span_id"]), self.rules, R.FAN_KEYS)
        self.assertEqual(next(x for x in legs if x["leg_key"] == leg["leg_key"])["leg_type"], "A")

    def test_roster_is_one_shape(self):
        with self.assertRaises(F.LookInputError):
            R.read_look_input({"roster": self.roster}, R.span_dirs(self.c.root, None), self.rules)

    def test_m4_meter_stream_without_samples_is_skipped(self):
        sid = self.roster[0]["span_id"]
        with tempfile.TemporaryDirectory() as d:
            sdir = self.span_copy(d, sid)
            hdr = (sdir / "hazards/meter/stream-0001.jsonl").read_text().splitlines()[0]
            (sdir / "hazards/meter/stream-0002.jsonl").write_text(hdr + "\n")
            m = R.MeterSpan(sdir)
            self.assertGreater(len(m.t), 100)
            (sdir / "hazards/meter/stream-0001.jsonl").unlink()
            with self.assertRaises(F.LookInputError):
                R.MeterSpan(sdir)

    def test_m4_stage1_preflight_refuses_a_missing_power_trace_before_stage_2(self):
        s1 = F.stage1(self.c.li, "0" * 64)
        R.stage2_preflight(s1, R.span_dirs(self.c.root, None))
        L = next(x for x in s1["legs"] if x["in_energy_fit"])
        with tempfile.TemporaryDirectory() as d:
            self.span_copy(d, L["span_id"])               # the copy carries no power_trace.csv
            sdir_of = R.span_dirs(self.c.root, [f"{L['span_id']}={d}/{L['span_id']}"])
            with self.assertRaisesRegex(F.LookInputError, "power_trace"):
                R.stage2_preflight(s1, sdir_of)

    def test_sol8_one_day_refuses_before_energy(self):
        li = copy.deepcopy(self.c.li)
        days = sorted({s["t0_local_date"] for s in li["spans"] if s["role"] == "fit"})
        keep = {s["span_id"] for s in li["spans"] if s["t0_local_date"] == days[-1] or s["role"] == "describe"}
        li["spans"] = [s for s in li["spans"] if s["span_id"] in keep]
        li["legs"] = [x for x in li["legs"] if x["span_id"] in keep]
        with tempfile.TemporaryDirectory() as d:
            ip, ep, s1p = os.path.join(d, "li.json"), os.path.join(d, "en.json"), os.path.join(d, "s1.json")
            wb(ip, synth.dump(li))
            wb(ep, synth.dump(self.c.en))
            rc, out, err = run_cli(["stage1", "--input", ip, "--out", s1p])
            self.assertEqual(rc, 0, err)
            h = out.split("sha256=")[1].strip()
            with spy_opens() as opened:
                rc, _, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", h, "--energy", ep,
                                      "--out", os.path.join(d, "fit.json")])
        self.assertEqual(rc, 2)
        self.assertIn("two fit days", err)
        self.assertFalse([p for p in opened if p.endswith("en.json")])
