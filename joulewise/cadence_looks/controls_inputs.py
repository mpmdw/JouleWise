"""Build the private ctl-01 roster and bind its native sources to two Checks."""

from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
import os
from pathlib import Path
import re

from .controls_analysis import ViewError, has_dose_quorum, prepare_admission, script_steps
from .controls_layout import GateRefusal, open_file, require_private, write_exclusive
from .controls_manifest import ISSUED_SETTINGS, STAGE1_SCHEMA, canonical
from .controls_print import CHANNELS, KIT_ID, MASTER_SEED, PILOT, REMAINDER, _hex_pin
from .controls_reader import (
    AC_POWERMODE,
    ELIGIBLE, LegTiming, ReaderBindingError, binding_projection, blind_stream, rail_timing, select_dc,
)
from .custody_pins import PinRefusal, safe_relative
from .description_inputs import PinnedInput
from .qualification_manifest import _decode
from .controls_time_fields import (
    BOOLEAN, EMPTY_ARRAY, INT64, INTEGER, NUMBER, OPAQUE_BOOLEAN, OPAQUE_FINITE_NUMBER, OPAQUE_INTEGER,
    OPAQUE_NONNEGATIVE_INTEGER, OPAQUE_STRING, STRING,
    DigestFields, DiscardedField, Nullable, RecordFields, RequiredRecordFields, TaggedFields, TimeFieldError, WireRecord,
    project_json,
)


IDS = PILOT + REMAINDER
INVENTORY_SCHEMA = "joulewise.cadence_ctl_inputs.v1"
CERTIFICATE_SCHEMA = "joulewise.cadence_ctl_channel_certificate.v1"
FILES = {
    "episode": "outputs/align_episode.json",
    "config": "config.json",
    "metadata": "metadata.json",
    "rails": "power_trace.csv",
}
SCRIPT_FIELDS = RequiredRecordFields(
    kind=STRING, hidden_tokens=INTEGER, cpu_s=INTEGER, gap_s=INTEGER, recovery_s=NUMBER,
    turn_tokens=[INTEGER],
)
SPEC_FIELDS = DigestFields(
    **dict.fromkeys(("schema", "campaign_id", "g0_role", "prefill_tokens", "leg_id", "seed",
                     "start_band", "decode_tokens", "g0_shape")),
    script=SCRIPT_FIELDS,
)
STEP_FIELDS = {"kind": STRING, "complete": BOOLEAN}
STEP_TIMES = dict.fromkeys(("started_ns", "ended_ns"), INT64)
CALL_RETURN_FIELDS = {
    **STEP_TIMES, "first_token_ns": Nullable(INT64), "context_tokens": INTEGER, "cached_prompt_tokens": INTEGER,
}
CALL_FIELDS = WireRecord({**STEP_FIELDS, "requested_tokens": INTEGER, "actual_tokens": Nullable(INTEGER)},
                         CALL_RETURN_FIELDS)
INTERVAL_TIMES = {**STEP_TIMES, **dict.fromkeys(("started_epoch_s", "ended_epoch_s"), OPAQUE_FINITE_NUMBER)}
INTERVAL_FIELDS = WireRecord({**STEP_FIELDS, "requested_s": NUMBER}, INTERVAL_TIMES)
CPU_FIELDS = WireRecord({**STEP_FIELDS, "requested_s": INTEGER},
                        {**INTERVAL_TIMES, "thread_cpu_ns": OPAQUE_NONNEGATIVE_INTEGER})
STEP_VARIANTS = {**dict.fromkeys(("turn", "hidden"), CALL_FIELDS),
                 **dict.fromkeys(("gap", "recovery"), INTERVAL_FIELDS), "cpu": CPU_FIELDS}
WORK_FIELDS = WireRecord(
    {"schema": STRING, "leg_id": STRING, "leg_spec_sha256": STRING, "complete": BOOLEAN,
     "script": SCRIPT_FIELDS, "steps": [TaggedFields("kind", STEP_VARIANTS)]},
    {"failed_envelope": RequiredRecordFields(
        **dict.fromkeys(("index", "context_tokens", "prefill_tokens", "decode_tokens", "hidden_tokens"), OPAQUE_INTEGER),
        start_ns=INT64, end_ns=INT64, first_token_ns=Nullable(INT64), tool_calls=EMPTY_ARRAY, logged=BOOLEAN,
    )},
)
REFERENCE_FIELDS = {"schema": None, "status": None, "source": {"run_id": None, "config_sha256": None},
                    "record_sha256": None}
RESULT_REQUIRED = {
    **dict.fromkeys(("leg_id", "leg_status", "bundle", "member_status", "g0_role", "script_record_sha256"), STRING),
    **dict.fromkeys(("g0_released", "script_complete"), BOOLEAN),
    "g0_reference_record_sha256": Nullable(STRING),
    "decode_tokens": Nullable(INTEGER), "prefill_tokens": Nullable(INTEGER),
}
RESULT_OPTIONAL = {
    **dict.fromkeys(("turn_start_ns", "turn_end_ns", "first_token_ns"), Nullable(INT64)),
    "config_sha256": STRING, "g0_outcome": Nullable(OPAQUE_STRING),
    "g0_wait_s": Nullable(OPAQUE_FINITE_NUMBER), "g0_timeout_s": OPAQUE_FINITE_NUMBER,
    "quiet_s": OPAQUE_FINITE_NUMBER, "prefill_chars": DiscardedField(OPAQUE_INTEGER), "decode_cap": OPAQUE_INTEGER,
    "decode_cap_reached": BOOLEAN, "episode_flags": [OPAQUE_STRING], "incomplete_reasons": [OPAQUE_STRING],
    "ac_powermode": Nullable(AC_POWERMODE), "quiet_spans_ns": [[INT64]], "g0_shape": OPAQUE_STRING,
    "g0_reference_source": Nullable(OPAQUE_STRING), "os_level_max": Nullable(OPAQUE_INTEGER),
    "pm_nominal": Nullable(OPAQUE_BOOLEAN),
}
BATTERY_SAMPLE = RequiredRecordFields(epoch_s=OPAQUE_FINITE_NUMBER, soc_pct=OPAQUE_INTEGER,
                                      state=Nullable(OPAQUE_STRING), ac=OPAQUE_BOOLEAN, raw=OPAQUE_STRING)
BATTERY_RESULT = RequiredRecordFields(
    samples=OPAQUE_INTEGER, valid_samples=OPAQUE_INTEGER, drain_pct_per_h=Nullable(OPAQUE_FINITE_NUMBER),
    drain_unavailable_reason=Nullable(OPAQUE_STRING),
    charge_resume_events=[RequiredRecordFields(epoch_s=OPAQUE_FINITE_NUMBER, soc_pct=OPAQUE_INTEGER,
                                              prior_soc_pct=OPAQUE_INTEGER)],
    charge_resume_soc_pct=Nullable(OPAQUE_INTEGER), first=Nullable(BATTERY_SAMPLE), last=Nullable(BATTERY_SAMPLE),
    resolution=OPAQUE_STRING,
)
RUNTIME_ONLY = {
    "cpu_busy_cores": [OPAQUE_FINITE_NUMBER], "cpu_busy_t_s": [OPAQUE_FINITE_NUMBER],
    "census": [RequiredRecordFields(
        label=OPAQUE_STRING, t_s=OPAQUE_FINITE_NUMBER,
        processes=[RequiredRecordFields(pid=OPAQUE_INTEGER, ppid=OPAQUE_INTEGER,
                                        pcpu=OPAQUE_FINITE_NUMBER, comm=OPAQUE_STRING)])],
    "load_journal_errors": [OPAQUE_STRING], "battery": BATTERY_RESULT,
}
RUNTIME_IDENTITY = dict.fromkeys(("schema", "kind", "backend"), STRING)
RESULT_FIELDS = WireRecord(RESULT_REQUIRED, {**RESULT_OPTIONAL, **RUNTIME_IDENTITY, **RUNTIME_ONLY})
RUNTIME_RESULT_FIELDS = WireRecord({**RESULT_REQUIRED, **RUNTIME_IDENTITY}, {**RESULT_OPTIONAL, **RUNTIME_ONLY})
NATIVE_RESULT_COPY = frozenset((
    "config_sha256", "g0_outcome", "g0_wait_s", "g0_timeout_s", "quiet_s", "prefill_chars", "decode_cap",
    "decode_cap_reached", "os_level_max", "pm_nominal", "incomplete_reasons", "ac_powermode", "quiet_spans_ns",
    "g0_shape", "g0_reference_source",
))
ATTEMPT_FIELDS = DigestFields.fromkeys(("attempt", "redone", "output_dir", "leg_status", "contaminated"))
CLOSE_FIELDS = {
    **dict.fromkeys(("span_id", "schema", "runner_kind", "mock", "rc", "legs_finished")),
    "desk_bundle_error": Nullable(OPAQUE_STRING),
    "roster": [None],
    "kit": RecordFields.fromkeys(("campaign_id", "sha256", "frozen_commit")),
    "feeds": {"meter": {"stop": {"rc": None, "proven_stopped": None}, "files": [
        {"path": None, "sha256": None},
    ]}},
    "span_result": Nullable({"outcome": None}),
    "steps": [{"name": None, "rc": None}],
    "legs": [{
        "leg_id": None, "attempts": [ATTEMPT_FIELDS],
        "summary": {"leg_id": None, "admitted": None},
        "span_reference": Nullable(dict.fromkeys(("leg_id", "attempt", "excluded"))),
    }],
}
LEG_RECORD_FIELDS = RequiredRecordFields(schema=STRING, spec=DigestFields(), attempts=[ATTEMPT_FIELDS],
                                         result=RESULT_FIELDS)
NATIVE_LEG_RECORD_FIELDS = RequiredRecordFields(
    LEG_RECORD_FIELDS,
    result=WireRecord({**RESULT_REQUIRED, **{key: RESULT_FIELDS[key] for key in NATIVE_RESULT_COPY}},
                      RESULT_FIELDS),
)
NATIVE_RUNTIME_RESULT_FIELDS = WireRecord(
    {**RESULT_REQUIRED, **RUNTIME_IDENTITY, **RUNTIME_ONLY,
     **{key: RESULT_OPTIONAL[key] for key in NATIVE_RESULT_COPY | {"episode_flags"}}},
    RUNTIME_RESULT_FIELDS,
)
TERMINAL_FIELDS = {"schema": None, "status": None, "files": {"runtime_result.json": None}}
STREAM = re.compile(r"hazards/meter/stream-[0-9]{3,}\.jsonl")


def digest(payload):
    return sha256(payload).hexdigest()


def _require(condition, token="INPUT_BINDING"):
    if not condition:
        raise GateRefusal(token)


def _path(value):
    _require(safe_relative(value) and all(part.casefold() != ".git" for part in value.split("/")))
    return value


def _protected_bytes(path):
    with open_file(path) as stream:
        require_private(stream.fileno(), directory=False)
        return stream.read()


def load_canonical(raw):
    document = _decode(raw)
    _require(canonical(document) == raw)
    return document


def _pin(role, path, entry, parent):
    _require(_hex_pin(entry["sha256"], 64) and type(entry["size"]) is int and entry["size"] >= 0)
    return dict(role=role, path=_path(path), size=entry["size"], sha256=entry["sha256"],
                parent_sha256=parent)


def _read(path, entry):
    # PinnedInput hashes and parses one immutable buffer, never opens a
    # compressed sibling, and checks the terminal SHA and exact byte count.
    try:
        with PinnedInput(path, entry).open("rb") as stream:
            return stream.read()
    except FileNotFoundError as error:
        raise GateRefusal("INPUT_CHANNELS") from error
    except (OSError, PinRefusal, ValueError) as error:
        raise GateRefusal("INPUT_BINDING") from error


def _entries(pins):
    return {entry["path"]: entry for entry in pins["files"]}


def _entry_from_check(check, role, path, expected_sha256=None, *, parent=None):
    entry = _entries(check).get(_path(path))
    _require(entry is not None, "INPUT_CHANNELS")
    if expected_sha256 is not None:
        _require(entry["sha256"] == expected_sha256)
    return _pin(role, path, entry, parent or check["offload_manifest_sha256"])


def _close(kit_sha, runner_commit, check, root, ids, *, synthetic):
    entry = _entry_from_check(check, "close_receipt", "runner_receipt.json")
    document = project_json(_read(root / entry["path"], entry), CLOSE_FIELDS, strict=True)
    _require(document["span_id"] == check["span_id"], "INPUT_CHANNELS")
    _require(document["schema"] == "joulewise.cadence_span_receipt.v1"
             and document["runner_kind"] == "cadence-ctl-v1"
             and document["mock"] is synthetic
             and type(document["rc"]) is int and document["rc"] == 0
             and document["roster"] == list(ids) and document["legs_finished"] == len(ids)
             and [row["leg_id"] for row in document["legs"]] == list(ids)
             and document["kit"] == {"campaign_id": KIT_ID, "sha256": kit_sha,
                                     "frozen_commit": runner_commit})
    meter = document["feeds"]["meter"]
    _require(meter["stop"]["rc"] == 0 and meter["stop"]["proven_stopped"] is True)
    if not synthetic:
        _require(document["span_result"]["outcome"] == "MEASURED_OK"
                 and not document.get("desk_bundle_error"))
        steps = document["steps"]
        restore, = (row for row in steps if row["name"] == "restore")
        _require(restore["rc"] == 0)
    streams = []
    names = set()
    for row in meter["files"]:
        name = _path(row["path"])
        if not STREAM.fullmatch(name):
            _require(not Path(name).name.startswith("stream-"), "INPUT_CHANNELS")
            continue
        _require(name.casefold() not in names and _hex_pin(row["sha256"], 64))
        names.add(name.casefold())
        streams.append(_entry_from_check(check, "stream", name, row["sha256"], parent=entry["sha256"]))
    return entry, document, streams


def _kit_inputs(raw, runner_commit, *, synthetic):
    kit = _decode(raw)
    _require(kit["schema"] == "joulewise.cadence_campaign_kit.ctl.v1" and kit["campaign_id"] == KIT_ID
             and kit["runner"]["kind"] == "cadence-ctl-v1"
             and kit["status"] == ("draft" if synthetic else "issued")
             and kit["ruling"]["authorizes_spans"] is (not synthetic)
             and (synthetic or kit["frozen"]["commit"] == runner_commit)
             and kit["seed_law"]["master_seed"] == MASTER_SEED
             and kit["layout"] == [list(PILOT), list(REMAINDER)]
             and tuple(row["leg_id"] for row in kit["legs"]) == IDS)
    scripts = [leg["script"] for leg in kit["legs"]]
    _require(Counter(script["kind"] for script in scripts) ==
             {"hidden": 6, "cpu": 3, "split": 1, "plain": 1, "extra-turn": 1}
             and scripts[0]["kind"] == "extra-turn" and scripts[3]["kind"] == "cpu"
             and sorted(script["hidden_tokens"] for script in scripts if script["kind"] == "hidden")
             == sorted(ISSUED_SETTINGS["hidden_tokens"] * 2)
             and sorted(script["cpu_s"] for script in scripts if script["kind"] == "cpu") == [10, 30, 90]
             and all(script["recovery_s"] == ISSUED_SETTINGS["recovery_s"] for script in scripts))
    split, = (i for i, row in enumerate(scripts) if row["kind"] == "split")
    plain, = (i for i, row in enumerate(scripts) if row["kind"] == "plain")
    _require(split >= 3 and plain >= 3 and abs(split - plain) == 1
             and scripts[split]["gap_s"] == ISSUED_SETTINGS["gap_s"]
             and kit["legs"][split]["seed"] == kit["legs"][plain]["seed"])
    return dict(zip(IDS, kit["legs"], strict=True))


def _check_script_requests(work, issued):
    try:
        script_steps(work, issued["kind"], allow_interrupted=not work["complete"])
    except ViewError as error:
        raise TimeFieldError("invalid native script step record") from error
    if work["complete"] and any(row["complete"] is not True for row in work["steps"]):
        raise TimeFieldError("incomplete step in completed native script")
    turns = iter(issued["turn_tokens"])
    intervals = {"cpu": "cpu_s", "gap": "gap_s", "recovery": "recovery_s"}
    for index, row in enumerate(work["steps"]):
        kind = row["kind"]
        trailing = not work["complete"] and index == len(work["steps"]) - 1 and not row["complete"]
        if kind in ("turn", "hidden"):
            if row["actual_tokens"] is None:
                if not trailing or {"first_token_ns", "context_tokens", "cached_prompt_tokens"} & row.keys():
                    raise TimeFieldError("invalid native interrupted call")
            elif (CALL_RETURN_FIELDS.keys() - row.keys()
                  or not 0 <= row["cached_prompt_tokens"] <= row["context_tokens"]):
                raise TimeFieldError("missing or invalid native returned call fields")
        else:
            required = INTERVAL_TIMES.keys() | ({"thread_cpu_ns"} if kind == "cpu" else set())
            if trailing:
                required = {"started_ns", "started_epoch_s"}
            if (required - row.keys()
                    or ("ended_ns" in row) != ("ended_epoch_s" in row)
                    or (kind == "cpu" and ("ended_ns" in row) != ("thread_cpu_ns" in row))):
                raise TimeFieldError("missing or unmatched native interval stamps")
        if kind == "turn":
            actual, expected = row["requested_tokens"], next(turns, None)
        elif kind == "hidden":
            actual, expected = row["requested_tokens"], issued["hidden_tokens"]
        else:
            actual, expected = row["requested_s"], issued[intervals[kind]]
        if actual != expected:
            raise TimeFieldError("native script step request differs from issued dose")
    if work["complete"] and next(turns, None) is not None:
        raise TimeFieldError("issued visible calls missing from native script")


def _terminal(root, check, close_leg, kit_leg, ordinal, *, synthetic):
    leg_id = kit_leg["leg_id"]
    prefix = f"legs/{leg_id}/"
    leg_record = _entry_from_check(check, "leg_record", prefix + "leg_record.json")
    leg_spec = _entry_from_check(check, "leg_spec", prefix + "leg_spec.json")
    record_fields = LEG_RECORD_FIELDS if synthetic else NATIVE_LEG_RECORD_FIELDS
    record = project_json(_read(root / leg_record["path"], leg_record), record_fields, strict=True)
    # Both the runner's file writer and its script binding sort object keys.
    # Compact the verified tokens to obtain the binding without decoding extras.
    spec, canonical_spec_sha = project_json(_read(root / leg_spec["path"], leg_spec), SPEC_FIELDS, strict=True)
    role = "capture" if ordinal == 0 else "consume"
    _require(record["schema"] == "joulewise.cadence_leg_record.v1" and record["spec"][1] == canonical_spec_sha
             and spec["schema"] == "joulewise.cadence_leg_spec.ctl.v1"
             and spec["campaign_id"] == KIT_ID and spec["g0_role"] == role
             and spec["prefill_tokens"] == ISSUED_SETTINGS["prefill_tokens"]
             and all(spec[key] == kit_leg[key] for key in
                     ("leg_id", "seed", "start_band", "script", "prefill_tokens", "decode_tokens", "g0_shape")))
    # The pinned writer serializes the same attempt objects with sorted keys
    # in both files. Bind their tokens while leaving diagnostics unconverted.
    attempts = [attempt for attempt, _ in record["attempts"]]
    _require(attempts and record["attempts"] == close_leg["attempts"]
             and all(type(row["attempt"]) is int and row["attempt"] == i and row["redone"] is (i < len(attempts))
                     for i, row in enumerate(attempts, 1)))
    selected = attempts[-1]
    runtime = _path(selected["output_dir"])
    _require(runtime == prefix + "runtime" and selected["redone"] is False)
    terminal = _entry_from_check(check, "terminal_map", runtime + "/runtime_custody.json")
    # The terminal map names the exact run directory from the projected result.
    terminal_raw = _read(root / terminal["path"], terminal)
    custody = project_json(terminal_raw, TERMINAL_FIELDS, strict=True)
    _require(custody["schema"] == "joulewise.align.r1_runtime_custody.v1" and custody["status"] == "complete")

    def file(role, member):
        pin = custody["files"].get(member)
        _require(pin is not None, "INPUT_CHANNELS")
        _require(_hex_pin(pin, 64))
        return _entry_from_check(check, role, runtime + "/" + member, pin, parent=terminal["sha256"])

    result_entry = file("result", "runtime_result.json")
    result_fields = RUNTIME_RESULT_FIELDS if synthetic else NATIVE_RUNTIME_RESULT_FIELDS
    result = project_json(_read(root / result_entry["path"], result_entry), result_fields, strict=True)
    expected_turn = {"turn_start_ns", "turn_end_ns", "first_token_ns"} if result["prefill_tokens"] is not None else set()
    if expected_turn - result.keys() or expected_turn - record["result"].keys():
        raise TimeFieldError("missing native runtime turn fields")
    _require(result["schema"] == "joulewise.align.r1_runtime_result.v1"
             and result["kind"] == "cadence-leg" and result["leg_id"] == leg_id
             and result["g0_role"] == role and (synthetic or result["backend"] != "synthetic")
             and result["leg_status"] == selected["leg_status"]
             and all(value == result[key] for key, value in record["result"].items()
                     if key in result and key != "script_complete")
             and all(key in record["result"] for key in ("leg_id", "leg_status", "bundle", "g0_released",
                                                        "g0_role", "script_record_sha256")))
    admitted = close_leg["summary"]["admitted"]
    dispatched = result["g0_released"]
    _require(close_leg["summary"]["leg_id"] == leg_id and type(admitted) is bool and type(dispatched) is bool
             and (not admitted or (dispatched and result["leg_status"] == "complete"
                                   and result["member_status"] == "succeeded" and not selected["contaminated"])))
    script_complete = result.get("script_complete")
    if (type(script_complete) is not bool or record["result"].get("script_complete") is not script_complete
            or (script_complete and not dispatched)
            or (not script_complete and (admitted or dispatched and result["leg_status"] == "complete"))):
        raise TimeFieldError("inconsistent native admission or terminal completion")
    bundle = _path(result["bundle"])
    _require(bundle.startswith("runs/") and len(bundle.split("/")) == 2)
    member_files = {bundle + "/" + member: None for member in (*FILES.values(),
                                                               "outputs/align_window_reference.json")}
    member_files["script-work.json"] = None
    custody = project_json(terminal_raw, {"files": member_files}, strict=True)
    run_id = bundle.split("/")[1]
    files = {"leg_record": leg_record, "leg_spec": leg_spec, "terminal_map": terminal, "result": result_entry}
    hidden_delivered = work = None
    if dispatched:
        script = file("script", "script-work.json")
        files["script"] = script
        work = project_json(_read(root / script["path"], script), WORK_FIELDS, strict=True)
        _require(result["script_record_sha256"] == script["sha256"]
                 and work["schema"] == "joulewise.cadence_script_work.v1" and work["leg_id"] == leg_id
                 and work["leg_spec_sha256"] == canonical_spec_sha and work["script"] == spec["script"])
        if work.get("complete") is not script_complete:
            raise TimeFieldError("native work completion disagrees with both result records")
        hidden = [step["actual_tokens"] for step in work["steps"] if step["kind"] == "hidden"]
        if len(hidden) == 1:
            hidden_delivered = hidden[0]
        for name, member in FILES.items():
            files[name] = file(name, bundle + "/" + member)
    if role == "capture":
        _require(admitted and dispatched, "INPUT_CHANNELS")
        reference_pin = file("reference", bundle + "/outputs/align_window_reference.json")
        files["reference"] = reference_pin
        reference = project_json(_read(root / reference_pin["path"], reference_pin), REFERENCE_FIELDS)
        _require(reference["schema"] == "joulewise.align_window_reference.v1" and reference["status"] == "captured"
                 and reference["source"] == {"run_id": run_id, "config_sha256": files["config"]["sha256"]})
        reference_sha = reference["record_sha256"]
    else:
        reference_sha = result["g0_reference_record_sha256"]
    _require(_hex_pin(reference_sha, 64))
    position = {
        "attempt": selected["attempt"], "role": role, "reference_sha256": reference_sha,
        "kind": spec["script"]["kind"], "admitted": admitted, "g0_released": dispatched,
        "leg_status": result["leg_status"], "script_complete": result["script_complete"],
        "hidden_delivered": hidden_delivered, "spec_sha256": canonical_spec_sha,
        "span_id": check["span_id"], "bundle": runtime + "/" + bundle, "run_id": run_id, "files": files,
    }
    return position, work


def admit_leg(position, work, issued, plan):
    """Apply the single scientific admission predicate to a bound leg."""
    if work is not None:
        _check_script_requests(work, issued)
    episode = plan.episode.projected_episode if plan is not None else None
    traces = plan.trace_timing() if plan is not None else None
    return prepare_admission(position, episode, work, issued, traces)


@dataclass
class Inputs:
    source: Path
    private: Path
    inventory: dict
    issued: dict
    legs: dict = field(default_factory=dict)
    certificates: dict = field(default_factory=dict)
    admissions: dict = field(default_factory=dict)
    timing: dict = field(default_factory=dict)

    @property
    def positions(self):
        return self.inventory["positions"]

    @property
    def spans(self):
        return self.inventory["spans"]

    def read_entry(self, span, entry):
        return _read(self.source / span / entry["path"], entry)

    def certificate(self, leg):
        pin = self.positions[leg]["certificate"]
        raw = _protected_bytes(self.private / pin["path"])
        if len(raw) != pin["size"] or digest(raw) != pin["sha256"]:
            raise ReaderBindingError("certificate bytes")
        return load_canonical(raw)

    def stage1_bytes(self):
        inputs = canonical(self.inventory)
        roster = canonical(dict(schema=STAGE1_SCHEMA, n_legs=sum(row["admitted"] for row in self.legs.values()),
                                legs=self.legs, input_inventory_sha256=digest(inputs)))
        return roster, inputs

    def verify_stage1(self, stage):
        roster, _ = self.stage1_bytes()
        if stage.inventory_sha256 != digest(canonical(self.inventory)) or stage.public["stage1_sha256"] != digest(roster):
            raise ReaderBindingError("stage-1 inventory")


def _make_inputs(source, private, kit_raw, checks, runner_commit, *, synthetic):
    kit_sha = digest(kit_raw)
    kit = _kit_inputs(kit_raw, runner_commit, synthetic=synthetic)
    inventory = dict(schema=INVENTORY_SCHEMA, kit_sha256=kit_sha, runner_commit=runner_commit,
                     spans={}, positions={})
    result = Inputs(source, private, inventory, kit)
    episode_ids = set()
    _require(len(checks) == 2 and len({row["span_id"].casefold() for row in checks}) == 2
             and len({row["check_item"] for row in checks}) == len({row["close_item"] for row in checks}) == 2)
    for number, (ids, check) in enumerate(zip((PILOT, REMAINDER), checks, strict=True), 1):
        span_id = check["span_id"]
        root = source / span_id
        _require(check["runner_commit"] == runner_commit)
        close_entry, close, streams = _close(kit_sha, runner_commit, check, root, ids, synthetic=synthetic)
        stream_views = tuple(blind_stream(entry["path"], _read(root / entry["path"], entry)) for entry in streams)
        span = dict(layout_index=number, close_item=check["close_item"], check_item=check["check_item"],
                    offload_manifest_sha256=check["offload_manifest_sha256"], close_receipt=close_entry,
                    streams=streams, capture_leg=ids[0])
        result.spans[span_id] = span
        for ordinal, (leg_id, close_leg) in enumerate(zip(ids, close["legs"], strict=True)):
            position, work = _terminal(root, check, close_leg, kit[leg_id], ordinal, synthetic=synthetic)
            position.update(span_index=number, disposition_sha256=None, certificate=None)
            result.positions[leg_id] = position
            if ordinal == 0:
                span.update(capture_attempt=position["attempt"], reference_sha256=position["reference_sha256"],
                            capture_run_id=position["run_id"], capture_config_sha256=position["files"]["config"]["sha256"],
                            reference=position["files"]["reference"])
            _require(position["reference_sha256"] == span["reference_sha256"])
            if ordinal and not synthetic:
                status = close_leg["span_reference"]
                _require((status["leg_id"], status["attempt"], status["excluded"]) ==
                         (ids[0], span["capture_attempt"], False))

            files = position["files"]
            episode_id = episode_sha = script_sha = None
            issued = kit[leg_id]["script"]
            if position["g0_released"]:
                payloads = {name: _read(root / files[name]["path"], files[name]) for name in FILES}
                timing, period, evidence = binding_projection(
                    payloads["episode"], payloads["config"], payloads["metadata"],
                    run_id=position["run_id"], config_sha256=files["config"]["sha256"], synthetic=synthetic,
                )
                if timing.episode_id in episode_ids:
                    raise TimeFieldError("duplicate native episode identity")
                episode_ids.add(timing.episode_id)
                rail = rail_timing(payloads["rails"], timing, period, evidence)
                dc = select_dc(timing, stream_views)
                plan = LegTiming(timing, rail, evidence, dc)
                result.timing[leg_id] = plan
                admission = admit_leg(position, work, issued, plan)
                episode_id, episode_sha, script_sha = timing.episode_id, files["episode"]["sha256"], files["script"]["sha256"]
                certificate = canonical({
                    "schema": CERTIFICATE_SCHEMA, "leg_id": leg_id, "span_id": span_id,
                    "episode_sha256": episode_sha, "rails": rail.evidence(),
                    "admission": admission.disposition, "admission_reason": admission.reason,
                    "fit_channels": [name for name in CHANNELS if admission.admitted
                                     and position["kind"] == "hidden" and admission.channels[name].fit_supported],
                    "input_sha256": {name: pin["sha256"] for name, pin in files.items()},
                    "stream_sha256": {entry["path"]: entry["sha256"] for entry in streams},
                    **dc.evidence(),
                })
                result.certificates[leg_id] = certificate
                position["certificate"] = _pin("certificate", f"certificates/{leg_id}.json",
                                               {"size": len(certificate), "sha256": digest(certificate)},
                                               close_entry["sha256"])
            else:
                admission = admit_leg(position, None, issued, None)
            result.admissions[leg_id] = admission
            result.legs[leg_id] = {
                "identity": [KIT_ID, kit_sha, runner_commit, number, leg_id, position["attempt"]],
                "role": position["role"], "reference": position["reference_sha256"],
                "script_sha": script_sha, "kind": position["kind"], "admitted": position["admitted"],
                "g0_released": position["g0_released"], "episode_id": episode_id, "episode_sha256": episode_sha,
            }
    return result


def make_inputs(source, private, kit_raw, checks, runner_commit, *, synthetic=False):
    try:
        return _make_inputs(source, private, kit_raw, checks, runner_commit, synthetic=synthetic)
    except (FileNotFoundError, TimeFieldError) as error:
        raise GateRefusal("INPUT_CHANNELS") from error
    except (AttributeError, KeyError, TypeError, ValueError, OSError, OverflowError) as error:
        raise GateRefusal("INPUT_BINDING") from error


def apply_disposition(inputs, disposition_raw):
    if disposition_raw is None:
        dispositions = {}
        disposition_sha = None
    else:
        document = _decode(disposition_raw)
        _require(document.keys() == {"schema", "legs"}
                 and document["schema"] == "joulewise.cadence_ctl_dc_disposition.v1",
                 "INPUT_CHANNELS")
        dispositions = {row["leg_id"]: row for row in document["legs"]}
        _require(dispositions and len(dispositions) == len(document["legs"]), "INPUT_CHANNELS")
        disposition_sha = digest(disposition_raw)
    disposed_legs = frozenset(dispositions)
    for leg, raw in inputs.certificates.items():
        certificate = load_canonical(raw)
        code = certificate["dc_code"]
        row = dispositions.pop(leg, None)
        if code == "ok":
            _require(row is None, "INPUT_CHANNELS")
        else:
            _require(code in ELIGIBLE and row == {"leg_id": leg, "code": code, "certificate_sha256": digest(raw)},
                     "INPUT_CHANNELS")
    _require(not dispositions, "INPUT_CHANNELS")
    if disposition_sha is not None:
        # Authorize the requested DC exclusions against the issued roster.
        # The actual fit quorum below also accounts for the blind verdicts.
        authorized_doses = (row["script"]["hidden_tokens"] for leg, row in inputs.issued.items()
                            if row["script"]["kind"] == "hidden" and leg not in disposed_legs)
        _require(has_dose_quorum(authorized_doses), "INPUT_CHANNELS")
        for position in inputs.positions.values():
            position["disposition_sha256"] = disposition_sha
    for name in CHANNELS:
        doses = (inputs.positions[leg]["hidden_delivered"] for leg, admission in inputs.admissions.items()
                 if admission.admitted and inputs.positions[leg]["kind"] == "hidden"
                 and admission.channels[name].fit_supported)
        _require(has_dose_quorum(doses), "insufficient_legs")


def write_or_compare(directory, name, data):
    try:
        write_exclusive(directory, name, data)
        os.fsync(directory)
    except FileExistsError:
        handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        with os.fdopen(handle, "rb") as stream:
            require_private(handle, directory=False)
            _require(stream.read() == data)
        os.fsync(directory)
