# Magistrate ruling — the smoke corpus (D-160; T26, 2026-08-27)

Trigger: three consecutive rulings (D-158 R-1, R-4(3), A-2) assumed an
evidence-production path that had never been executed; each was falsified
by execution. Per the standing rule the next spend was a consult. Three
blind seats (Sol xhigh, Opus 5, Fable 5) answered from code.

## Findings (converged)

F-1. **No path yields a claim-consumable synthetic bundle without a
production-code change** (all three). The fake-collector seam is a
scissor: `telemetry_backend: mock` → `mock_config` true
(`whole_window.py:935`) → `mock_telemetry_claim_ineligible` at
`inputs.py:2753`; `powermetrics` → no plist / no `uncertainty_evidence` →
`bundle_strict_invalid`. Mock is also dead a second way:
`capture_pipeline_absent` (`claims.py:135`) is CONTRACT and not
mock-exempt (Fable).

F-2. **The tier-2 replay seam is not CLI-reachable** (`adapters/__init__.py:153-170`
hard-codes `PowermetricsTelemetryAdapter(clock)`); the p2038 test reaches
strict validity only with a specialised registry, fixture clock,
environment-guard patch and synthetic calibration, and never
whole-windows, cooldown-joins, floor-binds or calls `analyze_claims`
(Sol, Fable). Making it reachable is TWO fail-closed production seams in
the collector, ~2 Sol-days, and each is a fresh custody surface with a
replay-only success-path risk (Sol, Fable).

F-3. **The floor path is closed by construction** (Opus): `inputs.py:3931`
refuses a floor cell with `calibration_scope == "smoke"` as
`cell_not_claim_ready`. A smoke-scoped family cannot reach a DATA
verdict even with the seams, unless the floor rule is relaxed.

F-4. **No producer exists for the `--bracket-binding` file** the finalizer
requires (`finalize_analysis_manifest.py:34`, `inputs.py:727-743`):
`build_calibration_bracket_binding` is in-memory only
(`calibration_bracketing.py:864`, called from `whole_window.py:570`); no
file of that schema exists in the tree (Opus, Sol). Independent of the
smoke: the real `_v4` finalization cannot run as documented.

F-5. Additional joins every clean leg must assert (Opus): cooldown
disposition re-derived from raw JSONL, selected by
`analysis_manifest_id == collection_manifest_id` (`inputs.py:2143`,
`:1982-2034`); whole-window verdict reasons attach to every bundle
(`:3185-3198`); `--runs-root` must equal the bracket binding's
`runs_root` (`:711-784`); supersession scan excludes conflicted bundles
(`:3060-3102`).

## Rulings

R-1. **The desk replay does NOT get a synthetic clean leg before the
night, and the smoke-scoped floor rule is NOT relaxed.** W-11 as landed
(PR #211: mutation legs proving contract refusals fire, the reason
partition, the launcher-argv regression, the window.env assertion) plus
Unit B (production freeze/arm refuse `generation_kind=pipeline_smoke` by
class, `9b3dab83`, lands after #209) is the desk smoke. It proves the
contract-defect class fails loudly in minutes; it does not prove a clean
pass, and the paper and RUN_STATE say so.

R-2. **The end-to-end clean proof is the LIVE ~20-minute run (D-158 R-3),
on a real, tiny, quarantined family generation** — NOT a smoke-scoped
one: real telemetry, its own real floor cells from two calibration
brackets, `fixed_n = 1`, decode-only, one ABBA block; zero production
seams. It requires Ed's machine and is the evening-before item on
ED-ITEMS. F-5's joins are its assertion list, with S11's five.

R-3. **BRACKET-BINDING-CLI-01 is upgraded from "no CLI" to "no producer
at all" and becomes a pre-CLOSE blocker** (finalization ≈ T+7 d after
the night). Assigned to S10 NOW as its next unit: a fail-closed CLI that
serialises `build_calibration_bracket_binding`'s output under custody
(schema `joulewise.calibration_bracket_binding.v1`), with a regression
that the finalizer accepts it and that `--runs-root` equality (F-5) holds.

R-4. **PIPELINE-SMOKE-TIER2-01** is registered post-`_v4` with the design
constraints recorded here: the two seams gated on an authenticated
plan-tree `generation_kind == pipeline_smoke`, hard-pinned fixture
executable/prefix, every F-5 join asserted, no floor-rule change; the
clean leg's floor must come from a real calibration in the replayed
trace, not a smoke-scoped mint.

R-5. Process: three falsified premises in one design is the ruled-not-
installed pattern turned inward — rulings about evidence paths are now
made only after a seat has EXECUTED the path or proven from code that it
cannot execute. Recorded in the cold-gate packet.

## Custody
`00-brief.md`, `01-sol-seat.md`, `02-opus-seat.md`, `03-fable-seat.md`.
