#!/usr/bin/env python3
"""Write one block-5 plan-input file (joulewise.b5_window_plan_inputs.v2) from sealed bytes.

Desk helper for the post-seal runbook; it is not part of the repository and never arms anything.
Every value that the registration fixes is read from the measurement checkout, never typed:

* the hazard thresholds are the JSON block under the registration heading
  "### 4.3 Registered thresholds" (the plan writer replaces the two sized keys itself);
* the two sizing allowances are read from configs/campaigns/v5_claim_25g83/sizing_b5.json;
* measurement_head and repo_head are the checkout's HEAD (the installer refuses any other value).

It writes <stage-dir>/plan-inputs.json once (it refuses to overwrite) and prints a JSON summary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PACKS = {"alpha": ("d117_floor_qwen3-1p7b_v5", "ALPHA"),
         "beta": ("d117_floor_qwen3-8b_v5", "BETA"),
         "gamma": ("d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5", "GAMMA")}
SEALED_DIR = "configs/campaigns/v5_claim_25g83"
REGISTRATION = SEALED_DIR + "/registration_block5.md"
SIZING = SEALED_DIR + "/sizing_b5.json"
THRESHOLD_HEADING = "### 4.3 Registered thresholds"
BYTES_PER_MEMBER = 182 * 1024 * 1024  # registration 4.2: 182 MiB per member


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def registered_thresholds(text: str) -> dict:
    start = text.index(THRESHOLD_HEADING)
    nxt = text.find("\n### ", start + 1)
    section = text[start: nxt if nxt > 0 else len(text)]
    opening = section.index("```json") + len("```json")
    block = json.loads(section[opening: section.index("```", opening)])
    if set(block) != {"clock", "battery", "thermal", "contention", "disk", "instrument"}:
        raise SystemExit(f"the registered threshold block names {sorted(block)}, not the six hazard modules")
    if block["contention"].get("clean_s") != 180:
        raise SystemExit(f"contention.clean_s is {block['contention'].get('clean_s')!r}, not the sealed 180")
    return block


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--measurement-root", required=True, type=Path)
    parser.add_argument("--pack", required=True, choices=sorted(PACKS))
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--attempt", required=True, type=int)
    parser.add_argument("--t0-epoch-s", required=True, type=int)
    parser.add_argument("--g10", required=True, choices=("true", "false"))
    parser.add_argument("--stage-dir", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--runs-parent", required=True, type=Path)
    parser.add_argument("--claim-backup", required=True, type=Path)
    parser.add_argument("--bound-backup", required=True, type=Path)
    parser.add_argument("--registration-sha256", required=True,
                        help="the sealed registration's SHA-256 from the seal record")
    args = parser.parse_args()
    root = args.measurement_root.resolve()
    pack_dir, label = PACKS[args.pack]
    for text in (args.plan_id, str(root), str(args.custody_root), str(args.runs_parent), str(args.stage_dir)):
        if "claude" in text.lower() or "codex" in text.lower():
            raise SystemExit(f"{text!r} contains an agent-census substring")
    registration_raw = (root / REGISTRATION).read_bytes()
    if sha256(registration_raw) != args.registration_sha256:
        raise SystemExit("the checkout's registration is not the sealed one (SHA-256 differs from the seal record)")
    thresholds = registered_thresholds(registration_raw.decode("utf-8"))
    sizing_raw = (root / SIZING).read_bytes()
    sizing = json.loads(sizing_raw)["packs"][label]
    head = subprocess.run(["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()
    stage = args.stage_dir.resolve()
    identity, t1 = stage / "identity-epoch.json", stage / "t1-bindings.json"

    def allowance(key: str) -> dict:
        return {"seconds": sizing[key], "source": {"path": SIZING, "sha256": sha256(sizing_raw)},
                "source_pointer": f"/packs/{label}/{key}"}

    inputs = {
        "schema": "joulewise.b5_window_plan_inputs.v2",
        "plan_id": args.plan_id, "attempt": args.attempt,
        "pack_root": str(root / "configs/campaigns" / pack_dir),
        "measurement_root": str(root), "measurement_head": head, "repo_head": head,
        "custody_root": str(args.custody_root), "runs_parent": str(args.runs_parent),
        "claim_backup_destination": str(args.claim_backup),
        "bound_backup_destination": str(args.bound_backup),
        "bracket_session_id": f"{args.plan_id}-calibration",
        "pre_attempt_id": f"{args.plan_id}-cal-pre", "post_attempt_id": f"{args.plan_id}-cal-post",
        "identity_epoch_json": {"path": str(identity), "sha256": sha256(identity.read_bytes())},
        "t1_bindings_json": {"path": str(t1), "sha256": sha256(t1.read_bytes())},
        "t0_epoch_s": args.t0_epoch_s,
        "programmed_span_s": allowance("programmed_span_s"),
        "T_stream_max_s": allowance("T_stream_max_s"),
        "bytes_per_member": BYTES_PER_MEMBER,
        "thresholds": thresholds,
        "g10": args.g10 == "true",
        "registration": {"path": REGISTRATION, "sha256": sha256(registration_raw)},
    }
    raw = (json.dumps(inputs, indent=2) + "\n").encode("utf-8")
    with open(stage / "plan-inputs.json", "xb") as stream:
        stream.write(raw)
    print(json.dumps({"inputs": str(stage / "plan-inputs.json"), "inputs_sha256": sha256(raw),
                      "measurement_head": head, "pack": label,
                      "thresholds_sha256": sha256(json.dumps(thresholds, sort_keys=True).encode()),
                      "contention_clean_s": thresholds["contention"]["clean_s"],
                      "programmed_span_s": sizing["programmed_span_s"],
                      "T_stream_max_s": sizing["T_stream_max_s"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
