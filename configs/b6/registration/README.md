# Block 6 registration inputs

The registration seat fills and commits this directory before round 1. Loaders
and validation are in `joulewise/b6/registration.py`; unreadable acceptance
values are recorded as `precheck.acceptance_unavailable`.

| File | Schema | Contents and owner |
|---|---|---|
| `acceptance.json` | `joulewise.b6_acceptance_registration.v1` | Registration seat (2026-10-17, draft until the cold gate): slot S-4, the fresh calibration acceptance derived from the 13 quiet-machine captures of 2026-10-16/17 by block 5's derivation (alignment reference 0.037054941476587 s, bracket screen 0.010818 s, drift budget 0.01550217418713139 s), and the registered code identity (`registered_commit` main `3bb305d7a`, the base of `executing_reviews.json`). One file serves all three packs (`pack_id` names the family); each pack's stop line stays in `capture_screen.REGISTERED_T10_STOP_S`, so `operative_bound_stop_s` is null. S-6 to S-9 are registration text, not fields here. Derivation: `/Users/edr/night-archive/b6-acceptance/DERIVATION.md`. |
| `identity_pins.json` | `joulewise.b5_identity_pins.v1`, `schema_identity_pins.json` | Exact copy of block 5's committed pins for S-18; registration seat confirms the copy at S-1. |
| `sizing_b5.json` | `joulewise.b5_sizing.v1`, `schema_sizing_b5.json` | Exact copy of block 5's committed sizing, used for the replication plan allowances. |
| `precheck_thresholds.json` (optional, absent) | Sparse object matching `precheck.PRECHECK_DEFAULTS`, checked by `load_precheck_thresholds` | Registration seat supplies only measured overrides; otherwise the existing precheck defaults apply. |

Copies retain their original status fields and all recorded source paths.
Loading these files reads their bytes only and never follows their source paths.

Block-6 clock policy (§8.6) is supplied by `b6.plan_inputs.CLOCK_THRESHOLDS`
to both precheck and driver plans: `h_ms = 0`, `frequency_margin_ppm = 0.25`,
`limit_ms = 5`. The hold is therefore 5000 / T_stream_max_s - 0.25 ppm;
at 335 s it is 14.675373 ppm. The band above block 5's `h_ms = 3.7` budget
(3.630597 ppm at 335 s) emits `clock.rate_above_budget` without a hold.
The copied `sizing_b5.json` retains block 5's registered values verbatim.
