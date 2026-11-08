"""Committed and tracked acquisition/reduction changes and their reviews."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Mapping, Sequence

from joulewise.b5.harvest import _porcelain_path


def _tracked_paths(porcelain: str) -> set[str]:
    paths = set()
    for line in porcelain.splitlines():
        if not line.strip() or line.startswith("??"):
            continue
        body = line[3:]
        renamed = re.fullmatch(r'("(?:\\.|[^"\\])*"|.*?) -> ("(?:\\.|[^"\\])*"|.*)', body)
        names = renamed.groups() if renamed and any(c in line[:2] for c in "RC") else (body,)
        paths.update(_porcelain_path(name) for name in names)
    return paths


def check(repo: Path | str, registered: str, executed: str | None,
          paths: Sequence[str], reviewed: Sequence, tracked_edits: str | None = None) -> dict:
    result = {"registered": registered, "executed": executed,
              "changed": [], "number_bearing_changed": [], "unreviewed": [], "flags": []}
    tracked = _tracked_paths(tracked_edits) if isinstance(tracked_edits, str) else set()
    if not isinstance(tracked_edits, str):
        result["flags"].append("code.tracked_edits_unrecorded")
    if executed is None:
        result["flags"].append("code.executed_head_unrecorded")

    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *args], check=True,
                              capture_output=True, text=True).stdout

    try:
        committed = set(filter(None, git("diff", "--no-renames", "--name-only", "-z",
                                        registered, executed, "--").split("\0"))) if executed and registered != executed else set()
    except (OSError, subprocess.SubprocessError, TypeError, ValueError):
        committed = set()
        result["flags"].append("code.identity_unmeasured")
    changed = sorted(committed | tracked)
    numbers = [path for path in changed if path in paths]
    commits = set()
    if not isinstance(reviewed, (list, tuple)):
        reviewed = []
        result["flags"].append("code.identity_unmeasured")
    for row in reviewed:
        commit = row.get("commit") if isinstance(row, Mapping) else row
        if isinstance(commit, str):
            commits.add(commit)
        elif "code.identity_unmeasured" not in result["flags"]:
            result["flags"].append("code.identity_unmeasured")
    unreviewed = []
    for path in numbers:
        try:
            if path in tracked or git("log", "-1", "--format=%H", executed, "--", path).strip() not in commits:
                unreviewed.append(path)
        except (OSError, subprocess.SubprocessError, TypeError, ValueError):
            if "code.identity_unmeasured" not in result["flags"]:
                result["flags"].append("code.identity_unmeasured")
    result.update(changed=changed, number_bearing_changed=numbers, unreviewed=unreviewed)
    if changed:
        result["flags"].append("code.changed_since_registration")
    if unreviewed:
        result["flags"].append("code.number_bearing_unreviewed")
    return result
