# Magistrate ruling — the pipeline smoke (D-158; T26, 2026-08-27)

Ed's forcing problem: "you need a shorter minimal way to verify the
instrument, not a whole 168h thing, to speed up this iterative full
pipeline test." Three blind seats (Sol xhigh, Opus 5, Fable 5) produced
the same stage map, the same holes, the same design shape and the same
48-hour cut. This ruling binds implementation stream S10.

## Findings (three-seat convergence)

F-1. The S-0 clone proof stops at the mint. The uncovered span is
launch → collection → finalization → claim edge, and D-157 lived there.
The D-139 shakedown does not cover it either (calibration purity + one
strict bundle; it never generates, freezes, finalizes or analyzes).

F-2. Three further holes in the stage map, each transaction-relevant
(routed to the S9 sweep for refutation; treated as true until refuted):
(a) `scripts/finalize_analysis_manifest.py` — the only place the
prospective manifest is validated before the claim edge — is invoked by
NO runbook phase, script or config (orphan stage); (b) the T-0
`window.env` 25-key allowlist in `capture_t0_step.py` refuses keys the
runbook tells the operator to bind; (c) `run_campaign.load_analysis_manifest`
routes v1/v2 only — the collector never opens the v3 manifest it collects
for. Also (Opus): no stage before the claim edge checks that a floor
artifact exists for each declared floor dependency.

F-3. All four historical defects (D-157, S0-O2, 3e/3f, the launcher
argument gap) share one signature — a contract-required input with no
supply line or no producer-side check — and a smoke that runs every
producer against its real consumer is the general detector for the class.

## Rulings

R-1. **PIPELINE-SMOKE-01 (desk replay, CI, minutes).** One entry point
drives the REAL chain on a throwaway generation: real generator into an
`--output-root` outside `configs/` with a `generation_kind: pipeline_smoke`
/ `claim_eligible: false` family (Sol) whose configs declare mock runtime
and mock telemetry so `mock_telemetry_claim_ineligible` is a config BYTE
in every bundle (Opus — the fence that cannot be forgotten); real freeze
(with W-10's admission check); diagnostic arm / T-0 / launch-capability
consumption via dry-run receipts (`readiness_dry_run_used_as_arm_record`
refuses them as arms — Fable); real `run_campaign` with `--cli-cmd` and
the existing fake collector seam (`tests/test_run_campaign.py make_fake_cli`,
`FakeClock`); real finalizer; real `analyze-claims`. Production `arm`
categorically refuses `generation_kind=pipeline_smoke`; the family never
enters `d117_row_registry_v2` or any marker. Tier-2 (replayed real
powermetrics trace through `PowermetricsTelemetryAdapter(executable=
tests/fixtures/fake_powermetrics_process.py)`) needs one new fail-closed
dev seam and follows tier-1.

R-2. **The pass predicate is mechanical and checked in.** A partition of
`REASON_CODES` into DATA (Sol's list: `effect_not_above_floor`,
`multiplicity_not_rejected`, `equivalence_not_supported`,
`equivalence_margin_not_above_floor`, `interpolation_bound_exceeds_floor`,
`interpolation_bound_exceeds_half_effect`,
`deterministic_bound_obscures_direction`, the randomization/LOO
sensitivity set, and `outcome == unresolved` with an EMPTY reason list —
Opus) versus CONTRACT (everything else, plus any exception). PASS = every
declared contrast returns a schema-valid verdict whose reasons are wholly
DATA, and `mock_telemetry_claim_ineligible` is present exactly once as
the lock. Dead vocabulary the code never emits (Opus's list) is excluded
from the table by a test that asserts each listed code is reachable.

R-3. **PIPELINE-SMOKE-LIVE-01 (~20 min, Ed's machine).** Decode contrast
only, `fixed_n = 1`, one ABBA block (2 runs × 2 conditions), two full
protocol-v3 calibration brackets, real MLX / powermetrics / `prewindow_check.sh`
/ `launch_window.py` execve; quarantined under a smoke pack id with its
own runs root outside the measurement checkout, never marker-signed. It
proves the hardware seam the replay cannot (powermetrics binary binding,
FD-198 handoff across execve, `window.env` allowlist against the real
chain, boot-session/clock at T-0). Runs under D-139/D-142's diagnostic
license; Ed's hands only for anything D-127/D-149 reserves.

R-4. **The 48-hour cut (W-11), in this order, before the `_v4` night:**
(1) W-10's mint-time admission (S8, in flight) — the smoke's first
assertion; (2) the reason-code partition + `assert_data_reason_only()`
with its reachability test; (3) the S6+S7 tail as a CI test — regenerated
manifest → `finalize_analysis_manifest.py` on a canned collection
(fixtures `d117_postcollection_trust`, `p2038_v3_production`) →
`analyze-claims` → predicate; (4) an exact launcher-argv regression that
renders the runbook's launch line with a non-default confirmation-table
path and executes it against the real parser; (5) the `window.env`
allowlist assertion against the runbook's bound keys. DEFERRED past the
night: tier-1 full S1→S9 chaining, tier-2 replay seam, and the live
variant (unless Ed schedules the 20 minutes the evening before — it is
worth it if he does).

R-5. **The runbook gains a finalization phase.** If S9 confirms F-2(a),
the real-transaction runbook and `window_runbook.md` gain the operator
line that runs `finalize_analysis_manifest.py` after campaign close and
before any claim consumption (as a docs PR through S1's runbook stream);
the smoke's tail test is the regression that it stays reachable.

R-6. Kernel rows PIPELINE-SMOKE-01 and PIPELINE-SMOKE-LIVE-01 are
registered in the end-of-sprint wave with this file as authority; the
48-hour cut is W-11 on the pre-window worklist.

## Custody
`00-brief.md`, `01-sol-seat.md`, `02-opus-seat.md`, `03-fable-seat.md`
(verbatim); implementation stream S10 on `feat/pipeline-smoke-w11`.
