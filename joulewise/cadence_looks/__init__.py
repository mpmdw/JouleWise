"""Look manifests for the conditionless calibration campaign (RL-150 R4).

This package holds the manifest validator. The fit code that a look runs will live beside it
(``joulewise/cadence_looks/fit_*.py``), never under ``joulewise/cadence``: the runner and the leg
runtime must never import it (RL-150 R4), and adding it must change no leg kit's frozen path.
"""
