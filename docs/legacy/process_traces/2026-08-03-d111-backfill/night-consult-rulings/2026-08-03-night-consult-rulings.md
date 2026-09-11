# Joint magistrate+Sol rulings under Ed's 16h standing order (2026-08-03 night)

Consult: Sol xhigh, 1 round, thread `019fca16-9e7f-7af2-90e0-090ff6ca878e`.
Authority: Ed's verbatim standing order ("you and sol can consult over
decisions that need me and decide... if the decision is major enough that
you and sol both think I should adjudicate it ping me"). Neither party
judged any of the three questions Ed-escalation-worthy. To be minted as a
decision entry in the end-of-session batch.

## Q1 — Mint-1 re-mint byte-compare: EXECUTE, corrected procedure
Sol refuted the magistrate's premise: the persisted a10 report
(~/JouleWise-window-custody/window_a10_20260725/detection-floor-extraction.json)
is REFUSED (all_cells_extractable: false, sha 629027…) and is NOT the
report mint-1 authenticated (expected sha 77dbcd9d…41d8). Corrected
chain, all scratch-only, zero custody/repo writes:
1. Regenerate a10 report: governed extractor, frozen corpus
   runs_window_a10_20260725, basis 79c6e8b9…e053e, semantics
   d078_authenticated_max_bracket_rederivation_v1, exact spec,
   --hash-bundles, exit 0, all cells extractable, zero refusals.
   REQUIRE byte-match sha 77dbcd9d…41d8.
2. Regenerate window_c report: corpus runs_window_c_20260726, basis
   0cf07a5c…8fa6, semantics d078_minted_envelopes_v1, exact spec.
   REQUIRE byte-match sha 94791d72…6917.
3. Generalized mint replay: mint1.json pinset (sha 4c58e646…9a67),
   original provenance commit 3de370ec…564e/clean, O_EXCL scratch out.
   REQUIRE artifact sha 559ab5ed…1188 + statement sha 925254f3…03d3.
Any mismatch at any step: STOP AND REPORT (tooling-drift signal), never
hand-repair.

## Q2 — Window C at 70W: REFUSED (joint)
No window C while the Anker negotiates 70W (20V×3.5A standard-PD).
Sol's sharpening: constant 70W could PASS adapter-continuity (the gate
requires stable identity, not >=140W) — which is exactly why the
battery-assist hazard matters; the machinery would not catch it.
80% battery cap at RESTORED 140W: ADMISSIBLE with conditions — settled
launch check shows AC Power + external connected + "pd charger"/140.0 +
is_charging=false; cap recorded in close-out; every recorded
pre/admission/post power snapshot manually inspected (adapter continuity
does NOT evaluate is_charging); any charging transition, wattage/source
change, or battery assist => window non-claim-bearing. Re-probe wattage
before any launch decision; all agent sessions closed before measurement.

## Q3 — Governed 7B mint: LICENSED WITH CONDITIONS (no Ed escalation)
Execute tonight ONLY after Q1 is fully byte-identical. Mint outputs
scratch-held, UNLANDED, unconsumed — landing/publication keeps the full
audit/refuter/D-072/cold-gate chain (that is where irreversibility
attaches; mint-1 precedent D-088). PREREQUISITE Sol surfaced: no
production 7B pinset exists (PR #96 landed machinery + mint-1 pinset
only). The magistrate must author + hash the exact 7B pinset first,
pinning at least: operative literal 13.998037, basis 3ff9128b…1173,
semantics d078_authenticated_max_bracket_rederivation_v1, plan sha
62f7ab3b…b388, order-manifest sha bc11a014…08ab, extraction-spec sha
8224af01…0cf, clean report sha bd87d5c4…309a; require
validate_floor_artifact == [] and truthful same-root provenance; O_EXCL
scratch outputs. Artifact ID + pinset path are magistrate-owned choices,
frozen before execution.
