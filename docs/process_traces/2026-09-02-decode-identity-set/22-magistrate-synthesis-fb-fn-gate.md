# Magistrate synthesis of the F-B / F-N cold gate (files 19–21), 2026-09-02

Packet: file 19. Seats: cold Fable ruling (file 20, with its executed
forgery probe custodied as 20a) and Opus 5 contract-lens refutation (file
21); both read-only, packet + primary evidence only; both disclosed harness
contamination (doctrine files auto-loaded) and grounded every conclusion in
executed evidence at the current head `b9b55e90`. This is the magistrate's
synthesis of a SPLIT verdict on Q1 — synthesized, not majority-voted — and
the disposition of every question and every finding against the packet.

## Q1 — classification of F-B (SPLIT; synthesized)

| Seat | Ruling | Rule applied |
| --- | --- | --- |
| Fable | SECOND fix round on F-B; rule 11 met. A closure counts only with a test that fails on removal of the cure; a mis-reported closure does not reset the round count (otherwise a false clause-map row resets rule 11 — the sunk-cost move it exists to stop). | mutation-cure counterfactual rule + rule 11 |
| Opus | FIRST-round finding against the mutation-cure rule; rule 11 NOT met. The round-1 brief (file 07 line 46, now correctly named) named F-B's regression only by cross-reference to F-D's `return frozenset()` mutation, which IS killed; Sol 214 satisfied an under-specified brief and wrote one false clause-map row ("Remove committed-pack digest comparison" — a counterfactual nobody executed). The broken rule is the counterfactual-input rule, which stands alone. | rule 11 counts rounds on a defect, not rounds in a lane |

Both seats agree on every fact: the check at `inputs.py:3898` exists, is
correct, and refuses a self-consistent forgery; no test in
`tests.test_analysis_inputs` (15/15 at the head, incl. the four round-1b
label tests) fails when it is replaced by `if False:`; a biting fixture is
buildable today from `_generated_frozen_gate_pack` with no new plumbing; the
residual is should-fix, not blocker. Both permit ONE fix round.

Synthesis: the gate was convened on the stricter reading, so the trigger
question is discharged whichever rule is right; what remains is how the
next round is COUNTED. The magistrate adopts the Fable count for that
purpose: round 2's F-B test is fix round 2 on F-B. If it, too, fails to bite
under the delta re-audit, that is the standing escalation signature and the
next spend is a consult, not round 3. Opus's reading is recorded as the more
charitable-to-the-seat account and is right that the brief, not Sol, wrote
the under-specification — the corrective (below) is in the brief shape.

Fixture shape for round 2: Fable's 14-step self-consistent forgery (file
20a) — forge `A/decode` to declare a drifted identity, re-render receipt +
sidecar + freeze receipt + sidecar + plan tree, COMMIT, keep the lineage's
honest `pack_sha256` — with the two assertions Fable named and the control
Fable and Opus both require (the same forged pack with a RE-STAMPED lineage
is accepted, proving the pack-tree comparison and nothing upstream decided).
Opus's cheaper marker-key variant (commit any change inside the pack after
capturing the lineage digest) is the floor, not the target: the forgery
variant is defect-shaped because it shows the wrong unit's set would
otherwise be returned. Seam per fixture (Fable finding 3): transport case →
`floor_request_for_evidence` returns `None` AND `_production_floor_resolution`
reason `("consumer_identity_set_unauthenticated",)`; exact-cell case →
`_production_floor_resolution` status `exact`/reasons `()` when the check is
dead (Fable Run B) — the round-2 test asserts on the production seam.

## Q2 — F-N residual and terra F2 (AGREED)

- luna's F-N residual (`U11` inside `D117-U11-IDPIN-PROJECTION` at line 184):
  NOT a first-use violation — a fixed identifier is a value the reader
  reproduces byte-for-byte, not a term doing technical work. Both seats.
  Closed NO CHANGE; an optional five-word parenthetical is a courtesy.
- terra F2: NEW first-round should-fix on round 1b's new paragraph (602–614),
  not a second round on F-N. Both seats. Two limbs hold ("U11 receipt" is a
  third name for the object defined at 567 and 588; "frozen declaration" is
  coined at 613 and defined nowhere); Opus rejects the third limb ("not
  standalone" — R-M5 never required it); Fable would rewrite the paragraph
  as an enumerated list of the gate's exits in gate order because "the
  authentication sequence above" is not something a reader can rebuild the
  two labels from.
- Synthesis on the cure: the writing standard's bar is REPLICATION from the
  text, which is Fable's point, so the paragraph is rewritten as the
  enumerated exit list (that is also what makes the two labels' emission
  rule rebuildable); Opus's two in-place glosses are folded into that
  rewrite ("also called the U11 receipt" at 567; "no frozen set has been
  declared" replaces "frozen declaration").
- Both seats fire the STANDING ESCALATION SIGNATURE on prose: two consecutive
  rounds (1: F-N; 1b: R-M5) produced first-use defects in the same contract
  section from the same instruction. Adopted: the formulation changes —
  the magistrate DICTATES the paragraph in the round-2 brief (dictated-fills
  pattern); the seat verifies every sentence against the code, may correct
  a factual error only with the code line that proves it, and MUST paste a
  first-use table (every noun phrase in the new text → line of first use →
  line of definition) in its report. The delta re-audit checks pedagogy as
  its own dimension.

## Q3 — composition of fix round 2 (AGREED with one Opus carve-out, ruled)

One fix round (Sol xhigh) carrying: F-B's biting test; F-COUPLING's unmocked
production-gate transport test; terra F1's mapping pin; the dictated prose.
Delta re-audit by a different model.

- terra F1: Fable asked for a stated intended mapping; Opus located it —
  R-M3 (file 15) already ruled the default (`… -> floor_transport_inapplicable`;
  no new engine reason). RATIFIED here as the pinned semantics; the pin
  freezes a ruling, not an accident.
- F-G (luna): Opus refuses the brief as written — the round-1 closure was
  delivered exactly as ruled (file 07 F-G clause: pure helper + synthetic
  mismatch), so the finding is against the ruling, and "add a production-
  path test" without settling reachability invites a seat to weaken a
  preceding fail-closed check to manufacture it. RULED (magistrate, from
  the code read at the bench this session, `identity_pins.py:1640–1710`):
  the preceding checks force every declared manifest to carry ≥1 member
  (`manifest_counts == declared_counts`) and exactly one scientific hash
  per manifest (`divergent_manifests`), and `scientific_config_identity`
  (`:218–237`) keeps `workload_profile.suite_manifest_sha256` (it pops only
  `run_id` and strips tags), so distinct manifests yield distinct scientific
  hashes and `len(scientific_hashes) == len(declared_by_manifest)` holds
  whenever the guard is reached — the guard is DOMINATED. Round 2 must
  PROVE that by execution (two manifests, show the typed identity retains
  the field and the hashes differ) and then document it under the repo's
  defensive-unreachable justification pattern
  (`tests/test_arm_readiness_integration.py:583`). If the proof fails, the
  seat builds the production-path fixture WITHOUT touching any preceding
  check and reports which branch it took. Weakening a preceding check is a
  protocol failure.

## Q4 — what a consumer loses today (AGREED)

Nothing, mechanically: the check refuses the forgery now. The loss is
durability — any future edit that drops line 3898 lands green. Opus adds
the compounding loss the packet did not name: with the check dead, the
forged pack's refusal collapses to `('cell_missing', 'consumer_term_unknown')`
(executed), i.e. a silent regression at 3898 also silently re-opens F-M and
undoes round 1b's whole benefit with nothing in the suite going red.

## Findings against the packet — disposition (charter §6)

| Finding | Seat | Disposition |
| --- | --- | --- |
| P1 files 07 and 13 carried swapped filenames; the packet header pointed at 13 for the round-1 brief while citing "file 07 line 46" | Opus (should-fix) | UPHELD and verified (`head` of both files); the two files were renamed back by `git mv` in the commit carrying this synthesis. Packet line 16 is corrected by this addendum, not by rewriting file 19: read "round-1 brief `07-…`; original implementation brief `13-…`". Custody commit `7c87fa71`'s message carries the wrong mapping; it stands as history. |
| P2 Q1 stem embeds "and is correct" | Opus (should-fix) | UPHELD. The seats were convened to test that; it should have arrived as evidence. |
| Evidence transcribed, not pasted (`<scratch>` placeholders, a hand-written echo, missing `----` separator, a grep's output labelled as the command's) | Opus P3, Fable 1 | UPHELD — a PD-1 violation by the assembler for the SECOND consecutive packet (file 25 recorded the first). Executed evidence blocks are pasted from a terminal transcript verbatim or not included. |
| Counterfactual not re-run at the head being decided (`3ac6cffb`, 6 tests, vs `b9b55e90`, 10/15) | Opus P4, Fable 1 | UPHELD (nit); both seats re-ran at the head and the claim held. |
| Packet never asks what authenticates `pack_sha256` upstream | Opus P5 | UPHELD (nit). Opus located the chain (`bundle.py:87–147` calls `authenticate_campaign_launch_lineage` at write time; caller-supplied lineage rejected at `:1056–1062`); the round-2 delta re-audit verifies that chain once. |
| Seam distinction omitted (transport fixture cannot reach `exact`) | Fable 3 | UPHELD; in the brief. |
| F1 mapping needs a stated intended mapping | Fable 5 | UPHELD; ratified above. |
| Q2 framing names the seat's likely out | Fable 4 | UPHELD in form; neither seat's answer was affected. |
| Line citations, terra quote, "other open findings" | both | Verified accurate. |

## What lands next

Fix round 2 brief (file 23): Sol xhigh, WRITE_SCOPE
`tests/test_analysis_inputs.py`, `tests/test_identity_pins.py`,
`tests/test_analysis_engine.py` (or the module where `_floor_engine_reasons`
is testable), `docs/contracts/identity_pin_projection.md`. Delta re-audit
(file 25) by luna (originator of F-B; execution lens) — pedagogy as its own
dimension; then the live P-8 runbook re-run that freezes all three _v5 packs.
