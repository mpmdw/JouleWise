"""Compose whole science modules; fixed replications retain their tree bytes."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

SCHEMA = "joulewise.b6_session_layout.v1"
FLOOR_TEMPLATE = "configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json"
GAMMA_TEMPLATE = "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json"


@dataclass(frozen=True)
class SessionLayout:
    session_id: str
    packs: tuple[str, ...]
    stages: tuple[dict, ...]
    fixed_part: dict
    template: dict
    fixed_bytes: bytes | None = None
    schema_version: str = SCHEMA
    campaign_id: str | None = None


def _repo_path(root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "configs":
        raise ValueError("input must name a repository config")
    full = (root / path).resolve()
    if not full.is_relative_to(root.resolve()):
        raise ValueError("config escaped repository")
    return full


def _entries(root, manifest_path, pack_id=None, module_id=None):
    path = _repo_path(root, manifest_path)
    manifest = json.loads(path.read_bytes())
    entries = []
    for row in manifest["executed_order"]:
        config = path.parent / row["config"]
        relative = config.relative_to(root).as_posix()
        config = _repo_path(root, relative)
        entries.append({**row, "config_path": relative,
                        "config_sha256": row.get("config_sha256") or hashlib.sha256(config.read_bytes()).hexdigest(),
                        "role": row.get("role"), "block_id": row.get("block_id"),
                        "position": row.get("position"), "arm": row.get("arm"),
                        "pack_id": pack_id, "module_id": module_id})
    return entries


def _manifest_path(row, tree, tree_path):
    ref = row.get("input", row.get("input_ref", {}))
    if ref.get("kind") == "pack_manifest":
        return (Path(tree_path).parent / ref["path"]).as_posix()
    if ref.get("kind") == "external_input":
        ref = next(x for x in tree["external_inputs"] if x["input_id"] == ref["input_id"])
        return ref.get("manifest_path")
    return ref.get("path") if row["kind"] == "campaign_collection" else None


def _stage(root, row, tree, tree_path, pack=None, module=None):
    row = deepcopy(row)
    manifest = _manifest_path(row, tree, tree_path)
    row["entries"] = _entries(root, manifest, pack, module) if manifest else []
    return row


def layout(selection, regs, repo_root) -> SessionLayout:
    root = Path(repo_root).resolve()
    selected = [regs[p] for p in selection.packs]
    session_id = "r%d-%s" % (selection.round, "-".join(selection.packs))
    if selected[0].session_shape == "fixed":
        if len(selected) != 1:
            raise ValueError("fixed pack must have its own session")
        reg = selected[0]
        raw = _repo_path(root, reg.plan_tree_ref).read_bytes()
        tree = json.loads(raw)
        stages = tuple(_stage(root, s, tree, reg.plan_tree_ref, reg.pack_id) for s in tree["stage_graph"])
        return SessionLayout(session_id, selection.packs, stages, reg.corpus, tree, raw,
                             campaign_id=Path(reg.plan_tree_ref).parent.name)
    cadences = {r.reference_cadence for r in selected}
    if len(cadences) != 1:
        raise ValueError("co-located packs need one registered reference cadence")
    tree = json.loads(_repo_path(root, FLOOR_TEMPLATE).read_bytes())
    fixed = [_stage(root, s, tree, FLOOR_TEMPLATE) for s in tree["stage_graph"] if "science" not in s["stage_id"]]
    science_template = next(s for s in tree["stage_graph"] if "science" in s["stage_id"])
    prefix = fixed[:5]
    suffix = fixed[-4:]
    if all(m["kind"] == "contrast" for r in selected for m in r.modules):
        gamma = json.loads(_repo_path(root, GAMMA_TEMPLATE).read_bytes())
        # GAMMA counts only actual members, not reservation/desk invocations.
        for s in prefix + suffix:
            if s["kind"] in {"bracket_reservation", "bound_derivation", "whole_window_verdict", "backup"}:
                s["expected_count"] = next(x["expected_count"] for x in gamma["stage_graph"] if x["kind"] == s["kind"])
    module_stages = []
    for r in selected:
        for m in r.modules:
            entries = []
            for directory in m["config_dirs"]:
                entries += _entries(root, str(Path(directory) / "order_manifest.json"), r.pack_id, m["module_id"])
            count = 50 if m["kind"] == "floor" else 40
            if len(entries) != count:
                raise ValueError(f"{m['module_id']}: expected {count} runs, got {len(entries)}")
            pieces = [("absolute", entries[:10]), ("quads-01-05", entries[10:30]), ("quads-06-10", entries[30:])] if count == 50 else [
                ("quads-01-05", entries[:20]), ("quads-06-10", entries[20:])]
            stages = []
            for name, members in pieces:
                s = deepcopy(science_template)
                s.update(stage_id=m["module_id"] + "-" + name, entries=members, expected_count=len(members),
                         module_id=m["module_id"], pack_id=r.pack_id, module_kind=m["kind"])
                stages.append(s)
            module_stages.append((r, m, stages))
    corpus = {"planned": max(r.corpus["planned"] for r in selected)}
    if all(r.kind == "new" for r in selected):
        corpus["stop_after_valid"] = 12
    prefix[2]["expected_count"] = corpus["planned"]
    prefix[2]["corpus"] = corpus
    if len(prefix[2]["entries"]) < corpus["planned"]:
        raise ValueError("template corpus has fewer members than registered")
    prefix[2]["entries"] = prefix[2]["entries"][:corpus["planned"]]
    middle = []
    midpoint = fixed[5]
    if next(iter(cadences)) == "session_half":
        total = sum(sum(s["expected_count"] for s in stages) for _, _, stages in module_stages)
        boundaries, running = [], 0
        for _, _, stages in module_stages[:-1]:
            running += sum(s["expected_count"] for s in stages)
            boundaries.append(running)
        boundary = min(boundaries, key=lambda x: abs(x - total / 2)) if boundaries else None
        running = 0
        for _, _, stages in module_stages:
            middle += stages
            running += sum(s["expected_count"] for s in stages)
            if running == boundary:
                middle.append(deepcopy(midpoint))
        # A single module has only its two quad-half boundary.
        if boundary is None:
            middle.insert(len(middle) - 1, deepcopy(midpoint))
    else:
        gamma = json.loads(_repo_path(root, GAMMA_TEMPLATE).read_bytes())
        for i, (_, m, stages) in enumerate(module_stages):
            middle += stages[:-1]
            source = next(s for s in gamma["stage_graph"] if s["stage_id"] == f"gamma-reference-{m['phase']}-midpoint")
            ref = _stage(root, source, gamma, GAMMA_TEMPLATE)
            ref["stage_id"] = m["module_id"] + "-reference-midpoint"
            middle += [ref, stages[-1]]
            if i < len(module_stages) - 1:
                ref = deepcopy(midpoint)
                ref["stage_id"] = m["module_id"] + "-reference-boundary"
                middle.append(ref)
    if any(r.data.get("interleave", "none") == "quad_round_robin" for r in selected):
        if next(iter(cadences)) == "session_half":
            # Put each module's first quad half before the shared midpoint;
            # repeats stay together, and second quad halves follow it.
            middle = [s for _, _, stages in module_stages for s in stages[:-1]] + [deepcopy(midpoint)] + [
                stages[-1] for _, _, stages in module_stages]
        # Alternate complete quads inside each reference-delimited half.
        segments, segment = [], []
        for s in middle + [None]:
            if s is None or "reference" in s["stage_id"]:
                repeats = [s for s in segment if s.get("module_kind") == "floor" and "absolute" in s["stage_id"]]
                quads = [s for s in segment if s not in repeats]
                segments += repeats
                for index in range(max((len(s["entries"]) // 4 for s in quads), default=0)):
                    for source in quads:
                        members = source["entries"][4*index:4*index+4]
                        if members:
                            q = deepcopy(source)
                            q.update(stage_id=source["stage_id"] + f"-q{index+1:02}", entries=members, expected_count=4)
                            segments.append(q)
                if s is not None:
                    segments.append(s)
                segment = []
            else:
                segment.append(s)
        middle = segments
    return SessionLayout(session_id, selection.packs, tuple(prefix + middle + suffix), corpus, tree)


def render(layout: SessionLayout, template_tree=None):
    if layout.fixed_bytes is not None:
        return json.loads(layout.fixed_bytes), {"plan_tree.json": layout.fixed_bytes}
    tree = deepcopy(template_tree or layout.template)
    files, graph, science = {}, [], []
    for stage in layout.stages:
        row = deepcopy(stage)
        entries = row.pop("entries")
        for key in ("module_kind", "module_id", "pack_id"):
            row.pop(key, None)
        if entries:
            path = f"stages/{row['stage_id']}/order_manifest.json"
            manifest_id = row["stage_id"] + "-order-v1"
            manifest = {"schema_version": "joulewise.order_manifest.v1", "manifest_id": manifest_id,
                        "planned_n_bundles": len(entries), "executed_order": [
                            {**e, "index": i+1, "config": e["config_path"]} for i, e in enumerate(entries)]}
            raw = (json.dumps(manifest, indent=2) + "\n").encode()
            files[path] = raw
            row["input"] = {"kind": "manifest", "path": path, "manifest_id": manifest_id,
                            "sha256": hashlib.sha256(raw).hexdigest()}
            args = row["launch"]["commands"][0]["argv_template"]["arguments"]
            args[0] = {"kind": "repo_path", "value": str(Path(path).parent)}
            science += [{**e, "stage_id": row["stage_id"]} for e in entries if e.get("module_id")]
        graph.append(row)
    for i, row in enumerate(graph):
        row.update(ordinal=i+1, predecessor=graph[i-1]["stage_id"] if i else None,
                   successor=graph[i+1]["stage_id"] if i+1 < len(graph) else None)
        for command in row["launch"]["commands"]:
            command["command_id"] = row["stage_id"] + "." + command.get("command_kind", "run")
    tree.update(schema_version="joulewise.d117_plan_tree.v1", stage_graph=graph, science=science,
                b6_layout={"schema_version": SCHEMA, "packs": layout.packs, "corpus": layout.fixed_part})
    files["plan_tree.json"] = (json.dumps(tree, indent=2) + "\n").encode()
    return tree, files


def registered_smoke_keep(campaign_id, *, path=None):
    """Fixed replications and the machine smoke share one campaign-keyed map."""
    target = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "configs/b6/smoke_keep.json"
    return dict(json.loads(target.read_text())[campaign_id])


def smoke_keep(layout):
    if layout.fixed_bytes is not None and layout.campaign_id is not None:
        return registered_smoke_keep(layout.campaign_id)
    keep, seen = {}, set()
    for s in layout.stages:
        sid = s["stage_id"]
        if "reference-start" in sid or "reference-end" in sid:
            keep[sid] = 1
        elif "science" in sid or s.get("module_id"):
            entries = s["entries"]
            if not entries:
                continue
            module = entries[0].get("module_id") or ("prefill" if "prefill" in sid else "decode")
            if module in seen:
                continue
            if entries[0]["role"] == "absolute_repeat":
                keep[sid] = 1
                seen.add(module)
            elif entries[0]["role"] == "comparative_contrast_member":
                keep[sid] = 2  # first A and B; no full quad in the smoke
                seen.add(module)
    return keep
