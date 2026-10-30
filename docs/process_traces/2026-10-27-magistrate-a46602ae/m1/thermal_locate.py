"""Where in each member did the OS thermal level leave 0?  Structure only, no energy.
Usage: python3 -I thermal_locate.py <checkout> <hazards/thermal.jsonl> <order.txt>
order.txt: one bundle directory per line in collection order (metadata.json, events.jsonl)."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from joulewise.b5.harvest import member_spans, read_monitor_journal, in_force
POLL_S = 5

def _mapper(metadata):
    pair = metadata["uncertainty_evidence"]["clock_anchor"]["clock_stamps"]["sampling_started"]
    return lambda wall: math.floor((pair["monotonic_before_s"] + (wall - pair["epoch_s"])) * 1e9)

def stage_ns(metadata, events, phase, kind):
    mapped = _mapper(metadata)
    for e in events:
        if e.get("phase") == phase and e.get("event_type") == kind:
            own = (e.get("metadata") or {}).get("monotonic_ns")
            return own if type(own) is int else mapped(e["timestamp_s"])
    return None

def members(order):
    out = []
    for line in Path(order).read_text().split():
        b = Path(line)
        meta = json.loads((b / "metadata.json").read_text())
        events = [json.loads(x) for x in (b / "events.jsonl").read_text().splitlines() if x.strip()]
        spans = member_spans(meta, events)
        out.append({"run_id": b.name, "span": spans["member"],
                    "load_start": stage_ns(meta, events, "warmup", "stage_started"),
                    "request_end": spans["request"][1] if spans["request"] else None})
    return out

def category(m, t):
    a, b = m["span"]
    if t <= a: return "before_start"
    if t >= b: return "after_end"
    if m["load_start"] is not None and t < m["load_start"]: return "idle_baseline"
    if m["request_end"] is not None and t <= m["request_end"]: return "load"
    return "tail"

def main():
    readings, malformed = read_monitor_journal(Path(sys.argv[2]), "thermal")
    samples = [(r.monotonic_ns, int(r.values["level"])) for r in readings
               if r.status == "ok" and isinstance(r.values.get("level"), int)]
    times = [t for t, _ in samples]
    ms = members(sys.argv[3])
    print(f"thermal reads {len(samples)}, malformed {malformed}, "
          f"largest poll gap {max(b - a for a, b in zip(times, times[1:])) / 1e9:.1f} s")
    for m in ms:
        idx = [i for i in in_force(times, *m["span"]) if samples[i][1] != 0]
        if idx:
            print(m["run_id"], sorted({category(m, samples[i][0]) for i in idx}))
    ends = sorted(m["request_end"] for m in ms if m["request_end"])
    i = 0
    while i < len(samples):
        if samples[i][1] == 0:
            i += 1; continue
        j = i
        while j + 1 < len(samples) and samples[j + 1][1] != 0:
            j += 1
        onset, stop = samples[i][0], (samples[j + 1][0] if j + 1 < len(samples) else samples[j][0])
        prior = [e for e in ends if e <= onset]
        inside = next((m["run_id"] for m in ms if m["span"][0] <= onset <= m["span"][1]), "gap")
        lag = f"{POLL_S * round((onset - prior[-1]) / 1e9 / POLL_S)} s" if prior else "n/a"
        print(f"episode: length ~{POLL_S * round((stop - onset) / 1e9 / POLL_S)} s, "
              f"onset {lag} after latest request end, onset in {inside}")
        i = j + 1

if __name__ == "__main__":
    main()
