#!/usr/bin/env python3.13
"""Block 5 cross-instrument edge check (exploratory, derived after release).

Implements docs/analysis/b5/edge-check-reading-rule.md (rule commit 7e1d4278c) literally.
Standard library only.  Read-only on the data.

For each edge, Delta = (sampler edge time) - (KM003C edge time) on the meter's CLOCK_MONOTONIC_RAW axis.
Both times come from one estimator, the energy-equivalent step time
    t = B - integral_A^B (P - L_pre) dt / (L_post - L_pre),
with L_pre, L_post the median power over -700..-250 ms and +350..+800 ms from the stamped edge.
T = median Delta over inference edges - median Delta over pulse edges, per direction (rise, fall).

Interpretations fixed in code before any Delta was computed (each one is printed in the output):
  I1  Kept runs: the target cells' kept units in each session's derived/exclusions.json, mapped to run ids by
      derived/roster.json.  ALPHA/BETA: the decode and prefill-p2048 reported cells (quads + repeats); GAMMA: the
      kept quads of the two contrasts.  Checked against the release-check recompute's kept lists.
  I2  "Each one's calibration capture" is the capture in the run's instrument_calibration/ directory.  If every
      kept run of a session carries a byte-identical capture, it is one capture: its pulse edges are counted once.
      Resampling runs then always brings that same capture, so the pulse median is fixed within a session (and the
      pooled pulse median, over the distinct captures of the three sessions, is fixed too).
  I3  Pulse edges are all pulse_command_on/off events (the non-warmup pulses).  The rule says 56; the data has
      59 non-warmup pulses plus 3 separate warmup pulses per capture.  Warmup command edges count as stamped edges
      for the neighbour exclusion only.
  I4  Stamped edges: pulse and warmup command ON/OFF (clock_stamp.epoch_s), request start (phase_start of
      tokenize, the request's first phase event), prefill-to-decode transition (phase_end of prefill), decode end
      (phase_end of decode).  Neighbour search covers the stamped edges of the kept runs and their capture only.
      Window bounds inclusive.  For the secondary edges the same run's transition is not counted as a neighbour.
  I5  Sampler level windows: the whole records lying inside the level window (start >= window start, end <=
      window end); median and sample SD over those records' summed power.  Sampler A..B: from the start of the
      record covering edge-250 ms to the end of the record covering edge+350 ms.
  I6  Meter integral over [A, B) uses the shipped km003c_parse.integrate convention: mean of the samples whose RAW
      time lies in [A, B) times (B - A).  Level windows are half-open [lo, hi) on RAW time.
  I7  Meter dropout: inside [edge-700, edge+800) a device-time gap other than one sample period, or the first or
      last sample farther than one period from the window edge.  Missing sampler record: in that window, a record
      without all three rails, a gap or overlap above 1 ms between consecutive records, or records not covering it.
  I8  Clock: per edge, ordinary least squares of poll rx on poll rt over the polls with |rt - edge| <= 30 s.
  I9  Bootstrap: one fixed seed; each iteration resamples each session's kept runs with replacement (all kept
      runs, both directions from the same draw), sessions in fixed order ALPHA, BETA, GAMMA; per-session and pooled
      T from the same draw.  Iterations where a direction has no inference edge leave that T undefined; their
      count is printed and the percentile interval is over the defined ones.  Percentiles: km003c_parse.percentile.
  I10 Reference b: RESULTS.md does not print b in ms.  b is each session's operative timing bound as recorded in
      the release-check recompute RESULTS.md cites (RC, windows.<S>.b_op_s), cross-checked against the session's
      withheld/bracket-evaluation.json assessment.b_fiducial_s.
  I11 Wording: the outcome sentence is chosen from the pooled T, per direction.  Pooled "inside" = inside +/-b for
      every session's b; "wholly outside" = outside +/-b for every session's b.  If either direction is wholly
      outside, row 2; if both directions are inside, row 1; otherwise row 3.  Per-session rows are printed too.
  I12 Step test: excluded if |L_post - L_pre| < 5 x max(SD_pre, SD_post), on either instrument.  An edge's
      reasons are all evaluated where computable; counts by reason are not exclusive.

Usage:
  python3.13 scripts/b5_edge_check.py --selftest       # synthetic fixture only
  python3.13 scripts/b5_edge_check.py --out DIR        # the real run
"""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from joulewise.external import km003c_parse  # noqa: E402

ARCHIVE = Path("/Volumes/JW-EXT/air-home/night-archive")
RC_PATH = Path("/Volumes/JW-EXT/air-home/jw-b5-custody/release-check-final-20261108T0942Z/recompute.json")
SESSIONS = [
    ("ALPHA", "harvest-v5-b5-alpha-a1-20261009T2312Z"),
    ("BETA", "harvest-v5-b5-beta-a6-20261011T2011Z"),
    ("GAMMA", "harvest-v5-b5-gamma-a1-20261012T0420Z"),
]
SEED = 20261112
N_BOOT = 2000
MS = 1_000_000  # ns per ms
WINDOW = (-700 * MS, 800 * MS)
PRE = (-700 * MS, -250 * MS)
POST = (350 * MS, 800 * MS)
SPAN = (-250 * MS, 350 * MS)
CLOCK_HALF_S = 30.0
STEP_K = 5.0
RAILS = ("cpu_power", "gpu_power", "ane_power")
GAP_TOL_NS = 1 * MS
PRIMARY = {"pulse_on": "rise", "pulse_off": "fall", "request_start_p2048": "rise", "decode_end": "fall"}
SECONDARY = ("request_start_short", "transition_p2048")
REASONS = ("neighbour_edge", "meter_dropout", "sampler_missing", "small_step_meter", "small_step_sampler",
           "level_sd_undefined")

WORDING = {
    1: "An exploratory cross-instrument check on released data found no pulse-to-inference difference in edge "
       "placement larger than the timing bound (T = {T}).",
    2: "An exploratory check found that the sampler places inference edges {T} ms differently from pulse edges, "
       "more than the timing bound; the pulse-derived bound may be too narrow for inference edges.",
    3: "The check did not resolve a difference at the scale of the timing bound (T = {T}).",
}
CAVEAT = ("Standing caveat: the meter reads whole-machine DC input, whose lag behind rail power may depend on step "
          "size and shape, so T mixes sampler placement with that path difference. The meter is not ground truth.")


# --------------------------------------------------------------------------
# Estimator (one estimator, both instruments)


def _median_sd(values):
    if not values:
        return None, None
    med = statistics.median(values)
    sd = statistics.stdev(values) if len(values) >= 2 else None
    return med, sd


def meter_edge(host_ns, watts, dev_ms, step_ms, E):
    """Meter step time (RAW ns) at stamped edge E (RAW ns), plus diagnostics.  host_ns sorted."""

    lo = bisect.bisect_left(host_ns, E + WINDOW[0])
    hi = bisect.bisect_left(host_ns, E + WINDOW[1])
    out = {"dropout": False, "small_step": False, "sd_undefined": False, "t": None}
    period_ns = step_ms * MS
    if hi - lo < 2 or host_ns[lo] - (E + WINDOW[0]) > period_ns or (E + WINDOW[1]) - host_ns[hi - 1] > period_ns:
        out["dropout"] = True
    elif any(dev_ms[i + 1] - dev_ms[i] != step_ms for i in range(lo, hi - 1)):
        out["dropout"] = True

    def window(a, b):
        i = bisect.bisect_left(host_ns, E + a)
        j = bisect.bisect_left(host_ns, E + b)
        return watts[i:j]

    pre, pre_sd = _median_sd(window(*PRE))
    post, post_sd = _median_sd(window(*POST))
    if pre is None or post is None or pre_sd is None or post_sd is None:
        out["sd_undefined"] = True
        return out
    out.update(L_pre=pre, L_post=post, sd_pre=pre_sd, sd_post=post_sd)
    if abs(post - pre) < STEP_K * max(pre_sd, post_sd):
        out["small_step"] = True
    if post == pre:
        return out
    A, B = E + SPAN[0], E + SPAN[1]
    span = window(*SPAN)
    if not span:
        out["dropout"] = True
        return out
    integral_ws = (sum(span) / len(span) - pre) * (B - A)  # W x ns, km003c_parse.integrate convention
    out["t"] = B - integral_ws / (post - pre)
    return out


def sampler_edge(records, E):
    """Sampler step time (RAW ns).  records: sorted list of (start_raw_ns, end_raw_ns, watts, n_rails)."""

    out = {"missing": False, "small_step": False, "sd_undefined": False, "t": None}
    w0, w1 = E + WINDOW[0], E + WINDOW[1]
    starts = [r[0] for r in records]
    i = max(bisect.bisect_right(starts, w0) - 1, 0)
    j = bisect.bisect_left(starts, w1)
    inwin = records[i:j]
    if not inwin or inwin[0][0] > w0 or inwin[-1][1] < w1:
        out["missing"] = True
    elif any(r[3] != len(RAILS) for r in inwin):
        out["missing"] = True
    elif any(abs(b[0] - a[1]) > GAP_TOL_NS for a, b in zip(inwin, inwin[1:])):
        out["missing"] = True

    def whole(a, b):
        return [r[2] for r in records if r[0] >= E + a and r[1] <= E + b]

    pre, pre_sd = _median_sd(whole(*PRE))
    post, post_sd = _median_sd(whole(*POST))
    if pre is None or post is None or pre_sd is None or post_sd is None:
        out["sd_undefined"] = True
        return out
    out.update(L_pre=pre, L_post=post, sd_pre=pre_sd, sd_post=post_sd)
    if abs(post - pre) < STEP_K * max(pre_sd, post_sd):
        out["small_step"] = True
    if post == pre or out["missing"]:
        return out
    a_t, b_t = E + SPAN[0], E + SPAN[1]
    cover = [r for r in records if r[1] > a_t and r[0] < b_t]
    if not cover or cover[0][0] > a_t or cover[-1][1] < b_t:
        out["missing"] = True
        return out
    A, B = cover[0][0], cover[-1][1]
    integral_ws = sum((r[2] - pre) * (r[1] - r[0]) for r in cover)
    out["t"] = B - integral_ws / (post - pre)
    out["A_rel_ms"], out["B_rel_ms"] = (A - E) / MS, (B - E) / MS
    return out


# --------------------------------------------------------------------------
# Synthetic fixture


def selftest() -> int:
    """A step at a known time plus noise, sampled at 20 ms (meter) and ~130 ms (sampler)."""

    rng = random.Random(7)
    worst = []
    for trial in range(200):
        E = 10_000 * MS
        t0 = E + rng.uniform(-80, 120) * MS           # the true step time
        lo_w, hi_w = (2.0, 75.0) if trial % 2 == 0 else (75.0, 2.0)   # rise and fall

        def p(t):
            return lo_w if t < t0 else hi_w

        # meter: point samples every 20 ms with a random phase, noise 0.5 W
        phase = rng.uniform(0, 20) * MS
        host = [int(E - 2_000 * MS + phase + k * 20 * MS) for k in range(200)]
        dev = [k * 20 for k in range(200)]
        watts = [p(h) + rng.gauss(0, 0.5) for h in host]
        m = meter_edge(host, watts, dev, 20, E)
        # sampler: records of 125-135 ms holding the exact average of the signal, noise 0.2 W
        recs, s = [], E - 2_000 * MS + rng.uniform(0, 130) * MS
        while s < E + 2_000 * MS:
            e = s + rng.uniform(125, 135) * MS
            frac = min(max((t0 - s) / (e - s), 0.0), 1.0)
            avg = lo_w * frac + hi_w * (1 - frac) + rng.gauss(0, 0.2)
            recs.append((s, e, avg, 3))
            s = e
        q = sampler_edge(recs, E)
        if m["t"] is None or q["t"] is None or m["dropout"] or q["missing"] or m["small_step"] or q["small_step"]:
            print(f"selftest trial {trial}: unexpected exclusion meter={m} sampler={q}")
            return 1
        worst.append(((m["t"] - t0) / MS, (q["t"] - t0) / MS))
    em = [abs(a) for a, _ in worst]
    es = [abs(b) for _, b in worst]
    print(f"selftest: 200 synthetic steps (100 rise, 100 fall), true time uniform in -80..+120 ms of the stamp")
    sm = [a for a, _ in worst]
    ss = [b for _, b in worst]
    print(f"  meter   (20 ms samples):  error mean {statistics.fmean(sm):+.2f} ms, |error| median "
          f"{statistics.median(em):.2f} ms, max {max(em):.2f} ms (one-sample quantisation, I6 convention)")
    print(f"  sampler (~130 ms records): error mean {statistics.fmean(ss):+.2f} ms, |error| median "
          f"{statistics.median(es):.2f} ms, max {max(es):.2f} ms")
    ok = max(em) <= 25.0 and max(es) <= 5.0
    # neighbour, dropout and small-step paths
    E = 10_000 * MS
    host = [int(E - 2_000 * MS + k * 20 * MS) for k in range(200)]
    dev = [k * 20 for k in range(200)]
    flat = [5.0 + rng.gauss(0, 0.5) for _ in host]
    ok &= meter_edge(host, flat, dev, 20, E)["small_step"]
    dev_drop = dev[:100] + [d + 40 for d in dev[100:]]
    ok &= meter_edge(host, [2.0 if h < E else 70.0 for h in host], dev_drop, 20, E)["dropout"]
    recs = [(E - 2_000 * MS + k * 130 * MS, E - 2_000 * MS + (k + 1) * 130 * MS, 3.0, 3) for k in range(31)]
    gappy = recs[:15] + recs[16:]
    ok &= sampler_edge(gappy, E)["missing"]
    print(f"  dropout / missing-record / small-step paths: {'ok' if ok else 'FAILED'}")
    return 0 if ok else 1


# --------------------------------------------------------------------------
# Data loading


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def kept_runs(root: Path):
    ex = json.loads((root / "derived/exclusions.json").read_text())
    ro = json.loads((root / "derived/roster.json").read_text())
    u2r = {}
    for m in ro["members"]:
        for u in m["units"]:
            u2r.setdefault((u["cell_id"], u["unit_id"]), []).append(m["run_id"])
    runs, cells = set(), {}
    for c in ex["cells"]:
        if not c["target"]:
            continue
        cells[c["cell_id"]] = c["kept_units"]
        for units in c["kept_units"].values():
            for u in units:
                runs.update(u2r[(c["cell_id"], u)])
    return sorted(runs), cells


def load_events(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_records(path: Path):
    acc = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            if row["rail"] not in RAILS:
                continue
            key = (float(row["interval_start_s"]), float(row["interval_end_s"]))
            w, n = acc.get(key, (0.0, 0))
            acc[key] = (w + float(row["power_w"]), n + 1)
    return sorted((s, e, w, n) for (s, e), (w, n) in acc.items())


def run_edges(run_id, events):
    """Stamped edges of one claim run: list of (class, rt_s)."""

    def one(etype, phase):
        hits = [e for e in events if e["event_type"] == etype and e["phase"] == phase]
        if len(hits) != 1:
            raise SystemExit(f"BLOCKED: run {run_id}: {len(hits)} {etype}/{phase} events, expected 1")
        return hits[0]

    ps = one("phase_start", "prefill")
    tokens = ps["metadata"]["prompt_tokens"]
    start = one("phase_start", "tokenize")["timestamp_s"]
    trans = one("phase_end", "prefill")["timestamp_s"]
    dend = one("phase_end", "decode")["timestamp_s"]
    long = tokens == 2048
    if tokens not in (42, 2048):
        raise SystemExit(f"BLOCKED: run {run_id}: prompt_tokens {tokens}")
    edges = [("request_start_p2048" if long else "request_start_short", start),
             ("transition_p2048" if long else "transition_short", trans),
             ("decode_end", dend)]
    return edges, tokens, trans - ps["timestamp_s"]


def capture_edges(events):
    out = []
    for e in events:
        t = e["event_type"]
        if t in ("pulse_command_on", "pulse_command_off", "warmup_command_on", "warmup_command_off"):
            cls = {"pulse_command_on": "pulse_on", "pulse_command_off": "pulse_off",
                   "warmup_command_on": "warmup_on", "warmup_command_off": "warmup_off"}[t]
            out.append((cls, e["metadata"]["clock_stamp"]["epoch_s"]))
    return sorted(out, key=lambda x: x[1])


class Clock:
    """REALTIME -> meter RAW, per edge, by a straight line of poll rx on poll rt within +/-30 s."""

    def __init__(self, batches):
        polls = sorted((b["rt"], b["rx"]) for b in batches if "rt" in b and "rx" in b)
        self.rt = [p[0] for p in polls]
        self.rx = [p[1] for p in polls]

    def fit(self, t_s):
        ref = int(round(t_s * 1e9))
        i = bisect.bisect_left(self.rt, ref - int(CLOCK_HALF_S * 1e9))
        j = bisect.bisect_right(self.rt, ref + int(CLOCK_HALF_S * 1e9))
        if j - i < 2:
            raise SystemExit(f"BLOCKED: fewer than two meter polls within 30 s of REALTIME {t_s}")
        xs = [self.rt[k] - ref for k in range(i, j)]
        y0 = self.rx[i]
        ys = [self.rx[k] - y0 for k in range(i, j)]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        a = my - slope * mx

        def to_raw(v_s):  # REALTIME epoch seconds -> RAW ns
            return y0 + a + slope * ((v_s - t_s) * 1e9)

        return to_raw, {"polls": n, "slope": slope}


# --------------------------------------------------------------------------
# Statistics


def iqr(v):
    return (km003c_parse.percentile(v, 25), km003c_parse.percentile(v, 75)) if v else (None, None)


def classify(lo, hi, bs):
    """Row of the rule's wording table for an interval against +/-b (every b in bs)."""

    if lo is None:
        return "n/a"
    if all(-b <= lo and hi <= b for b in bs):
        return "inside"
    if all(hi < -b or lo > b for b in bs):
        return "outside"
    return "other"


def fmt(x, nd=1, sign=True):
    if x is None:
        return "n/a"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", type=Path, default=Path(os.environ.get("TMPDIR", "/tmp")) / "b5-edge-check")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    t_wall = time.time()
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    print(f"b5_edge_check: script commit {head}, script sha256 {sha256(Path(__file__))}")
    print(f"rule: docs/analysis/b5/edge-check-reading-rule.md sha256 "
          f"{sha256(REPO / 'docs/analysis/b5/edge-check-reading-rule.md')}")
    print(f"seed {SEED}, bootstrap resamples {N_BOOT}")
    if selftest() != 0:
        print("BLOCKED: selftest failed")
        return 2

    rc = json.loads(RC_PATH.read_text())
    sessions = {}
    all_edges = []
    for S, dirname in SESSIONS:
        root = ARCHIVE / dirname
        runs, cells = kept_runs(root)
        # I1 cross-check against the release-check recompute
        if S == "GAMMA":
            for cid, c in rc["contrasts"].items():
                mine = [u for u in cells[cid]["quad"]]
                if sorted(c["kept_quads"]) != sorted(mine):
                    raise SystemExit(f"BLOCKED: GAMMA {cid} kept quads differ from RC")
        else:
            for cid, c in rc["reported_cells"].items():
                if cid in cells and c["kept_units"] != cells[cid]:
                    raise SystemExit(f"BLOCKED: {S} {cid} kept units differ from RC")
        b_ms = rc["windows"][S]["b_op_s"] * 1e3
        be = json.loads((root / "withheld/bracket-evaluation.json").read_text())["assessment"]["b_fiducial_s"]
        if abs(be * 1e3 - b_ms) > 1e-6:
            raise SystemExit(f"BLOCKED: {S} b mismatch RC {b_ms} vs bracket-evaluation {be * 1e3}")

        stream_path = root / "sources/night-custody/hazards/meter/stream-001.jsonl"
        stream = km003c_parse.parse(stream_path)
        if not stream.aligned:
            raise SystemExit(f"BLOCKED: {S} meter stream not aligned: {stream.fit_error}")
        clock = Clock(stream.batches)
        host, watts, dev, step = stream.host_ns, stream.watts, stream.samples.dev_ms, stream.samples.step_ms

        cap_hashes, run_info = {}, {}
        for r in runs:
            rdir = root / "sources/claim-runs" / r
            cap = rdir / "instrument_calibration/events.jsonl"
            if not cap.exists():
                raise SystemExit(f"BLOCKED: {S} kept run {r} has no calibration capture")
            cap_hashes.setdefault(sha256(cap), []).append(r)
            run_info[r] = rdir
        captures = []
        for h, rs in sorted(cap_hashes.items()):
            cdir = run_info[rs[0]] / "instrument_calibration"
            captures.append((h, cdir, rs))

        # stamped edges: every kept run and every distinct capture
        stamped = []  # (rt_s, owner, class)
        edges = []    # edges to estimate
        p2048 = {}
        for r in runs:
            ev = load_events(run_info[r] / "events.jsonl")
            redges, tokens, prefill_s = run_edges(r, ev)
            # Fix 1 (DEVIATION-LOG, edge check): the model label for check (a) came from the prefill event's
            # item_id, which 2,048-token runs do not carry; it now comes from the run's config.json.  Label only.
            model = json.loads((run_info[r] / "config.json").read_text())["model"]["name"]
            if tokens == 2048:
                p2048.setdefault(model, []).append(prefill_s)
            for cls, t in redges:
                stamped.append((t, r, cls))
                if cls in PRIMARY or cls in SECONDARY:
                    edges.append({"session": S, "owner": r, "run": r, "class": cls, "rt_s": t,
                                  "source": run_info[r]})
        for h, cdir, rs in captures:
            ev = load_events(cdir / "events.jsonl")
            for cls, t in capture_edges(ev):
                stamped.append((t, h, cls))
                if cls in ("pulse_on", "pulse_off"):
                    edges.append({"session": S, "owner": h, "run": None, "class": cls, "rt_s": t,
                                  "source": cdir})
        stamped.sort()
        st_t = [s[0] for s in stamped]

        rec_cache = {}
        for e in edges:
            reasons = []
            t = e["rt_s"]
            i = bisect.bisect_left(st_t, t + WINDOW[0] / 1e9)
            j = bisect.bisect_right(st_t, t + WINDOW[1] / 1e9)
            for k in range(i, j):
                tt, owner, cls = stamped[k]
                if owner == e["owner"] and cls == e["class"] and tt == t:
                    continue  # the edge itself
                if e["class"] in SECONDARY and owner == e["owner"] and cls.startswith("transition"):
                    continue  # the transition itself, for the secondary edges
                reasons.append("neighbour_edge")
                break
            to_raw, cinfo = clock.fit(t)
            E = to_raw(t)
            m = meter_edge(host, watts, dev, step, E)
            src = e["source"]
            if src not in rec_cache:
                rec_cache[src] = load_records(src / "power_trace.csv")
            recs = [(to_raw(s), to_raw(en), w, n) for s, en, w, n in rec_cache[src]
                    if s < t + 2.0 and en > t - 2.0]
            q = sampler_edge(recs, E)
            if m["dropout"]:
                reasons.append("meter_dropout")
            if q["missing"]:
                reasons.append("sampler_missing")
            if m["small_step"]:
                reasons.append("small_step_meter")
            if q["small_step"]:
                reasons.append("small_step_sampler")
            if m["sd_undefined"] or q["sd_undefined"]:
                reasons.append("level_sd_undefined")
            delta = None
            if not reasons:
                if m["t"] is None or q["t"] is None:
                    raise SystemExit(f"BLOCKED: {S} {e['class']} at {t}: estimator undefined without a reason")
                delta = (q["t"] - m["t"]) / MS
            e.update(reasons=reasons, delta_ms=delta, clock_polls=cinfo["polls"],
                     meter={k: v for k, v in m.items() if k != "t"}, sampler={k: v for k, v in q.items() if k != "t"},
                     meter_t_rel_ms=None if m["t"] is None else (m["t"] - E) / MS,
                     sampler_t_rel_ms=None if q["t"] is None else (q["t"] - E) / MS)
            del e["source"]
        sessions[S] = {"runs": runs, "b_ms": b_ms, "edges": edges, "captures": captures, "p2048": p2048,
                       "stream_sha256": sha256(stream_path), "fit": stream.fit.stats, "stamped": stamped}
        all_edges.extend(edges)
        print(f"{S}: {len(runs)} kept runs, {len(captures)} distinct calibration capture(s) "
              f"(carried by {[len(c[2]) for c in captures]} runs), b = {b_ms:.3f} ms, "
              f"meter stream sha256 {sessions[S]['stream_sha256'][:16]}...")

    # ---------------- assumption checks (stamps only)
    print("\n## Assumption checks (from stamps only)")
    for S, d in sessions.items():
        for model, v in d["p2048"].items():
            if v:
                print(f"(a) {S} {model} 2,048-token prefill duration: n {len(v)}, min {min(v) * 1e3:.0f} ms, "
                      f"median {statistics.median(v) * 1e3:.0f} ms, max {max(v) * 1e3:.0f} ms "
                      f"({'longer' if min(v) > 0.8 else 'NOT longer'} than the +800 ms window end)")
        cap_st = sorted((t, c) for t, o, c in d["stamped"] if c.startswith(("pulse", "warmup")))
        off_on = [b[0] - a[0] for a, b in zip(cap_st, cap_st[1:]) if a[1].endswith("off") and b[1].endswith("on")]
        on_off = [b[0] - a[0] for a, b in zip(cap_st, cap_st[1:]) if a[1].endswith("on") and b[1].endswith("off")]
        print(f"(b) {S} pulse gaps (OFF to next ON, incl. warmups): min {min(off_on) * 1e3:.0f} ms, "
              f"max {max(off_on) * 1e3:.0f} ms; pulse widths (ON to OFF): min {min(on_off) * 1e3:.0f} ms; "
              f"pulses per capture: {sum(1 for t, c in cap_st if c == 'pulse_on') // len(d['captures'])} "
              f"(+{sum(1 for t, c in cap_st if c == 'warmup_on') // len(d['captures'])} warmup)")

    # ---------------- exclusions
    classes = ["pulse_on", "pulse_off", "request_start_p2048", "decode_end", "request_start_short",
               "transition_p2048"]
    print("\n## Exclusions by reason (an edge may carry more than one reason)")
    print("| Session | Edge class | Stamped | " + " | ".join(REASONS) + " | Excluded | Kept |")
    print("|---|---|---|" + "---|" * len(REASONS) + "---|---|")
    for S, d in sessions.items():
        for cls in classes:
            es = [e for e in d["edges"] if e["class"] == cls]
            if not es:
                print(f"| {S} | {cls} | 0 |" + " - |" * len(REASONS) + " 0 | 0 |")
                continue
            cnt = [sum(1 for e in es if r in e["reasons"]) for r in REASONS]
            exc = sum(1 for e in es if e["reasons"])
            print(f"| {S} | {cls} | {len(es)} | " + " | ".join(map(str, cnt)) + f" | {exc} | {len(es) - exc} |")

    # ---------------- per-session and pooled T
    def deltas(es, cls):
        return [e["delta_ms"] for e in es if e["class"] == cls and e["delta_ms"] is not None]

    pulse_cls = {"rise": "pulse_on", "fall": "pulse_off"}
    inf_cls = {"rise": "request_start_p2048", "fall": "decode_end"}
    point = {}
    run_d = {}
    for S, d in sessions.items():
        by_run = {r: {"rise": [], "fall": []} for r in d["runs"]}
        for e in d["edges"]:
            if e["run"] and e["delta_ms"] is not None and e["class"] in PRIMARY:
                by_run[e["run"]][PRIMARY[e["class"]]].append(e["delta_ms"])
        run_d[S] = by_run
        for dr in ("rise", "fall"):
            pv = deltas(d["edges"], pulse_cls[dr])
            iv = deltas(d["edges"], inf_cls[dr])
            point[(S, dr)] = (pv, iv)
    pooled_pulse = {dr: [x for S in sessions for x in point[(S, dr)][0]] for dr in ("rise", "fall")}
    pooled_inf = {dr: [x for S in sessions for x in point[(S, dr)][1]] for dr in ("rise", "fall")}

    rng = random.Random(SEED)
    boots = {(S, dr): [] for S in list(sessions) + ["POOLED"] for dr in ("rise", "fall")}
    undefined = {k: 0 for k in boots}
    pmed = {(S, dr): (statistics.median(point[(S, dr)][0]) if point[(S, dr)][0] else None)
            for S in sessions for dr in ("rise", "fall")}
    pmed_pooled = {dr: statistics.median(pooled_pulse[dr]) if pooled_pulse[dr] else None for dr in ("rise", "fall")}
    for _ in range(N_BOOT):
        pooled = {"rise": [], "fall": []}
        for S, d in sessions.items():
            runs = d["runs"]
            draw = [runs[rng.randrange(len(runs))] for _ in runs]
            for dr in ("rise", "fall"):
                v = [x for r in draw for x in run_d[S][r][dr]]
                pooled[dr].extend(v)
                if v and pmed[(S, dr)] is not None:
                    boots[(S, dr)].append(statistics.median(v) - pmed[(S, dr)])
                else:
                    undefined[(S, dr)] += 1
        for dr in ("rise", "fall"):
            if pooled[dr] and pmed_pooled[dr] is not None:
                boots[("POOLED", dr)].append(statistics.median(pooled[dr]) - pmed_pooled[dr])
            else:
                undefined[("POOLED", dr)] += 1

    bs_all = [d["b_ms"] for d in sessions.values()]
    rows = []
    print("\n## Per session and direction (primary edges; Delta = sampler minus meter, ms)")
    print("| Session | b (ms) | Direction | Pulse n | Pulse median | Pulse IQR | Inference n | Inference median "
          "| Inference IQR | T (ms) | 95% interval | Undefined resamples | Reading |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    results = {}
    for S in list(sessions) + ["POOLED"]:
        for dr in ("rise", "fall"):
            if S == "POOLED":
                pv, iv, bref = pooled_pulse[dr], pooled_inf[dr], bs_all
                bstr = "/".join(f"{b:.1f}" for b in bs_all)
            else:
                pv, iv = point[(S, dr)]
                bref = [sessions[S]["b_ms"]]
                bstr = f"{sessions[S]['b_ms']:.1f}"
            T = statistics.median(iv) - statistics.median(pv) if (pv and iv) else None
            bt = boots[(S, dr)]
            lo = km003c_parse.percentile(bt, 2.5) if (bt and T is not None) else None
            hi = km003c_parse.percentile(bt, 97.5) if (bt and T is not None) else None
            reading = classify(lo, hi, bref)
            results[(S, dr)] = {"T": T, "lo": lo, "hi": hi, "reading": reading, "n_pulse": len(pv),
                                "n_inf": len(iv), "undefined": undefined[(S, dr)]}
            pq, iq = iqr(pv), iqr(iv)
            print(f"| {S} | {bstr} | {dr} | {len(pv)} | {fmt(statistics.median(pv) if pv else None)} | "
                  f"[{fmt(pq[0])}, {fmt(pq[1])}] | {len(iv)} | {fmt(statistics.median(iv) if iv else None)} | "
                  f"[{fmt(iq[0])}, {fmt(iq[1])}] | {fmt(T)} | [{fmt(lo)}, {fmt(hi)}] | {undefined[(S, dr)]} | "
                  f"{reading} |")

    print("\n## Secondary inference edges (reported, not in T)")
    print("| Session | Edge class | n kept | Median Delta (ms) | IQR |")
    print("|---|---|---|---|---|")
    for S, d in sessions.items():
        for cls in SECONDARY:
            v = deltas(d["edges"], cls)
            q = iqr(v)
            print(f"| {S} | {cls} | {len(v)} | {fmt(statistics.median(v) if v else None)} | "
                  f"[{fmt(q[0])}, {fmt(q[1])}] |")

    # ---------------- wording (I11)
    pr = {dr: results[("POOLED", dr)] for dr in ("rise", "fall")}
    if any(pr[dr]["reading"] == "outside" for dr in pr):
        row = 2
        tt = "; ".join(f"{fmt(pr[dr]['T'])} ({dr} edges; 95% interval {fmt(pr[dr]['lo'])} to {fmt(pr[dr]['hi'])})"
                       for dr in ("rise", "fall") if pr[dr]["reading"] == "outside")
        sentence = WORDING[2].format(T=tt)
    else:
        row = 1 if all(pr[dr]["reading"] == "inside" for dr in pr) else 3
        tt = ", ".join(f"{fmt(pr[dr]['T'])} ms, 95% interval [{fmt(pr[dr]['lo'])}, {fmt(pr[dr]['hi'])}] ms, for {dr}s"
                       for dr in ("rise", "fall"))
        sentence = WORDING[row].format(T=tt)
    print(f"\n## Outcome (rule §1 row {row}, from the pooled T per direction; I11)")
    print(sentence)
    print(CAVEAT)

    args.out.mkdir(parents=True, exist_ok=True)
    edges_path = args.out / "edges.json"
    edges_path.write_text(json.dumps(all_edges, indent=1, default=str))
    print(f"\nper-edge output: {edges_path} sha256 {sha256(edges_path)}")
    print(f"wall time {time.time() - t_wall:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
