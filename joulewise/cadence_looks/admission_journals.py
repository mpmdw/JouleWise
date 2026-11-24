"""The selected runtime bundle's journals as the pinned leg runtime writes them (RL-184 section 3.3).

``validate_bundle`` admits ``config.json``, ``events.jsonl``, ``outputs/align_turns.jsonl``,
``outputs/align_thermal.jsonl`` and the salvage journal ``outputs/align_runtime_events.jsonl``. The producers are
identical at the three rostered writer revisions (b4b6aeb19, 2d347f721, 6e9d42f1d):

* event rows: ``joulewise/bundle.py:1002-1011`` (five members), from the MLX adapter
  (``joulewise/adapters/mlx_runtime.py:754-992,1195-1208``), the endpoint (``joulewise/align/apple/endpoint.py:724-755``,
  which adds ``align_turn_index``), the thermal session (``joulewise/align/apple/thermal_gates.py:515-669``), the
  workload's zero-generation observations (``joulewise/align/apple/workload.py:494-542``) and the controller
  (``joulewise/controller.py``; ``joulewise/bundle.py:1193-1210``);
* the salvage journal: ``workload.py:811-841``, the failed episode's buffered runtime events in order;
* turns: ``endpoint.py:724-814``; the thermal journal: ``joulewise/align/apple/thermal.py:54-201`` and the session's
  gate rows; config: ``BenchmarkConfig.to_dict()`` of the registered template.

The registered cadence task is one turn with no tools (``joulewise/align/apple/r1_runtime.py:756-805``), so no
``align_tool_*`` phase is admitted (lead ruling F4). A refusal names a file and a member, never a value.
"""
from __future__ import annotations

import hashlib
import json

from joulewise.cadence_looks.admission_shape import (
    BOOL, DIGEST, FLOAT, INT, MEASURED, NAT, NUM, STR, TEXT, arr, const, either, enum, mapping, nullable, obj, refuse,
    rx)

EVENTS = "events.jsonl"
TURNS = "outputs/align_turns.jsonl"
THERMAL = "outputs/align_thermal.jsonl"
CONFIG = "config.json"
SALVAGE = "outputs/align_runtime_events.jsonl"

THERMAL_SCHEMA = "joulewise.align_thermal.v1"
SENSOR = rx(r"[TF][!-~]{3}")
TEMPERATURE = rx(r"T[!-~]{3}")
FAN = rx(r"F[!-~]Ac")


# ===================================================================================================== stamps
NS_STAMP = obj({"epoch_ns": INT, "monotonic_before_ns": INT, "monotonic_after_ns": INT, "wall_resolution_ns": INT,
                "monotonic_resolution_ns": INT})                       # thermal_gates.py _stamp_record
S_STAMP = obj({"epoch_s": FLOAT, "monotonic_before_s": NUM, "monotonic_after_s": NUM, "wall_resolution_s": NUM,
               "monotonic_resolution_s": NUM})                         # joulewise/clock.py ClockStamp
SIDE_STAMP = obj({"wall_ns": INT, "monotonic_ns": INT, "monotonic_raw_ns": INT})   # hazards/base.py:59-67


# =================================================================================================== intervals
def _interval(value, where, selected=None):
    """ThermalSession._wait's row (thermal_gates.py:636-648); ``resume_hold`` adds ``condition_met_stamp`` to a
    hold. A released interval carries its release, its exit sample and its reference."""
    kind = value.get("kind") if type(value) is dict else None
    enum("G0", "G1", "H")(kind, f"{where}.kind")
    optional = {"condition_met_stamp": NS_STAMP} if kind == "H" else {}
    obj({"kind": STR, "turn": NAT, "token_count": nullable(NAT), "start_ns": INT, "end_ns": INT,
         "entry_stamp": NS_STAMP, "exit_stamp": NS_STAMP, "entry_epoch_s": FLOAT, "exit_epoch_s": FLOAT,
         "clock": const("episode_monotonic_ns"), "duration_s": NUM, "reference": nullable(lambda v, w: None),
         "release": obj({"fast_c": nullable(NUM), "slow_c": nullable(NUM)}), "slope_c_per_min": nullable(NUM),
         "entry_slope_c_per_min": NUM, "entry_sensors": mapping(NUM, SENSOR), "exit_sample_ns": nullable(INT),
         "outcome": enum("released", "timeout", "deadman", "unobserved")}, optional)(value, where)
    if value["turn"] != 0:
        refuse(f"{where}.turn", "not the registered task's single turn")
    if value["entry_sensors"] and selected is not None and set(value["entry_sensors"]) != selected:
        refuse(f"{where}.entry_sensors", "not the selected keys of the last reading before entry")
    # G0 and G1 wait before the turn; a hold waits between decode chunks and knows its token count
    if (kind == "H") != (value["token_count"] is not None):
        refuse(f"{where}.token_count", "a count exactly on a hold")
    reference = value["reference"]
    if reference is not None:
        if kind == "G0":
            obj({"fast_c": NUM, "slow_c": NUM, "source_member": STR, "span_ns": arr(INT, least=2, most=2)},
                {"span_epoch_ns": arr(INT, least=2, most=2), "coverage_fraction": NUM, "samples": NAT})(
                reference, f"{where}.reference")
        else:                                           # the episode reference is G0's release (thermal_gates:628)
            obj({"fast_c": NUM, "slow_c": NUM})(reference, f"{where}.reference")
    if value["outcome"] == "released":
        if reference is None or value["exit_sample_ns"] is None or value["slope_c_per_min"] is None or any(
                value["release"][k] is None for k in ("fast_c", "slow_c")):
            refuse(where, "a released interval without its reference, release sample and slope")
    elif value["outcome"] == "unobserved" and reference is not None and value["exit_sample_ns"] is not None:
        refuse(f"{where}.outcome", "unobserved with a reference and a sample")
    if (value["exit_sample_ns"] is None) != (value["release"]["fast_c"] is None and value["release"]["slow_c"] is None):
        refuse(f"{where}.release", "release values exactly when an exit sample exists")
    if value["entry_epoch_s"] > value["exit_epoch_s"] or value["start_ns"] > value["end_ns"]:
        refuse(where, "an interval that ends before it starts")
    if "condition_met_stamp" in value and value["outcome"] != "released":
        refuse(f"{where}.condition_met_stamp", "a resumed hold is a released hold")


# ======================================================================================================= events
_TURN = {"align_turn_index": const(0)}                  # endpoint.py:750; the registered task has one turn
_CACHE_SETUP = {                                        # prompt_cache.py:266-279 less fed_delta_ids (endpoint:682)
    "cache_policy": const("episode_prefix"), "cache_accounting_version": STR, "prompt_tokens": NAT,
    "cached_prompt_tokens": NAT, "prefill_tokens": NAT, "fed_delta_ids_sha256": DIGEST, "cache_classes": arr(STR),
    "cache_trimmable": BOOL, "cache_created": BOOL, "cache_rebuilt": BOOL, "cache_trimmed_tokens": NAT,
    "cache_fallback_reason": nullable(STR), "cache_represented_tokens_before": NAT,
    "cache_represented_ids_before_sha256": DIGEST, "cache_reconciled_prefix_sha256": DIGEST,
    "cache_offsets_before_prefill": arr(nullable(INT))}
_CHECKPOINT = {                                         # prompt_cache.py:286-297, a hybrid model with checkpoints
    "cache_checkpoint_policy": STR, "cache_checkpoint_limit": NAT, "cache_checkpoint_boundary_tokens": nullable(NAT),
    "cache_checkpoint_byte_accounting": STR, "cache_checkpoint_count": NAT, "cache_checkpoint_bytes": NAT,
    "cache_checkpoint_retained_bytes": NAT, "cache_checkpoint_restore_count": NAT,
    "cache_checkpoint_restore_bytes": NAT, "cache_checkpoint_restored_tokens": NAT,
    "cache_prefill_tokens_saved": NAT, "cache_checkpoint_config_size": NAT,
    "cache_checkpoint_config_size_unavailable": const(True)}


def _setup(metadata, where, extra):
    """generation_setup carries the episode cache's observation on the registered cache path, else nothing."""
    if any(key in metadata for key in _CACHE_SETUP):
        obj({**_TURN, **extra, **_CACHE_SETUP}, _CHECKPOINT)(metadata, where)
    else:
        obj({**_TURN, **extra})(metadata, where)


_MESSAGES = {
    ("phase_start", "tokenize"): ("mlx tokenization started",),
    ("phase_end", "tokenize"): ("mlx tokenization completed",),
    ("phase_start", "generation_setup"): ("mlx generation setup started",),
    ("phase_end", "generation_setup"): ("mlx generation setup completed",),
    ("phase_start", "prefill"): ("mlx prefill started",),
    ("phase_end", "prefill"): ("mlx prefill completed", "mlx prefill completed without emitted tokens"),
    ("phase_start", "decode"): ("mlx decode started", "mlx decode started without emitted tokens"),
    ("phase_end", "decode"): ("mlx decode completed",),
}
_OBSERVATIONS = {                                       # workload.py:494-542, empty metadata
    "align_context_check": "render prompt",
    "align_context_stop_observation": "zero-generation sampler observation",
    "align_g0_unreleased_stop_observation": "zero-generation sampler observation",
}
_STAGES = ("validate", "prepare", "idle_baseline", "warmup", "measured_run", "idle_drift_sentinel", "cleanup", "reduce")
# joulewise/schemas.py:267-277 FailureReason, the same ten members at all three revisions; a failure row's metadata
# carries one member's value (controller.py:1663-1669; GRAMMAR.md, "failure fixture").
_FAILURE_REASONS = ("did_not_fit", "runtime_unavailable", "model_identity_mismatch", "telemetry_unavailable",
                    "format_unavailable", "permission_denied", "transport_unavailable", "unsupported_workload",
                    "cleanup_failed", "unknown_error")
DEADMAN = "episode.deadman"                             # endpoint.py:338,759,765: the episode deadman's stop text


def _mlx_metadata(row, where):
    """The adapter's metadata for one MLX row (mlx_runtime.py:775-975), plus the endpoint's turn index."""
    kind, phase, metadata, message = row["event_type"], row["phase"], row["metadata"], row["message"]
    at = f"{where}.metadata"
    if kind == "token":
        # RL-184 T05: an absent or null turn index on a token is turn 0
        obj({"index": NAT}, {"align_turn_index": nullable(const(0))})(metadata, at)
        if message != f"mlx token {metadata['index']}":
            refuse(f"{where}.message", "not the token constructor's message")
        if phase != "decode":
            refuse(f"{where}.phase", "a token outside decode")
        return
    if message not in _MESSAGES.get((kind, phase), ()):
        refuse(f"{where}.message", "not the constructor's message")
    empty = message.endswith("without emitted tokens")
    if (kind, phase) == ("phase_start", "tokenize"):
        obj(_TURN)(metadata, at)
    elif (kind, phase) == ("phase_end", "tokenize"):
        obj({**_TURN, "prompt_tokens": NAT})(metadata, at)
    elif (kind, phase) == ("phase_start", "generation_setup"):
        _setup(metadata, at, {})
    elif (kind, phase) == ("phase_end", "generation_setup"):
        _setup(metadata, at, {"requested_output_tokens": NAT, "eos_suppressed": BOOL})
    elif (kind, phase) == ("phase_start", "prefill"):
        cached = {"cached_tokens": NAT, "prefill_tokens": NAT} if "cached_tokens" in metadata else {}
        obj({**_TURN, "phase_boundary_method": const("first_token"), "prompt_tokens": NAT,
             "requested_output_tokens": NAT, "eos_suppressed": BOOL, **cached})(metadata, at)
    elif (kind, phase) == ("phase_end", "prefill"):
        obj({**_TURN, "phase_boundary_method": const("first_token")})(metadata, at)
    elif (kind, phase) == ("phase_start", "decode"):
        if empty:
            obj({**_TURN, "phase_boundary_method": const("first_token"), "max_tokens": NAT,
                 "eos_suppressed": BOOL})(metadata, at)
        else:
            obj({**_TURN, "phase_boundary_method": const("first_token"), "max_tokens": NAT, "eos_suppressed": BOOL,
                 "original_eos_token_ids": nullable(arr(INT))})(metadata, at)
            if (metadata["original_eos_token_ids"] is not None) != metadata["eos_suppressed"]:
                refuse(f"{at}.original_eos_token_ids", "recorded exactly when end of sequence was suppressed")
    else:
        obj({**_TURN, "phase_boundary_method": const("first_token"), "emitted_tokens": NAT,
             "requested_output_tokens": NAT})(metadata, at)


def _event_row(row, where):
    obj({"timestamp_s": FLOAT, "event_type": TEXT, "phase": TEXT, "message": STR, "metadata": lambda v, w: None})(
        row, where)
    if type(row["metadata"]) is not dict:
        refuse(f"{where}.metadata", "not an object")


class _Stack:
    """Phase pairing: every end closes the innermost open phase of the same name (and gate kind)."""

    def __init__(self, where):
        self.where, self.open = where, []

    def start(self, key, row, at):
        if key in [k for k, _ in self.open]:
            refuse(f"{at}.phase", "a phase opened again before it closed")
        self.open.append((key, row))

    def end(self, key, at):
        if not self.open or self.open[-1][0] != key:
            refuse(f"{at}.phase", "an end that does not close the innermost open phase")
        return self.open.pop()[1]


def _runtime_events(rows, where, *, controller, selected=None):
    """The episode's runtime events in order: thermal intervals, the turn's MLX phases and tokens and the zero-
    generation observations; with ``controller``, the controller's lifecycle rows too (events.jsonl)."""
    stack = _Stack(where)
    tokens, gate_kinds, mlx_seen, stage_state = [], [], [], {}
    emitted = []
    stages_started, stages_done, failure, finalized = [], [], None, False
    timing_spans, timing_sequences, sampling = {}, set(), []
    previous = None
    for index, row in enumerate(rows):
        at = f"{where}[{index}]"
        _event_row(row, at)
        kind, phase, metadata = row["event_type"], row["phase"], row["metadata"]
        if controller:
            if previous is not None and row["timestamp_s"] < previous:
                refuse(f"{at}.timestamp_s", "before the previous row; the controller flushes in time order")
            previous = row["timestamp_s"]
        if phase.startswith("align_tool_"):
            refuse(f"{at}.phase", "a tool phase; the registered task has no tools (F4)")
        if controller and kind == "timing_boundary":                 # routed by kind: its phase is the span's own
            _timing_row(row, at, timing_spans, timing_sequences)
            continue
        if controller and kind in ("sampling_started", "sampling_stopped"):
            _controller_row(row, at)
            if sampling != ([] if kind == "sampling_started" else ["sampling_started"]):
                refuse(at, "not the measured window's one start, then its one stop")
            sampling.append(kind)
            continue
        if phase in ("align_thermal_gate", "align_thermal_hold"):
            if kind not in ("phase_start", "phase_end"):
                refuse(f"{at}.event_type", "not a phase boundary")
            _interval(metadata, f"{at}.metadata", selected)
            if row["message"] != metadata["kind"] or (phase == "align_thermal_hold") != (metadata["kind"] == "H"):
                refuse(f"{at}.message", "not the interval's gate kind")
            key = (phase, metadata["kind"])
            if kind == "phase_start":
                if row["timestamp_s"] != metadata["entry_epoch_s"]:
                    refuse(f"{at}.timestamp_s", "not the interval's entry")
                if metadata["kind"] == "G0" and ("G0" in gate_kinds or mlx_seen):
                    refuse(f"{at}.metadata.kind", "G0 is the episode's first and only start gate")
                gate_kinds.append(metadata["kind"])
                stack.start(key, row, at)
            else:
                opened = stack.end(key, at)
                if opened["metadata"] != metadata:
                    refuse(f"{at}.metadata", "not the interval its start carries")
                if row["timestamp_s"] != metadata["exit_epoch_s"]:
                    refuse(f"{at}.timestamp_s", "not the interval's exit")
            continue
        if phase in _OBSERVATIONS:
            if kind not in ("phase_start", "phase_end") or row["message"] != _OBSERVATIONS[phase]:
                refuse(f"{at}.message", "not the observation's constructor")
            obj({})(metadata, f"{at}.metadata")
            (stack.start((phase,), row, at) if kind == "phase_start" else stack.end((phase,), at))
            continue
        if kind == "token" or phase in ("tokenize", "generation_setup", "prefill", "decode"):
            _mlx_metadata(row, at)
            if kind == "token":
                if not stack.open or stack.open[-1][0] != ("decode",):
                    refuse(f"{at}.event_type", "a token outside an open decode phase")
                if metadata["index"] != len(tokens):
                    refuse(f"{at}.metadata.index", "not the next token in order")
                if tokens and row["timestamp_s"] < tokens[-1]:
                    refuse(f"{at}.timestamp_s", "before the previous token")
                tokens.append(row["timestamp_s"])
                continue
            order = ("tokenize", "generation_setup", "prefill", "decode")
            step = (phase, kind)
            expected = [(p, k) for p in order for k in ("phase_start", "phase_end")]
            if len(mlx_seen) >= len(expected) or expected[len(mlx_seen)] != step:
                refuse(f"{at}.phase", "not the adapter's next phase boundary")
            if step == ("decode", "phase_start") and mlx_seen[-1] != ("prefill", "phase_end"):
                refuse(f"{at}.phase", "decode opens where prefill closed")
            mlx_seen.append(step)
            if kind == "phase_start":
                stack.start((phase,), row, at)
            else:
                stack.end((phase,), at)
            if step == ("prefill", "phase_end"):
                emitted.append(row["message"].endswith("without emitted tokens"))
            if step == ("decode", "phase_start"):
                if row["message"].endswith("without emitted tokens") != emitted[-1]:
                    refuse(f"{at}.message", "not the boundary its prefill end announced")
            if step == ("decode", "phase_end"):
                if metadata["emitted_tokens"] != len(tokens) or (len(tokens) == 0) != emitted[-1]:
                    refuse(f"{at}.metadata.emitted_tokens", "not the number of token rows")
            continue
        if not controller:
            refuse(f"{at}.event_type", "not a runtime event")
        _controller_row(row, at)
        if kind == "stage_started":
            if phase in stages_started or failure is not None or (stages_started and stages_done[-1:] != stages_started[-1:]):
                refuse(f"{at}.phase", "a stage started out of the lifecycle's order")
            if _STAGES.index(phase) < max((_STAGES.index(s) for s in stages_started), default=-1):
                refuse(f"{at}.phase", "a stage started out of the lifecycle's order")
            stages_started.append(phase)
        elif kind == "stage_completed":
            if not stages_started or stages_started[-1] != phase or phase in stages_done:
                refuse(f"{at}.phase", "a stage completed that is not the open one")
            stages_done.append(phase)
        elif kind == "failure":
            if failure is not None:
                refuse(at, "a second failure row")
            failure = phase
        elif kind == "run_started":
            if index != 0:
                refuse(at, "the run starts with its first row")
        elif kind == "run_finalized":
            if index != len(rows) - 1:
                refuse(at, "finalization is the last row")
            finalized = True
    if stack.open:
        refuse(where, "a phase left open; a completed record closes every phase")
    if mlx_seen and len(mlx_seen) != 8:
        refuse(where, "a turn without all of its adapter phases")
    if controller and (stages_started or failure is not None or finalized):
        _lifecycle_ends(rows, where, stages_started, stages_done, failure)
    return {"tokens": len(tokens), "mlx": bool(mlx_seen),
            "prompt_tokens": next((r["metadata"]["prompt_tokens"] for r in rows
                                   if (r["event_type"], r["phase"]) == ("phase_end", "tokenize")), None),
            "failure": failure}


def _lifecycle_ends(rows, where, started, done, failure):
    """A controller journal is complete only where ``_finish`` leaves it (controller.py:3963-3971): a run that
    recorded a failure flushes it and then appends ``run_finalized``, and a run that did not completed every stage
    it started. No pinned counter names a journal's final row (RL-184 F2), so a journal that stops after its failure
    row, or inside a stage, has nothing to be told apart from a cut one by. Which stages a run has is the
    controller's (the idle sentinel is skipped on a mock telemetry backend, controller.py:2630-2637), so their
    number is not checked here."""
    if failure is not None:
        if rows[-1]["event_type"] != "run_finalized":
            refuse(f"{where}[{len(rows) - 1}]", "a failure not followed by the finalization the writer appends")
    elif started != done:
        refuse(where, "a stage left open by a journal that records no failure")


def _cleanup_metadata(value, where):
    """controller.py:2685-2734. ``cleanup_ok`` and, when cleanup failed, why; a clean adapter's own cleanup
    metadata is merged in beside it, so the other members of a successful cleanup are the adapter's."""
    if type(value) is not dict:
        refuse(where, "not an object")
    if not value:
        return
    if type(value.get("cleanup_ok")) is not bool:
        refuse(f"{where}.cleanup_ok", "not a boolean")
    if not value["cleanup_ok"]:
        obj({"cleanup_ok": const(False), "message": nullable(STR)}, {"failure_reason": nullable(STR)})(value, where)


# What each stage's rows carry (controller.py, the same bytes at the three revisions). A bare ``{}`` is what the two
# stage helpers write when called with no metadata (3856-3867), which is how the frozen packet's serializer
# production drives them; the other form is the lifecycle's own call. On a telemetry backend that is not the mock,
# idle_baseline's start and the sentinel's completion also carry the battery clock's reading, null when it failed
# (3856-3875); the idle sentinel is skipped on the mock backend and reports "unavailable" without a provider.
_STAGE_STARTED = {"idle_baseline": either(obj({}), obj({"monotonic_ns": nullable(INT)}))}
_STAGE_COMPLETED = {
    "validate": either(obj({}), obj({"transport": STR, "runtime": STR, "telemetry": STR})),                # 1772-1779
    "idle_baseline": either(obj({}), obj({"power_w_mean": nullable(MEASURED), "duration_s": nullable(NUM),    # 2045-2057
                                          "admission_attempts": nullable(NAT), "admission_decision": nullable(STR)})),
    "warmup": either(obj({}), obj({"warmup_runs": NAT, "warmup_seconds": NUM})),                           # 2476-2479
    "measured_run": either(obj({}), obj({"sample_count": NAT, "runtime_event_count": NAT})),               # 2609-2615
    "idle_drift_sentinel": either(obj({}, {"monotonic_ns": nullable(INT)}),                                # 2630-2675
                                  obj({"status": nullable(STR)}, {"duration_requested_s": nullable(NUM),
                                                                  "monotonic_ns": nullable(INT)})),
    "cleanup": _cleanup_metadata,
}
_SAMPLING_MESSAGES = {
    "sampling_started": ("telemetry sampling confirmed active",),
    "sampling_stopped": ("measured window stopped; telemetry tail retained outside window",
                         "telemetry sampling stopping (failure path)"),
}
TIMING_SCHEMA = "joulewise.timing_boundary.v1"                          # timing_receipts.py:23


def _timing_row(row, where, spans, sequences):
    """One timing boundary (controller.py:3935-3942; timing_receipts.py:43-83,115-138): the receipt row is the
    event's metadata, its phase and activity are the event's phase and message, and the event's time is the row's.
    An ``align_episode`` bundle records them; a span has one start and at most one end, after it."""
    metadata, at = row["metadata"], f"{where}.metadata"
    ended = metadata.get("event") == "end"
    required = {"schema": const(TIMING_SCHEMA), "kind": const("timing_boundary"), "producer": const("bundle"),
                "plan_id": nullable(STR), "member": TEXT, "attempt": const(None), "boot_session_id": nullable(STR),
                "clock_domain": enum("host-monotonic", "synthetic-controller"), "producer_id": TEXT,
                "wall_resolution_s": NUM, "monotonic_resolution_s": NUM, "sequence": NAT,
                "event": enum("start", "end"), "span_id": TEXT, "parent_span_id": nullable(TEXT), "phase": TEXT,
                "activity": TEXT, "stage": nullable(TEXT), "epoch_ns": INT, "monotonic_before_ns": INT,
                "monotonic_after_ns": INT}
    if ended:
        required.update(status=TEXT, rc=nullable(INT))
    obj(required, {"timestamp_s": FLOAT, "requested_s": NUM})(metadata, at)
    if row["phase"] != metadata["phase"] or row["message"] != metadata["activity"]:
        refuse(where, "not the phase and activity its receipt row carries")
    if row["timestamp_s"] != metadata.get("timestamp_s", metadata["epoch_ns"] / 1e9):
        refuse(f"{where}.timestamp_s", "not its receipt row's time")
    if metadata["sequence"] < 1 or metadata["sequence"] in sequences:
        refuse(f"{at}.sequence", "not a sequence number of its own")
    sequences.add(metadata["sequence"])
    key, opened = metadata["span_id"], spans.get(metadata["span_id"])
    if not ended:
        if opened is not None:
            refuse(f"{at}.span_id", "a span started twice")
        spans[key] = [metadata["phase"], metadata["activity"], False]
    elif opened is None or opened[2] or opened[:2] != [metadata["phase"], metadata["activity"]]:
        refuse(f"{at}.span_id", "an end that closes no open span of its phase and activity")
    else:
        opened[2] = True


def _controller_row(row, where):
    """The controller's lifecycle rows (controller.py:1663-1681,1742-2827,3935-3960; bundle.py:1193-1210)."""
    kind, phase, metadata, message = row["event_type"], row["phase"], row["metadata"], row["message"]
    at = f"{where}.metadata"
    if kind == "run_started":
        obj({"run_id": TEXT})(metadata, at)
        if phase != "run" or message != f"run {metadata['run_id']} started":
            refuse(f"{where}.message", "not the constructor's message")
    elif kind == "run_finalized":
        obj({})(metadata, at)
        if phase != "run" or message != "bundle finalized":
            refuse(f"{where}.message", "not the constructor's message")
    elif kind in ("stage_started", "stage_completed"):
        enum(*_STAGES)(phase, f"{where}.phase")
        word = "started" if kind == "stage_started" else "completed"
        if message != f"stage {phase} {word}":
            refuse(f"{where}.message", "not the constructor's message")
        (_STAGE_STARTED if kind == "stage_started" else _STAGE_COMPLETED).get(phase, obj({}))(metadata, at)
    elif kind in ("sampling_started", "sampling_stopped"):
        obj({})(metadata, at)                                          # controller.py:2510-2521,2618-2627,2913-2922
        if phase != "measured_run" or message not in _SAMPLING_MESSAGES[kind]:
            refuse(f"{where}.message", "not the constructor's message")
    elif kind == "failure":
        enum(*_STAGES)(phase, f"{where}.phase")
        obj({"failure_reason": enum(*_FAILURE_REASONS)})(metadata, at)
        TEXT(message, f"{where}.message")
    else:
        refuse(f"{where}.event_type", "not an event a pinned writer records")


# ======================================================================================================== turns
_SAMPLER = either(
    obj({"kind": const("greedy"), "temperature": const(0.0), "pinned": const(True),
         "api": enum("mlx_lm.make_sampler", "mlx_lm.sample_utils.make_sampler"),
         "parameter": enum("temp", "temperature", "positional_temp")}, {"per_turn_seed": NAT}),
    obj({"kind": const("categorical"), "temperature": NUM, "top_p": NUM, "top_k": NAT, "min_p": NUM,
         "pinned": const(True), "api": enum("mlx_lm.make_sampler", "mlx_lm.sample_utils.make_sampler"),
         "parameter": const("temp"), "constructor_kwargs": obj({"temp": NUM, "top_p": NUM, "top_k": NAT, "min_p": NUM}),
         "per_turn_seed": NAT}))
_PREFILL_METHOD = enum("chat_template_token_count_difference", "scripted_prompt_count")
_CACHE_TURN = {**{k: v for k, v in _CACHE_SETUP.items()}, "fed_delta_ids": arr(INT), "cached_hidden_context_tokens": NAT,
               "fresh_hidden_prefill_tokens": NAT, "hidden_cache_accounting_method": STR}


def _generation(value, where):
    """endpoint.py:724-814: a generated turn's provenance, or the error path's four members."""
    if type(value) is dict and "prompt_token_ids" not in value:
        # The turn ended before the provenance dict was built: an endpoint error leaves no stop, and the episode
        # deadman expiring inside the generation (DeadmanExpired, endpoint.py:757-759) names itself as the stop.
        obj({"finish_reason": nullable(const(DEADMAN)), "prior_hidden_prefill_method": _PREFILL_METHOD,
             "prior_hidden_prefill_tokens": NAT, "stop_condition": nullable(const(DEADMAN))})(value, where)
        if value["finish_reason"] != value["stop_condition"]:
            refuse(f"{where}.stop_condition", "not the stop the turn's finish reason gives")
        return None
    cache = _CACHE_TURN if type(value) is dict and "cache_policy" in value else {}
    # finish_reason is whatever text the runtime's last response carried (mlx_runtime.py:911-913, endpoint.py:275-302),
    # or the episode deadman's, or null; the writer stores no other (endpoint.py:770-771)
    obj({"finish_reason": nullable(TEXT), "output_token_ids": arr(INT), "prior_hidden_prefill_method": _PREFILL_METHOD,
         "prior_hidden_prefill_tokens": NAT, "prompt_token_ids": arr(INT), "prompt_token_ids_sha256": DIGEST,
         "reasoning_token_accounting": STR, "runtime_stop_condition": STR, "sampler": _SAMPLER,
         "stop_condition": STR, **cache}, _CHECKPOINT if cache else None)(value, where)
    digest = hashlib.sha256(json.dumps(value["prompt_token_ids"], separators=(",", ":")).encode()).hexdigest()
    if value["prompt_token_ids_sha256"] != digest:
        refuse(f"{where}.prompt_token_ids_sha256", "not the digest of its prompt ids")
    return value


def _turns(rows, where):
    turn = obj({"turn": const(0), "flags": arr(STR), "generation": lambda v, w: None, "start_stamp": S_STAMP,
                "end_stamp": S_STAMP, "clock_mapping": obj({"trace_domain": STR, "episode_domain": STR,
                                                            "offset_ns": INT, "uncertainty_ns": NAT, "method": STR})})
    if len(rows) > 1:
        refuse(where, "more than the registered task's one turn")
    generated = []
    for index, row in enumerate(rows):
        turn(row, f"{where}[{index}]")
        generation = _generation(row["generation"], f"{where}[{index}].generation")
        generated.append(generation)
        stop = (generation if generation is not None else row["generation"])["finish_reason"]
        if stop == DEADMAN and f"{DEADMAN}:0" not in row["flags"]:
            refuse(f"{where}[{index}].flags", "the episode deadman's stop without its flag (endpoint.py:766-767)")
        if row["start_stamp"]["epoch_s"] > row["end_stamp"]["epoch_s"]:
            refuse(f"{where}[{index}]", "a turn that ends before it starts")
    return generated


# ================================================================================================ thermal journal
_POLICY = obj({"s_fast": TEMPERATURE, "s_slow": TEMPERATURE, "fan_keys": arr(FAN), "r0_sha256": DIGEST},
              {"record_keys": arr(TEMPERATURE)})                        # thermal.py:22-46
_COVERAGE_KEY = obj({"expected_samples": NAT, "gaps_ns": arr(arr(INT, least=2, most=2)),
                     "max_consecutive_empty_cells": NAT, "max_interval_ns": NAT, "sample_fraction": NUM,
                     "valid_samples": NAT})
_STATUS = either(obj({"os_level": INT, "pm_state": nullable(STR), "pm_observed_ns": nullable(INT)}, {"monotonic_ns": INT}),
                 obj({"error": TEXT}))                                  # thermal_gates.py:702-731; thermal.py:150-154


def _selected(policy):
    return {policy["s_fast"], policy["s_slow"], *policy["fan_keys"], *policy.get("record_keys", ())}


def _reading(values, where, selected):
    """thermal.py sample (54-82) and the status tap: every selected key in each map; a failed key is null with
    its reason; each raw reading is the probe's attributes plus value and error."""
    obj({"source": const("smc"), "sensors": mapping(nullable(NUM), SENSOR), "units": mapping(enum("degC", "rpm", "raw"),
                                                                                             SENSOR),
         "errors": mapping(TEXT, SENSOR),
         "readings": mapping(obj({"value": nullable(NUM), "error": nullable(TEXT)},
                                 {"data_type": STR, "data_size": NAT, "raw_hex": nullable(rx(r"[0-9a-f]*"))}), SENSOR)},
        {"status": lambda v, w: None})(values, where)
    if "status" not in values:
        refuse(f"{where}.status", "absent; the registered runtime binds the status tap (workload.py:244)")
    _STATUS(values["status"], f"{where}.status")
    for member in ("sensors", "units", "readings"):
        if set(values[member]) != selected:
            refuse(f"{where}.{member}", "not the policy's selected keys")
    if not set(values["errors"]) <= selected:
        refuse(f"{where}.errors", "a key the policy does not select")
    for key in selected:
        value, error = values["sensors"][key], values["errors"].get(key)
        if (value is None) != (error is not None):
            refuse(f"{where}.sensors.{key}", "null exactly when its read failed")
        if value is not None and not (-40 <= value <= 150 if key.startswith("T") else value >= 0):
            refuse(f"{where}.sensors.{key}", "a value the collector would have refused")
        unit = "degC" if key.startswith("T") else "rpm" if key.endswith("Ac") else "raw"
        if values["units"][key] != unit:
            refuse(f"{where}.units.{key}", "not the key's unit")
        reading = values["readings"][key]
        if type(reading["value"]) is not type(value) or reading["value"] != value or reading["error"] != error:
            refuse(f"{where}.readings.{key}", "not the cleaned value and its reason")
    status = values.get("status")
    if status is not None and "os_level" in status and (status["pm_state"] is None) != (status["pm_observed_ns"] is None):
        refuse(f"{where}.status", "a pressure state exactly with its observation stamp")


def _thermal(rows, where, *, complete=True):
    """The collector's journal (thermal.py:114-201): one session, numbered rows, opened and closed."""
    row_check = obj({"schema": const(THERMAL_SCHEMA), "module": const("temperature"),
                     "kind": enum("session_start", "reading", "align_thermal_gate", "align_thermal_hold", "session_end"),
                     "session": TEXT, "seq": INT, "started": SIDE_STAMP, "finished": SIDE_STAMP,
                     "values": lambda v, w: None, "raw": arr(lambda v, w: refuse(w, "a raw sample"), most=0),
                     "error": nullable(TEXT)})
    if not rows:
        refuse(where, "an empty journal; the collector opens its session first")
    selected, gates = None, []
    for index, row in enumerate(rows):
        at = f"{where}[{index}]"
        row_check(row, at)
        kind, values = row["kind"], row["values"]
        if row["seq"] != index + 1:
            refuse(f"{at}.seq", "not the next row number")
        if row["session"] != rows[0]["session"] or rows[0]["session"] != f"align-{rows[0]['started']['monotonic_ns']}":
            refuse(f"{at}.session", "not the session the first row opened")
        if (kind == "session_start") != (index == 0) or (kind == "session_end") != (index == len(rows) - 1 and complete):
            refuse(f"{at}.kind", "not where the session opens or closes")
        if row["started"]["monotonic_ns"] > row["finished"]["monotonic_ns"]:
            refuse(f"{at}.finished", "before it started")
        if kind == "session_start":
            obj({"thermal": _POLICY})(values, f"{at}.values")
            selected = _selected(values["thermal"])
        elif kind == "reading":
            _reading(values, f"{at}.values", selected)
        elif kind == "session_end":
            # A collector failure raises ThermalFault in the gate that sees it (thermal_gates.py:521-524, 551-554)
            obj({"collector_error": const(None), "coverage": obj(
                {"all_keys": _COVERAGE_KEY, "clock": const("monotonic_ns"), "edge_policy": STR,
                 "per_key": mapping(_COVERAGE_KEY, SENSOR), "period_ns": NAT, "sampling_grid_ns": INT,
                 "span_ns": arr(INT, least=2, most=2), "tolerance_ns": NAT})})(values, f"{at}.values")
            if set(values["coverage"]["per_key"]) != selected:
                refuse(f"{at}.values.coverage.per_key", "not the policy's selected keys")
        else:
            hold = kind == "align_thermal_hold"
            if type(values) is dict and values.get("state") == "begin":
                obj({"state": const("begin"), "gate_kind": enum("H") if hold else enum("G0", "G1"), "turn": const(0),
                     "token_count": NAT if hold else const(None), "entry_stamp": NS_STAMP})(values, f"{at}.values")
                if values["gate_kind"] in [g for g, _ in gates]:
                    refuse(f"{at}.values", "a gate begun again before it ended")
                gates.append((values["gate_kind"], values))
            else:
                obj({"state": const("end"), "gate": lambda v, w: _interval(v, w, selected)})(values, f"{at}.values")
                gate = values["gate"]
                if (gate["kind"] == "H") != hold:
                    refuse(f"{at}.values.gate.kind", "not this row's kind")
                begun = next((b for g, b in gates if g == gate["kind"]), None)
                if begun is None or begun["entry_stamp"] != gate["entry_stamp"] or begun["token_count"] != gate[
                        "token_count"]:
                    refuse(f"{at}.values.gate", "an end without its begin")
                gates.remove((gate["kind"], begun))
        joined = "; ".join(values["errors"].values()) if kind == "reading" else ""
        if (row["error"] or "") != joined:
            refuse(f"{at}.error", "not the joined reasons of its failed reads")
    if complete and gates:
        refuse(where, "a gate begun and never ended")
    return selected


# ======================================================================================================= config
_CONFIG = obj({
    "schema_version": const("0.1"), "run_id": TEXT,
    "hardware_target": obj({"device_kind": STR, "host": const(None), "id": STR, "notes": STR, "runtime_backend": STR,
                            "telemetry_backend": STR, "transport": STR}),
    "interconnect": obj({"link_speed_mbps": const(None), "name": STR, "notes": const(None)}),
    "model": obj({"context_window": const(None), "family": STR, "name": STR, "revision": STR, "source": STR,
                  "weight_format": STR}),
    "quantization": obj({"bits": INT, "group_size": INT, "name": STR}),
    "run_metadata": obj({"ambient_temp_c": const(None), "notes": const(None), "operator": STR, "project": STR,
                         "tags": arr(STR)}),
    "sampling": obj({"idle_seconds": NUM, "power_hz": NUM, "warmup_seconds": NUM}),
    "workload_profile": obj({"dataset_ref": const(None), "name": STR, "output_tokens": const(None),
                             "prompt_text": STR, "prompt_tokens": const(None), "repetitions": INT,
                             "warmup_runs": INT})})


def _config(doc, where):
    """The registered d_spam template as ``BenchmarkConfig.to_dict()`` writes it (schemas.py:797-1158)."""
    _CONFIG(doc, where)
    if not doc["sampling"]["power_hz"] > 0:
        refuse(f"{where}.sampling.power_hz", "not a sampling rate")
    try:
        spec = json.loads(doc["workload_profile"]["prompt_text"])
    except ValueError:
        refuse(f"{where}.workload_profile.prompt_text", "not the serialized episode spec")
    if type(spec) is not dict or spec.get("schema") != "joulewise.align.apple.episode_spec.v1":
        refuse(f"{where}.workload_profile.prompt_text", "not the serialized episode spec")


# ======================================================================================================= bundle
def validate_bundle(files, where, context):
    """Admit one runtime bundle's journals or raise Refusal. ``files`` maps each present journal name to its
    decoded content. A completed leg's bundle holds all four ordinary journals; a leg without a turn may lack
    its turn journal."""
    result = (context or {}).get("result") or {}
    turned = result.get("prefill_tokens") is not None
    for name in (CONFIG, EVENTS, THERMAL):
        if name not in files:
            refuse(f"{where}/{name}", "absent from a bundle whose other journals exist")
    if TURNS not in files and turned:
        refuse(f"{where}/{TURNS}", "absent for a leg with a turn")
    _config(files[CONFIG], f"{where}/{CONFIG}")
    selected = _thermal(files[THERMAL], f"{where}/{THERMAL}")
    events = _runtime_events(files[EVENTS], f"{where}/{EVENTS}", controller=True, selected=selected)
    generated = _turns(files.get(TURNS, []), f"{where}/{TURNS}")
    if SALVAGE in files:
        if not files[SALVAGE]:
            refuse(f"{where}/{SALVAGE}", "an empty salvage journal")
        _runtime_events(files[SALVAGE], f"{where}/{SALVAGE}", controller=False, selected=selected)
    if events["mlx"]:
        if len(generated) != 1 or generated[0] is None:
            refuse(f"{where}/{TURNS}", "not the generated turn its events record")
        if len(generated[0]["output_token_ids"]) != events["tokens"]:
            refuse(f"{where}/{TURNS}[0].generation.output_token_ids", "not one id per token row")
        if len(generated[0]["prompt_token_ids"]) != events["prompt_tokens"]:
            refuse(f"{where}/{TURNS}[0].generation.prompt_token_ids", "not the prompt its tokenization counted")
    if turned and not generated:
        refuse(f"{where}/{TURNS}", "no turn for a leg whose result counts one")
