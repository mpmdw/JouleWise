"""Shared fail-closed cooldown-trace disposition semantics."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def cooldown_disposition_from_raw(rows: Sequence[Any]) -> str | None:
    """Return the controller-equivalent terminal disposition, or ``None``.

    The cap is causal and wins when the release criterion becomes true only
    after the cap. Both terminal fields are required so arbitrary workload
    JSONL cannot be relabelled as cooldown evidence.
    """

    if not rows:
        return None
    terminal = rows[-1]
    if not isinstance(terminal, Mapping):
        return None
    released = terminal.get("release")
    released_late = terminal.get("release_criteria_met_late")
    if not isinstance(released, bool) or not isinstance(released_late, bool):
        return None
    if released is False:
        return "cap_hit"
    if released is True and released_late is False:
        return "recovered"
    return None
