"""Native ctl-01 trace projection and the post-start value reader."""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, replace
from fractions import Fraction
from hashlib import sha256
import json
from math import ceil, isfinite
import struct

from joulewise.adapters.powermetrics import RAIL_MANIFEST
from joulewise.align.apple.episode_bundle import join_episode_trace
from joulewise.align.apple.sampler import (
    NS_PER_SECOND as NS, _restore_stamp, seconds_ns, stamp_mapping,
)
from joulewise.align.power.windows import _support_edge_quantum_ns
from joulewise.align.records import ClockMapping, Episode, PowerTrace, _build, from_json
from joulewise.external import km003c_parse as meter
from joulewise.schemas import BenchmarkConfig

from . import controls_analysis as analysis
from . import controls_metadata as metadata_wire
from .qualification_manifest import _decode
from .controls_time_fields import (
    BOOLEAN, EMPTY_ARRAY, INT64, INTEGER, NUMBER, OPAQUE_BOOLEAN, OPAQUE_FINITE_NUMBER, OPAQUE_INTEGER,
    OPAQUE_NONBLANK_STRING,
    OPAQUE_NONNEGATIVE_NUMBER, OPAQUE_OBJECT, OPAQUE_PERCENT, OPAQUE_STRING, OPAQUE_STRING_OR_INTEGER,
    RAIL_COLUMNS, STRING,
    DependentRecord, ExtensionRecord, KeyedFields, Nullable, OpaqueIndex, RequiredRecordFields, TaggedFields,
    TimeFieldError, TokenForms, WireRecord,
    project_json, rail_rows, stream_fields,
)


METHOD = "km003c_raw_monotonic_pairs.v1"
CAP_NS = 100_000_000
FAILURES = ("boot_mismatch", "stream_unclosed", "anchor_unusable",
            "half_width_over_cap", "not_bracketed")
ELIGIBLE = frozenset(("meter_absent", *FAILURES[1:]))
RAILS = frozenset(("cpu_power", "gpu_power", "ane_power"))
STAMP_FIELDS = RequiredRecordFields.fromkeys(("epoch_ns", "monotonic_before_ns", "monotonic_after_ns",
                                             "wall_resolution_ns", "monotonic_resolution_ns"), INT64)
TOOL_FIELDS = RequiredRecordFields(
    start_ns=INT64, end_ns=INT64, args_bytes=INTEGER, result_bytes=INTEGER,
    logged=OPAQUE_BOOLEAN, state_changed=Nullable(OPAQUE_BOOLEAN), name=OPAQUE_STRING,
    state_before_sha256=Nullable(OPAQUE_STRING), state_after_sha256=Nullable(OPAQUE_STRING),
)
TURN_FIELDS = RequiredRecordFields(
    **dict.fromkeys(("index", "context_tokens", "prefill_tokens", "decode_tokens", "hidden_tokens"), INTEGER),
    start_ns=INT64, end_ns=INT64, first_token_ns=Nullable(INT64), logged=BOOLEAN, tool_calls=[TOOL_FIELDS],
)
REFERENCE_TEMPERATURES = WireRecord(dict.fromkeys(("fast_c", "slow_c"), Nullable(OPAQUE_FINITE_NUMBER)),
                                    {"source_member": OPAQUE_STRING, "span_ns": [INT64]})
AC_POWERMODE = WireRecord(
    {"value": Nullable(OPAQUE_INTEGER), "source": OPAQUE_STRING, "observed_at": OPAQUE_STRING},
    {"error": OPAQUE_STRING, "attempts": OPAQUE_INTEGER},
)
THERMAL_POLICY_SENSORS = WireRecord(
    {"s_fast": STRING, "s_slow": STRING, "fan_keys": [STRING], "r0_sha256": OPAQUE_STRING},
    {"record_keys": [STRING]},
)
THERMAL_POLICY = WireRecord(
    {"sensors": THERMAL_POLICY_SENSORS, **dict.fromkeys(("delta_fast_c", "delta_slow_c", "turn_cap_s"), OPAQUE_FINITE_NUMBER),
     "per_turn": BOOLEAN, "heavy": BOOLEAN, "chunk_tokens": OPAQUE_INTEGER,
     "window_reference": TaggedFields("role", {
         "capture": RequiredRecordFields(role=STRING),
         "consume": RequiredRecordFields(role=STRING, source_run_id=OPAQUE_STRING, source_config_sha256=OPAQUE_STRING),
     })},
    {"g0_cap_s": OPAQUE_FINITE_NUMBER,
     "g0_cap_receipt": RequiredRecordFields(authority=OPAQUE_STRING, receipt_sha256=OPAQUE_STRING),
     "contrast_fit": WireRecord(
         {"authority": OPAQUE_STRING, "role": OPAQUE_STRING, "value_s": OPAQUE_FINITE_NUMBER,
          "nominal_cap_s": OPAQUE_FINITE_NUMBER, "deadman_s": OPAQUE_FINITE_NUMBER,
          "episode_s": Nullable(OPAQUE_FINITE_NUMBER)},
         {"predeclared": Nullable(OPAQUE_STRING)})},
)
INTERVAL_REQUIRED = {"kind": STRING, "start_ns": INT64, "end_ns": INT64}
INTERVAL_OPTIONAL = {
    "outcome": OPAQUE_STRING, "clock": OPAQUE_STRING, "token_count": Nullable(OPAQUE_INTEGER),
    "entry_stamp": STAMP_FIELDS, "exit_stamp": STAMP_FIELDS, "exit_sample_ns": Nullable(INT64),
    **dict.fromkeys(("entry_epoch_s", "exit_epoch_s", "duration_s"), OPAQUE_FINITE_NUMBER),
    **dict.fromkeys(("slope_c_per_min", "entry_slope_c_per_min"), Nullable(OPAQUE_FINITE_NUMBER)),
    **dict.fromkeys(("reference", "release"), Nullable(REFERENCE_TEMPERATURES)),
    "entry_sensors": KeyedFields(r"(?:T[!-~]{3}|F[!-~]Ac)", Nullable(OPAQUE_FINITE_NUMBER)),
}
GATE_FIELDS = WireRecord(INTERVAL_REQUIRED, {**INTERVAL_OPTIONAL, "turn": Nullable(OPAQUE_STRING_OR_INTEGER)})
THERMAL_FIELDS = TaggedFields("kind", {"G0": GATE_FIELDS, "G1": GATE_FIELDS,
                                      "H": WireRecord({**INTERVAL_REQUIRED, "turn": INTEGER},
                                                      {**INTERVAL_OPTIONAL, "condition_met_stamp": STAMP_FIELDS})})
THERMAL_RECORD = WireRecord(
    {"intervals": [THERMAL_FIELDS]},
    {"policy": THERMAL_POLICY, "window_reference": Nullable(REFERENCE_TEMPERATURES),
     "episode_reference": Nullable(REFERENCE_TEMPERATURES), "flags": [OPAQUE_STRING],
     "custody": Nullable(WireRecord(
         {"record_sha256": OPAQUE_STRING, "source_run_id": OPAQUE_STRING, "source_journal_sha256": Nullable(OPAQUE_STRING)},
         {"source_config_sha256": OPAQUE_STRING}))},
)
ARTIFACT_IDENTITY = WireRecord(
    {"status": OPAQUE_STRING},
    {**dict.fromkeys(("algorithm", "kind", "reason", "path", "root", "source"), OPAQUE_STRING),
     **dict.fromkeys(("sha256", "folded_sha256"), Nullable(OPAQUE_STRING)),
     "marker": RequiredRecordFields(adapter=OPAQUE_STRING, model_name=OPAQUE_STRING,
                                    model_revision=Nullable(OPAQUE_STRING), model_source=Nullable(OPAQUE_STRING)),
     "inventory": [RequiredRecordFields(path=OPAQUE_STRING, resolved_path=OPAQUE_STRING, sha256=OPAQUE_STRING,
                                        size_bytes=OPAQUE_INTEGER, symlink=BOOLEAN)],
     "files": KeyedFields(r".+", OPAQUE_STRING)},
)
TOKEN_BUDGET = WireRecord(
    {**dict.fromkeys(("max_episode_decode_tokens", "max_context_tokens", "effective_context_cap"), Nullable(OPAQUE_INTEGER)),
     **dict.fromkeys(("max_tokens_per_turn", "decode_tokens_used", "prefill_tokens_used",
                      "cached_context_tokens_used"), OPAQUE_INTEGER),
     "deadman_s": Nullable(OPAQUE_FINITE_NUMBER), "stop_reason": OPAQUE_STRING, "incomplete": BOOLEAN},
    {"deadline_ns": INT64, "deadline_origin": OPAQUE_STRING, "planned_g0_allowance_s": OPAQUE_FINITE_NUMBER},
)
HARDWARE_FIELDS = WireRecord(
    {"paired_clock_stamps_ns": [STAMP_FIELDS], "run_bundle_id": OPAQUE_STRING,
     "controller_clock_domain": OPAQUE_STRING, "power_scope": OPAQUE_STRING,
     "context_limits": RequiredRecordFields.fromkeys(("max_position_embeddings", "max_context_tokens"),
                                                     Nullable(OPAQUE_INTEGER)),
     "runtime_identity": RequiredRecordFields(
         mlx_version=Nullable(OPAQUE_STRING), mlx_lm_version=Nullable(OPAQUE_STRING),
         model_artifact_identity=Nullable(ARTIFACT_IDENTITY)),
     "task_diagnostics": RequiredRecordFields(
         give_hint=Nullable(OPAQUE_BOOLEAN), main_task_score=Nullable(OPAQUE_FINITE_NUMBER),
         evaluation_outputs=OPAQUE_OBJECT, flags=[OPAQUE_STRING], tool_schemas=[OPAQUE_OBJECT])},
    {"boot_id": Nullable(STRING), "thermal": THERMAL_RECORD, "ac_powermode": AC_POWERMODE, "token_budget": TOKEN_BUDGET},
)
EPISODE_FIELDS = RequiredRecordFields(
    **dict.fromkeys(("schema", "episode_id", "clock_domain", "condition"), STRING),
    **dict.fromkeys(("start_ns", "end_ns"), INT64),
    **dict.fromkeys(("task_pair", "agent_model", "endpoint"), OPAQUE_STRING),
    seed=OPAQUE_INTEGER,
    hardware=HARDWARE_FIELDS,
    turns=[TURN_FIELDS], flags=[OPAQUE_STRING], power_traces=EMPTY_ARRAY, clock_mappings=EMPTY_ARRAY,
    main_task_score=Nullable(OPAQUE_FINITE_NUMBER), side_task_success=Nullable(OPAQUE_BOOLEAN),
    monitor_verdicts=[RequiredRecordFields(monitor_model=OPAQUE_STRING, visibility=STRING,
                                           suspicion=OPAQUE_PERCENT, prompt_sha256=OPAQUE_STRING)],
    router_log=Nullable(DependentRecord(
        "num_experts", lambda limit: {"experts": [[[OpaqueIndex(limit)]]]},
        model=OPAQUE_STRING, num_experts=INTEGER, top_k=INTEGER,
        layers=[OPAQUE_INTEGER], phase=[STRING], experts=[[[OPAQUE_INTEGER]]],
    )),
)
PRODUCER_CLOCK_STAMP = RequiredRecordFields.fromkeys((
    "epoch_s", "monotonic_before_s", "monotonic_after_s", "wall_resolution_s", "monotonic_resolution_s",
), OPAQUE_FINITE_NUMBER)
IDENTITY_CLOCK_FIELDS = WireRecord(
    {"status": STRING, "method": STRING, "wall_minus_monotonic_lower_s": NUMBER,
     "wall_minus_monotonic_upper_s": NUMBER, "effective_clock_anchor_bound_s": NUMBER},
    {**dict.fromkeys((
        "rate_fit_baseline_s", "model_departure_allowance_s", "min_l_infinity_residual_upper_bound_s",
        "anchor_lower_epoch_s", "anchor_upper_epoch_s", "admissible_lower_epoch_s", "admissible_upper_epoch_s",
        "first_sample_end_point_epoch_s", "anchor_only_bound_s", "wall_minus_monotonic_span_s",
        "stamp_resolution_s", "numeric_padding_s", "epoch_representation_term_s", "first_parse_lag_s",
        "placement_bound_s", "rate_lower", "rate_upper", "rate_limit_ppm", "wall_minus_monotonic_rate_ppm",
        "max_sustained_rate_ppm", "native_intersection_lower_epoch_s", "native_intersection_upper_epoch_s",
        "causal_lower_epoch_s", "causal_upper_epoch_s",
    ), OPAQUE_FINITE_NUMBER),
     **dict.fromkeys(("records_checked", "native_rollover_count"), OPAQUE_INTEGER),
     "first_sample_end_point_epoch_ns": INT64, "arithmetic": OPAQUE_STRING,
     "clock_anchor_method": OPAQUE_STRING, "schema_version": OPAQUE_STRING,
     "clock_stamps": WireRecord({}, dict.fromkeys((
         "pre_spawn", "first_parse", "sampling_started", "sampling_stopped", "post_parse",
     ), PRODUCER_CLOCK_STAMP)),
     "caps": WireRecord({"form": OPAQUE_STRING}, dict.fromkeys((
         "max_wall_minus_monotonic_span_s", "max_effective_clock_anchor_bound_s",
         "max_sustained_rate_ppm", "max_placement_bound_s",
     ), OPAQUE_FINITE_NUMBER))},
)
SAMPLER_PROBE = WireRecord(
    {"ok": BOOLEAN},
    {"reason": OPAQUE_STRING, "method": OPAQUE_STRING},
)
POWERMETRICS_DEVICE = WireRecord(
    {"executable_path": OPAQUE_STRING, "executable_sha256": Nullable(OPAQUE_STRING),
     "samplers_requested": OPAQUE_STRING,
     "samplers_available": TokenForms({"str": OPAQUE_STRING, "[": [OPAQUE_STRING]}),
     "samplers_probe": SAMPLER_PROBE},
)
DEVICE_FIELDS = WireRecord(
    {"rail_manifest": [STRING]},
    {**dict.fromkeys(("device", "telemetry", "boundary", "timestamp_derivation", "power_units"),
                     Nullable(OPAQUE_STRING)),
     "plist_anchor_offset_s": OPAQUE_FINITE_NUMBER, "powermetrics": POWERMETRICS_DEVICE,
     "capability_precheck": WireRecord({"ok": BOOLEAN}, {"reason": OPAQUE_STRING})},
)
SAMPLE_PHASE_FIELDS = WireRecord(
    {"status": OPAQUE_STRING},
    {"method": OPAQUE_STRING, "reason": OPAQUE_STRING, **dict.fromkeys((
        "sampling_started_epoch_s", "sampling_stopped_epoch_s", "first_elapsed_s", "last_elapsed_s",
        "marker_to_first_sample_phase_bound_s", "marker_to_last_sample_phase_bound_s",
    ), OPAQUE_FINITE_NUMBER)},
)
IDLE_DRIFT_FIELDS = WireRecord(
    {"status": OPAQUE_STRING},
    {**dict.fromkeys(("method", "reason", "pre_artifact", "post_artifact", "calibration_status"), OPAQUE_STRING),
     **dict.fromkeys(("pre_sample_count", "post_sample_count"), OPAQUE_INTEGER),
     **dict.fromkeys(("pre_idle_window_suspect", "post_idle_window_suspect"), OPAQUE_BOOLEAN),
     **dict.fromkeys(("pre_power_w_mean", "run_observed_envelope_w", "effective_bound_w"), OPAQUE_FINITE_NUMBER),
     "calibration_guard_w": Nullable(OPAQUE_FINITE_NUMBER),
     **dict.fromkeys(("calibration_artifact_sha256", "calibration_cell_id"), Nullable(OPAQUE_STRING))},
)
IDLE_GUARD_FIELDS = RequiredRecordFields(
    calibration_status=OPAQUE_STRING, method=OPAQUE_STRING, guard_w=Nullable(OPAQUE_FINITE_NUMBER),
    n_bundles=OPAQUE_INTEGER, bundle_sha256=[OPAQUE_STRING], cell_id=Nullable(OPAQUE_STRING),
    artifact_sha256=Nullable(OPAQUE_STRING),
)
SOURCE_STATE_FIELDS = RequiredRecordFields.fromkeys(("git_commit", "tracked", "staged", "untracked", "diff_sha256"),
                                                    OPAQUE_STRING)
SOURCE_PROVENANCE_FIELDS = RequiredRecordFields(
    schema=OPAQUE_STRING, diff_identity=RequiredRecordFields(algorithm=OPAQUE_STRING, version=OPAQUE_STRING),
    start=SOURCE_STATE_FIELDS, end=SOURCE_STATE_FIELDS, changed_during_run=Nullable(BOOLEAN),
    claim_eligible=BOOLEAN, reason_codes=[OPAQUE_STRING],
)
CLOCK_INFO_FIELDS = TaggedFields("kind", {
    "fake": RequiredRecordFields(kind=STRING, start_s=OPAQUE_FINITE_NUMBER),
    "system": RequiredRecordFields(kind=STRING, **dict.fromkeys((
        "monotonic_minus_wall_s", "wall_resolution_s", "monotonic_resolution_s",
        "wall_minus_monotonic_start_s", "wall_minus_monotonic_end_s",
    ), OPAQUE_FINITE_NUMBER)),
})
ADAPTER_FIELDS = WireRecord({}, {
    "runtime": ExtensionRecord(
        {"name": OPAQUE_STRING, "prepare_metadata": OPAQUE_OBJECT},
        {"cleanup_metadata": OPAQUE_OBJECT, "clock_alignments": [OPAQUE_OBJECT]},
    ),
    "telemetry": ExtensionRecord(
        {"name": OPAQUE_STRING}, {"clock_alignments": [OPAQUE_OBJECT]},
    ),
})
EXTRA_FIELDS = ExtensionRecord({}, {
    "node_cleanup": [OPAQUE_OBJECT], "cooldown_cap_hit": OPAQUE_BOOLEAN,
    "environment_admission_failed": OPAQUE_BOOLEAN, "clock_step_suspect": OPAQUE_BOOLEAN,
    "preceding_member_end_s": Nullable(OPAQUE_FINITE_NUMBER),
    "preceding_gap_s": Nullable(OPAQUE_FINITE_NUMBER), "idle_start_s": OPAQUE_FINITE_NUMBER,
})
TRACE_WINDOW_MARGINS = RequiredRecordFields.fromkeys((
    "requested_post_window_dwell_s", "achieved_pre_window_margin_s", "achieved_post_window_margin_s",
), OPAQUE_FINITE_NUMBER)
SAMPLER_NUMBERS = dict.fromkeys(("temperature", "top_p", "min_p"), OPAQUE_FINITE_NUMBER)
SAMPLER_POLICY = RequiredRecordFields(**SAMPLER_NUMBERS, top_k=OPAQUE_INTEGER)
EXECUTION_POLICY = WireRecord({}, {
    **dict.fromkeys(("prompt_cache", "fallback", "accounting_version", "repetition", "assistant_history",
                     "warmup_condition", "seed_law", "turn_seed_law", "seed_model_id", "seed_thinking"), OPAQUE_STRING),
    **dict.fromkeys(("seed_bits", "seed_index", "max_episode_decode_tokens", "hybrid_checkpoint_limit"), OPAQUE_INTEGER),
    **dict.fromkeys(("deadman_s", "max_episode_seconds"), OPAQUE_FINITE_NUMBER),
    "effective_context_cap": Nullable(OPAQUE_INTEGER),
    "seed_task_pair": Nullable(OPAQUE_STRING), "sampler": SAMPLER_POLICY, "thermal": THERMAL_POLICY,
    "chat_template_kwargs": WireRecord({}, {"enable_thinking": BOOLEAN}),
    "checkpoint": RequiredRecordFields(policy=OPAQUE_STRING, limit=OPAQUE_INTEGER, boundary=OPAQUE_STRING,
                                       prefill_step_size=OPAQUE_INTEGER),
})
WORKLOAD_PROVENANCE_FIELDS = WireRecord(
    {**dict.fromkeys(("kind", "episode_spec_sha256", "transcript_sha256", "endpoint_identity", "cache_policy"),
                     OPAQUE_STRING),
     "prompt": RequiredRecordFields(realized_token_count=Nullable(OPAQUE_INTEGER), token_hash_domain=OPAQUE_STRING,
                                    token_ids_sha256=OPAQUE_STRING, text_sha256=Nullable(OPAQUE_STRING)),
     "tokenizer": RequiredRecordFields(backend=OPAQUE_STRING, identifier=Nullable(OPAQUE_STRING),
                                        revision=Nullable(OPAQUE_STRING), **{"class": Nullable(OPAQUE_STRING)},
                                        vocab_size=Nullable(OPAQUE_INTEGER)),
     "model": RequiredRecordFields(name=OPAQUE_STRING, source=Nullable(OPAQUE_STRING),
                                    revision=Nullable(OPAQUE_STRING), artifact_identity=Nullable(ARTIFACT_IDENTITY)),
     "sampler": WireRecord(
         {"kind": OPAQUE_STRING, "temperature": OPAQUE_FINITE_NUMBER, "pinned": BOOLEAN,
          "requested_temperature": OPAQUE_FINITE_NUMBER, "max_tokens": OPAQUE_INTEGER},
         {"api": OPAQUE_STRING, "parameter": OPAQUE_STRING, "enable_thinking": BOOLEAN,
          "top_p": OPAQUE_FINITE_NUMBER, "min_p": OPAQUE_FINITE_NUMBER, "top_k": OPAQUE_INTEGER,
          "constructor_kwargs": RequiredRecordFields(temp=OPAQUE_FINITE_NUMBER, top_p=OPAQUE_FINITE_NUMBER,
                                                     min_p=OPAQUE_FINITE_NUMBER, top_k=OPAQUE_INTEGER),
          "execution_policy": EXECUTION_POLICY}),
     "output_policy": WireRecord(
         {"name": OPAQUE_STRING, "stop_condition": OPAQUE_STRING,
          **dict.fromkeys(("requested_tokens", "max_turns", "max_tokens_per_turn", "emitted_tokens"), OPAQUE_INTEGER)},
         {"max_context_tokens": OPAQUE_INTEGER, "max_episode_decode_tokens": OPAQUE_INTEGER,
          "deadman_s": OPAQUE_FINITE_NUMBER}),
     "episode_outcome": WireRecord({"stop_condition": OPAQUE_STRING, "emitted_tokens": OPAQUE_INTEGER},
                                   {"token_budget": TOKEN_BUDGET}),
     "generator": RequiredRecordFields(name=OPAQUE_STRING, version=OPAQUE_STRING),
     "flags": [OPAQUE_STRING]},
)
METADATA_REQUIRED = {
    "run_id": STRING, "config_sha256": STRING, "device": DEVICE_FIELDS,
    "uncertainty_evidence": WireRecord(
        {"clock_anchor": IDENTITY_CLOCK_FIELDS},
        {"telemetry_backend": OPAQUE_STRING, "schema_version": OPAQUE_STRING, "sample_phase": SAMPLE_PHASE_FIELDS,
         "idle_drift": IDLE_DRIFT_FIELDS, "idle_drift_guard": IDLE_GUARD_FIELDS,
         "process_group_teardown": metadata_wire.PROCESS_GROUP_TEARDOWN}),
}
OPTIONAL_CONFIG_TEXT = Nullable(OPAQUE_NONBLANK_STRING)
CONFIG_FIELDS = RequiredRecordFields(
    schema_version=STRING, run_id=OPTIONAL_CONFIG_TEXT,
    model=WireRecord(
        {"name": OPAQUE_NONBLANK_STRING, "context_window": Nullable(INTEGER),
         **dict.fromkeys(("family", "source", "revision", "weight_format"), OPTIONAL_CONFIG_TEXT)},
        dict.fromkeys(("tokenizer_json_sha256", "chat_template_sha256"), STRING)),
    quantization=RequiredRecordFields(name=OPAQUE_NONBLANK_STRING, bits=Nullable(INTEGER), group_size=Nullable(INTEGER)),
    hardware_target=RequiredRecordFields(
        id=OPAQUE_NONBLANK_STRING, **dict.fromkeys(("transport", "runtime_backend", "telemetry_backend"), STRING),
        **dict.fromkeys(("host", "device_kind", "notes"), OPTIONAL_CONFIG_TEXT)),
    workload_profile=WireRecord(
        {"name": OPAQUE_NONBLANK_STRING, **dict.fromkeys(("prompt_tokens", "output_tokens"), Nullable(INTEGER)),
         **dict.fromkeys(("repetitions", "warmup_runs"), INTEGER),
         **dict.fromkeys(("prompt_text", "dataset_ref"), OPTIONAL_CONFIG_TEXT)},
        {**dict.fromkeys(("suite_manifest_ref", "suite_manifest_sha256", "generator_sidecar_ref"), OPTIONAL_CONFIG_TEXT),
         "prompt_token_evidence_policy": STRING,
         "prompt_token_expectation": RequiredRecordFields(schema_version=STRING, token_hash_domain=STRING,
                                                         token_count=INTEGER, token_ids_sha256=STRING)}),
    interconnect=RequiredRecordFields(name=OPAQUE_NONBLANK_STRING, link_speed_mbps=Nullable(OPAQUE_NONNEGATIVE_NUMBER),
                                      notes=OPTIONAL_CONFIG_TEXT),
    sampling=RequiredRecordFields(power_hz=NUMBER,
                                   **dict.fromkeys(("idle_seconds", "warmup_seconds"), OPAQUE_NONNEGATIVE_NUMBER)),
    run_metadata=RequiredRecordFields(
        project=OPAQUE_NONBLANK_STRING, operator=OPTIONAL_CONFIG_TEXT, notes=OPTIONAL_CONFIG_TEXT,
        tags=[OPAQUE_STRING], ambient_temp_c=Nullable(OPAQUE_FINITE_NUMBER)),
)
METADATA_FIELDS = WireRecord(
    METADATA_REQUIRED,
    {"boot_id": Nullable(STRING),
     **dict.fromkeys(("platform", "machine", "python_version", "joulewise_version", "schema_version",
                      "git_commit"), OPAQUE_STRING),
     "source_provenance": SOURCE_PROVENANCE_FIELDS, "clock": CLOCK_INFO_FIELDS,
     "config_warnings": [RequiredRecordFields(code=OPAQUE_STRING, path=OPAQUE_STRING, message=OPAQUE_STRING)],
     "model": CONFIG_FIELDS["model"], "quantization": CONFIG_FIELDS["quantization"],
     "workload_observed": WireRecord(
         {"token_count": Nullable(OPAQUE_INTEGER), "output_token_count": Nullable(OPAQUE_INTEGER)},
         {"token_count_source": OPAQUE_STRING}),
     "serialization_quarantine": [WireRecord(
         {"path": OPAQUE_STRING, "reason": OPAQUE_STRING}, {"key_type": OPAQUE_STRING, "value_type": OPAQUE_STRING})],
     "adapters": ADAPTER_FIELDS, "extra": EXTRA_FIELDS, "trace_window_margins": TRACE_WINDOW_MARGINS,
     "workload_provenance": WORKLOAD_PROVENANCE_FIELDS,
     "battery_float": metadata_wire.BATTERY_FLOAT, "connection": metadata_wire.CONNECTION,
     "environment": metadata_wire.ENVIRONMENT, "idle_baseline": metadata_wire.IDLE_BASELINE,
     "thermal_pre": metadata_wire.THERMAL_STATE, "thermal_post": metadata_wire.THERMAL_STATE,
     "suite": metadata_wire.SUITE,
     "campaign_policy": metadata_wire.CAMPAIGN_POLICY, "campaign_environment_preflight": metadata_wire.CAMPAIGN_PREFLIGHT,
     "environment_admission": metadata_wire.ENVIRONMENT_ADMISSION,
     "instrument_calibration": metadata_wire.INSTRUMENT_CALIBRATION,
     **dict.fromkeys(("clock_anchor_bound_s", "marker_to_first_sample_phase_bound_s",
                      "marker_to_last_sample_phase_bound_s", "idle_drift_bound_w"), Nullable(OPAQUE_FINITE_NUMBER))},
)
_METADATA_PRODUCER_MEMBERS = frozenset((
    "platform", "machine", "python_version", "joulewise_version", "schema_version", "git_commit",
    "source_provenance", "clock", "battery_float", "config_warnings", "model", "quantization", "adapters",
))
PRODUCER_METADATA_FIELDS = WireRecord(
    {name: METADATA_FIELDS[name] for name in METADATA_FIELDS.required | _METADATA_PRODUCER_MEMBERS},
    {name: schema for name, schema in METADATA_FIELDS.items()
     if name not in METADATA_FIELDS.required | _METADATA_PRODUCER_MEMBERS},
)


class ReaderBindingError(RuntimeError):
    """Verified bytes and their blind identity or timing certificate disagree."""


@dataclass(frozen=True)
class EpisodeTiming:
    episode_id: str
    clock_domain: str
    start_ns: int
    end_ns: int
    stamp_rows: tuple
    boot_id: str | None
    projected_episode: Episode

    @property
    def epoch_minus_monotonic_ns(self):
        row = self.stamp_rows[0]
        midpoint = round(Fraction(row["monotonic_before_ns"] + row["monotonic_after_ns"], 2))
        return row["epoch_ns"] - midpoint


@dataclass(frozen=True)
class RailTiming:
    period_ns: int
    supports_sha256: str
    mapping: ClockMapping
    count: int

    def evidence(self):
        return {
            "period_ns": self.period_ns, "supports_sha256": self.supports_sha256,
            "offset_ns": self.mapping.offset_ns, "uncertainty_ns": self.mapping.uncertainty_ns,
            "count": self.count,
        }


@dataclass(frozen=True)
class StreamTiming:
    path: str
    header: dict | None
    trailer: dict | None
    present: bool
    fit: dict | None
    host_ns: tuple[int, ...]


@dataclass(frozen=True)
class StreamCheck:
    path: str
    failures: tuple
    width_ns: int | None
    offset_ns: int | None
    sample_slice: tuple[int, int] | None
    times_sha256: str | None
    excess_p95_ms: float | None
    excess_max_ms: float | None

    def evidence(self):
        return {
            "stream": self.path, "failures": list(self.failures), "H_ns": self.width_ns,
            "excess_p95_ms": self.excess_p95_ms, "excess_max_ms": self.excess_max_ms,
        }


@dataclass(frozen=True)
class DCSelection:
    code: str
    candidates: tuple[StreamCheck, ...]
    selected: StreamCheck | None = None

    def evidence(self):
        widths = {item.width_ns for item in self.candidates if item.width_ns is not None}
        width = self.selected.width_ns if self.selected else next(iter(widths)) if len(widths) == 1 else None
        fields = {"dc_code": self.code, "H_ns": width,
                  "candidates": [item.evidence() for item in self.candidates]}
        if self.selected is not None:
            fields.update(stream=self.selected.path, dc_times_sha256=self.selected.times_sha256,
                          offset_ns=-self.selected.offset_ns, method=METHOD)
        return fields


def _one_identity(values):
    recorded = {value for value in values if value is not None}
    if len(recorded) > 1 or any(type(value) is not str or not value for value in recorded):
        raise TimeFieldError("invalid episode boot identity")
    return next(iter(recorded), None)


def episode_timing(episode_raw, metadata):
    view = project_json(episode_raw, EPISODE_FIELDS, strict=True)
    try:
        # Use the installed record constructor on the blind envelope. Scores,
        # router observations and non-timing hardware values are skipped or masked.
        episode = _build(Episode, view)
        analysis.thermal_intervals(episode.hardware)
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as error:
        raise TimeFieldError("invalid native episode envelope") from error
    hardware = view["hardware"]
    thermal = hardware.get("thermal", {})
    policy = thermal.get("policy")
    sensors = policy["sensors"] if policy else None
    names = ({sensors["s_fast"], sensors["s_slow"], *sensors["fan_keys"], *sensors.get("record_keys", ())}
             if sensors is not None else set())
    if any(row.get("entry_sensors", {}).keys() - names for row in thermal.get("intervals", ())):
        raise TimeFieldError("native thermal sensor key is absent from its policy")
    episode_id = view["episode_id"]
    start, end = view["start_ns"], view["end_ns"]
    stamp_rows = tuple(hardware.get("paired_clock_stamps_ns", ()))
    if (type(episode_id) is not str or not episode_id
            or view["clock_domain"] != f"joulewise.monotonic:{episode_id}"
            or type(start) is not int or type(end) is not int or start >= end
            or not stamp_rows or any(
                row.keys() != STAMP_FIELDS.keys() or any(type(v) is not int for v in row.values())
                or row["monotonic_before_ns"] > row["monotonic_after_ns"]
                or min(row["wall_resolution_ns"], row["monotonic_resolution_ns"]) < 0
                for row in stamp_rows)):
        raise TimeFieldError("invalid episode timing")
    return EpisodeTiming(episode_id, view["clock_domain"], start, end, stamp_rows,
                         _one_identity((hardware.get("boot_id"), metadata.get("boot_id"))), episode)


def binding_projection(episode, config, metadata, *, run_id, config_sha256, synthetic=False):
    shape = METADATA_FIELDS if synthetic else PRODUCER_METADATA_FIELDS
    metadata = project_json(metadata, shape, strict=True)
    if (metadata["run_id"] != run_id or metadata["config_sha256"] != config_sha256):
        raise ReaderBindingError("bundle identity")
    manifest = metadata["device"]["rail_manifest"]
    if len(manifest) != len(set(manifest)) or not RAILS <= set(manifest) <= set(RAIL_MANIFEST):
        raise TimeFieldError("native rail manifest")
    try:
        settings = project_json(config, CONFIG_FIELDS, strict=True)
        # The native ctl runner uses the base config schema. AXI decode
        # extensions have their own config and opaque backend payloads.
        if settings.get("schema_extensions") is not None:
            raise ValueError("non-native config extension")
        rate = settings["sampling"]["power_hz"]
        if type(rate) not in (float, int) or not isfinite(rate) or rate <= 0:
            raise ValueError("invalid nominal rail cadence")
        period = round(NS / rate)
        typed = BenchmarkConfig.from_mapping(settings)
        if period <= 0 or round(NS / typed.sampling.power_hz) != period:
            raise ValueError("typed rail cadence")
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise TimeFieldError("invalid native bundle config") from error
    return episode_timing(episode, metadata), period, metadata.get("uncertainty_evidence")


def _rail_mapping(timing, evidence):
    anchor = (evidence or {}).get("clock_anchor", {})
    if anchor.get("status") == "bounded":
        bound = anchor.get("effective_clock_anchor_bound_s")
        lower = anchor.get("wall_minus_monotonic_lower_s")
        upper = anchor.get("wall_minus_monotonic_upper_s")
        if (not all(analysis._finite(value) and analysis._finite(value * NS) for value in (lower, upper, bound))
                or bound < 0 or lower > upper):
            raise TimeFieldError("invalid native rail clock bound")
    try:
        mapping, flags = stamp_mapping(
            tuple(_restore_stamp(row) for row in timing.stamp_rows),
            episode_domain=timing.clock_domain, evidence=evidence,
        )
    except (OverflowError, KeyError, TypeError, ValueError) as error:
        raise TimeFieldError("invalid native rail clock mapping") from error
    if mapping.method == "unmeasured":
        raise TimeFieldError("native rail clock is unresolved")
    if not analysis._finite(mapping.uncertainty_ns) or mapping.uncertainty_ns < 0:
        raise TimeFieldError("invalid native rail clock uncertainty")
    return mapping, flags


def _native_grid(rows):
    grids = {rail: [] for rail in RAILS}
    for timestamp, _, source, rail, start, end in rows:
        if source != "powermetrics" or rail not in grids:
            raise TimeFieldError("noncomponent native rail")
        try:
            stamps = tuple(float(value) for value in (timestamp, start, end))
            t, a, b = (_packed_ns(seconds_ns(stamp)) for stamp in stamps)
        except (ValueError, OverflowError) as error:
            raise TimeFieldError("invalid native rail support timestamp") from error
        if not a < b == t:
            raise TimeFieldError("invalid native rail interval")
        grids[rail].append((t, a, b))
    grid = sorted(grids.pop("cpu_power"))
    if (len(grid) < 2 or any(a[0] >= b[0] for a, b in zip(grid, grid[1:]))
            or any(sorted(other) != grid for other in grids.values())):
        raise TimeFieldError("missing or incompatible native rail support")
    for (_, _, edge), (_, start, _) in zip(grid, grid[1:]):
        # Compare in the trace clock using the frozen reader's snapping rule.
        if start < edge and edge - start > _support_edge_quantum_ns(edge):
            raise TimeFieldError("overlapping native rail support")
    return grid


def _support_digest(grid):
    pack = struct.Struct(">qqq").pack
    digest = sha256()
    for triple in grid:
        digest.update(pack(*(_packed_ns(stamp) for stamp in triple)))
    return digest.hexdigest()


def rail_timing(payload, timing, period_ns, evidence):
    grid = _native_grid(rail_rows(payload))
    mapping, _ = _rail_mapping(timing, evidence)
    if grid[0][1] + mapping.offset_ns > timing.start_ns or grid[-1][2] + mapping.offset_ns < timing.end_ns:
        raise TimeFieldError("native rail trace does not cover episode extent")
    return RailTiming(period_ns, _support_digest(grid), mapping, len(grid))


def _join_native_rails(episode, payload, timing, rail, evidence):
    """The buffer form of the runner's read_episode_bundle sampler join."""
    if episode.power_traces or episode.clock_mappings or episode.clock_domain != timing.clock_domain:
        raise ReaderBindingError("episode is not the original native envelope")
    rows = (dict(zip(RAIL_COLUMNS, row, strict=True)) for row in rail_rows(payload))
    joined = join_episode_trace(episode, rows, nominal_interval_ns=rail.period_ns, evidence=evidence)
    traces = joined.power_traces
    mapping, = joined.clock_mappings
    if {trace.channel for trace in traces} != RAILS or mapping != rail.mapping:
        raise ReaderBindingError("decoded rail identity")
    for trace in traces:
        supports = json.loads(trace.notes)["sample_support_ns"]
        grid = ((stamp, start, end) for stamp, (start, end) in zip(trace.t_ns, supports, strict=True))
        if (trace.source != "powermetrics" or trace.clock_domain != mapping.trace_domain
                or len(trace.t_ns) != rail.count or _support_digest(grid) != rail.supports_sha256
                or not all(map(isfinite, trace.values))):
            raise ReaderBindingError("decoded rail support")
    return joined


def blind_stream(path, payload):
    view = stream_fields(payload, path)
    header, trailer = view["header"], view["trailer"]
    if header is None or header.get("schema") != "joulewise.km003c_stream.v1":
        raise TimeFieldError("not a native meter stream")
    if header.get("status") not in ("streaming", "absent"):
        raise TimeFieldError("invalid native meter status")
    if type(header.get("rate_idx")) is not int or header["rate_idx"] not in meter.STEP_MS:
        raise TimeFieldError("invalid native meter rate")
    polls = view["polls"]
    batches = [row for row in polls if row.get("seq")]
    if (any(type(row.get("rx")) is not int or "p_shape" in row for row in polls)
            or any(type(row.get("tx")) is not int or type(row.get("n")) is not int
                   or row["n"] != len(row["seq"]) for row in batches)
            or any(row.get("n") and not row.get("seq") for row in polls)):
        raise TimeFieldError("malformed native meter poll")
    if any("tx" in row and row["tx"] > row["rx"] for row in polls):
        raise TimeFieldError("reversed native meter request interval")
    if header["status"] != "streaming" or not batches:
        return StreamTiming(path, header, trailer, False, None, ())
    batches.sort(key=lambda row: row["rx"])
    samples = meter.sample_times(header, batches)
    try:
        fit = meter.clock_fit(samples, batches)
    except ValueError:
        return StreamTiming(path, header, trailer, True, None, ())
    return StreamTiming(path, header, trailer, True, fit.stats,
                        tuple(fit.host_ns(counter) for counter in samples.dev_ms))


def decoded_stream(path, payload):
    decoded = meter.parse_bytes(payload)
    view = StreamTiming(path, decoded.header, decoded.trailer, decoded.present,
                        decoded.fit.stats if decoded.fit is not None else None, tuple(decoded.host_ns))
    return view, decoded


def _integer_field(document, field):
    value = (document or {}).get(field)
    return value if type(value) is int else None


def _stream_anchors(stream):
    return (_integer_field(stream.header, "start_raw_ns"),
            _integer_field(stream.header, "start_mono_ns"),
            _integer_field(stream.header, "start_real_ns"),
            _integer_field(stream.trailer, "end_raw_ns"),
            _integer_field(stream.trailer, "end_mono_ns"))


def _packed_ns(stamp):
    if type(stamp) is not int or not -(2**63) <= stamp < 2**63:
        raise TimeFieldError("native time does not fit a signed 64-bit digest field")
    return stamp


def _times_digest(times, offset):
    pack = struct.Struct(">q").pack
    return sha256(b"".join(pack(_packed_ns(stamp - offset)) for stamp in times)).hexdigest()


def _candidate(stream, timing):
    start_raw, start_mono, start_real, end_raw, end_mono = _stream_anchors(stream)
    complete_anchors = None not in (start_raw, start_mono, start_real, end_raw, end_mono)
    if complete_anchors and (end_mono < timing.start_ns or start_mono > timing.end_ns):
        return None

    failures = set()
    if stream.trailer is None:
        failures.add("stream_unclosed")
    boot_id = stream.header.get("boot_id")
    identity_bad = (
        (start_real is not None and start_mono is not None
         and abs(start_real - start_mono - timing.epoch_minus_monotonic_ns) > 5 * NS)
        or (boot_id is not None and timing.boot_id is not None and boot_id != timing.boot_id)
    )
    if identity_bad:
        failures.add("boot_mismatch")

    width = sample_range = times_sha256 = offset = None
    fit = stream.fit or {}
    if not complete_anchors or not fit:
        failures.add("anchor_unusable")
    if None not in (start_raw, start_mono, end_raw, end_mono):
        offset = meter.raw_anchor_offset_ns(stream.header, stream.trailer, allow_unclosed=False)
        if offset is None:
            failures.add("anchor_unusable")
        if fit and offset is not None:
            rtt = meter.FIT_MAX_RTT_MS if fit["filtered"] else fit["request_rtt_ms_max"]
            if not isfinite(rtt) or rtt < 0:
                raise TimeFieldError("invalid native meter request duration")
            step_ns = meter.STEP_MS[stream.header["rate_idx"]] * 1_000_000
            spread = abs((end_raw - end_mono) - (start_raw - start_mono))
            excess = max(0, -Fraction(fit["excess_latency_ms_min"]))
            width = spread + 1_000_000 + step_ns + ceil(1_000_000 * (excess + Fraction(rtt)))
            if width < 0:
                raise TimeFieldError("negative native meter uncertainty")
            if width > CAP_NS:
                failures.add("half_width_over_cap")
    if ((start_mono is not None and start_mono > timing.start_ns)
            or (end_mono is not None and end_mono < timing.end_ns)):
        failures.add("not_bracketed")
    if offset is not None and fit:
        raw = stream.host_ns
        lo = bisect_right(raw, timing.start_ns + offset) - 1
        hi = bisect_left(raw, timing.end_ns + offset)
        if lo < 0 or hi >= len(raw):
            failures.add("not_bracketed")
        else:
            window = raw[lo:hi + 1]
            if any(a >= b for a, b in zip(window, window[1:])):
                failures.add("anchor_unusable")
            else:
                sample_range = (lo, hi + 1)
                times_sha256 = _times_digest(window, offset)

    return StreamCheck(stream.path, tuple(code for code in FAILURES if code in failures), width, offset,
                       sample_range, times_sha256, fit.get("excess_latency_ms_p95"),
                       fit.get("excess_latency_ms_max"))


def select_dc(timing, streams):
    present = tuple(stream for stream in streams if stream.present)
    if not present:
        return DCSelection("meter_absent", ())
    candidates = tuple(check for stream in present if (check := _candidate(stream, timing)) is not None)
    passing = tuple(check for check in candidates if not check.failures)
    if len(passing) == 1:
        return DCSelection("ok", candidates, passing[0])
    if passing:
        return DCSelection("ambiguous_overlap", candidates)
    failures = {failure for check in candidates for failure in check.failures}
    return DCSelection(next((code for code in FAILURES if code in failures), "not_bracketed"), candidates)


def _attach_dc(episode, selected, decoded):
    source = decoded[selected.path]
    lo, stop = selected.sample_slice
    domain = "joulewise.km003c.raw:" + selected.path
    samples = tuple(source.watts[lo:stop])
    if len(samples) != stop - lo or not all(map(isfinite, samples)):
        raise ReaderBindingError("decoded meter values")
    period = meter.STEP_MS[source.header["rate_idx"]] * 1_000_000
    trace = PowerTrace("wall_meter", "dc_in", domain, tuple(source.host_ns[lo:stop]), samples,
                       "W", period)
    mapping = ClockMapping(domain, episode.clock_domain, -selected.offset_ns, selected.width_ns, METHOD)
    return replace(episode, power_traces=(*episode.power_traces, trace),
                   clock_mappings=(*episode.clock_mappings, mapping))


def first_read(inputs, stage1):
    """Rebind each dispatched leg and join the authenticated inputs in memory."""
    inputs.verify_stage1(stage1)
    cache = {}
    positions = []
    for leg in stage1.legs:
        leg_id = leg.binding.leg_id
        position = inputs.positions[leg_id]
        if not leg.g0_released:
            positions.append(analysis.LegInput(leg_id, leg.kind, leg.admitted, False))
            continue

        pin = position["files"]
        files = {role: inputs.read_entry(position["span_id"], pin[role])
                 for role in ("episode", "config", "metadata", "rails", "script")}
        timing, period, evidence = binding_projection(
            files["episode"], files["config"], files["metadata"], run_id=position["run_id"],
            config_sha256=pin["config"]["sha256"], synthetic=inputs.synthetic,
        )
        rail = rail_timing(files["rails"], timing, period, evidence)
        certificate = inputs.certificate(leg_id)
        if timing.episode_id != leg.episode_id or rail.evidence() != certificate["rails"]:
            raise ReaderBindingError("certificate rail or episode identity")
        span_id = position["span_id"]
        if span_id not in cache:
            decoded = {}
            projected = []
            for entry in inputs.spans[span_id]["streams"]:
                path = entry["path"]
                view, decoded[path] = decoded_stream(path, inputs.read_entry(span_id, entry))
                projected.append(view)
            cache[span_id] = (projected, decoded)
        projected, decoded = cache[span_id]
        dc = select_dc(timing, projected)
        if any(certificate.get(key) != value for key, value in dc.evidence().items()):
            raise ReaderBindingError("certificate meter timing")

        work = _decode(files["script"])
        if (work["leg_id"] != leg_id or work["leg_spec_sha256"] != position["spec_sha256"]
                or work["script"]["kind"] != leg.kind):
            raise ReaderBindingError("script identity")
        try:
            episode = from_json(Episode, files["episode"])
        except ValueError:
            positions.append(analysis.LegInput(leg_id, leg.kind, leg.admitted, True, analysis.INVALID_LEG_RECORD))
            continue
        if (episode.episode_id, episode.clock_domain, episode.start_ns, episode.end_ns) != (
                timing.episode_id, timing.clock_domain, timing.start_ns, timing.end_ns):
            raise ReaderBindingError("decoded episode identity")
        episode = _join_native_rails(episode, files["rails"], timing, rail, evidence)
        if dc.selected is not None:
            episode = _attach_dc(episode, dc.selected, decoded)
        positions.append(analysis.LegInput(leg_id, leg.kind, leg.admitted, True, episode, files["script"],
                                           pin["script"]["sha256"]))
    return tuple(positions)
