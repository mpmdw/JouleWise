"""Committed acquisition/reduction changes and their executing reviews."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Mapping, Sequence


def check(repo: Path | str, registered: str, executed: str | None,
          paths: Sequence[str], reviewed: Sequence) -> dict:
    result = {"registered": registered, "executed": executed,
              "changed": [], "number_bearing_changed": [], "unreviewed": [], "flags": []}
    if executed is None:
        result["flags"].append("code.executed_head_unrecorded")
        return result
    if registered == executed:
        # An unchanged commit has no changed paths, even in a desk checkout
        # that does not retain the rehearsal clone's historical git objects.
        return result

    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *args], check=True,
                              capture_output=True, text=True).stdout

    changed = sorted(filter(None, git("diff", "--no-renames", "--name-only", "-z",
                                      registered, executed, "--").split("\0")))
    numbers = [path for path in changed if path in paths]
    commits = {row["commit"] if isinstance(row, Mapping) else row for row in reviewed}
    unreviewed = [path for path in numbers
                  if git("log", "-1", "--format=%H", executed, "--", path).strip() not in commits]
    result.update(changed=changed, number_bearing_changed=numbers, unreviewed=unreviewed)
    if changed:
        result["flags"].append("code.changed_since_registration")
    if unreviewed:
        result["flags"].append("code.number_bearing_unreviewed")
    return result
