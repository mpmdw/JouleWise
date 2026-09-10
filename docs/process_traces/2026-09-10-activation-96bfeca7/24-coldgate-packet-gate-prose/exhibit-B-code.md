# Exhibit B — the code the paragraphs describe (58d4696b)

## B1 joulewise/environment_admission.py lines 20–26 and 172–192
```python
ADMISSION_SCHEMA = "joulewise.environment_admission.v1"
EVALUATION_SCHEMA = "joulewise.environment_evaluation.v1"
MAX_ADMISSION_GAP_S = 600.0
# Covers four contemporary epoch-binary64 roundings; not missing samples.
ADMISSION_TIME_ROUNDING_S = 1e-6
REGISTERED_POLICY_DIR = (
    Path(__file__).resolve().parents[1] / "configs" / "campaign_policies"
...
            baseline_duration_s = (
                _finite_number(baseline.get("duration_s"))
                if isinstance(baseline, Mapping)
                else None
            )
            if (
                attempt_start_s is None
                or attempt_end_s is None
                or baseline_duration_s is None
                or baseline_duration_s <= 0.0
                or baseline_duration_s > attempt_end_s - attempt_start_s + ADMISSION_TIME_ROUNDING_S
            ):
                reasons.add("environment_admission_missing")
                continue
            capture = _attempt_capture_interval(bundle_path, expected_attempt)
            if capture is None or (
                capture[0] < attempt_start_s - ADMISSION_TIME_ROUNDING_S
                or capture[1] > attempt_end_s + ADMISSION_TIME_ROUNDING_S
            ):
                reasons.add("environment_admission_missing")

```

## B2 joulewise/controller.py cooldown_gate lines 2490–2570
```python
    """
    selected = policy if policy is not None else CooldownPolicy()
    reference = reference_baseline.power_w_mean
    sub_config = replace(
        config,
        run_id=run_id if run_id is not None else config.run_id,
        sampling=replace(config.sampling, idle_seconds=selected.subwindow_s),
    )
    start_s = clock.now()
    readings: list[tuple[float, float, float, float]] = []
    trace: list[dict[str, Any]] = []
    while True:
        subwindow_start_s = clock.now()
        baseline = telemetry.measure_idle(sub_config)
        now_s = clock.now()
        duration_s = baseline.duration_s
        if not isinstance(duration_s, int | float) or duration_s <= 0.0:
            duration_s = max(0.0, now_s - subwindow_start_s)
        evidence_start_s = now_s - float(duration_s)
        # Do not let a backend-reported duration reach backward across the
        # actual start of this bounded capture.
        evidence_start_s = max(evidence_start_s, subwindow_start_s)
        readings.append(
            (subwindow_start_s, evidence_start_s, now_s, baseline.power_w_mean)
        )
        cutoff = now_s - selected.sustained_window_s
        readings = [reading for reading in readings if reading[2] > cutoff]
        weighted_sum = 0.0
        coverage_s = 0.0
        coverage_rounding_s = 0.0
        retained_start_s: float | None = None
        for capture_start, evidence_start, evidence_end, value in readings:
            clipped_start = max(evidence_start, cutoff)
            overlap_s = max(0.0, evidence_end - clipped_start)
            weighted_sum += overlap_s * value
            coverage_s += overlap_s
            if overlap_s > 0.0:
                coverage_rounding_s += (
                    math.ulp(evidence_end) + math.ulp(clipped_start)
                )
                retained_capture_start = max(capture_start, cutoff)
                retained_start_s = (
                    retained_capture_start
                    if retained_start_s is None
                    else min(retained_start_s, retained_capture_start)
                )
        rolling_mean = weighted_sum / coverage_s if coverage_s > 0.0 else None
        window_span_s = (
            max(0.0, now_s - retained_start_s)
            if retained_start_s is not None
            else 0.0
        )
        waited_s = now_s - start_s
        try:
            thermal = telemetry.thermal_state(sub_config)
            thermal_pressure = thermal.thermal_pressure
        except Exception:  # noqa: BLE001 - unknown thermal fails the conjunctive gate
            thermal_pressure = None
        thermal_nominal = (
            isinstance(thermal_pressure, str)
            and thermal_pressure.lower() in {"nominal", "normal"}
        )
        reference_upper_w = reference * (1.0 + selected.tolerance_fraction)
        effective_upper_w = reference_upper_w
        if selected.absolute_ceiling_w is not None:
            effective_upper_w = min(effective_upper_w, selected.absolute_ceiling_w)
        required_coverage_s = (
            selected.coverage_fraction * selected.sustained_window_s
        )
        span_complete = window_span_s + 1e-6 >= selected.sustained_window_s
        coverage_slack_s = max(
            1e-6, coverage_rounding_s + math.ulp(coverage_s)
        )
        coverage_complete = coverage_s + coverage_slack_s >= required_coverage_s
        window_complete = span_complete and coverage_complete
        power_recovered = (
            rolling_mean is not None and rolling_mean <= effective_upper_w
        )
        release_criteria_met = bool(
            window_complete
            and power_recovered
```

## B3 the subwindow policy field (joulewise/schemas.py 500–515)
```python
            ),
        )


@dataclass(frozen=True)
class CooldownPolicy:
    """Sustained, one-sided cooldown-v2 release policy."""

    policy_version: str = "cooldown-v2"
    subwindow_s: float = 5.0
    sustained_window_s: float = 30.0
    coverage_fraction: float = 0.8
    tolerance_fraction: float = 0.10
    cap_s: float = 300.0
    absolute_ceiling_w: float | None = None
    require_thermal_nominal: bool = True
```
