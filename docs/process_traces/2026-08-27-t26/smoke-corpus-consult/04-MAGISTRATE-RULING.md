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

## Addendum (2026-08-27, post S10 gauntlet on #217) — R-3 shape corrected

R-3 said the producer "serialises `build_calibration_bracket_binding`'s
output", which reads as post-verdict. Executed evidence (refuter A's
probe; director's bench check; `run_campaign.py` has zero references to
the binding; `calibration_bracket_for_bundles` :4646 takes only the
ledger snapshot; the builder at `calibration_bracketing.py:864` takes
ledger + session_id + plan identity + runs_root and NOTHING from a
verdict) shows the evaluator requires the binding as an INPUT: a
binding-less whole-window verdict is `status=failed` with
`calibration_bracket_binding_missing`, so the verdict the first CLI shape
read from can never exist in production.

R-3′ (adopted, option (b)): the lifecycle is **frozen plan + finalized
ledger session → build the binding (from exactly the builder's real
inputs) → `run_campaign --whole-window-verdict --bracket-binding <path>`
with the identity threaded into `calibration_bracket_for_bundles` →
finalize, which checks verdict and file agree byte-for-byte**. Option (a)
(identity flags alone) is insufficient; option (c) (persist provisional
descriptors in a failed verdict) is rejected — unbound evaluation would
pick the identity the binding exists to authorise. The F1 fixture-swap
test is replaced by one production-valid rich verdict carried unchanged
through producer → evaluator → finalizer with hashes asserted equal. The
runbook's H5/H6 gain the "build binding before the whole-window verdict"
ordering note. This lands BEFORE the night so finalization code is inside
the reviewed head; it does not touch pack bytes or the mint path.

## Addendum (2026-08-27, #217 merged) — split verdicts ruled

- **F2 (evaluator authority = ledger session; finalizer authority =
  prospective manifest):** fail-closed overall, a consistency gap, not a
  hole. RULING: not fixed pre-night; registered as
  BRACKET-EVALUATOR-PLAN-IDENTITY-01 (post-`_v4`): the evaluator gains an
  authenticated prospective-manifest/plan-tree identity input so that
  producer + evaluator success implies finalizer acceptance.
- **F3 (`AuthenticatedConsumptionSession` identity from the binding):**
  refuter A's refutation ADOPTED (redundant, not self-authorizing —
  a mutated identity with a recomputed digest is still refused against the
  ledger); an explicit identity parameter is a post-`_v4` should-fix row
  (touches `whole_window.py`).
- **Scope expansion into `joulewise/analysis_manifest_v3.py`** (16
  additive lines: byte-equality of the binding at finalization; the
  verdict-output no-clobber publish) RATIFIED under R-3′'s "finalization
  code inside the reviewed head".
- **Runbook H5-seal / H6-write conflict:** RULING — analysis outputs
  (bracket binding, whole-window verdict output, finalized manifest) are
  written under a DISTINCT ANALYSIS ROOT, never beneath the sealed
  transaction custody root; the seal at H5 step 7 stays where it is. The
  runbook delta (build binding → evaluate with `--bracket-binding` →
  finalize) lands as a docs PR naming that root.

## Addendum (2026-08-28) — NR-14 ratified

The "distinct analysis root" wording of the previous addendum was not
executable on merged code (seat probes: the evaluator requires the binding
beneath `$RUNS_ROOT`, `run_campaign.py:4884-4920`; the authoritative
verdict row is appended to `$RUNS_ROOT/campaign_log.jsonl`, `:6364`; the
finalizer replays exactly that row, `analysis_manifest_v3.py:3447-3504`).
RULING (NR-14): the runbook's executable placement is RATIFIED — the
bracket binding and the whole-window verdict row live beneath
`$RUNS_ROOT` and are built BEFORE H5 step 1, so `campaign-close.json`
digests them and step 7 seals them; only the finalized manifest goes under
`$ANALYSIS_ROOT` and claims under the sibling `$CLAIMS_ROOT`. No code
change. The aggregate floor artifact path stays `TODO(ruling)` until the
live mini-run shows where the mint places it (FLOOR-BIND-01 context).
Lesson (D-160 R-5 again): rule placement only after a seat has executed it.
