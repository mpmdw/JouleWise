"""The block-six night-job courier: a program, never an agent (design 3.1 and 6.4).

Block six sends no mail through an agent; the night job's courier is the
checkout's ``scripts/b6_courier.sh`` (or another program named explicitly), and
a missing courier is never replaced by ``claude`` from PATH. Block-five plans
keep the installer's and the driver's existing behaviour.

Standard library and :mod:`joulewise.agent_identity` only: the night-agent
installer imports this module before the driver's own preflight has shown that
the driver imports (the 2026-09-11 defect), so it must not import the driver.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

DEFAULT_RELATIVE = "scripts/b6_courier.sh"


def block_six_plan(plan: object) -> bool:
    """A block-six window plan: its hazard window carries the ``capture_screen`` binding.

    ``joulewise.b6.plan_inputs.build`` always supplies the binding (null values
    while the registration's acceptance.json is absent); block-five plans never
    carry it, and plans without a hazard window have no ``hazard_window``.
    """

    window = getattr(plan, "hazard_window", None)
    if window is None and isinstance(plan, Mapping):
        window = plan.get("hazard_window")
    bindings = window.get("bindings") if isinstance(window, Mapping) else None
    return isinstance(bindings, Mapping) and "capture_screen" in bindings


def resolve(requested: Path | str | None, measurement_root: Path | str) -> tuple[Path | None, str | None]:
    """The block-six courier, or None and the reason; never an agent, never a substitute."""

    from joulewise.agent_identity import identify

    candidate = Path(requested) if requested is not None else Path(measurement_root) / DEFAULT_RELATIVE
    if not candidate.is_absolute() or not candidate.is_file() or not os.access(candidate, os.X_OK):
        return None, f"block-six program courier is unavailable: {candidate}"
    if identify(str(candidate.resolve()), (str(candidate),)) != "not_agent":
        return None, f"block-six courier must be a program, not an agent: {candidate}"
    return candidate, None
