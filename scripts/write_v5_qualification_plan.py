#!/usr/bin/env python3
"""Stage V5 block-4 qualification inputs; this command never arms or launches.

Inputs are a reviewed JSON object, not defaults for the registration's FILLs.
Sizing seconds are prospective source-bound allowances, never bundle timings.
The duration-margin recorder authenticates collected durations and is deliberately
not called on an uncollected pack. No prospective estimator exists in that module.
"""
from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from types import SimpleNamespace
from fractions import Fraction

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness
from joulewise import night_gate, kernel_clock, t0_rehearsal, v5_qualification as q
from joulewise.night_plan_writer import night_plan_mapping, write_night_plan

INPUT_SCHEMA = "joulewise.v5_qualification_inputs.v1"
OUTPUT_SCHEMA = "joulewise.v5_qualification_plan_record.v1"
ARM_ONLY_SCHEMA = "joulewise.v5_qualification_arm_only.v1"
GAMMA = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
DWELL_CAP_S = 2700
FIXED_COMPONENTS = {
    "s1": {"pack_t0", "fixed_settles", "pre_post_calibration", "stage_custody", "terminal_shutdown"},
}
MEMBER_COMPONENTS = {"load", "warmup", "prefill", "forced_decode", "cooldown", "idle_admission"}


class QualificationError(ValueError):
    pass


def require(condition, field):
    if not condition:
        raise QualificationError(field)


def exact(value, keys, field):
    require(isinstance(value, dict) and set(value) == set(keys), field + ".keys")
    return value


def no_fill(value):
    if isinstance(value, str):
        require("FILL" not in value, "unresolved_fill")
    elif isinstance(value, dict):
        for key, item in value.items():
            no_fill(key)
            no_fill(item)
    elif isinstance(value, list):
        for item in value:
            no_fill(item)


def safe_path(value, *, exists=True):
    require(isinstance(value, (str, Path)), "path.type")
    path = Path(value)
    require(path.is_absolute() and ".." not in path.parts, "path.absolute")
    require(not any(p.is_symlink() for p in (path, *path.parents)), "path.symlink")
    require(path.resolve(strict=exists) == path, "path.lexical")
    return path


def locator(path):
    path = safe_path(path)
    return {"path": str(path), "sha256": readiness.sha256_bytes(path.read_bytes())}


def read_locator(value):
    exact(value, {"path", "sha256"}, "locator")
    path = Path(value["path"])
    if not path.is_absolute():
        require(".." not in path.parts, "locator.relative_escape")
        path = REPO_ROOT / path
    path = safe_path(path)
    raw = night_gate._pack_bytes(path, "qualification_input", value["sha256"])
    return path, raw


def read_object(path):
    return readiness.parse_json_bytes(safe_path(path).read_bytes())


def create_record(path, value):
    path = safe_path(path, exists=False)
    require(path.parent.is_dir(), "output.parent_missing")
    raw = readiness.render_json(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return locator(path)


def number(value, field):
    require(type(value) in (float, int) and math.isfinite(value) and value >= 0, field)
    return Fraction(value)


def allowance(value):
    exact(value, {"seconds", "source", "source_pointer"}, "allowance")
    _, raw = read_locator(value["source"])
    source = readiness.parse_json_bytes(raw)
    pointer = value["source_pointer"]
    require(isinstance(pointer, str) and pointer.startswith("/"), "allowance.source_pointer")
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        source = source[int(part)] if isinstance(source, list) else source[part]
    require(type(source) in (int, float) and source == value["seconds"], "allowance.source_value")
    return number(value["seconds"], "allowance.seconds")


def sizing_adapter(value):
    """Read the durable sizing-seat adapter without charging desk controls to the night."""
    if value.get("schema_version") != "joulewise.v5_qualification_sizing_allowances.v1":
        return value
    exact(value, {"schema_version", "sizing", "totals", "controls"}, "sizing_adapter")
    for group in ("totals", "controls"):
        require(isinstance(value[group], dict) and bool(value[group]), "sizing_adapter." + group)
        for item in value[group].values():
            allowance(item)
    return value["sizing"]


def size_window(occurrence, sizing, *, roster=(), auxiliary=(), brackets=(), nonsampling=()):
    """Component arithmetic follows block-3's prospective allowance method.

    Require every component, including model load/admission and every auxiliary
    stage. This does not assert a hard latency bound for unbounded inference.
    """
    require(occurrence in {"a1", "a2", "s1", "s2"}, "occurrence_retired_or_invalid")
    source_stream_max = (allowance(sizing["totals"]["T_stream_max"])
                         if sizing.get("schema_version") == "joulewise.v5_qualification_sizing_allowances.v1"
                         else Fraction())
    sizing = sizing_adapter(sizing)
    occurrence = "s1"
    exact(sizing, {"fixed", "members", "auxiliary", "streams", "clock"}, "sizing")
    exact(sizing["fixed"], FIXED_COMPONENTS[occurrence] | {"t0_stage_cap"}, "fixed")
    stage_cap = allowance(sizing["fixed"]["t0_stage_cap"])
    require(3180 <= stage_cap <= 3480, "t0_stage_cap_band")
    # The six captures (including the one dwell) precede the programmed chain;
    # pack_t0 covers only post-stage authoring, verification and consuming start.
    total = sum((allowance(v) for key, v in sizing["fixed"].items()
                 if key != "t0_stage_cap"), Fraction())
    members = sizing["members"]
    require(isinstance(members, dict), "members")
    require(set(members) == {r["run_id"] for r in roster}, "member_inventory")
    for value in members.values():
        exact(value, MEMBER_COMPONENTS, "member_components")
        total += sum((allowance(v) for v in value.values()), Fraction())
    require(isinstance(sizing["auxiliary"], dict), "auxiliary")
    require(set(sizing["auxiliary"]) == set(auxiliary), "auxiliary_inventory")
    total += sum((allowance(v) for v in sizing["auxiliary"].values()), Fraction())
    span = math.ceil(total)
    require(span > 0, "programmed_span")
    window = 60 * math.ceil((span + stage_cap) / 60)
    clock = exact(sizing["clock"], {"diagnostic_anchor_half_width_s", "stamp_resolution_s", "rho_per_s", "source", "observed_max_effective_bound"}, "clock")
    _, clock_raw = read_locator(clock["source"])
    clock_source = readiness.parse_json_bytes(clock_raw)
    # Raw sizing inputs retain the same production maximum through their
    # authenticated clock source, even without the outer allowance adapter.
    source_stream_max = max(source_stream_max, number(
        clock_source.get("totals", {}).get("T_stream_max", 0), "clock.source_stream_max"))
    require(all(clock_source[key] == clock[key] for key in (
        "diagnostic_anchor_half_width_s", "stamp_resolution_s", "rho_per_s")), "clock.source_values")
    from joulewise.uncertainty_evidence import NUMERIC_PADDING_S, _round_outward_up
    # v3 effective = anchor-only + stamp resolution + numeric padding + offset
    # span. rho*T estimates that span ONCE. It is not added again to an already
    # effective bound; exact Fractions/outward rounding match the estimator.
    placement = (number(clock["diagnostic_anchor_half_width_s"], "clock.h")
                 + number(clock["stamp_resolution_s"], "clock.resolution")
                 + Fraction(NUMERIC_PADDING_S))
    rho = number(clock["rho_per_s"], "clock.rho")
    streams = sizing["streams"]
    require(isinstance(streams, dict), "streams")
    # nonsampling names whole auxiliary stages without a clock anchor (bound
    # derivation). Cooldown subwindows and the post-run sentinel are helpers
    # inside a member, not extra anchor-bearing roster entries.
    require(set(nonsampling) <= set(auxiliary), "nonsampling_inventory")
    sampled_auxiliary = set(auxiliary) - set(nonsampling)
    require(set(streams) == (set(members) | sampled_auxiliary | set(brackets)), "stream_inventory")
    stream_seconds = {name: allowance(v) for name, v in streams.items()}
    require(all(seconds >= 60 for seconds in stream_seconds.values()), "anchor_stream_minimum")
    longest = max(stream_seconds.values(), default=Fraction())
    require(longest >= source_stream_max, "source_stream_maximum_omitted")
    for member_id, components in members.items():
        # Load precedes startup. The main sampler stops at
        # joulewise/controller.py:1607; cooldown runs on its own sampler.
        # Admission guards/retry remain covered by the anchor-bearing stream.
        sampled = sum((allowance(v) for key, v in components.items()
                       if key not in {"load", "cooldown"}), Fraction())
        require(stream_seconds[member_id] >= sampled, "stream_omits_guard_or_retry")
    # Bracket protocol spans are already included in pre_post_calibration;
    # their continuous sampler streams still need the independent clock check.
    effective = _round_outward_up(placement + rho * longest)
    observed = allowance(clock["observed_max_effective_bound"])
    require(observed <= Fraction(0.005), "clock_bound_exceeded")
    return {"programmed_span_s": span, "window_max_s": window,
            "t0_stage_cap_s": float(stage_cap),
            "pack_t0_s": float(allowance(sizing["fixed"]["pack_t0"])),
            "remaining_chain_span_s": float(span - allowance(sizing["fixed"]["pack_t0"])),
            "clean_dwell_cap_s": DWELL_CAP_S,
            "longest_sampler_stream_s": float(longest),
            "worst_case_effective_clock_bound_s": effective,
            "observed_max_effective_clock_bound_s": float(observed),
            "clock_admission_limit_s": 0.005,
            "clock_design_margin_s": float(Fraction(0.005) - observed),
            "clock": {key: clock[key] for key in (
                "diagnostic_anchor_half_width_s", "stamp_resolution_s", "rho_per_s", "source", "observed_max_effective_bound")},
            "numeric_padding_s": NUMERIC_PADDING_S,
            "estimate_only": True}


def pack_roster(root, occurrence):
    tree, _ = readiness._plan_tree(root)
    no_fill(tree)
    inventory = readiness._authenticated_pack_config_inventory(root)
    for relative, digest in inventory.items():
        night_gate._pack_bytes(safe_path(root / relative), "config_inventory", digest)
    require(root.name == GAMMA, "real_gamma_required")
    science = tree.get("science")
    require(isinstance(science, list) and len(science) == 80, "partial_gamma_pack")
    first = science[:4]
    require([r.get("position") for r in first] == ["A1", "B1", "B2", "A2"], "first_abba")
    require([r.get("arm") for r in first] == ["A", "B", "B", "A"], "first_abba")
    require(len({r.get("stage_id") for r in first}) == 1 and len({r.get("block_id") for r in first}) == 1, "first_block")
    stage = safe_path(root / first[0]["config_path"]).parent
    from scripts.run_campaign import load_order_entries, apply_order_manifest, discover_configs
    entries, warning = load_order_entries(stage)
    require(warning is None and len(entries) == 20, "authentic_first_stage")
    ordered = apply_order_manifest(discover_configs(stage), entries)
    require([p.relative_to(root).as_posix() for p in ordered[:4]] == [r["config_path"] for r in first], "first_stage_order")
    for row in science:
        require(inventory.get(row["config_path"]) == row["config_sha256"], "science_config_inventory")
    graph = tree.get("stage_graph")
    require(isinstance(graph, list) and graph, "stage_graph")
    dispatched = dispatched_stages(root, graph, first[0]["stage_id"])
    auxiliary = [r["stage_id"] for r in dispatched if r["stage_id"] != first[0]["stage_id"]
                 and r.get("kind") in {"campaign_collection", "bound_derivation"}]
    require(auxiliary and len(auxiliary) == len(set(auxiliary)), "auxiliary_roster")
    brackets = [r["stage_id"] for r in dispatched if r.get("kind") == "calibration_capture"]
    require(len(brackets) == 2 and len(set(brackets)) == 2, "bracket_stream_roster")
    nonsampling = [r["stage_id"] for r in dispatched if r.get("kind") == "bound_derivation"]
    return [{k: r[k] for k in ("run_id", "config_path", "config_sha256", "stage_id", "block_id", "position", "arm")} for r in first], auxiliary, brackets, nonsampling


def dispatched_stages(root, graph, science_stage):
    """Resolve dispatches in the rendered one-block chain against the frozen graph.

    Repeated reference paths resolve in graph order: only the first midpoint is
    dispatched. An unused graph row does not contribute a sizing allowance.
    """
    body = g2b_body(readiness._repo_for_pack(root))
    logical = body.replace("\\\n", " ")
    bindings = {"REPO": ""}
    for name, value in re.findall(r'^(?:export )?([A-Z_]+)="([^"\n]+)"$', logical, re.M):
        if name == "REPO":
            continue  # dispatch graph paths are repository-relative
        for key, bound in bindings.items():
            value = value.replace("$" + key, bound)
        bindings[name] = value
    dispatches = []
    require(logical.count('\ncd "$REPO"\n') == 1, "g2b_dispatch_start")
    for line in logical.split('\ncd "$REPO"\n', 1)[1].splitlines():
        line = line.strip()
        if line.startswith('run_stage '):
            argv = shlex.split(line)
            config = argv[3]
            if config == "$REPO/$stage":
                require("--max-blocks 1" in line and 'before_midpoint_stages.txt' in body
                        and '  break\n' in body, "one_block_dispatch")
                dispatches.append(("science", science_stage))
            else:
                for key, value in bindings.items():
                    config = config.replace("$" + key, value)
                require("$" not in config, "unresolved_dispatch_path")
                dispatches.append(("config", config.lstrip("/")))
        elif line.startswith('"$PY" "$REPO/scripts/run_campaign.py"') and '--derive-neg8-drift-bound' in line:
            dispatches.append(("kind", "bound_derivation"))
        elif re.match(r'^(PRE|POST)_CAL_CUSTODY=', line):
            slot = re.search(r'calibrate_slot (pre|post) ', line)
            require(slot is not None, "calibration_dispatch")
            dispatches.append(("slot", slot[1] + "_attempt_id"))
    require(len(dispatches) == 8, "g2b_dispatch_inventory")
    selected, cursor = [], 0
    for kind, value in dispatches:
        matches = []
        for index, row in enumerate(graph[cursor:], cursor):
            paths = [arg.get("value") for command in row.get("launch", {}).get("commands", [])
                     for arg in command.get("argv_template", {}).get("arguments", [])
                     if arg.get("kind") == "repo_path"]
            # GAMMA-INTERIOR-REFERENCES-01 (lane L10): GAMMA's first interior reference stage now
            # launches a run-id-only copy of the shared midpoint config (gamma_interior_references_v5/),
            # and the shared midpoint runs at the arm boundary. The one-block chain's midpoint dispatch
            # still sits after block 1, so it resolves to that first interior stage by stage id; its
            # member is the same config and class, so the sizing is unchanged.
            match = (row.get("stage_id") == value if kind == "science" else
                     (value in paths or (value.endswith("/midpoint")
                                         and row.get("stage_id") == "gamma-reference-decode-midpoint"))
                     if kind == "config" else
                     row.get("kind") == value if kind == "kind" else
                     row.get("kind") == "calibration_capture" and row.get("input_ref", {}).get("slot") == value)
            if match:
                matches.append((index, row))
        require(bool(matches), "dispatched_stage_missing")
        index, row = matches[0]
        require(row["stage_id"] not in {"gamma-reference-arm-boundary", "gamma-reference-prefill-midpoint"},
                "dispatched_stage_missing")
        if kind == "config" and value.endswith("/midpoint"):
            require(not any(item.get("input_ref", {}).get("kind") == "pack_manifest"
                            for item in graph[cursor:index]), "dispatched_stage_missing")
        selected.append(row)
        cursor = index + 1
    return selected


def backup_destinations(context):
    result = {name: str(safe_path(context[name + "_backup_destination"], exists=False))
              for name in ("claim", "bound")}
    paths = [Path(value) for value in result.values()]
    require(paths[0] != paths[1] and paths[0] not in paths[1].parents
            and paths[1] not in paths[0].parents, "backup_destinations_overlap")
    for destination in paths:
        for source in (context["custody_root"], context["claim_runs_root"], context["bound_runs_root"]):
            source = Path(source)
            require(destination != source and destination not in source.parents
                    and source not in destination.parents, "backup_source_destination_overlap")
    return result


def g2b_body(measurement):
    from scripts.gen_g2_phase_d import render_generated_region, END_MARKER
    import inspect
    options = ({"v5_references": True} if "v5_references" in
               inspect.signature(render_generated_region).parameters else {})
    generated = render_generated_region((measurement / "docs/phase_2/window_runbook.md").read_text(), **options)
    body = generated.split("<!-- GENERATED by scripts/gen_g2_phase_d.py from the pinned runbook chain. -->\n", 1)[1].split(END_MARKER)[0]
    require(body.startswith("```zsh\n") and body.endswith("```\n"), "g2b_source_fences")
    body = body[len("```zsh\n"):-len("```\n")]
    # The authenticated v3 consumption is the child authority. The generator's
    # explicit flags assume inherited confirmation variables, which the D-176
    # environment rule forbids. Its child already supports omission of the pair.
    old = ('  --lifecycle-event start \\\n'
           '  --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \\\n'
           '  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"\n')
    require(body.count(old) == 1, "g2b_consumption_interface_drift")
    # One reviewed specialization, before canonical-body validation and hashing.
    # Capture and the evidence author require the executing checkout's literal.
    repo_binding = "REPO=/Users/edr/JouleWise-measurement-20260813\n"
    require(body.count(repo_binding) == 1, "g2b_repo_binding_drift")
    repository = str(measurement.resolve())
    status_call = '"$REPO/scripts/recover_calibration_ledger.py" session-status \\\n'
    require(body.count(status_call) == 1, "g2b_ledger_binding_drift")
    body = body.replace(status_call, '"$REPO/scripts/recover_calibration_ledger.py" \\\n'
                        '    --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" session-status \\\n')
    require(not any(char in repository for char in "\n\r\"$`\\"), "g2b_repo_binding_invalid")
    return body.replace(old, "  --lifecycle-event start\n").replace(repo_binding, 'REPO="' + repository + '"\n')


def render_qualification_chain(occurrence, template, sizing, root, t0_epoch_s, output, *, arm_context=None):
    """Emit exact sizing literals and a chain sidecar before authorization.

    Templates are reviewed, fully bound shell bytes. s1 must contain the complete
    canonical #474 body (with confirmation supplied by consumption). No subset
    pack or guessed role/stage duration is generated here.
    """
    root = safe_path(root)
    require(occurrence in {"s1", "s2"}, "occurrence_retired_or_invalid")
    template = safe_path(template)
    text = template.read_text()
    no_fill(text)
    require(not re.search(r"(?m)^\s*(?:export\s+)?TRANSCRIPT_ROOT\s*=", text), "transcript_root_override")
    roster, auxiliary, brackets, nonsampling = pack_roster(root, occurrence)
    sized = size_window(occurrence, sizing, roster=roster, auxiliary=auxiliary, brackets=brackets, nonsampling=nonsampling)
    if occurrence in {"s1", "s2"}:
        require(g2b_body(readiness._repo_for_pack(root)) in text, "reviewed_g2b_chain_required")
    require(not re.search(r"(?:export\s+)?(?:EXPECTED_CONFIRMATION_DIGEST|STEP6_CONFIRMATION_TABLE)\s*=", text), "confirmation_environment_route")
    for name in ("NIGHT_PROGRAMMED_SPAN_S", "NIGHT_LATEST_CHAIN_START_EPOCH_S"):
        require(not re.search(r"(?m)^(?:export )?" + name + "=", text), "duplicate_span_literal")
    number(t0_epoch_s, "t0_epoch_s")
    latest = math.floor(t0_epoch_s + sized["t0_stage_cap_s"] + sized["pack_t0_s"])
    output = safe_path(output, exists=False)
    require(bool(roster), "first_stage_required")
    stage = (root / roster[0]["config_path"]).parent.relative_to(readiness._repo_for_pack(root)).as_posix()
    stage_path = output.parent / "before_midpoint_stages.txt"
    stage_raw = (stage + "\n").encode()
    stage_hash = readiness.sha256_bytes(stage_raw)
    require(not stage_path.exists() and not stage_path.is_symlink(), "stage_list_create_once")
    context_prefix = ""
    if arm_context is not None:
        context = readiness.validate_arm_context(arm_context)
        context_prefix = f"export NIGHT_ARM_CONTEXT_SHA256={readiness.sha256_bytes(readiness.render_json(context))}\n"
    prefix = ("#!/bin/zsh\nset -e\n"
              f"export NIGHT_PROGRAMMED_SPAN_S={sized['programmed_span_s']}\n"
              f"export NIGHT_CLOCK_STREAM_MAX_S={sized['longest_sampler_stream_s']}\n"
              f"export NIGHT_CLOCK_SIZING_SHA256={readiness.sha256_bytes(readiness.render_json(sizing))}\n"
              f"export NIGHT_LATEST_CHAIN_START_EPOCH_S={latest}\n"
              f"export V5_QUALIFICATION_OCCURRENCE={occurrence}\n"
              + context_prefix
              + ': "${NIGHT_DIR:?}"\nexport TRANSCRIPT_ROOT="$NIGHT_DIR/transcript"\n'
              '/bin/mkdir -p "$TRANSCRIPT_ROOT"\n'
              f'test "$(/usr/bin/shasum -a 256 "$1/before_midpoint_stages.txt" | /usr/bin/awk \'{{print $1}}\')" = "{stage_hash}"\n'
              'test "$(/bin/date +%s)" -le "$NIGHT_LATEST_CHAIN_START_EPOCH_S"\n')
    sidecar = safe_path(str(output) + ".sha256", exists=False)
    require(not output.exists() and not sidecar.exists(), "chain_create_once")
    raw = (prefix + text).encode()
    with stage_path.open("xb") as stream:
        os.chmod(stage_path, 0o600)
        stream.write(stage_raw)
    with output.open("xb") as stream:
        os.chmod(output, 0o600)
        stream.write(raw)
    with sidecar.open("xb") as stream:
        os.chmod(sidecar, 0o600)
        stream.write(readiness.gnu_sidecar(readiness.sha256_bytes(raw), output.name))
    return {"status": "STAGED", "chain": locator(output), "sidecar": locator(sidecar),
            "before_midpoint_stages": locator(stage_path),
            "terminal_boundary": "$NIGHT_DIR/transcript/post-bracket-terminal-boundary.json",
            "programmed_span_s": sized["programmed_span_s"], "window_max_s": sized["window_max_s"],
            "latest_chain_start_epoch_s": latest}


def deadlines(plan, span, declared, *, sizing=None):
    from scripts.run_night import COURIER_DEADLINE_S, WINDOW_SHUTDOWN_GRACE_S, deadman_epoch
    exact(declared, {"latest_chain_start_epoch_s", "shutdown_epoch_s", "courier_epoch_s", "deadman_epoch_s"}, "deadlines")
    end = plan.t0_epoch_s + plan.window_max_s
    latest = (math.floor(plan.t0_epoch_s + sizing["t0_stage_cap_s"] + sizing["pack_t0_s"])
              if sizing is not None else end - span)
    computed = {"latest_chain_start_epoch_s": latest,
                "shutdown_epoch_s": end + WINDOW_SHUTDOWN_GRACE_S,
                "courier_epoch_s": end + WINDOW_SHUTDOWN_GRACE_S + COURIER_DEADLINE_S,
                "deadman_epoch_s": deadman_epoch(plan)}
    require(plan.t0_epoch_s <= declared["latest_chain_start_epoch_s"] <= computed["latest_chain_start_epoch_s"], "latest_chain_start")
    for key in ("shutdown_epoch_s", "courier_epoch_s", "deadman_epoch_s"):
        number(declared[key], "deadlines." + key)
        require(declared[key] == computed[key], "deadlines." + key)
    require(end <= computed["shutdown_epoch_s"] <= computed["courier_epoch_s"] < computed["deadman_epoch_s"], "deadline_order")
    return declared


def prerequisites(occurrence, references, head, t0_sequence_start, custody, *, code_root=None):
    expected = (set() if occurrence == "a1" else {"a1_control"} if occurrence == "a2" else
                {"a1_control", "a2_control", "observation_producers", "g10_control", "g10_artifacts"})
    exact(references, expected, "prerequisites")
    if occurrence in {"s1", "s2"}:
        from joulewise import t0_rehearsal as t0
        exact(references["observation_producers"], {"driver", "bundle", "evaluator"}, "observation_producers")
        for name, suffix in (("driver", "scripts/run_night.py"), ("bundle", "scripts/produce_t0_rehearsal_bundle.py"),
                             ("evaluator", "joulewise/t0_rehearsal.py")):
            path, _ = read_locator(references["observation_producers"][name])
            require(path.as_posix().endswith("/" + suffix), "observation_producer_path")
        _, raw = read_locator(references["g10_control"])
        positive = readiness.parse_json_bytes(raw)
        exact(positive, t0._POSITIVE_CONTROL_KEYS, "g10_control")
        require(positive["schema_version"] == t0.POSITIVE_CONTROL_SCHEMA
                and positive["performed_by"] == "Ed"
                and all(positive[key] is True for key in ("outside_t0_sequence", "network_time_reenabled", "forced_resync"))
                and type(positive["anchor_before_ns"]) is int and type(positive["anchor_after_ns"]) is int
                and positive["author_refusal_reason_code"] == "evidence_author_t0_clock_attestation_underivable", "g10_control_not_pass")
        require(isinstance(references["g10_artifacts"], list) and len(references["g10_artifacts"]) == 1,
                "g10_custody_manifest_required")
        for ref in references["g10_artifacts"]:
            read_locator(ref)
    controls = {}
    for label in ("a1", "a2"):
        if label + "_control" not in expected:
            continue
        from scripts.check_v5_arm_abort import ABSENCE_KEYS, CONTROL_SCHEMA
        _, raw = read_locator(references[label + "_control"])
        control = readiness.parse_json_bytes(raw)
        exact(control["absence"], ABSENCE_KEYS, "a1_absence")
        require(control["schema_version"] == CONTROL_SCHEMA and control["occurrence"] == label and control["verdict"] == "PASS"
                and control["refusal_reason_code"] == "readiness_record_expired"
                and control["checked_epoch_s"] < t0_sequence_start
                and control["ordering"]["expired_before_s1_t0"] is True
                and all(value is True for value in control["absence"].values()), "a1_control_not_pass_or_ordered")
        context_path, _ = read_locator(control["context"])
        context = read_object(context_path)
        require(context["head"] == head, "a1_wrong_head")
        require(context_path.parent != custody and custody not in context_path.parent.parents
                and context_path.parent not in custody.parents, "prerequisite_custody_overlap")
        for ref in [control["arm_receipt"], control["observation"], *control["sources"]]:
            read_locator(ref)
        controls[label] = control
    if occurrence in {"s1", "s2"}:
        from scripts.ed_session.capture_t0_anchor_positive_control import verify_g10_custody
        positive_path, _ = read_locator(references["g10_control"])
        manifest_path, _ = read_locator(references["g10_artifacts"][0])
        writer_boot = readiness._current_boot_session_id().lower()
        verify_g10_custody(positive_path, manifest_path, code_root=code_root or REPO_ROOT, head=head,
            after_monotonic_ns=controls["a2"]["checked_monotonic_ns"],
            before_monotonic_ns=time.monotonic_ns(), boot_id=writer_boot)
        _, raw = read_locator(controls["a2"]["observation"])
        observation = readiness.parse_json_bytes(raw)
        require(controls["a1"]["checked_monotonic_ns"] < observation["first_t0_boundary_monotonic_ns"]
                and controls["a1"]["boot_session_id"] == controls["a2"]["boot_session_id"], "a1_before_a2_t0")
        require(controls["a2"]["boot_session_id"].lower() == writer_boot, "g10_boot_or_order")


def authenticate_frozen_pack(root, confirmation):
    tree, _ = readiness._plan_tree(root)
    registry, _, registry_reference = readiness._registry_reference(root)
    _, reference = readiness._load_freeze_reference(
        root, tree, registry_reference, registry, require_pass=True,
        step6_confirmation_table=confirmation["table_path"],
        expected_confirmation_digest=confirmation["table_sha256"])
    path = safe_path(root / reference["path"])
    require(locator(path)["sha256"] == reference["sha256"], "freeze_reference_digest")
    return locator(path)


def write_qualification(occurrence, inputs, output, *, g10_inputs=False):
    require(not g10_inputs or occurrence == "a1", "g10_sizing_route")
    require(occurrence in {"a1", "a2", "s1", "s2"}, "occurrence_retired_or_invalid")
    keys = {"schema_version", "head", "plan", "pack", "authorization", "confirmation", "sizing", "deadlines", "other_custody_roots", "arm_context", "prerequisites", "kernel_frequency"}
    if occurrence in {"s1", "s2"}:
        keys |= {"previous_attempt", "block_archive_root"}
        if "null_reservation_restore" in inputs:
            keys.add("null_reservation_restore")
    if occurrence == "s2":
        keys.add("s2_authority")
    exact(inputs, keys, "inputs")
    require(inputs["schema_version"] == INPUT_SCHEMA, "inputs.schema")
    no_fill(inputs)
    base = dict(inputs["plan"])
    require(base["repo_head"] == base["measurement_head"] == inputs["head"], "wrong_head")
    measurement = safe_path(base["measurement_root"])
    head = subprocess.check_output(["git", "-C", str(measurement), "rev-parse", "HEAD"], text=True).strip()
    require(head == inputs["head"], "checkout_head")
    custody = safe_path(base["custody_root"])
    output = safe_path(output, exists=False)
    require(output.parent == custody and not output.exists(), "output_custody_or_exists")
    require(not list(custody.rglob("*.consumed.json")) and not list(custody.rglob("chain.started")), "custody_used")
    for other in inputs["other_custody_roots"]:
        other = safe_path(other, exists=False)
        require(custody != other and custody not in other.parents and other not in custody.parents, "custody_overlap")
    exact(inputs["pack"], {"root", "sha256", "attempt_ordinal"}, "pack")
    root = safe_path(inputs["pack"]["root"])
    require(readiness._repo_for_pack(root) == measurement, "pack_checkout")
    digest = readiness.committed_pack_tree_sha256(root)
    require(digest == inputs["pack"]["sha256"], "pack_digest")
    frozen_identity = readiness._pack_record(root)
    if occurrence in {"a1", "a2"}:
        require(base["plan_id"] == frozen_identity["plan_id"], "frozen_plan_id")
    roster, auxiliary, brackets, nonsampling = pack_roster(root, occurrence)
    sizing = size_window(occurrence, inputs["sizing"], roster=roster, auxiliary=auxiliary, brackets=brackets, nonsampling=nonsampling)
    gate = kernel_clock.frequency_gate(inputs["kernel_frequency"], sizing["longest_sampler_stream_s"])
    if not gate["passes"]:
        refusal = QualificationError("kernel_frequency_gate_exceeded")
        refusal.kernel_frequency_gate = gate
        raise refusal
    sizing["kernel_frequency_gate"] = gate
    require(base["window_max_s"] == sizing["window_max_s"], "window_max")
    chain = safe_path(base["chain_path"])
    text = chain.read_text()
    no_fill(text)
    require(night_gate.chain_literal(text, "NIGHT_PROGRAMMED_SPAN_S") == str(sizing["programmed_span_s"]), "chain_span_literal")
    require(night_gate.chain_literal(text, "NIGHT_CLOCK_STREAM_MAX_S") == str(sizing["longest_sampler_stream_s"]), "chain_stream_literal")
    require(night_gate.chain_literal(text, "NIGHT_CLOCK_SIZING_SHA256") ==
            readiness.sha256_bytes(readiness.render_json(inputs["sizing"])), "chain_sizing_literal")
    require(not re.search(r"(?:export\s+)?(?:EXPECTED_CONFIRMATION_DIGEST|STEP6_CONFIRMATION_TABLE)\s*=", text), "confirmation_environment_route")
    require(g2b_body(measurement) in text, "reviewed_g2b_chain_required")
    purpose = "G2B_SHAKEDOWN"
    auth = dict(inputs["authorization"])
    auth_keys = {"purpose", "attempt_id", "claim_eligible", "pack_sha256", "permitted_chain_sha256", "permitted_blocks", "authority"}
    if occurrence in {"s1", "s2"}:
        night_gate.validate_attempt_bindings(inputs["previous_attempt"], inputs["block_archive_root"],
                                           inputs.get("null_reservation_restore"))
        require(night_gate.chain_literal(text, "V5_QUALIFICATION_OCCURRENCE") == occurrence, "chain_occurrence")
        for name in ("previous_attempt", "block_archive_root", "null_reservation_restore"):
            if name in inputs:
                require(name not in auth or auth[name] == inputs[name], "authorization_history_binding")
                require(name not in base or base[name] == inputs[name], "plan_history_binding")
                auth[name] = base[name] = inputs[name]
                auth_keys.add(name)
        q.previous_attempt(inputs["previous_attempt"])
        safe_path(inputs["block_archive_root"])
        # The create-once pointer and census are checked before publishing authority.
        provisional = {"schema": q.ATTEMPT_HARVEST_SCHEMA, "plan_id": base["plan_id"],
                       "previous_attempt": inputs["previous_attempt"], "occurrence": occurrence,
                       "block_archive_root": inputs["block_archive_root"], "verdict": "REFUSED"}
        # A proposed s2 must fit the allowance before authority is published.
        # An actual NULL harvest still spends neither allowance in replay.
        # The new plan is not yet published; authenticate all existing links.
        history = q.attempt_history(provisional, inputs["block_archive_root"])
        for ref in history["harvests"]:
            q.authenticate_attempt_record(q.read(q.authenticated_reference(ref)), Path(inputs["block_archive_root"]))
        if occurrence == "s2":
            q.authenticate_s2_authority(inputs["s2_authority"], base["plan_id"], inputs["previous_attempt"])
        q.verify_attempt_restore(SimpleNamespace(**{**base, "null_reservation_restore": inputs.get("null_reservation_restore")}), writer=True)
    require(auth.get("purpose") == purpose and auth.get("claim_eligible") is False and auth.get("permitted_blocks") == 1, "purpose_claim_blocks")
    require(not frozen_identity["window_id"].startswith("rehearsal-t0-unattended-"), "window_prefix")
    auth_path = custody / "authorization_record.json"
    confirm_path = custody / "step6_confirmation_record.json"
    require(not auth_path.exists() and not confirm_path.exists(), "create_once_records")
    confirmation_input = exact(inputs["confirmation"], {"record", "transcript", "expected_confirmation_digest"}, "confirmation_input")
    _, raw = read_locator(confirmation_input["record"])
    confirmation = readiness.parse_json_bytes(raw)
    _, transcript = read_locator(confirmation_input["transcript"])
    require(confirmation["transcript_sha256"] == readiness.sha256_bytes(transcript), "confirmation_transcript")
    expected = confirmation_input["expected_confirmation_digest"]
    require(confirmation["table_sha256"] == expected and expected.encode() in transcript, "independent_confirmation_digest")
    require(expected not in text, "confirmation_chain_literal")
    # The same table parser as freeze/ARM; expected hC comes from prior custody.
    readiness._authenticate_confirmation_table(confirmation["table_path"], expected)
    frozen = authenticate_frozen_pack(root, confirmation)
    records = {"authorization_record": {"path": str(auth_path), "sha256": readiness.sha256_bytes(readiness.render_json(auth))},
               "confirmation_record": {"path": str(confirm_path), "sha256": readiness.sha256_bytes(readiness.render_json(confirmation))}}
    base.update(schema=night_gate.PACK_PLAN_SCHEMA, schema_version=3, receipt_class="TRANSACTION_PACK",
                pack_night={"pack_id": root.name, "pack_root": str(root), "pack_sha256": digest,
                            "attempt_ordinal": inputs["pack"]["attempt_ordinal"], **records})
    plan = night_gate.NightPlan.from_mapping(base)
    bound_deadlines = deadlines(plan, sizing["programmed_span_s"], inputs["deadlines"], sizing=sizing)
    chain_deadline = night_gate.qualification_start_deadline(plan, text, purpose, sizing=inputs["sizing"])
    require(chain_deadline is not None and chain_deadline == bound_deadlines["latest_chain_start_epoch_s"], "qualification_chain_deadline")
    # Authenticate exact records and sidecar with canonical preparation before
    # publishing a plan. A refused attempt retains its create-once authority
    # bytes; it cannot be quietly rewritten and retried in the same custody.
    require(auth.get("attempt_id") == f"{plan.plan_id}/{plan.pack_night['attempt_ordinal']}", "attempt_id")
    require(auth.get("pack_sha256") == digest and auth.get("permitted_chain_sha256") == readiness.sha256_bytes(chain.read_bytes()), "authorization_bindings")
    exact(auth, auth_keys, "authorization")
    context = readiness.validate_arm_context(inputs["arm_context"])
    arm_root = safe_path(context["custody_root"])
    require(arm_root != custody and arm_root not in custody.parents and custody not in arm_root.parents,
            "arm_context.custody_roots_overlap")
    require(not any(arm_root.iterdir()), "arm_context.root_not_fresh")
    require(night_gate.chain_literal(text, "NIGHT_ARM_CONTEXT_SHA256") ==
            readiness.sha256_bytes(readiness.render_json(context)), "arm_context.pin")
    for key, value in context.items():
        if key.endswith("root") or key.endswith("path"):
            safe_path(value, exists=False)
    destinations = backup_destinations(context)
    for value in destinations.values():
        destination = Path(value)
        require(destination != custody and destination not in custody.parents
                and custody not in destination.parents, "backup_plan_custody_overlap")
    prerequisites(occurrence, inputs["prerequisites"], inputs["head"],
                  plan.t0_epoch_s - sizing["t0_stage_cap_s"], custody,
                  code_root=measurement)
    if occurrence in {"s1", "s2"}:
        for name, relative in (("driver", "scripts/run_night.py"), ("bundle", "scripts/produce_t0_rehearsal_bundle.py"),
                               ("evaluator", "joulewise/t0_rehearsal.py")):
            require(inputs["prerequisites"]["observation_producers"][name] == locator(measurement / relative), "observation_producer_checkout")
    create_record(auth_path, auth)
    create_record(confirm_path, confirmation)
    input_root = custody / root.name / "arm_readiness.t0.inputs"
    input_root.mkdir(parents=True, exist_ok=True)
    context_ref = create_record(input_root / "arm-context.json", context)
    create_record(input_root / "kernel-frequency-gate.json", gate)
    night_gate._authenticate_pack_records(plan)
    record = {"schema_version": OUTPUT_SCHEMA, "occurrence": occurrence,
              "head": inputs["head"], "pack_night": plan.pack_night,
              "window_id": frozen_identity["window_id"],
              "freeze_receipt": frozen,
              "science_roster": roster, "auxiliary_roster": auxiliary,
              "calibration_stream_roster": brackets,
              "nonsampling_auxiliary_roster": nonsampling,
              "sizing": sizing, "deadlines": bound_deadlines,
              "input_sha256": readiness.sha256_bytes(readiness.render_json(inputs)),
              "prerequisites": inputs["prerequisites"],
              "arm_context": context_ref,
              "t0_capture_recipe": {"argv": [str(measurement / ".venv/bin/python"),
                  str(measurement / "scripts/capture_t0_step.py"), "sequence",
                  "--pack-root", str(root), "--custody-root", str(custody),
                  "--window-plan-root", str(chain.parent)], "stdin": "/dev/null",
                  "stage": "before_ARM", "steps": ["clock-reference", "clock-disable",
                  "quiet-mac-prep", "prewindow-check", "ledger-readiness", "ledger-reservation"]},
              "backup_destinations": destinations,
              "desk_sources": t0_rehearsal.qualification_backup_sources(custody, context)}
    if occurrence in {"s1", "s2"}:
        record.update(previous_attempt=plan.previous_attempt, block_archive_root=plan.block_archive_root)
        if occurrence == "s2":
            record["s2_authority"] = inputs["s2_authority"]
        record["terminal_boundary_path"] = str(custody / "night/transcript/post-bracket-terminal-boundary.json")
    if occurrence in {"a1", "a2"}:
        record.update(schema_version=ARM_ONLY_SCHEMA, mode="ARM_ONLY_NO_LAUNCH",
                      arm_context=context, plan_binding=night_plan_mapping(plan),
                      recipe={"arm_argv": [str(measurement / ".venv/bin/python"), str(measurement / "scripts/check_v5_arm_abort.py"), "arm", "--context", str(output)],
                              "arm_api": "joulewise.arm_readiness.generate_arm_receipt",
                              "confirmation_record": records["confirmation_record"],
                              "expiry_checker": "scripts/check_v5_arm_abort.py"})
        if g10_inputs:
            # Reuse the full a1 sizing/confirmation checks, but do not create
            # an a1/a2 control context or a launchable night plan.
            record.update(mode="G10_INPUT_CAPTURE_NO_LAUNCH", recipe={
                "capture_argv": record["t0_capture_recipe"]["argv"],
                "author_inputs": str(input_root)})
        create_record(output, record)
    else:
        write_night_plan(output, plan, create_once=True)
        record.update(plan=locator(output), driver_argv=[str(measurement / ".venv/bin/python"), str(measurement / "scripts/run_night.py"), "run", "--plan", str(output)])
        record["observation_recipe"] = {
            "standdown_argv": [str(measurement / ".venv/bin/python"), str(measurement / "scripts/produce_t0_rehearsal_bundle.py"), "observe-standdown", "--plan", str(output), "--timeout-s", "300"],
            "supervised_driver_argv": [str(measurement / ".venv/bin/python"), str(measurement / "scripts/produce_t0_rehearsal_bundle.py"), "run-driver", "--plan", str(output), "--timeout-s", str(plan.window_max_s)],
            "desk_closeout_argv": [str(measurement / ".venv/bin/python"), str(measurement / "scripts/v5_s1_desk_closeout.py"), "--plan", str(output)],
            "desk_closeout_after_quiet_window": True,
            "bundle_manifest": str(custody / "s1-qualification-bundle.json"),
            "positive_control": inputs["prerequisites"]["g10_control"],
            "positive_control_artifacts": inputs["prerequisites"]["g10_artifacts"],
            "timeout_s_required": True}
        create_record(custody / "qualification-plan-record.json", record)
    sizing_ref = create_record(input_root / "kernel-frequency-sizing.json", inputs["sizing"])
    create_record(input_root / "kernel-frequency-binding.json", {
        "schema": "joulewise.v5_qualification_clock_binding.v1", "occurrence": occurrence,
        "plan": locator(output), "sizing": sizing_ref, "plan_id": plan.plan_id,
        "pack_root": str(root), "pack_sha256": digest})
    return {"status": "STAGED", "occurrence": "g10-inputs" if g10_inputs else occurrence, "output": locator(output),
            "kernel_frequency_margin_ms": gate["margin_ms"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="occurrence", required=True)
    for name in ("a1", "a2", "s1", "s2", "g10-inputs"):
        command = commands.add_parser(name)
        command.add_argument("--inputs", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
    render = commands.add_parser("render-chain")
    render.add_argument("--occurrence", dest="render_occurrence", choices=("s1", "s2"), required=True)
    render.add_argument("--template", type=Path, required=True)
    render.add_argument("--sizing", type=Path, required=True)
    render.add_argument("--pack-root", type=Path, required=True)
    render.add_argument("--t0-epoch-s", type=float, required=True)
    render.add_argument("--output", type=Path, required=True)
    render.add_argument("--arm-context", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.occurrence == "render-chain":
            result = render_qualification_chain(args.render_occurrence, args.template,
                read_object(args.sizing), args.pack_root, args.t0_epoch_s, args.output,
                arm_context=read_object(args.arm_context))
        else:
            result = write_qualification("a1" if args.occurrence == "g10-inputs" else args.occurrence,
                read_object(args.inputs), args.output, g10_inputs=args.occurrence == "g10-inputs")
    except QualificationError as exc:
        result = {"status": "REFUSED", "reason_code": "qualification_inputs_invalid"}
        if hasattr(exc, "kernel_frequency_gate"):
            result.update(reason_code="kernel_frequency_gate_exceeded",
                          kernel_frequency_margin_ms=exc.kernel_frequency_gate["margin_ms"],
                          kernel_frequency_gate=exc.kernel_frequency_gate)
        code = 2
    except q.HarvestRefusal as exc:
        result = {"status": "REFUSED", "reason_code": "qualification_inputs_invalid"}
        if str(exc) == "same_refusal_twice_consult_required" and hasattr(exc, "refusal_codes"):
            result.update(reason_code="same_refusal_twice", cause_codes=exc.refusal_codes)
        code = 2
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        # Input text, validator details and inference logs are never public.
        result = {"status": "REFUSED", "reason_code": "qualification_inputs_invalid"}
        code = 2
    else:
        code = 0
    sys.stdout.buffer.write(readiness.render_json(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
