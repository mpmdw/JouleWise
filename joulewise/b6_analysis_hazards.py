"""Registered §8.5 desk physics, from authenticated idle and monitor bytes."""
import json
import math
from pathlib import Path
import plistlib

from joulewise.b6_analysis_inputs import InputRefusal


def idle_graphics_power(data):
    total, length = 0., 0
    for frame in data.split(b"\0"):
        if not frame.strip():
            continue
        row = plistlib.loads(frame.strip())
        ns, processor = row["elapsed_ns"], row["processor"]
        power = (processor["gpu_power"] + processor["ane_power"]) / 1000.
        if type(ns) is not int or ns <= 0 or not math.isfinite(power) or power < 0:
            raise InputRefusal("idle_graphics_record_invalid")
        total += power * ns
        length += ns
    if not length:
        raise InputRefusal("idle_graphics_record_empty")
    return total / length


def desk_hazards(session, sizing):
    r = session.reader
    spans = r.json(session.archive / "withheld/spans.json", "hazard_spans").get("spans", {})
    journal = r.lines(session.archive / session.input_pin["contention_journal"], "contention_journal")
    intervals = []
    for row in journal:
        if row.get("schema") != "joulewise.hazard_journal.v1" or row.get("module") != "contention":
            raise InputRefusal("contention_journal_schema")
        if row.get("kind") != "interval":
            if row.get("kind") not in ("session_start", "session_end", "snapshot", "event", "cost"):
                raise InputRefusal("contention_journal_kind")
            continue
        v = row["values"]
        span = v["interval"]["monotonic_ns"]
        cpu = v["outside_total_cpu_s_per_s"]
        if row.get("error") is not None or span[1] <= span[0] or not math.isfinite(cpu) or cpu < 0:
            raise InputRefusal("contention_interval_invalid")
        intervals.append((span, cpu * (span[1] - span[0]) / 1e9))
    removed, processor_removed, records = set(), set(), {}
    for member in session.roster["members"]:
        if member.get("kind", "science") != "science":
            continue
        rid = member["run_id"]
        root = session.claim_root / rid
        if not (root / "metadata.json").is_file():
            continue  # a pre-bundle skip, already handled by C3
        metadata = r.json(root / "metadata.json", rid)
        if r.json(root / "summary_metrics.json", rid).get("status") != "succeeded":
            continue
        # The adapter promotes the ADMITTED retry to this canonical raw plist.
        # Attempt-specific raw artifacts remain audit evidence.
        px = idle_graphics_power(r.raw(root / "raw/powermetrics_idle.plist", rid))
        phase = "decode" if any("decode" in u["cell_id"] for u in member.get("units", [])) else "prefill"
        duration = sizing["phase_s"][session.pack][phase]
        pstar = sizing["F_min_j"] / (4 * duration)
        small = metadata.get("model", {}).get("name") == "Qwen3-1.7B-4bit"
        model_duration = sizing["gamma_small_model_phase_s"][phase] if session.pack == "GAMMA" and small else duration
        model_pstar = sizing["F_min_j"] / (4 * model_duration)
        if px >= pstar:
            removed.add(rid)
        request = spans.get(rid, {}).get("request")
        if isinstance(request, dict):
            request = request.get("monotonic_ns")
        if not isinstance(request, list) or len(request) != 2:
            raise InputRefusal("contention_request_span_missing")
        overlap = [(span, cpu) for span, cpu in intervals if span[0] <= request[1] and request[0] <= span[1]]
        if not overlap or min(span[0] for span, _ in overlap) > request[0] or max(span[1] for span, _ in overlap) < request[1]:
            raise InputRefusal("contention_request_uncovered")
        supports = sorted(span for span, _ in overlap)
        if any(left[1] < right[0] for left, right in zip(supports, supports[1:])):
            raise InputRefusal("contention_request_uncovered")
        cpu = math.fsum(c for _, c in overlap)
        excess = cpu - len(overlap) * sizing["quiet_cpu_s"]
        eadd = sizing["w_j_per_cpu_s"] * max(0., excess)
        if eadd >= sizing["F_min_j"] / 4:
            processor_removed.add(rid)
        records[rid] = {"P_x_w": px, "P_star_w": pstar, "T_phase_s": duration,
                        "per_model_P_star_w": model_pstar, "per_model_would_remove": px >= model_pstar,
                        "C_cpu_s": cpu, "k": len(overlap), "excess_cpu_s": excess, "E_add_j": eadd}
    return {"records": records, "power_removed": sorted(removed), "processor_alternative_removed": sorted(processor_removed),
            "power_rule": "registered per-pack and phase P*; GAMMA per-model line printed beside",
            "processor_label": "registered outside-processor rule (w = 5.432 J per CPU-s, c_q = 0.54 CPU-s)",
            "primary_processor_exclusion": False}
