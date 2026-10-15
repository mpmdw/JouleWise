"""Block-six replication inputs, without binding t0 until the caller launches."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import subprocess

from joulewise.b5 import plan
from joulewise.b6 import registration

SEALED_DIR = "configs/campaigns/v5_claim_25g83"
REGISTRATION = SEALED_DIR + "/registration_block5.md"
SIZING = SEALED_DIR + "/sizing_b5.json"
PACK_LABELS = {"d117_floor_qwen3-1p7b_v5": "ALPHA", "d117_floor_qwen3-8b_v5": "BETA",
               "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5": "GAMMA"}
BYTES_PER_MEMBER = 182 * 1024 * 1024


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def registered_thresholds(text):
    start = text.index("### 4.3 Registered thresholds")
    end = text.find("\n### ", start + 1)
    section = text[start:end if end > 0 else len(text)]
    opening = section.index("```json") + len("```json")
    value = json.loads(section[opening:section.index("```", opening)])
    if set(value) != {"clock", "battery", "thermal", "contention", "disk", "instrument"}:
        raise ValueError("registration must name the six hazard modules")
    if value["contention"].get("clean_s") != 180:
        raise ValueError("registration contention.clean_s must be the sealed 180")
    return value


def thresholds(measurement, registration_dir):
    result = registered_thresholds((Path(measurement) / REGISTRATION).read_text())
    overrides = registration.load_precheck_thresholds(registration_dir)
    contract = plan.hazard_threshold_defaults()
    # The precheck also has non-driver fields (agents, margins, probe timing).
    # Only fields in the driver's existing threshold contract enter its plan.
    for module, limits in result.items():
        limits.update({k: v for k, v in overrides.get(module, {}).items() if k in contract[module]})
    return result


def window_max_s(inputs):
    """Exactly the formula in b5.plan.write_window_plan, independent of t0."""
    span = math.ceil(inputs["programmed_span_s"]["seconds"])
    return 60 * math.ceil((span + plan.T0_STAGE_CAP_S + plan.PAUSE_LIMIT_S + plan.SESSION_WAIT_BUDGET_S) / 60)


def build(measurement_root, registration_dir, pack_id, session_id, identities, *, custody_root,
          runs_parent, claim_backup, bound_backup, head=None, attempt=1, run=subprocess.run):
    measurement, reg = Path(measurement_root), Path(registration_dir)
    if head is None:
        head = run(["git", "-C", str(measurement), "rev-parse", "HEAD"],
                   check=True, capture_output=True, text=True, timeout=30).stdout.strip()
    sized = registration.load_sizing(reg)
    label = next((key for key, value in sized["packs"].items() if value["pack_id"] == pack_id), None)
    if label is None:
        raise ValueError("pack has no registered sizing: " + pack_id)
    sizing_path = reg / "sizing_b5.json"
    raw = sizing_path.read_bytes()
    try:
        relative = sizing_path.relative_to(measurement).as_posix()
    except ValueError:
        # The machine test's non-claim registration is outside M. Cite the
        # identical sealed source in M, as the plan writer requires.
        if raw != (measurement / SIZING).read_bytes():
            raise ValueError("external sizing has no identical source in the measurement checkout")
        relative = SIZING

    def allowance(key):
        return {"seconds": sized["packs"][label][key], "source": {"path": relative, "sha256": sha256(raw)},
                "source_pointer": f"/packs/{label}/{key}"}

    registration_raw = (measurement / REGISTRATION).read_bytes()
    result = {"schema": "joulewise.b5_window_plan_inputs.v2", "plan_id": session_id, "attempt": attempt,
              "pack_root": str(measurement / "configs/campaigns" / pack_id),
              "measurement_root": str(measurement), "measurement_head": head, "repo_head": head,
              "custody_root": str(custody_root), "runs_parent": str(runs_parent),
              "claim_backup_destination": str(claim_backup), "bound_backup_destination": str(bound_backup),
              "bracket_session_id": session_id + "-calibration", "pre_attempt_id": session_id + "-cal-pre",
              "post_attempt_id": session_id + "-cal-post", "g10": False,
              "programmed_span_s": allowance("programmed_span_s"),
              "T_stream_max_s": allowance("T_stream_max_s"), "bytes_per_member": BYTES_PER_MEMBER,
              "thresholds": thresholds(measurement, reg),
              "registration": {"path": REGISTRATION, "sha256": sha256(registration_raw)}}
    for key, name in (("identity_epoch_json", "identity-epoch.json"), ("t1_bindings_json", "t1-bindings.json")):
        result[key] = {k: identities[name][k] for k in ("path", "sha256")}
    return deepcopy(result)
