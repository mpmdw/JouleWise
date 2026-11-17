Synthetic span outputs from the pinned runners' own `mock` (no host, no model, no sensor):

- `b4b6aeb19/`: `scripts/cadence_legs_runner.py mock` at b4b6aeb19 on `cl-dev-02.json`, L001-L006.
- `2d347f721/`: the same at 2d347f721 on `cl-dev-04.v1.1.json`, L001-L006.

t0 2026-11-17 13:20 local, batch window 02:00-02:35. Only the receipt's absolute soak-reference path was rewritten to /SPAN/.
Neither runner writes `soak_attempts` (RL-171's retry came later). `tests/cadence/test_desk_final.py` regenerates them when the pins are in the clone.
