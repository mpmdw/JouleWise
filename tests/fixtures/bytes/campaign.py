"""Production-shaped BYTES fixtures: mock reduction only, no inference/capture."""
from __future__ import annotations
import json
import math
import random
from pathlib import Path
from unittest.mock import patch
from joulewise import bytes_analysis as ba
from joulewise.external import km003c_parse as kp

FIXTURES = Path(__file__).resolve().parent

def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")

def archive_campaign(root, *, world="bytes", seed=1100, non_claim=True, release="all",
                     pass_duration_scales=(1.0, 2.0), clock_latency_ms=(-8.0, 3.0), sample_phase_ms=50,
                     edge_phase=True, min_receive_latency_ms=10.0,
                     subpack_sessions=False, uncollected_sessions=(), drop_8b_8bit=False):
    """1000 on-disk runs: real mock trace reducer -> harvest layout -> B6 export.

    No calibration hardware is claimed: the zero phase envelope is explicitly
    synthetic, with missing operative evidence disclosed. Each energy passes
    through reduce_bundle and the full CLI, not a summary oracle.
    subpack_sessions uses the R6 six sub-packs in both registered pass orders;
    an uncollected session is never generated or added to the manifest.
    """
    if len(pass_duration_scales) != 2 or any(v <= 0 for v in pass_duration_scales):
        raise ValueError("two positive pass duration scales required")
    if clock_latency_ms is not None and not clock_latency_ms[0] < 0 < clock_latency_ms[1]:
        raise ValueError("clock latency extremes must straddle zero")
    # Knob 1 (opus): samples sit strictly inside the 100 ms interval, 50 ms being the point
    # farthest from both edges. Knob 2: science-run edges sit at a uniform random offset
    # inside the interval (the device clock is not phase-locked to host events; the recorded
    # label phase drifts at ~2 ppm and sweeps a period every few hours). Knob 3: every batch
    # arrives at least 10 ms late (lower end of the recorded 10-17 ms USB arrival latency), so
    # the envelope fit labels every sample ~10 ms late: the physical form of the NR1 residual.
    if not 0 < sample_phase_ms < 100:
        raise ValueError("meter sample phase must lie strictly inside the 100 ms interval")
    if min_receive_latency_ms < 0:
        raise ValueError("minimum receive latency must be nonnegative")
    from types import SimpleNamespace
    from joulewise.b6 import export_runs, calibration, blinding
    import shutil
    from decimal import Decimal
    from tests.b6.support import document
    from joulewise.clock import FakeClock
    from joulewise.bundle import sanitize_id_component, _capture_source_state
    from joulewise.reduce import reduce_bundle
    from tests.test_reduce import BundleBuilder, load_config, DEFAULT_IDLE
    from joulewise.interfaces import PowerSample
    design = ba.read_json(FIXTURES / "campaign_design.json")
    if drop_8b_8bit:
        # Removed before registration: no run, reference identity or key uses this model.
        design["models"] = [m for m in design["models"] if m["model"] != "Qwen3-8B-8bit"]
    for model in design["models"]:
        model["config_key"] = blinding.configuration_key({"model": {"name": model["model"]},
            "workload_profile": {"name": "bytes-synthetic", "output_tokens": 512}})
    manifest = {"synthetic": True, "models": design["models"], "sessions": [],
                "synthetic_parameters": {"pass_duration_scales": list(pass_duration_scales),
                    "clock_latency_ms": clock_latency_ms, "reference_drift": design["reference_drift"],
                    "sample_phase_ms": sample_phase_ms, "edge_phase": edge_phase,
                    "min_receive_latency_ms": min_receive_latency_ms}}
    reference_drift = design["reference_drift"]
    rng = random.Random(seed)
    phase_rng = random.Random(seed * 7919 + 1)   # own stream: energy draws of every seed unchanged
    source_state = _capture_source_state()
    private = root / "private-keys" / "bytes" / "blinding"
    released = root / "released-keys" / "bytes" / "blinding"
    # The fixture JSON is sorted by name; R6 groups use registered identities.
    subpacks = (("Qwen3-1.7B-4bit", "Qwen3-4B-4bit"),
                ("Qwen3-8B-4bit", "Qwen3-30B-A3B-4bit"),
                ("Qwen3-14B-4bit", "Qwen3-Next-80B-A3B-Instruct-4bit"),
                ("Qwen3-32B-4bit", "Qwen3-8B-8bit"),
                ("Llama-3.3-70B-Instruct-4bit",), ("Qwen3.5-122B-A10B-4bit",))
    by_name = {m["model"]: m for m in manifest["models"]}
    schedule = [(pass_id, index + 1, [by_name[name] for name in (
                    indices if pass_id == 1 else tuple(reversed(indices))) if name in by_name])
                for pass_id in (1, 2)
                for index, indices in (list(enumerate(subpacks)) if pass_id == 1 else
                                       list(reversed(list(enumerate(subpacks)))))] if subpack_sessions else [
                    (pass_id, None, manifest["models"]) for pass_id in (1, 2)]
    for pass_id, subpack_id, models in schedule:
        pack_id = f"bytes-s{subpack_id}-p{pass_id}" if subpack_sessions else "bytes"
        session_id = pack_id if subpack_sessions else "bytes-p" + str(pass_id)
        if session_id in uncollected_sessions:
            continue
        archive = root / session_id
        bundles = archive / "sources/claim-runs"
        roster, evidence_members, meter_samples = [], [], []
        # Native 10 Hz meter, with optional unequal passes and signed clock-fit excess latency.
        tick = 1000
        meter_samples.extend([(.2, tick - 2), (.2, tick - 1)])
        jobs = []
        refs = design["neg8_references"]
        for ref in refs:
            if ref["role"] in ("corpus", "start"):
                jobs.append((manifest["models"][0], [ref]))
        midpoint = [(manifest["models"][0], [ref]) for ref in refs if ref["role"] == "midpoint"]
        for index, model in enumerate(models):
            if subpack_sessions and len(models) == 1:
                # Production single-model midpoint follows repeat + five quads.
                jobs += [(model, list(range(30))), *midpoint, (model, list(range(30, 50)))]
            else:
                jobs.append((model, [None] * 50))
                if index == (0 if subpack_sessions else 4):
                    jobs += midpoint
        jobs += [(manifest["models"][0], [ref]) for ref in refs if ref["role"] == "end"]
        for model, members in jobs:
            b = (model["W_bytes"] + model["KV_bytes"]) / 1e9
            resident = model["R_bytes"] / 1e9
            duration = model["synthetic_duration_s"] * pass_duration_scales[pass_id - 1]
            tau = duration / 512
            truth = .01 * b if world == "bytes" else 3 * tau if world == "time" else .01 * resident
            for ordinal, ref in enumerate(members):
                if isinstance(ref, int):
                    ordinal, ref = ref, None
                run_id = sanitize_id_component(ref["run_id"] if ref else model["model"] + "-" + str(ordinal))
                duration = 2.0 if ref else model["synthetic_duration_s"] * pass_duration_scales[pass_id - 1]
                own_idle = ref["idle_power_w"] if ref else 5.0
                reference_energy = (reference_drift["pivot_j"] + reference_drift["rails_scale"] *
                    (ref["gross_j"] - reference_drift["pivot_j"])) if ref else None
                energy = reference_energy * duration / (duration + 1) if ref else truth * 512 * (1 + rng.gauss(0, .002))
                power = energy / duration
                start = tick / 10 + (phase_rng.random() * .1 if edge_phase and not ref else 0)
                decode_start, end = start + 2, start + 2 + duration
                config = load_config(run_id=run_id, model={"name": model["model"], "family": "mock",
                    "weight_format": "mock", "context_window": 4096}, workload_profile={"name": "bytes-synthetic",
                    "prompt_tokens": 2048, "output_tokens": 512, "repetitions": 1, "warmup_runs": 1})
                with patch("joulewise.bundle._capture_source_state", return_value=source_state):
                    builder = BundleBuilder(bundles, config, FakeClock(start=1000))
                builder.measured_window(start + 1, end)
                builder.add_event("stage_started", "idle_baseline", start)
                builder.add_event("stage_completed", "idle_baseline", start + 1)
                builder.add_phase("prefill", start + 1, decode_start)
                builder.add_phase("decode", decode_start, end,
                    metadata={"output_tokens": 512, "requested_output_tokens": 512})
                # Compact constant-power point trace: all phase edges and at least
                # three records per phase, retaining the full pilot-scale span.
                stamps = [start+1, start+1.25, start+1.5, start+1.75,
                          decode_start, decode_start+duration/3,
                          decode_start+2*duration/3, end, end+.1]
                builder.write_trace([PowerSample(timestamp_s=t, power_w=power,
                    source="mock", rail="mock") for t in stamps])
                with patch("joulewise.bundle._capture_source_state", return_value=source_state):
                    bundle = builder.write_metadata(rail_manifest=["mock"], workload_observed={"output_token_count": 512},
                        idle={**DEFAULT_IDLE, "power_w_mean": own_idle, "duration_s": 1.0, "sample_count": 4,
                              "telemetry_backend": "mock", "status": "valid"})
                # Real desk reducer under the repository's mock telemetry path.
                summary = reduce_bundle(bundle).to_dict()
                actual = summary["phase_energy_j"]["decode"]
                # No half-width is defined for this constant-power reducer oracle:
                # use the brief's 1e-6 relative or absolute bar in joules.
                if not math.isclose(actual, energy, rel_tol=1e-6, abs_tol=1e-6):
                    raise AssertionError((actual, energy))
                summary.update(status="succeeded", bytes_synthetic_timing_fixture=True, energy_anchor_shift_envelopes={"/phase_energy_j/decode": {
                    "point_j": actual, "lower_j": actual, "upper_j": actual, "max_abs_delta_j": 0}},
                    energy_bound_terms_j={"E_clock_anchor_shift_bound_j": 0, "E_drift_bound_j": 0,
                        "E_interpolation_edge_bound_j": 0, "E_interpolation_joint_edge_bound_j": 0})
                _write_json(archive / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json"), summary)
                metadata = ba.read_json(bundle / "metadata.json")
                metadata["uncertainty_evidence"] = {"clock_anchor": {"clock_stamps": {
                    "sampling_started": {"epoch_s": start, "monotonic_before_s": start}}}}
                _write_json(bundle / "metadata.json", metadata)
                unit = {"cell_id": model["cell_ids"][0], "stratum": "repeat" if ordinal < 10 else "quad",
                        "unit_id": str(ordinal if ordinal < 10 else (ordinal - 10) // 4)}
                roster.append({"run_id": run_id, "stage_id": ref["role"] + "_reference" if ref else "decode",
                               "role": ref["role"] if ref else "science", "units": [] if ref else [unit]})
                evidence_members.append(SimpleNamespace(run_id=run_id, stage_id=ref["role"] + "_reference" if ref else "decode",
                                                       role=ref["role"] if ref else "science",
                                                       status="succeeded", config_key=model["model"]))
                end_tick = tick + 20 + round(duration * 10)
                baseline = 2 * own_idle if ref else .2
                active_tick = tick + (10 if ref else 20)
                # Whole-request DC = rails + independently drifting rest. At the
                # endpoints rest changes by 1 J (the attribution scale), while
                # rails changes by 0.01 J. Science DC remains twice rails.
                rest_reference = (reference_drift["pivot_j"] + reference_drift["rest_scale"] *
                    (ref["gross_j"] - reference_drift["pivot_j"])) if ref else None
                meter_power = power + rest_reference / (duration + 1) if ref else 2 * power
                if ref or not edge_phase:
                    meter_samples.extend((baseline if t < active_tick else meter_power, t) for t in range(tick, end_tick))
                    meter_samples.extend([(.2, end_tick), (.2, end_tick + 1)])
                else:
                    # The meter samples the true waveform at its own instants (tick + phase); edges are off-grid.
                    meter_samples.extend((meter_power if decode_start <= t / 10 + sample_phase_ms / 1000 < end else baseline, t)
                                         for t in range(tick, end_tick + 2))
                tick = end_tick + 2
        header = {"k": "h", "status": "streaming", "rate_idx": 1, "start_raw_ns": 0, "start_mono_ns": 0}
        batches = []
        for i in range(0, len(meter_samples), 10):
            part = meter_samples[i:i + 10]
            payload = b"".join(kp.SAMPLE.pack((t * 100 + sample_phase_ms) % kp.WRAP, 0, 1_000_000,
                round(w * 1e6), 0, 0, 0, 0) for w, t in part)
            stamp = part[-1][1] * 100_000_000 + sample_phase_ms * 1_000_000
            # One rare early receive and recurring late receives give the native
            # envelope fit both signs, with the negative extreme dominant.
            latency = 0 if clock_latency_ms is None else (clock_latency_ms[0]
                if i // 10 == (len(meter_samples) + 9) // 20 else clock_latency_ms[1] if i // 10 % 7 == 3 else 0)
            rx = stamp + round((latency + min_receive_latency_ms) * 1e6)
            batches.append({"k": "b", "tx": rx, "rx": rx, "n": len(part), "p": payload.hex(), "smc": {"B0AC": 0}})
        stream = archive / "sources/night-custody/hazards/meter/stream-001.jsonl"
        stream.parent.mkdir(parents=True)
        trailer = {"k": "t", "end_raw_ns": tick * 100_000_000, "end_mono_ns": tick * 100_000_000}
        stream.write_text("".join(json.dumps(item) + "\n" for item in (header, *batches, trailer)))
        _write_json(archive / "derived/roster.json", {"pack_id": pack_id, "attempt": 1, "members": roster})
        acceptance = {"pack_id": pack_id, "session_id": session_id, "verdict": "PASS", "counting": True,
                      "excluding": [], "flag_counts": {}, "emitted_flags": [],
                      "calibration": calibration.evaluate(calibration.Capture(Decimal(".040"), "valid"),
                          calibration.Capture(Decimal(".030"), "valid"), document(), [], [session_id], False)}
        _write_json(archive / "derived/b6-acceptance.json", acceptance)
        (archive / "derived/flags.jsonl").write_text("")
        evidence = SimpleNamespace(stages=[SimpleNamespace(members=evidence_members)], runtime={}, session_id=session_id)
        export_runs.export(archive, {}, root / "registration", root / "private-keys", root / "export", non_claim=non_claim,
                           evidence=evidence, acceptance_record=acceptance,
                           **({"pack_registration": {"blinding_group": "bytes", "bytes_pass": pass_id}}
                              if subpack_sessions else {}))
        manifest["sessions"].append({"session_id": session_id, "archive": str(archive), "pass_id": pass_id,
            "released_key_dir": "../released-keys/bytes/blinding", "test7_passed": False,
            # Deliberately false legacy values: the consumer must ignore these.
            "drift_allowance_j": dict.fromkeys(ba.BOUNDARIES, 999),
            "drift_reference": {"energy_j": dict.fromkeys(ba.BOUNDARIES, 999), "duration_s": 999, "test7_passed": True}})
    # Synthetic non-claim exports have identity keys, yet still require explicit
    # release files. Claim-shaped exports use the native exporter's random keys.
    if non_claim:
        private.mkdir(parents=True, exist_ok=True)
        _write_json(private / "pack.json", {"factor": 1.0})
        for key in ["neg8_reference", *(m["model"] + "|bytes-synthetic|512" for m in manifest["models"])]:
            _write_json(private / blinding._config_filename(key), {"key": key, "factor": 1.0})
    release_keys(root, manifest, release)
    return manifest


def release_keys(root, manifest, which):
    from joulewise.b6 import blinding
    import shutil
    private = root / "private-keys" / "bytes" / "blinding"
    released = root / "released-keys" / "bytes" / "blinding"
    released.mkdir(parents=True, exist_ok=True)
    if which == "none":
        return
    shutil.copyfile(private / "pack.json", released / "pack.json")
    keys = ["neg8_reference"] + [m["model"] + "|bytes-synthetic|512"
        for m in manifest["models"] if which == "all" or m["role"] == "fit"]
    for key in keys:
        name = blinding._config_filename(key)
        shutil.copyfile(private / name, released / name)
