"""Campaign kit: the frozen, conditionless leg program one standing ruling authorizes.

A kit is one JSON file (schema ``joulewise.cadence_campaign_kit.v1``). It names
the frozen commit and the sha256 of every executed path, a seeded leg list that
the validator regenerates, the inclusion and stop rules, the span template (one
span per day, outside the OS batch window), the pre-fixed looks at which frozen
fit code may read energy, and the machine-checked per-span checklist.

``validate_kit`` refuses, with every problem listed:

* an unknown or missing key at any level (closed schema everywhere);
* a condition label or a slot anywhere in the kit (``deny_scan``): keys whose
  tokens name a condition, slot, contrast, treatment or instruction, and string
  values carrying a registered condition or contrast label. Free-text keys
  (``title``, ``text``, ``notes``) are exempt from the value scan only;
* a leg list that is not exactly the one the seed law generates;
* stop rules looser than the approved named stops (3 contaminated redos,
  a band unreachable twice, a leg over 1.5x its time);
* a span template that overlaps the OS batch window or cannot hold its legs at
  their worst-case bound;
* a checklist missing a mandatory check;
* a look whose fit code is not a frozen path.

``verify_frozen`` re-hashes the frozen paths at the frozen commit in a git
repository. ``evaluate_checklist`` judges the magistrate's observations; a
missing observation fails its line, never passes it.
"""
from __future__ import annotations

from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

SCHEMA = "joulewise.cadence_campaign_kit.v1"
LOCAL_ZONE_NAME = "America/Los_Angeles"
# scripts/align_r1_rehearsal.py OS_BATCH_WINDOW_LOCAL (ruling 8): 11:45-13:15 local. RL-149 section 2.9
# item 4 moves the blackout to 02:00-02:35; the W1-line PR moves the driver constant. The validator takes
# the window as a parameter (``validate_kit(..., batch_window=...)``, ``validate-kit --batch-window``)
# so this default is not a second copy of that change.
OS_BATCH_WINDOW = ((11, 45), (13, 15))
# Approved named stops (Ed, 2026-11-13; throughput plan change 3). A kit may tighten, never loosen.
STOP_LIMITS = {"contaminated_redos_max": 3, "band_unreachable_max": 2, "leg_time_factor": 1.5}
STOP_SCOPES = ("span", "campaign")

CAMPAIGN_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,40}")
LEG_ID_RE = re.compile(r"L\d{3,4}")
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
# RL-149 section 2.8 line 1: "the kit's ruling is RL-149 §2" (an optional section suffix).
RULING_RE = re.compile(r"RL-\d{1,4}[a-z]?(?: §\d{1,2}(?:\.\d{1,2})?)?")
HHMM_RE = re.compile(r"([01]\d|2[0-3]):([0-5]\d)")
CHECK_ID_RE = re.compile(r"[a-z][a-z0-9_]{1,40}")
PATH_RE = re.compile(r"(?!/)(?!.*\.\./)[A-Za-z0-9_./-]{1,200}")

FREE_TEXT_KEYS = frozenset({"title", "text", "notes"})
# Key tokens (split on _ - . and space) that name a condition or a slot.
DENY_KEY_TOKENS = frozenset({
    "condition", "conditions", "slot", "slots", "sabotage", "benign", "treatment", "treatments",
    "instruction", "instructions", "contrast", "contrasts", "arm", "arms", "placebo", "control",
    "controls", "attack", "honest", "malicious",
})
DENY_KEY_SUBSTRINGS = ("known_h", "slot_detail", "condition_label")
# String values that carry a registered condition, task-condition or contrast label
# (configs/campaigns/align_v4/series/series_manifest.json vocabulary) or a slot file.
DENY_VALUE_RE = re.compile(
    r"(?i)(?:sabotage|benign|spam_filter_update|bank_transfer|known_h|treatment|placebo|"
    r"malicious|r1_slots|slot_detail|\bslots?\b|\bconditions?\b|\bcontrast\b|\binstructions?\b)"
    r"|^(?:X-G|Y-S|X-S|Y-G)$")

TOP_KEYS = {
    "schema", "campaign_id", "title", "ruling", "frozen", "runner", "model", "leg_defaults",
    "seed_law", "legs", "inclusion_rules", "stop_rules", "span_template", "checklist", "looks", "desk",
}
LEG_KEYS = {"leg_id", "seed", "start_band", "prefill_tokens", "decode_tokens"}
LEG_DEFAULT_KEYS = {"prefill_tokens", "decode_tokens"}
SEED_LAW_KEYS = {"method", "master_seed", "n_legs", "bands"}
STOP_KEYS = {"instrument_fault", "refusal", "contaminated_redos_max", "contaminated_redos_scope",
             "band_unreachable_max", "band_unreachable_scope", "leg_time_factor", "notes"}
TEMPLATE_KEYS = {"timezone", "t0_local", "end_by_local", "legs_per_span", "soak_s", "fixed_overhead_s",
                 "leg_budget_s", "leg_worst_case_s", "redo_quota"}
RUNNER_KEYS = {"kind", "entry", "stage_journal"}
RUNNER_KINDS = {"cadence-legs-v1"}
DESK_ADAPTERS = {"leg-summary-v1", "r1-journal-v1"}

# Mandatory per-span checks. Each reads named observations; see evaluate_checklist.
CHECK_KINDS = {
    "head_is_frozen_commit": "measurement checkout HEAD equals frozen.commit",
    "frozen_paths_hash": "every frozen path hashes as the kit says at the measurement checkout",
    "kit_sha256": "the kit file hashes as the queue entry pins it",
    "ac_power": "AC power",
    "powermode_zero": "pmset powermode 0",
    "network_time_off": "network time OFF",
    "freq_word_zero": "kernel frequency word 0",
    "no_stray_monitor": "no km003c_monitor, hazard_monitor or root powermetrics process",
    "no_other_agent": "no claude or codex process other than the magistrate",
    "no_night_agent_loaded": "no com.joulewise.night* or align-r0 label loaded",
    "no_high_power_marker": "no High Power marker",
    "sudo_kill": "sudo -n -l /bin/kill rc 0",
    "km003c_ready": "KM003C meter enumerated and readable",
    "disk_free_gb": "free disk at least args.min_gb",
    "previous_span_closed": "the previous span is closed with no named stop (or there is none)",
    "no_halt_or_veto": "no queue halt, cadence-stop issue or directive veto is open",
    "span_window": "t0 and end-by are the template's local times, outside the OS batch window",
}


class KitError(ValueError):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems) if self.problems else "invalid kit")


def _hhmm(text):
    m = HHMM_RE.fullmatch(text) if isinstance(text, str) else None
    return None if m is None else int(m.group(1)) * 60 + int(m.group(2))


def _is_int(v, lo=None, hi=None):
    return type(v) is int and (lo is None or v >= lo) and (hi is None or v <= hi)


def _closed(obj, allowed, where, problems, required=None):
    if not isinstance(obj, dict):
        problems.append(f"{where}: expected an object")
        return False
    for key in sorted(set(obj) - set(allowed)):
        problems.append(f"{where}: unknown key {key!r}")
    for key in sorted(set(required if required is not None else allowed) - set(obj)):
        problems.append(f"{where}: missing key {key!r}")
    return True


def deny_scan(node, path="$"):
    """Every condition label or slot in a kit, as ``path: reason`` strings."""
    hits = []
    if isinstance(node, dict):
        for key, value in node.items():
            k = str(key)
            tokens = set(re.split(r"[_\-.\s]+", k.lower()))
            if tokens & DENY_KEY_TOKENS or any(s in k.lower() for s in DENY_KEY_SUBSTRINGS):
                hits.append(f"{path}.{k}: key names a condition or slot")
            if k in FREE_TEXT_KEYS and isinstance(value, str):
                continue
            hits.extend(deny_scan(value, f"{path}.{k}"))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            hits.extend(deny_scan(value, f"{path}[{i}]"))
    elif isinstance(node, str) and DENY_VALUE_RE.search(node):
        hits.append(f"{path}: value carries a condition label or slot")
    return hits


def _draw(campaign_id, master_seed, tag, index):
    digest = hashlib.sha256(f"{campaign_id}|{master_seed}|{tag}|{index}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def generate_legs(campaign_id, seed_law, leg_defaults=None):
    """The seeded leg list. Seeds and the balanced band order come from sha256 draws
    (``sha256-v1``), so the list is the same on every host and Python version."""
    if seed_law.get("method") != "sha256-v1":
        raise KitError(["seed_law.method: only 'sha256-v1' is defined"])
    n, master, bands = seed_law["n_legs"], seed_law["master_seed"], list(seed_law["bands"])
    order = [bands[i % len(bands)] for i in range(n)]
    for i in range(n - 1, 0, -1):  # Fisher-Yates on sha256 draws
        j = _draw(campaign_id, master, "band", i) % (i + 1)
        order[i], order[j] = order[j], order[i]
    defaults = dict(leg_defaults or {})
    width = 3 if n < 1000 else 4
    return [{"leg_id": f"L{i + 1:0{width}d}", "seed": _draw(campaign_id, master, "seed", i) % (2 ** 32),
             "start_band": order[i], **defaults} for i in range(n)]


def _window_s(t0_min, end_min):
    return ((end_min - t0_min) % (24 * 60)) * 60


def _overlaps_batch(start_min, end_min, window=OS_BATCH_WINDOW):
    """True when the span [start, end) on a 24 h clock (end may be the next day) meets the window."""
    (h0, m0), (h1, m1) = window
    b0, b1 = h0 * 60 + m0, h1 * 60 + m1
    length = (end_min - start_min) % 1440 or 1440
    return any(start_min < b1 + d * 1440 and start_min + length > b0 + d * 1440 for d in (-1, 0, 1))


def _check_template(t, problems, batch_window=OS_BATCH_WINDOW):
    if not _closed(t, TEMPLATE_KEYS, "span_template", problems):
        return
    if t.get("timezone") != LOCAL_ZONE_NAME:
        problems.append(f"span_template.timezone: must be {LOCAL_ZONE_NAME}")
    t0, end = _hhmm(t.get("t0_local")), _hhmm(t.get("end_by_local"))
    if t0 is None or end is None:
        problems.append("span_template: t0_local and end_by_local must be HH:MM")
        return
    ints = {k: t.get(k) for k in ("legs_per_span", "soak_s", "fixed_overhead_s", "leg_budget_s",
                                   "leg_worst_case_s", "redo_quota")}
    for k, v in ints.items():
        if not _is_int(v, 0 if k in ("redo_quota", "soak_s", "fixed_overhead_s") else 1):
            problems.append(f"span_template.{k}: must be an integer >= {0 if k in ('redo_quota', 'soak_s', 'fixed_overhead_s') else 1}")
    if any(not _is_int(v) for v in ints.values()):
        return
    if _overlaps_batch(t0, end, batch_window):
        (h0, m0), (h1, m1) = batch_window
        problems.append(f"span_template: the span [t0_local, end_by_local) overlaps the OS batch window "
                        f"{h0:02d}:{m0:02d}-{h1:02d}:{m1:02d}")
    if ints["leg_worst_case_s"] < ints["leg_budget_s"]:
        problems.append("span_template.leg_worst_case_s: below leg_budget_s")
    need = (ints["soak_s"] + ints["fixed_overhead_s"]
            + (ints["legs_per_span"] + ints["redo_quota"]) * ints["leg_worst_case_s"])
    have = _window_s(t0, end)
    if need > have:
        problems.append(f"span_template: needs {need} s at the worst-case bound, the window holds {have} s")


def _check_stops(s, problems):
    if not _closed(s, STOP_KEYS, "stop_rules", problems, required=STOP_KEYS - {"notes"}):
        return
    if s.get("instrument_fault") is not True or s.get("refusal") is not True:
        problems.append("stop_rules: instrument_fault and refusal must both be true")
    if not _is_int(s.get("contaminated_redos_max"), 1, STOP_LIMITS["contaminated_redos_max"]):
        problems.append("stop_rules.contaminated_redos_max: integer 1..3")
    if not _is_int(s.get("band_unreachable_max"), 1, STOP_LIMITS["band_unreachable_max"]):
        problems.append("stop_rules.band_unreachable_max: integer 1..2")
    f = s.get("leg_time_factor")
    if not (isinstance(f, (int, float)) and not isinstance(f, bool) and 1.0 < f <= STOP_LIMITS["leg_time_factor"]):
        problems.append("stop_rules.leg_time_factor: number in (1.0, 1.5]")
    for k in ("contaminated_redos_scope", "band_unreachable_scope"):
        if s.get(k) not in STOP_SCOPES:
            problems.append(f"stop_rules.{k}: one of {STOP_SCOPES}")


def validate_kit(kit, *, batch_window=OS_BATCH_WINDOW):
    """Return the kit unchanged, or raise KitError naming every problem."""
    problems = []
    if not _closed(kit, TOP_KEYS, "kit", problems):
        raise KitError(problems)
    problems.extend(deny_scan(kit))
    if kit.get("schema") != SCHEMA:
        problems.append(f"schema: must be {SCHEMA}")
    cid = kit.get("campaign_id")
    if not (isinstance(cid, str) and CAMPAIGN_ID_RE.fullmatch(cid)):
        problems.append("campaign_id: lowercase id, 3-41 chars")
    if not (isinstance(kit.get("title"), str) and kit["title"].strip()):
        problems.append("title: non-empty text")
    if not (isinstance(kit.get("model"), str) and kit["model"].strip()):
        problems.append("model: non-empty text")

    ruling = kit.get("ruling")
    if _closed(ruling, {"id", "authorizes_spans"}, "ruling", problems):
        if not (isinstance(ruling.get("id"), str) and RULING_RE.fullmatch(ruling["id"])):
            problems.append("ruling.id: RL-<n>")
        if ruling.get("authorizes_spans") is not True:
            problems.append("ruling.authorizes_spans: must be true (a kit without a standing ruling arms nothing)")

    frozen = kit.get("frozen")
    paths = {}
    if _closed(frozen, {"commit", "paths"}, "frozen", problems):
        if not (isinstance(frozen.get("commit"), str) and HEX40.fullmatch(frozen["commit"])):
            problems.append("frozen.commit: full 40-hex sha")
        paths = frozen.get("paths") if isinstance(frozen.get("paths"), dict) else {}
        if not paths:
            problems.append("frozen.paths: at least one path")
        for p, h in paths.items():
            if not PATH_RE.fullmatch(p):
                problems.append(f"frozen.paths: bad path {p!r}")
            if not (isinstance(h, str) and HEX64.fullmatch(h)):
                problems.append(f"frozen.paths[{p}]: sha256 hex")

    runner = kit.get("runner")
    if _closed(runner, RUNNER_KEYS, "runner", problems):
        if runner.get("kind") not in RUNNER_KINDS:
            problems.append(f"runner.kind: one of {sorted(RUNNER_KINDS)}")
        if runner.get("entry") not in paths:
            problems.append("runner.entry: must be a frozen path")
        if runner.get("stage_journal") != "chain-stages.jsonl":
            problems.append("runner.stage_journal: must be chain-stages.jsonl (the RL-128 probe reads it)")

    defaults = kit.get("leg_defaults")
    if _closed(defaults, LEG_DEFAULT_KEYS, "leg_defaults", problems):
        for k in LEG_DEFAULT_KEYS:
            if not _is_int(defaults.get(k), 1):
                problems.append(f"leg_defaults.{k}: positive integer")

    law = kit.get("seed_law")
    bands = []
    if _closed(law, SEED_LAW_KEYS, "seed_law", problems):
        bands = law.get("bands") if isinstance(law.get("bands"), list) else []
        if not (bands and all(isinstance(b, str) and re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,30}", b) for b in bands)
                and len(set(bands)) == len(bands)):
            problems.append("seed_law.bands: distinct short lowercase names")
        if not _is_int(law.get("n_legs"), 1, 9999):
            problems.append("seed_law.n_legs: integer 1..9999")
        if not _is_int(law.get("master_seed"), 0, 2 ** 63 - 1):
            problems.append("seed_law.master_seed: non-negative integer")

    legs = kit.get("legs")
    if not isinstance(legs, list) or not legs:
        problems.append("legs: non-empty list")
        legs = []
    for i, leg in enumerate(legs):
        if _closed(leg, LEG_KEYS, f"legs[{i}]", problems, required={"leg_id", "seed", "start_band"}):
            if not (isinstance(leg.get("leg_id"), str) and LEG_ID_RE.fullmatch(leg["leg_id"])):
                problems.append(f"legs[{i}].leg_id: L<digits>")
            if leg.get("start_band") not in bands:
                problems.append(f"legs[{i}].start_band: not a seed_law band")
    if isinstance(law, dict) and isinstance(defaults, dict) and not any(
            p.startswith(("seed_law", "leg_defaults", "campaign_id")) for p in problems):
        try:
            expected = generate_legs(cid, law, defaults)
        except (KitError, KeyError, TypeError) as error:
            problems.append(f"seed_law: cannot generate legs ({error})")
        else:
            if legs != expected:
                first = next((i for i, (a, b) in enumerate(zip(legs, expected)) if a != b), min(len(legs), len(expected)))
                problems.append(f"legs: not the seed law's list (first difference at index {first}; "
                                f"{len(legs)} given, {len(expected)} generated)")

    rules = kit.get("inclusion_rules")
    if not isinstance(rules, list) or not rules:
        problems.append("inclusion_rules: non-empty list")
    else:
        ids = []
        for i, r in enumerate(rules):
            if _closed(r, {"id", "text"}, f"inclusion_rules[{i}]", problems):
                if not (isinstance(r.get("id"), str) and CHECK_ID_RE.fullmatch(r["id"])):
                    problems.append(f"inclusion_rules[{i}].id: lowercase id")
                if not (isinstance(r.get("text"), str) and r["text"].strip()):
                    problems.append(f"inclusion_rules[{i}].text: the ruling's words")
                ids.append(r.get("id"))
        if len(set(map(str, ids))) != len(ids):
            problems.append("inclusion_rules: duplicate id")

    _check_stops(kit.get("stop_rules"), problems)
    _check_template(kit.get("span_template"), problems, batch_window)

    checklist = kit.get("checklist")
    if not isinstance(checklist, list):
        problems.append("checklist: list")
        checklist = []
    seen_ids, kinds = set(), []
    for i, line in enumerate(checklist):
        if _closed(line, {"id", "kind", "args"}, f"checklist[{i}]", problems, required={"id", "kind"}):
            if not (isinstance(line.get("id"), str) and CHECK_ID_RE.fullmatch(line["id"])) or line["id"] in seen_ids:
                problems.append(f"checklist[{i}].id: unique lowercase id")
            seen_ids.add(line.get("id"))
            if line.get("kind") not in CHECK_KINDS:
                problems.append(f"checklist[{i}].kind: unknown {line.get('kind')!r}")
            kinds.append(line.get("kind"))
            args = line.get("args", {})
            if line.get("kind") == "disk_free_gb":
                if not (isinstance(args, dict) and set(args) == {"min_gb"} and _is_int(args.get("min_gb"), 1)):
                    problems.append(f"checklist[{i}].args: {{'min_gb': int >= 1}}")
            elif args not in ({}, None):
                problems.append(f"checklist[{i}].args: {line.get('kind')} takes no args")
    for kind in sorted(set(CHECK_KINDS) - set(kinds)):
        problems.append(f"checklist: mandatory check {kind!r} missing")
    for kind in sorted({k for k in kinds if kinds.count(k) > 1}):
        problems.append(f"checklist: {kind!r} listed twice")

    looks = kit.get("looks")
    if not isinstance(looks, list):
        problems.append("looks: list (may be empty)")
        looks = []
    last = 0
    n_legs = len(legs)
    for i, look in enumerate(looks):
        if _closed(look, {"look_id", "after_legs", "fit"}, f"looks[{i}]", problems):
            if not (isinstance(look.get("look_id"), str) and CHECK_ID_RE.fullmatch(look["look_id"])):
                problems.append(f"looks[{i}].look_id: lowercase id")
            a = look.get("after_legs")
            if not _is_int(a, last + 1, n_legs or None):
                problems.append(f"looks[{i}].after_legs: strictly increasing, at most the leg count")
            else:
                last = a
            fit = look.get("fit")
            if not (isinstance(fit, dict) and set(fit) == {"path"} and fit.get("path") in paths):
                problems.append(f"looks[{i}].fit: {{'path': <a frozen path>}} (energy is read only by frozen fit code)")

    desk = kit.get("desk")
    if _closed(desk, {"adapter"}, "desk", problems) and desk.get("adapter") not in DESK_ADAPTERS:
        problems.append(f"desk.adapter: one of {sorted(DESK_ADAPTERS)}")

    if problems:
        raise KitError(problems)
    return kit


def load_kit(path, *, batch_window=OS_BATCH_WINDOW):
    raw = Path(path).read_bytes()
    try:
        kit = json.loads(raw, object_pairs_hook=_unique)
    except ValueError as error:
        raise KitError([f"{path}: not JSON ({error})"]) from None
    return validate_kit(kit, batch_window=batch_window), hashlib.sha256(raw).hexdigest()


def _unique(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"duplicate key {k!r}")
        out[k] = v
    return out


def verify_frozen(kit, repo):
    """Hash every frozen path at frozen.commit in ``repo``. Returns mismatches (empty = ok)."""
    problems = []
    commit = kit["frozen"]["commit"]
    for path, expected in sorted(kit["frozen"]["paths"].items()):
        try:
            blob = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"{commit}:{path}"],
                                  capture_output=True, check=True, timeout=60).stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
            problems.append(f"{path}: not readable at {commit[:12]}")
            continue
        got = hashlib.sha256(blob).hexdigest()
        if got != expected:
            problems.append(f"{path}: sha256 {got} != kit {expected}")
    return problems


def span_window_epochs(template, day):
    """(t0, end_by) epoch seconds for the span whose t0 falls on local calendar ``day``."""
    zone = ZoneInfo(template["timezone"])
    t0_min, end_min = _hhmm(template["t0_local"]), _hhmm(template["end_by_local"])
    t0 = datetime(day.year, day.month, day.day, t0_min // 60, t0_min % 60, tzinfo=zone)
    end_day = day + timedelta(days=1 if end_min <= t0_min else 0)
    end = datetime(end_day.year, end_day.month, end_day.day, end_min // 60, end_min % 60, tzinfo=zone)
    return t0.timestamp(), end.timestamp()


def _local_hhmm(epoch, zone):
    return datetime.fromtimestamp(epoch, ZoneInfo(zone)).strftime("%H:%M")


def evaluate_checklist(kit, obs, *, expected_kit_sha256):
    """Judge one span's observations. Returns [{id, kind, ok, detail}]; all must be ok to arm."""
    frozen = kit["frozen"]
    template = kit["span_template"]
    out = []
    missing = object()

    def get(key):
        return obs.get(key, missing)

    for line in kit["checklist"]:
        kind, ok, detail = line["kind"], False, ""
        if kind == "head_is_frozen_commit":
            v = get("measurement_head"); ok = v == frozen["commit"]; detail = f"head {v if v is not missing else 'not observed'}"
        elif kind == "frozen_paths_hash":
            v = get("frozen_path_sha256")
            ok = isinstance(v, dict) and v == frozen["paths"]
            bad = sorted(p for p in frozen["paths"] if not isinstance(v, dict) or v.get(p) != frozen["paths"][p])
            detail = "all paths match" if ok else f"mismatch or unobserved: {bad[:5]}"
        elif kind == "kit_sha256":
            v = get("kit_sha256"); ok = v == expected_kit_sha256; detail = f"kit {v if v is not missing else 'not observed'}"
        elif kind == "ac_power":
            ok = get("ac_power") is True
        elif kind == "powermode_zero":
            ok = get("powermode") == 0
        elif kind == "network_time_off":
            ok = get("network_time") == "off"
        elif kind == "freq_word_zero":
            ok = get("freq_word") == 0
        elif kind == "no_stray_monitor":
            ok = get("stray_monitors") == []
        elif kind == "no_other_agent":
            ok = get("other_agents") == []
        elif kind == "no_night_agent_loaded":
            ok = get("night_labels_loaded") == []
        elif kind == "no_high_power_marker":
            ok = get("high_power_marker") is False
        elif kind == "sudo_kill":
            ok = get("sudo_kill_rc") == 0
        elif kind == "km003c_ready":
            ok = get("km003c_ready") is True
        elif kind == "disk_free_gb":
            v = get("disk_free_gb")
            ok = isinstance(v, (int, float)) and not isinstance(v, bool) and v >= line["args"]["min_gb"]
            detail = f"{v if v is not missing else 'not observed'} GB >= {line['args']['min_gb']}"
        elif kind == "previous_span_closed":
            v = get("previous_span"); ok = v in ("none", "closed_no_stop"); detail = str(v if v is not missing else "not observed")
        elif kind == "no_halt_or_veto":
            v = get("halts"); ok = v == []; detail = "none" if ok else f"{v if v is not missing else 'not observed'}"
        elif kind == "span_window":
            t0, end = get("t0_epoch_s"), get("end_by_epoch_s")
            ok = (isinstance(t0, (int, float)) and isinstance(end, (int, float)) and 0 < end - t0 <= 86400
                  and _local_hhmm(t0, template["timezone"]) == template["t0_local"]
                  and _local_hhmm(end, template["timezone"]) == template["end_by_local"])
            detail = "template times" if ok else "t0/end-by not the template's local times"
        if not detail:
            v = get({"ac_power": "ac_power", "powermode_zero": "powermode", "network_time_off": "network_time",
                     "freq_word_zero": "freq_word", "no_stray_monitor": "stray_monitors",
                     "no_other_agent": "other_agents", "no_night_agent_loaded": "night_labels_loaded",
                     "no_high_power_marker": "high_power_marker", "sudo_kill": "sudo_kill_rc",
                     "km003c_ready": "km003c_ready"}.get(kind, kind))
            detail = "not observed" if v is missing else f"observed {v!r}"
        out.append({"id": line["id"], "kind": kind, "ok": bool(ok), "detail": detail})
    return out
