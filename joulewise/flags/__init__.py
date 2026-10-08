"""Recorded flags for block-5 windows: facts that never stop collection.

Doctrine (Ed, 2026-10-05, "Physics refuses; everything else is a flag"): only
the hazard modules (``joulewise.hazards``) may refuse an arm. Every other check
is written here as a ``joulewise.flag.v1`` record. The sealed flag catalog
decides, per code, whether a flag excludes a member, excludes a window, or is
only disclosed; :func:`joulewise.flags.exclusions.compute` applies it blind.

Modules:

- :mod:`joulewise.flags.schema` -- the record, its identity and validation.
- :mod:`joulewise.flags.catalog` -- catalog loader and the draft code table.
- :mod:`joulewise.flags.sink` -- append-only, fsync-per-line, deduplicating sink.
- :mod:`joulewise.flags.collect` -- record-only desk/arm collectors, each run in
  a subprocess with a timeout.
- :mod:`joulewise.flags.exclusions` -- the pure exclusion function, the
  physics-in-span joins (plan section 3.4) and the cell unit minimum (3.5).

Nothing in this package imports the retired arm path (``arm_readiness*``,
``capture_t0_step``, ``launch_window``, ``t0_rehearsal``, ``v5_qualification``);
``tests/flags/test_flags_import_graph.py`` enforces that.
"""

from __future__ import annotations

FLAG_SCHEMA = "joulewise.flag.v1"

__all__ = ["FLAG_SCHEMA"]
