"""Invented native record shapes; no hardware, outcomes, or data paths."""
import json

NS = 1_000_000_000
EPOCH = 1_800_000_000


def fixture():
    def span(a, b, **extra):
        return dict(started_epoch_s=EPOCH + a, ended_epoch_s=EPOCH + b, **extra)

    def event(at, kind, phase):
        return dict(timestamp_s=EPOCH + at, event_type=kind, phase=phase,
                    message="synthetic", metadata={})

    stages = [("prepare", 20, 23), ("idle_baseline", 23, 28), ("warmup", 28, 30),
              ("measured_run", 30, 58), ("cleanup", 58, 59), ("reduce", 59, 60)]
    events = [event(20, "run_started", "run")]
    for phase, a, b in stages:
        events += [event(a, "stage_started", phase), event(b, "stage_completed", phase)]
    events += [event(60, "run_finalized", "run")]
    mono = lambda s: (100 + s) * NS
    episode = dict(
        episode_id="m1", start_ns=mono(30), end_ns=mono(58), clock_domain="synthetic.mono",
        hardware={"thermal": {"intervals": [
            dict(kind=k, start_ns=mono(a), end_ns=mono(b), duration_s=b-a, outcome=outcome)
            for k, a, b, outcome in [("G0", 30, 32, "released"), ("H", 38, 42, "released"),
                                      ("G1", 52, 55, "timeout")]]}},
        clock_mappings=[dict(trace_domain="joulewise.controller.epoch_ns",
                             episode_domain="synthetic.mono", offset_ns=(100-EPOCH)*NS,
                             uncertainty_ns=100, method="synthetic")],
        turns=[dict(index=0, start_ns=mono(32), first_token_ns=mono(34), end_ns=mono(52),
                    decode_tokens=100, tool_calls=[dict(start_ns=mono(50), end_ns=mono(52))]),
               dict(index=1, start_ns=mono(55), first_token_ns=mono(56), end_ns=mono(57),
                    decode_tokens=10, tool_calls=[])])
    docs = {
        "night/result.json": span(0, 87, started_monotonic_ns=0, ended_monotonic_ns=87*NS),
        "night/chain.started": dict(epoch_s=EPOCH+5, monotonic_ns=5*NS),
        "night/chain.exited": dict(epoch_s=EPOCH+85, monotonic_ns=85*NS, exit_code=0),
        "plan.json": dict(t0_epoch_s=EPOCH, window_max_s=59520),
        "arm.json": span(0, 2), "dwell.json": span(2, 5), "offload.json": span(90, 100),
        "night/chain-stages.jsonl": [span(5, 15, stage_id="refs", kind="campaign_collection", rc=0),
                                      span(20, 60, stage_id="science", kind="campaign_collection", rc=0),
                                      span(70, 85, stage_id="verdict", kind="whole_window_verdict", rc=0)],
        "runs/m1/metadata.json": dict(run_id="m1", clock={"type": "system"}),
        "runs/m1/events.jsonl": events,
        "runs/m1/outputs/align_episode.json": episode,
    }
    return {path: (("".join(json.dumps(row)+"\n" for row in obj)) if path.endswith(".jsonl")
                   else json.dumps(obj)).encode() for path, obj in docs.items()}


def options():
    return dict(night_result="night/result.json", chain_started="night/chain.started",
                chain_exited="night/chain.exited", chain_journal="night/chain-stages.jsonl",
                plan="plan.json", bundles=["runs/m1"], stage_phases={"refs": "references"},
                spans=[("arm", "arm.json"), ("dwell", "dwell.json"), ("offload", "offload.json")])


def campaign(members=22):
    """Expand the invented member in time; still no models or measurements."""
    docs, opts = fixture(), options()
    template = {p: raw for p, raw in docs.items() if p.startswith("runs/m1/")}
    for path in template:
        del docs[path]
    opts["bundles"] = []
    for i in range(members):
        member = f"m{i+1:03}"
        shift = i*40
        for path, raw in template.items():
            new_path = path.replace("runs/m1/", f"runs/{member}/")
            if path.endswith("events.jsonl"):
                rows = [json.loads(r) for r in raw.splitlines()]
                for row in rows:
                    row["timestamp_s"] += shift
                docs[new_path] = "".join(json.dumps(r)+"\n" for r in rows).encode()
            elif path.endswith("align_episode.json"):
                row = json.loads(raw)
                row["episode_id"] = member
                row["start_ns"] += shift*NS
                row["end_ns"] += shift*NS
                for turn in row["turns"]:
                    for key in ("start_ns", "end_ns", "first_token_ns"):
                        turn[key] += shift*NS
                    for call in turn["tool_calls"]:
                        call["start_ns"] += shift*NS
                        call["end_ns"] += shift*NS
                for gate in row["hardware"]["thermal"]["intervals"]:
                    gate["start_ns"] += shift*NS
                    gate["end_ns"] += shift*NS
                docs[new_path] = json.dumps(row).encode()
            else:
                row = json.loads(raw)
                row["run_id"] = member
                docs[new_path] = json.dumps(row).encode()
        opts["bundles"].append(f"runs/{member}")
    extra = (members-1)*40
    for path in ("night/result.json", "night/chain.exited", "offload.json"):
        row = json.loads(docs[path])
        if "ended_epoch_s" in row:
            row["ended_epoch_s"] += extra
        if "started_epoch_s" in row and path == "offload.json":
            row["started_epoch_s"] += extra
        if "ended_monotonic_ns" in row:
            row["ended_monotonic_ns"] += extra*NS
        if "epoch_s" in row:
            row["epoch_s"] += extra
            row["monotonic_ns"] += extra*NS
        docs[path] = json.dumps(row).encode()
    rows = [json.loads(r) for r in docs["night/chain-stages.jsonl"].splitlines()]
    rows[1]["ended_epoch_s"] += extra
    rows[2]["started_epoch_s"] += extra
    rows[2]["ended_epoch_s"] += extra
    docs["night/chain-stages.jsonl"] = "".join(json.dumps(r)+"\n" for r in rows).encode()
    return docs, opts
