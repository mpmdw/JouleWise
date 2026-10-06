"""Block 5's HAZARD_PACK path (gate-prune plan, lane L2).

Ed's ruling of 2026-10-05: an arm refuses only on a physical hazard, measured
directly; every other check is a recorded flag. This package holds the three
pieces of the window that are not hazard measurement:

- ``plan``: the desk-time window plan writer. It walks a v5 pack's committed
  stage graph, binds the fourteen launch bindings, creates fresh runs roots and
  writes ``window.env``, the chain and a ``HAZARD_PACK`` night plan.
- ``chain``: renders the zsh chain from the stage graph. A failed member costs
  only itself; the only chain stops are a failed reservation, a failed
  pre-calibration capture or screen (all before member 1) and a driver stop
  on low disk.
- ``driver``: the ``HAZARD_PACK`` branch of ``scripts/run_night.py`` (agent
  census, hazard arm, lineage, executed-code inventory, monitor, chain, G10,
  terminal record).

Nothing here imports the retired TRANSACTION_PACK arm path at module scope.
"""

RECEIPT_CLASS = "HAZARD_PACK"
