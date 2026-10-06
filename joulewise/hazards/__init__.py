"""Hazard modules: physics refuses; everything else is a flag (Ed, 2026-10-05).

One module per physical hazard, each measuring its quantity directly
(gate-prune plan §2): ``clock``, ``battery``, ``thermal``, ``contention``,
``disk`` and ``instrument``.  ``arm`` runs them in the registered order and
decides GO or NULL from their verdicts and the agent census alone;
``monitor`` samples them continuously inside the window and joins the
readings to member spans.  ``base`` holds the common Measurement/Verdict
shape.

Submodules are imported explicitly (``from joulewise.hazards import clock``);
importing this package imports nothing else.
"""

MODULES = ("clock", "battery", "thermal", "contention", "disk", "instrument")
