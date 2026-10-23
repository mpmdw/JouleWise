#!/usr/bin/env python3
"""Synthetic BYTES archives for the twin's own tests: real-shaped block-6 run records for a world
where bytes is the truth.  (The agreement test uses the analysis lane's generator, campaign.py.)

Writes, under --out:
  exports/<pack>/<session>.runs.csv and .session.json   (as joulewise/b6/export_runs.py writes them,
                                                        energies multiplied by the hidden offsets;
                                                        <pack> is the registered per-pass sub-pack
                                                        bytes-sN-pK, Addendum 5 item 2, which is the
                                                        twin's clock-free pass identity)
  keys/pack.json, keys/config-<sha16>.json              (the blinding directory, factor per key)
  archives/<session>/derived/{b6-acceptance,roster}.json, withheld/{spans,b6-neg8}.json,
                     withheld/reductions/<run>.summary_metrics.rereduced.json,
                     sources/claim-runs/<run>/{config,metadata,status}.json + events.jsonl,
                     sources/night-custody/hazards/meter/stream-001.jsonl   (KM003C stream)
  bytes_manifest.json                                   (the R4 manifest shape the twin reads)
  truth.json                                            (the world's parameters, for tests only)

The world: decode energy per step e = S_BYTES x b (b = W + KV, GB), so P_rails = S_BYTES x BW
exactly; DC input P = DC_BASE + DC_GAIN x P_rails + REST_PER_RESIDENT_W_PER_GB x R; rest = DC - rails.  Run-to-run noise is
multiplicative and small; every quad carries a slow drift that its ABBA order cancels.
No model inference and no measurement: every number here is made up and labelled synthetic.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import struct
from datetime import datetime, timezone
from pathlib import Path

GB = 1e9
DECODE_STEPS = 512   # Addendum 5 item 4
S_BYTES = 0.09          # J per GB read (the truth)
DC_BASE = 12.0          # W
DC_GAIN = 1.25
REST_PER_RESIDENT_W_PER_GB = 0.03   # DRAM standby in the rest boundary, so rest is not a multiple of rails
RAILS_IDLE_W = 0.5
DC_IDLE_W = 12.5
EDGE_BOUND_S = 0.02     # synthetic g for the first-kind bound
DRIFT_POWER_BOUND_W = 0.05
NOISE = 0.002
PACK_ID = "bytes"
REFERENCE_KEY = "neg8_reference"
PHASES = ("tokenize", "generation_setup", "prefill", "decode")
COLUMNS = (
    "pack_id", "session_id", "attempt", "run_id", "stage_id", "role", "order_index",
    "cell_ids", "strata", "unit_ids", "abba_block_id", "abba_label", "config_key",
    "model_name", "workload_name", "status", "excluded", "exclusion_codes", "flag_codes", "non_claim",
    "phase_tokenize_j", "phase_generation_setup_j", "phase_prefill_j", "phase_decode_j",
    "gross_energy_j", "idle_subtracted_energy_j", "energy_request_j",
    "bound_E_clock_anchor_shift_bound_j", "bound_E_drift_bound_j",
    "bound_E_interpolation_edge_bound_j", "bound_E_interpolation_joint_edge_bound_j",
    "idle_power_w", "idle_variance_of_mean_w2",
    "prompt_tokens", "emitted_tokens", "requested_output_tokens",
    "dur_tokenize_s", "dur_generation_setup_s", "dur_prefill_s", "dur_decode_s",
    "idle_baseline_s", "ttft_s", "decode_latency_s", "run_start_utc",
)

# Pilot-shaped roster: W (GB, stored weights read per step), KV (GB), R (GB), decode and prefill tok/s.
MODELS = {
    "Qwen3-1.7B-4bit": (0.968, 0.26, 0.968, 215.6, 3630.0),
    "Qwen3-4B-4bit": (2.263, 0.34, 2.263, 114.0, 1349.0),
    "Qwen3-8B-4bit": (4.258, 0.34, 4.608, 66.4, 666.0),
    "Qwen3-14B-4bit": (7.870, 0.38, 8.308, 40.2, 391.0),
    "Qwen3-32B-4bit": (17.992, 0.60, 18.430, 18.1, 163.0),
    "Llama-3.3-70B-Instruct-4bit": (39.097, 0.75, 39.688, 8.8, 75.0),
    "Qwen3-8B-8bit": (8.520, 0.34, 9.215, 38.0, 420.0),
    "Qwen3-30B-A3B-4bit": (1.711, 0.23, 17.175, 92.1, 1440.0),
    "Qwen3-Next-80B-A3B-Instruct-4bit": (2.032, 0.13, 44.844, 64.0, 1082.0),
    "Qwen3.5-122B-A10B-4bit": (5.070, 0.19, 68.691, 42.6, 417.0),
}
SUBPACKS = [("s1", ["Qwen3-1.7B-4bit", "Qwen3-4B-4bit"]), ("s2", ["Qwen3-8B-4bit", "Qwen3-30B-A3B-4bit"]),
            ("s3", ["Qwen3-14B-4bit", "Qwen3-Next-80B-A3B-Instruct-4bit"]),
            ("s4", ["Qwen3-32B-4bit", "Qwen3-8B-8bit"]), ("s5", ["Llama-3.3-70B-Instruct-4bit"]),
            ("s6", ["Qwen3.5-122B-A10B-4bit"])]
REFERENCE = {"name": "Qwen2.5-1.5B-Instruct-4bit", "prompt": 1024, "out": 256, "decode_tps": 150.0,
             "prefill_tps": 2500.0, "P_rails": 15.0}
SAMPLE = struct.Struct("<HHiiHHHH")
RATE_IDX = 0            # 500 ms device step: small streams for long synthetic sessions
STEP_MS = 500
POLL_NS = 2_000_000_000
RAW_MINUS_MONO_NS = 5_000_000_000
EPOCH0 = 1_791_936_000.0
MONO0 = 1000.0


def canon(name: str) -> str:
    return name.lower().replace("_", "-")


def config_filename(key: str) -> str:
    return "config-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".json"


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


class World:
    def __init__(self, seed: int, defects: bool, passes: int, models, refuse_pass=None):
        self.rng = random.Random(seed)
        self.defects = defects
        self.passes = passes
        # refuse_pass: (model name, pass index) whose repeats are mostly excluded, so that pass's
        # cell refuses below the 5-unit minimum (Addendum 7 D9 a/c exercise).
        self.refuse_pass = refuse_pass
        self.models = {name: MODELS[name] for name in models}
        self.factors = {"pack": self.rng.uniform(0.8, 1.25), "config": {}}

    def factor(self, key: str) -> float:
        if key not in self.factors["config"]:
            self.factors["config"][key] = self.rng.uniform(0.97, 1.03)
        return self.factors["pack"] * self.factors["config"][key]

    def decode_power(self, name: str, pass_index: int = 1) -> tuple[float, float]:
        """Rails power and seconds per step; pass 2 runs 3 % slower (Addendum 7 item 12: unequal
        pass durations), energy per step unchanged, so the pass-mean P is mean E / mean T."""
        w, kv, _r, tps, _ = self.models[name]
        b = w + kv
        tau = 1.0 / tps * (1.03 if pass_index == 2 else 1.0)
        e = S_BYTES * b
        return e / tau, tau   # rails W, s per step


def scaled_sample(watts: float, rng) -> tuple[int, int]:
    """Vbus 28 V EPR contract; current from power; returned in uV and uA."""
    vbus = 28.0 + rng.gauss(0, 0.01)
    return int(round(vbus * 1e6)), int(round(watts / vbus * 1e6))


class Session:
    def __init__(self, world: World, session_id: str, pass_index: int, order: list[str], start_epoch: float,
                 pack_id: str = PACK_ID):
        self.world, self.session_id, self.pass_index, self.order = world, session_id, pass_index, order
        self.pack_id = pack_id      # the registered per-pass sub-pack id (bytes-sN-pK)
        self.epoch = start_epoch
        self.mono = MONO0 + (start_epoch - EPOCH0)
        self.rows, self.bundles, self.segments, self.spans, self.roster = [], {}, [], {}, []
        self.excluding, self.flags = [], []
        self.order_index = 0
        self.stage_counter = 0

    # -- time bookkeeping ------------------------------------------------------------------
    def advance(self, seconds: float, dc_watts: float) -> tuple[float, float]:
        start = self.mono
        self.segments.append((int(start * 1e9), int((start + seconds) * 1e9), dc_watts))
        self.mono += seconds
        self.epoch += seconds
        return start, self.mono

    # -- one run ----------------------------------------------------------------------------
    def run(self, run_id, stage_id, role, model_name, config_key, *, rails_w, tau, prompt, out,
            prefill_tps, units, abba=None, drift_w=0.0, status="succeeded", excluded_by=None, flags=(),
            resident_gb=0.0):
        rng = self.world.rng
        noise = 1.0 + rng.gauss(0, NOISE)
        epoch_start = self.epoch
        events = []

        def ev(kind, phase, meta):
            events.append({"timestamp_s": self.epoch, "event_type": kind, "phase": phase, "metadata": meta})
        ev("run_started", "run", {"run_id": run_id})
        self.advance(0.2, DC_IDLE_W)
        for stage in ("validate", "prepare"):
            ev("stage_started", stage, {})
            self.advance(0.05, DC_IDLE_W)
            ev("stage_completed", stage, {})
        ev("stage_started", "idle_baseline", {"monotonic_ns": int(self.mono * 1e9)})
        idle_start, idle_end = self.advance(10.0, DC_IDLE_W + rng.gauss(0, 0.01))
        ev("stage_completed", "idle_baseline", {"power_w_mean": RAILS_IDLE_W, "duration_s": idle_end - idle_start})
        ev("stage_started", "warmup", {})
        self.advance(0.5, DC_BASE + DC_GAIN * rails_w + REST_PER_RESIDENT_W_PER_GB * resident_gb)
        ev("stage_completed", "warmup", {"warmup_runs": 1})
        ev("stage_started", "measured_run", {})
        sampling_started = (self.epoch, self.mono)
        ev("sampling_started", "measured_run", {})
        durations = {"tokenize": 0.01, "generation_setup": 0.02, "prefill": prompt / prefill_tps,
                     "decode": DECODE_STEPS * tau * (1.0 + rng.gauss(0, 0.001))}
        rails = {"tokenize": 2.0, "generation_setup": 2.0, "prefill": rails_w * 1.3, "decode": rails_w * noise + drift_w}
        energies, request_start = {}, self.mono
        for phase in PHASES:
            ev("phase_start", phase, {})
            p_dc = DC_BASE + DC_GAIN * rails[phase] + REST_PER_RESIDENT_W_PER_GB * resident_gb
            self.advance(durations[phase], p_dc)
            meta = {"prompt_tokens": prompt} if phase == "tokenize" else {
                "output_tokens": out, "emitted_tokens": out, "requested_output_tokens": out} if phase == "decode" else {}
            ev("phase_end", phase, meta)
            energies[phase] = rails[phase] * durations[phase]
        request_end = self.mono
        ev("sampling_stopped", "measured_run", {})
        ev("stage_completed", "measured_run", {})
        for stage in ("idle_drift_sentinel", "cleanup", "reduce"):
            ev("stage_started", stage, {})
            self.advance(0.7, DC_IDLE_W)
            ev("stage_completed", stage, {})
        ev("run_finalized", "run", {})
        self.advance(1.0, DC_IDLE_W)   # the settle before the next member
        request_s = request_end - request_start
        gross = math.fsum(energies.values())
        bounds = {"E_clock_anchor_shift_bound_j": EDGE_BOUND_S * (rails["decode"] + rails["prefill"]),
                  "E_drift_bound_j": DRIFT_POWER_BOUND_W * request_s,
                  "E_interpolation_edge_bound_j": 0.0, "E_interpolation_joint_edge_bound_j": 0.0}
        summary = {"phase_energy_j": dict(energies), "gross_energy_j": gross,
                   "idle_subtracted_energy_j": gross - RAILS_IDLE_W * request_s,
                   "energy_request_j": gross - RAILS_IDLE_W * request_s,
                   "energy_bound_terms_j": bounds,
                   "idle_baseline": {"duration_s": idle_end - idle_start, "power_w_mean": RAILS_IDLE_W,
                                     "sample_count": 160, "telemetry_backend": "powermetrics"},
                   "idle_mean_uncertainty": {"governed_variance_of_mean_w2": 0.0004},
                   "ttft_s": durations["tokenize"] + durations["generation_setup"] + durations["prefill"],
                   "decode_latency_s": durations["decode"], "status": status}
        bundle = {"events": events, "metadata": {
            "run_id": run_id, "status": {"state": status}, "schema": "joulewise.metadata.synthetic.v1",
            "uncertainty_evidence": {"clock_anchor": {"method": "synthetic", "clock_stamps": {
                "sampling_started": {"epoch_s": sampling_started[0], "monotonic_before_s": sampling_started[1],
                                     "monotonic_after_s": sampling_started[1] + 1e-6}}}}},
            "config": {"run_id": run_id, "model": {"name": model_name, "family": "synthetic"},
                       "workload_profile": {"name": "bytes_fixed_prompt_v1", "output_tokens": out, "warmup_runs": 1},
                       "run_metadata": {"tags": ["df-condition=" + config_key] + (
                           ["calibration-abba-block-id=" + abba[0], "calibration-abba-label=" + abba[1][0],
                            "calibration-abba-sequence-index=" + str(abba[2])] if abba else [])}},
            "summary": summary}
        self.bundles[run_id] = bundle
        self.spans[run_id] = {"monotonic_ns": [int(idle_start * 1e9), int(request_end * 1e9)],
                              "request_monotonic_ns": [int(request_start * 1e9), int(request_end * 1e9)]}
        self.roster.append({"run_id": run_id, "stage_id": stage_id, "role": role, "units": units,
                            "config_key": config_key})
        codes = []
        if status != "succeeded":
            codes.append("member.status_not_succeeded")
        if excluded_by:
            codes.append(excluded_by)
        for code in codes:
            self.excluding.append({"scope": "member", "run_id": run_id, "code": code, "why": code})
        for code in list(flags) + codes:
            self.flags.append({"code": code, "scope": {"run_id": run_id, "stage_id": stage_id}})
        row = {"pack_id": self.pack_id, "session_id": self.session_id, "attempt": 1, "run_id": run_id,
               "stage_id": stage_id, "role": role, "order_index": self.order_index,
               "cell_ids": ";".join(u["cell_id"] for u in units), "strata": ";".join(u["stratum"] for u in units),
               "unit_ids": ";".join(str(u["unit_id"]) for u in units),
               "abba_block_id": abba[0] if abba else None, "abba_label": abba[1][0] if abba else None,
               "config_key": config_key, "model_name": model_name, "workload_name": "bytes_fixed_prompt_v1",
               "status": status, "excluded": bool(codes), "exclusion_codes": ";".join(sorted(codes)),
               "flag_codes": ";".join(sorted(set(list(flags) + codes))), "non_claim": False,
               "prompt_tokens": prompt, "emitted_tokens": out, "requested_output_tokens": out,
               "idle_baseline_s": idle_end - idle_start, "ttft_s": summary["ttft_s"],
               "decode_latency_s": summary["decode_latency_s"],
               "run_start_utc": datetime.fromtimestamp(epoch_start, timezone.utc).isoformat()}
        for phase in PHASES:
            row["dur_" + phase + "_s"] = durations[phase]
        if status == "succeeded":
            for phase in PHASES:
                row["phase_" + phase + "_j"] = energies[phase]
            row.update({k: summary[k] for k in ("gross_energy_j", "idle_subtracted_energy_j", "energy_request_j")})
            for term, value in bounds.items():
                row["bound_" + term] = value
            row["idle_power_w"] = RAILS_IDLE_W
            row["idle_variance_of_mean_w2"] = 0.0004
        self.rows.append(row)
        self.order_index += 1

    # -- module and reference layout ---------------------------------------------------------
    def reference(self, slot, index):
        rails = REFERENCE["P_rails"] * (1.0 + self.world.rng.gauss(0, 0.004))
        self.run(f"{self.session_id}-ref-{slot}-{index:02d}", f"{self.session_id}-reference-{slot}",
                             slot, REFERENCE["name"], REFERENCE_KEY, rails_w=rails, tau=1.0 / REFERENCE["decode_tps"],
                             prompt=REFERENCE["prompt"], out=REFERENCE["out"], prefill_tps=REFERENCE["prefill_tps"],
                             units=[])

    def module(self, model_name):
        rails_w, tau = self.world.decode_power(model_name, self.pass_index)
        _w, _kv, resident_gb, _tps, prefill_tps = self.world.models[model_name]
        key = "bytes-decode-" + canon(model_name)
        cell = "bytes-decode-" + canon(model_name)
        module = f"{self.session_id}-m-{canon(model_name)}"
        defects = self.world.defects and self.pass_index == 1 and model_name in ("Qwen3-4B-4bit", "Qwen3-30B-A3B-4bit")
        refuse = self.world.refuse_pass == (model_name, self.pass_index)
        for i in range(1, 11):
            run_id = f"{module}-abs-r{i:02d}"
            kwargs = {}
            if defects and i == 6:
                kwargs["excluded_by"] = "thermal.os_level_nonzero"
            if defects and i == 8:
                kwargs["excluded_by"] = "member.cooldown_cap_hit"   # NUMBER class, valid record (D5)
            if defects and i == 3:
                kwargs["flags"] = ("battery.assist",)
            if refuse and i <= 6:
                kwargs["excluded_by"] = "contention.request_overlap"   # 4 kept repeats: the cell refuses
            self.run(run_id, module + "-absolute", "science", model_name, key, rails_w=rails_w, tau=tau,
                                 prompt=2048, out=512, prefill_tps=prefill_tps,
                                 units=[{"cell_id": cell, "stratum": "repeat", "unit_id": run_id}],
                                 resident_gb=resident_gb, **kwargs)
        for q in range(1, 11):
            block = f"{module}-b{q:02d}"
            drift = self.world.rng.gauss(0, 0.02) * rails_w / 100.0
            for seq, label in enumerate(("A1", "B1", "B2", "A2"), 1):
                run_id = f"{block}-{label.lower()}"
                kwargs = {}
                if defects and q == 5 and label == "B2":
                    kwargs["status"] = "failed"
                if defects and q == 2 and label == "A1":
                    kwargs["excluded_by"] = "battery.member_span"   # a hazard exclusion with a valid record
                self.run(run_id, module + ("-quads-01-05" if q <= 5 else "-quads-06-10"), "science",
                                     model_name, key, rails_w=rails_w, tau=tau, prompt=2048, out=512,
                                     prefill_tps=prefill_tps, drift_w=drift * seq,
                                     units=[{"cell_id": cell, "stratum": "quad", "unit_id": block}],
                                     abba=(block, label, seq), resident_gb=resident_gb, **kwargs)

    def build(self):
        for i in range(1, 19):
            self.reference("corpus", i)
        for i in range(1, 4):
            self.reference("start", i)
        for index, model_name in enumerate(self.order):
            self.module(model_name)
            if index < len(self.order) - 1:
                self.reference("midpoint", 1)
        for i in range(1, 4):
            self.reference("end", i)
        return self

    # -- writers -----------------------------------------------------------------------------
    def write(self, out: Path):
        world = self.world
        export_dir = out / "exports" / self.pack_id
        export_dir.mkdir(parents=True, exist_ok=True)
        rows = []
        for row in self.rows:
            f = world.factor(row["config_key"])
            blinded = dict(row)
            for key, value in row.items():
                if isinstance(value, float):
                    if key.endswith(("_j2", "_w2")):
                        blinded[key] = value * f * f
                    elif key.endswith(("_j", "_w")):
                        blinded[key] = value * f
            rows.append({k: ("" if blinded.get(k) is None else blinded[k]) for k in COLUMNS})
        with (export_dir / (self.session_id + ".runs.csv")).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        write_json(export_dir / (self.session_id + ".session.json"), {
            "schema": "joulewise.b6_export_session.v1", "pack_id": self.pack_id, "session_id": self.session_id,
            "verdict": "ACCEPT", "counting": True, "flag_counts": {}, "operative_bound_s": "0.046",
            "neg8": {"verdict": "passed", "survivors": {"start": 3, "midpoint": len(self.order) - 1, "end": 3},
                     "corpus_clean_n": 12, "reason": None},
            "non_claim": False, "blinding": {"applied": True, "key_dir": "../../keys"}})
        archive = out / "archives" / self.session_id
        write_json(archive / "derived/b6-acceptance.json", {
            "schema": "joulewise.b6_acceptance.v1", "mode": "archive", "pack_id": self.pack_id,
            "session_id": self.session_id, "verdict": "ACCEPT", "counting": True, "physics_stop": False,
            "excluding": self.excluding, "emitted_flags": [], "flag_counts": {},
            "calibration": {"operative_bound_s": "0.046"}, "neg8": {"verdict": "passed"}})
        write_json(archive / "derived/roster.json", {"pack_id": self.pack_id, "attempt": 1, "members": self.roster,
                                                      "cells": sorted({u["cell_id"] for m in self.roster for u in m["units"]})})
        (archive / "derived").mkdir(parents=True, exist_ok=True)
        (archive / "derived/flags.jsonl").write_text("".join(json.dumps(f) + "\n" for f in self.flags), encoding="utf-8")
        write_json(archive / "withheld/spans.json", {"spans": self.spans})
        for run_id, bundle in self.bundles.items():
            base = archive / "sources/claim-runs" / run_id
            base.mkdir(parents=True, exist_ok=True)
            (base / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in bundle["events"]), encoding="utf-8")
            write_json(base / "metadata.json", bundle["metadata"])
            write_json(base / "config.json", bundle["config"])
            write_json(base / "status.json", {"status": {"state": bundle["metadata"]["status"]["state"]}})
            write_json(archive / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json"), bundle["summary"])
        self.write_stream(archive / "sources/night-custody/hazards/meter/stream-001.jsonl")

    def write_stream(self, path: Path):
        rng = self.world.rng
        path.parent.mkdir(parents=True, exist_ok=True)
        start_mono = int(self.segments[0][0] - 5_000_000_000)
        end_mono = int(self.segments[-1][1] + 5_000_000_000)
        lines = [json.dumps({"k": "h", "schema": "joulewise.km003c_stream.v1", "model": "KM003C", "status": "streaming",
                             "rate_idx": RATE_IDX, "sps": 1000 // STEP_MS, "poll_s": POLL_NS / 1e9,
                             "smc_keys": ["B0AC", "B0AV"], "start_raw_ns": start_mono + RAW_MINUS_MONO_NS,
                             "start_mono_ns": start_mono, "serial": "synthetic"})]
        bounds = [s[0] for s in self.segments]
        import bisect as _bisect

        def power_at(mono_ns):
            i = _bisect.bisect_right(bounds, mono_ns) - 1
            if i < 0 or mono_ns >= self.segments[i][1]:
                return DC_IDLE_W
            return self.segments[i][2]
        seq, dev_ms = 0, 0
        t_mono = start_mono
        pending = []
        polls = 0
        last_rx = start_mono
        while t_mono < end_mono:
            v_uv, i_ua = scaled_sample(power_at(t_mono) + rng.gauss(0, 0.02), rng)
            pending.append(SAMPLE.pack(seq & 0xFFFF, 0, v_uv, i_ua, 0, 0, 0, 0))
            newest_mono = t_mono
            seq += STEP_MS
            dev_ms += STEP_MS
            t_mono += STEP_MS * 1_000_000
            if t_mono - last_rx >= POLL_NS:
                # The poll drains the meter's queue just after its newest sample was digitised
                # (the parser's earliest-arrival assumption): request 1 ms later, answer 0.6 ms after.
                # Non-zero, varying host latency (Addendum 7 item 12): the request leaves 1 to 3.5 ms
                # after the newest sample, the answer 0.6 ms later; the clock fit sees the spread.
                tx = newest_mono + RAW_MINUS_MONO_NS + 1_000_000 + int(rng.uniform(0, 2_500_000))
                rx = tx + 600_000
                lines.append(json.dumps({"k": "b", "tx": tx, "rx": rx, "n": len(pending), "p": b"".join(pending).hex(),
                                         "smc": {"B0AC": 0, "B0AV": 12154}}))
                pending, last_rx, polls = [], t_mono, polls + 1
        lines.append(json.dumps({"k": "t", "polls": polls, "stop_reason": "duration",
                                 "end_raw_ns": t_mono + RAW_MINUS_MONO_NS, "end_mono_ns": t_mono}))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(out: Path, *, seed=1, passes=1, defects=True, models=None, refuse_pass=None):
    out = Path(out)
    names = list(models or MODELS)
    world = World(seed, defects, passes, names, refuse_pass)
    epoch = EPOCH0
    sessions = []
    for pass_index in range(1, passes + 1):
        subpacks = [(sid, [m for m in order if m in world.models]) for sid, order in SUBPACKS]
        subpacks = [(sid, order) for sid, order in subpacks if order]
        if pass_index % 2 == 0:
            subpacks = [(sid, list(reversed(order))) for sid, order in reversed(subpacks)]
        for sid, order in subpacks:
            session = Session(world, f"p{pass_index}-{sid}", pass_index, order, epoch,
                              pack_id=f"{PACK_ID}-{sid}-p{pass_index}").build()
            session.write(out)
            epoch = session.epoch + 3600.0
            sessions.append(session.session_id)
    keys = out / "keys"
    write_json(keys / "pack.json", {"pack_id": PACK_ID, "factor": world.factors["pack"]})
    for key, value in world.factors["config"].items():
        write_json(keys / config_filename(key), {"key": key, "factor": value})
    write_json(out / "bytes_manifest.json", {
        "schema": "joulewise.bytes_manifest.synthetic.v1", "note": "synthetic; every number is made up",
        "models": {name: {"revision": "synthetic", "W_bytes": w * GB, "KV_bytes": kv * GB, "R_bytes": r * GB,
                          "tokenizer": "synthetic", "tied_embeddings": False,
                          # the public configuration identity of the model's science rows (the key the
                          # export sidecar's withheld digests name; lead ruling 2026-10-20 item 1)
                          "config_key": "bytes-decode-" + canon(name)}
                   for name, (w, kv, r, _tps, _p) in world.models.items()}})
    truth = {"S_BYTES_j_per_GB": S_BYTES, "DC_BASE_w": DC_BASE, "DC_GAIN": DC_GAIN, "RAILS_IDLE_W": RAILS_IDLE_W,
             "refuse_pass": list(refuse_pass) if refuse_pass else None, "pass2_tau_factor": 1.03,
             "REST_PER_RESIDENT_W_PER_GB": REST_PER_RESIDENT_W_PER_GB,
             "DC_IDLE_W": DC_IDLE_W, "sessions": sessions, "factors": world.factors,
             "models": {name: {"b_GB": w + kv, "R_GB": r, "tau_s": 1.0 / tps, "P_rails_w": world.decode_power(name)[0]}
                        for name, (w, kv, r, tps, _p) in world.models.items()}}
    write_json(out / "truth.json", truth)
    return truth


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--passes", type=int, default=1)
    parser.add_argument("--no-defects", action="store_true")
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--refuse-pass", nargs=2, metavar=("MODEL", "PASS"), default=None)
    args = parser.parse_args(argv)
    refuse = (args.refuse_pass[0], int(args.refuse_pass[1])) if args.refuse_pass else None
    truth = generate(args.out, seed=args.seed, passes=args.passes, defects=not args.no_defects, models=args.models,
                     refuse_pass=refuse)
    print(json.dumps({"out": str(args.out), "sessions": truth["sessions"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
