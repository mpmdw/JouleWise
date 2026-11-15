"""Campaign kit schema v1.1: the cell law (RL-155 section 5.1; RL-150 R3) over v1's kit.

Schema ``joulewise.cadence_campaign_kit.v1.1``, runner kind ``cadence-legs-v1.1``. Design:
``docs/process/cadence_queue_design.md`` section 14. ``kit.load_kit`` dispatches here on ``schema``;
v1 kits never reach this module and v1's validator is unchanged.

What v1.1 adds to v1:

* **the cell law** ``sha256-cells-v1``: each leg's prompt size by permuted blocks over
  ``seed_law.prompt_tokens`` (each aligned block of k legs in kit order, L001-L003, L004-L006, ..., holds
  each size once), and its G0 shape
  (``g0_shape``) from ``seed_law.g0_shapes``: with ``span``, L001 is ``own`` and, per size, the first
  ceil(m/2) of that size's m warm legs in a drawn order are ``span``. Seeds and bands are v1's
  ``sha256-v1`` draws on the same campaign id and master seed. Size and shape use their own draw tags,
  so the v1.1 and v1.1a lists of one block differ in ``g0_shape`` only;
* **legs that carry their cell**: ``prefill_tokens``, ``decode_tokens`` and ``g0_shape`` on every leg;
  ``leg_defaults`` holds ``decode_tokens`` only;
* **the free t0** (RL-149 section 2.9 item 6.3): ``span_template.t0_rule = "free"`` replaces
  ``t0_local`` and ``end_by_local``. A span arms at any hour whose worst case clears the blackout; the
  plan enforces that per span, and the checklist's ``span_window`` line judges the arm's own
  ``[t0, end_by]`` against the batch window.

**The qualification law** ``sha256-qual-v1`` (RL-165 section 8.1; RL-150 section 3.2) is a second law
of the same schema. The kit names its spans: ``seed_law.spans`` spans of equal length, each holding the
type-A sizes ``seed_law.span_a_tokens`` at the kit's decode cap and one type-L pair from
``seed_law.pairs`` (two legs at one prompt size, each with its own decode cap). Which span takes which
pair, the type-A order, where the pair sits and which of its legs runs first are sha256 draws. A
span's first leg is type A and not a pair member; the two legs of a pair are adjacent and in one span.
With ``g0_shapes`` ``own, span`` the first leg of each span is ``own`` (its capture is the span's
reference) and every other leg is ``span``; with ``own`` every leg is ``own`` (the own-shaped fallback).
Its legs add ``leg_type`` (``A`` or ``L``) and ``pair`` (``p<k>`` for ``seed_law.pairs[k-1]``, else
``null``); these are kit labels for the fit code and never reach a leg spec (``legs.leg_specs`` copies
named fields only). Seeds and bands are v1's ``sha256-v1`` draws, as for the cell law.

Everything else (closed keys, the condition/slot refusal, stop limits, the mandatory checklist,
frozen fit code for looks, the desk adapter) is v1's rule, applied by v1's own helpers.
"""
from __future__ import annotations

from datetime import datetime, timedelta, time as wall_time
import math
import re
from zoneinfo import ZoneInfo

from joulewise.cadence import kit as v1

SCHEMA = "joulewise.cadence_campaign_kit.v1.1"
RUNNER_KIND = "cadence-legs-v1.1"
LAW = "sha256-cells-v1"
# The qualification law (RL-165 section 8.1): named spans, type-A sizes per span, one type-L pair per span.
QUAL_LAW = "sha256-qual-v1"
LAWS = (LAW, QUAL_LAW)
# G0 shapes a v1.1 kit may draw from. "own": the leg's G0 is judged against its own capture (dev-01's
# shape; v1.1a). "span": against the span's reference, the capture of the span's first leg, consumed as
# a series member consumes its session's (RL-150 R1 part 2; design doc section 14.5; v1.1).
G0_SHAPE_SETS = (("own",), ("own", "span"))
# legs.PREFILL_TOKENS_RANGE (a test asserts they agree; legs imports kit, so it is not imported here).
PROMPT_TOKENS_RANGE = (256, 32768)
# legs.DECODE_TOKENS_RANGE (a test asserts they agree): a type-L leg's own cap must be a leg spec's.
DECODE_TOKENS_RANGE = (1, 4096)
# The launcher's ceiling (legs.MAX_SPAN_S = launch_align_r0.MAX_DESK_SECONDS).
MAX_SPAN_S = 12 * 3600

LEG_KEYS = {"leg_id", "seed", "start_band", "prefill_tokens", "decode_tokens", "g0_shape"}
LEG_DEFAULT_KEYS = {"decode_tokens"}
SEED_LAW_KEYS = {"method", "master_seed", "n_legs", "bands", "prompt_tokens", "g0_shapes"}
QUAL_SEED_LAW_KEYS = {"method", "master_seed", "n_legs", "bands", "spans", "span_a_tokens", "pairs", "g0_shapes"}
QUAL_LEG_KEYS = LEG_KEYS | {"leg_type", "pair"}
QUAL_PAIR_KEYS = {"prefill_tokens", "decode_tokens"}
TEMPLATE_KEYS = {"timezone", "t0_rule", "legs_per_span", "soak_s", "fixed_overhead_s", "leg_budget_s",
                 "leg_worst_case_s", "redo_quota"}
T0_RULES = ("free",)


def _permute(items, campaign_id, master, tag):
    out = list(items)
    for i in range(len(out) - 1, 0, -1):   # Fisher-Yates on sha256 draws
        j = v1._draw(campaign_id, master, tag, i) % (i + 1)
        out[i], out[j] = out[j], out[i]
    return out


def generate_legs(campaign_id, seed_law, leg_defaults):
    """The seeded leg list of ``sha256-cells-v1`` (design doc section 14.2) or ``sha256-qual-v1``."""
    if seed_law.get("method") == QUAL_LAW:
        return _generate_qual(campaign_id, seed_law, leg_defaults)
    if seed_law.get("method") != LAW:
        raise v1.KitError([f"seed_law.method: one of {list(LAWS)} for {SCHEMA}"])
    n, master = seed_law["n_legs"], seed_law["master_seed"]
    sizes, shapes = list(seed_law["prompt_tokens"]), tuple(seed_law["g0_shapes"])
    k = len(sizes)
    if not k or n % k:
        raise v1.KitError([f"seed_law.n_legs: {n} is not a multiple of the {k} prompt sizes"])
    if shapes not in G0_SHAPE_SETS:
        raise v1.KitError([f"seed_law.g0_shapes: one of {[list(s) for s in G0_SHAPE_SETS]}"])
    base = v1.generate_legs(campaign_id, {"method": "sha256-v1", "master_seed": master, "n_legs": n,
                                          "bands": list(seed_law["bands"])})
    order = []
    for block in range(n // k):
        order.extend(_permute(sizes, campaign_id, master, f"size{block}"))
    g0 = ["own"] * n
    if "span" in shapes:
        for size in sizes:
            warm = _permute([i for i in range(1, n) if order[i] == size], campaign_id, master, f"shape-{size}")
            for i in warm[:math.ceil(len(warm) / 2)]:
                g0[i] = "span"
    return [{**leg, "prefill_tokens": order[i], "decode_tokens": leg_defaults["decode_tokens"], "g0_shape": g0[i]}
            for i, leg in enumerate(base)]


def _generate_qual(campaign_id, seed_law, leg_defaults):
    """The seeded leg list of ``sha256-qual-v1`` (RL-165 section 8.1; module docstring)."""
    n, master, spans = seed_law["n_legs"], seed_law["master_seed"], seed_law["spans"]
    a_tokens, pairs, shapes = list(seed_law["span_a_tokens"]), list(seed_law["pairs"]), tuple(seed_law["g0_shapes"])
    per = len(a_tokens) + 2
    if not (type(spans) is int and spans >= 1 and a_tokens and len(pairs) == spans and n == spans * per):
        raise v1.KitError([f"seed_law: n_legs must be spans x (len(span_a_tokens) + 2) with one pair per span "
                           f"({n} legs, {spans} spans, {len(a_tokens)} type-A sizes, {len(pairs)} pairs)"])
    if shapes not in G0_SHAPE_SETS:
        raise v1.KitError([f"seed_law.g0_shapes: one of {[list(s) for s in G0_SHAPE_SETS]}"])
    base = v1.generate_legs(campaign_id, {"method": "sha256-v1", "master_seed": master, "n_legs": n,
                                          "bands": list(seed_law["bands"])})
    cap = leg_defaults["decode_tokens"]
    pair_of_span = _permute(range(spans), campaign_id, master, "qual-pairs")
    cells = []   # (leg_type, prefill_tokens, decode_tokens, pair)
    for s in range(spans):
        order = _permute(a_tokens, campaign_id, master, f"qual-a{s}")
        rest = [("A", t, cap, None) for t in order[1:]]
        at = v1._draw(campaign_id, master, f"qual-pair-at{s}", 0) % (len(rest) + 1)
        k = pair_of_span[s]
        caps = list(pairs[k]["decode_tokens"])
        if v1._draw(campaign_id, master, f"qual-pair-first{s}", 0) % 2:
            caps.reverse()
        pair = [("L", pairs[k]["prefill_tokens"], c, f"p{k + 1}") for c in caps]
        cells.extend([("A", order[0], cap, None), *rest[:at], *pair, *rest[at:]])
    legs = []
    for i, (leg, (kind, tokens, decode, pair)) in enumerate(zip(base, cells)):
        first = i % per == 0
        shape = "span" if "span" in shapes and not first else "own"
        legs.append({**leg, "prefill_tokens": tokens, "decode_tokens": decode, "g0_shape": shape,
                     "leg_type": kind, "pair": pair})
    return legs


def _window_s(window):
    (h0, m0), (h1, m1) = window
    return ((h1 * 60 + m1) - (h0 * 60 + m0)) * 60


def worst_case_s(template):
    """soak + overhead + (legs_per_span + redo_quota) x leg_worst_case_s: a full span's bound."""
    return (template["soak_s"] + template["fixed_overhead_s"]
            + (template["legs_per_span"] + template["redo_quota"]) * template["leg_worst_case_s"])


def _check_template(t, problems, batch_window):
    if not v1._closed(t, TEMPLATE_KEYS, "span_template", problems):
        return
    if t.get("timezone") != v1.LOCAL_ZONE_NAME:
        problems.append(f"span_template.timezone: must be {v1.LOCAL_ZONE_NAME}")
    if t.get("t0_rule") not in T0_RULES:
        problems.append(f"span_template.t0_rule: one of {T0_RULES} (the plan places t0 outside the blackout)")
    zero_ok = ("redo_quota", "soak_s", "fixed_overhead_s")
    ints = {k: t.get(k) for k in sorted(TEMPLATE_KEYS - {"timezone", "t0_rule"})}
    for k, v in ints.items():
        if not v1._is_int(v, 0 if k in zero_ok else 1):
            problems.append(f"span_template.{k}: must be an integer >= {0 if k in zero_ok else 1}")
    if any(not v1._is_int(v) for v in ints.values()):
        return
    if ints["leg_worst_case_s"] < ints["leg_budget_s"]:
        problems.append("span_template.leg_worst_case_s: below leg_budget_s")
    need = worst_case_s(ints)
    if need > MAX_SPAN_S:
        problems.append(f"span_template: needs {need} s at the worst-case bound, over the {MAX_SPAN_S} s launch ceiling")
    if need + _window_s(batch_window) > 86400:
        problems.append(f"span_template: needs {need} s at the worst-case bound; no t0 in a day clears the "
                        "OS batch window")


def _check_law(law, problems):
    """The law's own fields. Returns the bands (for the leg check)."""
    if isinstance(law, dict) and law.get("method") == QUAL_LAW:
        return _check_qual_law(law, problems)
    if not v1._closed(law, SEED_LAW_KEYS, "seed_law", problems):
        return []
    bands = law.get("bands") if isinstance(law.get("bands"), list) else []
    if not (bands and all(isinstance(b, str) and re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,30}", b) for b in bands)
            and len(set(bands)) == len(bands)):
        problems.append("seed_law.bands: distinct short lowercase names")
    if law.get("method") != LAW:
        problems.append(f"seed_law.method: must be {LAW}")
    if not v1._is_int(law.get("n_legs"), 1, 9999):
        problems.append("seed_law.n_legs: integer 1..9999")
    if not v1._is_int(law.get("master_seed"), 0, 2 ** 63 - 1):
        problems.append("seed_law.master_seed: non-negative integer")
    sizes = law.get("prompt_tokens")
    if not (isinstance(sizes, list) and sizes and all(v1._is_int(s, *PROMPT_TOKENS_RANGE) for s in sizes)
            and len(set(sizes)) == len(sizes)):
        problems.append(f"seed_law.prompt_tokens: distinct integers in {PROMPT_TOKENS_RANGE}")
    elif v1._is_int(law.get("n_legs"), 1) and law["n_legs"] % len(sizes):
        problems.append(f"seed_law.n_legs: must be a multiple of the {len(sizes)} prompt sizes")
    shapes = law.get("g0_shapes")
    if not (isinstance(shapes, list) and tuple(shapes) in G0_SHAPE_SETS):
        problems.append(f"seed_law.g0_shapes: one of {[list(s) for s in G0_SHAPE_SETS]}")
    return bands


def _check_qual_law(law, problems):
    """``sha256-qual-v1``'s own fields (RL-165 section 8.1). Returns the bands."""
    if not v1._closed(law, QUAL_SEED_LAW_KEYS, "seed_law", problems):
        return []
    bands = law.get("bands") if isinstance(law.get("bands"), list) else []
    if not (bands and all(isinstance(b, str) and re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,30}", b) for b in bands)
            and len(set(bands)) == len(bands)):
        problems.append("seed_law.bands: distinct short lowercase names")
    if not v1._is_int(law.get("n_legs"), 1, 9999):
        problems.append("seed_law.n_legs: integer 1..9999")
    if not v1._is_int(law.get("master_seed"), 0, 2 ** 63 - 1):
        problems.append("seed_law.master_seed: non-negative integer")
    spans = law.get("spans")
    if not v1._is_int(spans, 1, 99):
        problems.append("seed_law.spans: integer 1..99")
    a_tokens = law.get("span_a_tokens")
    if not (isinstance(a_tokens, list) and a_tokens and all(v1._is_int(t, *PROMPT_TOKENS_RANGE) for t in a_tokens)):
        problems.append(f"seed_law.span_a_tokens: a non-empty list of integers in {PROMPT_TOKENS_RANGE}")
        a_tokens = None
    pairs = law.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        problems.append("seed_law.pairs: non-empty list")
        pairs = None
    else:
        for i, pair in enumerate(pairs):
            if not v1._closed(pair, QUAL_PAIR_KEYS, f"seed_law.pairs[{i}]", problems):
                continue
            if not v1._is_int(pair.get("prefill_tokens"), *PROMPT_TOKENS_RANGE):
                problems.append(f"seed_law.pairs[{i}].prefill_tokens: integer in {PROMPT_TOKENS_RANGE}")
            caps = pair.get("decode_tokens")
            if not (isinstance(caps, list) and len(caps) == 2 and all(v1._is_int(c, *DECODE_TOKENS_RANGE) for c in caps)
                    and caps[0] != caps[1]):
                problems.append(f"seed_law.pairs[{i}].decode_tokens: two distinct integers in {DECODE_TOKENS_RANGE}")
    if v1._is_int(spans, 1) and pairs is not None and len(pairs) != spans:
        problems.append(f"seed_law.pairs: one pair per span ({spans} spans, {len(pairs)} pairs)")
    if v1._is_int(spans, 1) and a_tokens and v1._is_int(law.get("n_legs"), 1) \
            and law["n_legs"] != spans * (len(a_tokens) + 2):
        problems.append(f"seed_law.n_legs: must be spans x (len(span_a_tokens) + 2) = {spans * (len(a_tokens) + 2)}")
    shapes = law.get("g0_shapes")
    if not (isinstance(shapes, list) and tuple(shapes) in G0_SHAPE_SETS):
        problems.append(f"seed_law.g0_shapes: one of {[list(s) for s in G0_SHAPE_SETS]}")
    return bands


def validate_kit(kit, *, batch_window=v1.OS_BATCH_WINDOW):
    """Return the v1.1 kit unchanged, or raise ``kit.KitError`` naming every problem."""
    problems = []
    if not v1._closed(kit, v1.TOP_KEYS, "kit", problems):
        raise v1.KitError(problems)
    problems.extend(v1.deny_scan(kit))
    if kit.get("schema") != SCHEMA:
        problems.append(f"schema: must be {SCHEMA}")
    cid = kit.get("campaign_id")
    if not (isinstance(cid, str) and v1.CAMPAIGN_ID_RE.fullmatch(cid)):
        problems.append("campaign_id: lowercase id, 3-41 chars")
    for key in ("title", "model"):
        if not (isinstance(kit.get(key), str) and kit[key].strip()):
            problems.append(f"{key}: non-empty text")

    ruling = kit.get("ruling")
    if v1._closed(ruling, {"id", "authorizes_spans"}, "ruling", problems):
        if not (isinstance(ruling.get("id"), str) and v1.RULING_RE.fullmatch(ruling["id"])):
            problems.append("ruling.id: RL-<n>")
        if ruling.get("authorizes_spans") is not True:
            problems.append("ruling.authorizes_spans: must be true (a kit without a standing ruling arms nothing)")

    frozen = kit.get("frozen")
    paths = {}
    if v1._closed(frozen, {"commit", "paths"}, "frozen", problems):
        if not (isinstance(frozen.get("commit"), str) and v1.HEX40.fullmatch(frozen["commit"])):
            problems.append("frozen.commit: full 40-hex sha")
        paths = frozen.get("paths") if isinstance(frozen.get("paths"), dict) else {}
        if not paths:
            problems.append("frozen.paths: at least one path")
        for p, h in paths.items():
            if not v1.PATH_RE.fullmatch(p):
                problems.append(f"frozen.paths: bad path {p!r}")
            if not (isinstance(h, str) and v1.HEX64.fullmatch(h)):
                problems.append(f"frozen.paths[{p}]: sha256 hex")

    runner = kit.get("runner")
    if v1._closed(runner, v1.RUNNER_KEYS, "runner", problems):
        if runner.get("kind") != RUNNER_KIND:
            problems.append(f"runner.kind: must be {RUNNER_KIND} for {SCHEMA}")
        if runner.get("entry") not in paths:
            problems.append("runner.entry: must be a frozen path")
        if runner.get("stage_journal") != "chain-stages.jsonl":
            problems.append("runner.stage_journal: must be chain-stages.jsonl (the RL-128 probe reads it)")

    defaults = kit.get("leg_defaults")
    law = kit.get("seed_law")
    qual = isinstance(law, dict) and law.get("method") == QUAL_LAW
    if v1._closed(defaults, LEG_DEFAULT_KEYS, "leg_defaults", problems):
        if not v1._is_int(defaults.get("decode_tokens"), *((DECODE_TOKENS_RANGE) if qual else (1,))):
            problems.append("leg_defaults.decode_tokens: positive integer"
                            + (f" in {DECODE_TOKENS_RANGE}" if qual else ""))

    bands = _check_law(law, problems)
    leg_keys = QUAL_LEG_KEYS if qual else LEG_KEYS

    legs = kit.get("legs")
    if not isinstance(legs, list) or not legs:
        problems.append("legs: non-empty list")
        legs = []
    for i, leg in enumerate(legs):
        if v1._closed(leg, leg_keys, f"legs[{i}]", problems):
            if not (isinstance(leg.get("leg_id"), str) and v1.LEG_ID_RE.fullmatch(leg["leg_id"])):
                problems.append(f"legs[{i}].leg_id: L<digits>")
            if leg.get("start_band") not in bands:
                problems.append(f"legs[{i}].start_band: not a seed_law band")
    if isinstance(law, dict) and isinstance(defaults, dict) and not any(
            p.startswith(("seed_law", "leg_defaults", "campaign_id")) for p in problems):
        try:
            expected = generate_legs(cid, law, defaults)
        except (v1.KitError, KeyError, TypeError) as error:
            problems.append(f"seed_law: cannot generate legs ({error})")
        else:
            if legs != expected:
                first = next((i for i, (a, b) in enumerate(zip(legs, expected)) if a != b),
                             min(len(legs), len(expected)))
                problems.append(f"legs: not the cell law's list (first difference at index {first}; "
                                f"{len(legs)} given, {len(expected)} generated)")

    rules = kit.get("inclusion_rules")
    if not isinstance(rules, list) or not rules:
        problems.append("inclusion_rules: non-empty list")
    else:
        ids = []
        for i, r in enumerate(rules):
            if v1._closed(r, {"id", "text"}, f"inclusion_rules[{i}]", problems):
                if not (isinstance(r.get("id"), str) and v1.CHECK_ID_RE.fullmatch(r["id"])):
                    problems.append(f"inclusion_rules[{i}].id: lowercase id")
                if not (isinstance(r.get("text"), str) and r["text"].strip()):
                    problems.append(f"inclusion_rules[{i}].text: the ruling's words")
                ids.append(r.get("id"))
        if len(set(map(str, ids))) != len(ids):
            problems.append("inclusion_rules: duplicate id")

    v1._check_stops(kit.get("stop_rules"), problems)
    _check_template(kit.get("span_template"), problems, batch_window)
    _check_checklist(kit.get("checklist"), problems)
    _check_looks(kit.get("looks"), paths, len(legs), problems)

    desk = kit.get("desk")
    if v1._closed(desk, {"adapter"}, "desk", problems) and desk.get("adapter") not in v1.DESK_ADAPTERS:
        problems.append(f"desk.adapter: one of {sorted(v1.DESK_ADAPTERS)}")

    if problems:
        raise v1.KitError(problems)
    return kit


def _check_checklist(checklist, problems):
    if not isinstance(checklist, list):
        problems.append("checklist: list")
        checklist = []
    seen, kinds = set(), []
    for i, line in enumerate(checklist):
        if v1._closed(line, {"id", "kind", "args"}, f"checklist[{i}]", problems, required={"id", "kind"}):
            if not (isinstance(line.get("id"), str) and v1.CHECK_ID_RE.fullmatch(line["id"])) or line["id"] in seen:
                problems.append(f"checklist[{i}].id: unique lowercase id")
            seen.add(line.get("id"))
            if line.get("kind") not in v1.CHECK_KINDS:
                problems.append(f"checklist[{i}].kind: unknown {line.get('kind')!r}")
            kinds.append(line.get("kind"))
            args = line.get("args", {})
            if line.get("kind") == "disk_free_gb":
                if not (isinstance(args, dict) and set(args) == {"min_gb"} and v1._is_int(args.get("min_gb"), 1)):
                    problems.append(f"checklist[{i}].args: {{'min_gb': int >= 1}}")
            elif args not in ({}, None):
                problems.append(f"checklist[{i}].args: {line.get('kind')} takes no args")
    for kind in sorted(set(v1.CHECK_KINDS) - set(kinds)):
        problems.append(f"checklist: mandatory check {kind!r} missing")
    for kind in sorted({k for k in kinds if kinds.count(k) > 1}):
        problems.append(f"checklist: {kind!r} listed twice")


def _check_looks(looks, paths, n_legs, problems):
    if not isinstance(looks, list):
        problems.append("looks: list (may be empty)")
        return
    last = 0
    for i, look in enumerate(looks):
        if v1._closed(look, {"look_id", "after_legs", "fit"}, f"looks[{i}]", problems):
            if not (isinstance(look.get("look_id"), str) and v1.CHECK_ID_RE.fullmatch(look["look_id"])):
                problems.append(f"looks[{i}].look_id: lowercase id")
            a = look.get("after_legs")
            if not v1._is_int(a, last + 1, n_legs or None):
                problems.append(f"looks[{i}].after_legs: strictly increasing, at most the leg count")
            else:
                last = a
            fit = look.get("fit")
            if not (isinstance(fit, dict) and set(fit) == {"path"} and fit.get("path") in paths):
                problems.append(f"looks[{i}].fit: {{'path': <a frozen path>}} (energy is read only by frozen fit code)")


# --------------------------------------------------------------------------
# The checklist's span_window line under the free t0
# --------------------------------------------------------------------------
def meets_window(t0_epoch, end_epoch, window, zone_name=v1.LOCAL_ZONE_NAME):
    """True when [t0, end) meets the local batch window on any day it spans (DST-safe wall times)."""
    zone = ZoneInfo(zone_name)
    (h0, m0), (h1, m1) = window
    day = datetime.fromtimestamp(t0_epoch, zone).date() - timedelta(days=1)
    last = datetime.fromtimestamp(end_epoch, zone).date() + timedelta(days=1)
    while day <= last:
        start = datetime.combine(day, wall_time(h0, m0), tzinfo=zone).timestamp()
        end = datetime.combine(day, wall_time(h1, m1), tzinfo=zone).timestamp()
        if t0_epoch < end and end_epoch > start:
            return True
        day += timedelta(days=1)
    return False


# RL-155a section 3 (legs.FENCE_QUIET_LEAD_S, legs.SOAK_LAUNCH_LEAD_S; a test asserts they agree).
FENCE_QUIET_LEAD_S = 600
SOAK_LAUNCH_LEAD_S = 3300


def _shift(window, seconds):
    (h0, m0), end = window
    minutes = h0 * 60 + m0 - seconds // 60
    return (minutes // 60, minutes % 60), end


def launch_in_soak_bound(t0_epoch, soak_window, zone_name=v1.LOCAL_ZONE_NAME):
    """True when t0 is inside RL-155a section 3's no-launch interval (10:50-13:15 for the 11:45 window)."""
    zone = ZoneInfo(zone_name)
    (h0, m0), (h1, m1) = soak_window
    for offset in (-1, 0, 1):
        day = datetime.fromtimestamp(t0_epoch, zone).date() + timedelta(days=offset)
        start = datetime.combine(day, wall_time(h0, m0), tzinfo=zone).timestamp() - SOAK_LAUNCH_LEAD_S
        end = datetime.combine(day, wall_time(h1, m1), tzinfo=zone).timestamp()
        if start < t0_epoch < end:
            return True
    return False


def evaluate_checklist(kit, obs, *, expected_kit_sha256, batch_window=v1.OS_BATCH_WINDOW,
                       soak_window=v1.OS_BATCH_WINDOW):
    """v1's ``evaluate_checklist``, with the free t0's ``span_window`` line: the arm's own
    ``[t0, end_by]`` is longer than 0 s, at most 24 h, ends at least ten minutes before any batch
    window starts (RL-155a section 3's 01:50), and t0 is not inside the soak path's no-launch interval
    (10:50-13:15 while the driver's soak window is 11:45-13:15). The launcher and ``plan`` apply the
    same bounds to the fence end (worst case + 1,460 s)."""
    template = kit["span_template"]
    others = [line for line in kit["checklist"] if line["kind"] != "span_window"]
    judged = iter(v1.evaluate_checklist({**kit, "checklist": others}, obs, expected_kit_sha256=expected_kit_sha256))
    rows = []
    for line in kit["checklist"]:
        if line["kind"] != "span_window":
            rows.append(next(judged))
            continue
        t0, end = obs.get("t0_epoch_s"), obs.get("end_by_epoch_s")
        numbers = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (t0, end))
        quiet = _shift(batch_window, FENCE_QUIET_LEAD_S)
        ok = (numbers and 0 < end - t0 <= 86400 and not meets_window(t0, end, quiet, template["timezone"])
              and not launch_in_soak_bound(t0, soak_window, template["timezone"]))
        (h0, m0), (h1, m1) = quiet
        rows.append({"id": line["id"], "kind": "span_window", "ok": bool(ok),
                     "detail": (f"free t0; [t0, end_by] clears {h0:02d}:{m0:02d}-{h1:02d}:{m1:02d}; t0 outside the soak "
                                "bound" if ok else "t0/end-by not observed, not ordered within 24 h, meeting the quiet "
                                "before the batch window, or t0 inside the soak path's no-launch interval")})
    return rows
