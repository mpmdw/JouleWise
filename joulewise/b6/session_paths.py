"""Session-owned destinations, all supplied by roots outside the checkout."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from joulewise.b5.plan import DEFAULT_LEDGER_RELATIVE


def safe_path(path):
    original = Path(path).expanduser()
    resolved = original.resolve()
    if any(word in str(value).lower() for word in ("claude", "codex") for value in (original, resolved)):
        raise ValueError("agent-census substring in session path")
    return resolved


@dataclass(frozen=True)
class SessionPaths:
    measurement: Path
    loop: Path
    staging: Path
    custody: Path
    runs_parent: Path
    backup_claim: Path
    backup_bound: Path
    archive: Path
    export: Path

    @property
    def plan(self):
        return self.custody / "night_plan.json"

    @property
    def terminal(self):
        return self.custody / "night/result.json"

    def json(self):
        return {key: str(value) for key, value in vars(self).items()}


def for_session(measurement, loop_root, session_id, *, block_root=None, staging_root=None, roots=None):
    if not session_id or Path(session_id).name != session_id or session_id in (".", ".."):
        raise ValueError("session id must be one path component")
    measurement, loop_root = safe_path(measurement), safe_path(loop_root)
    base = safe_path(block_root or loop_root.parent) / "sessions" / session_id
    values = {"measurement": measurement, "loop": loop_root,
              "staging": staging_root or loop_root / "staging" / session_id,
              "custody": base / "custody", "runs_parent": base / "runs-parent",
              "backup_claim": base / "backup-claim", "backup_bound": base / "backup-bound",
              "archive": base / "archive", "export": base / "export"}
    values.update(roots or {})
    values = {key: safe_path(value) for key, value in values.items()}
    for key, path in values.items():
        if key != "measurement" and path.is_relative_to(measurement):
            raise ValueError("session destinations must be outside the measurement checkout")
    return SessionPaths(**values)


def disk_targets(paths, *, stat=os.stat):
    """Read headroom on every destination, budget the total writes once per device."""
    targets = (paths.measurement, paths.measurement / DEFAULT_LEDGER_RELATIVE, paths.runs_parent,
               paths.custody, paths.backup_claim, paths.backup_bound, paths.archive, paths.loop, paths.staging,
               paths.export)
    seen, rows = set(), []
    for target in targets:
        while True:
            try:
                device = stat(str(target)).st_dev
                break
            except FileNotFoundError:
                if target.parent == target:
                    raise
                target = target.parent
        rows.append({"path": str(target), "copies": int(device not in seen)})
        seen.add(device)
    return rows
