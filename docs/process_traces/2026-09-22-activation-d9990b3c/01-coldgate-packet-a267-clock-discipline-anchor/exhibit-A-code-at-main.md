# Exhibit A — code at main `9b6b3f0e` (verbatim `git show` extracts; the magistrate wrote only the headings)

### A1 — `joulewise/uncertainty_evidence.py` lines 28,45 (git show 9b6b3f0e:joulewise/uncertainty_evidence.py | sed -n '28,45p')

```
CLOCK_ANCHOR_UNRESOLVED = "clock_anchor_unresolved"
SCHEMA_FOR_ANCHOR_METHOD = {
    CLOCK_METHOD: SCHEMA_VERSION,
    CLOCK_METHOD_V2: SCHEMA_VERSION_V2,
    CLOCK_METHOD_V3: SCHEMA_VERSION_V3,
}
# D-078 fail-closed limits for the v2 censored-intersection anchor estimator.
MAX_WALL_MINUS_MONOTONIC_SPAN_S = 0.005
MAX_FIRST_PARSE_LAG_S = 0.25
MAX_AFFINE_CLOCK_RESIDUAL_S = 0.000250
MAX_CLOCK_RATE_DEVIATION_PPM = 50.0
MIN_RATE_FIT_BASELINE_S = 60.0
MIN_NATIVE_ROLLOVERS = 2
MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S = 0.005
# Float64 representation pricing (cold science review 2026-08-18, Q1c and
# condition 2).  The v3 chain is exact rational arithmetic, but its inputs are
# recorded binary64 values that ``Fraction`` exactifies: an inexact stored value
# is turned into an exact rational that may sit INWARD of the quantity it
```

### A2 — `joulewise/uncertainty_evidence.py` lines 814,905 (git show 9b6b3f0e:joulewise/uncertainty_evidence.py | sed -n '814,905p')

```
def derive_powermetrics_anchor_v3(
    *,
    stamps: Mapping[str, ClockStamp],
    records: Sequence[NativeAnchorRecord],
) -> dict[str, Any]:
    """Exact affine-rate set-membership anchor (schema ``p2-038.3``).

    Method identity: ``powermetrics_native_second_rate_aware_set_membership_v1``.
    The three paragraphs below are part of that identity, not commentary: the
    cold science review of 2026-08-18 ratified the method conditional on them
    being stated where the method lives (conditions 3 and 4).

    **Model condition (review Q1a).** Containment is conditional on a model,
    not unconditional. The model is (i) the wall clock is affine in monotonic
    time across the capture -- one rate, no mid-capture step -- and (ii) every
    native whole-second label may depart from that affine relation by at most
    ``MAX_AFFINE_CLOCK_RESIDUAL_S`` (250 us), an allowance charged IN FULL,
    always, never shrunk to an observed residual. Within the model the emitted
    interval contains the true first-record endpoint by construction: sustained
    slew cannot understate the bound (its drift is charged in full by the
    wall-minus-monotonic span term below), a rate projection touching
    +/-``MAX_CLOCK_RATE_DEVIATION_PPM`` refuses rather than clips, and a
    mid-capture rate change refuses at small magnitude because long-baseline
    stamp pairs constrain the rate to ~0.05 ppm width. The one genuine evasion
    window is a NON-affine wall excursion of at most ~250 us occurring between
    stamps: the arithmetic cannot see it, and it is excluded STRUCTURALLY, not
    statistically, by the authenticated network-time-OFF admission required of
    prospective claim-bearing captures (consult I4). Per-member network-time
    provenance therefore travels with every record derived by this method; a
    capture with network time ON or unknown is validation-only material, and no
    fitted rate may be treated as a substitute for that environmental control.

    **Span-term dependency (review Q1b).** The bound composes
    ``H + wall_minus_monotonic_span_s + stamp_resolution_s +
    numeric_padding_s``, and the first two terms price DIFFERENT errors. ``H``
    is half the projected anchor interval: it prices where the first record's
    endpoint sits on the wall timeline. ``wall_minus_monotonic_span_s`` prices
    within-capture wall-versus-elapsed drift, and it is load-bearing because
    the detector maps the trace forward from the single anchor point at rate
    exactly 1 (``joulewise.powermetrics_fiducial`` re-parses the raw records
    with ``first_record_endpoint_s`` and accumulates ``elapsed_ns``) while the
    pulse commands that trace is compared against carry wall-epoch stamps.
    Neither term subsumes the other and removing either breaks containment.
    Dropping the span term is lawful ONLY together with re-mapping the trace
    under the fitted rate window ``[rate_lower, rate_upper]`` -- that is a
    different estimator and requires a NEW method identity, not an edit here.
    The only true overlap is that the 250 us allowance widens ``H`` while a
    real departure also inflates the span; that is priced, one-sided
    conservatism of order <= ~0.5 ms and is retained deliberately.

    **Numeric pricing (review Q1c, condition 2).** ``NUMERIC_PADDING_S`` prices
    the float64 representation error of the epoch-scale inputs this function
    exactifies with ``Fraction``; see that constant's derivation. The guard
    below refuses ``numeric_padding_insufficient`` rather than assuming the
    constant is large enough for the capture's own epoch scale.
    """

    serialized_stamps = {
        name: stamp_to_dict(stamps[name])
        for name in STAMP_ORDER
        if name in stamps
    }
    if set(serialized_stamps) != set(STAMP_ORDER):
        return _unresolved_anchor_v3(
            "clock_stamp_unavailable", serialized_stamps
        )
    ordered = [stamps[name] for name in STAMP_ORDER]
    if not all(_valid_stamp(stamp) for stamp in ordered) or any(
        current.monotonic_before_s < previous.monotonic_before_s
        for previous, current in zip(ordered, ordered[1:])
    ):
        return _unresolved_anchor_v3("clock_stamp_invalid", serialized_stamps)
    if not records:
        return _unresolved_anchor_v3(
            "native_records_unavailable", serialized_stamps
        )
    if any(
        isinstance(record.elapsed_ns, bool)
        or not isinstance(record.elapsed_ns, int)
        or record.elapsed_ns <= 0
        or isinstance(record.native_timestamp_ns, bool)
        or not isinstance(record.native_timestamp_ns, int)
        for record in records
    ):
        return _unresolved_anchor_v3(
            "native_exact_inputs_unavailable", serialized_stamps
        )

    elapsed_ns = [record.elapsed_ns for record in records]
    native_ns = [record.native_timestamp_ns for record in records]
    # The gate above proves these optional fields are concrete integers.
    assert all(isinstance(value, int) for value in elapsed_ns)
```

### A3 — `joulewise/uncertainty_evidence.py` lines 990,1010 (git show 9b6b3f0e:joulewise/uncertainty_evidence.py | sed -n '990,1010p')

```
    if controller_coverage_ns < baseline_ns:
        return _unresolved_anchor_v3(
            "clock_fit_span_insufficient",
            serialized_stamps,
            {"rate_fit_baseline_s": float(baseline_s)},
        )

    offset_lower_s, offset_upper_s, offset_span_s = _offset_envelope_s(ordered)
    if (
        not math.isfinite(offset_span_s)
        or offset_span_s > MAX_WALL_MINUS_MONOTONIC_SPAN_S
    ):
        return _unresolved_anchor_v3(
            "wall_minus_monotonic_span_exceeded",
            serialized_stamps,
            {"wall_minus_monotonic_span_s": offset_span_s},
        )

    # Price the float64 representation error of the epoch-scale inputs this
    # estimator exactifies (review Q1c / condition 2).  The padding constant is
    # fixed, so the coverage claim is checked against THIS capture's epoch
```

### A4 — `joulewise/uncertainty_evidence.py` lines 1085,1105 (git show 9b6b3f0e:joulewise/uncertainty_evidence.py | sed -n '1085,1105p')

```
    box: _LP2Box = (
        beta_box_lower,
        beta_box_upper,
        a_box_lower,
        a_box_upper,
    )
    native_rows = _native_v3_constraints(
        exact_native_ns, cumulative_ns, departure_ns
    )
    if _lp2(native_rows, "min A", box=box) is None:
        return _unresolved_anchor_v3(
            "rate_aware_native_set_empty", serialized_stamps
        )
    native_stamp_rows = [*native_rows, *stamp_rows]
    if _lp2(native_stamp_rows, "min A", box=box) is None:
        return _unresolved_anchor_v3("affine_clock_fit_empty", serialized_stamps)
    joint_rows = [*native_stamp_rows, *causal_rows]
    if _lp2(joint_rows, "min A", box=box) is None:
        relaxed_native_rows = _native_v3_constraints(
            exact_native_ns, cumulative_ns, ns_per_second
        )
```

### A5 — `joulewise/uncertainty_evidence.py` lines 1170,1240 (git show 9b6b3f0e:joulewise/uncertainty_evidence.py | sed -n '1170,1240p')

```
        if _lp2(
            [*midpoint_rows, *stamp_rows, *causal_rows],
            "min A",
            box=box,
        ) is None:
            residual_lower = midpoint
        else:
            residual_upper = midpoint

    half_width_ns = (anchor_upper_ns - anchor_lower_ns) / 2
    anchor_only_bound = half_width_ns / ns_per_second
    stamp_resolution_s = max(
        max(stamp.wall_resolution_s, stamp.monotonic_resolution_s)
        for stamp in ordered
    )
    exact_effective_bound = (
        anchor_only_bound
        + Fraction(offset_span_s)
        + Fraction(stamp_resolution_s)
        + Fraction(NUMERIC_PADDING_S)
    )
    effective_bound_s = _round_outward_up(exact_effective_bound)
    anchor_lower_s = _round_outward_down(anchor_lower_ns / ns_per_second)
    anchor_upper_s = _round_outward_up(anchor_upper_ns / ns_per_second)
    anchor_point_s = float(
        (anchor_lower_ns + anchor_upper_ns) / (2 * ns_per_second)
    )
    bounded_record: dict[str, Any] = {
        "status": "bounded",
        "method": CLOCK_METHOD_V3,
        "clock_stamps": serialized_stamps,
        "records_checked": len(records),
        "native_rollover_count": rollovers,
        "rate_fit_baseline_s": float(baseline_s),
        "model_departure_allowance_s": MAX_AFFINE_CLOCK_RESIDUAL_S,
        "min_l_infinity_residual_upper_bound_s": _round_outward_up(
            residual_upper / ns_per_second
        ),
        **rate_fields,
        "anchor_lower_epoch_s": anchor_lower_s,
        "anchor_upper_epoch_s": anchor_upper_s,
        "admissible_lower_epoch_s": anchor_lower_s,
        "admissible_upper_epoch_s": anchor_upper_s,
        "first_sample_end_point_epoch_s": anchor_point_s,
        "anchor_only_bound_s": _round_outward_up(anchor_only_bound),
        "wall_minus_monotonic_lower_s": offset_lower_s,
        "wall_minus_monotonic_upper_s": offset_upper_s,
        "wall_minus_monotonic_span_s": offset_span_s,
        "stamp_resolution_s": stamp_resolution_s,
        "numeric_padding_s": NUMERIC_PADDING_S,
        "epoch_representation_term_s": epoch_representation_term_s,
        "first_parse_lag_s": first_parse_lag_s,
        "effective_clock_anchor_bound_s": effective_bound_s,
        "arithmetic": "exact_rational_outward_rounded_v1",
    }
    if effective_bound_s > MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S:
        return _unresolved_anchor_v3(
            "effective_clock_anchor_bound_exceeded",
            serialized_stamps,
            {
                key: value
                for key, value in bounded_record.items()
                if key not in {"status", "method", "clock_stamps"}
            },
        )
    return bounded_record


def derive_powermetrics_clock_evidence_v3(
    *,
    stamps: Mapping[str, ClockStamp],
```

### A6 — `scripts/sample_quiet_predicate_evidence.py` lines 237,310 (git show 9b6b3f0e:scripts/sample_quiet_predicate_evidence.py | sed -n '237,310p')

```
def overlap(a, b, c, d):
    return max(0.0, min(b, d) - max(a, c))


def integrate(frames, start, end, uncertainty_s=0.0):
    """Overlap seconds times watts; means divide by each rail's own coverage.

    For each averaging interval, moving either boundary by at most epsilon
    changes overlap by <=2*epsilon. Sum P_i*min(dt_i,2*epsilon) over frames
    touching the expanded round. This conservative interval-power bound does
    not shrink with sample count. Unobserved gaps have no finite energy bound.
    """
    if end <= start or uncertainty_s < 0:
        raise ValueError("invalid round support or alignment uncertainty")
    for left, right in zip(frames, frames[1:]):
        if right["start_s"] < left["end_s"] - 1e-6:
            raise ValueError("overlapping or unordered native supports")
    weighted = [(f, overlap(start, end, f["start_s"], f["end_s"])) for f in frames]
    coverage = math.fsum(w for _, w in weighted)
    energy, rail_coverage, bounds, power = {}, {}, {}, {}
    for rail in RAILS:
        selected = [(f["power"][rail], w) for f, w in weighted
                    if w > 0 and f["power"][rail] is not None]
        den = math.fsum(w for _, w in selected)
        expanded_coverage = math.fsum(overlap(start - uncertainty_s, end + uncertainty_s,
            f["start_s"], f["end_s"]) for f in frames if f["power"][rail] is not None)
        joules = math.fsum(p * w for p, w in selected)
        rail_coverage[rail] = den
        energy[rail] = joules if den else None
        power[rail] = joules / den if den else None
        bounds[rail] = (math.fsum(
            f["power"][rail] * min(f["elapsed_s"], 2 * uncertainty_s)
            for f in frames if f["power"][rail] is not None
            and overlap(start - uncertainty_s, end + uncertainty_s, f["start_s"], f["end_s"]) > 0)
            if expanded_coverage >= end - start + 2 * uncertainty_s - 1e-6 else None)
    power.update(coverage_s=coverage, rail_coverage_s=rail_coverage, energy_j=energy)
    def average_entities(kind, id_key, keys):
        ids = sorted({entry[id_key] for f, w in weighted if w > 0
                      for entry in f[kind] if entry[id_key] is not None}, key=str)
        result = []
        for entity in ids:
            row = {id_key: entity, "coverage_s": {}}
            for key in keys:
                values = [(entry[key], w) for f, w in weighted if w > 0 for entry in f[kind]
                          if entry[id_key] == entity and entry[key] is not None]
                den = math.fsum(w for _, w in values)
                row[key] = math.fsum(v * w for v, w in values) / den if den else None
                row["coverage_s"][key] = den
            result.append(reasons(row))
        return result
    return {
        "power": reasons(power, "no covered native samples for this rail"),
        "clusters": average_entities("clusters", "name", ("active_ratio", "idle_ratio", "down_ratio", "online_ratio", "freq_hz")) or None,
        "cpus": average_entities("cpus", "cpu", ("active_ratio", "freq_hz")) or None,
        "span_mismatch": abs(coverage - (end - start)) > 1e-6,
        "error_bound_j": bounds["rail_sum_w"], "rail_error_bound_j": reasons(bounds, "incomplete rail coverage; unobserved energy is unbounded"),
    }


def reduce_interior(frames, anchor, start, duration):
    """Integrate native interval supports; never rescale a whole-round mean."""
    result = {"start_epoch_s": start, "end_epoch_s": start + duration,
              "duration_s": duration, "complete_support": False, "status": "partial",
              "native_samples": 0, "power": None, "reason": "clock anchor unresolved"}
    if anchor.get("status") != "bounded":
        return reasons(result)
    values = integrate(frames, start, start + duration, anchor["effective_clock_anchor_bound_s"])
    complete = (not values["span_mismatch"] and all(
        abs(values["power"]["rail_coverage_s"][rail] - duration) <= 1e-6
        for rail in ("rail_sum_w", "combined_w")))
    result.update(values, complete_support=complete, status="complete" if complete else "partial",
                  native_samples=sum(overlap(start, start + duration, f["start_s"], f["end_s"]) > 0 for f in frames),
                  reason="complete native support" if complete else "incomplete interior support")
    return reasons(result)
```

### A7 — `scripts/sample_quiet_predicate_evidence.py` lines 744,756 (git show 9b6b3f0e:scripts/sample_quiet_predicate_evidence.py | sed -n '744,756p')

```
    metadata = metadata_reader()
    session = {"schema": SCHEMA, "session": session_id, **metadata,
               "state": args.state, "repeat": args.repeat, "load_setting": args.load_cores,
               "duration_s": args.duration_s, "sample_interval_s": args.sample_interval_s,
               "power_interval_ms": args.power_interval_ms, "power_enabled": args.power,
               "powermetrics_needs_root": True, "sudo_policy_probed": False,
               "evidence_status": "PROVISIONAL", "network_time_provenance": None,
               "alignment_model": ALIGNMENT_MODEL,
               "network_time_provenance_reason": "not established by this desk harness",
               "observer_definition": "SELF + reaped CHILDREN over production smoke incl. raw/stamp hooks; recorder CPU excluded",
               "round_workers": [], "power": None, "error": None, "error_rounds": 0}
    envelope_cpu_start = cpu_total()
    start = clock.stamp()
```

### A8 — `scripts/sample_quiet_predicate_evidence.py` lines 853,876 (git show 9b6b3f0e:scripts/sample_quiet_predicate_evidence.py | sed -n '853,876p')

```
        # the frozen scheduled start, preserving the bracket uncertainty.
        interior_epoch = start.epoch_s - (session["start_drift_s"] or 0) + args.interior_offset_s
        session["interior"] = reduce_interior(frames, interior_anchor, interior_epoch, args.interior_s)
    for row in rows:
        align = row["alignment"]
        why = str(anchor.get("detail", anchor.get("reason", "clock anchor unresolved")))
        if anchor["status"] == "bounded" and row["round_wall_end_s"] > row["round_wall_start_s"]:
            epsilon = anchor["effective_clock_anchor_bound_s"]
            # Add this round's own wall-read brackets to the production bound.
            epsilon += max(s["monotonic_after_s"] - s["monotonic_before_s"]
                           for s in (align["round_start_stamp"], align["round_end_stamp"]))
            values = integrate(frames, row["round_wall_start_s"], row["round_wall_end_s"], epsilon)
            row.update({k: values[k] for k in ("power", "clusters", "cpus")})
            align.update(anchor_lo=anchor["admissible_lower_epoch_s"], anchor_hi=anchor["admissible_upper_epoch_s"],
                         error_bound_j=values["error_bound_j"], rail_error_bound_j=values["rail_error_bound_j"],
                         frame_span_mismatch=values["span_mismatch"], error_bound_s=epsilon,
                         error_bound_j_reason="incomplete rail coverage; unobserved energy is unbounded")
        else:
            align.update(frame_span_mismatch=True, error_bound_j_reason=why)
            row["power"] = reasons(row["power"], why)
        align.update(method=anchor.get("method"), anchor_status=anchor["status"],
                     model=ALIGNMENT_MODEL,
                     bound_method="sum of per-frame overlap perturbation bounds on the interval-average power signal; gaps unbounded")
        if align["error_bound_j"] is not None:
```

### A9 — `joulewise/arm_readiness_evidence_t0.py` lines 1134,1146 (git show 9b6b3f0e:joulewise/arm_readiness_evidence_t0.py | sed -n '1134,1146p')

```
def _derive_clock_attestation(context: _Context) -> _DerivedRow:
    kind = "CLOCK_ATTESTATION"
    r0, r0_identity, _r0_agreement = _captured_clock_reference(
        context, kind=kind
    )
    disable, disable_identity = _capture(context, "clock-disable", kind=kind)
    _capture_ok(disable, kind=kind, label="network-time disable capture")
    if not _systemsetup_argv(disable["argv"], ("-setusingnetworktime", "off")):
        raise _underivable(kind, "network-time disable capture used the wrong command")
    if not (
        r0["batch_finished_monotonic_raw_ns"]
        >= r0["anchor_monotonic_raw_ns"]
        and context.captures["clock-reference"][0]["finished_monotonic_ns"]
```

### A10 — `joulewise/arm_readiness_evidence_t0.py` lines 1216,1245 (git show 9b6b3f0e:joulewise/arm_readiness_evidence_t0.py | sed -n '1216,1245p')

```
def _derive_clock_probe(context: _Context) -> _DerivedRow:
    kind = "CLOCK_PROBE"
    disable, disable_identity = _capture(context, "clock-disable", kind=kind)
    _capture_ok(disable, kind=kind, label="network-time disable capture")
    probe = _fresh_probe(
        context,
        kind,
        "network-time off enforcement",
        (
            "/usr/bin/sudo",
            "-n",
            "/usr/sbin/systemsetup",
            "-setusingnetworktime",
            "off",
        ),
    )
    if probe.exit_code != 0:
        raise _underivable(
            kind, "fresh D-127 enforcement exited nonzero before setting Off"
        )
    if probe.stdout != _readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT:
        raise _underivable(
            kind, "fresh D-127 enforcement stdout did not exactly report Off"
        )
    return _DerivedRow(
        "clock.network_time_off",
        kind,
        {"fresh_probe": True, "network_time": "off"},
        "PROBE",
        input_artifacts=(disable_identity,),
```

### A11 — `joulewise/arm_readiness.py` lines 100,106 (git show 9b6b3f0e:joulewise/arm_readiness.py | sed -n '100,106p')

```
CONTRACT_ID = "D-134"
ROW_REGISTRY_RELATIVE_PATH = Path("configs/arm_readiness/d117_row_registry_v2.json")
_T0_EVIDENCE_SOURCE_SCHEMA = "joulewise.arm_readiness_t0_evidence_source.v1"
_T0_INPUT_DIRECTORY = "arm_readiness.t0.inputs"
EXPECTED_NETWORK_TIME_OFF_STDOUT = "setUsingNetworkTime: Off\n"
"""Ed must bench-verify these exact sudo bytes before this value gates a window."""
# Launch-recipe receipts and sources are canonical JSON records measured in
```

### A12 — `scripts/joulewise-network-time.sudoers` lines 1,4 (git show 9b6b3f0e:scripts/joulewise-network-time.sudoers | sed -n '1,4p')

```
# JouleWise D-127: fixed network-time toggle capability for operator edr.
Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on
Defaults!JOULEWISE_NETWORK_TIME !requiretty
edr ALL=(root) NOPASSWD: JOULEWISE_NETWORK_TIME
```

### A13 — `scripts/quiet_window_clock.sh` lines 1,30 (git show 9b6b3f0e:scripts/quiet_window_clock.sh | sed -n '1,30p')

```
#!/bin/bash
# Quiet-window clock stabilization (operator tool; requires administrator rights).
#
# WHY THIS EXISTS
#   On 2026-07-26 two window-C collection attempts failed because the machine's
#   wall clock was being slewed against the monotonic clock by more than the
#   governed 5 ms anchor ceiling (5.544 ms at ~+110 ppm, then 7.769 ms at
#   ~-158 ppm). Those rates match adjtime(2), which macOS network time
#   synchronisation uses to speed up or slow down the clock by a fraction of a
#   percent. Every environment gate passed on both failing members, so nothing
#   else caught it. Disabling automatic network time for the duration of a
#   measurement window removes the adjuster.
#
#   This is OPERATIONAL STABILIZATION, NOT A PROTOCOL WAIVER. The 5 ms anchor
#   predicate remains authoritative and is never relaxed. Nothing here touches
#   admission gates, --max-failures, or any measurement code.
#
# USAGE
#   scripts/quiet_window_clock.sh status    # show clock state and current offset
#   scripts/quiet_window_clock.sh disable   # BEFORE a window: verify, then pin
#   scripts/quiet_window_clock.sh enable    # AFTER the window: restore and resync
#
# SAFETY
#   `disable` REFUSES to pin the clock if it is currently off by more than
#   MAX_OFFSET_S. Pinning a wrong clock is worse than leaving sync on: the
#   window would carry a fixed timestamp error instead of a transient one.

set -uo pipefail

MAX_OFFSET_S="${MAX_OFFSET_S:-0.5}"   # refuse to pin if |offset| exceeds this
```

### A14 — `scripts/quiet_window_clock.sh` lines 95,105 (git show 9b6b3f0e:scripts/quiet_window_clock.sh | sed -n '95,105p')

```
  bold ""
  bold "Step 2/3 — disabling automatic network time"
  sudo systemsetup -setusingnetworktime off >/dev/null 2>&1
  local state
  state="$(sync_state)"
  if [ "$state" = "On" ]; then
    fail "FAILED: network time is still On. Do not start the window."
    exit 1
  fi
  echo "  network time synchronisation: ${state:-Off}"

```

### A15 — `scripts/quiet_window_clock.sh` lines 160,172 (git show 9b6b3f0e:scripts/quiet_window_clock.sh | sed -n '160,172p')

```
}

do_enable() {
  bold "Re-enabling automatic network time"
  sudo systemsetup -setusingnetworktime on >/dev/null 2>&1
  sleep 2
  local state
  state="$(sync_state)"
  echo "  network time synchronisation: ${state:-UNKNOWN}"
  if [ "$state" != "On" ]; then
    fail "WARNING: expected On. Check System Settings > General > Date & Time."
    exit 1
  fi
```

### A16 — `tests/test_uncertainty_evidence.py` lines 368,373 (git show 9b6b3f0e:tests/test_uncertainty_evidence.py | sed -n '368,373p')

```
    def test_wall_minus_monotonic_step_fails_closed(self) -> None:
        stamps = self.stamps()
        stamps["post_parse"] = ClockStamp(1003.4 + 0.010, 1003.4, 1003.4, 0.0, 0.0)
        result = self.derive(stamps=stamps)
        self.assert_unresolved(result, "wall_minus_monotonic_span_exceeded")
        self.assertGreater(result["wall_minus_monotonic_span_s"], 0.005)
```

### A17 — `tests/test_uncertainty_evidence.py` lines 675,681 (git show 9b6b3f0e:tests/test_uncertainty_evidence.py | sed -n '675,681p')

```
    def test_wall_minus_monotonic_span_rule_still_refuses_under_v3(self) -> None:
        stamps = self.stamps()
        post = stamps["post_parse"]
        stamps["post_parse"] = replace(post, epoch_s=post.epoch_s + 0.006)
        result = self.derive(stamps=stamps)
        self.assert_unresolved(result, "wall_minus_monotonic_span_exceeded")
        self.assertGreater(result["wall_minus_monotonic_span_s"], 0.005)
```

### A18 — `tests/test_uncertainty_evidence.py` lines 486,540 (git show 9b6b3f0e:tests/test_uncertainty_evidence.py | sed -n '486,540p')

```

    def records(
        self,
        *,
        count: int = 61,
        first_elapsed_ns: int = 999_000_000,
        later_elapsed_ns: int = 1_000_000_000,
        rate: Fraction = Fraction(1),
    ):
        result = []
        q_ns = 0
        for index in range(count):
            elapsed_ns = first_elapsed_ns if index == 0 else later_elapsed_ns
            if index > 0:
                q_ns += elapsed_ns
            endpoint_ns = Fraction(self.A_NS) + rate * q_ns
            native_ns = (
                endpoint_ns.numerator
                // endpoint_ns.denominator
                // 1_000_000_000
                * 1_000_000_000
            )
            result.append(self.record(elapsed_ns, native_ns))
        return result

    @staticmethod
    def stamps(
        *,
        rate: Fraction = Fraction(1),
        first_delta: Fraction = Fraction(1) + Fraction(1, 1024),
        base_epoch: Fraction = Fraction(1000),
        resolution: float = 0.0,
    ) -> dict[str, ClockStamp]:
        def make(monotonic: Fraction) -> ClockStamp:
            epoch = base_epoch + rate * (monotonic - 100)
            return ClockStamp(
                float(epoch),
                float(monotonic),
                float(monotonic),
                resolution,
                resolution,
            )

        first = Fraction(100) + first_delta
        return {
            "pre_spawn": make(Fraction(100)),
            "first_parse": make(first),
            "sampling_started": make(max(first, Fraction(102))),
            "sampling_stopped": make(Fraction(160)),
            "post_parse": make(Fraction(161)),
        }

    def derive(self, *, stamps=None, records=None):
        from joulewise.uncertainty_evidence import derive_powermetrics_anchor_v3

```

### A19 — `scripts/night_chains/quiet_predicate_evidence.zsh` lines 1,16 (git show 9b6b3f0e:scripts/night_chains/quiet_predicate_evidence.zsh | sed -n '1,16p')

```
#!/bin/zsh
# QPE-01 idle-only pilot. The sealed protocol owns every timing parameter.
set -euo pipefail
cd "${0:A:h:h:h}"
export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence
: "${PY:?required}"
: "${EVIDENCE_PLAN_PATH:?required}"
: "${EVIDENCE_MANIFEST_SHA256:?required}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD"
if [[ "${NIGHT_VERIFY_ONLY:-0}" == 1 ]]; then
    exec "$PY" -B -m joulewise.quiet_predicate_campaign verify
fi
# The executor supervises collector, recorder and sampler process groups and
# journals their identities and bounded cleanup before returning an exit code.
exec "$PY" -B -m joulewise.quiet_predicate_campaign run
```

### A20 — `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json` lines 1,200 (git show 9b6b3f0e:configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json | sed -n '1,200p')

```
{
  "block_two": {
    "authored_after_pilot": true,
    "contrast": "idle-load-idle bracket",
    "levels": [
      0,
      0.05
    ],
    "one_profile": true,
    "one_qos": true,
    "smallest_holdable_share": 0.05,
    "upper_bound": "one-sided 95% paired-contrast upper bound"
  },
  "busy_cores_role": "covariate_only",
  "cadence_exclusion": "start_drift: absolute collector start drift greater than 10 s from the frozen schedule",
  "chain_source_sha256": "568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea",
  "envelope_s": 600,
  "envelopes": 12,
  "exclusions": [
    "census_not_clean_or_unknown",
    "ac_not_AC_Power_or_probe_error",
    "CPU_Speed_Limit_below_100_or_thermal_probe_error",
    "clock_anchor_unresolved",
    "incomplete_interior_support",
    "collect_error",
    "cleanup_unproven",
    "start_drift"
  ],
  "interior_offset_s": 60,
  "interior_s": 480,
  "load_generator": false,
  "minimum_adjacent_pairs": 4,
  "minimum_retained": 8,
  "pairing_rule": "disjoint_original_adjacent_pairs_both_retained_no_bridging",
  "power_interval_ms": 100,
  "receipt_class": "DIAGNOSTIC_NO_PACK",
  "recorder_journal": "evidence_busy_cores.jsonl",
  "ruling": "cold gate 10 Q1/Q2 (2026-09-19); adjudication 10a; sizing ruling 46b",
  "sample_interval_s": 30,
  "schema": "joulewise.quiet_predicate_pilot.v1",
  "settle_s": 600,
  "sizing": {
    "assumption": "independent normally distributed disjoint pair differences",
    "chi_square_lower_tail_probability": 0.1,
    "confidence": 0.9,
    "delta_j": 1,
    "formula": "max(3, ceil(8 * s_upper**2 / delta_j**2))",
    "maximum_pairs": 24,
    "minimum_pairs": 3,
    "multiplier": 8,
    "reference_factors": {
      "n_4": 2.266,
      "n_6": 1.762
    },
    "s_pair": "sample SD of retained disjoint differences, df = n - 1",
    "s_upper": "s_pair * sqrt((n - 1) / chi_square_quantile(0.10, n - 1))"
  },
  "start_drift_max_s": 10,
  "stop_branches": {
    "block_two_upper_bound_above_1_J": "no cutoff qualifies",
    "observer_floor_above_smallest_holdable_share": "no cutoff qualifies",
    "sized_pairs_above_24": "no cutoff qualifies"
  },
  "summary": [
    "interior rail-sum and combined joules",
    "retained disjoint pairs (e1,e2), (e3,e4), ..., (e11,e12); even minus odd interior joules; sample SD and upper 90% bound",
    "overlapping adjacent differences and SD, maximum absolute difference: diagnostics only, never sizing",
    "all single-envelope values and SD, first-to-last retained drift: diagnostics only, never sizing",
    "name every overlapping original adjacent pair with absolute difference above 3 * s_pair; diagnostic only; never exclude by magnitude",
    "whole-round observer cpu-s, self plus reaped children including recorder; never subtracted",
    "recorder journal joined by monotonic support: per-envelope busy-core median/max and clean-machine distribution; covariates only",
    "cadence and native sample counts",
    "boot_id, os_build, sw_vers, powermetrics identity",
    "all named exclusions; partial observations retained; PROVISIONAL, no cutoff authority"
  ],
  "top_up": false,
  "window_max_s": 9000
}
```

### A21 — `joulewise/quiet_predicate_campaign.py` lines 449,530 (git show 9b6b3f0e:joulewise/quiet_predicate_campaign.py | sed -n '449,530p')

```
def execute(plan, protocol, night_dir):
    """No schedule knobs: all quantities come from the authenticated protocol."""
    from scripts import sample_quiet_predicate_evidence as harness
    night_dir.mkdir(parents=True, exist_ok=True)
    directory = night_dir / "evidence"
    directory.mkdir()  # no overwrite/retry
    journal = night_dir / "evidence_processes.jsonl"
    journal.touch(exist_ok=False)
    env = {**os.environ, "EVIDENCE_PROCESS_JOURNAL": str(journal)}
    children, envelopes = [], []
    consecutive_cleanup_failures = 0
    outcome, error = "refused", None
    cpu_start = harness.cpu_total()
    go = time.monotonic()
    def interrupted(signum, _frame):
        raise InterruptedError(f"evidence chain signal {signum}")
    old = {s: signal.signal(s, interrupted) for s in (signal.SIGTERM, signal.SIGINT)}
    def launch(kind, argv):
        process = subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL, start_new_session=True)
        children.append(process)
        append_event(journal, {"kind": kind, "pgid": process.pid, "epoch_s": time.time()})
        return process
    try:
        # Settle belongs inside GO; verify-only never reaches this call.
        print(f"evidence_settle seconds={protocol['settle_s']}", flush=True)
        time.sleep(protocol["settle_s"])
        first = go + protocol["settle_s"]
        recorder = launch("recorder", [sys.executable, "-B", "-m", "joulewise.quiet_predicate_campaign", "record"])
        for index in range(1, protocol["envelopes"] + 1):
            scheduled = first + (index - 1) * protocol["envelope_s"]
            time.sleep(max(0, scheduled - time.monotonic()))
            if time.time() + protocol["envelope_s"] > plan.t0_epoch_s + plan.window_max_s:
                raise ValueError("evidence window exhausted; no compressed envelope or top-up")
            actual = time.monotonic()
            out = directory / f"envelope-{index:02d}"
            collector = launch("collector", [sys.executable, "-B", str(Path(plan.measurement_root) / HARNESS_PATHS[0]),
                "collect", "--state", "idle", "--repeat", str(index), "--duration-s", str(protocol["envelope_s"]),
                "--sample-interval-s", str(protocol["sample_interval_s"]), "--interior-offset-s", str(protocol["interior_offset_s"]),
                "--interior-s", str(protocol["interior_s"]), "--envelope-start-mono-s", str(scheduled), "--power-interval-ms", str(protocol["power_interval_ms"]), "--out", str(out)])
            print(f"envelope_start index={index} collector_pgid={collector.pid} recorder_pgid={recorder.pid}", flush=True)
            try:
                code = collector.wait(timeout=protocol["envelope_s"] + 30)
            except subprocess.TimeoutExpired:
                code = 124
            # The covariate recorder spans all envelopes. Each collector and
            # its independent sampler/power groups must be reaped between slots.
            cleanup = cleanup_groups(journal, children, budget_s=30, exclude={recorder.pid})
            envelopes.append({"index": index, "scheduled_mono_s": scheduled, "actual_mono_s": actual,
                              "start_drift_s": actual - scheduled, "collector_exit": code, "cleanup": cleanup})
            append_event(night_dir / "evidence_envelopes.jsonl", envelopes[-1])
            print(f"envelope_end index={index} rc={code} cleanup_proven={cleanup['cleanup_proven']}", flush=True)
            consecutive_cleanup_failures = 0 if cleanup["cleanup_proven"] else consecutive_cleanup_failures + 1
            if consecutive_cleanup_failures >= 2:
                raise ValueError("two consecutive cleanup_unproven envelopes")
            if recorder.poll() is not None:
                raise ValueError("evidence covariate recorder exited early")
        outcome = "partial" if any(e["collector_exit"] != 0 or not e["cleanup"]["cleanup_proven"] for e in envelopes) else "complete"
    except (OSError, ValueError, KeyboardInterrupt, subprocess.SubprocessError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        for signum in old:
            signal.signal(signum, signal.SIG_IGN)
        cleanup = cleanup_record(night_dir, children)
        try:
            pilot_summary(directory, protocol, envelopes,
                          harness.cpu_total() - cpu_start if cleanup["cleanup_proven"] else None)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            outcome, error = "refused", "pilot summary failed: " + str(exc)
        if not cleanup["cleanup_proven"]:
            outcome, error = "refused", error or "final evidence cleanup unproven"
        if outcome == "refused":
            write_refusal(night_dir, plan, error or "evidence execution aborted")
        harness.write_json(night_dir / "evidence_outcome.json", {"outcome": outcome, "error": error,
            "envelopes_attempted": len(envelopes), "cleanup_proven": cleanup["cleanup_proven"]})
        for signum, handler in old.items():
            signal.signal(signum, handler)
    print(f"evidence_end outcome={outcome} cleanup_proven={cleanup['cleanup_proven']}", flush=True)
    return 0 if outcome in {"complete", "partial"} and cleanup["cleanup_proven"] else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
```

### A22 — `joulewise/quiet_predicate_campaign.py` lines 94,109 and 211,217 (verify_environment, write_refusal)

```
def verify_environment():
    plan_path = Path(os.environ["EVIDENCE_PLAN_PATH"])
    plan = night_gate.NightPlan.from_mapping(json.loads(plan_path.read_text()))
    if (os.environ.get("NIGHT_PLAN_ID") != plan.plan_id or
            os.environ.get("MEASUREMENT_ROOT") != plan.measurement_root or
            os.environ.get("MEASUREMENT_HEAD") != plan.measurement_head):
        raise ValueError("evidence wrapper environment differs from plan")
    _, manifest, sha = verify_manifest(plan, Path(plan.chain_path).read_text())
    if os.environ.get("EVIDENCE_MANIFEST_SHA256") != sha:
        raise ValueError("evidence manifest environment mismatch")
    # Import checks are read-only; no power, sampler, load or hard probes run.
    from scripts import sample_quiet_predicate_evidence  # noqa: F401
    from joulewise import quiet_admission  # noqa: F401
    return plan, manifest, sha


def write_refusal(night_dir, plan, detail):
    from scripts.run_night import _write_driver_refusal
    night_dir.mkdir(parents=True, exist_ok=True)
    return _write_driver_refusal(night_dir / "refusal.json", plan, "night_probe_error",
                                 "evidence chain refused: " + detail)


```

### A23 — `joulewise/quiet_predicate_campaign.py` lines 41,75 (git show 9b6b3f0e:joulewise/quiet_predicate_campaign.py | sed -n '41,75p')

```
def frozen_protocol(raw=None):
    """The byte-pinned registration is the single source of protocol values."""
    if raw is None:
        raw = (Path(__file__).resolve().parents[1] / PROTOCOL_PATH).read_bytes()
    if digest(raw) != night_gate.QPE01_PILOT_REGISTRATION_SHA256:
        raise ValueError("protocol is not the ruled pilot registration")
    return json.loads(raw)


def validate_protocol(protocol, source_digest):
    if protocol != frozen_protocol() or protocol.get("chain_source_sha256") != source_digest:
        raise ValueError("frozen pilot protocol mismatch; CLI overrides are forbidden")
    return protocol


def manifest_for(plan):
    contents = {name: tracked_bytes(plan.measurement_root, plan.measurement_head, name)
                for name in MANIFEST_PATHS}
    files = {name: digest(raw) for name, raw in contents.items()}
    protocol = frozen_protocol(contents[PROTOCOL_PATH])
    validate_protocol(protocol, files[CHAIN_PATH])
    registration = Path(plan.registration_path)
    if not registration.is_absolute():
        registration = Path(plan.measurement_root) / registration
    if registration.resolve() != (Path(plan.measurement_root) / PROTOCOL_PATH).resolve():
        raise ValueError("evidence registration must be the tracked pilot protocol")
    if plan.receipt_class != "DIAGNOSTIC_NO_PACK" or plan.quiet_admission is not None:
        raise ValueError("evidence pilot requires v2 DIAGNOSTIC_NO_PACK")
    if plan.window_max_s != protocol["window_max_s"]:
        raise ValueError("window_max_s must equal the frozen protocol's 9000 s")
    return {"schema": MANIFEST_SCHEMA, "plan_id": plan.plan_id,
            "measurement_head": plan.measurement_head, "files": files}


def verify_manifest(plan, chain_text):
```


### A24 — `joulewise/t0_rehearsal.py` lines 1020,1035 (git show 9b6b3f0e:joulewise/t0_rehearsal.py | sed -n '1020,1035p')

```
        "anchor_monotonic_raw_ns": r0_raw,
        "anchor_read_skew_ns": inputs["r0_anchor_read_skew_ns"],
        "batch_finished_monotonic_raw_ns": inputs[
            "r0_batch_finished_monotonic_raw_ns"
        ],
    }
    disable = {
        "exit_code": 0,
        "argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off"],
        "started_monotonic_ns": inputs["clock_disable_started_monotonic_ns"],
        "finished_monotonic_ns": inputs["clock_disable_finished_monotonic_ns"],
    }
    context = SimpleNamespace(
        captures={
            "clock-reference": (
                {
```

### A25 — `scripts/sample_quiet_predicate_evidence.py` lines 183,236 (git show 9b6b3f0e:scripts/sample_quiet_predicate_evidence.py | sed -n '183,236p')

```
def parse_frames(data):
    """NUL-separated native plists; preserve the adapter's truncated-tail diagnostic."""
    documents, dropped = pm._powermetrics_documents(data)
    frames = []
    for doc in documents:
        elapsed = doc.get("elapsed_ns")
        native = doc.get("timestamp")
        if type(elapsed) is not int or elapsed <= 0 or not isinstance(native, datetime):
            raise ValueError("frame requires positive elapsed_ns and native datetime timestamp")
        if native.tzinfo is None:
            native = native.replace(tzinfo=timezone.utc)
        native_ns = pm._timestamp_epoch_ns_utc(native)
        processor = doc.get("processor", {})
        power = {}
        for rail in RAILS:
            if rail == "rail_sum_w":
                continue
            mw = number(processor.get(rail[:-2] + "_power"))
            power[rail] = mw / 1000 if mw is not None and mw >= 0 else None
        core_rails = [power[r] for r in RAILS[:3]]
        power["rail_sum_w"] = sum(core_rails) if all(v is not None for v in core_rails) else None
        energies = [number(processor.get(r + "_energy")) for r in ("cpu", "gpu", "ane")]
        energy = sum(energies) / 1000 if all(v is not None for v in energies) else None
        clusters = processor.get("clusters", [])
        frames.append({"native_timestamp_s": native.timestamp(), "native_timestamp_ns": native_ns,
                       "elapsed_ns": elapsed, "elapsed_s": elapsed / 1e9,
                       "is_delta": doc.get("is_delta"), "energy_j": energy,
                       "power": reasons(power, "rail absent or invalid in native frame"),
                       "clusters": [residency(c) for c in clusters],
                       "cpus": [residency(c, cpu=True) for group in clusters
                                for c in group.get("cpus", [])]})
    return frames, asdict(dropped) if dropped else None


def align_frames(frames, stamps, deriver=derive_powermetrics_anchor_v3):
    records = [NativeAnchorRecord(
        elapsed_s=f["elapsed_s"], native_timestamp_s=f["native_timestamp_s"],
        power_w=f["power"]["rail_sum_w"] if f["power"]["rail_sum_w"] is not None else math.nan,
        energy_j=f["energy_j"], is_delta=f["is_delta"],
        elapsed_ns=f["elapsed_ns"], native_timestamp_ns=f["native_timestamp_ns"])
        for f in frames]
    anchor = deriver(stamps=stamps, records=records)
    if anchor["status"] != "bounded":
        return [], anchor
    endpoint = anchor["first_sample_end_point_epoch_s"]
    aligned, elapsed_ns = [], 0
    for i, frame in enumerate(frames):
        if i:
            elapsed_ns += frame["elapsed_ns"]
        end = endpoint + elapsed_ns / 1e9
        aligned.append({**frame, "start_s": end - frame["elapsed_s"], "end_s": end})
    return aligned, anchor


```

### A26 — `scripts/capture_t0_step.py` lines 470,500 (git show 9b6b3f0e:scripts/capture_t0_step.py | sed -n '470,500p')

```


def _command_for_step(context: CaptureContext, step_id: str) -> tuple[str, ...]:
    values = context.assignments
    python = str(context.repository / ".venv/bin/python")
    if step_id == "clock-reference":
        return (
            python,
            str(context.repository / "scripts/collect_clock_reference.py"),
        )
    if step_id == "clock-disable":
        return (
            "/usr/bin/sudo",
            "-n",
            "/usr/sbin/systemsetup",
            "-setusingnetworktime",
            "off",
        )
    if step_id == "quiet-mac-prep":
        return ("/bin/bash", str(context.repository / "scripts/quiet_mac_prep.sh"))
    if step_id == "prewindow-check":
        return context.prewindow_command
    if step_id == "ledger-readiness":
        return (
            python,
            str(context.repository / "scripts/recover_calibration_ledger.py"),
            "readiness",
            "--phase",
            "pre-reserve",
            "--session-id",
            values["BRACKET_SESSION_ID"],
```
