#!/usr/bin/env python3
"""Reproduce the isolated r1 layout; refuse unsupported governed pack admission.

The seed is genesis, never a production-ledger copy. This producer deliberately
cannot mint a freeze/ARM receipt until the dedicated profile is installed.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from joulewise import arm_readiness as readiness, calibration_ledger, t0_rehearsal
from scripts.produce_t0_rehearsal_bundle import write


def generate(window_id, checkout, custody, backup_a, backup_b, *, home=None, inventory=None):
    if not window_id.startswith(t0_rehearsal.REHEARSAL_WINDOW_PREFIX) or Path(window_id).name != window_id:
        raise ValueError("window id must use the rehearsal prefix")
    paths = [Path(p) for p in (checkout, custody, backup_a, backup_b)]
    if any(not p.is_absolute() or any(q.is_symlink() for q in (p, *p.parents)) for p in paths):
        raise ValueError("layout requires absolute non-symlink paths")
    checkout, custody, backup_a, backup_b = (p.resolve(strict=True) for p in paths)
    if not checkout.name.startswith(readiness.REHEARSAL_CLONE_PREFIX) or custody.name != window_id:
        raise ValueError("layout identity does not use reviewed prefixes")
    # Use the independent production census; a missing production root still counts.
    if inventory is None:
        from scripts.rehearse_t0_unattended import _production_inventory
        import subprocess
        head = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
        inventory = _production_inventory({"repo_head": head, "measurement_head": head, "measurement_root": str(checkout)})
    roots = readiness.production_custody_roots(home=Path.home() if home is None else home, inventory=inventory)
    for p in (checkout, custody, backup_a, backup_b):
        for root in roots:
            spec = next(s for s in readiness.PRODUCTION_CUSTODY_ROOTS if s.role == root.role.split(":", 1)[0])
            if spec.predicate == "SIBLING_CHILD" and p == custody:
                if p.parent != root.path:
                    raise ValueError("custody is not the required sibling child")
            elif t0_rehearsal._contains(p, root.path) or t0_rehearsal._contains(root.path, p):
                raise ValueError("production-root overlap")
    for i, p in enumerate(paths):
        for other in paths[i+1:]:
            if t0_rehearsal._contains(p, other) or t0_rehearsal._contains(other, p):
                raise ValueError("rehearsal roots overlap")
    pack = checkout / "configs/campaigns/v5_pack_rehearsal"
    recipe = {"schema_version": "joulewise.v5_pack_rehearsal_recipe.v1",
        "status": "NEEDS_RULING", "window_id": window_id, "pack_root": str(pack),
        "measurement_root": str(checkout), "custody_root": str(custody),
        "purpose": "T0_REHEARSAL", "claim_eligible": False, "model_members": [],
        "claim_runs_root": str(checkout / "runs" / (window_id + "-claim")),
        "bound_runs_root": str(checkout / "runs" / (window_id + "-bound")),
        "claim_backup_destination": str(backup_a), "bound_backup_destination": str(backup_b),
        "ledger_path": str(checkout / "runs/calibration_observation_ledger.jsonl"),
        "genesis_pin": {"sequence": 0, "head_digest": calibration_ledger.GENESIS_DIGEST,
                        "ledger_schema": calibration_ledger.LEDGER_SCHEMA},
        "ledger_seed_source": "EMPTY_GENESIS_NO_PRODUCTION_IMPORT",
        "chain_source": "scripts/night_chains/v5_pack_rehearsal.zsh",
        "required_profile_ruling": "dedicated non-inference profile in arm_readiness._plan_profile",
        "required_pin_ruling": "rehearsal-local committed genesis pin, not checkout production pin"}
    return write(pack / "rehearsal-recipe.json", recipe)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--window-id", required=True)
    for name in ("checkout", "custody", "claim-backup", "bound-backup"):
        p.add_argument("--" + name, type=Path, required=True)
    args = p.parse_args(argv)
    try:
        path = generate(args.window_id, args.checkout, args.custody, args.claim_backup, args.bound_backup)
        sys.stdout.buffer.write(readiness.render_json({"status": "NEEDS_RULING", "recipe": str(path)}))
        return 2
    except (ValueError, OSError) as exc:
        sys.stdout.buffer.write(readiness.render_json({"status": "REFUSED", "detail": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
