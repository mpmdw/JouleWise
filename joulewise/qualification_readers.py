"""Historical qualification sizing authentication and stored-input readers."""
from __future__ import annotations
import math
import shlex
import re
from fractions import Fraction
from pathlib import Path
from joulewise import receipt_readers as readiness, night_gate

def sha(path):
    return readiness.sha256_bytes(Path(path).read_bytes())


class HarvestRefusal(ValueError):
    """Only fixed structural codes may cross the public boundary."""


def read(path):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise HarvestRefusal("input_not_regular")
    return readiness.parse_json_bytes(path.read_bytes())


def identifier(value):
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value) is None:
        raise HarvestRefusal("identity_invalid")
    return value


def authenticated_reference(value):
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise HarvestRefusal("locator_invalid")
    path = Path(value["path"])
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
        raise HarvestRefusal("locator_invalid")
    if not path.is_file() or sha(path) != value["sha256"]:
        raise HarvestRefusal("locator_digest_mismatch")
    return path


def reference(path):
    return {"path": str(path), "sha256": sha(path)}


def authenticated_clock_budget(input_root, pack_root):
    """Replay sizing against the chain pinned by the occurrence's authority.

    A self-consistent gate is not authority for its stream maximum. Both the
    source allowances and the computed maximum are pinned in the permitted
    chain before the authorization record is made.
    """
    from joulewise import kernel_clock
    input_root, pack_root = Path(input_root), Path(pack_root)
    binding_path = input_root / "kernel-frequency-binding.json"
    binding = read(binding_path)
    if (set(binding) != {"schema", "occurrence", "plan", "sizing", "plan_id", "pack_root", "pack_sha256"}
            or binding["schema"] != "joulewise.v5_qualification_clock_binding.v1"
            or binding["occurrence"] not in {"a1", "a2", "s1", "s2"}
            or binding["pack_root"] != str(pack_root)):
        raise HarvestRefusal("clock_sizing_binding_invalid")
    plan_path = authenticated_reference(binding["plan"])
    plan_record = read(plan_path)
    if binding["occurrence"] in {"a1", "a2"}:
        if (plan_record.get("schema_version") != ARM_ONLY_SCHEMA
                or plan_record.get("mode") not in {"ARM_ONLY_NO_LAUNCH", "G10_INPUT_CAPTURE_NO_LAUNCH"}
                or plan_record.get("occurrence") != binding["occurrence"]):
            raise HarvestRefusal("clock_sizing_plan_invalid")
        plan_record = plan_record["plan_binding"]
    plan = night_gate.NightPlan.from_mapping(plan_record)
    if (plan.plan_id != binding["plan_id"] or plan.pack_night["pack_root"] != str(pack_root)
            or plan.pack_night["pack_sha256"] != binding["pack_sha256"]
            or input_root != Path(plan.custody_root) / pack_root.name / "arm_readiness.t0.inputs"):
        raise HarvestRefusal("clock_sizing_plan_mismatch")
    night_gate._authenticate_pack_records(plan)
    chain = Path(plan.chain_path)
    if sha(chain) != Path(plan.chain_sha256_path).read_text().split()[0]:
        raise HarvestRefusal("clock_sizing_chain_mismatch")
    sizing_path = authenticated_reference(binding["sizing"])
    sizing = read(sizing_path)
    text = chain.read_text()
    if night_gate.chain_literal(text, "NIGHT_CLOCK_SIZING_SHA256") != sha(sizing_path):
        raise HarvestRefusal("clock_sizing_source_mismatch")
    roster, auxiliary, brackets, nonsampling = pack_roster(pack_root, binding["occurrence"])
    computed = size_window(binding["occurrence"], sizing, roster=roster,
        auxiliary=auxiliary, brackets=brackets, nonsampling=nonsampling)["longest_sampler_stream_s"]
    gate_path = input_root / "kernel-frequency-gate.json"
    gate = kernel_clock.validate_gate(read(gate_path))
    if (night_gate.chain_literal(text, "NIGHT_CLOCK_STREAM_MAX_S") != str(computed)
            or gate["t_stream_max_s"] != computed):
        raise HarvestRefusal("clock_stream_maximum_mismatch")
    return computed, tuple(reference(p) for p in (binding_path, plan_path, sizing_path, gate_path, chain))


REPO_ROOT = Path(__file__).resolve().parents[1]


ARM_ONLY_SCHEMA = "joulewise.v5_qualification_arm_only.v1"


class QualificationError(ValueError):
    pass


def require(condition, field):
    if not condition:
        raise QualificationError(field)


def exact(value, keys, field):
    require(isinstance(value, dict) and set(value) == set(keys), field + ".keys")
    return value


def safe_path(value, *, exists=True):
    require(isinstance(value, (str, Path)), "path.type")
    path = Path(value)
    require(path.is_absolute() and ".." not in path.parts, "path.absolute")
    require(not any(p.is_symlink() for p in (path, *path.parents)), "path.symlink")
    require(path.resolve(strict=exists) == path, "path.lexical")
    return path


def read_locator(value):
    exact(value, {"path", "sha256"}, "locator")
    path = Path(value["path"])
    if not path.is_absolute():
        require(".." not in path.parts, "locator.relative_escape")
        path = REPO_ROOT / path
    path = safe_path(path)
    raw = night_gate._pack_bytes(path, "qualification_input", value["sha256"])
    return path, raw


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



GAMMA = "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"


DWELL_CAP_S = 2700


FIXED_COMPONENTS = {
    "s1": {"pack_t0", "fixed_settles", "pre_post_calibration", "stage_custody", "terminal_shutdown"},
}


MEMBER_COMPONENTS = {"load", "warmup", "prefill", "forced_decode", "cooldown", "idle_admission"}


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

# Stored block-4 qualification/restore readers. These retain receipt identities,
# admission-abort arithmetic, original archive links and native ledger grammar.
import os
import time
import subprocess
from decimal import Decimal
from joulewise import calibration_ledger as ledger
from joulewise.authentication_io import read_authentication_input
from joulewise.measurement_liveness import pending_launch_closed, observe_identity, _start_token
from joulewise.receipt_formats import _COMMAND_SCHEMA as COMMAND_CAPTURE_SCHEMA
from scripts.harvest_window import inventory

ATTEMPT_HARVEST_SCHEMA = "joulewise.harvest_v5_g2b_window.v1"
ADMISSION_ABORT_CODE = "guard_attested_idle_admission_abort"
BATTERY_BOUNDARY_PHASES = {"arm": "arm_check", "publication": "publish_install", "t0": "t0"}
NULL_RESTORE_SCHEMA = "joulewise.v5_null_reservation_restore.v1"
REFUSAL = "evidence_author_t0_clock_attestation_underivable"
ANCHOR_DETAIL = "R0-to-author RAW anchor delta exceeds 5000000 ns"
from joulewise.hazards.network_time import OFF_ARGV as _OFF_ARGV
ON_ARGV = (*_OFF_ARGV[:-1], "on")


def previous_attempt(value):
    """Validate the mandatory pointer; absence is never a first-attempt default."""
    if isinstance(value, dict) and set(value) == {"none"} and value["none"] is True:
        return None
    if (not isinstance(value, dict) or set(value) != {"path", "sha256"}
            or not isinstance(value["path"], str)
            or not isinstance(value["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is None):
        raise HarvestRefusal("previous_attempt_required_or_invalid")
    path = authenticated_reference(value)
    if path.name != "harvest.json":
        raise HarvestRefusal("previous_attempt_not_harvest")
    return path



def admission_abort_evidence(value):
    """Replay every controller idle-admission abort predicate from native bytes."""
    from joulewise.environment_admission import ADMISSION_SCHEMA, environment_observation_failure, _registered_campaign_policy
    from joulewise.environment import evaluate_environment_policy
    from joulewise.authentication_io import read_authentication_input
    from joulewise.adapters.powermetrics import idle_window_gpu_quality
    from joulewise.idle_admission import evaluate_cpu_idle_admission
    if not isinstance(value, dict) or set(value) not in ({"metadata", "summary", "events"}, {"metadata", "summary", "events", "telemetry"}):
        raise HarvestRefusal("admission_abort_evidence_invalid")
    metadata_path, summary_path, events_path = (authenticated_reference(value[key]) for key in ("metadata", "summary", "events"))
    if (metadata_path.name != "metadata.json" or summary_path.name != "summary_metrics.json"
            or events_path.name != "events.jsonl" or metadata_path.parent != summary_path.parent
            or metadata_path.parent != events_path.parent):
        raise HarvestRefusal("admission_abort_bundle_mismatch")
    metadata, summary = read(metadata_path), read(summary_path)
    admission = metadata.get("environment_admission", {})
    guards, attempts = admission.get("guard_observations", []), admission.get("attempts", [])
    events = [readiness.parse_json_bytes(line) for line in read_authentication_input(
        events_path, grammar="jsonl", label="block-4 admission abort events").splitlines() if line.strip()]
    failures = [event for event in events if event.get("event_type") == "failure"]
    policy = _registered_campaign_policy(metadata)
    if (metadata.get("run_id") != metadata_path.parent.name or summary.get("status") != "failed"
            or len(failures) != 1 or failures[0].get("phase") != "idle_baseline"
            or admission.get("schema_version") != ADMISSION_SCHEMA or admission.get("decision") != "abort"
            or policy is None or policy.profile.value != "production"
            or not policy.idle_admission.enabled or policy.idle_admission.on_fail.value != "abort"
            or admission.get("on_fail") != "abort" or admission.get("policy_version") != policy.policy_version
            or not isinstance(guards, list) or not guards or not isinstance(attempts, list)):
        raise HarvestRefusal("admission_abort_not_guard_attested")
    phases = ["before_attempt_1", "after_attempt_1", "before_attempt_2", "after_attempt_2"]
    if ([guard.get("phase") for guard in guards] != phases[:len(guards)] or len(guards) > 4
            or any(guard.get("capture_skipped") is not False or not isinstance(guard.get("errors"), dict) for guard in guards)
            or any(environment_observation_failure(guard) is not None for guard in guards[:-1])):
        raise HarvestRefusal("admission_abort_not_guard_attested")
    reason = environment_observation_failure(guards[-1])
    stored = admission.get("per_run_environment_evaluation", {})
    if reason is None and len(guards) == 1:
        snapshot = stored.get("snapshot")
        if not isinstance(snapshot, dict):
            raise HarvestRefusal("admission_abort_environment_snapshot_missing")
        fresh = evaluate_environment_policy(snapshot, policy.environment_guard)
        if (fresh.get("eligible") is not False
                or any(stored.get(key) != fresh.get(key) for key in ("eligible", "snapshot_sha256", "findings", "findings_sha256"))
                or metadata.get("campaign_environment_preflight", {}).get("override") is not None):
            raise HarvestRefusal("admission_abort_environment_replay_mismatch")
        reason = "critical per-run environment policy did not pass"
    elif reason is None:
        if len(guards) != 4 or len(attempts) != 2 or len(value.get("telemetry", [])) != 2:
            raise HarvestRefusal("admission_abort_retry_evidence_missing")
        for index, (attempt, ref) in enumerate(zip(attempts, value["telemetry"]), 1):
            path = authenticated_reference(ref)
            name = "rich_telemetry_idle.jsonl" if index == 1 else "rich_telemetry_idle_attempt_2.jsonl"
            if path != metadata_path.parent / name or attempt.get("attempt") != index:
                raise HarvestRefusal("admission_abort_retry_evidence_mismatch")
            rows = [readiness.parse_json_bytes(line) for line in read_authentication_input(
                path, grammar="jsonl", label="block-4 native idle-admission telemetry").splitlines() if line.strip()]
            gpu = idle_window_gpu_quality(rows)
            if any(attempt.get("baseline", {}).get(key) != result for key, result in gpu.items()):
                raise HarvestRefusal("admission_abort_gpu_replay_mismatch")
            admitted = gpu["idle_window_suspect"] is False
            extension = policy.idle_admission_extension
            if extension is not None:
                cpu = evaluate_cpu_idle_admission(rows, extension.cpu_criteria, gpu_admitted=admitted)
                if (admission.get("idle_admission_extension", {}).get("sha256") != extension.sha256()
                        or attempt.get("cpu_admission_enforced") is not True or attempt.get("gpu_admitted") is not admitted
                        or attempt.get("cpu_admission") != cpu):
                    raise HarvestRefusal("admission_abort_cpu_replay_mismatch")
                admitted = cpu["admitted"]
            if admitted is not False or attempt.get("admitted") is not False:
                raise HarvestRefusal("admission_abort_retry_not_failed")
        reason = "idle environment admission failed after one retry"
    if (admission.get("failure") != reason or summary.get("failure_message") != reason
            or failures[0].get("message") != reason):
        raise HarvestRefusal("admission_abort_reason_mismatch")
    return value



def native_admission_abort(runs):
    """Locate native aborts; the harvester also assesses successful members."""
    candidates, other_causes = [], []
    for metadata_path in sorted(Path(runs).rglob("metadata.json")):
        bundle = metadata_path.parent
        summary_path = bundle / "summary_metrics.json"
        if not summary_path.is_file():
            other_causes.append("attempt_bundle_incomplete")
            continue
        metadata, summary = read(metadata_path), read(summary_path)
        if summary.get("status") == "succeeded":
            continue
        if metadata.get("environment_admission", {}).get("decision") != "abort":
            other_causes.append("member_failed_outside_idle_admission")
            continue
        value = {"metadata": reference(metadata_path), "summary": reference(summary_path),
                 "events": reference(bundle / "events.jsonl")}
        telemetry = [bundle / name for name in ("rich_telemetry_idle.jsonl", "rich_telemetry_idle_attempt_2.jsonl")]
        if all(path.is_file() for path in telemetry):
            value["telemetry"] = [reference(path) for path in telemetry]
        admission_abort_evidence(value)
        candidates.append(value)
    if len(candidates) > 1:
        other_causes.append("multiple_idle_admission_aborts_in_attempt")
    return (candidates[0] if candidates else None), sorted(set(other_causes))



def is_admission_abort(record):
    if record.get("recovery_classification") != "admission_abort":
        return False
    if (record.get("verdict") != "RECOVER"
            or record.get("cause_codes") != [ADMISSION_ABORT_CODE]
            or record.get("cause_classes") != ["instrument_physics"]):
        raise HarvestRefusal("admission_abort_has_other_recover_cause")
    admission_abort_evidence(record.get("admission_abort"))
    return True



def tooling_s2_predecessor(record):
    """Eligibility is necessary, not the lead's R3/head-coverage permission."""
    codes = record.get("cause_codes")
    if (record.get("occurrence") != "s1" or record.get("verdict") != "RECOVER"
            or record.get("cause_classes") != ["tooling"]
            or not isinstance(codes, list) or not codes
            or any(not isinstance(code, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", code)
                   for code in codes)
            or record.get("clock_majority", {}).get("triggered") is True
            or record.get("recovery_classification") in {"admission_abort", "recover_no_science"}):
        raise HarvestRefusal("s2_not_after_named_tooling_recover")
    return record



def authenticate_s2_authority(reference, plan_id, previous):
    authority = read(authenticated_reference(reference))
    prior_reference, prior = nearest_counted_predecessor(previous)
    tooling_s2_predecessor(prior)
    if (authority.get("schema") != "joulewise.v5_qualification_s2_authority.v1"
            or authority.get("new_plan_id") != plan_id or authority.get("lead_approved") is not True
            or authority.get("s1_harvest") != prior_reference
            or prior.get("plan_id") == plan_id
            or authority.get("tooling_cause") not in prior["cause_codes"]):
        raise HarvestRefusal("s2_not_authorized_tooling_cure")
    authenticated_reference(authority.get("r3_cure"))
    authenticated_reference(authority.get("head_coverage"))
    return authority



def authenticate_reharvest(record, destination, original, original_path):
    """Replay the existing source census against both retained source copies."""
    from scripts.harvest_window import copy_matches
    destination, original_path = Path(destination), Path(original_path)
    if (destination.parent != original_path.parent
            or re.fullmatch(r"reharvest-[1-9][0-9]*", destination.name) is None):
        raise HarvestRefusal("attempt_reharvest_layout_mismatch")
    for key in ("schema", "plan", "plan_sha256", "previous_attempt", "block_archive_root", "occurrence", "plan_id"):
        if original.get(key) != record.get(key):
            raise HarvestRefusal("attempt_reharvest_identity_mismatch")
    censuses = []
    for archive_root in (original_path.parent, destination):
        manifest = read(archive_root / "withheld/replay-locators.json")
        if manifest.get("schema") != "joulewise.v5_qualification_replay_locators.v1":
            raise HarvestRefusal("reharvest_source_census_changed")
        rows = manifest["sources"]
        sources, census = {}, {}
        for row in rows:
            name = identifier(row["name"])
            path = archive_root / "withheld/sources" / name
            if name in sources or row["archived_path"] != str(path):
                raise HarvestRefusal("reharvest_source_census_changed")
            sources[name] = path
            census[name] = {key: row[key] for key in ("original_path", "inventory")}
        retained = census_sources(sources)
        for name in sources:
            if not copy_matches(census[name]["inventory"], retained[name]):
                raise HarvestRefusal("reharvest_source_bytes_changed")
        censuses.append(census)
    if censuses[0].keys() != censuses[1].keys():
        raise HarvestRefusal("reharvest_source_census_changed")
    if censuses[0] != censuses[1]:
        raise HarvestRefusal("reharvest_source_bytes_changed")
    return record



def counted_attempt(record, original_path, *, pending=None):
    """Keep the original pointer and count the first non-REFUSED verdict."""
    if record.get("verdict") != "REFUSED":
        return record
    original_path = Path(original_path)
    candidates = {}
    for path in original_path.parent.glob("reharvest-*/harvest.json"):
        if re.fullmatch(r"reharvest-[1-9][0-9]*", path.parent.name):
            candidates[int(path.parent.name.removeprefix("reharvest-"))] = (path.parent, None)
    if pending is not None:
        destination, replacement = pending
        authenticate_reharvest(replacement, destination, record, original_path)
        candidates[int(Path(destination).name.removeprefix("reharvest-"))] = (destination, replacement)
    counted = record
    for number in sorted(candidates):
        destination, replacement = candidates[number]
        if replacement is None:
            replacement = read(Path(destination) / "harvest.json")
        authenticate_reharvest(replacement, destination, record, original_path)
        if counted.get("verdict") == "REFUSED" and replacement.get("verdict") != "REFUSED":
            counted = replacement
        # Later archives remain authenticated, but their verdicts are derived only.
    return counted



def nearest_counted_predecessor(previous):
    """Resolve NULL links and REFUSED re-harvests without changing pointers."""
    seen = set()
    while (path := previous_attempt(previous)) is not None:
        if path in seen:
            raise HarvestRefusal("attempt_history_cycle")
        seen.add(path)
        original = read(path)
        if path.parent.name != original.get("plan_id") or path.parent.parent.name != "attempts":
            raise HarvestRefusal("attempt_archive_layout_mismatch")
        record = counted_attempt(original, path)
        if record.get("verdict") != "NULL":
            return previous, record
        previous = original["previous_attempt"]
    raise HarvestRefusal("s2_not_after_named_tooling_recover")



def attempt_history(current, archive_root, *, current_harvest=None, reharvest=None):
    """Walk authenticated links and census the complete supplied block root.

    The caller must obtain the block root and current pointer from create-once
    plan/authorization bytes. Linked production records reauthenticate those
    bindings; the census unit is exactly attempts/*/harvest.json.

    Before publication, current_harvest is absent. For replay it is the exact
    original harvest.json being checked. Re-harvests supply counted verdicts,
    never another attempt or chain pointer. The optional reharvest tuple holds
    a pending destination/record after source archiving, before publication.
    """
    root = Path(archive_root)
    if (not root.is_absolute() or not root.is_dir()
            or any(p.is_symlink() for p in (root, *root.parents))):
        raise HarvestRefusal("attempt_archive_root_invalid")
    census_sources({"attempt-archive": root})  # Also refuses nested symlinks.
    found = set(root.glob("attempts/*/harvest.json"))
    records, chain, seen_ids = [current], set(), set()
    if current_harvest is not None:
        path = Path(current_harvest)
        if path not in found or read(path) != current:
            raise HarvestRefusal("current_attempt_harvest_mismatch")
        chain.add(path)
    cursor = current
    while True:
        if (not isinstance(cursor, dict) or cursor.get("schema") != ATTEMPT_HARVEST_SCHEMA
                or cursor.get("occurrence") not in {"s1", "s2"}
                or "previous_attempt" not in cursor):
            raise HarvestRefusal("attempt_history_record_invalid")
        identity = identifier(cursor.get("plan_id"))
        if "plan" in current:
            authenticate_attempt_record(cursor, root)
        if identity in seen_ids:
            raise HarvestRefusal("attempt_history_identity_reused")
        seen_ids.add(identity)
        path = previous_attempt(cursor["previous_attempt"])
        if path is None:
            break
        if path not in found:
            raise HarvestRefusal("previous_attempt_outside_block_archive")
        if path in chain:
            raise HarvestRefusal("attempt_history_cycle")
        chain.add(path)
        cursor = read(path)
        if path != root / "attempts" / cursor.get("plan_id", "") / "harvest.json":
            raise HarvestRefusal("attempt_archive_layout_mismatch")
        records.append(cursor)
    # Inspect all records before the set comparison so second roots and forks
    # have useful fixed refusal codes, including unreferenced attempts.
    roots, predecessors = 0, set()
    for record in [current, *(read(path) for path in sorted(found - ({Path(current_harvest)} if current_harvest else set())))]:
        if not isinstance(record, dict) or record.get("schema") != ATTEMPT_HARVEST_SCHEMA:
            raise HarvestRefusal("attempt_archive_contains_unregistered_harvest")
        if "previous_attempt" not in record:
            raise HarvestRefusal("previous_attempt_required_or_invalid")
        path = previous_attempt(record["previous_attempt"])
        if path is None:
            roots += 1
        elif path in predecessors:
            raise HarvestRefusal("attempt_history_fork")
        else:
            predecessors.add(path)
    if roots != 1:
        raise HarvestRefusal("attempt_history_second_none")
    if found != chain:
        raise HarvestRefusal("attempt_history_orphan_harvest")
    counted = [counted_attempt(record, root / "attempts" / record["plan_id"] / "harvest.json",
                               pending=reharvest if index == 0 else None)
               for index, record in enumerate(records)]
    chronological = list(reversed(counted))
    s2_count, admission_count = 0, 0
    repeated_null_codes = []
    prior = None
    for index, record in enumerate(chronological):
        if repeated_null_codes:
            refusal = HarvestRefusal("same_refusal_twice_consult_required")
            refusal.refusal_codes = repeated_null_codes
            raise refusal
        # NULL spends neither allowance, but two adjacent NULL refusals still
        # send the NEXT spend to a consult. Compare these records directly;
        # `prior` deliberately skips NULL for the separate allowance rules.
        if (index > 0 and record.get("verdict") == "NULL"
                and chronological[index - 1].get("verdict") == "NULL"):
            # New NULL harvests retain authenticated native refusal reasons.
            # Older retained records have only their original cause census.
            codes = record.get("native_refusal_codes", record.get("cause_codes", []))
            previous_record = chronological[index - 1]
            previous_codes = previous_record.get("native_refusal_codes", previous_record.get("cause_codes", []))
            if (not isinstance(codes, list) or not isinstance(previous_codes, list)):
                raise HarvestRefusal("attempt_history_refusal_codes_invalid")
            current_codes = sorted({identifier(code) for code in codes})
            previous_codes = sorted({identifier(code) for code in previous_codes})
            if current_codes and current_codes == previous_codes:
                repeated_null_codes = current_codes
        if record["occurrence"] == "s2":
            s2_count += record.get("verdict") != "NULL"
            if s2_count > 1:
                raise HarvestRefusal("attempt_history_second_s2")
            if prior is None:
                raise HarvestRefusal("s2_not_after_named_tooling_recover")
            tooling_s2_predecessor(prior)
        if is_admission_abort(record):
            admission_count += 1
            if admission_count > 1 and index < len(chronological) - 1:
                raise HarvestRefusal("same_refusal_twice_consult_required")
        if prior is not None and record["occurrence"] == "s1":
            if not (is_admission_abort(prior)
                    or prior.get("verdict") == "RECOVER"
                    and prior.get("recovery_classification") == "recover_no_science"
                    and prior.get("cause_classes") == ["tooling"]):
                raise HarvestRefusal("fresh_s1_predecessor_not_rearmable")
        if record.get("verdict") != "NULL":
            prior = record
    return {"harvests": [reference(path) for path in sorted(chain)],
            "s2_count": s2_count, "admission_abort_count": admission_count,
            "same_refusal_twice": admission_count > 1 or bool(repeated_null_codes),
            "same_refusal_codes": repeated_null_codes}



def authenticate_attempt_record(record, root):
    """A harvest's self-reported predecessor is checked against its authority."""
    path = authenticated_reference(record.get("plan"))
    plan = night_gate.NightPlan.from_mapping(read(path))
    if (record.get("plan_id") != plan.plan_id or record.get("plan_sha256") != sha(path)
            or record.get("previous_attempt") != plan.previous_attempt
            or record.get("block_archive_root") != plan.block_archive_root
            or str(root) != plan.block_archive_root):
        raise HarvestRefusal("attempt_history_plan_binding_mismatch")
    authorization = read(authenticated_reference(plan.pack_night["authorization_record"]))
    keys = {"purpose", "attempt_id", "claim_eligible", "pack_sha256", "permitted_chain_sha256",
            "permitted_blocks", "authority", "previous_attempt", "block_archive_root"}
    if plan.null_reservation_restore is not None:
        keys.add("null_reservation_restore")
    if (set(authorization) != keys or authorization.get("claim_eligible") is not False
            or authorization.get("permitted_blocks") != 1 or "D-171" not in authorization.get("authority", "")
            or authorization.get("pack_sha256") != plan.pack_night["pack_sha256"]):
        raise HarvestRefusal("attempt_history_authorization_binding_mismatch")
    for key in ("previous_attempt", "block_archive_root", "null_reservation_restore"):
        value = getattr(plan, key)
        if authorization.get(key) != value:
            raise HarvestRefusal("attempt_history_authorization_binding_mismatch")
    if (authorization.get("purpose") != "G2B_SHAKEDOWN"
            or authorization.get("attempt_id") != f"{plan.plan_id}/{plan.pack_night['attempt_ordinal']}"
            or authorization.get("permitted_chain_sha256") != sha(plan.chain_path)
            or night_gate.chain_literal(Path(plan.chain_path).read_text(), "V5_QUALIFICATION_OCCURRENCE") != record.get("occurrence")):
        raise HarvestRefusal("attempt_history_authorization_binding_mismatch")
    verify_attempt_restore(plan)
    if record.get("occurrence") == "s2":
        plan_record = read(Path(plan.custody_root) / "qualification-plan-record.json")
        authenticate_s2_authority(plan_record.get("s2_authority"), plan.plan_id, plan.previous_attempt)
    qualification = Path(root) / "attempts" / plan.plan_id / "qualification/harvest.json"
    counted = counted_attempt(record, Path(root) / "attempts" / plan.plan_id / "harvest.json")
    if counted.get("recovery_classification") == "admission_abort" and qualification.is_file():
        other = read(qualification)
        if (other.get("structural_harvest") != reference(Path(root) / "attempts" / plan.plan_id / "harvest.json")
                or other.get("end_state") is True
                or other.get("verdict") == "RECOVER" and other.get("cause_codes") != [ADMISSION_ABORT_CODE]):
            raise HarvestRefusal("admission_abort_has_other_recover_cause")
    return plan



def verify_attempt_restore(plan, *, writer=False):
    previous = previous_attempt(plan.previous_attempt)
    restore_ref = plan.null_reservation_restore
    if previous is None:
        if restore_ref is not None:
            raise HarvestRefusal("null_restore_without_null_predecessor")
        return
    prior = counted_attempt(read(previous), previous)
    if prior.get("verdict") != "NULL":
        if restore_ref is not None:
            raise HarvestRefusal("null_restore_without_null_predecessor")
        return
    prior_plan = night_gate.NightPlan.from_mapping(read(authenticated_reference(prior.get("plan"))))
    capture = Path(prior_plan.custody_root) / prior_plan.pack_night["pack_id"] / "arm_readiness.t0.inputs/ledger-reservation.json"
    if capture.exists() and restore_ref is None:
        raise HarvestRefusal("null_reservation_restore_required")
    if restore_ref is not None:
        record = read(authenticated_reference(restore_ref))
        environment = Path(plan.chain_path).parent / "window.env"
        if environment.is_file():
            from joulewise import receipt_formats as author
            from joulewise.authentication_io import read_authentication_input
            values = author.parse_window_environment(read_authentication_input(
                environment, grammar="raw", label="NULL rearm planned ledger bindings"))
        else:
            text = Path(plan.chain_path).read_text()
            values = {key: night_gate.chain_literal(text, key) for key in ("CALIBRATION_LEDGER", "LEDGER_HEAD_PIN")}
        if (values["CALIBRATION_LEDGER"] != record["restored_ledger"]["path"]
                or values["LEDGER_HEAD_PIN"] != record["head_pin"]["path"]):
            raise HarvestRefusal("null_restore_next_ledger_binding_mismatch")
        capture = Path(plan.custody_root) / plan.pack_night["pack_id"] / "arm_readiness.t0.inputs/ledger-reservation.json" if hasattr(plan, "pack_night") else None
        if not writer and capture is not None and capture.exists():
            argv = read(capture)["argv"]
            if any(flag(argv, "--" + name) != values[key] for name, key in (("ledger", "CALIBRATION_LEDGER"), ("head-pin", "LEDGER_HEAD_PIN"))):
                raise HarvestRefusal("null_restore_next_reservation_binding_mismatch")
        verify_restore(restore_ref, plan.previous_attempt,
                       restored_ledger=record["restored_ledger"] if writer else None)



def attempt_record(plan, plan_path, occurrence, **extra):
    previous_attempt(plan.previous_attempt)
    return {"schema": ATTEMPT_HARVEST_SCHEMA, "plan_id": identifier(plan.plan_id),
            "plan": reference(plan_path), "plan_sha256": sha(plan_path),
            "previous_attempt": plan.previous_attempt, "block_archive_root": plan.block_archive_root,
            "occurrence": occurrence, **extra}



def attempt_destination(plan, destination, *, qualification=False, replay=None):
    """Only the registered unit is an attempt; replay and qualification are children."""
    root = Path(plan.block_archive_root)
    attempt = root / "attempts" / identifier(plan.plan_id)
    destination = Path(destination)
    expected = attempt / "qualification" if qualification else attempt
    if replay is None:
        if destination != expected:
            raise HarvestRefusal("attempt_archive_layout_mismatch")
    elif (destination.parent != attempt or re.fullmatch(r"reharvest-[1-9][0-9]*", destination.name) is None
          or not Path(replay).is_relative_to(attempt)):
        raise HarvestRefusal("attempt_reharvest_layout_mismatch")
    else:
        number = int(destination.name.removeprefix("reharvest-"))
        # Counting uses numeric order, so publication must preserve that order.
        # Reserve every existing replay directory, including unpublished and
        # qualification archives, rather than only those with harvest.json.
        for path in attempt.glob("reharvest-*"):
            suffix = path.name.removeprefix("reharvest-")
            if path.is_dir() and re.fullmatch(r"[0-9]+", suffix) and int(suffix) >= number:
                raise HarvestRefusal("attempt_reharvest_number_not_increasing")
    return attempt



def checked_history(record, plan, *, replay=False, reharvest=None):
    path = Path(plan.block_archive_root) / "attempts" / plan.plan_id / "harvest.json"
    if replay:
        # Chain identity stays with the original; its REFUSED verdict may be
        # superseded by an authenticated identical-source re-harvest.
        original = read(path)
        for key in ("plan", "previous_attempt", "block_archive_root", "occurrence", "plan_id"):
            if original.get(key) != record.get(key):
                raise HarvestRefusal("attempt_reharvest_identity_mismatch")
        return attempt_history(original, plan.block_archive_root, current_harvest=path,
                               reharvest=(Path(reharvest), record) if reharvest is not None else None)
    return attempt_history(record, plan.block_archive_root)



def admission_abort_disposition(record, history):
    if not is_admission_abort(record):
        raise HarvestRefusal("admission_abort_not_guard_attested")
    repeated = history["admission_abort_count"] > 1
    return {"end_state": False, "s2_eligible": False, "consumes_s2": False,
            "next_step": "same_refusal_twice_consult_required" if repeated else
                         "fresh_s1_plan_authorization_t0_after_admission_cause_removed"}



def s1_desk_records(bundle):
    """Require the four post-STOP observations, each bound by its lifecycle hash."""
    from joulewise import rehearsal_readers as t0
    lifecycle = bundle.record("lifecycle")
    if lifecycle is None or not isinstance(lifecycle.value, dict):
        raise HarvestRefusal("s1_desk_lifecycle_missing")
    stages = lifecycle.value.get("stages", [])
    result = {}
    for name in ("claim_backup", "bound_backup", "close_out", "restore"):
        rows = [row for row in stages if row.get("stage_id") == name]
        if len(rows) != 1 or rows[0].get("status") != "COMPLETE":
            raise HarvestRefusal("s1_desk_stage_missing")
        try:
            artifact = t0._verify_artifact_reference(bundle, rows[0].get("evidence"), label=name)
        except ValueError as exc:
            raise HarvestRefusal("s1_desk_stage_digest_mismatch") from exc
        if (not isinstance(artifact.value, dict) or artifact.value.get("schema_version") != t0.QUALIFICATION_STAGE_SCHEMA
                or artifact.value.get("stage_id") != name):
            raise HarvestRefusal("s1_desk_stage_schema_invalid")
        result[name] = {"path": str(artifact.path), "sha256": artifact.sha256}
    return result



def group_clear(night, *, killpg=os.killpg, plan_id=None, observer=None):
    """Read #475 custody even if the PASS-only chain marker was never made.

    Do not write launch.resolved: absence is recorded in the derived harvest.
    A dead leader alone is insufficient to disprove a surviving process group.
    """
    night = Path(night)
    pending = night / "launch.pending"
    if pending.exists() or pending.is_symlink():
        value = read(pending)
        if (set(value) != {"schema", "pgid", "pid", "start_time", "plan_id", "attempt_id", "epoch_s"}
                or value["schema"] != "joulewise.launch_pending.v1"
                or type(value["pid"]) is not int or value["pid"] <= 1
                or value["pgid"] != value["pid"]
                or not isinstance(value["start_time"], (str, type(None)))
                or not isinstance(value["attempt_id"], str) or not value["attempt_id"]
                or type(value["epoch_s"]) not in (int, float)
                or (plan_id is not None and value["plan_id"] != plan_id)):
            raise HarvestRefusal("pending_launcher_identity_invalid")
        if pending_launch_closed(night):
            resolved = night / "launch.resolved"
            if resolved.exists() and read(resolved)["pgid"] != value["pgid"]:
                raise HarvestRefusal("pending_launcher_closure_mismatch")
            return True
        identity = (observer or observe_identity)(value["pid"])
        recorded, current = _start_token(value["start_time"]), _start_token(identity.start_time)
        if identity.state == "LIVE" and recorded is not None and current is not None and recorded != current:
            return True
        pgid = value["pgid"]
    else:
        started = night / "chain.started"
        if not started.exists() and not started.is_symlink():
            return True
        pgid = read(started).get("pgid")
        if type(pgid) is not int or pgid <= 1:
            raise HarvestRefusal("chain_group_identity_invalid")
    try:
        killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False



def g10_sources(custody):
    """Preserve the complete original physical-control tree for harvest replay."""
    record_path = Path(custody) / "qualification-plan-record.json"
    if not record_path.exists():
        return {}
    prereqs = read(record_path)["prerequisites"]
    positive = authenticated_reference(prereqs["g10_control"])
    manifests = prereqs["g10_artifacts"]
    if len(manifests) != 1:
        raise HarvestRefusal("g10_custody_manifest_required")
    manifest = authenticated_reference(manifests[0])
    if manifest.name != "custody-manifest.json" or positive != manifest.parent / "positive-control.json":
        raise HarvestRefusal("g10_custody_locator_invalid")
    return {"g10-custody": manifest.parent}



def replay_g10_custody(custody, positive, *, bundle=None):
    """Re-run G10's native verifier with the registered head/boot/order bounds."""
    record = read(Path(custody) / "qualification-plan-record.json")
    prereqs = record["prerequisites"]
    positive_path = authenticated_reference(prereqs["g10_control"])
    manifest_path = authenticated_reference(prereqs["g10_artifacts"][0])
    if read(positive_path) != positive:
        raise HarvestRefusal("g10_positive_copy_mismatch")
    first = read(authenticated_reference(prereqs["a1_control"]))
    second = read(authenticated_reference(prereqs["a2_control"]))
    plan = read(authenticated_reference(record["plan"]))
    from joulewise import receipt_formats as author
    input_root = Path(custody) / plan["pack_night"]["pack_id"] / author._INPUT_DIRECTORY
    captures = []
    for filename in author._CAPTURE_FILES.values():
        path = input_root / filename
        capture = read(path)
        if bundle is not None:
            from joulewise.rehearsal_readers import _artifact_for_path
            artifact = _artifact_for_path(bundle, str(path))
            if artifact is None or artifact.sha256 != sha(path) or artifact.value != capture:
                raise HarvestRefusal("g10_s1_boundary_custody")
        if (type(capture.get("started_monotonic_ns")) is not int
                or capture["started_monotonic_ns"] < 0
                or capture.get("boot_session_id", "").lower() != second["boot_session_id"].lower()):
            raise HarvestRefusal("g10_boot_or_order")
        captures.append(capture)
    if first["boot_session_id"].lower() != second["boot_session_id"].lower():
        raise HarvestRefusal("g10_boot_or_order")
    verify_g10_custody(positive_path, manifest_path, code_root=Path(plan["measurement_root"]),
        head=record["head"], after_monotonic_ns=second["checked_monotonic_ns"],
        before_monotonic_ns=min(c["started_monotonic_ns"] for c in captures),
        boot_id=second["boot_session_id"].lower())
    # The bundle carries an exact duplicate for custody, while replay retains
    # original absolute locators embedded by the live producer.
    retained = Path(custody) / "records/g10-custody" / manifest_path.parent.name
    if census_sources({"tree": retained}) != census_sources({"tree": manifest_path.parent}):
        raise HarvestRefusal("g10_retained_tree_mismatch")
    return {"path": str(manifest_path), "sha256": sha(manifest_path)}



def require_terminal_boundary(plan, terminal):
    """The chain writes STOP at one plan-bound path, never a supplied substitute."""
    expected = Path(plan.custody_root) / "night/transcript/post-bracket-terminal-boundary.json"
    record = read(Path(plan.custody_root) / "qualification-plan-record.json")
    if record.get("terminal_boundary_path") != str(expected) or Path(terminal) != expected:
        raise HarvestRefusal("terminal_boundary_path_mismatch")
    if list(Path(plan.custody_root).rglob("post-bracket-terminal-boundary.json")) != [expected]:
        raise HarvestRefusal("terminal_boundary_census_invalid")



def pin_only_head_extension(repository, armed_head, head):
    """Authenticate H_pin from Git objects without changing the live checkout."""
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value)
           for value in (armed_head, head)):
        raise ValueError("Phase G invalid head identity")
    command = ["git", "-C", str(repository)]
    if head == armed_head:
        return None
    if subprocess.run(command + ["merge-base", "--is-ancestor", armed_head, head],
                      capture_output=True, check=False).returncode != 0:
        raise ValueError("Phase G head is not descended from the armed head")
    try:
        changed = subprocess.check_output(command + ["diff", "--name-only", armed_head, head],
                                          text=True, stderr=subprocess.PIPE).splitlines()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("Phase G head extension is unavailable") from error
    if changed != ["configs/calibration/calibration_ledger_head.json"]:
        raise ValueError("Phase G head extension is not pin-only")
    try:
        raw = subprocess.check_output(command + ["show", head + ":" + changed[0]], stderr=subprocess.PIPE)
        pin = readiness.parse_json_bytes(raw)
    except (OSError, subprocess.CalledProcessError, readiness.ArmReadinessError) as error:
        raise ValueError("Phase G head extension pin is unavailable") from error
    from joulewise.calibration_ledger import LEDGER_SCHEMA, _head_pin
    if (not isinstance(pin, dict) or pin.get("ledger_schema") != LEDGER_SCHEMA
            or _head_pin(pin) is None):
        raise ValueError("Phase G head extension pin is malformed")
    return {"armed_head": armed_head, "head": head, "changed_paths": changed,
            "terminal_head_pin": pin}



def load_plan(path, purpose, *, now=time.time, clear=group_clear):
    from scripts.run_night import WINDOW_SHUTDOWN_GRACE_S
    plan = night_gate.NightPlan.from_mapping(read(path))
    previous_attempt(plan.previous_attempt)
    if plan.block_archive_root is None:
        raise HarvestRefusal("block_archive_root_required_or_invalid")
    verify_attempt_restore(plan)
    custody = Path(plan.custody_root)
    if Path(path).absolute().parent != custody or plan.receipt_class != "TRANSACTION_PACK":
        raise HarvestRefusal("qualification_plan_identity_invalid")
    records = night_gate._authenticate_pack_records(plan)
    authorization = records["authorization_record"]
    if (authorization["purpose"] != purpose or authorization["claim_eligible"] is not False
            or authorization["permitted_blocks"] != 1):
        raise HarvestRefusal("qualification_plan_identity_invalid")
    chain = Path(plan.chain_path)
    if sha(chain) != Path(plan.chain_sha256_path).read_text().split()[0]:
        raise HarvestRefusal("chain_digest_mismatch")
    if now() < plan.t0_epoch_s + plan.window_max_s + WINDOW_SHUTDOWN_GRACE_S:
        raise HarvestRefusal("harvest_before_completion_boundary")
    night = custody / "night"
    if not (night / "courier.sent").is_file() or not clear(night, plan_id=plan.plan_id):
        raise HarvestRefusal("delivery_missing_or_launcher_group_alive")
    return plan



def census_sources(sources):
    result = {}
    for name, path in sources.items():
        path = Path(path).absolute()
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise HarvestRefusal("source_symlink")
        rows = inventory(path)
        if any("link" in row for row in rows.values()):
            raise HarvestRefusal("source_symlink")
        result[name] = rows
    return result



def tree_hash(root):
    import hashlib
    rows = census_sources({"tree": root})["tree"]
    raw = "".join(f"{name}\0{row['sha256']}\n" for name, row in sorted(rows.items()) if "sha256" in row)
    return hashlib.sha256(raw.encode()).hexdigest()



def unchanged(sources, original):
    if census_sources(sources) != original:
        raise HarvestRefusal("source_tree_mutated")



def captured_battery_observation(path):
    """Read a native battery observation from a capture or the T-0 C3 receipt."""
    from joulewise import battery_float
    value = read(path)
    if value.get("schema") == battery_float.SCHEMA:
        observation = value
    else:
        candidates = [row.get("measured", {}).get("battery_float") for row in value.get("conditions", [])
                      if row.get("condition_id") == "C3" and "battery_float" in row.get("measured", {})]
        if len(candidates) != 1:
            raise HarvestRefusal("t0_battery_capture_missing")
        observation = candidates[0]
    stdout = observation.get("raw_stdout")
    if not isinstance(stdout, str):
        raise HarvestRefusal("t0_battery_raw_missing")
    raw = stdout.encode("utf-8")
    if readiness.sha256_bytes(raw) != observation.get("raw_stdout_sha256"):
        raise HarvestRefusal("t0_battery_raw_mismatch")
    return observation, raw



def battery_boundaries(path, digest, plan_id, *, plan_path=None):
    """Authenticate recorded #421 boundary probes with the shared raw parser."""
    from joulewise import battery_float
    authenticated_reference({"path": str(path), "sha256": digest})
    value = read(path)
    if (value.get("schema") != "joulewise.v5_qualification_battery_boundaries.v1"
            or value.get("plan_id") != plan_id
            or set(value.get("observations", {})) != {"arm", "publication", "t0"}):
        raise HarvestRefusal("battery_boundary_census_invalid")
    passed = True
    observed = {}
    for role, item in value["observations"].items():
        stored = read(authenticated_reference(item["record"]))
        raw = authenticated_reference(item["raw"]).read_bytes()
        if (stored.get("raw_stdout_sha256") != readiness.sha256_bytes(raw)
                or stored.get("plan_id") != plan_id
                or stored.get("schema") != battery_float.SCHEMA
                or stored.get("phase") != BATTERY_BOUNDARY_PHASES[role]):
            raise HarvestRefusal("battery_boundary_digest_or_identity_mismatch")
        if "source_capture" in stored:
            capture = authenticated_reference(stored["source_capture"])
            captured, original = captured_battery_observation(capture)
            if {k: v for k, v in stored.items() if k != "source_capture"} != captured or original != raw:
                raise HarvestRefusal("battery_boundary_capture_mismatch")
        observed[role] = stored
        if stored.get("probe_error") or stored.get("timed_out") or stored.get("exit_code") != 0 or stored.get("argv") != list(battery_float.IOREG_BATTERY_ARGV):
            passed = False
            continue
        try:
            parsed = battery_float.parse(raw, stored["wall_time_s"])
        except ValueError:
            passed = False
            continue
        if any(stored.get(key) != val for key, val in parsed.items()):
            raise HarvestRefusal("battery_boundary_replay_mismatch")
        passed = passed and parsed["passed"]
    authenticate_battery_lifecycle(value, observed, plan_path=plan_path)
    return passed



def authenticate_battery_lifecycle(value, observations, *, plan_path=None):
    """Bind readings to native check/install/T-0 records of this occurrence."""
    import math
    refs = value.get("lifecycle")
    if not isinstance(refs, dict) or set(refs) != {"plan", "prepare", "arm_check", "publication", "t0_receipt"}:
        raise HarvestRefusal("battery_boundary_lifecycle_missing")
    paths = {name: authenticated_reference(ref) for name, ref in refs.items()}
    if plan_path is not None and paths["plan"] != Path(plan_path):
        raise HarvestRefusal("battery_boundary_plan_locator_mismatch")
    plan = night_gate.NightPlan.from_mapping(read(paths["plan"]))
    if paths["t0_receipt"] != Path(plan.custody_root) / "night" / "receipt.json":
        raise HarvestRefusal("battery_boundary_t0_receipt_locator_mismatch")
    prepare, arm, publication, t0 = (read(paths[name]) for name in ("prepare", "arm_check", "publication", "t0_receipt"))
    if (plan.plan_id != value["plan_id"] or prepare.get("schema") != "joulewise.evidence_prepare.v1"
            or prepare.get("plan_id") != plan.plan_id
            or prepare.get("custody_root") != plan.custody_root
            or prepare.get("digests", {}).get(prepare.get("plan_path")) != refs["plan"]["sha256"]
            or arm.get("schema") != "joulewise.evidence_check.v1"
            or arm.get("prepare_sha256") != refs["prepare"]["sha256"]
            or arm.get("fake_launchctl") is not False
            or publication.get("schema") != "joulewise.evidence_install.v1"
            or publication.get("plan_sha256") != refs["plan"]["sha256"]
            or publication.get("published_plan") != str(paths["plan"])
            or publication.get("fake_launchctl") is not False
            or publication.get("outcome") != "installed"
            or t0.get("schema") != night_gate.SCHEMA or t0.get("plan_id") != plan.plan_id):
        raise HarvestRefusal("battery_boundary_lifecycle_identity_mismatch")
    arm_row = arm.get("checks", {}).get("battery_float", {})
    if (arm_row.get("record") != value["observations"]["arm"]["record"]
            or arm_row.get("raw") != value["observations"]["arm"]["raw"]
            or arm_row.get("observation") != observations["arm"]):
        raise HarvestRefusal("battery_boundary_arm_capture_mismatch")
    # Publication's native producer writes this observation in the immutable
    # install attempt, immediately before publishing the pinned plan.
    attempt = paths["publication"].parent
    if (publication.get("attempt_path") != str(attempt)
            or paths["publication"].name != "install.json"
            or authenticated_reference(value["observations"]["publication"]["record"]) != attempt / "battery-float-at-publication.json"
            or authenticated_reference(value["observations"]["publication"]["raw"]) != attempt / "battery-float-at-publication.ioreg"):
        raise HarvestRefusal("battery_boundary_publication_capture_mismatch")
    original, _raw = captured_battery_observation(paths["t0_receipt"])
    captured = {key: val for key, val in observations["t0"].items() if key != "source_capture"}
    if captured != original or observations["t0"].get("source_capture") != refs["t0_receipt"]:
        raise HarvestRefusal("battery_boundary_t0_capture_mismatch")
    def number(item):
        if type(item) not in (int, float) or not math.isfinite(item):
            raise HarvestRefusal("battery_boundary_timing_invalid")
        return item
    starts, ends, walls = {}, {}, {}
    for role, observation in observations.items():
        starts[role] = number(observation.get("monotonic_before_ns"))
        ends[role] = number(observation.get("monotonic_after_ns"))
        walls[role] = number(observation.get("wall_time_s"))
        if (type(starts[role]) is not int or type(ends[role]) is not int
                or not 0 <= starts[role] <= ends[role]):
            raise HarvestRefusal("battery_boundary_timing_invalid")
    if not (ends["arm"] < starts["publication"] and ends["publication"] < starts["t0"]
            and number(arm.get("started_epoch_s")) <= walls["arm"] <= number(arm.get("finished_epoch_s"))
            and arm["finished_epoch_s"] < number(publication.get("started_epoch_s"))
            # Native publish-install admits a check no older than 60 minutes.
            and publication["started_epoch_s"] - arm["finished_epoch_s"] <= 3600
            and publication["started_epoch_s"] <= walls["publication"] <= number(publication.get("published_epoch_s"))
            and publication["published_epoch_s"] < plan.t0_epoch_s
            and plan.t0_epoch_s <= walls["t0"] <= plan.t0_epoch_s + plan.window_max_s
            and ends["t0"] <= number(t0.get("authored_monotonic_ns"))):
        raise HarvestRefusal("battery_boundary_order_or_timing_invalid")



def disposition(occurrence, verdict, cause_classes, majority=None):
    # A RECOVER without an already reviewed named cure is END STATE. A later
    # explicit lead authority binds the one allowed s2; no automatic retry.
    end = verdict == "RECOVER"
    # Eligibility is a prospective lead decision, never automatic permission.
    return {"end_state": end, "s2_eligible": False,
            "next_step": ("design_consult_cold_gate" if end else
                          "r3_cure_and_head_coverage_required" if verdict == "RECOVER" else
                          "identical_byte_reharvest" if verdict == "REFUSED" else
                          "fresh_plan_after_cause_removed" if verdict == "NULL" else "lead_ratification")}



def release_metrics(*args, **kwargs):
    # Qualification PASS is deliberately incapable of releasing measurements.
    raise HarvestRefusal("claim_plan_seal_and_lead_release_required")



def boundary_sources(path):
    value = read(path)
    sources = {"battery-boundary-map": path}
    for role, item in value.get("observations", {}).items():
        identifier(role)
        for kind in ("record", "raw"):
            sources[f"battery-{role}-{kind}"] = authenticated_reference(item[kind])
        stored = read(sources[f"battery-{role}-record"])
        if "source_capture" in stored:
            sources[f"battery-{role}-capture"] = authenticated_reference(stored["source_capture"])
    for name, ref in (value.get("lifecycle") or {}).items():
        sources[f"battery-lifecycle-{identifier(name)}"] = authenticated_reference(ref)
    return sources



def regular_bytes(path, grammar):
    path = Path(path)
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise HarvestRefusal("null_restore_input_not_regular")
    return read_authentication_input(path, grammar=grammar, label="block-4 NULL reservation restore")



def validate_tail(seed, attempted, pin, reservation):
    """Use the existing ledger parser and shape; never redefine ledger rows."""
    pin_head = ledger._head_pin(pin)
    receipts, reasons = ledger._parse_ledger(seed)
    seed_head = (len(receipts), receipts[-1]["receipt_digest"] if receipts else ledger.GENESIS_DIGEST)
    if reasons or pin_head is None or pin_head != seed_head:
        raise HarvestRefusal("null_restore_seed_not_pinned_head")
    if not attempted.startswith(seed):
        raise HarvestRefusal("null_restore_seed_not_exact_prefix")
    tail = attempted[len(seed):]
    lines = tail.splitlines(keepends=True)
    if len(lines) != 2 or any(not line.endswith(b"\n") for line in lines):
        raise HarvestRefusal("null_restore_tail_not_one_reservation_unit")
    intent, row = (readiness.parse_json_bytes(line) for line in lines)
    if (not isinstance(row, dict) or row != reservation
            or row.get("event") != ledger.BRACKET_SESSION_OPEN_EVENT
            or not ledger._valid_session_receipt_shape(row)
            or row.get("sequence") != seed_head[0] + 2
            or intent.get("event") != ledger.APPEND_INTENT_EVENT
            or intent.get("sequence") != seed_head[0] + 1
            or intent.get("predecessor_digest") != seed_head[1]
            or row.get("predecessor_digest") != intent.get("receipt_digest")
            or intent.get("target_core") != ledger._target_core(row)
            or any(intent["target_core"].get(key) != row.get(key) for key in ("session_id", "plan_id"))):
        raise HarvestRefusal("null_restore_tail_not_attempt_reservation")
    complete, reasons = ledger._parse_ledger(attempted)
    if reasons or len(complete) != len(receipts) + 2:
        raise HarvestRefusal("null_restore_ledger_chain_invalid")
    return row



def require_null(harvest, plan, plan_digest):
    if (harvest.get("schema") != ATTEMPT_HARVEST_SCHEMA
            or harvest.get("verdict") != "NULL"
            or harvest.get("plan_id") != plan.plan_id or harvest.get("plan_sha256") != plan_digest):
        raise HarvestRefusal("null_restore_requires_attempt_null_harvest")
    started = Path(plan.custody_root) / "night/chain.started"
    if started.exists() or started.is_symlink():
        raise HarvestRefusal("null_restore_chain_started")



def flag(argv, name):
    if not isinstance(argv, list) or argv.count(name) != 1:
        raise HarvestRefusal("null_restore_reservation_argv_invalid")
    index = argv.index(name)
    if index + 1 >= len(argv):
        raise HarvestRefusal("null_restore_reservation_argv_invalid")
    return argv[index + 1]



def reservation_binding(plan, capture, row):
    """Bind the dropped row to the actual T-0 command and frozen ARM identity."""
    if (capture.get("schema_version") != COMMAND_CAPTURE_SCHEMA
            or capture.get("step_id") != "ledger-reservation" or capture.get("exit_code") != 0):
        raise HarvestRefusal("null_restore_reservation_capture_invalid")
    argv = capture.get("argv")
    expected_script = str(Path(plan.measurement_root) / "scripts/reserve_calibration_window_bracket.py")
    if (not isinstance(argv, list) or len(argv) < 2 or argv[1] != expected_script
            or "--execute" not in argv):
        raise HarvestRefusal("null_restore_reservation_argv_invalid")
    result = readiness.parse_json_bytes(capture.get("stdout", "").encode())
    if result.get("status") != "reserved" or result.get("receipt") != row:
        raise HarvestRefusal("null_restore_reservation_receipt_mismatch")
    pack = Path(plan.pack_night["pack_root"])
    frozen = read(pack / "calibration_plan.json")
    record = read(Path(plan.custody_root) / "qualification-plan-record.json")
    context = read(authenticated_reference(record["arm_context"]))
    for name, value in {"session-id": context["bracket_session_id"],
                        "plan-id": frozen["plan_id"], "plan-sha256": sha(pack / "calibration_plan.json"),
                        "runs-root": context["claim_runs_root"],
                        "pre-attempt-id": context["pre_attempt_id"],
                        "post-attempt-id": context["post_attempt_id"]}.items():
        if flag(argv, "--" + name) != value:
            raise HarvestRefusal("null_restore_reservation_identity_mismatch")
    for name in ("session_id", "window_id", "plan_id", "plan_sha256", "evidence_root_id", "runs_root"):
        if row[name] != flag(argv, "--" + name.replace("_", "-")):
            raise HarvestRefusal("null_restore_reservation_identity_mismatch")
    return Path(flag(argv, "--ledger")), Path(flag(argv, "--head-pin"))



def verify_restore(reference, previous_harvest, *, restored_ledger=None):
    """Replay saved attempted bytes and bind the next attempt to its NULL prior."""
    record = read(authenticated_reference(reference))
    expected = {"schema", "plan_id", "plan", "harvest", "seed", "reservation", "attempt_ledger",
                "restored_ledger", "head_pin", "head_pin_copy", "dropped_receipt_sha256"}
    if set(record) != expected or record["schema"] != NULL_RESTORE_SCHEMA or record["harvest"] != previous_harvest:
        raise HarvestRefusal("null_restore_record_identity_mismatch")
    plan_path = authenticated_reference(record["plan"])
    plan = night_gate.NightPlan.from_mapping(read(plan_path))
    harvest_path = authenticated_reference(record["harvest"])
    harvest = counted_attempt(read(harvest_path), harvest_path)
    require_null(harvest, plan, record["plan"]["sha256"])
    if record["plan_id"] != plan.plan_id or Path(reference["path"]) != Path(plan.custody_root) / "null-reservation-restore.json":
        raise HarvestRefusal("null_restore_record_identity_mismatch")
    if (Path(record["attempt_ledger"]["path"]) != Path(plan.custody_root) / "null-reservation-ledger.jsonl"
            or Path(record["reservation"]["path"]) != Path(plan.custody_root) / plan.pack_night["pack_id"] /
               "arm_readiness.t0.inputs/ledger-reservation.json"):
        raise HarvestRefusal("null_restore_custody_path_mismatch")
    seed = regular_bytes(authenticated_reference(record["seed"]), "jsonl")
    attempted = regular_bytes(authenticated_reference(record["attempt_ledger"]), "jsonl")
    capture = read(authenticated_reference(record["reservation"]))
    row = readiness.parse_json_bytes(capture["stdout"].encode())["receipt"]
    live, pin = reservation_binding(plan, capture, row)
    # The live pin may advance after this restore. Authenticate its retained
    # bytes against the path/digest recorded while the native lease was held.
    pin_path = authenticated_reference(record["head_pin_copy"])
    if (pin_path != Path(plan.custody_root) / "null-reservation-head-pin.json"
            or record["head_pin"] != {"path": str(pin), "sha256": record["head_pin_copy"]["sha256"]}
            or record["restored_ledger"] != {"path": str(live), "sha256": record["seed"]["sha256"]}):
        raise HarvestRefusal("null_restore_ledger_binding_mismatch")
    validate_tail(seed, attempted, read(pin_path), row)
    if row["receipt_digest"] != record["dropped_receipt_sha256"]:
        raise HarvestRefusal("null_restore_dropped_row_mismatch")
    # Writer verification checks the live seed. A later harvester replays the
    # retained pre-reservation seed, since its own reservation extended live.
    if restored_ledger is not None:
        path = authenticated_reference(restored_ledger)
        if restored_ledger["sha256"] != record["seed"]["sha256"] or regular_bytes(path, "jsonl") != seed:
            raise HarvestRefusal("null_restore_next_seed_mismatch")
    return record



def preflight_argv(repository):
    repository = Path(repository)
    return (str(repository / ".venv/bin/python"),
            str(repository / "scripts/collect_clock_reference.py"))


class NotDischarged(ValueError):
    pass



def read_json(path):
    if path.is_symlink():
        raise NotDischarged("symlink_in_custody")
    return readiness.parse_json_bytes(path.read_bytes(), require_canonical=True)



def anchor(value):
    return value["realtime_ns"] - value["monotonic_raw_ns"]



def residual_between(before, after, frequency):
    from joulewise import kernel_clock
    return kernel_clock.anchor_residual_ns(anchor(after) - anchor(before),
        after["monotonic_raw_ns"] - before["monotonic_raw_ns"], frequency)



def r0_residual(r0, stamp):
    from joulewise import kernel_clock
    return kernel_clock.anchor_residual_ns(
        anchor(stamp) - (r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"]),
        stamp["monotonic_raw_ns"] - r0["anchor_monotonic_raw_ns"], r0["kernel_frequency"])



def movement_record(before, after, frequency):
    from joulewise import kernel_clock
    return {"anchor_check_version": kernel_clock.ANCHOR_CHECK_VERSION,
            "absolute_movement_ns": abs(anchor(after) - anchor(before)),
            "residual_movement_ns": float(residual_between(before, after, frequency))}



def preflight_measurement(command, boot, *, repository=None):
    from joulewise import rehearsal_readers as author
    if (command["argv"] != list(preflight_argv(REPO_ROOT if repository is None else repository))
            or command["exit_code"] != 0):
        raise NotDischarged("g10_preflight_command_invalid")
    value = readiness.parse_json_bytes(command["stdout"].encode(), require_canonical=True)
    legs = author._validate_reference_object(value, kind="CLOCK_ATTESTATION",
        label="G10 preflight", boot_session_id=boot)
    started, finished = command["started"], command["finished"]
    if (any(s["boot_id"] != boot or not 0 <= s["read_skew_ns"] <= 1_000_000
            for s in (started, finished))
            or not started["monotonic_ns"] <= finished["monotonic_ns"]
            or not started["monotonic_raw_ns"] <= value["anchor_monotonic_raw_ns"]
                <= value["batch_finished_monotonic_raw_ns"] <= finished["monotonic_raw_ns"]):
        raise NotDischarged("g10_preflight_boot_or_order")
    if value["anchor_read_skew_ns"] > 1_000_000:
        raise NotDischarged("g10_preflight_read_skew")
    try:
        agreement = author._reference_agreement(legs, kind="CLOCK_ATTESTATION", label="G10 preflight")
        midpoint, bound = agreement.midpoint, agreement.bound
    except author.T0EvidenceAuthoringError as exc:
        if str(exc) != "G10 preflight bound exceeds 0.5 seconds":
            raise
        # The shared helper refuses above 0.5 s. Retain its same arithmetic
        # for that rejected measurement too; never admit it or resync it.
        lower = max(parsed.offset_s - parsed.uncertainty_s for _, parsed in legs)
        upper = min(parsed.offset_s + parsed.uncertainty_s for _, parsed in legs)
        midpoint = (lower + upper) / Decimal(2)
        bound = abs(midpoint) + (upper - lower) / Decimal(2)
    status = ("g10_preflight_offset_too_large" if bound > Decimal("0.400") else
              "g10_preflight_offset_too_small" if abs(midpoint) < Decimal("0.020") else "PASS")
    return {"midpoint_s": str(midpoint), "bound_s": str(bound), "status": status}



def verify_g10_custody(positive_path, manifest_path, *, code_root, head,
                       before_monotonic_ns, boot_id, after_monotonic_ns=None):
    """Replay the physical control's complete support census, never a locator alone."""
    positive_path, manifest_path = Path(positive_path), Path(manifest_path)
    root = manifest_path.parent
    if (manifest_path.name != "custody-manifest.json" or positive_path != root / "positive-control.json"
            or not root.is_absolute() or any(p.is_symlink() for p in (root, *root.parents))):
        raise NotDischarged("g10_custody_locator")
    manifest = read_json(manifest_path)
    if set(manifest) != {"files"} or not isinstance(manifest["files"], dict):
        raise NotDischarged("g10_manifest_schema")
    observed = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise NotDischarged("g10_custody_symlink")
        if path.is_file() and path != manifest_path:
            observed[path.relative_to(root).as_posix()] = readiness.sha256_bytes(path.read_bytes())
    if manifest["files"] != observed:
        raise NotDischarged("g10_custody_hash_or_census")
    from joulewise import rehearsal_readers as author, rehearsal_readers as t0_rehearsal
    from joulewise import kernel_clock
    from joulewise.hazards import network_time as network_time_off
    preflight = read_json(root / "commands/preflight.json")
    measurement = preflight_measurement(preflight, boot_id, repository=code_root)
    if measurement["status"] != "PASS" or read_json(root / "preflight.json") != measurement:
        raise NotDischarged("g10_preflight_measurement")
    before, after = read_json(root / "before.json"), read_json(root / "after.json")
    positive = read_json(positive_path)
    movement = read_json(root / "anchor-movement.json")
    residual_version = "anchor_check_version" in movement
    if residual_version:
        frequency = kernel_clock.validate_probe(before.get("kernel_frequency"))
        kernel_clock.validate_probe(after.get("kernel_frequency"))
        expected_movement = movement_record(before, after, frequency)
        control_moved = residual_between(before, after, frequency) > 5_000_000
    else:
        expected_movement = {"absolute_movement_ns": abs(anchor(after) - anchor(before))}
        control_moved = abs(anchor(after) - anchor(before)) > 5_000_000
    if (set(positive) != t0_rehearsal._POSITIVE_CONTROL_KEYS
            or positive["schema_version"] != t0_rehearsal.POSITIVE_CONTROL_SCHEMA
            or positive["performed_by"] != "Ed"
            or any(positive[key] is not True for key in
                   ("outside_t0_sequence", "network_time_reenabled", "forced_resync"))
            or positive["anchor_before_ns"] != anchor(before)
            or positive["anchor_after_ns"] != anchor(after)
            or not control_moved
            or positive["author_refusal_reason_code"] != REFUSAL
            or movement != expected_movement):
        raise NotDischarged("g10_anchor_or_record")
    on, execution = read_json(root / "commands/on.json"), read_json(root / "author-execution.json")
    response = read_json(root / "author.stdout.json")
    lineage = read_json(root / "author-input-lineage.json")
    r0_capture = read_json(root / "author-custody" / Path(lineage["pack_root"]).name /
                           author._INPUT_DIRECTORY / "clock-reference.json")
    r0 = readiness.parse_json_bytes(r0_capture["stdout"].encode())
    if residual_version:
        r0["kernel_frequency"] = kernel_clock.validate_probe(r0_capture.get("kernel_frequency"))
        if (frequency["raw_word"] != r0["kernel_frequency"]["raw_word"]
                or r0_residual(r0, before) > 5_000_000 or r0_residual(r0, after) <= 5_000_000):
            raise NotDischarged("g10_r0_binding")
        stream_max = r0_capture.get("t_stream_max_s")
        if stream_max is not None and not kernel_clock.frequency_gate(frequency, stream_max)["passes"]:
            raise NotDischarged("g10_frequency_gate")
        kernel_clock.validate_probe(read_json(root / "kernel-frequency-after-off.json"))
    r0_anchor = r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"]
    if (lineage["r0_anchor_ns"] != r0_anchor or r0["boot_session_id"].lower() != boot_id
            or (not residual_version and (abs(r0_anchor - anchor(before)) > 5_000_000
                or abs(r0_anchor - anchor(after)) <= 5_000_000))):
        raise NotDischarged("g10_r0_binding")
    if (on["argv"] != list(ON_ARGV) or on["exit_code"] != 0
            or " ".join(on["stdout"].split()).lower().rstrip(".") not in
               {"setusingnetworktime: on", "network time is already on"}
            or execution["exit_code"] != 2 or execution["present_namespaces"] != []
            or response.get("status") != "REFUSE" or response.get("kind") != "CLOCK_ATTESTATION"
            or response.get("reason_codes") != [REFUSAL] or response.get("detail") != ANCHOR_DETAIL
            or Path(execution["argv"][1]) != Path(code_root) / "scripts/author_arm_evidence_t0.py"
            or execution["argv"][2:] != ["--pack-root", lineage["pack_root"],
                "--custody-root", str(root / "author-custody")]):
        raise NotDischarged("g10_on_or_author_refusal")
    for label, command in (("preflight", preflight), ("on", on)):
        directory = root / "commands" / label
        if (read_json(directory / "started.json") != command["started"]
                or read_json(directory / "finished.json") != command["finished"]
                or (directory / "stdout.txt").read_bytes() != command["stdout"].encode()
                or (directory / "stderr.txt").read_bytes() != command["stderr"].encode()):
            raise NotDischarged("g10_command_support")
    off = network_time_off.read_receipt(root / network_time_off.RECEIPT_BASENAME,
                                       plan_id=root.name, window_id=root.name)
    polls = [read_json(path) for path in sorted((root / "polls").glob("*.json"))]
    if not polls or polls[-1] != after:
        raise NotDischarged("g10_poll_support")
    stamps = [preflight["started"], preflight["finished"], before, on["started"], on["finished"],
              *polls, after, execution["started"], execution["finished"]]
    times = [value["monotonic_ns"] for value in stamps]
    if (any(value["boot_id"] != boot_id or value["read_skew_ns"] > 1_000_000 for value in stamps)
            or times != sorted(times) or off["boot_id"] != boot_id
            or not times[-1] <= round(off["monotonic_s"] * 1e9) < before_monotonic_ns
            or (after_monotonic_ns is not None and not after_monotonic_ns < times[0])
            or lineage["boot_id"] != boot_id):
        raise NotDischarged("g10_boot_or_order")
    expected_codes = {"scripts/author_arm_evidence_t0.py", "joulewise/arm_readiness_evidence_t0.py",
                      "scripts/capture_t0_step.py", "scripts/collect_clock_reference.py", "joulewise/clock_reference.py"}
    if residual_version:
        expected_codes.add("joulewise/kernel_clock.py")
    if set(lineage["author_code_sha256"]) != expected_codes:
        raise NotDischarged("g10_code_inventory")
    for relative, digest in lineage["author_code_sha256"].items():
        raw = subprocess.check_output(["git", "-C", str(code_root), "show", f"{head}:{relative}"])
        if readiness.sha256_bytes(raw) != digest:
            raise NotDischarged("g10_code_pin")
    if read_json(root / "commands/off.json") != off:
        raise NotDischarged("g10_off_support")
    if ((root / "commands/off/stdout.txt").read_bytes() != off["stdout"].encode()
            or (root / "commands/off/stderr.txt").read_bytes() != off["stderr"].encode()):
        raise NotDischarged("g10_off_streams")
    outcome = read_json(root / "outcome.json")
    if outcome != {"status": "DISCHARGED", "positive_control_path": str(positive_path)}:
        raise NotDischarged("g10_outcome")
    return positive



def off_receipt_path(plan, night_dir=None):
    from joulewise.battery_records import off_receipt_path as locate
    return locate(plan, night_dir)
