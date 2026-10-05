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
import subprocess
import sys
from fractions import Fraction

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness
from joulewise import night_gate
from joulewise.night_plan_writer import night_plan_mapping, write_night_plan

INPUT_SCHEMA = "joulewise.v5_qualification_inputs.v1"
OUTPUT_SCHEMA = "joulewise.v5_qualification_plan_record.v1"
ARM_ONLY_SCHEMA = "joulewise.v5_qualification_arm_only.v1"
GAMMA = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
DWELL_CAP_S = 2700
FIXED_COMPONENTS = {
    "r1": {"pack_t0", "noninference_chain", "backup_close_restore", "shutdown"},
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
    path = safe_path(value["path"])
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


def size_window(occurrence, sizing, *, roster=(), auxiliary=(), brackets=(), nonsampling=()):
    """Component arithmetic follows block-3's prospective allowance method.

    Require every component, including model load/admission and every auxiliary
    stage. This does not assert a hard latency bound for unbounded inference.
    """
    occurrence = "s1" if occurrence == "a1" else occurrence
    exact(sizing, {"fixed", "members", "auxiliary", "streams", "clock"}, "sizing")
    exact(sizing["fixed"], FIXED_COMPONENTS[occurrence], "fixed")
    total = sum((allowance(v) for v in sizing["fixed"].values()), Fraction())
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
    window = 60 * math.ceil(Fraction(span + DWELL_CAP_S, 60))
    clock = exact(sizing["clock"], {"diagnostic_anchor_half_width_s", "stamp_resolution_s", "rho_per_s", "source"}, "clock")
    _, clock_raw = read_locator(clock["source"])
    clock_source = readiness.parse_json_bytes(clock_raw)
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
    require(set(nonsampling) <= set(auxiliary), "nonsampling_inventory")
    sampled_auxiliary = set(auxiliary) - set(nonsampling)
    require(set(streams) == (set(members) | sampled_auxiliary | set(brackets)), "stream_inventory")
    longest = max((allowance(v) for v in streams.values()), default=Fraction())
    for member_id, components in members.items():
        # Load occurs before sampler startup; every later guarded/retry term is
        # inside the longest stream estimate and must be explicitly covered.
        sampled = sum((allowance(v) for key, v in components.items() if key != "load"), Fraction())
        require(allowance(streams[member_id]) >= sampled, "stream_omits_guard_or_retry")
    # Bracket protocol spans are already included in pre_post_calibration;
    # their continuous sampler streams still need the independent clock check.
    for stage in (*sampled_auxiliary, *brackets):
        require(allowance(streams[stage]) > 0, "auxiliary_stream")
    effective = _round_outward_up(placement + rho * longest)
    require(effective <= 0.005, "clock_bound_exceeded")
    return {"programmed_span_s": span, "window_max_s": window,
            "clean_dwell_cap_s": DWELL_CAP_S,
            "longest_sampler_stream_s": float(longest),
            "prospective_effective_clock_bound_s": effective,
            "clock": {key: clock[key] for key in (
                "diagnostic_anchor_half_width_s", "stamp_resolution_s", "rho_per_s", "source")},
            "numeric_padding_s": NUMERIC_PADDING_S,
            "estimate_only": True}


def pack_roster(root, occurrence):
    tree, _ = readiness._plan_tree(root)
    no_fill(tree)
    inventory = readiness._authenticated_pack_config_inventory(root)
    for relative, digest in inventory.items():
        night_gate._pack_bytes(safe_path(root / relative), "config_inventory", digest)
    if occurrence == "r1":
        require(tree.get("science") == [], "r1_noninference")
        return [], [], [], []
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
    science_stages = {r["stage_id"] for r in science}
    auxiliary = [r["stage_id"] for r in graph if r["stage_id"] not in science_stages
                 and r.get("kind") in {"campaign_collection", "bound_derivation"}]
    require(auxiliary and len(auxiliary) == len(set(auxiliary)), "auxiliary_roster")
    brackets = [r["stage_id"] for r in graph if r.get("kind") == "calibration_capture"]
    require(len(brackets) == 2 and len(set(brackets)) == 2, "bracket_stream_roster")
    nonsampling = [r["stage_id"] for r in graph if r.get("kind") == "bound_derivation"]
    return [{k: r[k] for k in ("run_id", "config_path", "config_sha256", "stage_id", "block_id", "position", "arm")} for r in first], auxiliary, brackets, nonsampling


def g2b_body(measurement):
    from scripts.gen_g2_phase_d import render_generated_region, END_MARKER
    generated = render_generated_region((measurement / "docs/phase_2/window_runbook.md").read_text())
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
    return body.replace(old, "  --lifecycle-event start\n")


def render_qualification_chain(occurrence, template, sizing, root, t0_epoch_s, output):
    """Emit exact sizing literals and a chain sidecar before authorization.

    Templates are reviewed, fully bound shell bytes. s1 must contain the complete
    canonical #474 body (with confirmation supplied by consumption). No subset
    pack or guessed role/stage duration is generated here.
    """
    root = safe_path(root)
    template = safe_path(template)
    text = template.read_text()
    no_fill(text)
    roster, auxiliary, brackets, nonsampling = pack_roster(root, occurrence)
    sized = size_window(occurrence, sizing, roster=roster, auxiliary=auxiliary, brackets=brackets, nonsampling=nonsampling)
    if occurrence == "s1":
        require(g2b_body(readiness._repo_for_pack(root)) in text, "reviewed_g2b_chain_required")
    require(not re.search(r"(?:export\s+)?(?:EXPECTED_CONFIRMATION_DIGEST|STEP6_CONFIRMATION_TABLE)\s*=", text), "confirmation_environment_route")
    for name in ("NIGHT_PROGRAMMED_SPAN_S", "NIGHT_LATEST_CHAIN_START_EPOCH_S"):
        require(not re.search(r"(?m)^(?:export )?" + name + "=", text), "duplicate_span_literal")
    number(t0_epoch_s, "t0_epoch_s")
    latest = math.floor(t0_epoch_s + sized["window_max_s"] - sized["programmed_span_s"])
    prefix = ("#!/bin/zsh\nset -e\n"
              f"export NIGHT_PROGRAMMED_SPAN_S={sized['programmed_span_s']}\n"
              f"export NIGHT_LATEST_CHAIN_START_EPOCH_S={latest}\n"
              f"export V5_QUALIFICATION_OCCURRENCE={occurrence}\n"
              'test "$(/bin/date +%s)" -le "$NIGHT_LATEST_CHAIN_START_EPOCH_S"\n')
    output = safe_path(output, exists=False)
    sidecar = safe_path(str(output) + ".sha256", exists=False)
    require(not output.exists() and not sidecar.exists(), "chain_create_once")
    raw = (prefix + text).encode()
    with output.open("xb") as stream:
        os.chmod(output, 0o600)
        stream.write(raw)
    with sidecar.open("xb") as stream:
        os.chmod(sidecar, 0o600)
        stream.write(readiness.gnu_sidecar(readiness.sha256_bytes(raw), output.name))
    return {"status": "STAGED", "chain": locator(output), "sidecar": locator(sidecar),
            "programmed_span_s": sized["programmed_span_s"], "window_max_s": sized["window_max_s"],
            "latest_chain_start_epoch_s": latest}


def deadlines(plan, span, declared):
    from scripts.run_night import COURIER_DEADLINE_S, WINDOW_SHUTDOWN_GRACE_S, deadman_epoch
    exact(declared, {"latest_chain_start_epoch_s", "shutdown_epoch_s", "courier_epoch_s", "deadman_epoch_s"}, "deadlines")
    end = plan.t0_epoch_s + plan.window_max_s
    computed = {"latest_chain_start_epoch_s": end - span,
                "shutdown_epoch_s": end + WINDOW_SHUTDOWN_GRACE_S,
                "courier_epoch_s": end + WINDOW_SHUTDOWN_GRACE_S + COURIER_DEADLINE_S,
                "deadman_epoch_s": deadman_epoch(plan)}
    require(plan.t0_epoch_s <= declared["latest_chain_start_epoch_s"] <= computed["latest_chain_start_epoch_s"], "latest_chain_start")
    for key in ("shutdown_epoch_s", "courier_epoch_s", "deadman_epoch_s"):
        number(declared[key], "deadlines." + key)
        require(declared[key] == computed[key], "deadlines." + key)
    require(end <= computed["shutdown_epoch_s"] <= computed["courier_epoch_s"] < computed["deadman_epoch_s"], "deadline_order")
    return declared


def prerequisites(occurrence, references, head, t0_sequence_start, custody):
    expected = set() if occurrence == "r1" else {"r1_bundle"}
    if occurrence == "s1":
        expected.add("a1_control")
    exact(references, expected, "prerequisites")
    if not expected:
        return
    from scripts.rehearse_t0_unattended import load_evidence_bundle
    from joulewise.t0_rehearsal import evaluate_rehearsal
    path, _ = read_locator(references["r1_bundle"])
    require(path.name == "t0-rehearsal-bundle.json", "r1_bundle_locator")
    require(path.parent != custody and custody not in path.parent.parents and path.parent not in custody.parents, "prerequisite_custody_overlap")
    bundle = load_evidence_bundle(path.parent)
    verdict = evaluate_rehearsal(bundle)
    require(verdict["overall_verdict"] == "PASS" and len(verdict["gates"]) == 10
            and all(g["status"] == "PASS" for g in verdict["gates"]), "r1_not_pass")
    require(bundle.record("d149_go").value["repo_head"] == head, "r1_wrong_head")
    if occurrence == "s1":
        from scripts.check_v5_arm_abort import ABSENCE_KEYS, CONTROL_SCHEMA
        _, raw = read_locator(references["a1_control"])
        control = readiness.parse_json_bytes(raw)
        exact(control["absence"], ABSENCE_KEYS, "a1_absence")
        require(control["schema_version"] == CONTROL_SCHEMA and control["occurrence"] == "a1" and control["verdict"] == "PASS"
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


def write_qualification(occurrence, inputs, output):
    exact(inputs, {"schema_version", "head", "plan", "pack", "authorization", "confirmation", "sizing", "deadlines", "other_custody_roots", "arm_context", "prerequisites"}, "inputs")
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
    require(base["plan_id"] == frozen_identity["plan_id"], "frozen_plan_id")
    roster, auxiliary, brackets, nonsampling = pack_roster(root, occurrence)
    sizing = size_window(occurrence, inputs["sizing"], roster=roster, auxiliary=auxiliary, brackets=brackets, nonsampling=nonsampling)
    require(base["window_max_s"] == sizing["window_max_s"], "window_max")
    chain = safe_path(base["chain_path"])
    text = chain.read_text()
    no_fill(text)
    require(night_gate.chain_literal(text, "NIGHT_PROGRAMMED_SPAN_S") == str(sizing["programmed_span_s"]), "chain_span_literal")
    require(not re.search(r"(?:export\s+)?(?:EXPECTED_CONFIRMATION_DIGEST|STEP6_CONFIRMATION_TABLE)\s*=", text), "confirmation_environment_route")
    if occurrence != "r1":
        require(g2b_body(measurement) in text, "reviewed_g2b_chain_required")
    purpose = "T0_REHEARSAL" if occurrence == "r1" else "G2B_SHAKEDOWN"
    auth = inputs["authorization"]
    require(auth.get("purpose") == purpose and auth.get("claim_eligible") is False and auth.get("permitted_blocks") == 1, "purpose_claim_blocks")
    require(frozen_identity["window_id"].startswith("rehearsal-t0-unattended-") == (occurrence == "r1"), "window_prefix")
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
    bound_deadlines = deadlines(plan, sizing["programmed_span_s"], inputs["deadlines"])
    chain_deadline = night_gate.qualification_start_deadline(plan, text, purpose)
    require(chain_deadline is not None and chain_deadline == bound_deadlines["latest_chain_start_epoch_s"], "qualification_chain_deadline")
    # Authenticate exact records and sidecar with canonical preparation before
    # publishing a plan. A refused attempt retains its create-once authority
    # bytes; it cannot be quietly rewritten and retried in the same custody.
    require(auth.get("attempt_id") == f"{plan.plan_id}/{plan.pack_night['attempt_ordinal']}", "attempt_id")
    require(auth.get("pack_sha256") == digest and auth.get("permitted_chain_sha256") == readiness.sha256_bytes(chain.read_bytes()), "authorization_bindings")
    exact(auth, {"purpose", "attempt_id", "claim_eligible", "pack_sha256", "permitted_chain_sha256", "permitted_blocks", "authority"}, "authorization")
    context = readiness.validate_arm_context(inputs["arm_context"])
    require(context["custody_root"] == str(custody), "arm_context.custody_root")
    for key, value in context.items():
        if key.endswith("root") or key.endswith("path"):
            safe_path(value, exists=False)
    prerequisites(occurrence, inputs["prerequisites"], inputs["head"],
                  plan.t0_epoch_s - float(allowance(inputs["sizing"]["fixed"]["pack_t0"])), custody)
    create_record(auth_path, auth)
    create_record(confirm_path, confirmation)
    night_gate._authenticate_pack_records(plan)
    if purpose == "T0_REHEARSAL":
        night_gate._pack_rehearsal_roots(plan, {"arm_context": context, "pack": frozen_identity}, purpose)
    record = {"schema_version": OUTPUT_SCHEMA, "occurrence": occurrence,
              "head": inputs["head"], "pack_night": plan.pack_night,
              "window_id": frozen_identity["window_id"],
              "freeze_receipt": frozen,
              "science_roster": roster, "auxiliary_roster": auxiliary,
              "calibration_stream_roster": brackets,
              "nonsampling_auxiliary_roster": nonsampling,
              "sizing": sizing, "deadlines": bound_deadlines,
              "input_sha256": readiness.sha256_bytes(readiness.render_json(inputs)),
              "prerequisites": inputs["prerequisites"]}
    if occurrence == "a1":
        record.update(schema_version=ARM_ONLY_SCHEMA, mode="ARM_ONLY_NO_LAUNCH",
                      arm_context=context, plan_binding=night_plan_mapping(plan),
                      recipe={"author_argv": [str(measurement / ".venv/bin/python"), str(measurement / "scripts/author_arm_evidence_t0.py"), "--pack-root", str(root), "--custody-root", str(custody)],
                              "arm_api": "joulewise.arm_readiness.generate_arm_receipt",
                              "confirmation_record": records["confirmation_record"],
                              "expiry_checker": "scripts/check_v5_arm_abort.py"})
        create_record(output, record)
    else:
        write_night_plan(output, plan, create_once=True)
        record.update(plan=locator(output), driver_argv=[str(measurement / ".venv/bin/python"), str(measurement / "scripts/run_night.py"), "run", "--plan", str(output)])
        create_record(custody / "qualification-plan-record.json", record)
    return {"status": "STAGED", "occurrence": occurrence, "output": locator(output)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="occurrence", required=True)
    for name in ("r1", "a1", "s1"):
        command = commands.add_parser(name)
        command.add_argument("--inputs", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
    render = commands.add_parser("render-chain")
    render.add_argument("--occurrence", dest="render_occurrence", choices=("r1", "s1"), required=True)
    render.add_argument("--template", type=Path, required=True)
    render.add_argument("--sizing", type=Path, required=True)
    render.add_argument("--pack-root", type=Path, required=True)
    render.add_argument("--t0-epoch-s", type=float, required=True)
    render.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.occurrence == "render-chain":
            result = render_qualification_chain(args.render_occurrence, args.template,
                read_object(args.sizing), args.pack_root, args.t0_epoch_s, args.output)
        else:
            result = write_qualification(args.occurrence, read_object(args.inputs), args.output)
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
