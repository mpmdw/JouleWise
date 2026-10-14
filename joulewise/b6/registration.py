"""Read pack registrations and determine which committed packs are open."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Mapping

from joulewise.flags.catalog import Catalog, EFFECTS, load_catalog

SCHEMA = "joulewise.b6_pack_registration.v1"
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


@dataclass(frozen=True)
class Registration:
    data: Mapping[str, Any]
    path: str | None = None
    commit_time: int = 0

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def load(path: str | Path) -> Registration:
    return Registration(json.loads(Path(path).read_text()), str(path))


def validate(reg: Registration, catalog: Catalog, *, root=None) -> list[str]:
    d = reg.data
    if not isinstance(d, dict):
        return ["registration must be an object"]
    errors = []
    draft = d.get("status") == "draft"

    def check(field, valid):
        if not valid:
            errors.append(field)

    def integer(value, minimum=1):
        return type(value) is int and value >= minimum

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    check("schema_version", d.get("schema_version") == SCHEMA)
    check("draft_notes", draft or "draft_notes" not in d)
    check("pack_id", isinstance(d.get("pack_id"), str) and bool(ID.fullmatch(d["pack_id"])))
    for field in ("title", "question", "flag_catalog"):
        check(field, text(d.get(field)))
    check("question", text(d.get("question")) and "\n" not in d["question"])
    for field, choices in (("status", ("draft", "registered")), ("kind", ("replication", "new")),
                           ("session_shape", ("fixed", "modular")),
                           ("reference_cadence", ("session_half", "half_module_plus_boundary"))):
        check(field, d.get(field) in choices)
    if d.get("session_shape") == "fixed":
        check("plan_tree_ref", text(d.get("plan_tree_ref")))
        if root is not None and d.get("status") == "registered" and text(d.get("plan_tree_ref")):
            try:
                checkout = Path(root).resolve()
                path = (checkout / d["plan_tree_ref"]).resolve()
                path.relative_to(checkout)
                tree = json.loads(path.read_text())
                check("plan_tree_ref", isinstance(tree, dict) and isinstance(tree.get("stage_graph"), list))
            except (OSError, ValueError):
                check("plan_tree_ref", False)
    modules = d.get("modules")
    check("modules", isinstance(modules, list) and (bool(modules) or d.get("session_shape") == "fixed"))
    ids = []
    for i, m in enumerate(modules if isinstance(modules, list) else []):
        prefix = f"modules[{i}]"
        if not isinstance(m, dict):
            check(prefix, False)
            continue
        check(prefix + ".module_id", text(m.get("module_id")) and bool(ID.fullmatch(m["module_id"])))
        if isinstance(m.get("module_id"), str):
            ids.append(m["module_id"])
        check(prefix + ".kind", m.get("kind") in ("floor", "contrast"))
        check(prefix + ".phase", m.get("phase") in ("decode", "prefill"))
        dirs = m.get("config_dirs")
        check(prefix + ".config_dirs", isinstance(dirs, list) and bool(dirs) and all(text(x) for x in dirs))
        check(prefix + ".est_minutes", type(m.get("est_minutes")) in (int, float) and m["est_minutes"] > 0)
        expected = 50 if m.get("kind") == "floor" else 40
        # The schema names committed manifest directories, not a second roster.
        # An optional declared count is checked too, never trusted over entries.
        if "run_count" in m:
            check(prefix + ".run_count", type(m["run_count"]) is int and m["run_count"] == expected)
        if isinstance(dirs, list) and dirs and all(text(x) for x in dirs):
            manifest_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
            if reg.path:
                configs = next((p for p in Path(reg.path).resolve().parents if p.name == "configs"), None)
                if configs and root is None:
                    manifest_root = configs.parent
            count = 0
            try:
                for directory in dirs:
                    relative = Path(directory)
                    if relative.is_absolute() or ".." in relative.parts or relative.parts[0] != "configs":
                        raise ValueError("not a repository config directory")
                    manifest = json.loads((manifest_root / relative / "order_manifest.json").read_text())
                    count += len(manifest["executed_order"])
                check(prefix + ".run_count", count == expected)
            except (OSError, ValueError, KeyError, TypeError):
                check(prefix + ".config_dirs", False)
    check("modules.module_id", len(set(ids)) == len(ids))
    units = d.get("pack_unit", ids)
    check("pack_unit", isinstance(units, list) and all(isinstance(x, str) for x in units)
          and set(units).issubset(set(ids)) and len(set(units)) == len(units))
    corpus = d.get("corpus")
    check("corpus", isinstance(corpus, dict) and integer(corpus.get("planned")))
    if d.get("kind") == "replication":
        check("corpus.planned", isinstance(corpus, dict) and corpus.get("planned") == 18)
    else:
        check("corpus.stop_after_valid", isinstance(corpus, dict) and corpus.get("stop_after_valid") == 12
              and integer(corpus.get("planned"), 12))
    for field in ("target_sessions", "minimum_sessions", "attempts_before_pause"):
        check(field, integer(d.get(field)))
    check("minimum_sessions", integer(d.get("minimum_sessions"), 2 if d.get("kind") == "replication" else 1))
    if integer(d.get("target_sessions")) and integer(d.get("minimum_sessions")):
        check("minimum_sessions", d["minimum_sessions"] <= d["target_sessions"])
    estimators = d.get("estimators")
    check("estimators", isinstance(estimators, list) and (draft or bool(estimators)))
    for i, e in enumerate(estimators if isinstance(estimators, list) else []):
        if not isinstance(e, dict):
            check(f"estimators[{i}]", False)
            continue
        for f in ("name", "library", "function", "version"):
            check(f"estimators[{i}].{f}", f in e and (text(e.get(f)) or (f == "version" and draft and e.get(f) is None)))
        check(f"estimators[{i}].library", text(e.get("library")) and e["library"].startswith("joulewise."))
    stopping = d.get("stopping")
    check("stopping", isinstance(stopping, dict))
    if isinstance(stopping, dict):
        check("stopping.count", integer(stopping.get("count")) and stopping["count"] == d.get("target_sessions"))
        date = stopping.get("end_t0_before")
        try:
            aware = isinstance(date, str) and datetime.fromisoformat(date).utcoffset() is not None
        except ValueError:
            aware = False
        check("stopping.end_t0_before", "end_t0_before" in stopping and (aware or (draft and date is None)))
        p = stopping.get("precision")
        check("stopping.precision", "precision" in stopping and (p is None or (
            isinstance(p, dict) and text(p.get("quantity")) and type(p.get("max_half_width_J")) in (int, float)
            and p["max_half_width_J"] > 0 and text(p.get("evaluator")) and ":" in p["evaluator"])))
    effects = d.get("flag_effects")
    check("flag_effects", isinstance(effects, dict))
    for code, effect in (effects.items() if isinstance(effects, dict) else []):
        check("flag_effects." + code, code in catalog.codes and (effect in EFFECTS or (draft and effect is None)))
    deps = d.get("dependencies")
    check("dependencies", isinstance(deps, list))
    for i, dep in enumerate(deps if isinstance(deps, list) else []):
        check(f"dependencies[{i}]", isinstance(dep, dict) and text(dep.get("pack_id"))
              and dep.get("use") == "floors" and dep.get("pairing") == "same_round_else_next_counting")
    check("blinding", d.get("blinding") == {"hidden_offset": True})
    check("interleave", d.get("interleave", "none") in ("none", "quad_round_robin"))
    return sorted(set(errors))


def open_packs(checkout: str | Path, *, run: Callable, rejected: Callable = lambda *args: None) -> list[Registration]:
    """Git observations use the caller's runner; never observe data archives."""
    root = Path(checkout)
    opened = []
    for path in sorted((root / "configs/b6/packs").glob("*/registration.json")):
        relative = path.relative_to(root).as_posix()
        argv = ["git", "-C", str(root)]
        try:
            reg = load(path)
            tracked = run(argv + ["ls-files", "--error-unmatch", "--", relative])
            dirty = run(argv + ["status", "--porcelain", "--", relative])
            catalog = load_catalog(root / reg.flag_catalog)
            problems = validate(reg, catalog, root=root)
            if tracked.returncode or dirty.returncode or dirty.stdout.strip():
                problems.append("untracked_or_dirty")
            if reg.status != "registered":
                problems.append("draft")
            if not problems:
                stamp = run(argv + ["log", "-1", "--format=%ct", "--", relative])
                if stamp.returncode or not stamp.stdout.strip():
                    problems.append("commit_time_unavailable")
                else:
                    opened.append(replace(reg, commit_time=int(stamp.stdout.strip())))
            if problems:
                rejected(relative, problems)
        except (OSError, ValueError, AttributeError, TypeError) as exc:
            rejected(relative, [type(exc).__name__])
    return opened
