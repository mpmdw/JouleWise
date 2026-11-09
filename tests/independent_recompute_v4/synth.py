"""Synthetic inputs for the v4 independent recompute. Standard library only; no real data.

Two frame writers:
- ``frame_dict``/``frame_bytes``: a powermetrics-shaped plist dict serialized by plistlib (the reference).
- ``FrameTemplate``: the same document serialized once with placeholders, then filled by string
  substitution, so a full-size member (about 507 MB, 9,600 frames of about 52.8 kB) is cheap to write.

``write_series`` writes a complete synthetic series root in the recompute's input layout
(docs/analysis/v4/RECOMPUTE-opus.md, "Input layout").
"""
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import random
import struct

PAIRS = ("spam", "bank")
EPOCH0_S = 1_794_000_000  # 2026-11-07, synthetic
NS = 1_000_000_000


def _task(i, rng):
    # Decoy keys named like the extracted ones live inside tasks and clusters: a path-blind
    # extractor would pick them up.
    return {"pid": 100 + i, "name": f"proc{i:04d}", "cputime_ns": rng.randrange(10**9),
            "cputime_ms_per_s": rng.random() * 10, "cputime_sample_ms_per_s": rng.random(),
            "cputime_user_ns": rng.randrange(10**9), "intr_wakeups": rng.randrange(1000),
            "idle_wakeups": rng.randrange(1000), "diskio_bytesread": rng.randrange(10**6),
            "diskio_byteswritten": rng.randrange(10**6), "packets_received": rng.randrange(100),
            "gpu_power": rng.random() * 1000, "energy_impact": rng.random() * 5,
            "timer_wakeups": [{"interval_ns": 2000000, "wakeups": rng.randrange(50)},
                              {"interval_ns": 5000000, "wakeups": rng.randrange(50)}]}


def frame_dict(elapsed_ns, timestamp_s, gpu_mw, cpu_mw=1500.0, ane_mw=0.0, pressure="Nominal",
               dvfm=((389, 0.1), (1398, 0.6)), n_tasks=35, seed=0, n_clusters=3):
    """A powermetrics-like sample of about 52.8 kB in XML. ``dvfm`` gives (MHz, used fraction) pairs."""
    rng = random.Random(seed)
    clusters = []
    for c, name in enumerate(("E-Cluster", "P0-Cluster", "P1-Cluster")[:n_clusters]):
        clusters.append({"name": name, "freq_hz": 2.0e9 + c, "idle_ns": rng.randrange(elapsed_ns + 1),
                         "dvfm_states": [{"freq": f, "used_ns": rng.randrange(elapsed_ns + 1),
                                          "used_ratio": rng.random()} for f in (600, 1200, 2000, 3000)],
                         "cpus": [{"cpu": k, "freq_hz": 3.0e9, "idle_ns": rng.randrange(elapsed_ns + 1),
                                   "cpu_power": rng.random() * 100,  # decoy at a nested path
                                   "dvfm_states": [{"freq": f, "used_ns": rng.randrange(elapsed_ns + 1),
                                                    "used_ratio": rng.random()} for f in (600, 2000)]}
                                  for k in range(4)]})
    return {
        "is_delta": True, "elapsed_ns": elapsed_ns, "hw_model": "Mac15,9",
        "kern_osversion": "25A000", "kern_bootargs": "", "kern_boottime": EPOCH0_S - 86400,
        "timestamp": datetime.datetime.fromtimestamp(timestamp_s, datetime.UTC).replace(tzinfo=None),
        "thermal_pressure": pressure,
        "tasks": [_task(i, rng) for i in range(n_tasks)],
        "all_tasks": {"cputime_ns": rng.randrange(10**12), "gpu_power": 1.0, "elapsed_ns": 7},
        "network": {"ibyte_rate": 0.0, "obyte_rate": 0.0},
        "processor": {"clusters": clusters, "cpu_energy": int(cpu_mw), "cpu_power": cpu_mw,
                      "gpu_energy": int(gpu_mw), "gpu_power": gpu_mw, "ane_energy": int(ane_mw),
                      "ane_power": ane_mw, "combined_power": cpu_mw + gpu_mw + ane_mw},
        "gpu": {"freq_hz": 1.398e9, "idle_ns": 1, "idle_ratio": 0.3,
                "dvfm_states": [{"freq": f, "used_ns": round(u * elapsed_ns), "used_ratio": u} for f, u in dvfm],
                "sw_requested_state": [{"sw_req_state": "P1", "used_ns": 1, "used_ratio": 0.1}],
                "gpu_energy": int(gpu_mw)},
    }


def frame_bytes(**kwargs):
    return plistlib.dumps(frame_dict(**kwargs), fmt=plistlib.FMT_XML)


class FrameTemplate:
    """One plistlib serialization with placeholders; fill() substitutes the per-sample values."""
    FIELDS = ("elapsed", "stamp", "pressure", "cpu", "gpu", "ane", "used0", "used1")

    def __init__(self, n_tasks=35, seed=0, clusters=3):
        doc = frame_dict(elapsed_ns=100_000_000, timestamp_s=EPOCH0_S, gpu_mw=0.0, n_tasks=n_tasks, seed=seed,
                         n_clusters=clusters)
        doc["elapsed_ns"] = "@@elapsed@@"
        doc["timestamp"] = "@@stamp@@"
        doc["thermal_pressure"] = "@@pressure@@"
        doc["processor"]["cpu_power"] = "@@cpu@@"
        doc["processor"]["gpu_power"] = "@@gpu@@"
        doc["processor"]["ane_power"] = "@@ane@@"
        doc["gpu"]["dvfm_states"][0]["used_ns"] = "@@used0@@"
        doc["gpu"]["dvfm_states"][1]["used_ns"] = "@@used1@@"
        text = plistlib.dumps(doc, fmt=plistlib.FMT_XML).decode()
        for name, tag in (("elapsed", "integer"), ("stamp", "date"), ("cpu", "real"), ("gpu", "real"),
                          ("ane", "real"), ("used0", "integer"), ("used1", "integer")):
            text = text.replace(f"<string>@@{name}@@</string>", f"<{tag}>@@{name}@@</{tag}>")
        parts = text.split("@@")
        self.literal, self.slots = parts[0::2], parts[1::2]

    def fill(self, elapsed_ns, timestamp_s, gpu_mw, cpu_mw=1500.0, ane_mw=0.0, pressure="Nominal",
             used=(0.1, 0.6)):
        stamp = datetime.datetime.fromtimestamp(timestamp_s, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        values = {"elapsed": str(elapsed_ns), "stamp": stamp, "pressure": pressure, "cpu": repr(float(cpu_mw)),
                  "gpu": repr(float(gpu_mw)), "ane": repr(float(ane_mw)),
                  "used0": str(round(used[0] * elapsed_ns)), "used1": str(round(used[1] * elapsed_ns))}
        out = [self.literal[0]]
        for slot, lit in zip(self.slots, self.literal[1:]):
            out.append(values[slot])
            out.append(lit)
        return "".join(out).encode()


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")


# ---------------------------------------------------------------- series writer

class Member:
    """A synthetic member: turns with token counts and a GPU power profile, placed on a clock."""

    def __init__(self, run_id, pair, condition, kind, model, start_mono_ns, rng, n_turns, beta, sigma,
                 period_ns, template, reasoning=200, identical_to=None):
        self.run_id, self.pair, self.condition, self.kind, self.model = run_id, pair, condition, kind, model
        self.period_ns, self.template = period_ns, template
        self.turns = []
        t = start_mono_ns + 300 * NS  # G0 window before the first turn
        context = 0
        trng = random.Random(identical_to) if identical_to is not None else rng
        for k in range(n_turns):
            prefill = trng.randrange(200, 1500) if k else trng.randrange(2000, 6000)
            decode = trng.randrange(100, 1200)
            reason = min(decode, trng.randrange(0, reasoning + 1))
            duration = (2 + decode // 40) * NS
            start = t + (30 * NS if k else 0)  # G1 window before turns k >= 1
            x = design(context, prefill, decode)
            energy = sum(b * v for b, v in zip(beta, x)) + rng.gauss(0, sigma)
            tool = (start + duration, start + duration + 2 * NS)
            self.turns.append({"index": k, "start_ns": start, "end_ns": start + duration,
                               "context_tokens": context, "prefill_tokens": prefill, "decode_tokens": decode,
                               "hidden_tokens": 0, "reasoning_tokens": reason,
                               "tool_calls": [{"name": "t", "start_ns": tool[0], "end_ns": tool[1],
                                               "args_bytes": 1, "result_bytes": 1}],
                               "_energy": max(energy, 1.0)})
            context += prefill + decode
            t = tool[1] + 5 * NS
        self.start_ns, self.end_ns = start_mono_ns, t + 5 * NS


COHORT = "c" * 64


def seed_law(seed_index, pair):
    """P:166-170 seed law, written again here for the synthetic writer."""
    name = "spam_filter_update" if pair == "spam" else "bank_transfer_2"
    text = json.dumps(["align-p4-v1", "qwen3.8-27b", "thinking_on", "shade/" + name, seed_index],
                      separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


def design(c, p, d):
    return (1.0, float(p), float(d), (c + p) * d + d * d / 2, c * p + p * p / 2)


MODEL_TAGS = {"D": "qwen3.8-27b", "30B": "qwen3-30b-a3b"}


def seed_law_model(model_tag, seed_index, pair):
    """Production sampling.episode_seed for any model tag (thinking_on)."""
    name = "spam_filter_update" if pair == "spam" else "bank_transfer_2"
    text = json.dumps(["align-p4-v1", model_tag, "thinking_on", "shade/" + name, seed_index],
                      separators=(",", ":"), ensure_ascii=True)
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")


def write_config(base, run_id, seed_index, pair, condition, model="D", thinking=True, sampler=True, root=None):
    """The member's kit config (a producer-shaped BenchmarkConfig subset: run_id, model.name,
    run_metadata.tags, workload_profile.prompt_text = the episode spec JSON) and the bundle config.json
    RunBundleWriter.create writes for it (indent-2, sorted keys, newline). Returns (planned_config reference
    relative to ``root``, kit sha256 = the plan's config_sha256)."""
    spec = {"schema": "joulewise.align.apple.episode_spec.v1", "seed": seed_index, "condition": condition,
            "task_kwargs": {"task_pair": "spam_filter_update" if pair == "spam" else "bank_transfer_2"}}
    if thinking is not None:
        spec["enable_thinking"] = thinking
    if sampler:
        spec["sampler"] = {"min_p": 0, "temperature": 1.0, "top_k": 20, "top_p": 0.95}
    local = run_id.split(":", 1)[-1]
    kit = {"run_id": local, "model": {"name": "synthetic/Qwen"},
           "run_metadata": {"project": "joulewise", "tags": [f"align-model={MODEL_TAGS[model]}"]},
           "workload_profile": {"name": "align_episode", "prompt_text": json.dumps(spec, sort_keys=True)}}
    raw = (json.dumps(kit, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (Path(base) / "config.json").write_bytes(raw)
    root = Path(root) if root is not None else Path(base).parents[3]
    kpath = root / "kit" / Path(base).parts[-3] / (local + ".json")
    kpath.parent.mkdir(parents=True, exist_ok=True)
    kpath.write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()
    return {"path": str(kpath.relative_to(root)), "sha256": sha}, sha


def write_member(root, wid, m, epoch_offset_ns, delta=(1.0, 1.0), big=False, full_frames=None, extra=None):
    """Write metadata, episode, thermal journal and the raw plist of one member."""
    base = Path(root) / "windows" / wid / "members" / m.run_id
    span_start = m.start_ns - 10 * NS
    # Power: piecewise constant per sample. Inside an owned turn span the GPU power is the turn's mean
    # power; tool spans and idle draw 2 W, which also enters the owned tool energy.
    owned = []
    for t in m.turns:
        owned.append((t["start_ns"], t["end_ns"], t["_energy"] / ((t["end_ns"] - t["start_ns"]) / NS) * 1000))
    period = m.period_ns
    n = full_frames if full_frames is not None else (m.end_ns + 10 * NS - span_start) // period
    raw = base / "raw" / "powermetrics.plist"
    raw.parent.mkdir(parents=True, exist_ok=True)
    first_end = span_start + period
    with open(raw, "wb") as fh:
        j = 0
        for i in range(n):
            end = first_end + i * period
            mid = end - period // 2
            while j < len(owned) and owned[j][1] <= mid:
                j += 1
            gpu = owned[j][2] if j < len(owned) and owned[j][0] <= mid < owned[j][1] else 2000.0
            fh.write(m.template.fill(elapsed_ns=period, timestamp_s=(end + epoch_offset_ns) // NS, gpu_mw=gpu))
            fh.write(b"\x00")
    stamp = {"epoch_ns": m.start_ns + epoch_offset_ns, "monotonic_before_ns": m.start_ns,
             "monotonic_after_ns": m.start_ns}
    dump(base / "metadata.json", {"uncertainty_evidence": {"clock_anchor": {
        "first_sample_end_point_epoch_s": (first_end + epoch_offset_ns) / NS}},
        "sampling": {"power_period_ns": period}})
    g0 = {"kind": "G0", "turn": 0, "start_ns": m.start_ns, "end_ns": m.start_ns + 290 * NS,
          "outcome": "released", "release": {"fast_c": 50.0, "slow_c": 40.0},
          "exit_sample_ns": m.start_ns + 290 * NS}
    intervals = [g0]
    for t in m.turns[1:]:
        intervals.append({"kind": "G1", "turn": t["index"], "start_ns": t["start_ns"] - 30 * NS,
                          "end_ns": t["start_ns"] - NS, "outcome": "released",
                          "release": {"fast_c": 50.0, "slow_c": 40.0}, "exit_sample_ns": t["start_ns"] - NS})
    episode = {"episode_id": m.run_id, "task_pair": "shade/" + ("spam_filter_update" if m.pair == "spam"
                                                                else "bank_transfer_2"),
               # R21 A2 / R23: G0 lies before the episode, so the episode starts after the G0 window.
               "condition": m.condition, "start_ns": g0["end_ns"] + 5 * NS, "end_ns": m.end_ns,
               "turns": [dict({k: v for k, v in t.items() if not k.startswith("_")},
                              first_token_ns=t["start_ns"] + NS) for t in m.turns],
               "flags": [],
               "hardware": {"paired_clock_stamps_ns": [stamp, stamp],
                            "registered_span_ns": [g0["end_ns"] + 5 * NS, m.end_ns],
                            "thermal": {"policy": {"sensors": {"s_fast": "Tg0f", "s_slow": "Th0x"},
                                                   "delta_fast_c": delta[0], "delta_slow_c": delta[1]},
                                        "episode_reference": {"fast_c": 50.0, "slow_c": 40.0},
                                        "intervals": intervals},
                            "cache": {"rebuilds": 0, "rewinds": 0}}}
    episode.update(extra or {})
    dump(base / "outputs" / "align_episode.json", episode)
    rows = []
    t = span_start
    while t <= m.end_ns + 10 * NS:
        rows.append(json.dumps({"kind": "sample", "monotonic_ns": t, "sensors": {"Tg0f": 50.0, "Th0x": 40.0},
                                "status": {"os_level": 0}}, sort_keys=True))
        t += NS
    (base / "outputs" / "align_thermal.jsonl").write_text("\n".join(rows) + "\n")


ALLOCATION = Path(__file__).resolve().parent / "fixtures" / "series_manifest_r24.json"


def window_roster(wid, role, index):
    """The frozen R24 allocation's roster of a C/T window (fixtures/series_manifest_r24.json), in the
    recompute layout: production run ids ``align-v4-<window>-eNN`` (anchors "<window>:<W1 kit id>"), the
    manifest's seed_index and episode_seed (expected_episode_seed) for D members."""
    kinds = {"anchor": "anchor", "sentinel": "sentinel", "calibration": "benign", "known_h": "sabotage"}
    doc = json.loads(ALLOCATION.read_text())
    rows = next(w for w in doc["windows"] if w["id"] == wid)["members"]
    roster = []
    for a in sorted(rows, key=lambda a: a["ordinal"]):
        o = a["ordinal"]
        kind = kinds.get(a["pool"]) or ("sabotage" if a["condition"] == "sabotage" else "benign")
        model = "D" if a["model_id"] == "qwen3.8-27b" else "30B"
        r = {"ordinal": o, "kind": kind, "model": model,
             "pair": "spam" if a["pair"] == "spam_filter_update" else "bank", "condition": a["condition"],
             "run_id": (f"{wid}:align-pilot-v3-episodes-a-e{o:02d}" if kind == "anchor"
                        else f"align-v4-{wid.lower()}-e{o:02d}")}
        r.update(seed_index=a["seed_index"], expected_episode_seed=a["episode_seed"])
        roster.append(r)
    return roster


W1_ROSTER = (  # protocol v4 "W1 roster" after chair 1(g): (ordinal, kind, model, pair, condition, contrast)
    (1, "anchor", "30B", "spam", "benign", None), (2, "anchor", "30B", "bank", "sabotage", None),
    (3, "anchor", "30B", "spam", "sabotage", None), (4, "anchor", "30B", "bank", "benign", None),
    (5, "sentinel", "D", "spam", "benign", None), (6, "contrast", "30B", "spam", "sabotage", ("X", "G")),
    (7, "contrast", "30B", "spam", "benign", ("Y", "S")), (8, "development", "D", "bank", "benign", None),
    (9, "contrast", "30B", "spam", "sabotage", ("X", "S")), (10, "contrast", "30B", "spam", "benign", ("Y", "G")),
    (11, "development", "D", "spam", "sabotage", None), (12, "contrast", "30B", "spam", "benign", ("Y", "G")),
    (13, "contrast", "30B", "spam", "sabotage", ("X", "S")), (14, "development", "D", "bank", "sabotage", None),
    (15, "contrast", "30B", "spam", "benign", ("Y", "S")), (16, "contrast", "30B", "spam", "sabotage", ("X", "G")),
    (17, "sentinel", "D", "spam", "benign", None), (18, "development", "D", "bank", "benign", None))


def w1_roster():
    out = []
    for o, kind, model, pair, cond, contrast in W1_ROSTER:
        row = {"ordinal": o, "kind": kind, "model": model, "pair": pair, "condition": cond,
               "run_id": (f"W1:align-v4-w1-e{o:02d}" if kind == "anchor" else f"align-v4-w1-e{o:02d}")}
        if contrast:
            row["contrast"] = {"template": contrast[0], "arm": contrast[1], "stage": 0 if o <= 11 else 1}
        row["seed_index"] = (93 if o == 18 else 1) if model == "D" else ({"X": 16, "Y": 14}[contrast[0]] if contrast else 1)
        row["expected_episode_seed"] = seed_law_model(MODEL_TAGS[model], row["seed_index"], pair)
        out.append(row)
    return out


def write_meter(path, spans_ns, raw_minus_mono=5000, watts=30.0, period_ms=100, per_poll=10, close=True):
    """KM003C-shaped stream: 20 V, current = watts / 20 V, device ms counter wrapping at 65536."""
    start, end = spans_ns
    # KM003C rate index for the poll period (production STEP_MS {0: 500, 1: 100, 2: 20, 3: 1} ms); R23 fix:
    # this writer used rate_idx 2 (20 ms) for 100 ms polls, which a drop check reads as dropped samples.
    rate_idx = {500: 0, 100: 1, 20: 2, 1: 3}[period_ms]
    lines = [json.dumps({"k": "h", "schema": "joulewise.km003c_stream.v1", "rate_idx": rate_idx, "status": "streaming",
                         "start_raw_ns": start + raw_minus_mono, "start_mono_ns": start})]
    ua = round(watts / 20.0 * 1e6)
    t, dev = start, 0
    while t <= end:
        payload = b""
        for _ in range(per_poll):
            payload += struct.pack("<HHiiHHHH", dev % 65536, 0, 20_000_000, ua, 0, 0, 0, 0)
            last = t
            t += period_ms * 1_000_000
            dev += period_ms
        rx = last + raw_minus_mono
        lines.append(json.dumps({"k": "b", "tx": rx - 1_000_000, "rx": rx, "n": per_poll, "p": payload.hex()}))
    if close:
        lines.append(json.dumps({"k": "t", "end_raw_ns": t + raw_minus_mono, "end_mono_ns": t}))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n")


def write_series(root, windows=None, members_per_window=None, period_ns=100_000_000, n_tasks=35, seed=1, clusters=3,
                 turns=(3, 6), beta=(40.0, 0.004, 0.25, 2e-6, 1e-7), sigma=3.0, saboteur_extra=0.0,
                 w1=False, u3=True, references=True, meter=True):
    """Write [W1] + C1-C8 + T1-T3 (or ``windows``) and the series files."""
    root = Path(root)
    windows = windows or [f"C{i}" for i in range(1, 9)] + [f"T{i}" for i in range(1, 4)]
    if w1:
        windows = ["W1"] + list(windows)
    rng = random.Random(seed)
    template = FrameTemplate(n_tasks=n_tasks, seed=seed, clusters=clusters)
    series = {"schema": "joulewise.v4_recompute_input.series.v1", "windows": [],
              "h_star_grid": [128, 256, 384, 512, 768, 1024, 1536, 2048]}   # R26 (1)
    epoch_offset = EPOCH0_S * NS
    clock = 0
    next_index = {"spam": 2, "bank": 2}
    for index, wid in enumerate(windows):
        role = "W1" if wid == "W1" else ("calibration" if wid.startswith("C") else "test")
        roster = w1_roster() if wid == "W1" else window_roster(wid, role, index)
        if members_per_window is not None:
            roster = roster[:members_per_window]
        series["windows"].append({"window_id": wid, "role": role})
        w_start = clock
        identity = {}
        plan_rows = []
        for r in roster:
            n_turns = rng.randrange(turns[0], turns[1] + 1)
            identical = None
            if r["kind"] == "sentinel":
                identical, n_turns = 5, 4
            elif r["kind"] == "contrast":
                identical, n_turns = (16 if r["contrast"]["template"] == "X" else 14), 3
            if identical is not None:
                identity[r["run_id"]] = "identical"
            m = Member(r["run_id"], r["pair"], r["condition"], r["kind"], r["model"], clock, rng, n_turns,
                       beta, sigma, period_ns, template, identical_to=identical)
            if r["condition"] == "sabotage" and saboteur_extra and r["model"] == "D":
                for t in m.turns:
                    t["_energy"] += saboteur_extra
            if r["kind"] == "contrast" and r["contrast"]["arm"] == "S":
                for t in m.turns:
                    t["_energy"] += 8.0
            extra = {"identity_sha256": hashlib.sha256(
                (f"traj-{identical}" if identical is not None else r["run_id"]).encode()).hexdigest()}
            if "seed_index" not in r:
                if r["model"] == "D" and r["kind"] != "sentinel":
                    r["seed_index"] = next_index[r["pair"]]
                    next_index[r["pair"]] += 1
                else:
                    r["seed_index"] = 1
            # Producer shape (seed ruling (a)): the Episode records the seed INDEX (workload.py:722); the roster
            # carries the derived expected_episode_seed and the planned config_sha256; config.json carries the
            # member's identity and seed inputs.
            r.setdefault("expected_episode_seed", seed_law_model(MODEL_TAGS[r["model"]], r["seed_index"], r["pair"]))
            assert r["expected_episode_seed"] == seed_law_model(MODEL_TAGS[r["model"]], r["seed_index"], r["pair"])
            extra.update(seed=r["seed_index"])
            if r["model"] == "D":
                extra.update(cohort_sha256=COHORT)
            write_member(root, wid, m, epoch_offset, extra=extra)
            r["planned_config"], ksha = write_config(root / "windows" / wid / "members" / r["run_id"], r["run_id"],
                                                     r["seed_index"], r["pair"], r["condition"], r["model"], root=root)
            plan_rows.append({"ordinal": r["ordinal"], "run_id": r["run_id"].split(":", 1)[-1],
                              "config_path": r["planned_config"]["path"], "config_sha256": ksha})
            clock = m.end_ns + 60 * NS
        streams = {}
        if meter:
            write_meter(root / "windows" / wid / "meter" / "km003c-0.jsonl", (w_start - 20 * NS, clock))
            streams["km003c-0.jsonl"] = sha256_file(root / "windows" / wid / "meter" / "km003c-0.jsonl")
        terminal = {}
        # The window's committed collection_plan.json (plan_source): each member's planned kit config digest.
        ppath = root / "windows" / wid / "collection_plan.json"
        header = ({"schema_version": "joulewise.align_v4.v1", "plan_id": "align-v4"} if wid == "W1" else
                  {"schema_version": "joulewise.align_v4.series_window.v1", "plan_id": "align-v4-" + wid.lower(),
                   "window_id": wid, "series_manifest_sha256": sha256_file(ALLOCATION)})
        dump(ppath, dict(header, members=plan_rows))
        plan_ref = {"plan_source": {"path": f"windows/{wid}/collection_plan.json", "sha256": sha256_file(ppath)}}
        if role == "calibration":    # R22-2: every captured C window binds its completed-chain terminal result
            tpath = root / "windows" / wid / "terminal_result.json"
            dump(tpath, {"verdict": "GO", "chain_exit_code": 0})
            terminal = {"terminal_result_source": {"path": f"windows/{wid}/terminal_result.json",
                                                   "sha256": sha256_file(tpath)}}
        dump(root / "windows" / wid / "window.json", {
            "schema": "joulewise.v4_recompute_input.window.v1", "window_id": wid, "role": role,
            "members": roster, "adjudication": {"final": True, "excluded": {}},
            "identity": identity, "battery": {}, "meter": {"streams": streams}, "cohort_sha256": COHORT,
            **({"sentinel_ordinals": [5, 17]} if wid == "W1" else {}), **terminal, **plan_ref})
    # R24 allocation: the frozen 18-window manifest, byte for byte (fixtures/series_manifest_r24.json).
    (root / "allocation").mkdir(parents=True, exist_ok=True)
    (root / "allocation" / "series_manifest.json").write_bytes(ALLOCATION.read_bytes())
    series["allocation_source"] = {"path": "allocation/series_manifest.json", "sha256": sha256_file(ALLOCATION)}
    dump(root / "series.json", series)
    if u3:
        dump(root / "u3_bar.json", {"signed": True, "beta": 0.05, "N": 22, "f": 1.5, "r1_d_screen": 0.004,
                                    "pilot_relative_differences": [0.004, -0.006, 0.003, 0.005, -0.002, 0.001,
                                                                   -0.004]})
    if references:
        dump(root / "references.json", {"r1_replay_pair_j": [1500.0, 1510.0], "delta_slow_c": 1.0,
                                        "r1_designed_start_states": [
                                            {"designed_slow_c": 38.0, "g0_release_slow_c": 38.0, "energy_j": 1500.0},
                                            {"designed_slow_c": 40.0, "g0_release_slow_c": 40.0, "energy_j": 1501.0},
                                            {"designed_slow_c": 42.0, "g0_release_slow_c": 42.0, "energy_j": 1502.5}]})
    return root


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":  # pragma: no cover - manual sizing helper
    import sys
    t = FrameTemplate()
    b = t.fill(100_000_000, EPOCH0_S, 12345.0)
    print(len(b), math.ceil(507e6 / len(b)), file=sys.stderr)
    os._exit(0)
