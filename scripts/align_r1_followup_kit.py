#!/usr/bin/env python3
"""RL-72/74/76 R1 follow-up: prepare, bounded native smoke, temperature-only desk.

Preparing does not install or arm a night. The lead supplies the ordinary
night-plan machine/custody fields using this exact sizing and chain. RL-62
and RL-73 refuse-only checks plug in at prepare_checks(), before any dwell.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import align_v4_session as v4_session
from scripts import align_r1_rehearsal as r1
from scripts import align_r1_thermal_replay as replay
from joulewise.align.apple import r1_runtime as rt, v4_registration as reg
from joulewise.align.apple.thermal import Coverage, valid_value

# R1 changes run IDs; project each explicit member to the registered root,
# retaining the registration's exact digests and file maps (never re-register).
MEMBER_ROOTS = {
    "step-30b": ("model_30b", "qwen3-30b-a3b-align-pilot-v3-episodes-a-e01"),
    "high-power-aba-a1": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "high-power-aba-b": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "high-power-aba-a2": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "capture-predecessor-30b": ("model_30b", "qwen3-30b-a3b-align-pilot-v3-episodes-a-e01"),
    "step-d": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-planning-turn-r-plus-4c": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-planning-turn-r-plus-2c": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-planning-turn-r-plus-0c": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-bank-benign-s1": ("d_bank", "qwen3.8-27b-align-v4-episodes-a-e08"),
    "d-spam-benign-s1-a": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-spam-benign-s1-b": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "x-g": ("x_g", "qwen3-30b-a3b-align-v4-episodes-a-e06"),
    "neg8-reference": (None, "neg8_reference"),
}


def prepare_checks(root, config, *, weight_digest_check=None, runtime_stack_check=None,
                   identity_fn=None, runtime_runner=None, reader=None):
    """Both public armcheck APIs run before source checks or any dwell.

    reader/identity_fn/runtime_runner are synthetic-test seams. Production
    uses the real checks; this function does not launch any host setter.
    """
    root = Path(root)
    registration = root / reg.REGISTRATION
    read = reader or (lambda p: json.loads(Path(p).read_bytes()))
    inventory_path = registration / "model_artifact_inventory.json"
    mapping = {}
    try:
        inventory = read(inventory_path)
        projected = dict(inventory["artifacts"])
        members, mapping = [], {}
        for name, (template_key, registered_unit) in MEMBER_ROOTS.items():
            row = projected.get(registered_unit)
            if not isinstance(row, dict):
                raise ValueError(f"weight_digest_preflight: no_inventory_row: {registered_unit}")
            if template_key is not None:
                template_path = Path(config["templates"][template_key])
                template = read(template_path if template_path.is_absolute() else root / template_path)
                if template["model"]["source"] != row["root"]:
                    raise ValueError(f"weight_digest_preflight: no_inventory_row: {name}: template root differs")
            if template_key is None:
                member = {"model_id": "neg8", "run_id": "reference"}
            else:
                member = {"model_id": "qwen3.8-27b" if template_key in ("d_spam", "d_bank") else "qwen3-30b-a3b",
                          "run_id": template["run_id"] if name == "capture-predecessor-30b" else "align-v4-r1-" + name}
            unit = v4_session.pilot.h.align_unit_id(**member)
            projected[unit] = row
            members.append(member)
            mapping[unit] = registered_unit
        def projected_reader(path):
            return {**inventory, "artifacts": projected} if Path(path) == inventory_path else read(path)
        weights = (weight_digest_check or v4_session.weight_digest_preflight)(
            registration, members, identity_fn=identity_fn, reader=projected_reader)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        reason = str(exc)
        if not reason.startswith("weight_digest_preflight:"):
            reason = f"weight_digest_preflight: unavailable: {type(exc).__name__}: {exc}"
        weights = {"ok": False, "reasons": [reason], "roots": {}}
    stack = (runtime_stack_check or v4_session.runtime_stack_preflight)(
        config.get("measurement_python", str(root / ".venv/bin/python")), registration / "identity_pins.json",
        runner=runtime_runner, reader=read)
    checks = {"weight_digests": weights, "runtime_stack": stack, "registered_member_roots": mapping}
    return checks


# RL-119 step 2 / RL-122: after RL-116 unseated the registered slow pick on the
# saved Part B D classification, the second gate key is the registered fast
# rule applied a second time to that same classification, under ruling RL-122
# only. No other slow rule, and no hand pick, is accepted.
SECOND_FAST_RULE = "fast_rule_second_application"
SECOND_FAST_RULE_RULING = "RL-122"
SECOND_FAST_RULE_CLASSIFICATION_SHA256 = "0b9cdb9e136eee48c742a6bdfef3313373f795949027779353c31f717630e0a6"
# The regenerated table (docs/run_reports/2026-11-12-rl122/smoke_part_b.rl122.json):
# the RL-122 path accepts these exact bytes only, so an edited ranking or
# coverage under the same declared classification digest cannot move the pick
# (PR #752 cold review F2).
SECOND_FAST_RULE_TABLE_SHA256 = "b2369b6c78d91b75299e10ff7249f1e8cae7304b48cf022e20b2c6a6f69f2884"


# RL-145 section 3 / addendum row 4: the second key is the lexically first other member
# of the fast pick's alias group on the same saved Part B classification. It replaces
# RL-122's rule (TVh0 failed its own quality clauses on the 11-13 D step). The Part B
# table is re-derived from the RL-122 table (itself re-derived from RL-89's), never
# re-measured; the RL-145 path accepts those exact bytes only.
ALIAS_SECOND_KEY_RULE = "alias_group_lexical_first"
ALIAS_SECOND_KEY_RULING = "RL-145"
ALIAS_SECOND_KEY_SOURCE_TABLE_SHA256 = SECOND_FAST_RULE_TABLE_SHA256   # the RL-122 table
ALIAS_SECOND_KEY_TABLE_SHA256 = "0dd1d4efeec3acb1e6ee6f26b5ca94e1bd2748560a627a040811c3df6af9498b"


def table_bytes(table):
    """The kit's own Part B serialization (smoke() writes exactly this)."""
    return (json.dumps(table, indent=2, sort_keys=True) + "\n").encode()


def second_fast_rule_selection(table, config):
    """RL-119 step 2 / RL-122 item 7: the fast rule applied a second time.

    On the saved Part B table: among keys R0 classed ``die`` (the config's
    ``r0_classes``) that pass every smoke phase (the filter the registered fast
    pick itself went through) and are admissible for the slow role beside the
    registered fast pick as ``sensor_admissibility`` tests it, excluding the
    fast pick and its aliases and clamped keys: the largest observed rise,
    lexical ties (``select_keys``'s order). Derived here, never supplied.
    """
    classification = table["classification_table"]["classification"]
    coverage, r0_keys = table["coverage"], config["r0_classified_keys"]
    fast = smoke_selection(classification, coverage, r0_keys)["s_fast"]
    excluded = {fast, *classification.get("selected_key_aliases", {}).get(fast, [])}
    excluded.update(k for group in classification.get("alias_groups", []) if fast in group for k in group)
    phases = coverage.get("phases") or {}
    candidates = sorted(
        (row for row in classification["ranking"]
         if config["r0_classes"].get(row["key"]) == "die" and row["key"] not in excluded
         and not row.get("clamped") and rt._finite(row.get("observed_rise"))
         and phases and all(p.get(row["key"], {}).get("pass", False) for p in phases.values())
         and rt.sensor_admissibility(classification, {"s_fast": fast, "s_slow": row["key"]}, r0_keys)["ok"]),
        key=lambda r: (-r["observed_rise"], r["key"]))
    slow = candidates[0]["key"] if candidates else None
    result = rt.sensor_admissibility(classification, {"s_fast": fast, "s_slow": slow}, r0_keys)
    return {**result, "ok": result["ok"] and fast is not None and slow is not None, "fallback": False,
            "selected_at": "smoke_part_b", "slow_rule": SECOND_FAST_RULE,
            "candidates": [r["key"] for r in candidates]}


def second_fast_rule_table_identities(saved, regenerated, config):
    """RL-89's four identities, with only ``selection.s_slow`` changed (RL-122 item 7 step 2)."""
    pick = second_fast_rule_selection(saved, config)
    failures = []
    digests = {t["classification_table"]["classification"].get("classification_sha256") for t in (saved, regenerated)}
    if digests != {SECOND_FAST_RULE_CLASSIFICATION_SHA256}:
        failures.append("1: classification_sha256 is not the saved D classification's")
    if saved.get("coverage") != regenerated.get("coverage") or not saved.get("coverage", {}).get("pass"):
        failures.append("2: coverage differs or did not pass")
    selection = regenerated.get("selection", {})
    if not (pick["ok"] and selection.get("ok") is True and selection.get("fallback") is False
            and selection.get("reasons") == [] and selection.get("s_fast") == pick["s_fast"]
            and selection.get("s_slow") == pick["s_slow"]):
        failures.append("3: selection is not ok / no fallback / the rule's pair")
    others = [k for k in set(saved) | set(regenerated) if k != "selection" and saved.get(k) != regenerated.get(k)]
    others += [f"selection.{k}" for k in set(saved.get("selection", {})) | set(selection)
               if k != "s_slow" and saved.get("selection", {}).get(k) != selection.get(k)]
    if others:
        failures.append("4: fields other than selection.s_slow changed: " + ", ".join(sorted(others)))
    if failures:
        raise ValueError("RL-122: regenerated Part B table fails RL-89's identities: " + "; ".join(failures))
    return pick


def regenerate_second_fast_rule_table(saved_raw, config):
    """Re-derive (never re-measure) the Part B table: only the selection's slow key changes."""
    saved = json.loads(saved_raw)
    if table_bytes(saved) != saved_raw:
        raise ValueError("RL-122: the saved Part B table is not in the kit's own serialization")
    pick = second_fast_rule_selection(saved, config)
    if not pick["ok"]:
        raise ValueError("RL-122: the fast rule's second application gives no admissible pair: "
                         + "; ".join(pick["reasons"]))
    regenerated = json.loads(saved_raw)
    regenerated["selection"]["s_slow"] = pick["s_slow"]
    second_fast_rule_table_identities(saved, regenerated, config)
    return table_bytes(regenerated)


def alias_second_key_selection(table, config):
    """RL-145 section 3: the lexically first other member of the fast pick's alias group.

    Derived on the saved Part B table, never supplied: the fast pick is the registered
    chooser's (``smoke_selection``); its alias group is the one in the classification's
    ``alias_groups``; the second key is that group's lexically first other member. The
    pair must pass the session's own confirmation (``rt.night_confirmation``) on this
    classification. No group, or an inadmissible fast key, gives no pair.
    """
    classification = table["classification_table"]["classification"]
    coverage, r0_keys = table["coverage"], config["r0_classified_keys"]
    fast = smoke_selection(classification, coverage, r0_keys)["s_fast"]
    group = next((g for g in classification.get("alias_groups", []) if fast in g), [])
    others = sorted(k for k in group if k != fast)
    slow = others[0] if others else None
    result = rt.night_confirmation(classification, {"s_fast": fast, "s_slow": slow}, r0_keys, config["r0_classes"])
    return {**result, "ok": result["ok"] and fast is not None and slow is not None, "fallback": False,
            "selected_at": "smoke_part_b", "slow_rule": ALIAS_SECOND_KEY_RULE, "candidates": others}


def alias_second_key_table_identities(saved, regenerated, config):
    """RL-89's four identities against the RL-122 table, with only ``selection.s_slow`` changed."""
    pick = alias_second_key_selection(saved, config)
    failures = []
    digests = {t["classification_table"]["classification"].get("classification_sha256") for t in (saved, regenerated)}
    if digests != {SECOND_FAST_RULE_CLASSIFICATION_SHA256}:
        failures.append("1: classification_sha256 is not the saved D classification's")
    if saved.get("coverage") != regenerated.get("coverage") or not saved.get("coverage", {}).get("pass"):
        failures.append("2: coverage differs or did not pass")
    selection = regenerated.get("selection", {})
    if not (pick["ok"] and selection.get("ok") is True and selection.get("fallback") is False
            and selection.get("reasons") == [] and selection.get("s_fast") == pick["s_fast"]
            and selection.get("s_slow") == pick["s_slow"]):
        failures.append("3: selection is not ok / no fallback / the rule's pair")
    others = [k for k in set(saved) | set(regenerated) if k != "selection" and saved.get(k) != regenerated.get(k)]
    others += [f"selection.{k}" for k in set(saved.get("selection", {})) | set(selection)
               if k != "s_slow" and saved.get("selection", {}).get(k) != selection.get(k)]
    if others:
        failures.append("4: fields other than selection.s_slow changed: " + ", ".join(sorted(others)))
    if failures:
        raise ValueError("RL-145: regenerated Part B table fails RL-89's identities: " + "; ".join(failures))
    return pick


def regenerate_alias_second_key_table(saved_raw, config):
    """Re-derive (never re-measure) the RL-122 Part B table: only the selection's slow key changes."""
    saved = json.loads(saved_raw)
    if table_bytes(saved) != saved_raw:
        raise ValueError("RL-145: the saved Part B table is not in the kit's own serialization")
    pick = alias_second_key_selection(saved, config)
    if not pick["ok"]:
        raise ValueError("RL-145: the alias-group rule gives no confirmed pair: " + "; ".join(pick["reasons"]))
    regenerated = json.loads(saved_raw)
    regenerated["selection"]["s_slow"] = pick["s_slow"]
    alias_second_key_table_identities(saved, regenerated, config)
    return table_bytes(regenerated)


def validate_sensor_ruling(config, ruling, smoke_sha256, table):
    if (not ruling.get("research_lead_ruling") or ruling.get("smoke_part_b_sha256") != smoke_sha256
            or ruling.get("sensors") != config["sensors"] or ruling.get("authorizes_night") is not True):
        raise ValueError("arm requires the research lead's ruling on this smoke D table and this policy")
    if not table.get("coverage", {}).get("pass"):
        raise ValueError("smoke Part B sampler bar failed")
    if table.get("r0_classified_keys") != config["r0_classified_keys"]:
        raise ValueError("RL-78: smoke R0 key set changed; selection is made once")
    classification = table["classification_table"]["classification"]
    digest = classification.get("classification_sha256")
    rule = ruling.get("slow_rule")
    if rule is None:
        if digest == SECOND_FAST_RULE_CLASSIFICATION_SHA256:
            raise ValueError("RL-116: the registered slow pick on this D classification was unseated; only "
                             f"ruling {ALIAS_SECOND_KEY_RULING}'s {ALIAS_SECOND_KEY_RULE} pick is accepted")
        selected = smoke_selection(classification, table["coverage"], config["r0_classified_keys"])
        label = "RL-78: policy must use the fixed smoke Part B selection: "
    elif rule == SECOND_FAST_RULE:
        raise ValueError(f"slow rule {rule!r} (ruling {SECOND_FAST_RULE_RULING}) is refused: it prepares a session on "
                         "TVh0, which RL-145 unseated with no fallback role; only the alias-group rule of "
                         f"{ALIAS_SECOND_KEY_RULING} is accepted")
    elif (rule == ALIAS_SECOND_KEY_RULE and ruling.get("research_lead_ruling") == ALIAS_SECOND_KEY_RULING
          and ruling.get("classification_sha256") == digest == SECOND_FAST_RULE_CLASSIFICATION_SHA256):
        if smoke_sha256 != ALIAS_SECOND_KEY_TABLE_SHA256:
            raise ValueError(f"{ALIAS_SECOND_KEY_RULING}: the Part B table must be the regenerated table "
                             f"{ALIAS_SECOND_KEY_TABLE_SHA256}, not {smoke_sha256}")
        selected = alias_second_key_selection(table, config)
        if table.get("selection", {}).get("ok") is not True or table["selection"].get("fallback") is not False:
            raise ValueError("RL-145: the Part B selection must be ok with no fallback")
        label = f"{ALIAS_SECOND_KEY_RULING}: policy must use the fast pick's lexically first alias: "
    else:
        raise ValueError(f"slow rule {rule!r} refused: only the registered rule, or {ALIAS_SECOND_KEY_RULE} under "
                         f"ruling {ALIAS_SECOND_KEY_RULING} on its own D classification, is accepted")
    mismatched = [r for r in ("s_fast", "s_slow")
                  if selected[r] != config["sensors"][r] or selected[r] != table.get("selection", {}).get(r)]
    if not selected["ok"] or mismatched:
        raise ValueError(label + "; ".join(selected["reasons"] + [
            f"{r}: policy {config['sensors'][r]!r} / table {table.get('selection', {}).get(r)!r} "
            f"is not the derived {selected[r]!r}" for r in mismatched]))
    if config.get("slow_band_floor_c") != 1.0:
        raise ValueError("RL-78: default max(1 C, 3 soak idle SD); no S6 receipt transfer")
    if "Tf08" not in config["sensors"].get("record_keys", []):
        raise ValueError("RL-84: Tf08 must be journalled in every member that runs the thermal sidecar")
    return selected


def prepare(output, *, root=ROOT, config_path=None, ruling=None, smoke_table=None,
            weight_digest_check=None, runtime_stack_check=None, identity_fn=None, runtime_runner=None, reader=None):
    root = Path(root)
    path = Path(config_path or root / r1.DEFAULT_RUNTIME_CONFIG)
    config, _ = rt.load_config(path)
    checks = prepare_checks(root, config, weight_digest_check=weight_digest_check,
                            runtime_stack_check=runtime_stack_check, identity_fn=identity_fn,
                            runtime_runner=runtime_runner, reader=reader)
    failures = [reason for key in ("weight_digests", "runtime_stack") if not checks[key]["ok"]
                for reason in (checks[key]["reasons"] or [key + ": preflight refused"])]
    if failures:
        # Keep both refuse-only results reviewable even when prepare refuses.
        with Path(output).open("x") as handle:
            handle.write(json.dumps({"status": "REFUSED", **checks}, indent=2, sort_keys=True) + "\n")
        raise ValueError("; ".join(failures))
    if ruling is None or smoke_table is None:
        raise ValueError("arm waits for smoke Part B and RL-74/75 sensor ruling")
    validate_sensor_ruling(config, ruling, hashlib.sha256(Path(smoke_table).read_bytes()).hexdigest(),
                           json.loads(Path(smoke_table).read_bytes()))
    commit = r1.executed_commit(root)
    reg.verify_r1_executed_sources(root, {"executed_commit": commit})
    gate = "joulewise/align/apple/thermal_gates.py"
    expected = reg._committed_bytes(root, "82c14c9ea", [gate])[gate]
    if (root / gate).read_bytes() != expected:
        raise ValueError("W1 thermal gate bytes changed")
    bounds = r1.night_worst_case_s(["--config", str(path)])
    # RL-72 E2's construction at the RL-149 section 2.9 item 4 blackout (02:00-02:35): 119,880 s (was 126,480).
    if bounds["window_max_s"] != 119880 or bounds["overhead_s"] != 9000:
        raise ValueError("follow-up sizing differs from RL-72 E2 at the RL-149 blackout")
    packet = {"schema": "joulewise.align.r1_followup_prepare.v1", "status": "FOR_LEAD_ARM",
              "executed_commit": commit, "sensors": config["sensors"], "sensor_ruling": ruling,
              **checks, "chain_script": "scripts/night_chains/align_r1_rehearsal.zsh",
              **bounds, "bound_files": {p: rt.sha256_file(root / p) for p in reg.R1_EXECUTED_SOURCES}}
    with Path(output).open("x") as handle:
        handle.write(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    return packet


def phase_coverage(rows, keys, phases, *, required_keys=("Tf08",)):
    """RL-84: sweep stalls fail smoke; a key's failures reject only that key.

    Tf08 is mandatory for the disclosure. Key accounting follows rank()'s
    half-period grid, bracket validity and phase-local read-error denominator.
    A sweep is counted independently of whether any of its key reads succeed.
    """
    report, sampler = {}, {}
    for name, (start, end) in phases.items():
        selected = [r for r in rows if start <= r["started"]["monotonic_ns"] < end]
        sweeps = Coverage(start, ["sweep"], tolerance_ns=rt.NS // 2)
        for row in selected:
            a, b = row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"]
            if a <= b < end and b-a <= rt.NS:
                sweeps.observe(a, b, {"sensors": {"sweep": 1}, "errors": {}})
        sweep = sweeps.report(end)["all_keys"]
        sampler[name] = {**sweep, "pass": (sweep["sample_fraction"] is not None
                         and sweep["sample_fraction"] >= .99 and sweep["max_consecutive_empty_cells"] < 2)}
        per_key = {}
        for key in keys:
            counter = Coverage(start, [key], tolerance_ns=rt.NS // 2)
            failures = 0
            for row in selected:
                values = row["values"]
                a, b = row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"]
                bracket_valid = a <= b < end and b-a <= rt.NS
                failures += (not bracket_valid or key in values.get("errors", {})
                             or not valid_value(key, values.get("sensors", {}).get(key)))
                if bracket_valid:
                    counter.observe(a, b, values)
            cell = counter.report(end)["all_keys"]
            error_fraction = failures / len(selected) if selected else 1.0
            reasons = []
            if cell["sample_fraction"] is None or cell["sample_fraction"] < .99:
                reasons.append("under 99% of one-second cells")
            if error_fraction >= .01:
                reasons.append(">=1% read errors")
            if cell["max_consecutive_empty_cells"] >= 2:
                reasons.append("two consecutive empty one-second cells")
            per_key[key] = {**cell, "read_error_fraction": error_fraction,
                           "pass": not reasons, "reasons": reasons}
        report[name] = per_key
    return {"phases": report, "sampler": sampler, "required_keys": list(required_keys),
            "pass": bool(report) and all(s["pass"] for s in sampler.values()) and all(
                p.get(key, {}).get("pass", False) for p in report.values() for key in required_keys)}


def smoke_selection(classification, coverage, r0_keys):
    """Run the registered chooser on keys passing every phase, then RL-78's fallback.

    Keep the full classifier result unchanged in the table. Pre-warmup is an
    additional smoke phase; its failures also exclude a key from either role.
    R0 membership is checked after selection, and restricts fallback candidates
    only; an otherwise selected key outside R0 must be held for the lead.
    """
    from joulewise.align.apple.smc_enumeration import select_keys
    phases = coverage["phases"]
    ranking = [row for row in classification["ranking"] if phases
               and all(p.get(row["key"], {}).get("pass", False) for p in phases.values())]
    filtered = {**classification, "ranking": ranking, **select_keys(ranking),
                "heatsink_candidates": [r["key"] for r in ranking if r["class"] == "heatsink"]}
    return rt.select_smoke_sensors(filtered, r0_keys)


def class_edge_margins(classification):
    """Signed headroom, disclosure only; selection never reads this table."""
    result = []
    for row in classification["ranking"]:
        def margin(value, edge, lower=False):
            return None if value is None else value-edge if lower else edge-value
        result.append({"key": row["key"], "rise_above_3_c": margin(row.get("observed_rise"), 3., True),
            "return_time_below_300_s": margin(row.get("t_band_s"), 300.),
            "tau_below_fast_edge_s": margin(row.get("tau_s"), 60.),
            "tau_above_slow_edge_s": margin(row.get("tau_s"), 60., True),
            "noise_below_fast_c": margin(row.get("noise"), 1/3),
            "noise_below_slow_c": margin(row.get("noise"), .15)})
    return result


def smoke_table(segment_dir):
    """Part B: classifier verbatim plus candidate/band/ref-sensitivity table."""
    segment = Path(segment_dir)
    fields = json.loads((segment / rt.RESULT_NAME).read_text())
    bundle = segment / fields["bundle"]
    journal = replay.read_journal(bundle / "outputs/align_thermal.jsonl")
    session = replay.Session(journal["rows"], journal["s_fast"], journal["s_slow"])
    anchor = replay.warmup_anchor(bundle, session)
    saved = json.loads((segment / "inventory/r1_classification.json").read_text())
    rows = [json.loads(line) for line in (segment / "inventory/inventory_journal.jsonl").read_text().splitlines() if line.strip()]
    bounds = saved["classification"]["phase_bounds_ns"]
    idle_start = anchor - 300 * rt.NS
    for line in (bundle / "events.jsonl").read_text().splitlines():
        event = json.loads(line)
        if event.get("event_type") == "stage_started" and event.get("phase") == "idle_baseline":
            idle_start = session.mono_from_epoch(event["timestamp_s"])
            break
    spans = {"pre_warmup_idle": (idle_start, anchor),
             **{name: tuple(span) for name, span in bounds.items()}}
    keys = [k["key"] for k in saved["inventory"]["keys"] if k.get("unit") == "degC"]
    config = json.loads((ROOT / r1.DEFAULT_RUNTIME_CONFIG).read_bytes())
    coverage = phase_coverage(rows, keys, spans)
    rejected = [{"key": key, "r0_class": config["r0_classes"].get(key, "unclassified"),
                 "phase": phase, "reason": reason}
                for phase, per_key in coverage["phases"].items() for key, cell in per_key.items()
                for reason in cell["reasons"]]
    selection = smoke_selection(saved["classification"], coverage, config["r0_classified_keys"])
    g0 = journal["g0"][0]
    candidates = replay.candidate_replays(rows, journal["rows"], keys, journal["s_fast"], anchor,
                                          g0["start_ns"], g0["end_ns"])
    return {"schema": "joulewise.align.r1_smoke_b.v1", "classification_table": saved,
            "coverage": coverage, "rejected_keys": rejected, "candidate_replays": candidates,
            "status": ("COVERAGE_FAILED" if not coverage["pass"] else
                       "FOR_RESEARCH_LEAD_RULING" if selection["ok"] else "SELECTION_FAILED"),
            "selection": selection, "r0_classified_keys": config["r0_classified_keys"],
            "class_edge_margins": class_edge_margins(saved["classification"]),
            "note": "RL-78/84: margins are disclosures; sweep/Tf08 failures fail smoke; other keys fail individually. Classifier unchanged."}


PART_C_GATED_D = "D_bank_benign_s1_gated_held"      # r1_phase_table.GATED_D_RUNS[0]
PART_C_X_G = "X_G_contrast"


def smoke_part_c(output, runtime, config, *, soak_reference, invoke=r1._invoke,
                 facts=None, step_facts=None, prints=None):
    """RL-145 step 3 / addendum section 6, Part C: a gated smoke on the final bytes.

    The 30B predecessor, then step-D as the night runs it (Part A on the final bytes, with the
    slots it needs), then the gated D_bank member seed 1 (the runtime applies W1's
    inter-member schedule: the member's own configured idle), then X_G, which the existing
    runtime kind runs with no further condition-13 code. It produces no slots and enters
    nothing: the slots the gated runs read stay in this smoke's own step-D result. The verdict
    is ``align_r1_part_c.evaluate``'s; a failure raises after the table is written.
    """
    from scripts import align_r1_part_c as part_c
    facts = facts or part_c.facts_from_bundle
    step_facts = step_facts or part_c.step_d_facts
    if prints is None:
        from joulewise.align.apple.rl145_prints import bundle_prints
        prints = lambda bundle: bundle_prints(bundle, estimate_tokens=True)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    result = {"part": "C", "authority": "RL-145 step 3; RL-145 addendum section 6", "slots_entered": False, "members": {}}

    def finish(verdict_doc=None, error=None):
        if verdict_doc is not None:
            result["evaluation"] = verdict_doc
        if error is not None:
            result["error"] = error
        result["elapsed_s"] = time.monotonic() - started
        (output / "smoke_part_c.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        (output / "smoke.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    try:
        result["members"]["predecessor"] = invoke(runtime, "capture-predecessor-30b", output / "capture_predecessor_30b",
                                                  soak_reference=soak_reference)
        step_dir = output / rt.STEP_D_SEGMENT
        step = invoke(runtime, "step-d", step_dir, soak_reference=soak_reference)
        result["members"]["step_d"] = step
        slots = step.get("slots")
        n_chunk = (slots or {}).get("N_chunk")
        step_line = step_facts(step_dir / step["bundle"], step) if step.get("bundle") else {"g0_outcome": step.get("g0_outcome")}
        if not isinstance(slots, dict) or not isinstance(n_chunk, int):
            doc = part_c.evaluate(step_d=step_line, d_bank=None, n_chunk=n_chunk if isinstance(n_chunk, int) else 1)
            finish(doc, "step-D produced no slots: the gated members cannot run")
            raise ValueError("Part C: step-D produced no slots; see smoke_part_c.json")
        bank_dir = output / PART_C_GATED_D
        bank = invoke(runtime, "d-bank-benign-s1", bank_dir, soak_reference=soak_reference)
        result["members"]["d_bank"] = bank
        bank_facts = facts(bank_dir / bank["bundle"], role="d-bank")
        # The runtime's own X7 flag and T_dead are the authority where it reports them.
        bank_facts["x7"] = bank.get("x7", bank_facts["x7"])
        bank_facts["t_dead_s"] = (bank.get("deadman") or {}).get("T_dead_s", bank_facts["t_dead_s"])
        # RL-149 section 1.5: the stop reason is read from the runtime's episode flags where it reports them.
        if isinstance(bank.get("episode_flags"), list):
            bank_facts["episode_flags"] = list(bank["episode_flags"])
        printed = prints(bank_dir / bank["bundle"])
        x_g_facts, why = None, None
        try:
            x_g = invoke(runtime, "x-g", output / PART_C_X_G, soak_reference=soak_reference)
            result["members"]["x_g"] = x_g
            x_g_facts = facts(output / PART_C_X_G / x_g["bundle"], role="x-g")
            x_g_facts["x7"] = any(f.startswith("episode.deadman:") for f in x_g.get("episode_flags", []))
        except (r1.Refusal, ValueError, KeyError, OSError) as exc:
            why = f"{type(exc).__name__}: {exc}"
            print(f"Part C: X_G left out, the launcher could not run it without more condition-13 code: {why}",
                  file=sys.stderr)
        doc = part_c.evaluate(step_d=step_line, d_bank=bank_facts, n_chunk=n_chunk, x_g=x_g_facts,
                              x_g_not_run_reason=why, printed=printed)
        result["n_chunk_formula_recorded"] = (step.get("slot_detail") or {}).get("N_chunk_formula")
        finish(doc)
    except BaseException as exc:
        if "evaluation" not in result and "error" not in result:
            finish(error=f"{type(exc).__name__}: {exc}")
        raise
    if not doc["pass"]:
        raise ValueError(f"Part C failed ({doc['verdict']}): {doc['disposition']}")
    return result


def smoke(output, part, runtime, *, soak_reference, invoke=r1._invoke):
    """Native only when explicitly run by the lead in an agent-free session.

    B runs the same admission followed by the D step, in one member. Its
    inventory process spans idle/quiet/load/recovery. A stops after G0.
    C (RL-145 addendum) runs the gated D_bank (and X_G) behind a full step-D.
    """
    reg.verify_r1_executed_sources(ROOT, {"executed_commit": r1.executed_commit(ROOT)})
    gate = "joulewise/align/apple/thermal_gates.py"
    if (ROOT / gate).read_bytes() != reg._committed_bytes(ROOT, "82c14c9ea", [gate])[gate]:
        raise ValueError("smoke requires W1's exact thermal gate module")
    config_path = r1.runtime_config_path(runtime)
    if config_path.read_bytes() != (ROOT / r1.DEFAULT_RUNTIME_CONFIG).read_bytes():
        raise ValueError("condition 13: smoke config differs from the bound runtime config")
    config, _ = rt.load_config(config_path)
    if part == "C":
        return smoke_part_c(output, runtime, config, soak_reference=soak_reference, invoke=invoke)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    predecessor = invoke(runtime, "capture-predecessor-30b", output / "capture_predecessor_30b",
                         soak_reference=soak_reference)
    if time.monotonic() - started >= rt.SMOKE_ADMISSION_S:
        raise ValueError("Part A exhausted at predecessor; partial smoke is not a pass")
    command = list(runtime) + ["--smoke-part", part, "--smoke-started", str(started)]
    fields = invoke(command, "step-d", output / rt.STEP_D_SEGMENT, soak_reference=soak_reference)
    segment = output / rt.STEP_D_SEGMENT
    receipt = json.loads((segment / "smoke_part_a.json").read_text())
    # Desk authentication through the exact W1 verifier, with the source
    # config digest from completed runtime custody. Never recapture here.
    from joulewise.align.apple.thermal_gates import load_window_reference
    source = segment / fields["bundle"]
    custody = json.loads((segment / rt.CUSTODY_NAME).read_text())
    policy = {"sensors": config["sensors"], "window_reference": {"role": "consume",
        "source_run_id": source.name,
        "source_config_sha256": custody["files"][(Path(fields["bundle"]) / "config.json").as_posix()]}}
    reference, verified = load_window_reference(policy, SimpleNamespace(
        bundle_path=source.parent / "smoke-reference-consumer", run_id="smoke-reference-consumer"))
    if part == "A" and time.monotonic() - started > rt.SMOKE_ADMISSION_S:
        raise ValueError(f"Part A exceeded {rt.SMOKE_ADMISSION_S} s including close; partial smoke is not a pass")
    result = {"part": part, "predecessor": predecessor, "capture_and_gate": receipt, "member": fields,
              "verified_reference": reference, "reference_custody": verified}
    if part == "B":
        result["part_b"] = smoke_table(segment)
        (output / "smoke_part_b.json").write_text(json.dumps(result["part_b"], indent=2, sort_keys=True) + "\n")
    (output / "smoke.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if part == "B" and not result["part_b"]["coverage"]["pass"]:
        raise ValueError("smoke Part B sampler/Tf08 coverage failed; diagnostics saved in smoke_part_b.json")
    if part == "B" and not result["part_b"]["selection"]["ok"]:
        raise ValueError("smoke Part B has no admissible sensor pair; diagnostics saved in smoke_part_b.json")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--sensor-ruling", type=Path, required=True)
    p.add_argument("--smoke-table", type=Path, required=True)
    p = sub.add_parser("smoke")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--part", choices=("A", "B", "C"), required=True)
    p.add_argument("--soak-reference", type=Path, required=True)
    p.add_argument("--inputs", type=Path, default=ROOT / reg.REGISTRATION / "inputs.json")
    p = sub.add_parser("desk")
    p.add_argument("--run-dir", type=Path, required=True)
    p = sub.add_parser("regenerate-table", help="RL-122: re-derive (not re-measure) the Part B selection")
    p.add_argument("--saved-table", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--rule", choices=("rl122", "rl145"), default="rl122",
                   help="rl145: re-derive the RL-122 table's slow key by the alias-group rule")
    args = parser.parse_args(argv)
    if args.command == "prepare":
        prepare(args.output, ruling=json.loads(args.sensor_ruling.read_text()), smoke_table=args.smoke_table)
    elif args.command == "regenerate-table":
        config, _ = rt.load_config(ROOT / r1.DEFAULT_RUNTIME_CONFIG)
        regenerate = regenerate_alias_second_key_table if args.rule == "rl145" else regenerate_second_fast_rule_table
        raw = regenerate(args.saved_table.read_bytes(), config)
        with args.output.open("xb") as handle:
            handle.write(raw)
        print(hashlib.sha256(raw).hexdigest())
    elif args.command == "smoke":
        smoke(args.output, args.part, r1.runtime_argv_from_inputs(args.inputs), soak_reference=args.soak_reference)
    else:
        print(json.dumps(replay.night_desk(args.run_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
