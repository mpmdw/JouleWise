"""Small readers shared by acceptance, survivor screening and run export."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
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


def bundle_roots(root: Path, plan: Mapping) -> tuple[Path, ...]:
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
    return tuple(roots)


def bundle_of(root: Path, plan: Mapping, run_id: str) -> Path | None:
    return next((base / run_id for base in bundle_roots(root, plan)
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
