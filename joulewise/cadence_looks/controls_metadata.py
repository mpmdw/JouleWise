"""Closed ancillary record projections for the pinned ctl-01 bundle writer."""

from .controls_time_fields import (
    OPAQUE_BOOLEAN, OPAQUE_FINITE_NUMBER, OPAQUE_INTEGER, OPAQUE_STRING,
    Nullable, RequiredRecordFields, TokenForms, WireRecord,
)


NULL_TEXT = Nullable(OPAQUE_STRING)
NULL_INT = Nullable(OPAQUE_INTEGER)
NULL_NUMBER = Nullable(OPAQUE_FINITE_NUMBER)
NULL_BOOL = Nullable(OPAQUE_BOOLEAN)

BATTERY_OBSERVATION = RequiredRecordFields(
    **dict.fromkeys(("schema", "policy_id", "phase", "stderr", "raw_stdout_sha256", "raw_path"), OPAQUE_STRING),
    **dict.fromkeys(("plan_id", "session_id", "slot", "attempt_id", "external_connected_raw",
                     "is_charging_raw", "instant_amperage_raw", "update_time_raw"), NULL_TEXT),
    **dict.fromkeys(("limit_ma", "monotonic_before_ns", "monotonic_after_ns"), OPAQUE_INTEGER),
    **dict.fromkeys(("max_update_age_s", "wall_time_s"), OPAQUE_FINITE_NUMBER),
    **dict.fromkeys(("exit_code", "object_count", "instant_amperage_ma", "update_time_s", "amperage_ma",
                     "voltage_mv", "temperature_raw", "current_capacity_pct", "apple_raw_current_capacity_mah",
                     "apple_raw_max_capacity_mah"), NULL_INT),
    **dict.fromkeys(("external_connected", "is_charging", "fully_charged"), NULL_BOOL),
    **dict.fromkeys(("passed", "timed_out", "probe_error"), OPAQUE_BOOLEAN),
    **dict.fromkeys(("argv", "property_lines", "reasons"), [OPAQUE_STRING]),
    update_age_s=NULL_NUMBER,
)
BATTERY_FLOAT = WireRecord(
    {"pre": Nullable(BATTERY_OBSERVATION), "post": Nullable(BATTERY_OBSERVATION)},
    {"not_applicable": OPAQUE_STRING, "not_reached": OPAQUE_STRING,
     "not_observed": WireRecord({}, dict.fromkeys(("pre", "post"), OPAQUE_STRING))},
)
CONNECTION = RequiredRecordFields(transport=OPAQUE_STRING, host=OPAQUE_STRING)

IDLE_BASELINE = RequiredRecordFields(
    **dict.fromkeys(("power_w_mean", "power_w_stddev", "duration_s"), OPAQUE_FINITE_NUMBER),
    **dict.fromkeys(("gpu_idle_ratio_mean", "gpu_idle_ratio_min", "gpu_freq_mhz_mean", "gpu_freq_hz_mean"), NULL_NUMBER),
    sample_count=OPAQUE_INTEGER, telemetry_backend=OPAQUE_STRING, idle_window_suspect=NULL_BOOL,
)
THERMAL_STATE = RequiredRecordFields(
    timestamp_s=OPAQUE_FINITE_NUMBER, temperature_c=NULL_NUMBER, thermal_pressure=NULL_TEXT, fan_state=NULL_TEXT,
    metadata=WireRecord({}, {"source": OPAQUE_STRING, "temperature_c_available": OPAQUE_BOOLEAN}),
)
SUITE = RequiredRecordFields(
    **dict.fromkeys(("suite_id", "suite_profile", "suite_revision", "manifest_sha256", "source_file_sha256",
                     "order_policy"), OPAQUE_STRING),
    item_count=OPAQUE_INTEGER, order_seed=NULL_INT, order_row=NULL_INT,
)
PROCESS_GROUP_TEARDOWN = RequiredRecordFields(
    **dict.fromkeys(("status", "isolation_mode", "termination_signal", "census_method"), OPAQUE_STRING),
    **dict.fromkeys(("spawn_observed", "kill_escalated", "census_completed", "survivors_detected", "leader_reaped"),
                     OPAQUE_BOOLEAN),
    **dict.fromkeys(("direct_child_pid", "process_group_id"), NULL_INT),
    **dict.fromkeys(("spawn_argv", "sampler_argv", "errors"), [OPAQUE_STRING]),
    **dict.fromkeys(("termination_grace_s", "census_timeout_s"), OPAQUE_FINITE_NUMBER),
    exception_class=NULL_TEXT,
    group_survivors=[RequiredRecordFields(pid=OPAQUE_INTEGER, state=OPAQUE_STRING)],
    escaped_candidates=[RequiredRecordFields(pid=OPAQUE_INTEGER, argv=[OPAQUE_STRING])],
    signal_attempts=[RequiredRecordFields(signal=OPAQUE_STRING, target=OPAQUE_STRING, outcome=OPAQUE_STRING)],
)

# The initial display inventory and the post-run guard have different fixed
# members. Both use the same parser for observed display counts.
DISPLAY_BASE = {
    **dict.fromkeys(("status", "probe", "reason"), NULL_TEXT),
    **dict.fromkeys(("active_displays", "external_display_count", "built_in_display_count"), NULL_INT),
}
ASLEEP_COUNTS = dict.fromkeys(("asleep_evidence_count", "asleep_display_count"), NULL_INT)
ENVIRONMENT_POWER = RequiredRecordFields(
    adapter_watts=NULL_INT, adapter_description=NULL_TEXT,
    **dict.fromkeys(("external_connected", "is_charging", "fully_charged"), NULL_BOOL),
)
ADAPTER_POWER = RequiredRecordFields(
    source=OPAQUE_STRING, adapter_watts=NULL_NUMBER, adapter_description=NULL_TEXT, power_source=NULL_TEXT,
)
GUARD_ERRORS = ("system_profiler_spdisplays", "pmset_systemstate", "screensaver_defaults", "ioreg_hid_idle",
                "ioreg_battery", "collector")
GUARD_BASE = {
    "display_power_state": NULL_TEXT, "screensaver_module": NULL_TEXT, "screensaver_engaged": NULL_BOOL,
    "hid_idle_s": NULL_NUMBER, "screensaver_delay_s": NULL_INT,
}
POST_RUN_OBSERVATION = WireRecord(
    {"capture_skipped": OPAQUE_BOOLEAN, "captured_at_s": NULL_NUMBER},
    {**GUARD_BASE, "skip_reason": OPAQUE_STRING, "display": RequiredRecordFields(**DISPLAY_BASE, **ASLEEP_COUNTS),
     "errors": WireRecord({}, dict.fromkeys(GUARD_ERRORS, OPAQUE_STRING)), "power": ENVIRONMENT_POWER,
     "adapter_power_observation": ADAPTER_POWER, "capture_duration_s": OPAQUE_FINITE_NUMBER,
     "collector_error": OPAQUE_STRING},
)
ENVIRONMENT = WireRecord(
    {**GUARD_BASE,
     **dict.fromkeys(("power_source", "battery_state", "thermal_pressure", "thermal_probe_reason", "product_name",
                      "product_version", "build_version", "hw_model", "cpu_brand"), NULL_TEXT),
     **dict.fromkeys(("battery_percent", "powermode", "boot_time_s", "logical_cpu_count", "captured_for_rep"), NULL_INT),
     **dict.fromkeys(("low_power_mode", "display_sleep_prevented"), NULL_BOOL),
     **dict.fromkeys(("memory_free_percent", "memory_pressure_percent", "uptime_s", "load_average_1m",
                      "load_average_5m", "load_average_15m", "captured_at_s", "settle_s"), NULL_NUMBER),
     "capture_skipped": OPAQUE_BOOLEAN, "capture_scope": OPAQUE_STRING, "env_capture_duration_s": OPAQUE_FINITE_NUMBER,
     "memory": RequiredRecordFields(
         swap_usage=Nullable(RequiredRecordFields.fromkeys(("total", "used", "free"), OPAQUE_STRING)),
         **dict.fromkeys(("page_size_bytes", "pages_free", "pageins", "pageouts", "pages_occupied_by_compressor",
                          "pages_stored_in_compressor", "compressor_bytes"), NULL_INT)),
     "display": WireRecord(
         {**DISPLAY_BASE, **dict.fromkeys(("framebuffer_pipes_total", "framebuffer_pipes_external_capable"), NULL_INT)},
         ASLEEP_COUNTS),
     "power": ENVIRONMENT_POWER,
     "clock_sync": RequiredRecordFields(status=OPAQUE_STRING, timed_running=NULL_BOOL, timed_probe_error=NULL_TEXT),
     "python_packages": RequiredRecordFields.fromkeys(
         ("mlx", "mlx-lm", "transformers", "mlx-metal", "tokenizers"),
         WireRecord({"present": OPAQUE_BOOLEAN, "version": NULL_TEXT}, {"error": OPAQUE_STRING})),
     "errors": WireRecord({}, dict.fromkeys((
         *GUARD_ERRORS, "pmset_batt", "pmset", "pmset_assertions", "memory_pressure", "vm_stat", "sysctl_hw_memsize",
         "sysctl_vm_swapusage", "ioreg_framebuffer_pipes", "sysctl_kern_boottime", "pgrep_timed", "pmset_therm",
         "uptime", "sw_vers", "sysctl_host",
     ), OPAQUE_STRING))},
    {"skip_reason": OPAQUE_STRING, "post_run_observation": POST_RUN_OBSERVATION},
)

CAPTURE_FIELDS = frozenset(("capture_skipped", "capture_scope", "captured_for_rep", "captured_at_s",
                            "env_capture_duration_s", "settle_s"))
ENVIRONMENT_SNAPSHOT = WireRecord(
    {key: ENVIRONMENT[key] for key in ENVIRONMENT.required - CAPTURE_FIELDS},
    {key: ENVIRONMENT[key] for key in (*CAPTURE_FIELDS, "skip_reason")},
)
ENVIRONMENT_FINDING = TokenForms({"str": OPAQUE_STRING, "lit": Nullable(OPAQUE_BOOLEAN)})
ENVIRONMENT_EVALUATION = RequiredRecordFields(
    **dict.fromkeys(("schema_version", "snapshot_sha256", "findings_sha256"), OPAQUE_STRING),
    eligible=OPAQUE_BOOLEAN, findings=[RequiredRecordFields(
        code=OPAQUE_STRING, field=OPAQUE_STRING, status=OPAQUE_STRING,
        actual=ENVIRONMENT_FINDING, required=ENVIRONMENT_FINDING)],
    load_average_evidence=RequiredRecordFields(
        **dict.fromkeys(("load_average_1m", "load_average_5m", "load_average_15m"), NULL_NUMBER), admission_gate=OPAQUE_BOOLEAN),
)
IDLE_EXTENSION_BINDING = RequiredRecordFields(
    schema_version=OPAQUE_STRING, policy_version=OPAQUE_STRING, claim_bearing=OPAQUE_BOOLEAN, sha256=OPAQUE_STRING,
)
CAMPAIGN_POLICY = WireRecord(
    {**dict.fromkeys(("schema_version", "policy_id", "policy_version", "profile", "sha256", "source"), OPAQUE_STRING),
     "calibration_bracketing": RequiredRecordFields(require_bracket=OPAQUE_BOOLEAN, calibration_bracket_max_drift_s=NULL_NUMBER)},
    {"idle_admission_extension": IDLE_EXTENSION_BINDING},
)
CAMPAIGN_PREFLIGHT = RequiredRecordFields(
    **dict.fromkeys(("schema_version", "policy_sha256", "captured_at", "initial_snapshot_sha256",
                    "initial_findings_sha256"), OPAQUE_STRING),
    snapshot=ENVIRONMENT_SNAPSHOT, evaluation=ENVIRONMENT_EVALUATION,
    arm_quiet_mode=RequiredRecordFields(
        requested=OPAQUE_BOOLEAN, countdown_s=NULL_INT, command=Nullable([OPAQUE_STRING]), command_returncode=NULL_INT,
        verified_by_reprobe=OPAQUE_BOOLEAN),
    override=Nullable(RequiredRecordFields(
        **dict.fromkeys(("schema_version", "snapshot_sha256", "findings_sha256", "reason", "approver", "timestamp",
                         "source", "classification"), OPAQUE_STRING), claim_eligible=OPAQUE_BOOLEAN)),
    enforced=OPAQUE_BOOLEAN, admitted=OPAQUE_BOOLEAN,
)
CPU_ADMISSION = RequiredRecordFields(
    schema_version=OPAQUE_STRING, decision=OPAQUE_STRING, admitted=OPAQUE_BOOLEAN, conditions=[OPAQUE_STRING],
    sample_count=OPAQUE_INTEGER, cpu_busy_ratio_p95=NULL_NUMBER, processor_combined_power_w_p95=NULL_NUMBER,
    criteria=RequiredRecordFields(cpu_busy_ratio_p95_max=OPAQUE_FINITE_NUMBER,
                                 processor_combined_power_w_p95_max=OPAQUE_FINITE_NUMBER,
                                 min_samples=OPAQUE_INTEGER, on_missing_telemetry=OPAQUE_STRING),
    gpu_admitted=NULL_BOOL,
)
ENVIRONMENT_ADMISSION = WireRecord(
    {**dict.fromkeys(("schema_version", "policy_version", "on_fail"), OPAQUE_STRING),
     "attempts": [WireRecord(
         {"attempt": OPAQUE_INTEGER, "start_s": OPAQUE_FINITE_NUMBER, "end_s": OPAQUE_FINITE_NUMBER,
          "baseline": IDLE_BASELINE, "admitted": OPAQUE_BOOLEAN},
         {"gpu_admitted": NULL_BOOL, "cpu_admission": CPU_ADMISSION, "cpu_admission_enforced": OPAQUE_BOOLEAN})],
     "per_run_environment_evaluation": RequiredRecordFields(
         **ENVIRONMENT_EVALUATION, snapshot=ENVIRONMENT_SNAPSHOT),
     "critical_environment_passed": OPAQUE_BOOLEAN, "reference_provenance_present": OPAQUE_BOOLEAN,
     "decision": NULL_TEXT, "claim_reason": NULL_TEXT},
    {"idle_admission_extension": IDLE_EXTENSION_BINDING, "failure": OPAQUE_STRING,
     "retry_backoff": RequiredRecordFields.fromkeys(("requested_s", "start_s", "end_s"), OPAQUE_FINITE_NUMBER),
     "guard_observations": [WireRecord(
         {**GUARD_BASE, "phase": OPAQUE_STRING, "capture_skipped": OPAQUE_BOOLEAN,
          "errors": WireRecord({}, dict.fromkeys(GUARD_ERRORS, OPAQUE_STRING))},
         {"display": RequiredRecordFields(**DISPLAY_BASE, **ASLEEP_COUNTS), "power": ENVIRONMENT_POWER,
          "adapter_power_observation": ADAPTER_POWER, "skip_reason": OPAQUE_STRING, "collector_error": OPAQUE_STRING})]},
)
INSTRUMENT_CALIBRATION = WireRecord(
    {**dict.fromkeys(("artifact_path", "artifact_sha256", "validation_manifest_path", "validation_manifest_sha256"),
                     OPAQUE_STRING),
     "b_fiducial_s": OPAQUE_FINITE_NUMBER, "verified_effective_b_fiducial_s": OPAQUE_FINITE_NUMBER,
     "bindings": RequiredRecordFields(
         **dict.fromkeys(("hardware_model", "os_build", "mlx_version"), NULL_TEXT),
         **dict.fromkeys(("powermetrics_sha256", "anchor_method_version", "pulse_protocol_id", "power_policy",
                         "estimator_revision", "protocol_sha256"), OPAQUE_STRING), sampling_interval_ms=OPAQUE_INTEGER),
     "binding_observations": RequiredRecordFields(powermetrics_sha256=NULL_TEXT, power_policy=NULL_TEXT)},
    {"g2a_pre_bracket": RequiredRecordFields.fromkeys(
        ("session_id", "slot", "plan_sha256", "receipt_digest"), OPAQUE_STRING),
     "g2b_pre_slot": RequiredRecordFields.fromkeys(
        ("session_id", "slot", "plan_id", "plan_sha256", "receipt_digest", "launch_lineage_locator_sha256"),
        OPAQUE_STRING)},
)
