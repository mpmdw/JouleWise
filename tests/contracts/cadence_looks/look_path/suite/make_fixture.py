"""Regenerate the frozen synthetic tree with runner 043b972f9 on PYTHONPATH."""
import hashlib
import json
import math
import struct
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.align.apple import cadence_ctl, workload
from joulewise.align.apple.r1_runtime import write_custody
from joulewise.bundle import RunBundleWriter
from joulewise.cadence import ctl, legs
from joulewise.clock import FakeClock
from joulewise.interfaces import PowerSample
from tests.align.test_apple_campaign import as_config, EpisodeSpec, ROOT

NS = 10**9
WALL = 18000  # wall minus monotonic, seconds
RAW = 7       # RAW minus monotonic, seconds
RUNNER = "043b972f999913d248769237f1901d78119ceb72"
RAILS = ("cpu_power", "gpu_power", "ane_power")
PACK = struct.Struct("<HHiiHHHH")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value) + b"\n")
    return digest(path.read_bytes())


class OffsetClock(FakeClock):
    def now(self):
        return super().now() + WALL

    def stamp(self):
        stamp = super().stamp()
        return replace(stamp, epoch_s=stamp.epoch_s + WALL)


def make_leg(span, spec, start, capture):
    leg = spec["leg_id"]
    legdir = span / "legs" / leg
    runtime = legdir / "runtime"
    member = "cadence-cl-ctl-01-" + leg
    bundle = runtime / "runs" / member
    (bundle / "outputs").mkdir(parents=True)
    script = spec["script"]
    work = dict(schema=ctl.WORK_SCHEMA, leg_id=leg, leg_spec_sha256=ctl.leg_spec_sha256(spec),
                script=script, complete=False, steps=[])
    mock_turns = ({"prompt_tokens": 2000, "content": "x"},) * 3
    cfg = as_config(EpisodeSpec(task_factory="tests.align.test_apple_campaign:make_synthetic_task",
                                condition="benign", seed=spec["seed"], max_turns=1, max_tokens=4096,
                                temperature=0, mock_turns=mock_turns), member)
    clock = OffsetClock(start)
    adapter = workload.EpisodeRuntimeAdapter(MockRuntimeAdapter(clock), clock)
    prepared = adapter.prepare(cfg)
    if not prepared.ok:
        raise ValueError(prepared.message)
    gate = dict(kind="G0", outcome="released", start_ns=int((start - 2)*NS), end_ns=start*NS)
    thermal = {"intervals": [gate]}
    adapter.thermal = SimpleNamespace(intervals=[gate], episode_reference={}, flags=[], events=[],
                                      wait=lambda *args, **kwargs: gate, record=lambda: thermal)
    with cadence_ctl.scripted_endpoint(script, work, synthetic=True):
        record = adapter.run_workload(cfg)
    episode_text = record.output_artifacts["align_episode.json"]
    episode = json.loads(episode_text)
    assert work["complete"] and not episode["power_traces"] and not episode["clock_mappings"]
    config_bytes = json.dumps(cfg.to_dict(), sort_keys=True, indent=2).encode() + b"\n"
    (bundle/"config.json").write_bytes(config_bytes)
    writer = RunBundleWriter(bundle, member, cfg, digest(config_bytes), clock, {"state": "synthetic"})
    writer.write_output("align_episode.json", episode_text)
    anchor = {"status": "bounded", "wall_minus_monotonic_lower_s": WALL,
              "wall_minus_monotonic_upper_s": WALL, "effective_clock_anchor_bound_s": 0.0001,
              "method": "invented paired stamps"}
    write(bundle/"metadata.json", {"run_id": member, "config_sha256": digest(config_bytes),
                                 "uncertainty_evidence": {"clock_anchor": anchor},
                                 "device": {"rail_manifest": list(RAILS)}})
    recovery = work["steps"][-1]
    # The plateau extends beyond all calls. Recovery's last 80 s are exactly flat.
    edge = recovery["started_ns"] / NS + 2
    end = episode["end_ns"] / NS
    samples = []
    for i in range((start-2)*10, math.ceil((end+2)*10) + 1):
        t = i/10
        for rail, idle, increment in zip(RAILS, (2, 3, 1), (1, 2, 0.5)):
            samples.append(PowerSample(timestamp_s=t+WALL, power_w=idle+(increment if t <= edge else 0),
                                       source="powermetrics", rail=rail, interval_start_s=(i-1)/10+WALL,
                                       interval_end_s=t+WALL))
    writer.write_power_trace(samples)
    if spec["g0_role"] == "capture":
        ref = {"schema": "joulewise.align_window_reference.v1", "status": "captured",
               "source": {"run_id": member, "config_sha256": digest(config_bytes)},
               "sensors": {"s_fast": "FAKE", "s_slow": "SLOW"},
               "rule": {"anchor": "warmup_entry", "window_s": 60, "statistic": "median", "min_coverage": .9},
               "span_ns": [(start-62)*NS, (start-2)*NS],
               "span_epoch_ns": [(start-62+WALL)*NS, (start-2+WALL)*NS],
               "coverage_fraction": 1, "samples": [[(start-62+i)*NS, 30, 30] for i in range(61)],
               "fast_c": 30, "slow_c": 30, "journal": "outputs/align_thermal.jsonl"}
        ref["sensors_policy_sha256"] = digest(canonical(ref["sensors"]))
        capture = digest(canonical(ref))
        write(bundle/"outputs/align_window_reference.json", dict(ref, record_sha256=capture))
    write(legdir/"leg_spec.json", spec)
    work_raw = (json.dumps(work, indent=1, sort_keys=True) + "\n").encode()
    (runtime/"script-work.json").write_bytes(work_raw)
    turn = episode["turns"][0]
    result = dict(schema="joulewise.align.r1_runtime_result.v1", kind="cadence-leg", backend="synthetic",
                  leg_id=leg, bundle="runs/"+member, member_status="succeeded", leg_status="complete",
                  g0_role=spec["g0_role"], g0_released=True, g0_reference_record_sha256=(
                      capture if spec["g0_role"] == "consume" else None),
                  turn_start_ns=turn["start_ns"], first_token_ns=turn["first_token_ns"], turn_end_ns=turn["end_ns"],
                  decode_tokens=turn["decode_tokens"], prefill_tokens=turn["prefill_tokens"],
                  script_record_sha256=digest(work_raw), script_complete=True)
    write(runtime/"runtime_result.json", result)
    write_custody(runtime, {"status": "complete"})
    attempt = {"attempt": 1, "redone": False, "contaminated": False, "output_dir": "legs/"+leg+"/runtime",
               "started_epoch_s": start+WALL-2, "ended_epoch_s": end+WALL+2, "leg_status": "complete"}
    write(legdir/"leg_record.json", {"schema": "joulewise.cadence_leg_record.v1", "spec": spec,
                                     "attempts": [attempt], "result": result})
    ordinal = int(leg[1:])
    return dict(leg_id=leg, attempts=[attempt], summary={"leg_id": leg, "admitted": True}), capture, (start, end, edge, ordinal)


def stream_file(path, spans):
    path.parent.mkdir(parents=True)
    lo = int(spans[0][0]) - 2
    hi = math.ceil(spans[-1][1]) + 2
    header = {"k":"h","schema":"joulewise.km003c_stream.v1","model":"POWER-Z KM003C","status":"streaming",
              "reason":None,"rate_idx":2,"sps":50,"poll_s":0.1,"start_raw_ns":(lo+RAW)*NS,
              "start_mono_ns":lo*NS,"start_real_ns":(lo+WALL)*NS}
    k = 0
    polls = 0
    with path.open("wb") as f:
        f.write(canonical(header)+b"\n")
        for j in range(lo*50, hi*50+1, 5):
            data = bytearray()
            for i in range(j, min(j+5,hi*50+1)):
                t = i/50
                while k+1 < len(spans) and t >= spans[k+1][0]-2:
                    k += 1
                start, end, edge, ordinal = spans[k]
                idle = 10 + ordinal  # sibling or wrong-span substitution changes the oracle
                watts = idle + (4 if start-2 <= t <= edge else 0)
                data.extend(PACK.pack(i*20 % 65536, 0, 10_000_000, watts*100_000, 0,0,0,0))
            rx = i*20_000_000 + RAW*NS
            f.write(canonical({"k":"b","n":len(data)//20,"p":data.hex(),"rx":rx,"tx":rx-1000,
                               "rt":rx+(WALL-RAW)*NS,"smc":{}})+b"\n")
            polls += 1
        f.write(canonical({"k":"t","polls":polls,"empties":0,"bad":0,"usb_errors":0,
                           "end_raw_ns":(hi+RAW)*NS,"end_mono_ns":hi*NS,
                           "elapsed_s":hi-lo,"stop_reason":"stop-file"})+b"\n")


def main(out):
    out.mkdir()
    kit = json.loads((ROOT/"docs/process/cadence/kits/cl-ctl-01.draft.json").read_bytes())
    for script in kit["seed_law"]["scripts"]:
        if script["kind"] == "split":
            script["gap_s"] = 60
    kit["legs"] = ctl.generate_legs(kit["campaign_id"], kit["seed_law"], kit["leg_defaults"])
    kit_sha = write(out/"authority/kit.json", kit)
    checks = {}
    for index, ids in enumerate(kit["layout"], 1):
        name = f"ctl-01-s0{index}"
        span = out/"spans"/name
        start = index*10000
        rows, windows = [], []
        capture = None
        for spec in legs.leg_specs(kit, ids):
            row, capture, window = make_leg(span, spec, start, capture)
            rows.append(row)
            windows.append(window)
            start = math.ceil(window[1])+6
        path = span/"hazards/meter/stream-001.jsonl"
        stream_file(path, windows)
        close = {"schema":"joulewise.cadence_span_receipt.v1","mock":True,"runner_kind":"cadence-ctl-v1",
                 "rc":0,"span_id":name,"roster":ids,"legs_finished":len(ids),"legs":rows,
                 "kit":{"campaign_id":"cl-ctl-01","sha256":kit_sha,"frozen_commit":RUNNER},
                 "feeds":{"meter":{"stop":{"rc":0,"proven_stopped":True},"files":[
                     {"path":path.relative_to(span).as_posix(),"sha256":digest(path.read_bytes())}]}}}
        write(span/"runner_receipt.json", close)
        # A test trust anchor for the actual close/Check bridge. Hash selected paths only.
        checks[name] = {p.relative_to(span).as_posix(): digest(p.read_bytes())
                        for p in sorted(span.rglob("*")) if p.is_file() and
                        p.name in ("runner_receipt.json","runtime_custody.json","leg_spec.json","leg_record.json")}
    write(out/"authority/check.json", checks)
    leaf = {"mean_w":1, "sd10_w":1, "sd40_w":1, "sd128_w":1, "kept":[60,15,4],
            "dropped":[0,0,0], "drift_w_per_600s":0}
    hold = {f"f2-inst-01/L00{i}": {c:leaf for c in ("gpu_rail","rail_sum","dc_in")} for i in (1,2)}
    write(out/"instrument/hold.json", hold)
    channels = ("gpu_rail", "rail_sum", "dc_in")
    edges = {"fallback":False,"gap_outside":False,"completion_to_stage_s":1,"unobserved_s":1}
    for field in ("recovery_s", "resolution_s", "rise_s", "recovery_resolution_s", "recovery_skipped_windows"):
        edges[field] = dict.fromkeys(channels, 0 if field == "recovery_skipped_windows" else 1)
    edges["recovery_resolution_s"] = dict.fromkeys(channels, 10)
    for field in ("rail_return_censor_s", "onset_lag_s", "decode_end_lag_s"):
        edges[field] = dict.fromkeys(channels[:2], 1)
    write(out/"instrument/edges.json", {k:edges for k in hold})


if __name__ == "__main__":
    main(Path(sys.argv[1]))
