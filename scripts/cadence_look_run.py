#!/usr/bin/env python3
"""The interim look's two-stage CLI (RL-166 Q1, Q2, Q8; the analyst seat runs it).

    stage1 --out STAGE1.json  (--input LOOK_INPUT.json
                               | --roster ROSTER.json --custody ROOT --rules-3-4 VERDICTS.json
                                 [--span-dir SPAN_ID=PATH ...] [--write-input LOOK_INPUT.json])
           --manifest MANIFEST.json [--allow-draft]   (both stages; checked first, before any input opens)
    stage2 --stage1 STAGE1.json --stage1-sha256 HEX --looks LOOKS.json --out FIT.json
                              (--energy SEGMENT_ENERGY.json
                               | --custody ROOT [--span-dir SPAN_ID=PATH ...] [--step3-module PATH])

Stage 1 opens NO energy file. In custody mode it opens, per span: `runner_receipt.json`,
`soak/soak_reference.json`, and per leg `leg_record.json`; per accepted attempt's bundle: `events.jsonl`
(token index and stamp), `outputs/align_turns.jsonl` (stamps, prompt count, the LENGTH of the output ids),
`outputs/align_thermal.jsonl` (journal readings), and, for the native power-management state only,
`rich_telemetry.jsonl` and `raw/powermetrics.plist`, from which it extracts by pattern the row end stamp,
`elapsed_ns` and `thermal_pressure` and nothing else: no line or frame of those two files is parsed as a whole,
so no power or energy value is decoded. It never opens `power_trace.csv`. Of each span's meter stream it decodes
the header line (no sample) and reads the last poll line's `rx` and `rt` stamps by pattern, for RL-167 R-20's clock
print; no sample payload is decoded.

Stage 2 takes the stage-1 file by its sha256 as its only roster. In custody mode it computes the level-E object
in memory (GPU rail through the committed step 3 module's `load_gpu_trace` and `Trace`; DC-in by the trapezoid
between consecutive KM003C samples, through `joulewise.external.km003c_parse`) and never writes it.

Stdout carries the output path and its sha256 only. A refusal prints its field-only message; any other
exception prints its type and line number only (step 3's rule: a message could carry a value).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
# Mythos N10: -B stops writing bytecode, not reading it. A fresh, empty pycache prefix makes Python look for cached
# bytecode only there, so a stale __pycache__ entry beside a pinned source is never run; every repository module
# below compiles from the source bytes verify_pins hashes. _check_sources() confirms it before any energy opens.
import tempfile  # noqa: E402
_PYC_PREFIX = tempfile.mkdtemp(prefix="jw-look-pyc-")
sys.pycache_prefix = _PYC_PREFIX
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.cadence_looks import fit_interim as F  # noqa: E402
from joulewise.cadence_looks import manifest as M  # noqa: E402
from joulewise.cadence_looks import inclusion_34 as I34  # noqa: E402

STEP3_SHA256 = "84a1a5530ab06e688b000c84f248b2c4e561e8330f37d3132ec47aa2572eb173"
FAN_KEYS = ("F0Ac", "F1Ac")          # configs/align/v4/r1_runtime.json sensors.fan_keys
PM_FRESH_S = 2.0
NS = 1_000_000_000
METER_MAX_GAP_S = 2.0                # RL-166 Q7: no gap over 2 s between meter sample stamps in the leg's interval
MODE_BY_POWER = {"automatic": 0, "high_power": 2}
JOURNAL_PRE_S, JOURNAL_POST_S = 60.0, 5.0
CODE_PATHS = ("joulewise/cadence_looks/fit_interim.py", "scripts/cadence_look_run.py")
RUNNING = tuple(ROOT / p for p in CODE_PATHS)          # the files verify_pins requires to be pinned


# =============================================================================================== helpers
def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def code_hashes():
    """Every repository source file this process has loaded, with its sha256 (M.loaded_repo_files; Sol N2 /
    Mythos 3). Taken when the stage's output is built, after everything it ran has been imported."""
    return M.loaded_repo_files(ROOT)


_VERIFIED = []


def _stamp(out, a):
    """Provenance and run mode on a stage output: the manifest verify_pins checked, and allow_draft. Before writing,
    refuse if any repository module loaded in this process is not pinned (manifest.unpinned_loaded_modules)."""
    doc, mpath = _VERIFIED[0]
    _guard_loaded(doc)
    out["manifest_sha256"] = sha256_file(mpath)
    out["allow_draft"] = bool(a.allow_draft)
    return out


def _jsonl(path):
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def _json(path):
    with open(path) as f:
        return json.load(f)


def write_canonical(path, obj):
    data = F.dump(obj)
    with open(path, "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def span_dirs(custody, pairs):
    m = {}
    for p in pairs or []:
        sid, _, path = p.partition("=")
        if not sid or not path:
            raise F.LookInputError("--span-dir wants SPAN_ID=PATH")
        m[sid] = Path(path)
    return lambda sid: m.get(sid, Path(custody) / sid)


# =============================================================================================== stage-1 reader
_RICH_TS = re.compile(rb'"timestamp_s":\s*(-?[0-9][0-9.eE+-]*)')
_RICH_EL = re.compile(rb'"elapsed_ns":\s*([0-9]+)')
_PL_TP = re.compile(rb"<key>thermal_pressure</key>\s*<string>([^<]*)</string>")
_PL_EL = re.compile(rb"<key>elapsed_ns</key>\s*<integer>([0-9]+)</integer>")


def native_states(bundle, lo, hi):
    """[(row end epoch, state)] for rows ending in [lo, hi]. Pattern extraction only (module docstring)."""
    ends = []
    with open(bundle / "rich_telemetry.jsonl", "rb") as f:
        for line in f:
            if not line.strip():
                continue
            m, e = _RICH_TS.search(line), _RICH_EL.search(line)
            if not m or not e:
                raise F.LookInputError("rich_telemetry: a row without timestamp_s or elapsed_ns")
            ends.append((float(m.group(1)), int(e.group(1))))
            del line
    with open(bundle / "raw/powermetrics.plist", "rb") as f:
        frames = [p for p in f.read().split(b"\0") if p.strip()]
    if not (len(frames) == len(ends) or len(frames) == len(ends) + 1):
        raise F.LookInputError("plist/rich frame count mismatch")
    out = []
    for i, (end, el) in enumerate(ends):
        if not (lo <= end <= hi):
            continue
        fr = frames[i]
        me = _PL_EL.search(fr)
        if not me or int(me.group(1)) != el:
            raise F.LookInputError("plist/rich elapsed mismatch")
        mt = _PL_TP.search(fr)
        out.append({"t_end_s": end, "state": mt.group(1).decode() if mt else None})
    del frames
    return out


def journal_readings(bundle, lo, hi, fan_keys):
    out = []
    for r in _jsonl(bundle / "outputs/align_thermal.jsonl"):
        if r.get("kind") != "reading" or r.get("error"):
            continue
        t = r["finished"]["wall_ns"] / 1e9
        if not (lo <= t <= hi):
            continue
        v = r.get("values") or {}
        st = v.get("status") or {}
        sen = v.get("sensors") or {}
        pmo = st.get("pm_observed_ns")
        fresh = type(pmo) is int and (r["started"]["monotonic_ns"] - pmo) <= PM_FRESH_S * 1e9
        fans = [sen.get(k) for k in fan_keys]
        fan = (sum(float(x) for x in fans) / len(fans)) if fans and all(x is not None for x in fans) else None  # R-7
        lvl = st.get("os_level")
        out.append({"t_s": t, "os_level": lvl if type(lvl) is int else None,
                    "pm_state": st.get("pm_state") if isinstance(st.get("pm_state"), str) else None,
                    "pm_fresh": bool(fresh),
                    "tf08_c": None if sen.get("Tf08") is None else float(sen["Tf08"]), "fan_rpm": fan,
                    "tv0h_c": None if sen.get("TV0h") is None else float(sen["TV0h"])})
    out.sort(key=lambda x: x["t_s"])
    return out


def token_stamps(bundle):
    toks = []
    with open(bundle / "events.jsonl") as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("event_type") == "token":
                md = e.get("metadata") or {}
                if md.get("align_turn_index", 0) not in (0, None):
                    raise F.LookInputError("events: a multi-turn leg")
                toks.append((int(md["index"]), float(e["timestamp_s"])))
            del e
    toks.sort()
    if [i for i, _ in toks] != list(range(len(toks))):
        raise F.LookInputError("events: token indices not contiguous")
    t = [s for _, s in toks]
    if any(b < a for a, b in zip(t, t[1:])):
        raise F.LookInputError("events: token stamps not monotone")
    return t


def build_turn(bundle, result, fan_keys):
    turns = _jsonl(bundle / "outputs/align_turns.jsonl")
    if len(turns) != 1:
        raise F.LookInputError("align_turns: not one turn")
    tr = turns[0]
    ts = float(tr["start_stamp"]["epoch_s"])
    n_out = len(tr["generation"]["output_token_ids"])          # LENGTH only
    P = tr["generation"].get("prefill_tokens", result.get("prefill_tokens"))
    del turns, tr
    tok = token_stamps(bundle)
    if len(tok) != n_out or not tok:
        raise F.LookInputError("token count differs from the output length")
    N = len(tok)
    segs = [{"seg": 0, "kind": "prefill", "n_tokens": int(P), "edge_lo": None, "edge_hi": None, "tok_first": None,
             "tok_last": None, "wall_start_s": ts, "wall_end_s": tok[0], "first_token_s": None}]
    for k in range(N // F.BLOCK):
        lo = 0 if k == 0 else F.BLOCK * k - 1
        hi = F.BLOCK * k + F.BLOCK - 1
        segs.append({"seg": k + 1, "kind": "decode", "block": k, "n_tokens": F.BLOCK, "tok_first": F.BLOCK * k,
                     "tok_last": hi, "edge_lo": lo, "edge_hi": hi, "wall_start_s": tok[lo], "wall_end_s": tok[hi],
                     "first_token_s": tok[F.BLOCK * k]})
    tails = []
    for L in sorted(F.PREFIX.values(), reverse=True):
        if L >= N:
            continue
        nb = L // F.BLOCK
        a, lo, hi = F.BLOCK * nb, F.BLOCK * nb - 1, L - 1
        tails.append({"prefix_len": L, "kind": "prefix_tail", "tok_first": a, "tok_last": hi, "n_tokens": L - a,
                      "edge_lo": lo, "edge_hi": hi, "wall_start_s": tok[lo], "wall_end_s": tok[hi],
                      "first_token_s": tok[a]})
    return {"prefill_tokens": int(P), "decode_tokens": N, "turn_start_s": ts, "first_token_s": tok[0],
            "last_token_s": tok[-1], "segments": segs, "prefix_tails": tails,
            "journal": journal_readings(bundle, ts - JOURNAL_PRE_S, tok[-1] + JOURNAL_POST_S, fan_keys),
            "native_pm": native_states(bundle, ts, tok[-1])}


_B_KIND = re.compile(rb'"k":\s*"b"')
_H_KIND = re.compile(rb'^\{\s*"k"\s*:\s*"h"\s*,')
_RX = re.compile(rb'"rx":\s*([0-9]+)')
_RT = re.compile(rb'"rt":\s*([0-9]+)')


def meter_offsets(sdir):
    """RL-167 R-20: (header wall-minus-raw offset, end-of-span offset) in ns. The header line is decoded (it holds
    no sample); the last poll line is read by pattern for its `rx` and `rt` stamps only, never parsed. (None, None)
    with no stream; end None when no poll carries both stamps."""
    paths = sorted(glob.glob(str(sdir / "hazards/meter/stream-*.jsonl")))
    if not paths:
        return None, None
    header_off, end_off = None, None
    for p in paths:
        with open(p, "rb") as f:
            head = f.readline(65536)
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 262144))
            tail = f.read().splitlines()
        # Mythos N11: decode the first line only when it is a header line; a sample line is never decoded
        h = json.loads(head) if _H_KIND.match(head) else {}
        if header_off is None and h.get("k") == "h" and isinstance(h.get("start_raw_ns"), int) \
                and isinstance(h.get("start_real_ns"), int):
            header_off = h["start_real_ns"] - h["start_raw_ns"]
        for line in reversed(tail):
            if _B_KIND.search(line):
                rx, rt = _RX.search(line), _RT.search(line)
                if rx and rt:
                    end_off = int(rt.group(1)) - int(rx.group(1))
                break
        del tail
    return header_off, end_off


def draft_ledger_check(looks_doc, stage1_sha256):
    """Synthetic runs (--allow-draft) only: a scratch ledger's row for this look names this stage-1 hash at
    stage1_committed or later. A real look uses manifest.require_stage1_committed on the committed ledger."""
    M.validate_look_ledger(looks_doc)
    row = next((r for r in looks_doc["looks"] if r.get("look_id") == F.LOOK_ID), None)
    if row is None or row.get("status") not in ("stage1_committed", "run", "frozen"):
        raise F.LookInputError("draft ledger: the look's row is not at stage1_committed or later")
    if row.get("stage1_sha256") != stage1_sha256:
        raise F.LookInputError("draft ledger: the row does not name this stage-1 file's sha256")


def _mode(result):
    m = result.get("ac_powermode")
    return m.get("value") if isinstance(m, dict) else m


def read_span(sdir, entry, rules34, fan_keys):
    """(span, legs) of one roster span, in level-R shape. Opens no energy file."""
    receipt = _json(sdir / "runner_receipt.json")
    try:
        soak = float(_json(sdir / "soak/soak_reference.json")["sensors_c"]["TV0h"])
    except (OSError, KeyError, TypeError, ValueError):
        soak = None
    power = "high_power" if entry["block_id"].startswith("hp-") else "automatic"
    span = {"span_id": entry["span_id"], "block_id": entry["block_id"],
            "phase": "extension" if entry["role"] == "describe" else "development", "role": entry["role"],
            "power_mode": power, "t0_epoch_s": float(receipt["started"]["epoch_s"]),
            "t0_local_date": entry["t0_local_date"], "soak_reference_tv0h_c": soak, "marks": [],
            "meter_offsets_ns": dict(zip(("header", "end"), meter_offsets(sdir)))}
    legs, marks, suppliers = [], set(), set()
    for leg_id in receipt["roster"]:
        key = f"{entry['span_id']}/{leg_id}"
        ldir = sdir / "legs" / leg_id
        v34 = rules34.get(key)
        if v34 is None:
            raise F.LookInputError("rules 3 and 4: no verdict for a roster leg")
        if not (ldir / "leg_record.json").is_file():          # the span stopped before this leg (R-21)
            legs.append({"leg_key": key, "span_id": entry["span_id"], "leg_id": leg_id, "leg_type": "A",
                         "cell_prompt_tokens": None, "g0_role": None,
                         "inclusion": {r: False for r in F.RULES}, "turn": None})
            continue
        rec = _json(ldir / "leg_record.json")
        spec, attempts, result = rec["spec"], rec["attempts"], rec.get("result") or {}
        summ = _json(ldir / "leg_summary.json") if (ldir / "leg_summary.json").is_file() else {}
        ref = summ.get("span_reference")
        if isinstance(ref, dict):
            if isinstance(ref.get("leg_id"), str):
                suppliers.add(ref["leg_id"])
            if ref.get("redone"):
                marks.add("reference from a redo")
            if ref.get("excluded"):
                marks.add("reference from an excluded leg")
        leg_type = "T" if spec.get("leg_type") == "T" else "A"          # R-21: spec.leg_type only
        inc = {"ran_to_cap": result.get("leg_status") == "complete" and result.get("decode_cap_reached") is True,
               "g0_released": result.get("g0_released") is True,
               "sidecar_coverage": v34["sidecar_coverage"] is True, "km003c_clean": v34["km003c_clean"] is True,
               "not_a_contaminated_attempt": bool(attempts) and not attempts[-1].get("contaminated"),
               "block_power_mode": _mode(result) == MODE_BY_POWER[power]}
        turn = None
        if leg_type == "A" and result.get("bundle"):
            try:
                turn = build_turn(ldir / "runtime" / result["bundle"], result, fan_keys)
            except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
                # A G0 timeout (cadence_leg.py: a bundle and no turn) is a ruled exclusion (rules 1 and 2), not a
                # refusal: a leg the six verdicts already exclude carries no turn. An included leg refuses.
                if all(inc.values()):
                    raise F.LookInputError(f"an included leg's bundle has no readable turn ({type(exc).__name__})")
                turn = None
        legs.append({"leg_key": key, "span_id": entry["span_id"], "leg_id": leg_id, "leg_type": leg_type,
                     "cell_prompt_tokens": int(spec["prefill_tokens"]), "g0_role": spec.get("g0_role"),
                     "inclusion": inc, "turn": turn})
    # RL-161 §4 (Mythos cold seats 7 and N3): the leg that supplied the span's reference, excluded AT THE LOOK (any of
    # the six verdicts, rules 3 and 4 included), marks the span when a consumer is on its roster. The supplier is
    # named by each consumer's leg_summary span_reference.leg_id (the runner takes the span's first leg, whatever
    # its shape: an own-shaped first leg supplies dev-03's first span); a capture-role leg also counts.
    consumers = any(leg["g0_role"] == "consume" for leg in legs)
    supplier_ids = suppliers | {leg["leg_id"] for leg in legs if leg["g0_role"] == "capture"}
    if consumers and any(not all(leg["inclusion"].values()) for leg in legs if leg["leg_id"] in supplier_ids):
        marks.add("reference from an excluded leg")
    span["marks"] = sorted(marks)
    return span, legs


def read_look_input(roster, sdir_of, rules34, fan_keys=FAN_KEYS):
    """Level R from the custody copy. `synthetic` is true only when every span's runner receipt says so
    (the synthetic generator writes it; a real runner never does)."""
    if not isinstance(roster, list):                # one shape: validate --roster-out's JSON list
        raise F.LookInputError("roster: not a list of spans")
    spans, legs, synth = [], [], []
    for entry in roster:
        sdir = sdir_of(entry["span_id"])
        synth.append(_json(sdir / "runner_receipt.json").get("synthetic") is True)
        s, ls = read_span(sdir, entry, rules34, fan_keys)
        spans.append(s)
        legs += ls
    return {"schema": F.INPUT_SCHEMA, "look_id": F.LOOK_ID, "synthetic": bool(synth) and all(synth),
            "spans": spans, "legs": legs}


def stage2_preflight(stage1_out, sdir_of):
    """Structural checks of every file stage 2 will open, by presence only (stat, never a read): each
    energy-fit leg's power_trace.csv, and a meter stream in its span. Run by stage 1, so a layout fault refuses
    before any energy file is opened (Mythos cold seat 4)."""
    seen = set()
    for L in stage1_out["legs"]:
        if not L["in_energy_fit"]:
            continue
        sdir = sdir_of(L["span_id"])
        leg_id = L["leg_key"].split("/", 1)[1]
        rec = _json(sdir / "legs" / leg_id / "leg_record.json")
        if not (sdir / "legs" / leg_id / "runtime" / rec["result"]["bundle"] / "power_trace.csv").is_file():
            raise F.LookInputError("stage-2 preflight: an energy-fit leg has no power_trace.csv")
        if L["span_id"] not in seen:
            if not glob.glob(str(sdir / "hazards/meter/stream-*.jsonl")):
                raise F.LookInputError("stage-2 preflight: an energy-fit leg's span has no meter stream")
            seen.add(L["span_id"])


# =============================================================================================== stage-2 reader
def load_step3(path=None):
    if path is None:
        mod = importlib.import_module("joulewise.cadence_looks.step3_energy_ratios")
        path = mod.__file__
    if sha256_file(path) != STEP3_SHA256:
        raise F.LookInputError("the step 3 module is not the committed bytes")
    spec = importlib.util.spec_from_file_location("_step3_pinned", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


class MeterSpan:
    """KM003C samples of a span on wall-clock epoch seconds; Vbus x Ibus; in memory only. Also the receipt stamps
    (rt) of the polls that carried samples, which rule 4 judges (inclusion_34.rule4)."""

    def __init__(self, sdir):
        from joulewise.external import km003c_parse as kp
        paths = sorted(glob.glob(str(sdir / "hazards/meter/stream-*.jsonl")))
        if not paths:
            raise F.LookInputError("no meter stream in the span")
        t, w, steps, polls = [], [], [], []
        for p in paths:
            st = kp.parse(p)
            if not st.present or not st.aligned:     # contributes no sample; a fit interval it alone spans refuses
                del st
                continue
            steps.append(kp.STEP_MS[st.header["rate_idx"]] / 1000.0)
            off = int(st.header["start_real_ns"]) - int(st.header["start_raw_ns"])    # RAW -> REALTIME (R-20)
            t += [(h + off) / 1e9 for h in st.host_ns]
            w += list(st.watts)
            polls += [int(b["rt"]) for b in st.batches if b.get("n") and isinstance(b.get("rt"), int)]
            del st
        if not t:
            raise F.LookInputError("no meter stream in the span has aligned samples")
        order = sorted(range(len(t)), key=t.__getitem__)
        self.t = [t[i] for i in order]
        self.w = [w[i] for i in order]
        self.poll_rt_ns = sorted(polls)
        self.step_s = max(steps)

    def _support(self, a, b):
        """Rule 4's own gap test on the interval [a, b] (inclusion_34.rule4; RL-166 Q7, Mythos r3 N6): the points
        {a, b} and the receipt stamps of the sample-carrying polls inside, no two consecutive more than 2 s apart.
        So a segment of a leg rule 4 admitted is supported, and no longer gap is ever bridged. A sample must also
        lie within 2 s of the interval, for the value held at an edge."""
        import bisect
        if b < a:
            raise F.LookInputError("a segment with its end before its start")
        a_ns, b_ns = round(a * NS), round(b * NS)
        lo, hi = bisect.bisect_left(self.poll_rt_ns, a_ns), bisect.bisect_right(self.poll_rt_ns, b_ns)
        points = [a_ns] + self.poll_rt_ns[lo:hi] + [b_ns]
        if max(y - x for x, y in zip(points, points[1:])) > METER_MAX_GAP_S * NS:
            raise F.LookInputError("DC-in: a gap over 2 s between meter samples inside an energy-fit interval")
        i = bisect.bisect_left(self.t, a - METER_MAX_GAP_S)
        if i >= len(self.t) or self.t[i] > b + METER_MAX_GAP_S:
            raise F.LookInputError("DC-in: an energy-fit interval is not bracketed by meter samples")

    def _value(self, x):
        """Vbus x Ibus at x: linear between samples, held flat beyond the first and last (the edge stretch rule 4
        admits, at most 2 s)."""
        import bisect
        j = bisect.bisect_right(self.t, x) - 1
        if j < 0:
            return self.w[0]
        if j >= len(self.t) - 1:
            return self.w[-1]
        t0, t1 = self.t[j], self.t[j + 1]
        return self.w[j] + (self.w[j + 1] - self.w[j]) * (x - t0) / (t1 - t0) if t1 > t0 else self.w[j]

    def coverage(self, a, b):
        """Fraction of [a, b] within half a nominal sample period of a sample (a print; decides nothing)."""
        if b <= a:
            return None
        h = 0.5 * self.step_s
        import bisect
        i = max(0, bisect.bisect_left(self.t, a - h))
        cov, edge = 0.0, a
        while i < len(self.t) and self.t[i] - h < b:
            lo, hi = max(edge, self.t[i] - h, a), min(b, self.t[i] + h)
            if hi > lo:
                cov += hi - lo
                edge = hi
            i += 1
        return cov / (b - a)

    def energy(self, a, b):
        """Trapezoid between consecutive samples, cut at a and b (linear value at the cuts; held at an edge with no
        sample beyond it), on supported intervals only (see _support)."""
        import bisect
        self._support(a, b)
        xs = [a] + self.t[bisect.bisect_right(self.t, a):bisect.bisect_left(self.t, b)] + [b]
        return sum(0.5 * (self._value(x) + self._value(y)) * (y - x) for x, y in zip(xs, xs[1:]))


def gpu_max_uncovered_s(trace, a, b):
    """The longest stretch of [a, b] that no power_trace row covers (the GPU rail's analogue of the DC-in gap)."""
    edge, worst = a, 0.0
    for i in trace._range(a, b):
        s0, e0 = trace.s[i], trace.e[i]
        if e0 <= edge or s0 >= b:
            continue
        worst = max(worst, s0 - edge)
        edge = max(edge, e0)
    return max(worst, b - edge)


def gpu_gap_rule(doc):
    """Mythos r3 N7, pending the research lead: refuse a GPU-rail segment with an uncovered stretch over
    max_gap_s. Read from the manifest's fit.gpu_trace_hole_refusal {"enabled": bool, "max_gap_s": number}; absent
    or disabled (the default), the GPU rail integrates the rows present, as step 3 does."""
    sw = ((doc or {}).get("fit") or {}).get("gpu_trace_hole_refusal") or {}
    return float(sw.get("max_gap_s", METER_MAX_GAP_S)) if sw.get("enabled") is True else None


def read_segment_energy(stage1_out, sdir_of, step3_path=None, gpu_max_gap_s=None):
    """The level-E object, in memory (never written in production). gpu_max_gap_s: see gpu_gap_rule."""
    s3, _ = load_step3(step3_path)
    meters = {}
    out = {"schema": F.ENERGY_SCHEMA, "look_id": F.LOOK_ID, "synthetic": False,
           "input_sha256": stage1_out["input_sha256"], "legs": {}}
    for L in stage1_out["legs"]:
        if not L["in_energy_fit"]:                  # RL-167 §3: no hp-01 energy is opened
            continue
        sdir = sdir_of(L["span_id"])
        leg_id = L["leg_key"].split("/", 1)[1]
        rec = _json(sdir / "legs" / leg_id / "leg_record.json")
        bundle = sdir / "legs" / leg_id / "runtime" / rec["result"]["bundle"]
        trace = s3.Trace(s3.load_gpu_trace(str(bundle)))
        if L["span_id"] not in meters:
            meters[L["span_id"]] = MeterSpan(sdir)
        m = meters[L["span_id"]]
        entry = {}
        def gpu_energy(a, b, trace=trace):
            if gpu_max_gap_s is not None and gpu_max_uncovered_s(trace, a, b) > gpu_max_gap_s:
                raise F.LookInputError("GPU rail: a stretch with no power_trace row inside an energy-fit interval")
            return trace.energy(a, b)
        for ch, fn, cov in (("gpu_rail", gpu_energy, trace.coverage), ("dc_in", m.energy, m.coverage)):
            segs = [fn(s["wall_start_s"], s["wall_end_s"]) for s in L["segments"]]
            tails = {str(t["prefix_len"]): fn(t["wall_start_s"], t["wall_end_s"]) for t in L["prefix_tails"]}
            covs = [c for c in (cov(s["wall_start_s"], s["wall_end_s"]) for s in L["segments"]) if c is not None]
            entry[ch] = {"segments": segs, "prefix_tails": tails, "coverage_min": min(covs) if covs else 1.0}
        out["legs"][L["leg_key"]] = entry
        del trace
    return out


# =============================================================================================== main
def cmd_stage1(a):
    if a.input and not a.allow_draft:
        raise F.LookInputError("--input (level R) runs only with --allow-draft; a committed look reads custody")
    if a.input:
        with open(a.input, "rb") as f:
            raw = f.read()
        look_input = json.loads(raw)
        input_sha = hashlib.sha256(raw).hexdigest()
        extra = {"roster_sha256": input_sha}        # a level-R run has no roster: its input file stands in
    else:
        roster = _json(a.roster)
        rules34 = _json(a.rules_3_4)
        look_input = read_look_input(roster, span_dirs(a.custody, a.span_dir), rules34)
        data = F.dump(look_input)
        input_sha = hashlib.sha256(data).hexdigest()
        if a.write_input:
            with open(a.write_input, "wb") as f:
                f.write(data)
        extra = {"roster_sha256": sha256_file(a.roster), "rules_3_4_sha256": sha256_file(a.rules_3_4)}
    if a.allow_draft and look_input.get("synthetic") is not True:
        raise F.LookInputError("--allow-draft runs on synthetic input only (Mythos N2)")
    out = F.stage1(look_input, input_sha, code_hashes())
    # RL-172a's soak-retry print, from the runner receipts (none in a level-R run)
    if a.input:
        out["soak_retries"] = I34.soak_retries({})
    else:
        sdir_of = span_dirs(a.custody, a.span_dir)
        out["soak_retries"] = I34.soak_retries({e["span_id"]: Path(sdir_of(e["span_id"])) for e in roster})
    if not a.input:
        stage2_preflight(out, span_dirs(a.custody, a.span_dir))
    if extra:
        out["code_sha256"].update({f"input:{k}": v for k, v in extra.items()})
    return _stamp(out, a)


def cmd_stage2(a):
    with open(a.stage1, "rb") as f:
        raw = f.read()
    if hashlib.sha256(raw).hexdigest() != a.stage1_sha256:
        raise F.LookInputError("stage 2: the stage-1 file does not match --stage1-sha256")
    s1 = json.loads(raw)
    if F.dump(s1) != raw:
        raise F.LookInputError("stage 2: the stage-1 file is not in canonical form")
    if a.allow_draft and s1.get("synthetic") is not True:
        raise F.LookInputError("--allow-draft runs on synthetic input only (Mythos N2)")
    if a.energy and not a.allow_draft:
        raise F.LookInputError("--energy (level E) runs only with --allow-draft; a committed look reads custody")
    # committed: the repository's LOOKS.json row names this stage-1 file's sha256 (Mythos cold seat 8; N1), before any
    # energy opens. A caller-named ledger is accepted for synthetic (--allow-draft) runs only.
    if a.looks and not a.allow_draft:
        raise F.LookInputError("--looks names a ledger other than the repository's; only with --allow-draft")
    if a.allow_draft:
        draft_ledger_check(_json(a.looks) if a.looks else _json(ROOT / M.LOOK_LEDGER_PATH), a.stage1_sha256)
    else:
        # the committed ledger at HEAD, HEAD on the ledger ref, the manifest and roster bound (builder's contract)
        M.require_stage1_committed(ROOT, F.LOOK_ID, a.stage1_sha256, stage1_doc=s1, ledger_ref=a.ledger_ref)
    F.stage2_preflight(s1)                          # refuses before any energy file is opened
    stage2_energy_preflight(s1, a)                  # Mythos round 3 N1, N2: every remaining refusal, before energy
    if a.energy:
        energy = _json(a.energy)
    else:
        energy = read_segment_energy(s1, span_dirs(a.custody, a.span_dir),
                                     gpu_max_gap_s=gpu_gap_rule(_VERIFIED[0][0]))
    return _stamp(F.stage2(s1, a.stage1_sha256, energy, code_hashes()), a)


def stage2_energy_preflight(s1, a):
    """Everything stage 2 can refuse on without energy, checked before the first energy file opens:
    - a stage-1 file made under --allow-draft is refused by a run without it (Mythos r3 N2);
    - the stage-1 file names the manifest this run verified (N2);
    - under --allow-draft, every span the custody run opens has a runner receipt saying "synthetic": true (N1);
    - stage 2's whole module set (the meter decoder, the step 3 file) is imported now and the unpinned-module and
      cached-bytecode checks run on it (N2, N10)."""
    if s1.get("allow_draft") is True and not a.allow_draft:
        raise F.LookInputError("the stage-1 file was made under --allow-draft; a run without it refuses it")
    doc, mpath = _VERIFIED[0]
    if s1.get("manifest_sha256") != sha256_file(mpath):
        raise F.LookInputError("the stage-1 file was made under another manifest")
    if a.allow_draft and a.custody:
        sdir_of = span_dirs(a.custody, a.span_dir)
        for sp in s1["roster"]["spans"]:
            if _json(sdir_of(sp["span_id"]) / "runner_receipt.json").get("synthetic") is not True:
                raise F.LookInputError("--allow-draft opens synthetic custody only: a span's receipt is not synthetic")
    importlib.import_module("joulewise.external.km003c_parse")
    importlib.import_module("joulewise.cadence_looks.step3_energy_ratios")
    _guard_loaded(doc)


def _guard_loaded(doc):
    """Refuse on any loaded repository module the manifest does not pin (M.unpinned_loaded_modules), or one whose
    code did not come from its source under this run's fresh pycache prefix (Mythos N10)."""
    loose = M.unpinned_loaded_modules(doc, ROOT)
    if loose:
        raise F.LookInputError(f"modules loaded but not pinned: {sorted(loose)}")
    _check_sources()


def _check_sources():
    """No loaded repository module may have a bytecode file at its cache path. This run writes none (-B, and a
    fresh empty prefix), so a file there is one Python may have run in place of the pinned source."""
    root = str(ROOT.resolve())
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f or not str(Path(f).resolve()).startswith(root):
            continue
        cached = getattr(mod, "__cached__", None)
        if f.endswith((".pyc", ".pyo")) or (cached and os.path.exists(cached)):
            raise F.LookInputError(f"a repository module may have run from cached bytecode: {Path(f).name}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="The interim look's two stages (RL-166 Q8).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("stage1")
    p1.add_argument("--out", required=True)
    g = p1.add_mutually_exclusive_group(required=True)
    g.add_argument("--input")
    g.add_argument("--roster")
    p1.add_argument("--custody")
    p1.add_argument("--rules-3-4")
    p1.add_argument("--span-dir", action="append")
    p1.add_argument("--write-input")
    p1.add_argument("--ledger-ref", help="the ref HEAD must be an ancestor of (default: upstream, else origin/main)")
    p2 = sub.add_parser("stage2")
    p2.add_argument("--stage1", required=True)
    p2.add_argument("--stage1-sha256", required=True)
    p2.add_argument("--out", required=True)
    g2 = p2.add_mutually_exclusive_group(required=True)
    g2.add_argument("--energy")
    g2.add_argument("--custody")
    p2.add_argument("--span-dir", action="append")
    p2.add_argument("--looks", help="with --allow-draft only: a scratch LOOKS.json in place of the repository's")
    p2.add_argument("--ledger-ref", help="the ref HEAD must be an ancestor of (default: upstream, else origin/main)")
    for p in (p1, p2):
        p.add_argument("--manifest", required=True, help="the look manifest whose pins the running code must match")
        p.add_argument("--allow-draft", action="store_true", help="synthetic runs: accept a draft manifest")
    a = ap.parse_args(argv)
    if a.cmd == "stage1" and a.roster and not (a.custody and a.rules_3_4):
        ap.error("--roster needs --custody and --rules-3-4")
    try:
        # FIRST, before any input is opened: the running code must be the pinned code (Mythos cold seat 3; Sol 9)
        _VERIFIED[:] = [(M.verify_pins(a.manifest, ROOT, allow_draft=a.allow_draft, running=RUNNING,
                                       ledger_ref=getattr(a, "ledger_ref", None)), a.manifest)]
        out = cmd_stage1(a) if a.cmd == "stage1" else cmd_stage2(a)
        sha = write_canonical(a.out, out)
    except F.LookInputError as exc:
        print(f"REFUSED {exc}", file=sys.stderr)
        return 2
    except M.ManifestError as exc:
        print(f"REFUSED {'; '.join(exc.problems)}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - no message: it could carry a value
        tb = exc.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        print(f"FAILED {type(exc).__name__} at {os.path.basename(tb.tb_frame.f_code.co_filename)}:{tb.tb_lineno}",
              file=sys.stderr)
        return 2
    print(f"wrote {a.out} sha256={sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
