"""The look's one reader of time fields in energy files (joulewise/cadence_looks/time_fields.py; RL-173 E.1).
Synthetic only: every stream, trace and custody copy here is written by this module or by
scripts/cadence_look_synth.py; no fixture, custody, meter or power file of a real run is opened.

* Reader equivalence: ``scan_line`` against ``json.loads`` on a seeded fuzz; ``meter_times`` against the pinned
  decoder (``km003c_parse.parse``) on faulted streams; ``gpu_rows`` / ``gpu_max_uncovered`` against step 3's loader.
* The perturbation test RL-173 E.1 item 1 requires: every power value of a custody copy changed, and inclusion's
  verdict file and detail, level R and stage 1's output byte-identical.
* The trace clauses through the CLI, the stage-2 backstops, the custody binding (Mythos r5 N6), the ledger's
  superseded commitments (N3, N5), and the round-5 rows Sol NEW-2/NEW-3 and Mythos N1/N7/N9.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

from joulewise.cadence_looks import time_fields as TF
from joulewise.cadence_looks import manifest as M
from joulewise.external import km003c_parse as kp

try:  # the stage CLI needs numpy (CI's look-fit job installs it)
    from joulewise.cadence_looks import fit_interim as F
    from scripts import cadence_look_run as R
    from scripts import cadence_look_synth as synth
    from tests.cadence import test_look_run as TLR
except ModuleNotFoundError as _exc:  # pragma: no cover
    if _exc.name != "numpy":
        raise
    F = R = synth = TLR = None

REPO = Path(__file__).resolve().parents[2]
NEEDS_NUMPY = unittest.skipIf(R is None, "numpy is not installed; this class runs in CI's look-fit job")
SAMPLE = struct.Struct("<HHiiHHHH")
OFF = 1_790_000_000 * 10**9 - 10**12              # wall minus raw, synthetic
T0 = 1_790_000_000.0


def tearDownModule():
    if TLR is not None:
        TLR.tearDownModule()


def tmpdir(test, prefix="tf-"):
    d = Path(tempfile.mkdtemp(prefix=prefix))
    test.addCleanup(lambda: shutil.rmtree(d, ignore_errors=True))
    return d


def rj(p):
    with open(p) as f:
        return json.load(f)


# ============================================================================================ synthetic streams
def stream_lines(seconds=200.0, *, step=0.5, per_poll=2, fault=None, rng=None, header_sorted=True, extra_lines=()):
    """A KM003C stream as km003c_monitor.py writes it (compact poll lines with SMC values, a sorted-key header and
    trailer). ``fault(x, poll)`` may change a poll before it is written: x is its first sample's offset in seconds;
    poll is {"dev": [device ms], "rx", "tx", "n", "p": "normal" | "resend" | "empty" | "nonhex", "drop": bool,
    "latency_ns": int}. Values (Vbus, Ibus, the SMC readings) are random."""
    rng = rng or random.Random(5)
    raw0 = int(round(T0 * 1e9)) - OFF
    header = {"k": "h", "schema": "synthetic", "status": "streaming", "reason": None, "rate_idx": 0,
              "sps": 1.0 / step, "poll_s": step * per_poll, "start_raw_ns": raw0, "start_real_ns": raw0 + OFF,
              "start_mono_ns": raw0}
    lines = [json.dumps(header, sort_keys=header_sorted)]
    prev, polls = None, 0
    for j in range(0, int(seconds / step), per_poll):
        x = j * step
        dev = [int(round((j + i) * step * 1000)) for i in range(per_poll)]
        rx = raw0 + dev[-1] * 1_000_000 + 400_000
        poll = {"dev": dev, "rx": rx, "tx": rx - 1_000_000, "n": per_poll, "p": "normal", "drop": False,
                "latency_ns": 0}
        if fault:
            fault(x, poll)
        if poll["drop"]:
            continue
        raw = b"".join(SAMPLE.pack(d % 65536, rng.randrange(65536), rng.randrange(26_000_000, 29_000_000),
                                   rng.randrange(0, 3_000_000), 0, 0, 0, 0) for d in poll["dev"])
        p = {"normal": raw.hex(), "resend": (prev or raw).hex(), "empty": "", "nonhex": "zz" * 40}[poll["p"]]
        if poll["p"] == "normal":
            prev = raw
        rx = poll["rx"] + poll["latency_ns"]
        tx = poll["tx"] + poll["latency_ns"]
        smc = ",".join(f'"{k}":{v!r}' for k, v in (("PDTR", rng.uniform(5, 90)), ("B0AC", rng.randrange(-900, 900)),
                                                   ("B0AV", rng.randrange(11000, 13000))))
        lines.append('{"k":"b","tx":%d,"rx":%d,"rt":%d,"n":%d,"p":"%s","smc":{%s}}' % (tx, rx, rx + OFF, poll["n"],
                                                                                       p, smc))
        polls += 1
    lines += list(extra_lines)
    lines.append(json.dumps({"k": "t", "polls": polls, "empties": 0, "bad": 0, "usb_errors": 0,
                             "elapsed_s": seconds, "end_raw_ns": raw0 + int(seconds * 1e9), "end_mono_ns": raw0,
                             "stop_reason": "signal 15"}, sort_keys=True))
    return lines


def write_stream(d, lines, name="stream-0001.jsonl", final_newline=True):
    p = Path(d) / "hazards" / "meter" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + ("\n" if final_newline else ""))
    return p


def decoder_view(path):
    """What stage 2's decoder gives: (times in epoch s, duplicates, present, aligned, clock stats)."""
    st = kp.parse(path)
    if not st.present:
        return [], (st.samples.duplicates if st.samples else None), False, False, None
    off = int(st.header["start_real_ns"]) - int(st.header["start_raw_ns"])
    return ([(h + off) / 1e9 for h in st.host_ns], st.samples.duplicates, st.present, st.aligned,
            st.fit.stats if st.fit else None)


def in_window(a, b):
    return lambda x, poll: a <= x < b


# ============================================================================================ 1. reader equivalence
class ScanLineEqualsJsonLoads(unittest.TestCase):
    """``scan_line`` accepts exactly what json.loads accepts as an object, with the same keys and values."""

    def same(self, line):
        try:
            want = json.loads(line)
            ok = isinstance(want, dict)
        except ValueError:
            ok = False
        got = TF.scan_line(line)
        if not ok:
            self.assertIsNone(got, line[:200])
            return False
        self.assertIsNotNone(got, line[:200])
        self.assertEqual(set(got), set(want), line[:200])
        for k, w in want.items():
            v = TF.member(got, k)
            if isinstance(w, (dict, list)):
                self.assertIs(v, TF.NESTED, line[:200])
            elif isinstance(w, float) and math.isnan(w):
                self.assertTrue(isinstance(v, float) and math.isnan(v), line[:200])
            else:
                self.assertEqual((type(v), v), (type(w), w), line[:200])
        return True

    @staticmethod
    def value(rng, depth=0):
        r = rng.random()
        if depth < 4 and r < 0.12:
            return {ScanLineEqualsJsonLoads.text(rng): ScanLineEqualsJsonLoads.value(rng, depth + 1)
                    for _ in range(rng.randrange(4))}
        if depth < 4 and r < 0.22:
            return [ScanLineEqualsJsonLoads.value(rng, depth + 1) for _ in range(rng.randrange(4))]
        if r < 0.4:
            return ScanLineEqualsJsonLoads.text(rng)
        if r < 0.55:
            return rng.choice([0, -0, 1, -7, 2**70, -(2**64), 10**20, 123456789])
        if r < 0.75:
            return rng.choice([0.0, -0.0, 1.5, -2.5e-300, 1e308, 3.14159, 1.0e-7, 6.02e23, float("nan"),
                               float("inf"), float("-inf")])
        return rng.choice([True, False, None])

    @staticmethod
    def text(rng):
        alphabet = ['a', 'k', 'b', 'h', '"', '\\', '/', '\b', '\f', '\n', '\r', '\t', '\x00', '\x1f', ' ', 'é',
                    ' ', '\U0001F600', '￿', 'p', 'smc']
        return "".join(rng.choice(alphabet) for _ in range(rng.randrange(6)))

    def mutate(self, rng, line):
        """Lexical faults json.loads may or may not accept: cut, insert, swap, trailing garbage, escapes."""
        ops = [lambda s: s[:rng.randrange(len(s) + 1)],
               lambda s: s + rng.choice([" ", "x", "}", ",", "\t", "  {}", "\n", " 1", "]"]),
               lambda s: rng.choice([" ", "\t\n "]) + s,
               lambda s: (lambda i: s[:i] + rng.choice(list('{}[],:"\\ 0-.eE+tfn')) + s[i:])(rng.randrange(len(s) + 1)),
               lambda s: (lambda i: s[:i] + s[i + 1:])(rng.randrange(max(1, len(s)))),
               lambda s: s.replace(":", " : ", 1),
               lambda s: s.replace('"k"', '"\\u006b"', 1),
               lambda s: s.replace("1", "01", 1),
               lambda s: s.replace(".", "..", 1),
               lambda s: s.replace("e", "E+", 1),
               lambda s: s.replace('"', '"\\ud83d\\ude00', 1),
               lambda s: s.replace('"', '"\\ud800', 1),
               lambda s: s.replace('"', '"\\udc00\\ud800x', 1),
               lambda s: s.replace('"', '"\\u12', 1),
               lambda s: s.replace("NaN", "nan", 1),
               lambda s: s.replace("Infinity", "-Infinity", 1),
               lambda s: s.replace("true", "True", 1)]
        for _ in range(rng.randrange(1, 3)):
            line = rng.choice(ops)(line)
        return line

    def test_a_seeded_fuzz_of_lines(self):
        rng = random.Random(20261115)
        n_ok = n_refused = 0
        for i in range(4000):
            obj = {self.text(rng): self.value(rng) for _ in range(rng.randrange(6))}
            if rng.random() < 0.3:
                obj["k"] = rng.choice(["b", "h", "t", "e", 1, None])
            kw = rng.choice([{}, {"separators": (",", ":")}, {"indent": None, "sort_keys": True},
                             {"ensure_ascii": False}, {"separators": (" , ", " : ")}])
            line = json.dumps(obj, **kw)
            if rng.random() < 0.15:                          # duplicate keys: json keeps the last
                line = line[:-1] + (', ' if len(obj) else '') + '"k": "b", "k": "h"}'
            if rng.random() < 0.55:
                line = self.mutate(rng, line)
            if rng.random() < 0.05:
                line = rng.choice(["[1, 2]", "1", '"s"', "null", "", " ", "{}", "{} {}", '{"a":1}x', '{"a":[1,}'])
            try:
                line.encode("utf-8")              # a stream is UTF-8: a literal lone surrogate cannot occur in one
            except UnicodeEncodeError:
                continue
            if self.same(line):
                n_ok += 1
            else:
                n_refused += 1
        self.assertGreater(n_ok, 1500)
        self.assertGreater(n_refused, 600)

    def test_the_cases_that_matter(self):
        lines = ['{"k":"b","tx":1,"rx":2,"rt":3,"n":2,"p":"ab","smc":{"PDTR":NaN,"B0AC":-Infinity}}',
                 '{"k": "b", "k": "h"}', '{"\\u006b": "h", "x": 1}', '{"a": "\\ud83d\\ude00"}',
                 '{"a": "\\ud83d\\u0041\\ude00"}', '{"a": "\\udc00\\ud800"}', '{"a": 1}  \t',
                 '{"a": 1} x', '{"a": 01}', '{"a": 1.}', '{"a": .5}', '{"a": -}', '{"a": +1}', '{"a": 1e5}',
                 '{"a": 1E-5}', '{"a": -0}', '{"a": "\x01"}', '{"a": "tab\there"}', "{'a': 1}", '{"a": [1, {"b": [2]}]}',
                 '{"a": nan}', '{"a": infinity}', '{"a": "x"', '{"a": "\\x41"}', '{"a" "b"}', '{,}', '{"a":1,}',
                 '{"a": ' + "1" * 4300 + '}', '{"a": ' + "1" * 4301 + '}', '{"a": -' + "1" * 4301 + '}',
                 '{"a": ' + "1" * 5000 + '.5}', '{"smc": {"x": ' + "9" * 4400 + '}, "k": "b"}']
        for line in lines:
            self.same(line)

    def test_deep_nesting_is_refused_not_followed(self):
        line = '{"a": ' + "[" * 70 + "]" * 70 + "}"
        with self.assertRaises(TF.TimeFieldError):
            TF.scan_line(line)
        self.same('{"a": ' + "[" * 40 + "]" * 40 + "}")

    def test_scan_line_never_calls_the_json_decoder(self):
        with unittest.mock.patch.object(json, "loads", side_effect=AssertionError("json.loads")), \
                unittest.mock.patch.object(json.JSONDecoder, "decode", side_effect=AssertionError("decode")), \
                unittest.mock.patch.object(json.JSONDecoder, "raw_decode", side_effect=AssertionError("raw")):
            got = TF.scan_line('{"k":"b","tx":1,"rx":2,"rt":3,"n":0,"p":"","smc":{"PDTR":1.5}}')
        self.assertEqual(TF.member(got, "rt"), 3)


class MeterTimesEqualTheDecoder(unittest.TestCase):
    """``meter_times(read_stream(p))`` gives the pinned decoder's sample times, duplicate count and clock fit."""

    CASES = {
        "healthy": None,
        "counter_step_back_6s": lambda x, p: p["dev"].__setitem__(slice(None), [d - 6000 for d in p["dev"]])
        if x >= 100 else None,
        "counter_forward_6s": lambda x, p: p["dev"].__setitem__(slice(None), [d + 6000 for d in p["dev"]])
        if x >= 100 else None,
        "resend_6s": lambda x, p: p.update(p="resend") if 80 <= x < 86 else None,
        "empty_payload_4s": lambda x, p: p.update(p="empty") if 60 <= x < 64 else None,
        "removed_polls_and_latency": lambda x, p: (p.update(drop=True) if 120 <= x < 123 else
                                                   p.update(latency_ns=2_500_000_000) if 123 <= x < 124 else None),
        "n_zero_polls": lambda x, p: p.update(n=0, p="empty") if 30 <= x < 33 else None,
    }

    def check(self, path):
        view = TF.read_stream(path)
        got = TF.meter_times(view)
        t, dups, present, aligned, stats = decoder_view(path)
        self.assertEqual(got["t"], t)
        self.assertEqual((got["present"], got["aligned"]), (present, aligned))
        self.assertEqual(got["duplicates"], dups)
        self.assertEqual(got["clock_fit"], stats)
        st = kp.parse(path)
        self.assertEqual(view["errors"], len(st.errors))
        raw = kp.load(path)[0]
        self.assertEqual(view["header"], None if raw is None else {k: v for k, v in raw.items() if k in TF.HEADER_KEYS})
        return got

    def test_faulted_streams(self):
        d = tmpdir(self)
        dup = {}
        for name, fault in self.CASES.items():
            p = write_stream(d / name, stream_lines(fault=fault))
            dup[name] = self.check(p)["duplicates"]
        self.assertEqual(dup["healthy"], 0)
        self.assertGreater(dup["counter_step_back_6s"], 10)      # the decoder drops what does not advance
        self.assertGreater(dup["resend_6s"], 5)

    def test_error_lines_a_truncated_last_line_and_an_unsorted_header(self):
        d = tmpdir(self)
        lines = stream_lines(header_sorted=False)
        lines.insert(5, json.dumps({"k": "e", "rx": 999, "raw": "deadbeef"}))
        lines.insert(9, '{"k":"b","tx":1,"rx":2, not json')
        lines.insert(12, '["a list"]')
        p = write_stream(d, lines + ['{"k":"b","tx":1,"rx'], final_newline=False)     # a killed writer's last line
        got = self.check(p)
        self.assertEqual(TF.read_stream(p)["errors"], 3)
        self.assertTrue(got["present"])
        p2 = write_stream(d / "sorted", stream_lines(header_sorted=True))
        self.check(p2)

    def test_header_missing_or_not_streaming_gives_no_sample(self):
        d = tmpdir(self)
        lines = stream_lines()
        p = write_stream(d / "none", lines[1:])
        self.assertFalse(self.check(p)["present"])
        h = json.loads(lines[0])
        h["status"] = "absent"
        p = write_stream(d / "absent", [json.dumps(h, sort_keys=True)] + lines[1:])
        self.assertFalse(self.check(p)["present"])
        del h["status"]                                   # the probe's streams predate the field: streaming
        p = write_stream(d / "nostatus", [json.dumps(h, sort_keys=True)] + lines[1:])
        self.assertTrue(self.check(p)["present"])

    def test_counters_false_reads_no_payload(self):
        d = tmpdir(self)
        p = write_stream(d, stream_lines(fault=lambda x, poll: poll.update(p="nonhex") if x == 50 else None))
        with self.assertRaisesRegex(TF.TimeFieldError, "a payload that is not hex"):
            TF.read_stream(p)
        view = TF.read_stream(p, counters=False)
        self.assertFalse([q for q in view["polls"] if "seq" in q])


class GpuRowsEqualStep3(unittest.TestCase):
    """``gpu_rows`` selects step 3's rows (``load_gpu_trace``) without converting power_w; ``gpu_max_uncovered`` is
    the exact longest uncovered stretch (checked against an independent merge) on the rows stage 2 reads."""

    def trace(self, d, rng):
        rows, x = [], 1_790_000_000.0
        lines = ["timestamp_s,power_w,source,rail,interval_start_s,interval_end_s"]
        while x < 1_790_000_300.0:
            w = rng.choice([1.0, 1.0, 0.5, 0.25, 1.7])
            if rng.random() < 0.05:
                x += rng.choice([0.5, 1.9, 2.0, 2.1, 3.0])               # a hole
            u, v = x, x + w
            lines.append(f"{v!r},{rng.uniform(0, 40)!r},powermetrics,gpu_power,{u!r},{v!r}")
            lines.append(f"{v!r},{rng.uniform(0, 9)!r},powermetrics,cpu_power,{u!r},{v!r}")
            if rng.random() < 0.03:
                lines.append(f"{v!r},1.0,other,gpu_power,{u - 50!r},{v + 50!r}")      # not powermetrics: not read
            if rng.random() < 0.03:                                                  # an overlapping row
                lines.append(f"{v!r},2.0,powermetrics,gpu_power,{u - 0.3!r},{v - 0.1!r}")
            rows.append((u, v))
            x = v
        body = lines[1:]
        rng.shuffle(body)
        (d / "power_trace.csv").write_text("\n".join(lines[:1] + body) + "\n")

    @staticmethod
    def uncovered(rows, a, b):
        """Independent: merge every row clipped to [a, b], then the longest stretch outside the union."""
        iv = sorted((max(a, s), min(b, e)) for s, e in rows if e > a and s < b and min(b, e) > max(a, s))
        worst, edge = 0.0, a
        for s, e in iv:
            worst = max(worst, s - edge)
            edge = max(edge, e)
        return max(worst, b - edge)

    def test_rows_and_uncovered_stretches(self):
        s3, _ = R.load_step3() if R else (None, None)
        if s3 is None:
            self.skipTest("numpy is not installed")
        rng = random.Random(3)
        for k in range(4):
            d = tmpdir(self)
            self.trace(d, rng)
            rows = TF.gpu_rows(d)
            tr = s3.Trace(s3.load_gpu_trace(str(d)))
            self.assertEqual(rows, list(zip(tr.s, tr.e)))
            ss, ee = [r[0] for r in rows], [r[1] for r in rows]
            for _ in range(300):
                a = rng.uniform(1_789_999_990.0, 1_790_000_310.0)
                b = a + rng.choice([0.0, 0.1, 1.0, 5.0, 30.0, 200.0])
                got = TF.gpu_max_uncovered(ss, ee, a, b)
                self.assertEqual(got, R.gpu_max_uncovered_s(tr, a, b))           # stage 2's backstop
                self.assertAlmostEqual(got, self.uncovered(rows, a, b), places=9)

    def test_power_w_is_never_converted_and_a_bad_stamp_refuses(self):
        d = tmpdir(self)
        (d / "power_trace.csv").write_text("timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
                                           "2.0,NOT_A_NUMBER,powermetrics,gpu_power,1.0,2.0\n")
        self.assertEqual(TF.gpu_rows(d), [(1.0, 2.0)])
        (d / "power_trace.csv").write_text("timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
                                           "2.0,1.0,powermetrics,gpu_power,x,2.0\n")
        with self.assertRaisesRegex(TF.TimeFieldError, "without numeric interval stamps"):
            TF.gpu_rows(d)
        (d / "power_trace.csv").write_text("timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
                                           "2.0,1.0,powermetrics,gpu_power,nan,2.0\n")
        with self.assertRaisesRegex(TF.TimeFieldError, "non-finite"):
            TF.gpu_rows(d)
        (d / "power_trace.csv.zst").write_bytes(b"x")
        with self.assertRaisesRegex(TF.TimeFieldError, "desk-compressed"):
            TF.gpu_rows(d)

    def test_support_is_exact_at_the_bound(self):
        t = [0.0, 0.5, 2.5, 3.0]
        self.assertEqual(TF.support(t, 0.5, 2.5), (1, 2, 2.0))
        self.assertEqual(TF.support(t, 0.0, 3.0), (0, 3, 2.0))
        self.assertIsNone(TF.support(t, -0.1, 1.0))
        self.assertIsNone(TF.support(t, 1.0, 3.01))
        self.assertEqual(TF.support(t, 0.6, 0.7), (1, 2, 2.0))


# ============================================================================================ 2. perturbation
def _perturb_custody(root, rng, baseline):
    """Change every power value of a custody copy, keeping every time field (RL-173 E.1 item 1). With ``baseline``
    the stream polls are first rewritten in the monitor's exact line format with SMC values (both copies get this),
    so there are SMC values to change."""
    n = {"trace": 0, "stream": 0, "rich": 0, "plist": 0}
    for p in sorted(root.glob("*/legs/*/runtime/runs/*/power_trace.csv")):
        if baseline:
            continue
        lines = p.read_text().splitlines()
        out = [lines[0]]
        for line in lines[1:]:
            f = line.split(",")
            f[1] = repr(rng.uniform(0.01, 99.0))                          # every rail's power_w
            out.append(",".join(f))
        p.write_text("\n".join(out) + "\n")
        n["trace"] += 1
    for p in sorted(root.glob("*/hazards/meter/stream-*.jsonl")):
        out = []
        for line in p.read_text().splitlines():
            doc = json.loads(line)                     # a synthetic stream this test wrote: parsed to rewrite it
            if doc.get("k") != "b":
                out.append(line)
                continue
            raw = bytes.fromhex(doc["p"])
            smc = doc.get("smc") or {}
            if baseline:
                smc = {"PDTR": 12.5, "B0AC": -40, "B0AV": 12500, "PSTR": 3.25}
            else:
                raw = b"".join(raw[i:i + 2] + bytes(rng.randrange(256) for _ in range(18))
                               for i in range(0, len(raw), 20))           # counter kept, every other byte changed
                smc = {k: (rng.uniform(-99, 99) if isinstance(v, float) else rng.randrange(-9999, 9999))
                       for k, v in smc.items()}
            smc_text = ",".join(f'"{k}":{v!r}' for k, v in smc.items())
            out.append('{"k":"b","tx":%d,"rx":%d,"rt":%d,"n":%d,"p":"%s","smc":{%s}}'
                       % (doc["tx"], doc["rx"], doc["rt"], doc["n"], raw.hex(), smc_text))
        p.write_text("\n".join(out) + "\n")
        n["stream"] += 1
    for p in sorted(root.glob("*/legs/*/runtime/runs/*/rich_telemetry.jsonl")):
        if baseline:
            continue
        out = []
        for line in p.read_text().splitlines():
            doc = json.loads(line)
            doc["gpu"]["gpu_energy"] = rng.randrange(10**7)
            doc["processor_combined_power_w"] = rng.uniform(0, 60)
            out.append(json.dumps(doc))
        p.write_text("\n".join(out) + "\n")
        n["rich"] += 1
    for p in sorted(root.glob("*/legs/*/runtime/runs/*/raw/powermetrics.plist")):
        if baseline:
            continue
        frames = [f for f in p.read_bytes().split(b"\0") if f.strip()]
        out = b""
        for f in frames:
            doc = plistlib.loads(f)
            doc["processor"] = {"gpu_power": rng.uniform(0, 60), "gpu_energy": rng.randrange(10**6),
                                "cpu_power": rng.uniform(0, 30)}
            out += plistlib.dumps(doc) + b"\0"
        p.write_bytes(out)
        n["plist"] += 1
    return n


@NEEDS_NUMPY
class Perturbation(unittest.TestCase):
    """RL-173 E.1 item 1: change every power value of a synthetic custody copy (each rail's power_w; each meter
    sample's voltage, current, marker and aux bytes, keeping its counter; every SMC value; the power fields of
    rich_telemetry.jsonl and raw/powermetrics.plist). inclusion_34.py's verdict file and detail, level R and stage
    1's output must be byte-identical."""

    def run_both(self, d, man):
        outs = {}
        for name in ("a", "b"):
            cwd = d / name
            inc = subprocess.run([sys.executable, "-I", "-B", str(REPO / "joulewise/cadence_looks/inclusion_34.py"),
                                  "--roster", "custody/roster.json", "--custody", "custody", "--manifest", man,
                                  "--allow-draft", "--out", "v.json", "--detail-out", "detail.json"],
                                 cwd=cwd, capture_output=True, text=True, timeout=600)
            self.assertEqual(inc.returncode, 0, inc.stdout + inc.stderr)
            s1 = subprocess.run([sys.executable, "-I", "-B", str(REPO / "scripts/cadence_look_run.py"), "stage1",
                                 "--roster", "custody/roster.json", "--custody", "custody", "--rules-3-4", "v.json",
                                 "--write-input", "li.json", "--out", "s1.json", "--manifest", man, "--allow-draft"],
                                cwd=cwd, capture_output=True, text=True, timeout=600)
            self.assertEqual(s1.returncode, 0, s1.stdout + s1.stderr)
            outs[name] = {f: (cwd / f).read_bytes() for f in ("v.json", "detail.json", "li.json", "s1.json")}
        return outs

    def test_every_power_value_changed_and_stage_1_is_byte_identical(self):
        d = tmpdir(self, "tf-perturb-")
        r = subprocess.run([sys.executable, "-B", str(REPO / "scripts/cadence_look_synth.py"), "--out", str(d / "a"),
                            "--custody", "--scenario", "noisy"], capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr)
        _perturb_custody(d / "a" / "custody", random.Random(1), baseline=True)
        shutil.copytree(d / "a" / "custody", d / "b" / "custody")
        n = _perturb_custody(d / "b" / "custody", random.Random(2), baseline=False)
        self.assertTrue(all(v > 5 for v in n.values()), n)
        # the perturbation reached every file it names, and the decoder sees other watts on the same times
        a, b = d / "a" / "custody", d / "b" / "custody"
        for rel in (p.relative_to(a) for pat in ("*/legs/*/runtime/runs/*/power_trace.csv",
                                                 "*/hazards/meter/stream-*.jsonl",
                                                 "*/legs/*/runtime/runs/*/rich_telemetry.jsonl",
                                                 "*/legs/*/runtime/runs/*/raw/powermetrics.plist")
                    for p in a.glob(pat)):
            self.assertNotEqual((a / rel).read_bytes(), (b / rel).read_bytes(), rel)
        sa, sb = (kp.parse(next(x.glob("dev-01-s02/hazards/meter/stream-*.jsonl"))) for x in (a, b))
        self.assertEqual(sa.host_ns, sb.host_ns)
        self.assertNotEqual(sa.watts, sb.watts)
        outs = self.run_both(d, TLR.pinned_manifest())
        for f in ("v.json", "detail.json", "li.json", "s1.json"):
            self.assertEqual(outs["a"][f], outs["b"][f], f)
        li = json.loads(outs["a"]["li.json"])
        self.assertTrue(any(leg["trace_holes"] for leg in li["legs"]))       # the clauses read both channels
        self.assertTrue(all(sp["custody"]["meter_time_sha256"] for sp in li["spans"]))


# ============================================================================================ 3. trace clauses
def gpu_hole(pt, x, width):
    """Cut [x, x + width] out of a power_trace.csv's gpu_power rows exactly: the rows overlapping it are replaced by
    two rows ending at x and starting at x + width (x and width chosen so both stamps are exact floats)."""
    lines = pt.read_text().splitlines()
    head, rows = lines[0], [r.split(",") for r in lines[1:]]
    keep, cut = [], []
    for f in rows:
        if f[3] == "gpu_power" and float(f[4]) < x + width and float(f[5]) > x:
            cut.append(f)
        else:
            keep.append(f)
    lo, hi = min(float(f[4]) for f in cut), max(float(f[5]) for f in cut)
    keep.append([repr(x), "7.0", "powermetrics", "gpu_power", repr(lo), repr(x)])
    keep.append([repr(hi), "7.0", "powermetrics", "gpu_power", repr(x + width), repr(hi)])
    pt.write_text("\n".join([head] + [",".join(f) for f in keep]) + "\n")


def edit_polls(stream, edit):
    """Rewrite a synthetic stream's poll lines: ``edit(first_sample_epoch_s, doc)`` returns the doc to write, or
    None to remove the poll. The generator writes 2 samples 0.5 s apart per poll, the newest 0.4 ms before rt."""
    out = []
    for line in stream.read_text().splitlines():
        doc = json.loads(line)                        # a synthetic stream this test module's generator wrote
        if doc.get("k") != "b":
            out.append(line)
            continue
        first = (doc["rt"] - 400_000) / 1e9 - 0.5
        doc = edit(first, doc)
        if doc is not None:
            out.append(json.dumps(doc, separators=(",", ":")))
    stream.write_text("\n".join(out) + "\n")


def shift_counters(doc, ms):
    raw = bytearray(bytes.fromhex(doc["p"]))
    for i in range(0, len(raw), 20):
        c = (raw[i] | raw[i + 1] << 8) + ms
        raw[i], raw[i + 1] = c % 65536 & 0xFF, (c % 65536) >> 8
    return dict(doc, p=raw.hex())


def bundle_of(sdir, leg_key):
    lid = leg_key.split("/")[1]
    rec = rj(sdir / "legs" / lid / "leg_record.json")
    return sdir / "legs" / lid / "runtime" / rec["result"]["bundle"]


@NEEDS_NUMPY
class TraceClausesThroughTheCli(unittest.TestCase):
    """RL-173 E.1 items 1 and 2 on the synthetic custody, through the stage-1 CLI."""

    @classmethod
    def setUpClass(cls):
        cls.c = TLR._Custody.get()
        cls.s1 = cls.c.s1_custody()
        cls.fit = {}
        for L in cls.s1["legs"]:
            if L["in_energy_fit"]:
                cls.fit.setdefault(L["span_id"], []).append(L)

    def stage1(self, root=None, span_dirs=(), expect=0):
        d = tmpdir(self)
        out = d / "s1.json"
        argv = ["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(root or self.c.root),
                "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", str(out)]
        for sd in span_dirs:
            argv += ["--span-dir", sd]
        rc, _, err = TLR.run_cli(argv)
        self.assertEqual(rc, expect, err)
        return (rj(out), out) if rc == 0 else (err, None)

    def leg(self, doc, key):
        return next(x for x in doc["legs"] if x["leg_key"] == key)

    def test_gpu_rail_clause_3_s_excluded_2_s_admitted_and_stage_2_runs(self):
        sid = "dev-01-s02"
        A, B = self.fit[sid][1], self.fit[sid][2]
        d = tmpdir(self)
        sdir = d / sid
        shutil.copytree(self.c.root / sid, sdir)
        for L, width in ((A, 3.0), (B, 2.0)):
            seg = L["segments"][3]                                     # a decode block
            x = float(math.floor(seg["wall_start_s"]) + 4)
            self.assertLess(x + width + 1, seg["wall_end_s"])
            gpu_hole(bundle_of(sdir, L["leg_key"]) / "power_trace.csv", x, width)
        s1, p1 = self.stage1(span_dirs=[f"{sid}={sdir}"])
        a, b = self.leg(s1, A["leg_key"]), self.leg(s1, B["leg_key"])
        self.assertEqual(a["trace_holes"]["gpu_rail"]["max_gap_s"], 3.0)
        self.assertEqual((a["trace_holes"]["gpu_rail"]["excluded"], a["trace_holes"]["gpu_rail"]["reason"]),
                         (True, "a stretch over 2 s with no power_trace row"))
        self.assertEqual((a["inclusion"]["sidecar_coverage"], a["inclusion"]["km003c_clean"], a["in_energy_fit"]),
                         (False, True, False))
        self.assertEqual(b["trace_holes"]["gpu_rail"]["max_gap_s"], 2.0)              # exactly 2 s: admitted
        self.assertEqual((b["trace_holes"]["gpu_rail"]["excluded"], b["in_energy_fit"]), (False, True))
        self.assertEqual(s1["counts"]["excluded_by_trace_clause"]["gpu_rail"], 1)
        self.assertEqual(s1["counts"]["in_energy_fit"], self.s1["counts"]["in_energy_fit"] - 1)
        fit = d / "fit.json"
        rc, _, err = TLR.run_cli(["stage2", "--stage1", str(p1), "--stage1-sha256", R.sha256_file(p1), "--custody",
                                  str(self.c.root), "--span-dir", f"{sid}={sdir}", "--out", str(fit)])
        self.assertEqual(rc, 0, err)                                  # the backstop (on at 2 s) admits B's 2.0 s
        files = {f["path"] for f in rj(fit)["custody"]["files"]}
        lid = lambda L: L["leg_key"].split("/")[1]
        self.assertTrue([f for f in files if f.startswith(f"{sid}/legs/{lid(B)}/")])
        self.assertFalse([f for f in files if f.startswith(f"{sid}/legs/{lid(A)}/")])   # A's trace never opened

    def test_meter_attacks_are_excluded_in_stage_1(self):
        """Stage 1 excludes, by rule 4's DC-in clause, each shape of the round-5 reports; none reaches stage 2."""
        root = tmpdir(self) / "custody"
        shutil.copytree(self.c.root, root, ignore=shutil.ignore_patterns("segment_energy.json"))
        stream = lambda sid: root / sid / "hazards/meter/stream-0001.jsonl"
        legs = self.fit["dev-01-s02"]
        mid = lambda L, k=3: L["segments"][k]["wall_start_s"] + 5.0
        C, D, E, G = legs[0], legs[3], legs[4], legs[5]
        cases = {}

        def attacks(first, doc):
            for L, a, b, what in cases.values():
                if a <= first < b:
                    if what == "remove":
                        return None
                    if what == "resend":
                        return dict(doc, p=attacks.prev)
                    if what == "empty":
                        return dict(doc, p="")
            attacks.prev = doc["p"]
            return doc
        x = math.floor(mid(C))
        cases["gap_2_5"] = (C, x + 0.25, x + 2.25, "remove")              # two polls: decoded gap 2.5 s
        x = math.floor(mid(D))
        cases["gap_1_5"] = (D, x + 0.25, x + 1.25, "remove")              # one poll: 1.5 s, admitted
        x = math.floor(mid(E))
        cases["resend_6_5"] = (E, x + 0.25, x + 6.25, "resend")           # 6 polls re-send: 6.5 s
        x = math.floor(mid(G, 2))
        cases["empty_40_5"] = (G, x + 0.25, x + 40.25, "empty")           # 40.5 s of n>0 with no payload
        edit_polls(stream("dev-01-s02"), attacks)
        # latency + removed polls after the leg's end (Sol r5 NEW-1's shape), on its own span
        H = self.fit["dev-02-s01"][1]
        end = max(x["wall_end_s"] for x in H["segments"] + H["prefix_tails"])

        def late(first, doc):
            if end - 0.4 <= first < end + 3.0:
                return None
            if end + 3.0 <= first < end + 4.0:
                return dict(doc, tx=doc["tx"] + 1_500_000_000, rx=doc["rx"] + 1_500_000_000,
                            rt=doc["rt"] + 1_500_000_000)
            return doc
        edit_polls(stream("dev-02-s01"), late)
        # counter steps, each on a span of its own: back 6 s and forward 6 s
        J = self.fit["dev-01-s01"][1]
        K = self.fit["dev-03-s01"][1]
        edit_polls(stream("dev-01-s01"), lambda f, doc: shift_counters(doc, -6000) if f >= mid(J) else doc)
        edit_polls(stream("dev-03-s01"), lambda f, doc: shift_counters(doc, 6000) if f >= mid(K) else doc)
        # a payload that is not hex: every leg of its span fails rule 4, and stage 1 still writes
        hit = []
        edit_polls(stream("dev-02-s02"), lambda f, doc: (hit.append(1), dict(doc, p="zz" * 40))[1] if not hit
                   else doc)
        s1, _ = self.stage1(root)
        dc = lambda L: self.leg(s1, L["leg_key"])["trace_holes"]["dc_in"]
        self.assertAlmostEqual(dc(C)["max_gap_s"], 2.5, places=6)
        self.assertEqual((dc(C)["excluded"], dc(C)["reason"]), (True, "a gap over 2 s between decoded meter samples"))
        self.assertAlmostEqual(dc(D)["max_gap_s"], 1.5, places=6)
        self.assertFalse(dc(D)["excluded"])
        self.assertTrue(self.leg(s1, D["leg_key"])["in_energy_fit"])
        self.assertAlmostEqual(dc(E)["max_gap_s"], 6.5, places=6)
        self.assertAlmostEqual(dc(G)["max_gap_s"], 40.5, places=6)
        self.assertTrue(dc(H)["excluded"])
        for L in (J, K):
            self.assertTrue(dc(L)["excluded"], L["leg_key"])
            self.assertGreater(dc(L)["clock_fit_excess_s"], 2.0, L["leg_key"])
        span = next(sp for sp in s1["roster"]["spans"] if sp["span_id"] == "dev-02-s02")
        self.assertIsNone(span["custody"]["meter_time_sha256"])
        self.assertRegex(span["custody"]["meter_unreadable"], "a payload that is not hex")
        for L in s1["legs"]:
            if L["span_id"] == "dev-02-s02" and L["trace_holes"]:
                self.assertEqual(L["trace_holes"]["dc_in"]["excluded"], True)
                self.assertRegex(L["trace_holes"]["dc_in"]["reason"], r"^a meter stream the decoder cannot read \(")
                self.assertFalse(L["inclusion"]["km003c_clean"])
        for L in (C, E, G, H, J, K):
            got = self.leg(s1, L["leg_key"])
            self.assertEqual((got["inclusion"]["km003c_clean"], got["in_energy_fit"]), (False, False), L["leg_key"])
        n_dc = sum(1 for L in s1["legs"] if L["trace_holes"] and L["trace_holes"]["dc_in"]["excluded"])
        self.assertEqual(s1["counts"]["excluded_by_trace_clause"]["dc_in"], n_dc)
        R.stage2_preflight(s1, R.span_dirs(root, None))         # what stage 2 would open: only admitted legs

    def test_a_zst_sibling_refuses_stage_1_and_inclusion(self):
        sid = "dev-01-s02"
        d = tmpdir(self)
        sdir = d / sid
        shutil.copytree(self.c.root / sid, sdir)
        (sdir / "hazards/meter/stream-0001.jsonl.zst").write_bytes(b"(\xb5/\xfd")
        err, _ = self.stage1(span_dirs=[f"{sid}={sdir}"], expect=2)
        self.assertIn("stream-0001.jsonl.zst is desk-compressed", err)
        inc = subprocess.run([sys.executable, "-I", "-B", str(REPO / "joulewise/cadence_looks/inclusion_34.py"),
                              "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root), "--span-dir",
                              f"{sid}={sdir}", "--manifest", TLR.pinned_manifest(), "--allow-draft",
                              "--out", str(d / "v.json")], capture_output=True, text=True, timeout=600)
        self.assertEqual(inc.returncode, 1, inc.stdout + inc.stderr)
        self.assertIn("REFUSE", inc.stdout)
        self.assertIn("desk-compressed", inc.stdout)
        self.assertFalse((d / "v.json").exists())


# ============================================================================================ 4. backstops
@NEEDS_NUMPY
class StageTwoBackstops(unittest.TestCase):
    """RL-173 E.1 item 3: stage 2 judges both channels again. A stage-1 file that admits a leg the custody would
    not (built by hand: its custody digests re-pointed at the changed copy) refuses, naming the leg and the gap and
    printing no energy number."""

    @classmethod
    def setUpClass(cls):
        cls.c = TLR._Custody.get()

    def hand_built(self, d, change):
        """(stage-1 path, span copy, leg): a CLI stage 1 on the intact custody, the span copied and changed, and
        the stage-1 file's custody digests for that span and leg re-pointed at the copy (canonical form)."""
        s1p = d / "s1.json"
        rc, _, err = TLR.run_cli(["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root),
                                  "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", str(s1p)])
        self.assertEqual(rc, 0, err)
        s1 = rj(s1p)
        sid = "dev-01-s02"
        L = [x for x in s1["legs"] if x["in_energy_fit"] and x["span_id"] == sid][2]
        sdir = d / sid
        shutil.copytree(self.c.root / sid, sdir)
        change(sdir, L)
        span = next(sp for sp in s1["roster"]["spans"] if sp["span_id"] == sid)
        span["custody"]["meter_time_sha256"] = TF.SpanMeter(sdir).digest()
        L["trace_holes"]["gpu_rail"]["rows_sha256"] = TF.rows_digest(TF.gpu_rows(bundle_of(sdir, L["leg_key"])))
        s1p.write_bytes(F.dump(s1))
        return s1p, sdir, L

    def stage2(self, d, s1p, sdir, L):
        out = d / "fit.json"
        rc, stdout, err = TLR.run_cli(["stage2", "--stage1", str(s1p), "--stage1-sha256", R.sha256_file(s1p),
                                       "--custody", str(self.c.root), "--span-dir", f"{L['span_id']}={sdir}",
                                       "--out", str(out)])
        self.assertEqual(rc, 2, err)
        self.assertFalse(out.exists())
        self.assertEqual(stdout, "")
        return err.strip()

    def test_gpu_rail_backstop_names_the_leg_and_the_gap(self):
        d = tmpdir(self)

        def hole(sdir, L):
            seg = L["segments"][4]
            gpu_hole(bundle_of(sdir, L["leg_key"]) / "power_trace.csv", float(math.floor(seg["wall_start_s"]) + 3), 3.0)
        s1p, sdir, L = self.hand_built(d, hole)
        err = self.stage2(d, s1p, sdir, L)
        self.assertEqual(err, f"REFUSED GPU rail: {L['leg_key']}: 3.000 s with no power_trace row inside an "
                              "energy-fit interval")

    def test_dc_in_backstop_names_the_leg_and_the_gap(self):
        d = tmpdir(self)

        def gap(sdir, L):
            x = math.floor(L["segments"][4]["wall_start_s"]) + 3
            edit_polls(sdir / "hazards/meter/stream-0001.jsonl",
                       lambda first, doc: None if x + 0.25 <= first < x + 2.25 else doc)
        s1p, sdir, L = self.hand_built(d, gap)
        err = self.stage2(d, s1p, sdir, L)
        self.assertEqual(err, f"REFUSED DC-in: {L['leg_key']}: a gap of 2.500 s between meter samples inside an "
                              "energy-fit interval")

    def test_meter_span_refuses_times_other_than_the_readers(self):
        sdir = self.c.root / "dev-01-s02"
        sm = TF.SpanMeter(sdir)
        self.assertEqual(R.MeterSpan(sdir, expected_t=sm.t).t, sm.t)
        for bad in (sm.t[:-1], sm.t[:10] + [sm.t[10] + 1e-6] + sm.t[11:], []):
            with self.assertRaisesRegex(F.LookInputError, "DC-in: dev-01-s02: the decoder's sample times differ"):
                R.MeterSpan(sdir, expected_t=bad)
        with unittest.mock.patch.object(R.TF, "span_streams", return_value=[]):
            with self.assertRaisesRegex(F.LookInputError, "DC-in: dev-01-s02: no meter stream"):
                R.MeterSpan(sdir)


# ============================================================================================ 5. custody binding
@NEEDS_NUMPY
class CustodyBinding(unittest.TestCase):
    """Mythos round-5 N6: what stage 2 reads is what stage 1 judged, checked before any energy is read."""

    @classmethod
    def setUpClass(cls):
        cls.c = TLR._Custody.get()
        cls.d = Path(tempfile.mkdtemp(prefix="tf-custody-"))
        cls.s1p = cls.d / "s1.json"
        rc, _, err = TLR.run_cli(["stage1", "--roster", cls.c.paths["roster.json"], "--custody", str(cls.c.root),
                                  "--rules-3-4", cls.c.paths["rules_3_4.json"], "--out", str(cls.s1p)])
        assert rc == 0, err
        cls.s1 = rj(cls.s1p)
        cls.L = [x for x in cls.s1["legs"] if x["in_energy_fit"] and x["span_id"] == "dev-01-s02"][1]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def stage2(self, sdir, out):
        with TLR.spy_opens():
            rc, _, err = TLR.run_cli(["stage2", "--stage1", str(self.s1p), "--stage1-sha256", R.sha256_file(self.s1p),
                                      "--custody", str(self.c.root), "--span-dir", f"dev-01-s02={sdir}",
                                      "--out", str(out)])
        return rc, err, TLR.LAST_RUN

    def test_another_copy_refuses_before_energy(self):
        lid = self.L["leg_key"].split("/")[1]

        def receipt(sdir):
            rec = rj(sdir / "runner_receipt.json")
            rec["note"] = "another copy"
            (sdir / "runner_receipt.json").write_text(json.dumps(rec))

        def leg_record(sdir):
            p = sdir / "legs" / lid / "leg_record.json"
            p.write_text(p.read_text() + " ")

        def meter_stamp(sdir):
            hit = []
            edit_polls(sdir / "hazards/meter/stream-0001.jsonl",
                       lambda f, doc: (hit.append(1), dict(doc, rt=doc["rt"] + 1))[1] if not hit else doc)

        def trace_stamp(sdir):
            pt = bundle_of(sdir, self.L["leg_key"]) / "power_trace.csv"
            lines = pt.read_text().splitlines()
            i = next(i for i, x in enumerate(lines) if ",gpu_power," in x)
            f = lines[i].split(",")
            f[5] = repr(float(f[5]) + 1e-6)
            lines[i] = ",".join(f)
            pt.write_text("\n".join(lines) + "\n")
        for name, change, fragment in (
                ("receipt", receipt, "custody: dev-01-s02/runner_receipt.json is not the file stage 1 read"),
                ("leg_record", leg_record, f"custody: dev-01-s02/legs/{lid}/leg_record.json is not the file stage 1"),
                ("meter", meter_stamp, "custody: dev-01-s02's meter streams are not the ones stage 1 read"),
                ("trace", trace_stamp, f"custody: {self.L['leg_key']}'s power_trace.csv is not the one stage 1 read")):
            d = tmpdir(self)
            sdir = d / "dev-01-s02"
            shutil.copytree(self.c.root / "dev-01-s02", sdir)
            change(sdir)
            rc, err, run = self.stage2(sdir, d / "fit.json")
            self.assertEqual(rc, 2, name)
            self.assertIn(fragment, err, name)
            self.assertFalse((d / "fit.json").exists(), name)
            energy = [(p, who) for p, who in run["frames"] if p.endswith(("power_trace.csv", ".jsonl"))
                      and ("power_trace" in p or "/hazards/meter/" in p.replace(os.sep, "/"))]
            # only the time reader opened an energy file (for its time fields), never the decoder or step 3
            self.assertEqual({who for _, who in energy} - {"joulewise/cadence_looks/time_fields.py"}, set(), name)

    def test_the_fit_records_its_custody(self):
        d = tmpdir(self)
        sdir = d / "dev-01-s02"
        shutil.copytree(self.c.root / "dev-01-s02", sdir)              # an identical copy: admitted
        rc, err, _ = self.stage2(sdir, d / "fit.json")
        self.assertEqual(rc, 0, err)
        cust = rj(d / "fit.json")["custody"]
        self.assertEqual(cust["root"], str(self.c.root.resolve()))
        self.assertEqual(cust["span_dirs"], [{"span_id": "dev-01-s02", "path": str(sdir.resolve())}])
        sdir_of = R.span_dirs(self.c.root, [f"dev-01-s02={sdir}"])
        want = set()
        for L in self.s1["legs"]:
            if L["in_energy_fit"]:
                b = bundle_of(sdir_of(L["span_id"]), L["leg_key"])
                want.add(str(b.relative_to(sdir_of(L["span_id"]).parent) / "power_trace.csv"))
                want.add(f"{L['span_id']}/hazards/meter/stream-0001.jsonl")
        self.assertEqual({f["path"] for f in cust["files"]}, want)
        for f in cust["files"]:
            sid, rest = f["path"].split("/", 1)
            self.assertEqual(f["sha256"], R.sha256_file(sdir_of(sid) / rest))

    def test_step3_refuses_a_changed_leg_record_and_records_its_custody(self):
        d = tmpdir(self)
        run = lambda *extra: subprocess.run(
            [sys.executable, "-I", "-B", str(REPO / "joulewise/cadence_looks/step3_roster.py"), "--manifest",
             TLR.pinned_manifest(), "--allow-draft", "--stage1", str(self.s1p), "--stage1-sha256",
             R.sha256_file(self.s1p), "--custody", str(self.c.root), "--out", str(d / "s3.json"), *extra],
            capture_output=True, text=True, timeout=900)
        r = run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cust = rj(d / "s3.json")["custody"]
        self.assertEqual(cust["root"], str(self.c.root.resolve()))
        self.assertTrue([f for f in cust["files"] if f["path"].endswith("/power_trace.csv")])
        (d / "s3.json").unlink()
        lid = self.L["leg_key"].split("/")[1]
        sdir = d / "dev-01-s02"
        shutil.copytree(self.c.root / "dev-01-s02", sdir)
        p = sdir / "legs" / lid / "leg_record.json"
        p.write_text(p.read_text() + "\n")
        r = run("--span-dir", f"dev-01-s02={sdir}")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(f"REFUSE custody: dev-01-s02/legs/{lid}/leg_record.json is not the file stage 1 read", r.stdout)
        self.assertFalse((d / "s3.json").exists())


# ============================================================================================ 6. the ledger
@NEEDS_NUMPY
class SupersededStage1(unittest.TestCase):
    """RL-173 E.1 item 4 and Mythos round-5 N3/N5 on a mini repository (tests/cadence/look_minirepo.py)."""

    @classmethod
    def setUpClass(cls):
        cls.c = TLR._Custody.get()
        cls.roster_sha = R.sha256_file(cls.c.paths["roster.json"])
        cls.verdicts_sha = R.sha256_file(cls.c.paths["rules_3_4.json"])

    def setUp(self):
        from tests.cadence import look_minirepo as mr
        self.mr = mr
        self.mini = mr.mini_repo(self)
        self.d = tmpdir(self)
        mr.commit(self.mini, roster_sha256=self.roster_sha, verdicts_sha256=self.verdicts_sha)
        self.msha = M.sha256_file(self.mini / mr.MANIFEST)

    def set_row(self, publish=True, **fields):
        led = json.loads((self.mini / M.LOOK_LEDGER_PATH).read_text())
        row = next(r for r in led["looks"] if r["look_id"] == "lm-interim-01")
        for k, v in fields.items():
            if v is None:
                row.pop(k, None)
            else:
                row[k] = v
        (self.mini / M.LOOK_LEDGER_PATH).write_text(json.dumps(led, indent=2) + "\n")
        self.mr.git_commit(self.mini, "ledger", publish=publish)

    def stage1(self, *extra):
        out = self.d / f"s1-{len(list(self.d.iterdir()))}.json"
        r = self.mr.py(self.mini, "scripts/cadence_look_run.py", "stage1", "--roster", self.c.paths["roster.json"],
                       "--custody", self.c.root, "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", out,
                       "--manifest", self.mini / self.mr.MANIFEST, *extra)
        return r, out

    def stage2(self, s1p):
        out = self.d / "fit.json"
        r = self.mr.py(self.mini, "scripts/cadence_look_run.py", "stage2", "--stage1", s1p, "--stage1-sha256",
                       R.sha256_file(s1p), "--custody", self.c.root, "--out", out,
                       "--manifest", self.mini / self.mr.MANIFEST)
        return r, out

    def entry(self, stage1_sha, rx=(), ruling="RL-999", roster=None, verdicts=None):
        return {"stage1_sha256": stage1_sha, "roster_sha256": roster or self.roster_sha,
                "verdicts_sha256": verdicts or self.verdicts_sha, "ruling": ruling,
                "ruled_exclusions": [{"leg_key": k, "rule": r} for k, r in rx]}

    def test_a_typo_corrected_by_a_ruling_lets_stage_2_run(self):
        r, s1p = self.stage1()
        self.assertEqual(r.returncode, 0, r.stderr)
        h = R.sha256_file(s1p)
        typo = h[:-1] + ("0" if h[-1] != "0" else "1")
        self.set_row(status="stage1_committed", stage1_sha256=typo)
        r, out = self.stage2(s1p)
        self.assertEqual(r.returncode, 2)
        self.assertIn(f"names stage-1 sha256 {typo}, not {h}", r.stderr)            # full hashes: the typo shows
        self.set_row(stage1_sha256=h)                                                # corrected, with no entry
        r, out = self.stage2(s1p)
        self.assertEqual(r.returncode, 2)
        self.assertIn(f"stage1 {typo}, roster {self.roster_sha}, verdicts {self.verdicts_sha}", r.stderr)
        self.assertFalse(out.exists())
        self.set_row(stage1_superseded=[self.entry(typo)])                           # the ruling, no exclusion
        r, out = self.stage2(s1p)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(out.exists())
        # a corrected hash needs no new stage 1: a rerun is refused
        rerun = lambda **kw: M.require_inputs_committed(self.mini, "lm-interim-01", self.msha,
                                                        roster_sha256=self.roster_sha,
                                                        verdicts_sha256=self.verdicts_sha, **kw)
        with self.assertRaises(M.ManifestError) as ctx:
            rerun()
        self.assertTrue(any("history already commits a stage 1" in p or "excludes no leg" in p
                            for p in ctx.exception.problems), ctx.exception.problems)

    def test_a_rerun_with_the_ruled_exclusion(self):
        r, s1p = self.stage1()
        self.assertEqual(r.returncode, 0, r.stderr)
        h1 = R.sha256_file(s1p)
        self.set_row(status="stage1_committed", stage1_sha256=h1)
        leg = next(x["leg_key"] for x in rj(s1p)["legs"] if x["in_energy_fit"])
        self.assertNotEqual(leg, "dev-05-s02/L002")
        # without the research lead's entry, stage 1 never runs again
        self.set_row(status="committed", stage1_sha256=None)
        r, out = self.stage1("--ruled-exclusion", f"{leg}=km003c_clean=RL-999")
        self.assertEqual(r.returncode, 2)
        self.assertIn(f"already commits a stage 1 for lm-interim-01 ({h1}) that no ruling supersedes", r.stderr)
        self.assertFalse(out.exists())
        self.set_row(stage1_superseded=[self.entry(h1, [(leg, "km003c_clean")])])
        req = lambda rx, roster=self.roster_sha, verdicts=self.verdicts_sha: M.require_inputs_committed(
            self.mini, "lm-interim-01", self.msha, roster_sha256=roster, verdicts_sha256=verdicts,
            ruled_exclusions=rx)
        rx = {leg: ["km003c_clean", "RL-999"]}
        req(rx)                                                        # exactly the entry's exclusion: admitted
        for bad, fragment in (({}, "are not the ones the row's last superseded entry names"),
                              ({leg: ["sidecar_coverage", "RL-999"]}, "are not the ones"),
                              (dict(rx, **{"dev-05-s02/L002": ["km003c_clean", "RL-999"]}), "are not the ones"),
                              ({leg: ["km003c_clean", "RL-998"]}, f"the ruled exclusion of {leg} does not name RL-999")):
            with self.assertRaises(M.ManifestError) as ctx:
                req(bad)
            self.assertTrue(any(fragment in p for p in ctx.exception.problems), (bad, ctx.exception.problems))
        for kw in ({"roster": "5" * 64}, {"verdicts": "6" * 64}):     # another roster or verdict file
            with self.assertRaises(M.ManifestError) as ctx:
                req(rx, **kw)
            self.assertTrue(any("takes the replaced commitment's roster and verdict file" in p
                                for p in ctx.exception.problems), ctx.exception.problems)
        r, out = self.stage1("--ruled-exclusion", f"{leg}=sidecar_coverage=RL-999")      # the CLI, mismatched
        self.assertEqual(r.returncode, 2)
        self.assertFalse(out.exists())
        r, out = self.stage1("--ruled-exclusion", f"{leg}=km003c_clean=RL-999")
        self.assertEqual(r.returncode, 0, r.stderr)
        s2 = rj(out)
        got = next(x for x in s2["legs"] if x["leg_key"] == leg)
        self.assertEqual(got["ruled_exclusion"], {"rule": "km003c_clean", "ruling": "RL-999"})
        self.assertEqual((got["inclusion"]["km003c_clean"], got["in_energy_fit"]), (False, False))
        self.assertEqual(s2["counts"]["ruled_exclusions"], 1)
        h2 = R.sha256_file(out)
        self.set_row(status="stage1_committed", stage1_sha256=h2)
        M.require_stage1_committed(self.mini, "lm-interim-01", h2, stage1_doc=s2)       # the rerun is committed
        with self.assertRaises(M.ManifestError) as ctx:                                 # a file without it is not
            M.require_stage1_committed(self.mini, "lm-interim-01", h2, stage1_doc=rj(s1p))
        self.assertTrue(any("are not the ones the row's last superseded entry names" in p
                            for p in ctx.exception.problems))
        with self.assertRaises(M.ManifestError) as ctx:                  # a row still naming a stage-1 hash
            req(rx)
        self.assertTrue(any("still names a stage-1 hash" in p for p in ctx.exception.problems))

    def test_history_on_another_remote_branch_is_seen(self):
        """Mythos round-5 N5: a stage-1 commitment published only on a second remote-tracking branch."""
        base = self.mr.git(self.mini, "rev-parse", "HEAD").stdout.strip()
        self.mr.git(self.mini, "checkout", "-q", "-b", "side")
        self.set_row(publish=False, status="stage1_committed", stage1_sha256="7" * 64)
        self.mr.git(self.mini, "update-ref", "refs/remotes/origin/side", "HEAD")
        self.mr.git(self.mini, "checkout", "-q", "main")
        self.assertEqual(self.mr.git(self.mini, "rev-parse", "HEAD").stdout.strip(), base)
        self.set_row(status="stage1_committed", stage1_sha256="8" * 64)
        doc = {"code_sha256": {"input:roster_sha256": self.roster_sha, "input:rules_3_4_sha256": self.verdicts_sha}}
        with self.assertRaises(M.ManifestError) as ctx:
            M.require_stage1_committed(self.mini, "lm-interim-01", "8" * 64, stage1_doc=doc)
        self.assertTrue(any(f"stage1 {'7' * 64}" in p for p in ctx.exception.problems), ctx.exception.problems)
        self.mr.git(self.mini, "update-ref", "-d", "refs/remotes/origin/side")           # unpublished: not seen
        self.mr.git(self.mini, "branch", "-q", "-D", "side")
        M.require_stage1_committed(self.mini, "lm-interim-01", "8" * 64, stage1_doc=doc)

    def test_the_row_subcommand_writes_hashes_only_after_its_checks(self):
        mr = self.mr
        looks = self.mini / M.LOOK_LEDGER_PATH
        row = lambda *a: mr.py(self.mini, "scripts/cadence_look_manifest.py", "row", "--manifest",
                               self.mini / mr.MANIFEST, "--repo", self.mini, *a)
        before = looks.read_bytes()
        r = row("--roster", self.c.paths["roster.json"], "--verdicts", self.c.paths["rules_3_4.json"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("nothing written without --write", r.stdout)
        self.assertEqual(looks.read_bytes(), before)
        r, s1p = self.stage1()                                           # a committed-mode stage 1
        self.assertEqual(r.returncode, 0, r.stderr)
        bad = rj(s1p)
        bad["allow_draft"] = True
        badp = self.d / "bad.json"
        badp.write_bytes(F.dump(bad))
        other = dict(rj(s1p))
        other["code_sha256"] = dict(other["code_sha256"], **{"input:roster_sha256": "5" * 64})
        otherp = self.d / "other.json"
        otherp.write_bytes(F.dump(other))
        for p, fragment in ((badp, "REFUSE"), (otherp, f"records input:roster_sha256 {'5' * 64}")):
            r = row("--stage1", p, "--write")
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn(fragment, r.stdout)
            self.assertEqual(looks.read_bytes(), before)
        r = row("--stage1", s1p, "--write")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        h = R.sha256_file(s1p)
        self.assertIn(f"stage1_sha256: None -> {h}", r.stdout)
        got = next(x for x in json.loads(looks.read_text())["looks"] if x["look_id"] == "lm-interim-01")
        self.assertEqual((got["stage1_sha256"], got["status"]), (h, "stage1_committed"))
        r = row("--roster", self.c.paths["roster.json"], "--verdicts", self.c.paths["rules_3_4.json"], "--write")
        self.assertEqual(r.returncode, 1)                                  # inputs only on a row with no stage 1
        self.assertIn("REFUSE the inputs are written on a committed row with no stage-1 hash", r.stdout)


# ============================================================================================ 7. round-5 rows
@NEEDS_NUMPY
class LedgerGateAgreesWithTheRunMode(unittest.TestCase):
    """Sol round-5 NEW-3: a stage-1 file made without --allow-draft but recording no ledger gate (or made under it
    and recording one) refuses at stage 2 and at step 3 before any energy file opens."""

    @classmethod
    def setUpClass(cls):
        cls.c = TLR._Custody.get()
        cls.d = Path(tempfile.mkdtemp(prefix="tf-gate-"))
        p = cls.d / "s1.json"
        rc, _, err = TLR.run_cli(["stage1", "--roster", cls.c.paths["roster.json"], "--custody", str(cls.c.root),
                                  "--rules-3-4", cls.c.paths["rules_3_4.json"], "--out", str(p)])
        assert rc == 0, err
        cls.s1 = rj(p)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    CASES = ((dict(allow_draft=False, ledger_gate=None), "stage 1 was not made under --allow-draft but records no "
                                                         "ledger gate"),
             (dict(ledger_gate={"commit": "a" * 40, "ref": "refs/remotes/origin/main", "ref_commit": "a" * 40}),
              "stage 1 was made under --allow-draft but records a ledger gate"))

    def write(self, change, name):
        p = self.d / f"{name}.json"
        p.write_bytes(F.dump(dict(self.s1, **change)))
        return p

    def test_stage_2_refuses_before_energy(self):
        for i, (change, fragment) in enumerate(self.CASES):
            p = self.write(change, f"s2-{i}")
            with TLR.spy_opens() as opened:
                rc, _, err = TLR.run_cli(["stage2", "--stage1", str(p), "--stage1-sha256", R.sha256_file(p),
                                          "--custody", str(self.c.root), "--out", str(self.d / "o.json")])
            self.assertEqual(rc, 2, err)
            self.assertIn(fragment, err)
            self.assertEqual(TLR.energy_opens(opened), [])

    def test_step_3_refuses_before_energy(self):
        harness = self.d / "spy_step3.py"
        harness.write_text(SPY_HARNESS)
        for i, (change, fragment) in enumerate(self.CASES):
            p = self.write(change, f"s3-{i}")
            report = self.d / f"report-{i}.json"
            r = subprocess.run([sys.executable, "-I", "-B", str(harness), str(report),
                                str(REPO / "joulewise/cadence_looks/step3_roster.py"), "--manifest",
                                TLR.pinned_manifest(), "--allow-draft", "--stage1", str(p), "--stage1-sha256",
                                R.sha256_file(p), "--custody", str(self.c.root), "--out", str(self.d / "s3.json")],
                               capture_output=True, text=True, timeout=600)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn(fragment, r.stdout)
            opened = rj(report)["opened"]
            self.assertTrue([x for x in opened if x.endswith("s3-%d.json" % i)])       # the spy saw the stage-1 read
            self.assertFalse([x for x in opened if "/runtime/" in x.replace(os.sep, "/")
                              or x.endswith(("power_trace.csv", ".plist", "rich_telemetry.jsonl"))])


SPY_HARNESS = r'''
import json, os, runpy, sys
report, target = sys.argv[1], sys.argv[2]
sys.argv = [target] + sys.argv[3:]
opened = []
def _hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        opened.append(os.fsdecode(args[0]))
sys.addaudithook(_hook)
code = 0
try:
    runpy.run_path(target, run_name="__main__")
except SystemExit as exc:
    code = exc.code
finally:
    with open(report, "w") as f:
        json.dump({"opened": opened}, f)
sys.exit(code)
'''


@NEEDS_NUMPY
class StageOneChecksItsOwnFile(unittest.TestCase):
    """Mythos round-5 N7: stage 1 runs manifest.stage1_problems on its own output before writing it, and the block
    id the validator admits is the one the stage-1 schema admits."""

    BLOCK_IDS = ("dev-01", "hp-01", "reserve-01", "dev-01b", "rehearsal-1112-step-d", "q1", "abc", "ab", "a", "-ab",
                 "Dev-01", "dev_01", "dev 01", "x" * 41, "x" * 42, "0ab", "a-", "a--", "dev-01-", "é-01", " dev-01")

    def by_block_ok(self, bid):
        from joulewise.cadence_looks import schema_check as sc
        schema = json.loads((REPO / "docs/process/cadence/looks/lm-interim-01.stage1.schema.json").read_text())
        return not sc.errors({bid: {"named": 1, "included": 0}},
                             schema["properties"]["counts"]["properties"]["by_block"], schema)

    def test_the_block_id_patterns_agree(self):
        """The stage-1 schema's by_block key, as the shared checker (schema_check) applies it, admits exactly the
        block ids the manifest validator's BLOCK_ID_RE admits."""
        for bid in self.BLOCK_IDS:
            self.assertEqual(bool(M.BLOCK_ID_RE.fullmatch(bid)), self.by_block_ok(bid), repr(bid))

    @unittest.expectedFailure
    def test_a_trailing_newline_block_id(self):
        """Reported, not fixed here: schema_check applies a pattern with re.search, where "$" also matches before a
        final newline (JSON Schema's ECMA-262 "$" does not), so "dev-01\n" passes the schema and not the validator."""
        self.assertEqual(bool(M.BLOCK_ID_RE.fullmatch("dev-01\n")), self.by_block_ok("dev-01\n"))

    def run_input(self, li, extra=None):
        d = tmpdir(self)
        ip, out = d / "li.json", d / "s1.json"
        ip.write_bytes(synth.dump(li))
        rc, _, err = TLR.run_cli(["stage1", "--input", str(ip), "--out", str(out)], extra=extra)
        return rc, err, out

    def test_stage_1_refuses_its_own_file_when_the_shared_check_does(self):
        li, _, _ = synth.build("exact")
        sp = next(s for s in li["spans"] if s["block_id"] == "dev-01")
        sp["block_id"] = "dev-01b"                             # refused by round 4's schema pattern; one pattern now
        rc, err, out = self.run_input(li)
        self.assertEqual(rc, 0, err)
        self.assertIn("dev-01b", rj(out)["counts"]["by_block"])
        sp["block_id"] = "DEV-01"                              # a block id the schema refuses
        rc, err, out = self.run_input(li)
        self.assertEqual(rc, 2)
        self.assertIn("stage 1's own output: stage 1 does not pass its schema", err)
        self.assertFalse(out.exists())
        sp["block_id"] = "dev-01"
        rc, err, out = self.run_input(li, extra={"stage1_problems": ["a planted problem"]})
        self.assertEqual(rc, 2)
        self.assertIn("stage 1's own output: a planted problem", err)
        self.assertFalse(out.exists())


@NEEDS_NUMPY
class RealHeaderShape(unittest.TestCase):
    """Mythos round-5 N1: R-20's header offset is read from a header of the monitor's shape (km003c_monitor.py
    writes it with sort_keys=True, so "k" is not its first key), and a planted 0.5 s clock difference raises
    meter_clock.to_research_lead."""

    MONITOR_KEYS = ("k", "schema", "status", "reason", "model", "vid", "pid", "rate_idx", "sps", "poll_s", "qos",
                    "init_errors", "process_id", "smc_keys", "smc_units", "start_raw_ns", "start_mono_ns",
                    "start_real_ns")

    def test_monitor_header_and_a_planted_clock_difference(self):
        c = TLR._Custody.get()
        sid = "dev-01-s02"
        src = c.root / sid / "hazards/meter/stream-0001.jsonl"
        lines = src.read_text().splitlines()
        old = json.loads(lines[0])                                   # the generator's synthetic header
        h = {"k": "h", "schema": "km003c-monitor.v1", "status": "streaming", "reason": None,
             "model": "POWER-Z KM003C", "vid": "5fc9", "pid": "0063", "rate_idx": old["rate_idx"], "sps": old["sps"],
             "poll_s": old["poll_s"], "qos": "default", "init_errors": [], "process_id": 4242,
             "smc_keys": ["PDTR", "B0AC", "B0AV"], "smc_units": {"PDTR": "W", "B0AC": "mA", "B0AV": "mV"},
             "start_raw_ns": old["start_raw_ns"], "start_mono_ns": old["start_mono_ns"],
             "start_real_ns": old["start_real_ns"]}
        self.assertEqual(tuple(h), self.MONITOR_KEYS)
        text = json.dumps(h, sort_keys=True)
        self.assertFalse(text.startswith('{"k"'))
        d = tmpdir(self)
        sdir = d / sid
        shutil.copytree(c.root / sid, sdir)
        p = sdir / "hazards/meter/stream-0001.jsonl"
        p.write_text("\n".join([text] + lines[1:]) + "\n")
        sm, why = R.span_meter(sdir)
        self.assertIsNone(why)
        off = h["start_real_ns"] - h["start_raw_ns"]
        self.assertEqual(R.meter_offsets(sm), (off, off))
        edit_polls(p, lambda f, doc: dict(doc, rt=doc["rt"] + 500_000_000))      # wall clock 0.5 s off the raw
        sm, _ = R.span_meter(sdir)
        self.assertEqual(R.meter_offsets(sm), (off, off + 500_000_000))
        li = R.read_look_input(rj(c.paths["roster.json"]), R.span_dirs(c.root, [f"{sid}={sdir}"]),
                               rj(c.paths["rules_3_4.json"]))
        mc = F.stage1(li, "0" * 64)["meter_clock"]
        self.assertAlmostEqual(mc["spans"][sid]["end_minus_header_s"], 0.5, places=6)
        self.assertIs(mc["to_research_lead"], True)
        self.assertIs(F.stage1(c.read_r(), "0" * 64)["meter_clock"]["to_research_lead"], False)


class TopLevelKindOnly(unittest.TestCase):
    """Sol round-5 NEW-2: a poll line whose top-level k is "b" but which nests {"k": "h"} and spells a key with an
    escape is never a header, and its SMC values are not converted."""

    def test_nested_and_escaped_kinds(self):
        d = tmpdir(self)
        lines = stream_lines(seconds=20)
        header = lines[0]
        evil = ('{"\\u006b":"h","tx":5,"rx":6,"rt":7,"n":0,"p":"","smc":{"k":"h","status":"streaming",'
                '"start_raw_ns":1,"start_real_ns":2,"rate_idx":3,"PDTR":77.25},"x":{"k":"h"},"k":"b"}')
        self.assertEqual(json.loads(evil)["k"], "b")
        p = write_stream(d, lines[:3] + [evil] + lines[3:])
        converted = []
        real = TF._convert
        with unittest.mock.patch.object(TF, "_convert", lambda kind, text: (converted.append(text), real(kind, text))[1]):
            view = TF.read_stream(p)
        self.assertEqual(view["header"], {k: v for k, v in json.loads(header).items() if k in TF.HEADER_KEYS})
        self.assertEqual(view["header"], view["first_line_header"])
        self.assertIn({"tx": 5, "rx": 6, "rt": 7, "n": 0}, view["polls"])
        self.assertNotIn("77.25", converted)
        self.assertEqual(kp.load(p)[0], json.loads(header))                   # the decoder agrees on the header
        self.assertEqual(TF.meter_times(view)["t"], decoder_view(p)[0])


# ============================================================================================ 8. Mythos r5 N9
class N9Survivors(unittest.TestCase):
    """The six mutants of Mythos round 5 §N9 that no test killed, each held here."""

    def test_stage1_problems_refuses_a_draft_file_in_committed_mode(self):
        doc = json.loads((REPO / "docs/process/cadence/looks/lm-interim-01.json").read_text())
        s1 = {"allow_draft": True, "ledger_gate": None}
        probs = M.stage1_problems(REPO, doc, s1, "0" * 64, allow_draft=False)
        self.assertIn("the stage-1 file was made under --allow-draft", probs)
        self.assertNotIn("the stage-1 file was made under --allow-draft",
                         M.stage1_problems(REPO, doc, s1, "0" * 64, allow_draft=True))

    def plant_cache(self, mini, rel):
        """A cache file where an unprefixed import of ``rel`` would look for its bytecode (a valid one)."""
        import importlib.util
        import py_compile
        src = mini / rel
        cfile = importlib.util.cache_from_source(str(src))
        py_compile.compile(str(src), cfile=cfile, doraise=True)
        return cfile

    def test_each_tool_refuses_a_module_loaded_from_cached_bytecode(self):
        """inclusion, standalone step 3 and assemble each refuse when a repository module they loaded was loaded
        from a cache file: here a wrapper imports the manifest module from a valid __pycache__ entry (no fresh
        prefix can undo that import) and then runs the tool's main()."""
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        self.plant_cache(mini, "joulewise/cadence_looks/manifest.py")
        d = tmpdir(self)
        (d / "s1.json").write_text("{}")
        (d / "roster.json").write_text("[]")
        tools = {"inclusion": ("joulewise.cadence_looks.inclusion_34", ["--roster", d / "roster.json", "--custody", d,
                                                                         "--manifest", mini / mr.MANIFEST,
                                                                         "--allow-draft", "--out", d / "v.json"]),
                 "step3": ("joulewise.cadence_looks.step3_roster", ["--manifest", mini / mr.MANIFEST, "--allow-draft",
                                                                     "--stage1", d / "s1.json", "--stage1-sha256",
                                                                     M.sha256_file(d / "s1.json"), "--custody", d,
                                                                     "--out", d / "s3.json"]),
                 "assemble": ("scripts.cadence_look_manifest", ["assemble", "--manifest", mini / mr.MANIFEST,
                                                                "--stage1", d / "s1.json", "--fit", d / "s1.json",
                                                                "--step3", d / "s1.json", "--analyst-seat", "t",
                                                                "--allow-draft", "--out", d / "o.json"])}
        for name, (module, args) in tools.items():
            wrapper = d / f"wrap_{name}.py"
            wrapper.write_text("import sys\nsys.path.insert(0, %r)\n"
                               "import joulewise.cadence_looks.manifest as m\n"
                               "assert m.__cached__ and m.__spec__.cached, 'loaded from the cache'\n"
                               "import importlib\n"
                               "sys.exit(importlib.import_module(%r).main([str(x) for x in sys.argv[1:]]))\n"
                               % (str(mini), module))
            r = subprocess.run([sys.executable, "-I", str(wrapper), *map(str, args)], capture_output=True, text=True,
                               cwd=str(d), timeout=300)
            self.assertNotEqual(r.returncode, 0, (name, r.stdout, r.stderr))
            self.assertIn("may have run from cached bytecode", r.stdout + r.stderr, name)

    def test_load_step3_executes_the_bytes_it_hashed_whatever_the_import_order(self):
        """In a fresh interpreter with no pycache prefix (the order-independent case: cadence_look_run.py, imported
        first, would set one), a stale cache entry beside a copy of the step 3 file is never what load_step3 runs."""
        d = tmpdir(self)
        copy_ = d / "step3_energy_ratios.py"
        shutil.copy2(REPO / M.STEP3_PATH, copy_)
        from tests.cadence.test_look_manifest import plant_stale_bytecode
        plant_stale_bytecode(copy_, lambda t: t + "\nSTALE = True\n")
        code = ("import sys; sys.path.insert(0, sys.argv[1]); assert sys.pycache_prefix is None\n"
                "from joulewise.cadence_looks import step3_roster as sr\n"
                "from pathlib import Path\n"
                "m = sr.load_step3(path=Path(sys.argv[2]))\n"
                "print('STALE' if hasattr(m, 'STALE') else 'FRESH')\n")
        r = subprocess.run([sys.executable, "-I", "-c", code, str(REPO), str(copy_)], capture_output=True, text=True,
                           timeout=120, env={**os.environ, "TMPDIR": str(d)})
        self.assertEqual(r.stdout.strip(), "FRESH", r.stderr)

    @unittest.skipIf(R is None, "numpy is not installed")
    def test_the_two_stage_cli_removes_its_prefix_at_exit(self):
        """Every look tool removes its fresh pycache prefix at exit; asserted on a private TMPDIR the child
        processes are given, so no other process's prefix can make the test pass or fail (Mythos r5 N9)."""
        d = tmpdir(self)
        private = d / "tmp"
        private.mkdir()
        li, _, _ = synth.build("exact")
        (d / "li.json").write_bytes(synth.dump(li))
        env = {**os.environ, "TMPDIR": str(private)}
        r = subprocess.run([sys.executable, "-I", "-B", str(REPO / "scripts/cadence_look_run.py"), "stage1",
                            "--input", str(d / "li.json"), "--out", str(d / "s1.json"), "--manifest",
                            TLR.pinned_manifest(), "--allow-draft"], capture_output=True, text=True, timeout=600,
                           env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = subprocess.run([sys.executable, "-I", "-B", str(REPO / "scripts/cadence_look_run.py"), "stage1",
                            "--input", str(d / "missing.json"), "--out", str(d / "s2.json"), "--manifest",
                            TLR.pinned_manifest(), "--allow-draft"], capture_output=True, text=True, timeout=600,
                           env=env)
        self.assertEqual(r.returncode, 2)                       # a failing run cleans up too
        self.assertEqual(sorted(p.name for p in private.iterdir()), [])
        # the control: the prefix is made in the private directory (so the empty listing above means something)
        r = subprocess.run([sys.executable, "-I", "-B", "-c",
                            "import sys, os; sys.path.insert(0, sys.argv[1]); sys.argv = ['x']\n"
                            "import atexit; atexit.register = lambda *a, **k: None\n"
                            "from scripts import cadence_look_run as R; print(R._PYC_PREFIX)", str(REPO)],
                           capture_output=True, text=True, timeout=120, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.strip().startswith(str(private)), r.stdout)
        self.assertTrue([p for p in private.iterdir() if p.name.startswith("jw-look-pyc-")])


if __name__ == "__main__":
    unittest.main()
