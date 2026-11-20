"""The look's one reader of TIME fields in energy-bearing files (RL-173 E.1). Opens no energy value.

RL-173 E.1 item 1: "Stage 1 may read time fields of the energy files, and nothing else: the row stamps of
``power_trace.csv`` and each meter sample's device counter. Neither is a power or energy value. It goes through one
dedicated reader." This module is that reader. ``inclusion_34.py`` (rule 4's poll stamps), the stage-1 CLI (the trace
hole clauses, R-20's clock print, the custody digests) and stage 2's pre-energy custody check all read through it.

**What is read.**

* A KM003C stream line is scanned by a validating lexer (``scan_line``) that accepts exactly what ``json.loads``
  accepts and decides the record kind from the line's TOP-LEVEL ``k`` member (Sol round-5 NEW-2: a nested or
  escaped ``k`` never decides). Only whitelisted members are converted: a header's and a trailer's operational keys
  (``HEADER_KEYS``, ``TRAILER_KEYS``); a poll line's ``tx``, ``rx``, ``rt``, ``n`` and, from its payload ``p``, the
  first two bytes of each 20-byte sample, the 16-bit device counter. Every other member (the SMC values, each
  sample's voltage and current bytes, an error line's text) is tokenised to find the next member and dropped
  unconverted.
* From ``power_trace.csv``, the ``gpu_power`` / ``powermetrics`` rows' ``interval_start_s`` and ``interval_end_s``
  (``gpu_rows``). The row is split into fields by the csv module to find those columns; ``power_w`` is never
  converted.

**What it computes.** The decoded sample times the pinned decoder (``joulewise.external.km003c_parse``) gives the
same stream, by running the decoder's own ``samples`` and ``clock_fit`` on a payload that carries the counters and
zero in every value byte (``meter_times``): the unwrap, the duplicate drop and the clock fit read only counters and
poll stamps, so the times are the decoder's times. Stage 2 checks that equality on the real decode (a backstop).
The GPU rail's longest stretch with no row (``gpu_max_uncovered``) is the one definition stage 2 also uses.

The test ``tests/cadence/test_time_fields.py`` changes every power value of a synthetic custody copy and requires
inclusion's verdict file and stage 1's output to be byte-identical.
"""
from __future__ import annotations

import bisect
import csv
import glob
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

NS = 1_000_000_000
MAX_GAP_S = 2.0                     # RL-166 Q7, RL-173 E.1: the gap bound on both channels
CLOCK_FIT_EXCESS_MAX_S = 2.0        # RL-173 E.1 item 2: a leg whose decoder clock-fit excess is over 2 s is excluded
SAMPLE_BYTES = 20                   # km003c_parse.SAMPLE: "<HHiiHHHH"; the first H is the device counter
STREAM_GLOB = "hazards/meter/stream-*.jsonl"
HEADER_KEYS = ("k", "schema", "status", "reason", "rate_idx", "sps", "poll_s", "start_raw_ns", "start_real_ns",
               "start_mono_ns")
TRAILER_KEYS = ("k", "polls", "empties", "bad", "usb_errors", "elapsed_s", "end_raw_ns", "end_mono_ns", "stop_reason")
POLL_KEYS = ("tx", "rx", "rt", "n")
GPU_COLUMNS = ("rail", "source", "interval_start_s", "interval_end_s")


class TimeFieldError(ValueError):
    """A file the reader cannot take apart the way the decoder or step 3 would. Its message names the file and the
    field, never a value."""


class CompressedCustody(TimeFieldError):
    """A ``.zst`` sibling of a file the look reads (Mythos round-5 N8): the custody copy is not decompressed. It
    refuses the look, whichever channel meets it."""


# ============================================================================================ the JSON line lexer
_TOKEN = re.compile(r"""[ \t\n\r]*(?:
     (?P<str>"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*")
    |(?P<lit>true|false|null|NaN|Infinity|-Infinity)
    |(?P<num>-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?)
    |(?P<punct>[{}\[\]:,])
    )""", re.X)
_TAIL_WS = re.compile(r"[ \t\n\r]*\Z")
MAX_DEPTH = 64
NESTED = object()                    # a member whose value is an object or an array: never converted


class _Bad(Exception):
    pass


_ESC = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
_ESC_RE = re.compile(r'\\(?:u([0-9a-fA-F]{4})|(.))')


def _unstring(raw):
    """A JSON string token's text, as json.loads gives it (escapes, and a \\u surrogate pair joined), without
    json.loads: the reader never hands any part of an energy file's line to the JSON decoder."""
    body = raw[1:-1]
    if "\\" not in body:
        return body
    out, pos = [], 0
    for m in _ESC_RE.finditer(body):
        out.append(body[pos:m.start()])
        pos = m.end()
        if m.group(1) is not None:
            out.append(chr(int(m.group(1), 16)))
        else:
            out.append(_ESC[m.group(2)])
    out.append(body[pos:])
    text = "".join(out)
    # json joins a high surrogate followed by a low one into one character
    return text.encode("utf-16", "surrogatepass").decode("utf-16", "surrogatepass") if any(
        0xD800 <= ord(c) <= 0xDFFF for c in text) else text


_LITERALS = {"true": True, "false": False, "null": None, "NaN": float("nan"), "Infinity": float("inf"),
             "-Infinity": float("-inf")}


def _convert(kind, text):
    """One scalar token's value as json.loads gives it: int for an integer literal, float otherwise."""
    if kind == "str":
        return _unstring(text)
    if kind == "lit":
        return _LITERALS[text]
    if any(c in text for c in ".eE"):
        return float(text)
    return int(text)


def _over_int_limit(text):
    """An integer literal longer than ``sys.get_int_max_str_digits()`` digits: ``json.loads`` raises ValueError on
    it (int() of the token), so the decoder keeps the line as an error line; the scanner refuses it the same way."""
    if "." in text or "e" in text or "E" in text:
        return False
    limit = sys.get_int_max_str_digits()
    return bool(limit) and len(text) - text.startswith("-") > limit


def _tokens(s):
    pos, n = 0, len(s)
    while True:
        m = _TOKEN.match(s, pos)
        if m is None or m.end() == pos:
            if _TAIL_WS.match(s, pos):
                return
            raise _Bad()
        pos = m.end()
        kind = m.lastgroup
        text = m.group(kind)
        if kind == "num" and _over_int_limit(text):
            raise _Bad()             # json.loads refuses an integer literal over the interpreter's digit limit
        yield kind, text
        if pos >= n:
            return


def _skip_value(it, first, depth):
    kind, text = first
    if kind in ("str", "lit", "num"):
        return
    if kind != "punct" or text not in "{[":
        raise _Bad()
    if depth > MAX_DEPTH:
        raise TimeFieldError("a JSON line nests deeper than the reader follows")
    close = "}" if text == "{" else "]"
    nxt = next(it, None)
    if nxt == ("punct", close):
        return
    while True:
        if close == "}":
            if nxt is None or nxt[0] != "str" or next(it, None) != ("punct", ":"):
                raise _Bad()
            nxt = next(it, None)
        if nxt is None:
            raise _Bad()
        _skip_value(it, nxt, depth + 1)
        sep = next(it, None)
        if sep == ("punct", close):
            return
        if sep != ("punct", ","):
            raise _Bad()
        nxt = next(it, None)


def scan_line(s):
    """The top-level members of one JSON line as ``json.loads`` would accept it, WITHOUT converting any value:
    ``{key: (kind, raw text)}`` with kind "str", "num" or "lit", or ``{key: (NESTED, None)}`` for an object or array.
    A repeated key keeps its last value, as ``json.loads`` does. Returns None when ``json.loads`` would refuse the
    line or its value is not a JSON object (the decoder then keeps it as an error line and reads no sample from it)."""
    it = _tokens(s)
    try:
        if next(it, None) != ("punct", "{"):
            return None
        out = {}
        nxt = next(it, None)
        if nxt == ("punct", "}"):
            members_done = True
        else:
            members_done = False
        while not members_done:
            if nxt is None or nxt[0] != "str" or next(it, None) != ("punct", ":"):
                return None
            key = _unstring(nxt[1])                    # a member NAME, never a value
            val = next(it, None)
            if val is None:
                return None
            if val[0] == "punct":
                _skip_value(it, val, 1)
                out[key] = (NESTED, None)
            else:
                out[key] = val
            sep = next(it, None)
            if sep == ("punct", "}"):
                break
            if sep != ("punct", ","):
                return None
            nxt = next(it, None)
        if next(it, None) is not None:                 # "Extra data"
            return None
        return out
    except _Bad:
        return None


def member(members, key):
    """The converted value of one whitelisted member: str, int, float, bool or None; NESTED for an object or
    array; KeyError when absent."""
    kind, text = members[key]
    return NESTED if kind is NESTED else _convert(kind, text)


def _kind(members):
    """The record kind: the top-level ``k`` member's string value, else None (km003c_parse.load's item.get("k"))."""
    if members is None or "k" not in members:
        return None
    v = member(members, "k")
    return v if isinstance(v, str) else None


def _pick(members, keys):
    return {k: member(members, k) for k in keys if k in members}


def _counters(text, where):
    """The 16-bit device counter of each 20-byte sample in a poll's payload, as km003c_parse.samples unpacks it
    (``bytes.fromhex`` then ``SAMPLE.iter_unpack``); the other 18 bytes of each sample are not looked at."""
    try:
        raw = bytes.fromhex(text)
    except ValueError:
        raise TimeFieldError(f"{where}: a payload that is not hex") from None
    if len(raw) % SAMPLE_BYTES:
        raise TimeFieldError(f"{where}: a payload that is not whole 20-byte samples")
    return tuple(raw[i] | (raw[i + 1] << 8) for i in range(0, len(raw), SAMPLE_BYTES))


# ============================================================================================ KM003C streams
def span_streams(sdir):
    """The span's KM003C stream files, as stage 2 globs them. Mythos round-5 N8: a ``.zst`` sibling of any file the
    look reads (a desk-compressed custody copy) refuses here, before anything is read: the decoder would read it
    through desk_compress, the stamp readers would not see it."""
    sdir = Path(sdir)
    zst = sorted(glob.glob(str(sdir / (STREAM_GLOB + ".zst"))))
    if zst:
        raise CompressedCustody(f"{sdir.name}: {Path(zst[0]).name} is desk-compressed; the look reads a decompressed "
                             "custody copy that matches its marker")
    return sorted(glob.glob(str(sdir / STREAM_GLOB)))


def read_stream(path, *, counters=True):
    """One stream's time view: {"name", "header", "trailer", "first_line_header", "polls", "errors"}. ``header`` is
    the last line of kind "h" and ``trailer`` the last of kind "t" (km003c_parse.load); ``first_line_header`` is the
    first line when it is a header (rule 4's reading). ``polls`` are the kind-"b" lines in file order, each
    {"tx", "rx", "rt", "n", "seq"} with ``seq`` the payload's counters or None (no payload). A whitelisted member that
    is absent is absent from the dict. With ``counters`` false (rule 4 reads stamps and counts only) no payload is
    taken apart. Raises TimeFieldError on a line the decoder would fail on."""
    path = Path(path)
    data = path.read_bytes().decode("utf-8")           # km003c_parse.load decodes the whole file the same way
    lines = data.split("\n")
    header = trailer = first = None
    polls, errors, seen = [], 0, False
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        is_first, seen = not seen, True
        members = scan_line(line)
        if members is None:
            if number != len(lines):
                errors += 1                            # a protocol error line in the decoder's count
            continue
        kind = _kind(members)
        if kind == "h":
            header = _pick(members, HEADER_KEYS)
            if is_first:
                first = header
        elif kind == "t":
            trailer = _pick(members, TRAILER_KEYS)
        elif kind == "e":
            errors += 1
        elif kind == "b":
            poll = _pick(members, POLL_KEYS)
            if counters and "p" in members:
                pk, ptext = members["p"]
                if pk is NESTED:
                    poll["p_shape"] = "nested"
                else:
                    p = _unstring(ptext) if pk == "str" else None
                    if pk == "str" and p:
                        poll["seq"] = _counters(p, f"{path.name}:{number}")
                    elif pk != "str":
                        poll["p_shape"] = "not a string"
            polls.append(poll)
    return {"name": path.name, "header": header, "trailer": trailer, "first_line_header": first,
            "polls": polls, "errors": errors}


def _is_int(x):
    return type(x) is int


def meter_times(view):
    """The decoder's sample times for one stream, from its time view (km003c_parse.parse, then the stage-2 reader's
    RAW -> REALTIME shift by the header's start_real_ns - start_raw_ns, RL-167 R-20). Returns
    {"name", "present", "aligned", "t" (epoch seconds, the decoder's order), "step_s", "duplicates",
     "clock_fit": stats or None, "fit_error"}. Raises TimeFieldError where the decoder would fail."""
    from joulewise.external import km003c_parse as kp       # the pinned decoder's unwrap and clock fit
    name = view["name"]
    header = view["header"]
    if header is not None and "status" not in header:
        header = {**header, "status": "streaming"}
    out = {"name": name, "present": False, "aligned": False, "t": [], "step_s": None, "duplicates": None,
           "clock_fit": None, "fit_error": None}
    if header is None or header.get("status") != "streaming":
        return out
    for p in view["polls"]:
        if not _is_int(p.get("rx")):
            raise TimeFieldError(f"{name}: a poll line without an integer rx")
        if "p_shape" in p:
            raise TimeFieldError(f"{name}: a poll line whose payload is {p['p_shape']}")
        if "n" in p and not (p["n"] is None or _is_int(p["n"])):
            raise TimeFieldError(f"{name}: a poll line whose n is not an integer")
    polls = sorted(view["polls"], key=lambda b: b["rx"])            # stable, as km003c_parse.parse
    with_samples = [b for b in polls if b.get("n")]
    for b in with_samples:
        if not _is_int(b.get("tx")):
            raise TimeFieldError(f"{name}: a sample-bearing poll line without an integer tx")
    rate = header.get("rate_idx")
    if not _is_int(rate) or rate not in kp.STEP_MS:
        raise TimeFieldError(f"{name}: the header's rate_idx is not one the decoder knows")
    zero = b"\0" * (SAMPLE_BYTES - 2)
    batches = [{"rx": b["rx"], "tx": b["tx"], "n": b["n"],
                "p": b"".join(s.to_bytes(2, "little") + zero for s in b.get("seq") or ()).hex()}
               for b in with_samples]
    s = kp.samples(header, batches)
    out.update(duplicates=s.duplicates, step_s=kp.STEP_MS[rate] / 1000.0)
    if not s.dev_ms:
        return out
    out["present"] = True
    try:
        fit = kp.clock_fit(s, batches)
    except ValueError as exc:
        out["fit_error"] = str(exc)
        return out
    for k in ("start_real_ns", "start_raw_ns"):
        if not _is_int(header.get(k)):
            raise TimeFieldError(f"{name}: the header's {k} is not an integer")
    off = int(header["start_real_ns"]) - int(header["start_raw_ns"])
    out.update(aligned=True, t=[(fit.host_ns(d) + off) / 1e9 for d in s.dev_ms], clock_fit=dict(fit.stats))
    return out


def clock_fit_excess_s(times):
    """RL-173 E.1 item 2: the decoder's clock-fit excess, in seconds: the largest distance of a fit point from the
    fitted line, either side (km003c_parse.clock_fit's excess_latency_ms_max and _min). None without a fit."""
    st = times.get("clock_fit")
    if not st:
        return None
    return max(st["excess_latency_ms_max"], -st["excess_latency_ms_min"]) / 1000.0


class SpanMeter:
    """All of a span's streams through the reader: their views, their decoded times merged as stage 2 merges them
    (present and aligned streams only, sorted), and the span's digest of every time field read."""

    def __init__(self, sdir):
        self.paths = span_streams(sdir)
        self.views = [read_stream(p) for p in self.paths]
        self.times = [meter_times(v) for v in self.views]
        t = []
        for m in self.times:
            if m["present"] and m["aligned"]:
                t += m["t"]
        self.t = sorted(t)

    def summary(self):
        """The level-R print: per stream, its sample count, duplicates, clock-fit excess and rate (clock numbers)."""
        rows = []
        for m in self.times:
            st = m["clock_fit"] or {}
            rows.append({"name": m["name"], "present": m["present"], "aligned": m["aligned"], "samples": len(m["t"]),
                         "duplicates": m["duplicates"], "clock_fit_excess_s": clock_fit_excess_s(m),
                         "clock_rate_ppm": st.get("clock_rate_ppm"), "fit_error": m["fit_error"]})
        return rows

    def digest(self):
        """sha256 over every time field this reader took from the span's streams (header and trailer keys, each
        poll's stamps, count and counters), in file order. Stage 2 recomputes it before opening energy (Mythos
        round-5 N6)."""
        h = hashlib.sha256()
        for v in self.views:
            h.update(json.dumps([v["name"], v["header"], v["trailer"], v["errors"]], sort_keys=True,
                                allow_nan=True).encode())
            for p in v["polls"]:
                h.update(json.dumps([p.get(k) for k in POLL_KEYS] + [list(p.get("seq") or ())]).encode())
        return h.hexdigest()

    def excess_over(self, a, b):
        """The largest clock-fit excess among the streams whose decoded samples reach into [a, b] (epoch s)."""
        worst = None
        for m in self.times:
            if not (m["present"] and m["aligned"]) or not m["t"]:
                continue
            if m["t"][0] <= b and m["t"][-1] >= a:
                e = clock_fit_excess_s(m)
                if e is not None and (worst is None or e > worst):
                    worst = e
        return worst


def support(t, a, b):
    """The decoded samples bracketing [a, b] (the last at or before a, the first at or after b) and the largest gap
    between consecutive samples from one to the other: (i0, i1, max_gap_s), or None when [a, b] is not bracketed.
    The stage-2 integrator (``MeterSpan._support``) and stage 1's DC-in clause both call this."""
    i0 = bisect.bisect_right(t, a) - 1
    i1 = bisect.bisect_left(t, b)
    if i0 < 0 or i1 >= len(t):
        return None
    gap = max((t[i + 1] - t[i] for i in range(i0, i1)), default=0.0)
    return i0, i1, gap


# ============================================================================================ power_trace.csv
# joulewise/bundle.py ``write_power_trace`` hands Python floats to ``csv.writer``, which writes their ``repr``: ASCII
# digits, an optional fraction and exponent. ``float`` alone would also take digits outside ASCII, a sign, spaces
# and underscores, none of which a pinned writer writes.
_STAMP = re.compile(r"-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")


def _stamp(text):
    """A stamp cell's value. ``nan`` and ``inf`` are ``repr`` spellings too; the caller refuses them by value."""
    if not isinstance(text, str) or not (_STAMP.fullmatch(text) or text in ("nan", "inf", "-inf")):
        raise ValueError("not a stamp as the writer formats one")
    return float(text)


def gpu_rows(bundle):
    """[(interval_start_s, interval_end_s)] of the ``gpu_power`` / ``powermetrics`` rows, sorted, as step 3's
    ``load_gpu_trace`` selects them; all three permitted time stamps are validated. ``power_w`` is never
    converted. Raises TimeFieldError where step 3 would fail, and on a stamp no pinned writer spells (``_stamp``)."""
    path = Path(bundle) / "power_trace.csv"
    if Path(str(path) + ".zst").exists():
        raise CompressedCustody(f"{path.name}.zst is desk-compressed; the look reads a decompressed custody copy")
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("rail") == "gpu_power" and row.get("source") == "powermetrics":
                try:
                    s, e = _stamp(row["interval_start_s"]), _stamp(row["interval_end_s"])
                except (KeyError, TypeError, ValueError):
                    raise TimeFieldError("power_trace.csv: a gpu_power row without numeric interval stamps") from None
                if not (math.isfinite(s) and math.isfinite(e)):
                    raise TimeFieldError("power_trace.csv: a gpu_power row with a non-finite interval stamp")
                try:
                    ts = _stamp(row["timestamp_s"])
                except (KeyError, TypeError, ValueError):
                    raise TimeFieldError("power_trace.csv: a gpu_power row without numeric timestamp_s") from None
                if not math.isfinite(ts):
                    raise TimeFieldError("power_trace.csv: a gpu_power row with non-finite timestamp_s")
                rows.append((s, e))
            del row
    rows.sort()
    return rows


def rows_digest(rows):
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()


def gpu_max_uncovered(s, e, a, b):
    """The longest stretch of [a, b] that no row covers (rows sorted by start; ``s``/``e`` their starts and ends).
    Step 3's ``Trace._range`` selects the candidate rows. The one definition: stage 1's GPU clause and stage 2's
    backstop both call it."""
    maxw = max((y - x for x, y in zip(s, e)), default=0.0)
    i = max(0, bisect.bisect_left(s, a - maxw - 1e-9) - 1)
    j = bisect.bisect_right(s, b)
    edge, worst = a, 0.0
    for k in range(i, j):
        s0, e0 = s[k], e[k]
        if e0 <= edge or s0 >= b:
            continue
        worst = max(worst, s0 - edge)
        edge = max(edge, e0)
    return max(worst, b - edge)


def connected_intervals(intervals):
    """Union of fitted intervals, merging touching segments so their boundary cannot split a trace hole.

    Disjoint intervals stay disjoint: time outside the fit does not enter its gap check.
    """
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def file_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def compressed_siblings(paths):
    """The ``.zst`` siblings that exist for any of ``paths`` (Mythos round-5 N8)."""
    return [str(p) + ".zst" for p in paths if os.path.exists(str(p) + ".zst")]
