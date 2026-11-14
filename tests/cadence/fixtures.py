"""Synthetic campaign kits and queues for the cadence tests. No real kit, ruling or custody."""
from __future__ import annotations

import copy
import hashlib
import json

from joulewise.cadence import kit as kitmod

RUNNER = "scripts/cadence_legs_runner.py"
FIT = "joulewise/cadence_fit.py"
COMMIT = "a" * 40


def make_kit(n_legs=6, legs_per_span=3, **overrides):
    law = {"method": "sha256-v1", "master_seed": 20261113, "n_legs": n_legs, "bands": ["cool", "mid", "warm"]}
    defaults = {"prefill_tokens": 19500, "decode_tokens": 4096}
    kit = {
        "schema": kitmod.SCHEMA,
        "campaign_id": "conditionless-test",
        "title": "Synthetic conditionless campaign",
        "ruling": {"id": "RL-999", "authorizes_spans": True},
        "frozen": {"commit": COMMIT, "paths": {RUNNER: "1" * 64, FIT: "2" * 64}},
        "runner": {"kind": "cadence-legs-v1", "entry": RUNNER, "stage_journal": "chain-stages.jsonl"},
        "model": "qwen3.8-27b",
        "leg_defaults": defaults,
        "seed_law": law,
        "legs": kitmod.generate_legs("conditionless-test", law, defaults),
        "inclusion_rules": [{"id": "g0_released", "text": "A leg counts when its G0 released in band."}],
        "stop_rules": {"instrument_fault": True, "refusal": True, "contaminated_redos_max": 3,
                       "contaminated_redos_scope": "span", "band_unreachable_max": 2,
                       "band_unreachable_scope": "span", "leg_time_factor": 1.5},
        "span_template": {"timezone": "America/Los_Angeles", "t0_local": "13:20", "end_by_local": "11:30",
                          "legs_per_span": legs_per_span, "soak_s": 1950, "fixed_overhead_s": 3600,
                          "leg_budget_s": 1500, "leg_worst_case_s": 2400, "redo_quota": 2},
        "checklist": [{"id": k, "kind": k, **({"args": {"min_gb": 40}} if k == "disk_free_gb" else {})}
                      for k in kitmod.CHECK_KINDS],
        "looks": [{"look_id": "look1", "after_legs": n_legs, "fit": {"path": FIT}}],
        "desk": {"adapter": "leg-summary-v1"},
    }
    for k, v in overrides.items():
        kit[k] = v
    return kit


def kit_bytes(kit):
    raw = json.dumps(kit, indent=1, sort_keys=True).encode()
    return raw, hashlib.sha256(raw).hexdigest()


def make_queue(kit, sha, path="configs/campaigns/conditionless-test/campaign_kit.json", spans=None):
    legs = [leg["leg_id"] for leg in kit["legs"]]
    per = kit["span_template"]["legs_per_span"]
    spans = spans or [
        {"seq": i + 1, "span_id": f"ct-s{i + 1:02d}", "block_id": "ct-dev", "kit": {"path": path, "sha256": sha},
         "legs": legs[i * per:(i + 1) * per], "attempt": 1, "not_before": "2026-11-15"}
        for i in range((len(legs) + per - 1) // per)]
    return {"schema": "joulewise.cadence_queue.v1", "queue_id": "cq-ct-1", "expires_at": "2026-12-31T00:00:00-08:00",
            "halt": None, "standing_notice": {"issue": 900}, "spans": copy.deepcopy(spans)}


GOOD_OBS = {
    "measurement_head": COMMIT, "frozen_path_sha256": {RUNNER: "1" * 64, FIT: "2" * 64},
    "ac_power": True, "powermode": 0, "network_time": "off", "freq_word": 0, "stray_monitors": [],
    "other_agents": [], "night_labels_loaded": [], "high_power_marker": False, "sudo_kill_rc": 0,
    "km003c_ready": True, "disk_free_gb": 120.0, "previous_span": "none", "halts": [],
}
