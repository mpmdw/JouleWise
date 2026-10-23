"""Synthetic v3 primary pulse bytes; copied from the reducer fixture generator.

Signal lag is a hardware-producer parameter. Physics and authentication execute
through unmodified production functions. No measured capture is read.
"""
import json, math, plistlib, hashlib, os
from datetime import datetime, timezone
from dataclasses import asdict
from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD
_SELF_CONSISTENT_CALIBRATIONS = {}

def self_consistent_calibration(
    *,
    first_endpoint_s: float | None = None,
    commanded_edges: list[tuple[float, float]] | None = None,
    protocol_id: str | None = None,
    anchor_method: str = ACTIVE_CAPTURE_ANCHOR_METHOD,
    signal_lag_s: float = .021331,
    os_build: str = "25G83",
) -> tuple[dict, bytes, bytes]:
    """Build a physically consistent protocol calibration for reducer tests."""

    from joulewise.uncertainty_evidence import (
        resolve_anchor_deriver,
    )
    from joulewise.adapters.powermetrics import (
        anchor_records_from_powermetrics,
        parse_powermetrics_records,
    )
    from joulewise.clock import ClockStamp
    from joulewise.powermetrics_fiducial import (
        LEGACY_PULSE_COUNT,
        PROTOCOL_ID,
        PROTOCOL_V2_ID,
        PROTOCOL_V2_SHA256,
        PROTOCOL_V3_SHA256,
        RESIDUAL_REGION_METHOD,
        CommandedPulse,
        instrument_evidence,
        LEGACY_PROTOCOL_ID,
        protocol_pulse_count,
        pulse_schedule,
        rederive_detection_from_artifacts,
    )
    # Keep the synthetic calibration on the same epoch scale as the retained
    # D-078 measuring bundle.  Freshness now covers the measured-window end,
    # so a calibration living near epoch 1000 would be correctly stale for a
    # 2026 bundle even though its relative pulse geometry is self-consistent.
    protocol_id = protocol_id or LEGACY_PROTOCOL_ID
    if first_endpoint_s is None:
        first_endpoint_s = 1_784_490_850.05
    nanoseconds_per_second = 1_000_000_000
    cadence_ns = 100_000_000
    cadence_s = cadence_ns / nanoseconds_per_second
    warmup_edges = [
        (first_endpoint_s + 1.95, first_endpoint_s + 2.95),
        (first_endpoint_s + 4.45, first_endpoint_s + 5.45),
        (first_endpoint_s + 6.95, first_endpoint_s + 7.95),
    ]
    if commanded_edges is None:
        commanded_edges = pulse_schedule(
            protocol_pulse_count(protocol_id),
            start_s=first_endpoint_s + 14.95,
        )
    cache_key = (
        first_endpoint_s,
        tuple(commanded_edges),
        protocol_id,
        anchor_method,
        signal_lag_s,
        os_build,
        os.environ.get('S10_SPARSE_CALIBRATION')=='1',
    )
    if cache_key in _SELF_CONSISTENT_CALIBRATIONS:
        evidence, raw, events = _SELF_CONSISTENT_CALIBRATIONS[cache_key]
        return json.loads(json.dumps(evidence)), raw, events
    true_edges = [(on_s + signal_lag_s, off_s + signal_lag_s) for on_s, off_s in commanded_edges]
    capture_end_s = true_edges[-1][1] + 5.0

    documents: list[dict] = []
    first_endpoint_ns = round(first_endpoint_s * nanoseconds_per_second)
    # Keep the established synthetic waveform byte-for-byte stable for its
    # many reducer callers. Its float phase affects only overlap/power values;
    # record endpoints and native-second labels come exclusively from the
    # integer grid below, so it cannot corrupt clock-anchor consistency.
    signal_endpoint_s = first_endpoint_s
    record_index = 0
    while signal_endpoint_s <= capture_end_s + 1e-12:
        endpoint_ns = first_endpoint_ns + record_index * cadence_ns
        endpoint_s = endpoint_ns / nanoseconds_per_second
        whole_second_s = endpoint_ns // nanoseconds_per_second
        if math.floor(endpoint_s) != whole_second_s:
            raise AssertionError("integer endpoint lost its whole-second label")
        start_s = signal_endpoint_s - cadence_s
        overlap = math.fsum(
            max(
                0.0,
                min(signal_endpoint_s, off_s) - max(start_s, on_s),
            )
            / cadence_s
            for on_s, off_s in (*warmup_edges, *true_edges)
        )
        gpu_w = 2.0 + 20.0 * overlap
        documents.append(
            {
                "timestamp": datetime.fromtimestamp(
                    whole_second_s, tz=timezone.utc
                ),
                "elapsed_ns": cadence_ns,
                "is_delta": True,
                "hw_model": "Mac15,9",
                "kern_osversion": os_build,
                "processor": {
                    "cpu_power": 0.0,
                    "gpu_power": gpu_w * 1000.0,
                    "ane_power": 0.0,
                    "cpu_energy": 0,
                    "gpu_energy": round(gpu_w * cadence_s * 1000.0),
                    "ane_energy": 0,
                },
            }
        )
        record_index += 1
        signal_endpoint_s += cadence_s
    if os.environ.get('S10_SPARSE_CALIBRATION')=='1':
        # Synthetic hardware supplies longer constant-power intervals while
        # retaining each fractional pulse edge and an interior plateau row.
        # Protocol edges/count, total time, power and every pulse stay real.
        sparse=[];pending=None;span=0
        def emit(document,elapsed):
            document['elapsed_ns']=elapsed
            document['processor']['gpu_energy']=round(document['processor']['gpu_power']*elapsed/1e9)
            sparse.append(document)
        for index,document in enumerate(documents):
            power=document['processor']['gpu_power']
            if abs(power-2000.)<.1:power=2000.
            elif abs(power-22000.)<.1:power=22000.
            document['processor']['gpu_power']=power
            if pending is not None and pending['processor']['gpu_power']!=power and span:
                emit(pending,span);span=0
            span+=document['elapsed_ns'];pending=document
            limit=1000000000 if power==2000. else 200000000
            if index<10 or index==len(documents)-1 or span>=limit or power not in (2000.,22000.):
                emit(document,span);span=0
        documents=sparse
    raw = b"\0".join(plistlib.dumps(document) for document in documents)

    def stamp(epoch_s: float) -> ClockStamp:
        mono = epoch_s - 1791600000.0 + 100.0
        return ClockStamp(
            epoch_s=epoch_s,
            monotonic_before_s=mono - 1e-6,
            monotonic_after_s=mono + 1e-6,
            wall_resolution_s=1e-6,
            monotonic_resolution_s=1e-6,
        )

    anchor_stamps = {
        # Tight but non-zero causal bracket around the true 1000.05 endpoint;
        # this keeps the synthetic production calibration representative of a
        # usable live bound rather than a deliberately wide 50 ms half-width.
        "pre_spawn": stamp(first_endpoint_s - 0.101),
        "first_parse": stamp(first_endpoint_s + 0.001),
        "sampling_started": stamp(first_endpoint_s + 0.15),
        "sampling_stopped": stamp(capture_end_s + 0.5),
        "post_parse": stamp(capture_end_s + 1.0),
    }
    native = parse_powermetrics_records(raw)
    clock_anchor = resolve_anchor_deriver(anchor_method)(
        stamps=anchor_stamps,
        records=anchor_records_from_powermetrics(native),
    )
    if clock_anchor.get("status") != "bounded":
        raise AssertionError(clock_anchor)
    if clock_anchor.get("method") != anchor_method:
        raise AssertionError(clock_anchor)

    event_rows: list[dict] = []

    def add_pair(kind: str, on_s: float, off_s: float, index: int) -> None:
        for edge, epoch_s in (("on", on_s), ("off", off_s)):
            event_rows.append(
                {
                    "timestamp_s": epoch_s,
                    "event_type": f"{kind}_command_{edge}",
                    "phase": "instrument_validation",
                    "message": f"{kind}_command_{edge}",
                    "metadata": {
                        "clock_stamp": asdict(stamp(epoch_s)),
                        f"{kind}_index": index,
                    },
                }
            )

    for index, (on_s, off_s) in enumerate(warmup_edges):
        add_pair("warmup", on_s, off_s, index)
    for index, (on_s, off_s) in enumerate(commanded_edges):
        add_pair("pulse", on_s, off_s, index)
    events = "".join(
        json.dumps(row, sort_keys=True) + "\n" for row in event_rows
    ).encode("utf-8")
    detection = rederive_detection_from_artifacts(
        raw, events, clock_anchor, protocol_id=protocol_id
    )
    bindings = {
        "hardware_model": "Mac15,9",
        "os_build": os_build,
        "powermetrics_sha256": "ab" * 32,
        "sampling_interval_ms": 100,
        "anchor_method_version": anchor_method,
        "mlx_version": "0.31.2",
        "pulse_protocol_id": protocol_id,
        "power_policy": "ac_high_power",
    }
    if protocol_id in {PROTOCOL_V2_ID, PROTOCOL_ID}:
        bindings.update(
            {
                "estimator_revision": RESIDUAL_REGION_METHOD,
                "protocol_sha256": (
                    PROTOCOL_V2_SHA256
                    if protocol_id == PROTOCOL_V2_ID
                    else PROTOCOL_V3_SHA256
                ),
            }
        )
    evidence = instrument_evidence(
        detection,
        bindings=bindings,
        validation_id="synthetic-self-consistent-v1",
        artifact_sha256={
            "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
            "events.jsonl": hashlib.sha256(events).hexdigest(),
        },
        protocol_id=protocol_id,
        protocol_pulse_count=protocol_pulse_count(protocol_id),
        capture_wall_time_s=(
            min(float(row["timestamp_s"]) for row in event_rows)
            if protocol_id in {PROTOCOL_V2_ID, PROTOCOL_ID}
            else None
        ),
    )
    evidence["clock_anchor"] = clock_anchor
    evidence["clock_anchor_resolved"] = True
    if evidence["status"] != "valid":
        raise AssertionError(evidence["reasons"])
    _SELF_CONSISTENT_CALIBRATIONS[cache_key] = (evidence, raw, events)
    return json.loads(json.dumps(evidence)), raw, events
