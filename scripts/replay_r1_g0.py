#!/usr/bin/env python3
"""Read-only R1 G0 replay through ThermalSession.wait, on a virtual clock.

The fixture projects the selected temperatures, read brackets and status at
every recorded 1 Hz observation; other sensors and post-G0 work are omitted.
No temperature or status is interpolated on the observed span. Only the
explicit model-B continuation creates synthetic observations/status.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple.r1_runtime import gate_policy
from joulewise.align.apple.thermal_gates import NS, ThermalSession, sample_rows
from joulewise.clock import FakeClock

FIXTURE = ROOT / "tests/align/fixtures/r1_g0_20261110.json"
JOURNAL = Path("/Users/edr/night-align/r1-20261111T014106Z/night/align-r1/step_30b/"
               "runs/align-v4-r1-step-30b/outputs/align_thermal.jsonl")


def project(journal):
    """Use only the thermal interval and warmup stage timestamps of the bundle."""
    raw = journal.read_bytes()
    rows = sample_rows([json.loads(line) for line in raw.splitlines()])
    episode = json.loads((journal.parent / "align_episode.json").read_text())
    g0 = next(r for r in episode["hardware"]["thermal"]["intervals"] if r["kind"] == "G0")
    events = [json.loads(line) for line in (journal.parent.parent / "events.jsonl").read_text().splitlines()]
    stages = {r["event_type"]: r["timestamp_s"] for r in events if r.get("phase") == "warmup"}
    # Same ordinary clock as the journal: map the stage's epoch timestamp
    # using G0's own bracket, preserving the recorded timestamp precision.
    def ns(epoch):
        return g0["start_ns"] + round((epoch - g0["entry_epoch_s"]) * NS)
    warmup = ns(stages["stage_started"])
    end = g0["start_ns"] + 600 * NS  # the as-run cap, not the later teardown span
    sensors = episode["hardware"]["thermal"]["policy"]["sensors"]
    keys = [sensors["s_fast"], sensors["s_slow"]]
    selected = [r for r in rows if warmup - 70 * NS <= r["monotonic_ns"] <= end]
    # 70 = the 60 s capture plus the 10 s clean-idle offset in ruling §10.
    data = [[r["monotonic_ns"], r["finished"]["monotonic_after_ns"], r["epoch_ns"],
             *[r["sensors"][k] for k in keys], r["status"].get("os_level"),
             r["status"].get("pm_state"), r["status"].get("pm_observed_ns")]
            for r in selected]
    return {"journal_sha256": hashlib.sha256(raw).hexdigest(), "source": str(journal),
            "columns": ["monotonic_ns", "finished_ns", "epoch_ns", *keys,
                        "os_level", "pm_state", "pm_observed_ns"],
            "sensors": sensors, "warmup_ns": warmup, "warmup_end_ns": ns(stages["stage_completed"]),
            "g0_ns": g0["start_ns"], "record_end_ns": end, "recorded_wait_s": g0["duration_s"],
            "soak_reference": g0["reference"], "rows": data}


def observations(data):
    fast, slow = (data["sensors"][k] for k in ("s_fast", "s_slow"))
    return [{"kind": "sample", "monotonic_ns": t, "epoch_ns": epoch,
             "started": {"monotonic_before_ns": t, "monotonic_after_ns": t},
             "finished": {"monotonic_after_ns": end}, "sensors": {fast: f, slow: s}, "errors": {},
             "status": {"os_level": os_level, "pm_state": state, "pm_observed_ns": pm}}
            for t, end, epoch, f, s, os_level, state, pm in data["rows"]]


class EndOfRecord(Exception):
    pass


class ReplayClock(FakeClock):
    def __init__(self, now_ns, end_ns):
        super().__init__(now_ns / NS)
        self.end_ns = end_ns

    def sleep(self, seconds):
        if round((self.now() + seconds) * NS) > self.end_ns:
            raise EndOfRecord
        super().sleep(seconds)


class ReplaySession(ThermalSession):
    """Substitute journal delivery only; capture and wait are production code."""
    def __init__(self, data, rows, *, cap_s, slow_band, end_ns):
        self.observations = rows
        clock = ReplayClock(data["warmup_ns"], end_ns)
        policy = gate_policy(data["sensors"], {"delta_fast_c": 1.0, "delta_slow_c": slow_band},
                             turn_cap_s=300, chunk_tokens=256, heavy=False, per_turn=False, g0_cap_s=cap_s)
        super().__init__(policy, clock, reader=SimpleNamespace())  # no hardware reader
        self.sidecar.counter = SimpleNamespace(start_ns=rows[0]["monotonic_ns"])
        self.sidecar.session = "read-only-replay"

    @property
    def rows(self):
        now = round(self.clock.now() * NS)
        return [r for r in self.observations if r["finished"]["monotonic_after_ns"] <= now]

    def sample(self):
        # wait() polls the real recorded timestamps; no duplicate samples.
        self.sidecar._seq += 1


def own_idle(data, rows):
    # Ruling §10: clean idle is 60 s ending 10 s before warmup entry.
    return {role: median(r["sensors"][data["sensors"][key]] for r in rows
                        if data["warmup_ns"] - 70 * NS <= r["monotonic_ns"] < data["warmup_ns"] - 10 * NS)
            for role, key in (("fast_c", "s_fast"), ("slow_c", "s_slow"))}


def model_b(data, rows):
    """OLS amplitudes at fixed own-idle level, tau=70/500 s (ruling §3.2)."""
    level = own_idle(data, rows)
    fit = [r for r in rows if 60 <= (r["monotonic_ns"] - data["warmup_end_ns"]) / NS
           and r["monotonic_ns"] <= data["record_end_ns"]]
    x = [(math.exp(-(r["monotonic_ns"] - data["warmup_end_ns"]) / NS / 70),
          math.exp(-(r["monotonic_ns"] - data["warmup_end_ns"]) / NS / 500)) for r in fit]
    aa = math.fsum(a*a for a, b in x)
    ab = math.fsum(a*b for a, b in x)
    bb = math.fsum(b*b for a, b in x)
    models = {}
    for role, key in (("fast_c", "s_fast"), ("slow_c", "s_slow")):
        y = [r["sensors"][data["sensors"][key]] - level[role] for r in fit]
        ay = math.fsum(a*v for (a, b), v in zip(x, y))
        by = math.fsum(b*v for (a, b), v in zip(x, y))
        a, b = (ay*bb - by*ab)/(aa*bb-ab*ab), (by*aa-ay*ab)/(aa*bb-ab*ab)
        if a < 0:  # non-negative amplitudes, as fitted in ruling §10
            a, b = 0.0, max(0.0, by/bb)
        elif b < 0:
            a, b = max(0.0, ay/aa), 0.0
        rmse = math.sqrt(math.fsum((v-a*u-b*w)**2 for (u, w), v in zip(x, y))/len(y))
        models[role] = {"level_c": level[role], "a_c": a, "b_c": b, "rmse_c": rmse}
    return models


def continuation(data, rows, models):
    rows = list(rows)
    last = rows[-1]
    # Continue the observed 1 Hz cadence. Both source statuses are explicitly
    # synthetic Nominal, not inferred from the last recorded PM observation.
    for t in range(last["monotonic_ns"] + NS, data["g0_ns"] + 1200 * NS + NS, NS):
        elapsed = (t - data["warmup_end_ns"])/NS
        values = {data["sensors"][key]: m["level_c"] + m["a_c"]*math.exp(-elapsed/70)
                  + m["b_c"]*math.exp(-elapsed/500)
                  for role, key in (("fast_c", "s_fast"), ("slow_c", "s_slow")) for m in [models[role]]}
        rows.append({**last, "monotonic_ns": t, "finished": {"monotonic_after_ns": t},
                     "sensors": values, "status": {"os_level": 0, "pm_state": "Nominal", "pm_observed_ns": t}})
    return rows


def replay(data):
    rows = observations(data)
    models = model_b(data, rows)
    result = {"journal_sha256": data["journal_sha256"], "model_b": models,
              "recorded_wait_s": data["recorded_wait_s"]}
    for label, cap, band, extend in (("old", 600, 1.0, False), ("new_observed", 1200, 1.5, False),
                                     ("new_model_b", 1200, 1.5, True)):
        end = data["g0_ns"] + cap*NS if extend else data["record_end_ns"]
        session = ReplaySession(data, continuation(data, rows, models) if extend else rows,
                                cap_s=cap, slow_band=band, end_ns=end)
        session.capture_reference("step-30b")
        result["R_op"] = dict(session.reference)
        if label == "old":
            session.reference = data["soak_reference"]
        session.clock._now = data["g0_ns"]/NS
        try:
            row = session.wait("G0")
            result[label] = {k: row[k] for k in ("outcome", "duration_s", "release", "slope_c_per_min")}
        except EndOfRecord:
            result[label] = {"outcome": "record_ended_unreleased", "duration_s": 600}
        result[label]["cap_s"] = cap
    result["operating_minus_soak_c"] = {k: result["R_op"][k] - data["soak_reference"][k]
                                         for k in ("fast_c", "slow_c")}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal", type=Path, help="real journal, read only; default uses the embedded fixture")
    args = parser.parse_args()
    data = project(args.journal) if args.journal else json.loads(FIXTURE.read_text())
    result = replay(data)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if (result["old"]["outcome"] == "timeout"
                 and result["new_observed"]["outcome"] == "record_ended_unreleased"
                 and result["new_model_b"]["outcome"] == "released"
                 and 600 < result["new_model_b"]["duration_s"] < 1200) else 1


if __name__ == "__main__":
    raise SystemExit(main())
