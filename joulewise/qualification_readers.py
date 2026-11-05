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
    from joulewise import qualification_readers as writer
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
        if (plan_record.get("schema_version") != writer.ARM_ONLY_SCHEMA
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
    roster, auxiliary, brackets, nonsampling = writer.pack_roster(pack_root, binding["occurrence"])
    computed = writer.size_window(binding["occurrence"], sizing, roster=roster,
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

