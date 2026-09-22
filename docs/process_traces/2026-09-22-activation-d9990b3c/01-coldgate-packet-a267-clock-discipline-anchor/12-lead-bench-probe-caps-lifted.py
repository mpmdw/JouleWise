"""Lead-side bench probe: derive the v3 anchor on the real envelope data with the two absolute
caps lifted (span cap and effective-bound cap set to 1.0 s). Everything else unchanged.
Read-only over the archive. Prints per-envelope status/detail and the bound."""
import json, sys, time, dataclasses
sys.path.insert(0, "/Users/edr/code/JouleWise-wt-mag-d9990b3c")
import joulewise.uncertainty_evidence as ue
from scripts import sample_quiet_predicate_evidence as h
A = "/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence"
ue.MAX_WALL_MINUS_MONOTONIC_SPAN_S = 1.0
ue.MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S = 1.0
fields = [f.name for f in dataclasses.fields(ue.ClockStamp)]
print("ClockStamp fields:", fields)
for n in [int(x) for x in sys.argv[1:]] or [1, 2, 7, 8, 9, 10]:
    e = f"{n:02d}"
    s = json.load(open(f"{A}/envelope-{e}/session.json"))
    cs = s["power"]["anchor"]["clock_stamps"]
    stamps = {k: ue.ClockStamp(**{f: v[f] for f in fields}) for k, v in cs.items()}
    t = time.time()
    frames, dropped = h.parse_frames(open(f"{A}/envelope-{e}/raw/powermetrics-idle-{n}.plist", "rb").read())
    records = [ue.NativeAnchorRecord(elapsed_s=f["elapsed_s"], native_timestamp_s=f["native_timestamp_s"],
        power_w=f["power"]["rail_sum_w"] if f["power"]["rail_sum_w"] is not None else float("nan"),
        energy_j=f["energy_j"], is_delta=f["is_delta"], elapsed_ns=f["elapsed_ns"], native_timestamp_ns=f["native_timestamp_ns"]) for f in frames]
    an = ue.derive_powermetrics_anchor_v3(stamps=stamps, records=records)
    print(f"envelope {e}: frames={len(frames)} parse+derive={time.time()-t:.1f}s status={an['status']} detail={an.get('detail')} "
          f"span_ms={an.get('wall_minus_monotonic_span_s', float('nan'))*1e3:.3f} H_ms={(an.get('anchor_only_bound_s') or float('nan'))*1e3:.3f} "
          f"bound_ms={(an.get('effective_clock_anchor_bound_s') or float('nan'))*1e3:.3f} rate=[{an.get('rate_lower')},{an.get('rate_upper')}]", flush=True)
