#!/usr/bin/env python3
"""Lead-owned [QUIET-MAC] pulse-fiducial calibration run (D-078).

The current claim-bearing protocol is frozen in
configs/calibration/powermetrics_fiducial/protocol_v3.json and documented in
docs/contracts/powermetrics_fiducial.md. Historical protocol files remain
byte-frozen validation identities.

- preallocated 4096x4096 FP16 MLX matmuls, mx.eval GPU fencing;
- 3 warmup pulses, then k=59 pulses of 1.0 s each;
- deterministic low-discrepancy spacing 1.5 + vanDerCorput_2(j) s
  (avoids 10 Hz phase lock);
- >= 5 s baseline before and after the pulse train;
- events pulse_command_on/off carry full paired ClockStamps;
- primary rail gpu_power; CPU+GPU combined is corroboration only;
- gates: plateau >= 10 W over baseline, robust SNR >= 10, all pulses
  detected, no spurious plateaus - otherwise the artifact is invalid.

NEVER run this while another agent session is active on the machine
([QUIET-MAC] discipline); the run is refused without --allow-live.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.adapters.powermetrics import (  # noqa: E402
    POWER_METRICS,
    SAMPLERS,
    anchor_records_from_powermetrics,
    parse_powermetrics_records,
    samples_from_records,
)
from joulewise.clock import SystemClock  # noqa: E402
from joulewise.powermetrics_fiducial import (  # noqa: E402
    BASELINE_S,
    LEGACY_PROTOCOL_ID,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    PROTOCOL_V2_PULSE_COUNT,
    RESIDUAL_REGION_METHOD,
    PULSE_COUNT,
    PULSE_DURATION_S,
    SAMPLING_INTERVAL_MS,
    CommandedPulse,
    TraceInterval,
    WARMUP_PULSE_COUNT,
    allocate_matmul_buffers,
    capture_wall_time_from_events,
    clock_stamp_half_width_s,
    detect_pulses,
    instrument_evidence,
    protocol_definition_matches,
    pulse_schedule,
    run_matmul_pulse,
    trim_trace_after_pulses,
    rederive_detection_from_artifacts,
)
from joulewise.uncertainty_evidence import (  # noqa: E402
    derive_powermetrics_clock_evidence_v2,
)

PROTOCOL_PATH = (
    REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v3.json"
)
PROTOCOL_V2_PATH = (
    REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v2.json"
)
ROLLOVER_GATE_TIMEOUT_REASON = "pulse_calibration_rollover_gate_timeout"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_protocol(path: Path = PROTOCOL_PATH) -> bool:
    """Load and field-bind the frozen JSON to executable module constants."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return protocol_definition_matches(payload)


def _terminate_powermetrics(process: subprocess.Popen) -> None:
    """Best-effort bounded termination for a calibration sampler."""

    process.terminate()
    try:
        process.communicate(timeout=10.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()


def wait_for_preworkload_rollover(
    capture_path: Path,
    process: subprocess.Popen,
    *,
    timeout_s: float = 15.0,
    poll_s: float = 0.05,
) -> None:
    """Require an advancing native plist timestamp before any workload.

    Timeout is a governed refusal, not permission to fall through. The
    sampler is terminated here so callers cannot accidentally continue with
    baseline, warmup, or pulse work after the gate fails.
    """

    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            records = parse_powermetrics_records(capture_path.read_bytes())
        except (OSError, ValueError):
            records = []
        stamps = [
            float(record.metadata["plist_timestamp_s"])
            for record in records
        ]
        if any(later > earlier for earlier, later in zip(stamps, stamps[1:])):
            return
        time.sleep(poll_s)
    _terminate_powermetrics(process)
    raise RuntimeError(ROLLOVER_GATE_TIMEOUT_REASON)


def trim_trace_after_warmups(
    intervals: list[TraceInterval], warmups: list[CommandedPulse]
) -> list[TraceInterval]:
    """Remove captured warmup plateaus before measured-pulse detection.

    Warmups are deliberately inside the raw capture but are not protocol
    pulses.  Leaving them in the detector's ``outside`` baseline launders no
    evidence: they are classified as spurious plateaus and make every clean
    live validation invalid.  Trim only through the final commanded warmup
    edge; the second BASELINE_S pause remains available to fit the first
    measured edge, and any genuinely uncommanded plateau after that edge is
    still detected.
    """

    return trim_trace_after_pulses(intervals, warmups)


def rederive_artifact(source_dir: Path, output: Path) -> dict[str, object]:
    """Re-emit v2 validation evidence from compatible 40-pulse primary bytes."""

    source_dir = Path(source_dir)
    manifest_path = source_dir / "manifest.json"
    evidence_path = source_dir / "instrument_evidence.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        stored = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("source calibration metadata is unreadable") from exc
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if not isinstance(artifacts, dict) or not isinstance(stored, dict):
        raise ValueError("source calibration metadata is malformed")
    if (
        stored.get("protocol_id") not in {LEGACY_PROTOCOL_ID, PROTOCOL_V2_ID}
        or stored.get("pulse_count") != PROTOCOL_V2_PULSE_COUNT
    ):
        raise ValueError("re-derivation requires compatible 40-pulse v1/v2 evidence")
    raw_by_name: dict[str, bytes] = {}
    for relative in (
        "raw/powermetrics.plist",
        "events.jsonl",
        "instrument_evidence.json",
    ):
        expected = artifacts.get(relative)
        candidate = source_dir / relative
        try:
            raw = candidate.read_bytes()
        except OSError as exc:
            raise ValueError(f"source artifact missing: {relative}") from exc
        if (
            not isinstance(expected, str)
            or hashlib.sha256(raw).hexdigest() != expected
        ):
            raise ValueError(f"source artifact hash mismatch: {relative}")
        raw_by_name[relative] = raw
    stored_hashes = stored.get("artifact_sha256")
    if not isinstance(stored_hashes, dict):
        raise ValueError("source evidence omits primary artifact hashes")
    for relative in ("raw/powermetrics.plist", "events.jsonl"):
        if hashlib.sha256(raw_by_name[relative]).hexdigest() != stored_hashes.get(
            relative
        ):
            raise ValueError(f"source evidence hash mismatch: {relative}")
    fresh = rederive_detection_from_artifacts(
        raw_by_name["raw/powermetrics.plist"],
        raw_by_name["events.jsonl"],
        stored.get("clock_anchor"),
        protocol_id=str(stored.get("protocol_id")),
    )
    stored_bound = stored.get("b_fiducial_s")
    if (
        isinstance(stored_bound, bool)
        or not isinstance(stored_bound, int | float)
        or fresh.b_fiducial_s is None
    ):
        raise ValueError("source calibration bound is malformed")
    fresh = replace(
        fresh,
        b_fiducial_s=max(float(stored_bound), float(fresh.b_fiducial_s)),
    )
    bindings = dict(stored.get("bindings", {}))
    bindings.update(
        {
            "pulse_protocol_id": PROTOCOL_V2_ID,
            "estimator_revision": RESIDUAL_REGION_METHOD,
            "protocol_sha256": sha256_path(PROTOCOL_V2_PATH),
        }
    )
    validation_id = str(stored.get("validation_id") or source_dir.name) + "-v2"
    payload = instrument_evidence(
        fresh,
        bindings=bindings,
        validation_id=validation_id,
        artifact_sha256={
            relative: hashlib.sha256(raw_by_name[relative]).hexdigest()
            for relative in ("raw/powermetrics.plist", "events.jsonl")
        },
        capture_wall_time_s=capture_wall_time_from_events(
            raw_by_name["events.jsonl"]
        ),
        protocol_id=PROTOCOL_V2_ID,
        protocol_pulse_count=PROTOCOL_V2_PULSE_COUNT,
    )
    payload["clock_anchor"] = stored.get("clock_anchor")
    payload["clock_anchor_resolved"] = True
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create: re-derivation must never clobber an existing evidence
    # artifact (same rule as the extraction and campaign-log outputs).
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-live",
        action="store_true",
        help="explicitly confirm a lead-owned quiet-machine live run",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "runs" / "instrument_validation",
    )
    parser.add_argument("--rederive-from", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pulse-count", type=int, default=PULSE_COUNT)
    parser.add_argument(
        "--power-policy",
        default=None,
        help="operator-recorded power policy identity (e.g. 'ac_high_power'); required",
    )
    args = parser.parse_args()
    if not verify_frozen_protocol():
        print(
            "refusing: frozen powermetrics fiducial protocol is missing, "
            "incomplete, or disagrees with executable constants",
            file=sys.stderr,
        )
        return 2
    if args.rederive_from is not None:
        if args.output is None:
            print("refusing: --rederive-from requires --output", file=sys.stderr)
            return 2
        try:
            payload = rederive_artifact(args.rederive_from, args.output)
        except ValueError as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 2
        print(json.dumps({"status": payload["status"], "output": str(args.output)}))
        return 0 if payload["status"] == "valid" else 1
    if args.output is not None:
        print("refusing: --output requires --rederive-from", file=sys.stderr)
        return 2
    if not args.allow_live:
        print(
            "refusing: live [QUIET-MAC] calibration is lead-owned; "
            "pass --allow-live on a quiet machine",
            file=sys.stderr,
        )
        return 77
    if not args.power_policy:
        print("refusing: --power-policy is a binding field", file=sys.stderr)
        return 2

    import mlx.core as mx  # noqa: PLC0415

    clock = SystemClock()
    validation_id = time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    out_dir = args.output_root / validation_id
    (out_dir / "raw").mkdir(parents=True, exist_ok=False)
    capture_path = out_dir / "raw" / "powermetrics.plist"
    events_path = out_dir / "events.jsonl"
    events = events_path.open("w", encoding="utf-8")

    def emit(event_type: str, metadata: dict) -> None:
        events.write(
            json.dumps(
                {
                    "timestamp_s": clock.now(),
                    "event_type": event_type,
                    "phase": "instrument_validation",
                    "message": event_type,
                    "metadata": metadata,
                },
                sort_keys=True,
            )
            + "\n"
        )
        events.flush()

    buffers = allocate_matmul_buffers()
    command = [
        "sudo",
        "-n",
        POWER_METRICS,
        "-b",
        "0",
        "-i",
        str(SAMPLING_INTERVAL_MS),
        "--samplers",
        SAMPLERS,
        "--format",
        "plist",
        "-o",
        str(capture_path),
    ]
    pre_spawn = clock.stamp()
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    first_parse = None
    deadline = time.monotonic() + 15.0
    while time.monotonic() < deadline:
        if capture_path.exists() and capture_path.stat().st_size > 0:
            first_frame = capture_path.read_bytes().split(b"\0", 1)[0]
            if first_frame.strip():
                try:
                    parse_powermetrics_records(first_frame)
                except ValueError:
                    pass
                else:
                    first_parse = clock.stamp()
                    break
        time.sleep(0.05)
    if first_parse is None:
        process.terminate()
        print("powermetrics never became ready", file=sys.stderr)
        return 1
    # D-078: wait for a native whole-second rollover before any workload.
    try:
        wait_for_preworkload_rollover(capture_path, process)
    except RuntimeError as exc:
        events.close()
        print(f"refusing: {exc}", file=sys.stderr)
        return 1
    sampling_started = clock.stamp()
    emit("sampling_started", {})

    time.sleep(BASELINE_S)
    warmups: list[CommandedPulse] = []
    for warmup_index in range(WARMUP_PULSE_COUNT):
        on_stamp = clock.stamp()
        emit(
            "warmup_command_on",
            {"warmup_index": warmup_index, "clock_stamp": asdict(on_stamp)},
        )
        run_matmul_pulse(PULSE_DURATION_S, buffers)
        off_stamp = clock.stamp()
        emit(
            "warmup_command_off",
            {"warmup_index": warmup_index, "clock_stamp": asdict(off_stamp)},
        )
        warmups.append(
            CommandedPulse(
                on_s=on_stamp.epoch_s,
                off_s=off_stamp.epoch_s,
                on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
                off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
            )
        )
        time.sleep(1.5)
    time.sleep(BASELINE_S)

    # Van der Corput spacing is schedule-relative (offsets start at 0 for the
    # first pulse), so the loop cursor MUST be measured from the pulse-loop
    # start, not from sampling-start (which precedes it by the baseline +
    # warmup + baseline preamble). Measuring elapsed against sampling_started
    # made every gap negative and collapsed the pulses back-to-back.
    pulse_loop_mono0 = time.monotonic()
    pulses: list[CommandedPulse] = []
    for on_offset_s, off_offset_s in pulse_schedule(args.pulse_count):
        if pulses:
            elapsed_s = time.monotonic() - pulse_loop_mono0
            time.sleep(max(0.0, on_offset_s - elapsed_s))
        on_stamp = clock.stamp()
        emit(
            "pulse_command_on",
            {"clock_stamp": asdict(on_stamp), "planned_on_offset_s": on_offset_s},
        )
        run_matmul_pulse(PULSE_DURATION_S, buffers)
        off_stamp = clock.stamp()
        emit(
            "pulse_command_off",
            {"clock_stamp": asdict(off_stamp), "planned_off_offset_s": off_offset_s},
        )
        pulses.append(
            CommandedPulse(
                on_s=on_stamp.epoch_s,
                off_s=off_stamp.epoch_s,
                on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
                off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
            )
        )
    time.sleep(BASELINE_S)
    sampling_stopped = clock.stamp()
    emit("sampling_stopped", {})
    _terminate_powermetrics(process)
    post_parse = clock.stamp()

    data = capture_path.read_bytes()
    native_records = parse_powermetrics_records(data)
    evidence, point_anchor_s = derive_powermetrics_clock_evidence_v2(
        stamps={
            "pre_spawn": pre_spawn,
            "first_parse": first_parse,
            "sampling_started": sampling_started,
            "sampling_stopped": sampling_stopped,
            "post_parse": post_parse,
        },
        records=anchor_records_from_powermetrics(native_records),
    )
    anchor_resolved = point_anchor_s is not None
    if not anchor_resolved:
        print(
            "clock_anchor_unresolved: calibration capture cannot be anchored",
            file=sys.stderr,
        )
        # Fail closed: an unanchored capture can never be a valid calibration.
        # Detection still runs against the 1 s-quantized native stamps so the
        # diagnostic artifact records why, but the evidence is forced invalid
        # and the script exits nonzero below.
        anchored = native_records
    else:
        anchored = parse_powermetrics_records(
            data, first_record_endpoint_s=point_anchor_s
        )
    samples = samples_from_records(anchored)
    trace_path = out_dir / "power_trace.csv"
    with trace_path.open("w", encoding="utf-8") as handle:
        handle.write(
            "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
        )
        for sample in samples:
            handle.write(
                f"{sample.timestamp_s!r},{sample.power_w!r},{sample.source},"
                f"{sample.rail},{sample.interval_start_s!r},{sample.interval_end_s!r}\n"
            )

    intervals = [
        TraceInterval(
            start_s=record.timestamp_s - record.elapsed_ns / 1e9,
            end_s=record.timestamp_s,
            power_w=record.rail_power_w["gpu_power"],
        )
        for record in anchored
    ]
    detection = detect_pulses(
        trim_trace_after_warmups(intervals, warmups),
        pulses,
        trace_anchor_bound_s=(
            float(evidence["clock_anchor"]["effective_clock_anchor_bound_s"])
            if anchor_resolved
            else 0.0
        ),
    )
    events.close()

    device_meta = native_records[0].metadata if native_records else {}
    bindings = {
        "hardware_model": device_meta.get("hw_model"),
        "os_build": device_meta.get("kern_osversion"),
        "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
        "anchor_method_version": evidence["clock_anchor"].get("method"),
        "mlx_version": getattr(mx, "__version__", None),
        "pulse_protocol_id": PROTOCOL_ID,
        "power_policy": args.power_policy,
        "estimator_revision": RESIDUAL_REGION_METHOD,
        "protocol_sha256": sha256_path(PROTOCOL_PATH),
    }
    evidence_payload = instrument_evidence(
        detection,
        bindings=bindings,
        validation_id=validation_id,
        artifact_sha256={
            "raw/powermetrics.plist": sha256_path(capture_path),
            "events.jsonl": sha256_path(events_path),
            "power_trace.csv": sha256_path(trace_path),
        },
        capture_wall_time_s=sampling_started.epoch_s,
    )
    evidence_payload["clock_anchor"] = evidence["clock_anchor"]
    evidence_payload["clock_anchor_resolved"] = anchor_resolved
    if not anchor_resolved:
        evidence_payload["status"] = "invalid"
        evidence_payload["reasons"] = sorted(
            set(evidence_payload.get("reasons", [])) | {"clock_anchor_unresolved"}
        )
    (out_dir / "instrument_evidence.json").write_text(
        json.dumps(evidence_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "joulewise.instrument_validation_manifest.v1",
        "validation_id": validation_id,
        "protocol_id": PROTOCOL_ID,
        "pulse_count": args.pulse_count,
        "artifacts": {
            name: sha256_path(out_dir / name)
            for name in (
                "events.jsonl",
                "power_trace.csv",
                "instrument_evidence.json",
            )
        }
        | {"raw/powermetrics.plist": sha256_path(capture_path)},
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "validation_id": validation_id,
        "status": evidence_payload["status"],
        "b_fiducial_s": evidence_payload["b_fiducial_s"],
        "output": str(out_dir),
    }, indent=2))
    return 0 if evidence_payload["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
