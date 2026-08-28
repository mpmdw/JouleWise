# Magistrate ruling — the live-proof gate, corrected on executed evidence (D-162; 2026-08-28)

Two seats (Sol high, Fable) converge from code; the Opus seat is pending
and this ruling is amended if it dissents.

## What the seats proved
- A partial run on the real `_v4` pack can NEVER answer for a DATA reason:
  `insufficient_complete_blocks` (`complete_blocks < 2`, `__init__.py:694-697`)
  and `fixed_n_plan_incomplete` (`:698`) are CONTRACT-classed; the
  prospective finalizer itself requires ten blocks / 40 members per
  contrast / 80 total (`analysis_manifest_v3.py:2508, :2596`) and a
  verdict that is both `passed` and claim-licensing (`run_campaign.py:6310`,
  `analysis_manifest_v3.py:3299`). No flag cures arithmetic.
- The diagnostic-family path (A) costs 7–10 Sol-days, touches the three
  generators, freeze/arm admission, T-0/launch, finalizer, engine, reason
  partition and the floor mint, re-triggers estate 11, and installs a new
  admission lane into production days before the campaign — the bypass
  risk is exactly the lane the campaign's unique risks live in.
- A custody copy is not relocatable (`inputs.py:736-784`); a shakedown on
  its own runs root is isolated from the campaign's occurrence/verdict
  accounting (`whole_window.py:531, 2859`; `run_campaign.py:5553`) but an
  extra `_v4` arm is priced by the runbook (it is already the family's
  first real arm, B-3 design).

## The corrected gate (replaces the 2026-08-28 addendum's "DATA reason")
The purpose of the gate is that no CONTRACT defect lies between launch
and the claim edge. That is proved in three modular pieces, none of which
spends a window or adds production code:

G1 — PRE-SHAKEDOWN (desk): estate 11 green at the reviewed head (mint,
freeze, marker, probes on real MLX freezes); the W-11 desk tail on the
REGENERATED `_v4` manifest (finalize → claim edge on a canned collection
refuses only for the expected count reasons; the D-157 mutation refuses
for a contract reason); the S11 five assertions + D-160 F-5 joins packaged
as one runnable script over a runs root.

G2 — THE SHAKEDOWN NIGHT (real pack, real telemetry, one A/B/B/A block on
the shakedown's own non-claim runs root — B-3): reach the whole-window
verdict and build the bracket binding on REAL bytes; at the desk, run the
G1 script over the shakedown bundles (manifest id/sha non-null and equal
to the pack's; cooldown join non-empty; no `campaign_cooldown_evidence_missing`;
null-bound stages null; the gamma manifest_id present); then run
`finalize_analysis_manifest.py` and require that its refusal set equals
EXACTLY the expected incompleteness set (`fixed_n_plan_incomplete` /
member-count codes / `insufficient_complete_blocks`) and nothing else — a
refusal that reaches the count check has passed every contract check
before it. Any other code halts the transaction before the campaign.

G3 — EVERY CAMPAIGN NIGHT: after each window closes, the same desk script
over that night's real bundles, before the next night arms. A failure
costs one night, not the week. This is the modular verification Ed asked
for; it is written into the runbook as a per-night desk step.

## Rulings
R-1. Path A (diagnostic family) is NOT built pre-campaign. It is registered
post-campaign as the substrate of PIPELINE-SMOKE-TIER2-01 (the permanent
desk clean leg), where its bypass risk is irrelevant to the `_v4` claims.
R-2. The shakedown runsheet is re-cut from PR #225's Phases to G2 (same
pack, shakedown runs root, one block, then the desk script and the
expected-refusal-set assertion); `preflight.sh` stands.
R-3. The G1/G2/G3 desk script (`scripts/check_window_provenance.py` or
similar; read-only over a runs root + custody; prints PASS/FAIL per
assertion) is the one small code deliverable; no production gate changes.
R-4. The calendar stands: estate 11 + G1 Fri 08-28; shakedown + G2 Sat
08-29; campaign from Sun 08-30 with G3 nightly.
