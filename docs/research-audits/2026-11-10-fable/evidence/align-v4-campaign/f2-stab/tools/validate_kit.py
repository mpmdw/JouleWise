"""Validate an RL-180 stability kit with the unchanged pinned runner."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


BASE = Path(__file__).resolve().parents[2] / "item-drafts-f2" / "f2-inst-01.v1.1.json"
BASE_SHA256 = "651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b"
PIN_B = "6e9d42f1dd3d308bc9239143d0d634ab965e50e1"
BASE_B = Path(__file__).resolve().parents[1] / "qual-pin" / "f2-stab-15.v1.1.json"
BASE_B_SHA256 = "8dceffc2e1a10a03d25c6c06487756fe37f8f5a1c57d52e242a64faabcbc36a1"
CELL_FIELDS = ("prefill_tokens", "decode_tokens", "g0_shape", "start_band")


def validate_cells(kit, base):
    """Enforce RL-180 row 13 and RL-179's allowed kit differences."""
    if not re.fullmatch(r"f2-stab-\d{2}", kit["campaign_id"]):
        raise ValueError("campaign_id: expected f2-stab-NN")
    if kit["ruling"]["id"] != "RL-179":
        raise ValueError("ruling.id: expected RL-179")
    if len(kit["legs"]) != len(base["legs"]):
        raise ValueError(f"legs: expected {len(base['legs'])} positions")
    for pos, (actual, original) in enumerate(zip(kit["legs"], base["legs"], strict=True)):
        for field in CELL_FIELDS:
            if actual[field] != original[field]:
                raise ValueError(f"legs[{pos}].{field}: expected {original[field]!r}, got {actual[field]!r}")
        if {**actual, "seed": original["seed"]} != original:
            raise ValueError(f"legs[{pos}]: only the derived seed may differ")

    # Power mode is kit-wide. The copied checklist's powermode_zero and
    # block_power_mode inclusion rule apply to every leg.
    if any(kit[key] != base[key] for key in ("checklist", "inclusion_rules")):
        raise ValueError("checklist and inclusion_rules: preserve the base guards, including Automatic power mode")
    restored = {
        **kit,
        "campaign_id": base["campaign_id"],
        "ruling": {**kit["ruling"], "id": base["ruling"]["id"]},
        "seed_law": {**kit["seed_law"], "master_seed": base["seed_law"]["master_seed"]},
        "legs": base["legs"],
    }
    if restored != base:
        raise ValueError("kit: only campaign_id, ruling.id, master_seed and per-leg seeds may differ")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kit", type=Path)
    parser.add_argument("--repo", required=True, type=Path, help="clean checkout at the admitted runner pin")
    parser.add_argument("--batch-window", choices=("02:00-02:35", "13:14-13:15"),
                        help="required for pin A, omitted for pin B")
    args = parser.parse_args(argv)
    try:
        repo = args.repo.resolve()
        git = ["git", "-C", str(repo)]
        head = subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip()
        source, base_sha = (BASE_B, BASE_B_SHA256) if head == PIN_B else (BASE, BASE_SHA256)
        base_raw = source.read_bytes()
        if hashlib.sha256(base_raw).hexdigest() != base_sha:
            raise ValueError("base kit SHA-256 mismatch")
        base = json.loads(base_raw)
        kit_path = args.kit.resolve()
        kit_raw = kit_path.read_bytes()
        validate_cells(json.loads(kit_raw), base)
        pin = base["frozen"]["commit"]
        status = subprocess.check_output([*git, "status", "--porcelain"], text=True)
        if head != pin or status:
            raise ValueError(f"runner must be a clean checkout at {pin}")
        if (head == PIN_B) == bool(args.batch_window):
            raise ValueError("--batch-window is required for pin A and must be omitted for pin B")
        window = ["--batch-window", args.batch_window] if args.batch_window else []
        native = subprocess.run(
            [sys.executable, "-I", "-B", str(repo / "scripts/cadence_queue.py"),
             "validate-kit", str(kit_path), "--repo", str(repo), *window],
            capture_output=True, text=True,
        )
        if native.returncode:
            sys.stderr.write(native.stdout + native.stderr)
            return native.returncode
        output = json.loads(native.stdout)
        if (output["kit_sha256"] != hashlib.sha256(kit_raw).hexdigest()
                or not output["frozen_paths_verified"] or output["frozen_commit"] != pin):
            raise ValueError("pinned validator must verify the same kit bytes and frozen paths")
    except (OSError, ValueError, TypeError, KeyError, subprocess.CalledProcessError) as error:
        print(f"REFUSE {error}", file=sys.stderr)
        return 1
    print(json.dumps({**output, "base_kit_sha256": base_sha, "positional_cells_verified": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
