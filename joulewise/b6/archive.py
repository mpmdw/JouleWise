"""Small readers shared by acceptance, survivor screening and run export."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from joulewise.desk_compress import read_bytes


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(read_bytes(path).decode("utf-8"))
    except (OSError, ValueError):
        return default


def bindings(plan: Mapping) -> dict:
    result = dict(plan)
    hazard = plan.get("hazard_window") or {}
    result.update(hazard)
    result.update(hazard.get("pack") or {})
    for source in (plan, hazard):
        for name in ("bindings", "arm_bindings", "harvest"):
            if isinstance(source.get(name), Mapping):
                result.update(source[name])
    if result.get("repo_root"):
        result.setdefault("measurement_root", result["repo_root"])
    return result


def bundle_roots(root: Path, plan: Mapping, *, archive_only: bool = False) -> tuple[Path, ...]:
    bound = bindings(plan)
    roots = [root / "sources/claim-runs", root / "sources/bound-runs"]
    custody = Path(bound["custody_root"]) if bound.get("custody_root") else None
    for key in ("claim_runs_root", "bound_runs_root"):
        if bound.get(key):
            original = Path(bound[key])
            if custody:
                try:
                    roots.append(root / "sources/night-custody" / original.relative_to(custody))
                except ValueError:
                    pass
            roots.append(original)
    if archive_only:
        # Keep lexical archive symlinks digest-verifiable, but do not let a
        # plan's ".." components turn a copied-custody alias into an outside root.
        sources = Path(os.path.abspath(root / "sources"))
        roots = [base for base in roots if Path(os.path.abspath(base)).is_relative_to(sources)]
    return tuple(roots)


def bundle_of(root: Path, plan: Mapping, run_id: str, *, archive_only: bool = False) -> Path | None:
    return next((base / run_id for base in bundle_roots(root, plan, archive_only=archive_only)
                 if (base / run_id).is_dir()), None)


def plan_tree(root: Path, plan: Mapping, pack_id: str) -> tuple[dict, Path | None]:
    candidates = [root / "sources/repo/configs/campaigns" / pack_id,
                  root / "sources/pack"]
    bound = bindings(plan)
    if bound.get("pack_root"):
        candidates.append(Path(bound["pack_root"]))
    for candidate in candidates:
        tree = read_json(candidate / "plan_tree.json")
        if tree:
            return tree, candidate
    return plan.get("plan_tree", {}), None


def ordered_roster(roster: Mapping, evidence) -> dict:
    """The plan stage walk supplies order and roles; the roster supplies units."""
    blueprints = {m["run_id"]: m for m in roster.get("members", [])}
    members = [{**blueprints.get(m.run_id, {}), "run_id": m.run_id,
                "stage_id": m.stage_id, "role": m.role, "status": m.status,
                "config_key": m.config_key}
               for stage in evidence.stages for m in stage.members]
    return {**roster, "members": members}


def executed_porcelain(root: Path, plan: Mapping, plan_path: Path | None = None) -> str | None:
    """Read the same executed checkout as harvest, including every edit line."""
    from joulewise.b5.harvest import _inventory_checkout, _plan_value

    custody = Path(_plan_value(plan, "custody_root") or (plan_path.parent if plan_path else root))
    supplied = _plan_value(plan, "executed_inventory_path", "executed_inventory")
    original = Path(supplied) if supplied else custody / "night/executed_inventory.json"
    if not original.is_absolute():
        original = custody / original
    candidates = []
    try:
        candidates.append(root / "sources/night-custody" / original.relative_to(custody))
    except ValueError:
        pass
    candidates.extend((root / "night/executed_inventory.json", root / "sources/night/executed_inventory.json", original))
    for path in candidates:
        inventory = read_json(path)
        if inventory is not None:
            value = _inventory_checkout(inventory).get("status_porcelain")
            return value if isinstance(value, str) else None
    return None


CLOCK_ANCHOR_STATUS = "member.anchor_not_bounded"


def unresolved_clock_anchor(metadata: Mapping, summary: Mapping, codes=()) -> bool:
    """Recognize the recorded anchor failure, without re-estimating any time."""
    metadata = metadata if isinstance(metadata, Mapping) else {}
    uncertainty = metadata.get("uncertainty_evidence")
    anchor = uncertainty.get("clock_anchor") if isinstance(uncertainty, Mapping) else None
    anchor = anchor if isinstance(anchor, Mapping) else {}
    precheck = summary.get("window_evidence_precheck")
    phases = precheck.get("phase") if isinstance(precheck, Mapping) else None
    phases = phases if isinstance(phases, Mapping) else {}
    return (CLOCK_ANCHOR_STATUS in codes
            or anchor.get("detail") == "effective_clock_anchor_bound_exceeded"
            or (anchor.get("trace_fallback_method") == "legacy_spawn_bracket_midpoint_v1"
                and anchor.get("status") != "bounded")
            or bool(phases) and all(isinstance(phase, Mapping)
                                    and "clock_anchor_unresolved" in (phase.get("reasons") or [])
                                    for phase in phases.values()))


def summary_with_clock_status(summary: Mapping, metadata: Mapping, codes=()) -> dict:
    """Mark the derived block-six summary; source bundles and eligibility stay intact."""
    from copy import deepcopy
    result = deepcopy(dict(summary))
    if not unresolved_clock_anchor(metadata, summary, codes):
        return result

    def null_numbers(value):
        if isinstance(value, Mapping):
            # Retain the clock bounds and method evidence inside energy envelopes.
            return {key: child if key.endswith(("_s", "_ns")) else null_numbers(child)
                    for key, child in value.items()}
        if isinstance(value, list):
            return [null_numbers(child) for child in value]
        return None if isinstance(value, (int, float)) and not isinstance(value, bool) else value

    # The precheck remains the recorded exclusion evidence. Only the energy
    # outputs are withheld; status/counting and the raw source bytes are untouched.
    for key, value in result.items():
        if "energy" in key and key != "energy_uncertainty_status":
            result[key] = null_numbers(value)
    result["energy_status"] = CLOCK_ANCHOR_STATUS
    return result


def registration_digests(paths) -> dict:
    """Digest named registration inputs; unavailable bytes are recorded, never refused."""
    import hashlib
    result = {}
    for path in paths:
        path = Path(path)
        try:
            result[str(path)] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        except OSError as exc:
            result[str(path)] = {"sha256": None, "error": type(exc).__name__}
    return result
