# Block 6 registration inputs

The registration seat fills and commits this directory before round 1. Loaders
and validation are in `joulewise/b6/registration.py`; unreadable acceptance
values are recorded as `precheck.acceptance_unavailable`.

| File | Schema | Contents and owner |
|---|---|---|
| `acceptance.json` | `joulewise.b6_acceptance_registration.v1` | Registration seat (2026-10-17, draft until the cold gate): slot S-4, the fresh calibration acceptance derived from the 13 quiet-machine captures of 2026-10-16/17 by block 5's derivation (alignment reference 0.037054941476587 s, bracket screen 0.010818 s, drift budget 0.01550217418713139 s), and the registered code identity (`registered_commit` main `3bb305d7a`, the base of `executing_reviews.json`). One file serves all three packs (`pack_id` names the family); each pack's stop line stays in `capture_screen.REGISTERED_T10_STOP_S`, so `operative_bound_stop_s` is null. S-6 to S-9 are registration text, not fields here. Derivation: `/Users/edr/night-archive/b6-acceptance/DERIVATION.md`. |
| `identity_pins.json` | `joulewise.b5_identity_pins.v1`, `schema_identity_pins.json` | Block-5 units retained for S-18, with the eleven BYTES science/reference file identities and installed runtime observation under `bytes_c4`; registration seat confirms the final digest at the gate. |
| `sizing_b5.json` | `joulewise.b5_sizing.v1`, `schema_sizing_b5.json` | Exact copy of block 5's committed sizing, used for the replication plan allowances. |
| `precheck_thresholds.json` (optional, absent) | Sparse object matching `precheck.PRECHECK_DEFAULTS`, checked by `load_precheck_thresholds` | Registration seat supplies only measured overrides; otherwise the existing precheck defaults apply. |

Copies retain their original status fields and all recorded source paths.
Loading these files reads their bytes only and never follows their source paths.

BYTES C4 is recorded separately from the historical block-5 evidence. The
`bytes_c4.file_source` is the exact `configs/bytes/identity_pins.json` file
inventory. Its eleven weight identities were rehashed on the Mac, following
file symlinks. Each unit's `bytes_file_evidence` binds the generated dispatch
config inventory, checkpoint quantization, tokenizer/config file hashes and
recorded download revisions. These are file observations. A null configured
8B-8bit revision remains visible alongside its recorded download revision;
the BY-FILL seat owns the source roster/config correction.

`bytes_c4.runtime_observation` records package metadata from the executed
`/Users/edr/code/JouleWise/.venv/bin/python`, its resolved binary digest, and
the separate MLX-LM import result. The build sandbox has no Metal device, so
that import is unavailable. Installed versions are still observed using the
collector's real metadata probe and hashed with `runtime_versions_sha256`.
No model or tokenizer was loaded. A model execution stack and a frozen
projection receipt are not inferred from these observations. All twelve
generated projections use the H author's `unprojected` form with null
execution pins and exact pack-local config copies; the governed freeze
operation remains a later gate.

`desk_identity.collect` independently writes `identity-epoch.json` and
`t1-bindings.json` to session staging. Those live machine/protocol vectors
are consumed by `plan_inputs.build`; they are not the model C4 pin file.
The build-seat attempt could not read `sysctl kern.osversion` in the
sandbox and issued no vectors. Native render tests use isolated fixture
vectors and a matching fixture ledger, not a live calibration receipt.
Block-6 harvest passes this directory's `identity_pins.json` to the model
identity collector. The build-seat inspection found that the native driver's
`production_seams.collectors_argv` still selects
`configs/campaigns/v5_claim_25g83/identity_pins.json`; changing that
out-of-scope consumer requires a lead scope grant. Populating this shared
file alone therefore does not complete the driver's C4 runtime binding.
The runtime session destinations come from
`configs/b6/loop_bytes.json` and `session_paths.for_session`, never from a
test launch declaration or an H non-claim runs root.

Block-6 clock policy (§8.6) is supplied by `b6.plan_inputs.CLOCK_THRESHOLDS`
to both precheck and driver plans: `h_ms = 0`, `frequency_margin_ppm = 0.25`,
`limit_ms = 5`. The hold is therefore 5000 / T_stream_max_s - 0.25 ppm;
at 335 s it is 14.675373 ppm. The band above block 5's `h_ms = 3.7` budget
(3.630597 ppm at 335 s) emits `clock.rate_above_budget` without a hold.
The copied `sizing_b5.json` retains block 5's registered values verbatim.
