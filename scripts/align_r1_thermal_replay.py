#!/usr/bin/env python3
"""R1 thermal replay desk (RL-59 item 4, step 1). Stdlib only, temperatures only.

Question: had each D-type member of the ALIGN v4 R1 rehearsal (custody
r1-20261111T043229Z, build da3187e6e) been gated against its OWN pre-warmup
60 s median instead of R_op (the cold step-30b pre-warmup reference), would
its G0 start gate have released, and when?

RL-64 extension (Sol design seat): --consume-label adds the D capture consume
case, at both 1.0 and 1.5 C, alongside own and recorded references. It prints
fast/slow release margins and censors counterfactuals at the recorded G0 end.
The original recorded-outcome self-check remains mandatory. Planning rows
are threshold tests on the old heater trace, never a heater counterfactual.

The script re-implements, at da3187e6e, the registered G0 release rule and the
window-reference capture, and replays them on each member's own thermal
journal (``outputs/align_thermal.jsonl``). Before it prints any own-reference
verdict it replays every member against the reference the night actually used
and requires that replay to reproduce the outcome the journal recorded. If it
does not, the replay is wrong: the script says so and stops (exit 2).

Sources, all at da3187e6e:

* ``joulewise/align/apple/thermal_gates.py``
  - :23-24   G0_CAP_DEFAULT_S = 600, G0_CAP_MAX_S = 1200
  - :73-92   sample_rows (journal ``reading`` row -> sample projection)
  - :220-224 _good_window_rows (60 s window, read bracket <= 1 s, valid keys)
  - :227-234 _window_coverage (Coverage over the 60 s window, grid = first row)
  - :237-248 slow_slope (OLS degC/min over the preceding 60 s, coverage >= .9)
  - :396-414 capture_reference (warmup entry; final 60 s; median; coverage >= .9)
  - :459-593 wait('G0'): 10 consecutive good samples (:487); good = observed,
    continuous (<= 2 s, :516), fresh (<= 2 s, :518), valid, fast <= R_f + d_f,
    slow <= R_s + d_s (:520-521), |slope| <= 0.2 degC/min, os_level 0,
    pm_state Nominal, pm observation <= 2 s old (:525-528); unobserved
    (coverage < .9, :506-509) caps the wait at 300 s (:537), else the cap.
* ``joulewise/align/apple/thermal.py``
  - :44-46   valid_value (finite, -40..150 degC for T keys)
  - :195-267 Coverage (100 ms tolerance, 1 s grid, all_keys sample_fraction)
* ``joulewise/align/apple/workload.py`` :394-396: capture_reference is called
  at the start of the runtime warmup; ``joulewise/controller.py`` :2445-2446
  emits ``stage_started warmup`` immediately before it. That event's
  timestamp is the anchor this replay uses (validated on step-30b against its
  own ``align_window_reference.json``).
* ``joulewise/align/apple/r1_runtime.py``
  - :84      PLANNING_FAST_CEILING_C = 150.0 (planning gates band S_slow only)
  - :87      BAND_FLOOR_C = 1.0 (delta_fast = max(1.0, 3 SD), :409-425)
  - :441     g0_timeout_s (the 1,200 s R1 G0 timeout, R7-2)
  - :1493-1530 reference_hook: R_op installed before warmup, so
    capture_reference returns early (thermal_gates.py:398) for every consumer
  - :1532-1545 planning_hook: G0 reference = (150.0, R_op_slow + offset)
* ``configs/campaigns/align_v4/registration/r1_slots.json`` :21 S6 = 1.5 degC
  (delta_slow, adopted by RL-32).

Blinding. Each journal line is parsed and immediately projected onto an
allow-list: kind, read stamps, the two gate sensor temperatures and their
read errors, the thermal status (os_level, pm_state and the pm observation
stamp, all gate inputs) and the recorded G0 interval (outcome, times,
reference and release temperatures, slope). Nothing else in a row is kept,
and the script refuses any energy, power, joule, watt, token or performance
field, and any non-temperature field, if one is requested with --field.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from statistics import median

NS = 1_000_000_000
JOURNAL_NAME = "align_thermal.jsonl"
JOURNAL_SCHEMA = "joulewise.align_thermal.v1"

# Registered parameters (sources in the module docstring).
G0_CAP_DEFAULT_S = 600          # thermal_gates.py:23 (sensors-only release sessions)
G0_CAP_R1_S = 1200              # thermal_gates.py:24; r1_runtime.py:441 (R7-2)
DELTA_FAST_C = 1.0              # r1_runtime.py:87, :409-425 (soak 3 SD below the floor)
DELTA_SLOW_C = 1.5              # r1_slots.json:21 S6 (RL-32)
SLOPE_MAX_C_PER_MIN = 0.2       # thermal_gates.py:526
REQUIRED_CONSECUTIVE = 10       # thermal_gates.py:487 (G0)
WINDOW_S = 60                   # thermal_gates.py:221, :401
MIN_COVERAGE = 0.9              # thermal_gates.py:204, :242, :406, :507
UNOBSERVED_LIMIT_S = 300        # thermal_gates.py:537
CONTINUITY_S = 2                # thermal_gates.py:516
FRESH_S = 2                     # thermal_gates.py:518, :528
COVERAGE_TOLERANCE_NS = NS // 10  # thermal.py:207
PLANNING_FAST_CEILING_C = 150.0  # r1_runtime.py:84
RELEASE_TIME_TOLERANCE_S = 2.0  # replay vs recorded: a 1 Hz loop, poll phase unknown

FORBIDDEN = re.compile(
    r"energy|power|joule|watt|token|tok_s|tps|perf|throughput|latency|score|"
    r"soc|battery|drain|current|volt|amp|(^|_)(j|mj|w|mw|uj)$", re.IGNORECASE)
TEMPERATURE_KEY = re.compile(r"T[!-~]{3}")


class Refused(RuntimeError):
    pass


class SelfCheckFailed(RuntimeError):
    pass


def require_temperature_field(name):
    """Allow only an SMC temperature key; refuse energy/power/token/perf names."""
    if not isinstance(name, str) or FORBIDDEN.search(name):
        raise Refused(f"refused field {name!r}: energy, power, joule, watt, token and "
                      "performance fields are never read by the thermal replay")
    if not TEMPERATURE_KEY.fullmatch(name):
        raise Refused(f"refused field {name!r}: not an SMC temperature key (T???)")
    return name


def valid_value(key, value):
    """thermal.py:44-46."""
    return (type(value) in (int, float) and math.isfinite(value)
            and (-40 <= value <= 150 if key.startswith("T") else value >= 0))


# Journal projection -----------------------------------------------------------

def _project_stamp(stamp):
    return {"monotonic_ns": stamp["monotonic_ns"], "wall_ns": stamp["wall_ns"]}


def _project_status(status):
    if not isinstance(status, dict):
        return {}
    return {k: status[k] for k in ("os_level", "pm_state", "pm_observed_ns", "monotonic_ns")
            if k in status}


def _project_ref(value):
    if not isinstance(value, dict):
        return None
    return {k: value.get(k) for k in ("fast_c", "slow_c")}


def project_line(raw, temps):
    """One journal row reduced to the allow-list. ``temps`` are T keys only."""
    kind = raw.get("kind")
    if raw.get("schema") != JOURNAL_SCHEMA or raw.get("module") != "temperature":
        raise Refused("not a joulewise.align_thermal.v1 temperature row")
    values = raw.get("values") if isinstance(raw.get("values"), dict) else {}
    if kind == "reading":
        sensors = values.get("sensors") or {}
        errors = values.get("errors") or {}
        return {"kind": "reading", "started": _project_stamp(raw["started"]),
                "finished": _project_stamp(raw["finished"]),
                "sensors": {k: sensors.get(k) for k in temps},
                "errors": {k: "error" for k in temps if k in errors},
                "status": _project_status(values.get("status"))}
    if kind == "session_start":
        thermal = values.get("thermal") or {}
        return {"kind": kind, "s_fast": thermal.get("s_fast"), "s_slow": thermal.get("s_slow")}
    if kind == "align_thermal_gate" and values.get("state") == "end":
        gate = values.get("gate") or {}
        if gate.get("kind") != "G0":
            return None
        return {"kind": "g0_end", "outcome": gate.get("outcome"), "start_ns": gate.get("start_ns"),
                "end_ns": gate.get("end_ns"), "duration_s": gate.get("duration_s"),
                "reference": _project_ref(gate.get("reference")),
                "reference_source": (gate.get("reference") or {}).get("source_member"),
                "release": _project_ref(gate.get("release")),
                "slope_c_per_min": gate.get("slope_c_per_min"),
                "exit_sample_ns": gate.get("exit_sample_ns")}
    return None


def read_journal(path, sha256=None, extra_fields=()):
    path = Path(path)
    if path.name != JOURNAL_NAME:
        raise Refused(f"{path}: only {JOURNAL_NAME} thermal journals are read")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if sha256 is not None and digest != sha256:
        raise Refused(f"{path}: sha256 {digest} != manifest {sha256}")
    lines = [json.loads(line) for line in raw.splitlines() if line.strip()]
    start = next((r for r in lines if r.get("kind") == "session_start"), None)
    if start is None:
        raise Refused(f"{path}: no session_start row")
    head = project_line(start, ())
    temps = [require_temperature_field(head["s_fast"]), require_temperature_field(head["s_slow"])]
    temps += [require_temperature_field(f) for f in extra_fields if f not in temps]
    projected = [p for p in (project_line(r, temps) for r in lines) if p is not None]
    del lines, raw
    readings = [p for p in projected if p["kind"] == "reading"]
    gates = [p for p in projected if p["kind"] == "g0_end"]
    return {"sha256": digest, "s_fast": temps[0], "s_slow": temps[1], "extra": temps[2:],
            "rows": sample_rows(readings), "g0": gates}


def sample_rows(readings):
    """thermal_gates.py:73-92 for projected reading rows."""
    out = []
    for r in readings:
        out.append({"monotonic_ns": r["started"]["monotonic_ns"], "wall_ns": r["started"]["wall_ns"],
                    "finished_ns": r["finished"]["monotonic_ns"], "sensors": r["sensors"],
                    "errors": r["errors"], "status": r["status"]})
    out.sort(key=lambda r: r["monotonic_ns"])
    return out


# Coverage, window rows, slope --------------------------------------------------

def coverage_fraction(rows, keys, start_ns, end_ns, grid_ns):
    """thermal.py:195-267 Coverage(start).observe(...).report(end)['all_keys']['sample_fraction'],
    as called by thermal_gates.py:227-234 (grid preset to the session's first row)."""
    tol = COVERAGE_TOLERANCE_NS
    grid = grid_ns
    stamps = []
    for r in rows:
        started, finished = r["monotonic_ns"], r["finished_ns"]
        if finished < started or finished - started > NS:
            continue
        grid = min(grid, started) if grid is not None else started
        if all(k not in r["errors"] and valid_value(k, r["sensors"].get(k)) for k in keys):
            stamps.append((started + finished) // 2)
    if end_ns < start_ns:
        raise ValueError("temperature span ends before it starts")
    grid = start_ns if grid is None else grid

    def nearest(t):
        return (t - grid + NS // 2) // NS

    def boundary(t):
        snapped = grid + nearest(t) * NS
        return snapped if abs(t - snapped) <= tol else t
    first = -((grid - boundary(start_ns)) // NS)
    last = (boundary(end_ns) - grid) // NS
    expected = max(0, last - first) if end_ns > start_ns else 0
    ticks = {nearest(t) for t in stamps
             if first <= nearest(t) < last and abs(t - (grid + nearest(t) * NS)) <= tol}
    return len(ticks) / expected if expected else None


class Session:
    """The rows a ThermalSession held, with bisect windows for speed."""

    def __init__(self, rows, s_fast, s_slow):
        self.rows, self.fast, self.slow = rows, s_fast, s_slow
        self.times = [r["monotonic_ns"] for r in rows]
        self.grid = rows[0]["monotonic_ns"] if rows else None
        # A row joins the session snapshot only once its tick (SMC read, then
        # status read) has finished (thermal.py:134-148).
        self.avail = [max(r["finished_ns"], r["status"].get("monotonic_ns") or 0) for r in rows]

    def visible(self, now_ns):
        """Index bound of rows the session snapshot would hold at ``now_ns``."""
        return bisect.bisect_right(self.avail, now_ns)

    def _slice(self, lo_ns, hi_ns, limit):
        a = bisect.bisect_left(self.times, lo_ns, 0, limit)
        b = bisect.bisect_right(self.times, hi_ns, 0, limit)
        return self.rows[a:b]

    def coverage(self, end_ns, keys, limit):
        start = end_ns - WINDOW_S * NS
        rows = self._slice(start - NS, end_ns + NS, limit)
        return coverage_fraction(rows, keys, start, end_ns, self.grid)

    def good_window(self, end_ns, keys, limit):
        """thermal_gates.py:220-224."""
        start = end_ns - WINDOW_S * NS
        return [r for r in self._slice(start, end_ns - 1, limit)
                if start <= r["monotonic_ns"] < end_ns
                and 0 <= r["finished_ns"] - r["monotonic_ns"] <= NS
                and all(k not in r["errors"] and valid_value(k, r["sensors"].get(k)) for k in keys)]

    def slope(self, end_ns, limit):
        """thermal_gates.py:237-248."""
        key = self.slow
        good = [(r["monotonic_ns"], r["sensors"][key]) for r in self.good_window(end_ns, (key,), limit)]
        fraction = self.coverage(end_ns, (key,), limit)
        if fraction is None or fraction < MIN_COVERAGE:
            return None
        x = [(t - end_ns) / NS for t, _ in good]
        y = [v for _, v in good]
        xm, ym = sum(x) / len(x), sum(y) / len(y)
        denom = sum((t - xm) ** 2 for t in x)
        return 60 * sum((t - xm) * (v - ym) for t, v in zip(x, y)) / denom if denom else None

    def capture_reference(self, now_ns):
        """thermal_gates.py:396-414 at warmup entry ``now_ns``."""
        keys = (self.fast, self.slow)
        limit = self.visible(now_ns)
        good = self.good_window(now_ns, keys, limit)
        fraction = self.coverage(now_ns, keys, limit)
        if fraction is None or fraction < MIN_COVERAGE:
            return {"captured": False, "coverage": fraction}
        times = [r["monotonic_ns"] for r in good]
        start = now_ns - WINDOW_S * NS
        margin = min(min(t - start for t in times), min(now_ns - t for t in times)) / NS
        return {"captured": True, "coverage": fraction, "samples": len(good),
                "fast_c": median(r["sensors"][self.fast] for r in good),
                "slow_c": median(r["sensors"][self.slow] for r in good),
                "edge_margin_s": margin}

    def mono_from_epoch(self, epoch_s):
        """Map a controller epoch stamp onto the journal's monotonic clock using
        the nearest reading's paired (wall_ns, monotonic_ns) stamp."""
        target = round(epoch_s * NS)
        row = min(self.rows, key=lambda r: abs(r["wall_ns"] - target))
        return target - (row["wall_ns"] - row["monotonic_ns"])


def replay_g0(session, start_ns, reference, *, cap_s, delta_fast_c=DELTA_FAST_C,
              delta_slow_c=DELTA_SLOW_C, use_status=True, observed_until_ns=None):
    """thermal_gates.py:459-593 for kind G0 on a recorded sample stream.

    The live loop polled about once a second; the replay polls once per
    sample, at the moment the sample joined the session snapshot.
    """
    fast, slow = session.fast, session.slow
    keys = (fast, slow)
    first = session.visible(start_ns)
    polls = [start_ns] + [t for t in session.avail[first:] if t > start_ns]
    if observed_until_ns is not None:
        if observed_until_ns < start_ns:
            raise Refused("observation ends before G0 starts")
        polls = [t for t in polls if t <= observed_until_ns]
        if polls[-1] != observed_until_ns:
            polls.append(observed_until_ns)
    consecutive, last_ns, unobserved = 0, None, reference is None
    latest = None
    slope = None
    outcome, release_ns = "timeout", None
    for now in polls:
        limit = session.visible(now)
        latest = session.rows[limit - 1] if limit else None
        fraction = session.coverage(now, keys, limit)
        if fraction is None or fraction < MIN_COVERAGE:
            unobserved = True
        slope = session.slope(now, limit)
        new_rows = (session.rows[max(0, limit - 1):limit] if last_ns is None else
                    session.rows[bisect.bisect_right(session.times, last_ns, 0, limit):limit])
        for sample in new_rows:
            continuous = last_ns is None or 0 < sample["monotonic_ns"] - last_ns <= CONTINUITY_S * NS
            last_ns = sample["monotonic_ns"]
            values = sample["sensors"]
            good = (not unobserved and continuous and 0 <= now - last_ns <= FRESH_S * NS
                    and all(valid_value(k, values.get(k)) for k in keys)
                    and values[fast] <= reference["fast_c"] + delta_fast_c
                    and values[slow] <= reference["slow_c"] + delta_slow_c)
            sample_slope = session.slope(last_ns, limit)
            good = good and sample_slope is not None and abs(sample_slope) <= SLOPE_MAX_C_PER_MIN
            if use_status:
                status = sample["status"]
                pm_ns = status.get("pm_observed_ns")
                good = (good and status.get("os_level") == 0 and status.get("pm_state") == "Nominal"
                        and type(pm_ns) is int and 0 <= now - pm_ns <= FRESH_S * NS)
            consecutive = consecutive + 1 if good else 0
        if new_rows and consecutive >= REQUIRED_CONSECUTIVE:
            outcome, release_ns = "released", now
            break
        elapsed = (now - start_ns) / NS
        if elapsed >= (UNOBSERVED_LIMIT_S if unobserved else cap_s):
            break
    if outcome == "timeout" and unobserved:
        outcome = "unobserved"
    elif outcome == "timeout" and observed_until_ns is not None and (now - start_ns) / NS < cap_s:
        # After the recorded release the workload/heater control changes. A
        # tighter counterfactual cannot borrow those later observations.
        outcome = "right_censored"
    end_ns = release_ns if release_ns is not None else now
    values = latest["sensors"] if latest else {}
    return {"outcome": outcome, "wait_s": (end_ns - start_ns) / NS,
            "slow_c": values.get(slow), "fast_c": values.get(fast), "slope_c_per_min": slope,
            "sample_ns": latest["monotonic_ns"] if latest else None}


def followup_cases(member, journal, own, consume_references, *, use_status=True):
    """RL-64: own, recorded and D-consumed references at both slow bands.

    The journal is evidence only through its recorded G0 end. Planning cases
    apply the new thresholds to the OLD heater trace, not a new heater run.
    Margins are band edge minus release temperature, positive inside.
    """
    session = Session(journal["rows"], journal["s_fast"], journal["s_slow"])
    g0 = journal["g0"][0]
    refs = {"recorded": g0["reference"]}
    if own and own.get("captured"):
        refs["own"] = {k: own[k] for k in ("fast_c", "slow_c")}
    refs.update(consume_references)
    offset = member.get("planning_offset_c", 0.0)
    out = []
    for label, base in refs.items():
        ref = dict(base)
        if member["role"] == "planning" and label != "recorded":
            ref = {"fast_c": PLANNING_FAST_CEILING_C, "slow_c": base["slow_c"] + offset}
        for delta in (1.0, 1.5):
            result = replay_g0(session, g0["start_ns"], ref,
                               cap_s=G0_CAP_DEFAULT_S if member["role"] == "release_check" else G0_CAP_R1_S,
                               delta_slow_c=delta, use_status=use_status, observed_until_ns=g0["end_ns"])
            released = result["outcome"] == "released"
            out.append({"reference_label": label, "reference": ref, "delta_slow_c": delta, **result,
                        "fast_margin_c": ref["fast_c"] + DELTA_FAST_C - result["fast_c"] if released else None,
                        "slow_margin_c": ref["slow_c"] + delta - result["slow_c"] if released else None,
                        "trace_only": member["role"] == "planning"})
    return out


# Desk -------------------------------------------------------------------------

def _check(condition, message, failures):
    if not condition:
        failures.append(message)


def replay_member(member, journal, r_op, cap_s, use_status=True):
    session = Session(journal["rows"], journal["s_fast"], journal["s_slow"])
    if len(journal["g0"]) != 1:
        raise Refused(f"{member['label']}: expected one recorded G0 interval, found {len(journal['g0'])}")
    g0 = journal["g0"][0]
    recorded_ref = g0["reference"]
    role = member["role"]
    offset = member.get("planning_offset_c", 0.0)
    out = {"label": member["label"], "role": role, "recorded": g0, "s_fast": journal["s_fast"],
           "s_slow": journal["s_slow"]}
    failures = []
    if role == "planning":
        _check(recorded_ref["fast_c"] == PLANNING_FAST_CEILING_C
               and math.isclose(recorded_ref["slow_c"], r_op["slow_c"] + offset, abs_tol=1e-9),
               f"{member['label']}: recorded planning reference is not (150, R_op_slow + {offset})", failures)
    elif role in ("gated", "release_check"):
        _check(recorded_ref == {"fast_c": r_op["fast_c"], "slow_c": r_op["slow_c"]},
               f"{member['label']}: recorded G0 reference is not R_op", failures)
    # Self-check: the rule against the reference the night used.
    check = replay_g0(session, g0["start_ns"], recorded_ref, cap_s=cap_s, use_status=use_status)
    out["check"] = check
    _check(check["outcome"] == g0["outcome"],
           f"{member['label']}: replay against the recorded reference gives {check['outcome']}, "
           f"journal recorded {g0['outcome']}", failures)
    if g0["outcome"] == "released":
        _check(abs(check["wait_s"] - g0["duration_s"]) <= RELEASE_TIME_TOLERANCE_S,
               f"{member['label']}: replayed release {check['wait_s']:.2f} s vs recorded "
               f"{g0['duration_s']:.2f} s", failures)
    if member.get("expected_outcome") is not None:
        _check(g0["outcome"] == member["expected_outcome"],
               f"{member['label']}: journal outcome {g0['outcome']} != r1_result {member['expected_outcome']}",
               failures)
    out["edge_rop_slow_c"] = recorded_ref["slow_c"] + DELTA_SLOW_C
    if member.get("warmup_entry_epoch_s") is not None:
        anchor = session.mono_from_epoch(member["warmup_entry_epoch_s"])
        own = session.capture_reference(anchor)
        out["own"] = own
        if own["captured"]:
            out["own_minus_rop"] = {"fast_c": own["fast_c"] - r_op["fast_c"],
                                    "slow_c": own["slow_c"] - r_op["slow_c"]}
            if role == "planning":
                own_ref = {"fast_c": PLANNING_FAST_CEILING_C, "slow_c": own["slow_c"] + offset}
            else:
                own_ref = {"fast_c": own["fast_c"], "slow_c": own["slow_c"]}
            out["own_reference"] = own_ref
            out["edge_own_slow_c"] = own_ref["slow_c"] + DELTA_SLOW_C
            out["own_replay"] = replay_g0(session, g0["start_ns"], own_ref, cap_s=cap_s,
                                          use_status=use_status)
    return out, failures


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    policy = manifest["policy"]
    registered = {"delta_fast_c": DELTA_FAST_C, "delta_slow_c": DELTA_SLOW_C, "g0_cap_s": G0_CAP_R1_S}
    for key, value in registered.items():
        if policy.get(key) != value:
            raise Refused(f"manifest policy {key}={policy.get(key)!r} is not the registered {value!r}")
    return manifest


def run(manifest_path, root, *, use_status=True, extra_fields=(), consume_labels=()):
    for f in extra_fields:
        require_temperature_field(f)
    manifest = load_manifest(manifest_path)
    root = Path(root)
    members = manifest["members"]
    control = next(m for m in members if m["role"] == "control")
    journals = {m["label"]: read_journal(root / m["journal"], m.get("sha256"), extra_fields)
                for m in members}
    for m in members:
        j = journals[m["label"]]
        if (j["s_fast"], j["s_slow"]) != (manifest["policy"]["s_fast"], manifest["policy"]["s_slow"]):
            raise Refused(f"{m['label']}: journal sensors {j['s_fast']}/{j['s_slow']} differ from the policy")
    failures = []
    # R_op: step-30b's own pre-warmup median, which must equal the recorded record.
    cj = journals[control["label"]]
    cs = Session(cj["rows"], cj["s_fast"], cj["s_slow"])
    captured = cs.capture_reference(cs.mono_from_epoch(control["warmup_entry_epoch_s"]))
    expected = manifest["r_op"]
    if not captured["captured"]:
        failures.append("step-30b: R_op could not be recomputed (coverage < 0.9)")
        r_op = expected
    else:
        r_op = {"fast_c": captured["fast_c"], "slow_c": captured["slow_c"]}
        _check(r_op == {"fast_c": expected["fast_c"], "slow_c": expected["slow_c"]},
               f"step-30b: recomputed pre-warmup median {r_op} != recorded R_op {expected}", failures)
    results = []
    for m in members:
        cap = G0_CAP_DEFAULT_S if m["role"] == "release_check" else G0_CAP_R1_S
        out, f = replay_member(m, journals[m["label"]], r_op, cap, use_status=use_status)
        results.append(out)
        failures += f
    consume = {}
    if consume_labels and not failures:
        by_label = {o["label"]: o for o in results}
        for label in consume_labels:
            source = by_label.get(label)
            if source is None or source["role"] != "gated" or not source.get("own", {}).get("captured"):
                raise Refused(f"consume source {label!r} must be an observed gated D member")
            consume[label] = {k: source["own"][k] for k in ("fast_c", "slow_c")}
        for m, o in zip(members, results):
            o["followup"] = followup_cases(m, journals[m["label"]], o.get("own"), consume,
                                           use_status=use_status)
    return {"r_op": r_op, "r_op_capture": captured, "results": results, "failures": failures,
            "journals": {k: v["sha256"] for k, v in journals.items()}, "use_status": use_status,
            "consume_references": consume}


def _f(value, fmt="{:+.3f}"):
    return "n/a" if value is None else fmt.format(value)


def render(report, *, verdicts=True):
    lines = []
    r = report["r_op"]
    lines.append(f"R_op (step-30b pre-warmup 60 s median, recomputed): fast {r['fast_c']:.3f} C, "
                 f"slow {r['slow_c']:.3f} C; band d_fast {DELTA_FAST_C} C, d_slow {DELTA_SLOW_C} C; "
                 f"cap {G0_CAP_R1_S} s; status conditions {'applied' if report['use_status'] else 'IGNORED'}")
    lines.append("")
    lines.append("Self-check: the rule replayed against the reference each gate actually used")
    lines.append("| member | recorded ref slow C | recorded | replay | recorded wait s | replay wait s |")
    lines.append("|---|---|---|---|---|---|")
    for o in report["results"]:
        g, c = o["recorded"], o["check"]
        lines.append(f"| {o['label']} | {g['reference']['slow_c']:.3f} | {g['outcome']} | {c['outcome']} | "
                     f"{g['duration_s']:.2f} | {c['wait_s']:.2f} |")
    lines.append("")
    if report["failures"]:
        lines.append("SELF-CHECK FAILED: the replay does not reproduce the recorded gates, so it is wrong.")
        lines += [f"- {x}" for x in report["failures"]]
        lines.append("No own-reference verdict is printed.")
        return "\n".join(lines)
    lines.append("SELF-CHECK PASSED: every recorded G0 outcome is reproduced "
                 f"(released waits within {RELEASE_TIME_TOLERANCE_S} s), and the recomputed step-30b "
                 "pre-warmup median equals R_op exactly.")
    if not verdicts:
        return "\n".join(lines)
    lines.append("")
    lines.append("Own pre-warmup reference (planning: own slow median + designed offset; fast ceiling 150 C)")
    lines.append("| member | own-R_op fast C | own-R_op slow C | at cap: slow - R_op edge C | at cap: slow - own edge C "
                 "| at cap: slope C/min | own-ref G0 | own-ref release s |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for o in report["results"]:
        if "own" not in o:
            continue
        g, c = o["recorded"], o["check"]
        if not o["own"]["captured"]:
            lines.append(f"| {o['label']} | unobserved | unobserved | | | | not captured | |")
            continue
        d = o["own_minus_rop"]
        at_cap = g["outcome"] != "released"
        rop_edge = _f(c["slow_c"] - o["edge_rop_slow_c"]) if at_cap else "released"
        own_edge = _f(c["slow_c"] - o["edge_own_slow_c"]) if at_cap else "released"
        slope = _f(c["slope_c_per_min"]) if at_cap else "released"
        own = o["own_replay"]
        when = f"{own['wait_s']:.2f}" if own["outcome"] == "released" else "-"
        lines.append(f"| {o['label']} | {d['fast_c']:+.3f} | {d['slow_c']:+.3f} | {rop_edge} | {own_edge} | "
                     f"{slope} | {own['outcome']} | {when} |")
    if report.get("consume_references"):
        lines += ["", "RL-64 follow-up: bounded by each recorded G0 end; planning is OLD heater trace only.",
                  "Positive margin = band edge minus release temperature; right_censored is not a timeout.",
                  "| member | reference | slow band C | outcome | wait/observed s | fast margin C | slow margin C |",
                  "|---|---|---|---|---|---|---|"]
        for o in report["results"]:
            for c in o["followup"]:
                lines.append(f"| {o['label']} | {c['reference_label']} | {c['delta_slow_c']:.1f} | "
                             f"{c['outcome']} | {c['wait_s']:.2f} | {_f(c['fast_margin_c'])} | "
                             f"{_f(c['slow_margin_c'])} |")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--root", required=True, help="directory holding the copied journals")
    parser.add_argument("--ignore-status", action="store_true",
                        help="diagnostic: treat os_level/pm_state conditions as met")
    parser.add_argument("--field", action="append", default=[],
                        help="extra temperature key to carry (refused unless an SMC T key)")
    parser.add_argument("--json", help="write the structured result here")
    parser.add_argument("--consume-label", action="append", default=[],
                        help="RL-64: replay both bands against this D member's captured median (repeatable)")
    args = parser.parse_args(argv)
    try:
        report = run(args.manifest, args.root, use_status=not args.ignore_status,
                     extra_fields=tuple(args.field), consume_labels=tuple(args.consume_label))
    except Refused as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 3
    print(render(report))
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    return 2 if report["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
