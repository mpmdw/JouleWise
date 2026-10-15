# Block 6 registration inputs

The registration seat fills and commits this directory before round 1. Loaders
and validation are in `joulewise/b6/registration.py`; unreadable acceptance
values are recorded as `precheck.acceptance_unavailable`.

| File | Schema | Contents and owner |
|---|---|---|
| `acceptance.json` (absent) | `joulewise.b6_acceptance_registration.v1` | Registration seat: fresh quiet-machine acceptance, stop line and registered code identity. S-4 through S-9 remain open; no calibration constants are supplied here. |
| `identity_pins.json` | `joulewise.b5_identity_pins.v1`, `schema_identity_pins.json` | Exact copy of block 5's committed pins for S-18; registration seat confirms the copy at S-1. |
| `sizing_b5.json` | `joulewise.b5_sizing.v1`, `schema_sizing_b5.json` | Exact copy of block 5's committed sizing, used for the replication plan allowances. |
| `precheck_thresholds.json` (optional, absent) | Sparse object matching `precheck.PRECHECK_DEFAULTS`, checked by `load_precheck_thresholds` | Registration seat supplies only measured overrides; otherwise the existing precheck defaults apply. |

Copies retain their original status fields and all recorded source paths.
Loading these files reads their bytes only and never follows their source paths.
