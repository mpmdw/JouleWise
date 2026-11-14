"""Campaign runner library for runner kind ``cadence-legs-v1`` (RL-149 section 2; section 5 item 6).

Pure code: no host command, no SSH, no energy. The span driver
(``scripts/cadence_legs_runner.py``) and the leg runtime
(``joulewise/align/apple/cadence_leg.py``) use it for:

* **leg specs**: a kit leg plus its band recipe becomes the one JSON document a
  leg runtime reads (prompt size, decode cap, seed, quiet);
* **the plan adapter** (``plan_span``): sizes one span's deadline from the kit's
  span template and the span's roster (the queue span's leg ids), including the
  wait a batch blackout can add;
* **batch admission**: no soak overlaps a blackout and no leg starts inside one
  (RL-149 section 2.9 item 4). The blackout is a parameter, so the W1-line PR's
  move of the R1 driver constant flows through without being duplicated here;
* **stage stamps**: ``chain-stages.jsonl`` lines in the shape the RL-128 probe
  projects (``stage_id, kind, rc, started_epoch_s, ended_epoch_s``);
* **the leg-summary projection** (``leg-summary-v1``): exactly the desk adapter's
  allowlist (``joulewise.cadence.desk.LEG_SUMMARY_KEYS``), refused if any key or
  value would carry energy, power, a slot, a transcript or a condition label;
* **the meter-health projection**: the KM003C stream's header and trailer lines
  only (status and counters); a sample line is never parsed.

Bands are history recipes, never temperature targets (RL-149 section 2.2: "No
designed start state is waited for"). ``qN`` means N seconds of idle after the
leg's own G0 release and before its prefill; ``q0`` is the warm start "directly
after a heavy leg's G0". The first leg of a span follows the span's fresh soak
(at least 30 min idle), which is the block's cold start.
"""
from __future__ import annotations

from datetime import datetime, timedelta, time as wall_time
import json
import math
import os
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from joulewise.cadence import kit as kitmod
from joulewise.cadence.desk import DENIED_KEY_RE, LEG_SUMMARY_KEYS, METER_KEYS, RESULT_KEYS

RUNNER_KIND = "cadence-legs-v1"
LEG_KIND = "cadence-leg"
LEG_SPEC_SCHEMA = "joulewise.cadence_leg_spec.v1"
PLAN_SCHEMA = "joulewise.cadence_span_plan.v1"
STAGE_JOURNAL = "chain-stages.jsonl"
LOCAL_ZONE = ZoneInfo(kitmod.LOCAL_ZONE_NAME)

# The step leg's prompt is ``StepTask`` text sized in characters. The anchor is the
# series' step shape: 40,000 characters gave 19,458 prefill tokens (r1_runtime.json
# ``step.prefill_chars``; Mythos block-design memo section 1). Other sizes scale by
# the same ratio; the realized count is read back from the bundle, never assumed.
ANCHOR_PREFILL_CHARS = 40000
ANCHOR_PREFILL_TOKENS = 19458
PREFILL_TOKENS_RANGE = (256, 32768)
DECODE_TOKENS_RANGE = (1, 4096)

# History recipes (see the module docstring). The kit's seed_law.bands must name these.
BAND_RECIPES = {"q0": {"quiet_s": 0}, "q300": {"quiet_s": 300}, "q600": {"quiet_s": 600}}

# Leg time model (Mythos memo section 3; it gives 1,155 s for the 11-13 leg at its
# 114 s G0 against 1,158 s measured). G0 is Part C's step-D G0 on TV1h, 209 s
# (partc-desk/DESK-TABLE.md). A leg's budget is this model's seconds, rounded up.
TIME_MODEL = {"fixed_s": 500.0, "warmup_extra_s": 6.0, "prefill_s_per_token": 0.005,
              "decode_tokens_per_s": 12.03, "g0_s": 209.0}

# The launcher's ceiling (launch_align_r0.MAX_DESK_SECONDS); a plan longer than this cannot be armed.
MAX_SPAN_S = 12 * 3600

LEG_SPEC_KEYS = {"schema", "campaign_id", "leg_id", "seed", "start_band", "prefill_tokens", "prefill_chars",
                 "decode_tokens", "quiet_s"}


class PlanError(ValueError):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


class LeakRefusal(RuntimeError):
    """A projection would carry energy, power, a slot, a transcript or a condition label."""


# --------------------------------------------------------------------------
# Leg specs
# --------------------------------------------------------------------------
def prefill_chars(tokens):
    """Step-task characters for a prefill of about ``tokens`` tokens (the anchor maps exactly)."""
    return round(tokens * ANCHOR_PREFILL_CHARS / ANCHOR_PREFILL_TOKENS)


def validate_leg_spec(spec):
    """Return ``spec`` or raise PlanError. Closed keys; a leg runtime reads nothing else."""
    problems = []
    if not isinstance(spec, dict):
        raise PlanError(["leg spec: object"])
    for k in sorted(set(spec) ^ LEG_SPEC_KEYS):
        problems.append(f"leg spec: {'unknown' if k in spec else 'missing'} key {k!r}")
    if spec.get("schema") != LEG_SPEC_SCHEMA:
        problems.append(f"leg spec: schema must be {LEG_SPEC_SCHEMA}")
    if not (isinstance(spec.get("leg_id"), str) and kitmod.LEG_ID_RE.fullmatch(spec["leg_id"])):
        problems.append("leg spec: leg_id L<digits>")
    if not (isinstance(spec.get("campaign_id"), str) and kitmod.CAMPAIGN_ID_RE.fullmatch(spec["campaign_id"])):
        problems.append("leg spec: campaign_id")
    if not _int(spec.get("seed"), 0, 2 ** 32 - 1):
        problems.append("leg spec: seed 0..2^32-1")
    if spec.get("start_band") not in BAND_RECIPES:
        problems.append(f"leg spec: start_band one of {sorted(BAND_RECIPES)}")
    elif spec.get("quiet_s") != BAND_RECIPES[spec["start_band"]]["quiet_s"]:
        problems.append("leg spec: quiet_s is not the band recipe's")
    if not _int(spec.get("prefill_tokens"), *PREFILL_TOKENS_RANGE):
        problems.append(f"leg spec: prefill_tokens {PREFILL_TOKENS_RANGE}")
    elif spec.get("prefill_chars") != prefill_chars(spec["prefill_tokens"]):
        problems.append("leg spec: prefill_chars is not the anchor ratio's")
    if not _int(spec.get("decode_tokens"), *DECODE_TOKENS_RANGE):
        problems.append(f"leg spec: decode_tokens {DECODE_TOKENS_RANGE}")
    hits = kitmod.deny_scan(spec)
    if hits:
        problems.extend(hits)
    if problems:
        raise PlanError(problems)
    return spec


def _int(v, lo, hi):
    return type(v) is int and lo <= v <= hi


def leg_specs(kit, leg_ids=None):
    """The span's legs as runtime specs, in the kit's seeded order.

    ``leg_ids`` is the queue span's roster: distinct kit leg ids, in the kit's order.
    ``None`` means every kit leg."""
    by_id = {leg["leg_id"]: leg for leg in kit["legs"]}
    order = [leg["leg_id"] for leg in kit["legs"]]
    ids = list(order) if leg_ids is None else list(leg_ids)
    problems = []
    if not ids:
        problems.append("roster: no legs")
    if len(set(ids)) != len(ids):
        problems.append("roster: a leg is listed twice")
    unknown = [i for i in ids if i not in by_id]
    if unknown:
        problems.append(f"roster: not kit legs {unknown}")
    elif [i for i in order if i in set(ids)] != ids:
        problems.append("roster: legs are not in the kit's seeded order")
    if problems:
        raise PlanError(problems)
    specs = []
    for leg_id in ids:
        leg = by_id[leg_id]
        band = leg["start_band"]
        if band not in BAND_RECIPES:
            raise PlanError([f"{leg_id}: band {band!r} has no recipe in {sorted(BAND_RECIPES)}"])
        tokens = leg.get("prefill_tokens", kit["leg_defaults"]["prefill_tokens"])
        spec = {"schema": LEG_SPEC_SCHEMA, "campaign_id": kit["campaign_id"], "leg_id": leg_id,
                "seed": leg["seed"], "start_band": band, "prefill_tokens": tokens,
                "prefill_chars": prefill_chars(tokens) if type(tokens) is int else None,
                "decode_tokens": leg.get("decode_tokens", kit["leg_defaults"]["decode_tokens"]),
                "quiet_s": BAND_RECIPES[band]["quiet_s"]}
        specs.append(validate_leg_spec(spec))
    return specs


def leg_expected_s(spec, model=TIME_MODEL):
    """Modeled wall seconds of one leg: fixed + warm-up (one prefill) + G0 + quiet + prefill + decode."""
    prefill = spec["prefill_tokens"] * model["prefill_s_per_token"]
    return (model["fixed_s"] + prefill + model["warmup_extra_s"] + model["g0_s"] + spec["quiet_s"]
            + prefill + spec["decode_tokens"] / model["decode_tokens_per_s"])


# --------------------------------------------------------------------------
# Batch blackout
# --------------------------------------------------------------------------
HHMM_RANGE_RE = re.compile(r"([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)")


def parse_window(text):
    """``"HH:MM-HH:MM"`` local -> ((h0, m0), (h1, m1)). The window may not wrap midnight."""
    m = HHMM_RANGE_RE.fullmatch(text or "")
    if m is None:
        raise ValueError(f"batch window {text!r}: HH:MM-HH:MM")
    w = ((int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4))))
    if w[1] <= w[0]:
        raise ValueError(f"batch window {text!r}: end must follow start on the same day")
    return w


def format_window(window):
    (h0, m0), (h1, m1) = window
    return f"{h0:02d}:{m0:02d}-{h1:02d}:{m1:02d}"


def window_epochs(epoch, windows, zone=LOCAL_ZONE):
    """Every (start, end) epoch pair of ``windows`` on the local days around ``epoch``, sorted.

    Boundaries are built from the local calendar date, so they keep their wall
    times across a DST change (as ``align_r1_rehearsal._batch_windows`` does)."""
    day = datetime.fromtimestamp(epoch, zone).date()
    out = []
    for offset in (-1, 0, 1, 2):
        date = day + timedelta(days=offset)
        for (h0, m0), (h1, m1) in windows:
            out.append((datetime.combine(date, wall_time(h0, m0), tzinfo=zone).timestamp(),
                        datetime.combine(date, wall_time(h1, m1), tzinfo=zone).timestamp()))
    return sorted(out)


def leg_start_delay(epoch, windows):
    """Seconds to wait so that a leg does not start inside a blackout (0 when outside)."""
    for start, end in window_epochs(epoch, windows):
        if start <= epoch < end:
            return end - epoch
    return 0.0


def interval_delay(epoch, duration_s, windows):
    """Seconds to wait so that [t, t + duration) meets no blackout (the soak's rule)."""
    t = epoch
    for _ in range(16):
        hit = next(((s, e) for s, e in window_epochs(t, windows) if t < e and t + duration_s > s), None)
        if hit is None:
            return t - epoch
        t = hit[1]
    raise ValueError("no blackout-free interval within 16 windows")


def blackout_bound_s(t0, span_s, windows):
    """Upper bound on blackout waits inside [t0, t0 + span_s): the full length of every window
    that starts in it (each can delay one leg start or the soak by at most its length)."""
    total = 0.0
    for start, end in window_epochs(t0, windows):
        if end <= t0:
            continue
        if start >= t0 + span_s + total:
            break
        total += end - max(start, t0)
    return total


# --------------------------------------------------------------------------
# The plan adapter
# --------------------------------------------------------------------------
def plan_span(kit, *, t0_epoch, windows, leg_ids=None, max_span_s=MAX_SPAN_S):
    """Size one span from the kit's span template and the span's roster.

    worst case = soak_s + fixed_overhead_s + (roster legs + redo_quota) x leg_worst_case_s. The
    deadline is t0 + that bound, and the plan refuses a t0 whose worst case meets a blackout. Each leg's budget is the
    time model's seconds (LEG_OVERTIME compares a leg's wall time to it); the kit's leg_budget_s must
    cover every leg's budget, and leg_worst_case_s is each leg's process cap."""
    t = kit["span_template"]
    specs = leg_specs(kit, leg_ids)
    problems = []
    if len(specs) > t["legs_per_span"]:
        problems.append(f"roster: {len(specs)} legs > legs_per_span {t['legs_per_span']}")
    legs = []
    for spec in specs:
        budget = math.ceil(leg_expected_s(spec))
        if budget > t["leg_budget_s"]:
            problems.append(f"{spec['leg_id']}: modeled {budget} s > kit leg_budget_s {t['leg_budget_s']}")
        legs.append({**spec, "budget_s": budget})
    if problems:
        raise PlanError(problems)
    worst = t["soak_s"] + t["fixed_overhead_s"] + (len(specs) + t["redo_quota"]) * t["leg_worst_case_s"]
    if worst > max_span_s:
        raise PlanError([f"worst case {worst:.0f} s exceeds the {max_span_s:.0f} s launch ceiling"])
    # RL-149 section 2.9 item 6.3: a span arms at any hour "if the block's worst-case bound clears the
    # blackout". The driver's start rule (no soak overlaps it, no leg starts in it) stays as the net.
    blackout = blackout_bound_s(t0_epoch, worst, windows)
    if blackout > 0:
        raise PlanError([f"the worst-case span [t0, t0 + {worst:.0f} s] meets a batch blackout "
                         f"({', '.join(format_window(w) for w in windows)}); arm after it or earlier"])
    expected = t["soak_s"] + t["fixed_overhead_s"] + sum(leg["budget_s"] for leg in legs)
    return {"schema": PLAN_SCHEMA, "runner_kind": RUNNER_KIND, "campaign_id": kit["campaign_id"],
            "t0_epoch_s": t0_epoch, "deadline_epoch_s": t0_epoch + worst, "worst_case_s": worst,
            "blackout_clear": True, "expected_s": expected, "soak_s": t["soak_s"],
            "fixed_overhead_s": t["fixed_overhead_s"], "leg_cap_s": t["leg_worst_case_s"],
            "redo_quota": t["redo_quota"], "batch_windows": [format_window(w) for w in windows],
            "time_model": dict(TIME_MODEL), "legs": legs}


# --------------------------------------------------------------------------
# Stage stamps
# --------------------------------------------------------------------------
class StageJournal:
    """``chain-stages.jsonl``: one line when a stage starts (rc null) and one when it ends.

    The RL-128 probe projects each line to stage_id, kind, rc, started_epoch_s,
    ended_epoch_s, so a running stage is visible as a fresh start stamp."""

    def __init__(self, path, clock):
        self.path = Path(path)
        self.clock = clock

    def _append(self, row):
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def start(self, stage_id, kind, cap_s=None):
        started = self.clock.time()
        self._append({"stage_id": stage_id, "kind": kind, "event": "start", "rc": None,
                      "started_epoch_s": started, "ended_epoch_s": None, "cap_s": cap_s})
        return started

    def end(self, stage_id, kind, rc, started, cap_s=None):
        self._append({"stage_id": stage_id, "kind": kind, "event": "end", "rc": rc,
                      "started_epoch_s": started, "ended_epoch_s": self.clock.time(), "cap_s": cap_s})


# --------------------------------------------------------------------------
# Projections (no energy, no condition, no slot, no transcript)
# --------------------------------------------------------------------------
def _walk(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield f"{path}.{k}", str(k), None
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, None, node


def guard_projection(doc, where, *, values=True):
    """Refuse a document with a denied key at any depth (the desk's rule: energy, power, slot,
    transcript) or, with ``values``, a string carrying a condition label or slot (the kit's rule)."""
    for path, key, value in _walk(doc):
        if key is not None and DENIED_KEY_RE.search(key):
            raise LeakRefusal(f"{where}: {path} is a denied key (energy, power, slot or transcript)")
        if values and value is not None and kitmod.DENY_VALUE_RE.search(value):
            raise LeakRefusal(f"{where}: {path} carries a condition label or slot")
    return doc


def leg_admitted(result, *, contaminated):
    """RL-149 section 2.4 rules 1, 2, 5 and 6 as the runner sees them. Rules 3 and 4 (sidecar
    and powermetrics coverage, a clean KM003C stream) are judged on custody at the look."""
    mode = (result or {}).get("ac_powermode")
    mode = mode.get("value") if isinstance(mode, dict) else mode
    return bool(result is not None and not contaminated and result.get("leg_status") == "complete"
                and result.get("g0_released") is True and result.get("decode_cap_reached") is True
                and mode == 0)


def leg_summary(*, spec, budget_s, attempts, accepted, started_epoch_s, ended_epoch_s):
    """The ``leg-summary-v1`` projection of one leg (the desk's allowlist, nothing else).

    ``attempts`` are this leg's attempt records in order ({wall_s, contaminated, redo_reason}); an
    attempt is contaminated when the load-redo rule fired on it, whether or not quota remained to
    redo it. ``accepted`` is the last attempt's runtime result (None when none returned one)."""
    rejected = [a for a in attempts if a.get("contaminated")]
    last = attempts[-1] if attempts else {}
    contaminated = bool(last.get("contaminated"))
    result = accepted or {}
    summary = {
        "leg_id": spec["leg_id"], "seed": spec["seed"], "start_band": spec["start_band"],
        "band_reached": result.get("g0_released") is True,
        "g0_s": result.get("g0_wait_s"), "g0_outcome": result.get("g0_outcome"),
        "wall_s": last.get("wall_s"), "budget_s": budget_s, "attempts": len(attempts),
        "contaminated_redos": len(rejected), "redo_reasons": [a["redo_reason"] for a in rejected],
        "os_level_max": result.get("os_level_max"), "pm_nominal": result.get("pm_nominal"),
        "started_epoch_s": started_epoch_s, "ended_epoch_s": ended_epoch_s,
        "admitted": leg_admitted(accepted, contaminated=contaminated),
    }
    assert set(summary) <= LEG_SUMMARY_KEYS
    return guard_projection(summary, f"legs/{spec['leg_id']}/leg_summary.json")


def meter_health(stream_paths, *, started, stop_record):
    """KM003C health from each stream's first (header) and last (trailer) line only.

    The monitor writes ``{"k": "h", "status": ...}`` first and ``{"k": "t", polls, bad,
    usb_errors, elapsed_s, ...}`` last (scripts/km003c_monitor.py). Sample lines are
    never parsed: the tail is read by seeking, and only the last line is decoded."""
    out = {"present": False, "proven_stopped": bool(stop_record and stop_record.get("proven_stopped")),
           "bad_polls": None, "usb_errors": None, "elapsed_s": None, "polls": None}
    paths = [Path(p) for p in stream_paths if Path(p).is_file()]
    if not started or not paths:
        return out
    totals = {"bad_polls": 0, "usb_errors": 0, "polls": 0, "elapsed_s": 0.0}
    for path in paths:
        with path.open("rb") as handle:
            head = handle.readline(65536)
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - 65536))
            tail_lines = handle.read().splitlines()
        try:
            header = json.loads(head)
            trailer = json.loads(tail_lines[-1]) if tail_lines else {}
        except ValueError:
            return out
        if header.get("k") != "h" or header.get("status") != "streaming" or trailer.get("k") != "t":
            return out
        for key, source in (("bad_polls", "bad"), ("usb_errors", "usb_errors"), ("polls", "polls")):
            if type(trailer.get(source)) is not int:
                return out
            totals[key] += trailer[source]
        if not isinstance(trailer.get("elapsed_s"), (int, float)):
            return out
        totals["elapsed_s"] += float(trailer["elapsed_s"])
    out.update(present=True, **totals)
    assert set(out) <= METER_KEYS
    return guard_projection(out, "span/meter.json")


def span_result(*, rc, planned, finished, fault):
    """``span/result.json`` (desk RESULT_KEYS). A complete roster with rc 0 is MEASURED_OK; a
    roster with an excluded leg is still COMPLETE (the desk and the reserve handle exclusion)."""
    complete = rc == 0 and finished == planned
    doc = {"chain_exit_code": rc, "chain_outcome": "COMPLETE" if complete else "INCOMPLETE",
           "fault": bool(fault), "outcome": "MEASURED_OK" if complete and not fault else "REFUSED",
           "verdict": f"{finished}/{planned} legs run"}
    assert set(doc) <= RESULT_KEYS
    return doc


def write_desk_bundle(root, *, summaries, result, meter):
    """The per-span ``leg-summary-v1`` bundle (RL-149 section 2.9 item 5 row 3): exactly the files
    the desk adapter opens. Create-once."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    for summary in summaries:
        leg_dir = root / "legs" / summary["leg_id"]
        leg_dir.mkdir(parents=True)
        (leg_dir / "leg_summary.json").write_text(json.dumps(guard_projection(summary, summary["leg_id"]),
                                                             indent=1, sort_keys=True) + "\n")
    (root / "span").mkdir()
    (root / "span" / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    (root / "span" / "meter.json").write_text(json.dumps(guard_projection(meter, "meter"), indent=1,
                                                         sort_keys=True) + "\n")
    return root
