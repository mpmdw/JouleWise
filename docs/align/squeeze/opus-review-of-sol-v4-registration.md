# Opus 5.5 cross-review: Sol v4-registration seats 1 and 2

2026-11-07. Reviewer: Opus 5.5 (laptop lead's cross-family seat). Inputs:
`align/2026-11-07-sol-v4-registration-seat1@73e8e6d52` and `-seat2@3110a171a`.
Checked against protocol v4 and code on `lane/2026-11-06-v4-r1-integrated@e901eb2a4`,
the W1 kit `lane/2026-11-07-w1-kit-r10@d600baba0`, `RUN_STATE.md` on main
`6f0bfd2d6` (items 202-209), CHAIR.md and OC-TABLE (`b7d5e14c8`). One pass,
read-only. Nothing restricted was opened, and no code was executed.

Legend: **AGREE** means the claim checks against the cited source. **DISAGREE**
means the source contradicts it or a better option exists. **UNVERIFIABLE**
means the claim needs native or R1 data, or is a design proposal with no repo
ground truth.

## Verdict

Both seats are sound and agree with each other on about 85% of the substance.
Both reach the same top-line verdict: do not register or arm W1 on `e901eb2a4`
or `d600baba0`. Every code defect I spot-checked is real. Seat 1 is more
accurate on authority (R0-L2 has already ruled on D5). Seat 2's deviations on
the seed tag and on U6 are cheaper and more proportionate. Both seats
over-scope, though: about 20 P0 items each, many of them code-level guards
that a lead-signed checklist line would cover. Under Ed's proportionate-care
direction (11-06), adopt the science items in full and downgrade most
mechanism items (see "Proportionality" below).

## Claim checks

| # | Claim (seat) | Mark | Reason (source) |
|---|---|---|---|
| 1 | Protocol still DRAFT; `require_w1_ready` has no registration-receipt check (S1 A0, S2 0) | AGREE | `pilot_protocol_v4.md:3 @e901` "DRAFT SKELETON"; `align_v4_kit.py:1226-1234 @d600` checks inputs, R1 slots, the 1(f) receipt, sizing and WP18 only |
| 2 | Need a registration receipt bound to the exact candidate, acyclic manifest (S1, S2) | AGREE (scope) | The need is real. An acyclic manifest plus a forged-verdict test suite is heavier than needed: a lead-signed manifest digest checked at prepare/install covers it |
| 3 | No battery SoC/IsCharging/OBC arm check; protocol still says 95 % (S1 R4, S2 1) | AGREE | `align_v4_session.py @e901` reads only `pmset -g custom` (power mode); `pilot_protocol_v4.md:698` says "battery ≥95%"; CHAIR:78 says ≥99 % within about 30 min |
| 4 | Battery window bar: zero charging-affected contrast members (S1) vs ≤1 per model-window (S2) | UNVERIFIABLE | Both are new numbers that CHAIR does not set. They are compatible, since S1's covers the contrast and S2's the window. The lead must pick one; S2's is the simpler rule |
| 5 | U3 bar still the old `3*max(2.97,.0011E)` same-ordinal constant (S1 R5, S2 2) | AGREE | `thermal_desk.py` `identical_pair`: `margin = 3*max(2.97, .0011*energy)`; OC-TABLE:126 says "its bar re-derivation is still owed" |
| 6 | The numeric U3 bar cannot be filled from desk; it needs a lead pilot-summary derivation (S1, S2) | AGREE | Correct refusal. Both reject option (c), "keep the constant"; both are right |
| 7 | U5 kit accepts any U5 verdict as long as c=1.0 (S2 3) | AGREE | `align_v4_kit.py:270-272 @e901`: `u5.get('verdict') not in U5_VERDICTS` passes FAIL/INCONCLUSIVE |
| 8 | CHAIR names W1 "5 and 18" for E_ref and cross-day identity, but the swap made the replay 17 (S1, S2) | AGREE | CHAIR:100, :240 say "5 and 18"; protocol table :121-123 puts the replay at 17 and the seed-93 development member at 18; the `u4_reference` error text also says "5 and 18" |
| 9 | U6 helper uses a normal 1.645 interval (S1, S2) | AGREE | `v4_estimands.py` `u6_stability`: `ci = [effect - 1.645*se, ...]` |
| 10 | U6 only about 4 % pass at m=21/pair; series ≤15 % target uncertified (S1, S2) | AGREE | OC-TABLE:150-163 |
| 11 | U6 remedy: keep margin, allow honest unresolved, rerun OC at Q6 m (S1) vs descope to diagnostic by deviation (S2) | DISAGREE (both incomplete) | Neither re-scaled to Q6. At m=39/pair the OC half-width scales to about 0.52·√(21/39) ≈ 0.38 s_r, so the null pass rate is about 40 %, not 4 %. Rerun the OC at m=39 first (desk, minutes). If pass stays under ~50 %, adopt S2's diagnostic deviation |
| 12 | Contrast desk: no stage term, df=4, accepts negative same-sign differences (S1 R9, S2 4) | AGREE | `deciding_experiment`: 4-column x, rule string "df=4", `d['X']*d['Y'] > 0` with \|d\|≥10 confirms two −15 J differences |
| 13 | Delivery test per template (S1) vs pooled (S2) | AGREE with S1 | Per-template keeps one template's delivery from licensing the other; same cost |
| 14 | Checkpoints already off; rebuild re-feed accounting still owed (S1 R11, S2 5) | AGREE | `pilot_protocol_v4.md:82-91` off; chair 11 is still in the open list |
| 15 | Sentinel alternate is bank/benign s93; ordinal 18 cannot stand in for the spam reference (S1 R15, S2 6) | AGREE | CHAIR:182; RUN_STATE 203 R10-3 calls 18 "the alternate sentinel"; mixing tasks in E_ref would be invalid |
| 16 | W1 is a second slot-filling pass; the frozen-slot helper names only 4 keys (S1 R17, S2 7) | AGREE | `FROZEN_D_SLOT_KEYS` holds 4 keys; the cohort key needs model, stack and bands too |
| 17 | Offload rehash at arm conflicts with the "no external volume mounted" rule; use a 24 h daytime receipt (S1 R20, S2 9) | AGREE (gap) / UNVERIFIABLE (24 h) | The contradiction is real (prearm audit :138). 24 h is a new number. A signed lead note will do; no new code is needed |
| 18 | WP19 still owed; protocol puts WP18→WP19 before R1 (S2 10, S1 A1) | AGREE | `pilot_protocol_v4.md:695`. Both correctly say native Y identity cannot come from R1's single X-G |
| 19 | R10 contrast proof runs only under a receipt; no-receipt path keeps the old gap and needs a lead supersession (S1 A2, S2 11) | AGREE | LR2 cold-review MEDIUM-2 @d600: "with NO receipt the kit must behave exactly as at e901eb2a4 ... INCONCLUSIVE X-G does not refuse" |
| 20 | Duty fallback passes on step∈{1,2,3} plus any authority string (S1 A3, S2 12) | AGREE | `align_v4_kit.py:298-302 @d600`; LR2 R10 (a) "OPEN ... no code" |
| 21 | Protocol classifier text is the old t63 rule; code is D1-D6 (S1 A6, S2 13) | AGREE | `pilot_protocol_v4.md:221-230` t63 table vs `smc_enumeration.py` |
| 22 | **D5 slow pick still needs a final lead ruling before R1** (S2 13, exec summary) | **DISAGREE** | Ruled: RUN_STATE item 202 **R0-L2** adopts longest band hold ≤300 s as final. S2 cited LR2:730, which predates R0-L2. S1 is correct ("do not reopen") |
| 23 | D seed tag: adopt `-8bit` now per chair 25 (S1) vs label-only deviation keeping `qwen3.8-27b` (S2) | AGREE with S2 | Both are valid. R1 has not run (item 209: R0 re-run 11 pending), so S1's rename is still cheap, but it re-cuts the R1 kit on the critical path for a cosmetic gain. S2's deviation keeps quantization in the config identity and drops only an unclaimed CRN inference |
| 24 | Member-5 loss: protocol's "`--max-failures 1` stops the stage" is false; keep the current chain, fix the text (S1 A5, S2 15) | AGREE | `pilot_protocol_v4.md:308-309` vs prearm audit :167-176. Both rightly avoid new chain code |
| 25 | R1 in-process schedule ≠ W1 cooldown/fresh child; fit is a phase-sum bound (S1 A7, S2 16) | AGREE (gap) / UNVERIFIABLE (size) | The source traces hold; the bias size needs native timing. Neither seat holds R1 for it, correctly |
| 26 | Ruling-76 observer test conflict; courier skips deadman restore (S1 A8, S2 17) | AGREE as cited | Taken from the prearm audit; not rerun here. Both correctly scope it to TRANSACTION_PACK |
| 27 | Q4/Q6 affirmative; protocol still says registration grade "defaults off" (S1 A9, S2 18) | AGREE | RUN_STATE 204 vs `pilot_protocol_v4.md:520-521` |
| 28 | 3 nominal windows give 21 benign/pair; D6 gives about 42 before losses (S1) | AGREE | 7/pair/window, matching protocol:612 (≥21 by D3, cap D6 under registration grade) |
| 29 | Rank ceil(.95(m+1))=38 at m=39 gives a 5 % bound; the explainer advertises the max and 2.5 %; reconcile (S1, S2) | AGREE | `energy-tripwire.html:151` says "largest residual ... 2.5 % at m ≥ 39". Protocol rank formula gives 38 |
| 30 | Use max-score per channel (α=.025 each) so energy OR transcript is ≤5 % by union bound (S1) | AGREE (recommend) | Arithmetic is right (1/40 each). It also makes the public explainer true as written. S2 only flags the choice |
| 31 | Carrier helper thresholds against other carriers at the same H; a common shift leaves detection flat; `>=` counts ties (S1, S2) | AGREE | `benign_carrier_curve`: `others = ... r in group` grouped by (pair, h); `subturn_h_star` uses `>=`. Both seats' synthetic probes (1/21 at every H) match the code |
| 32 | `conformal_threshold_diagnostics` uses sample-max formulas regardless of rank (S2 19) | AGREE | Uses `scores[-1]`, `scores[-2]` unconditionally |
| 33 | v4 omission estimand ≠ squeeze; needs a separate addendum with external DC, real hidden compute and an adaptive attacker (S1 A10, S2 20) | AGREE | `pilot_protocol_v4.md:508-516` changes counts at fixed joules only. Both refuse a product-of-miss-rates claim |
| 34 | Blind Fable+Opus gate checklists (S1 10 boxes, S2 10 steps) | AGREE (scope) | Content is right. Merge them into one packet spec, and cap the gate at one round plus a delta round, per proportionate care |

## Where the two seats agree

Same verdict. Same nine chair rows plus WP19, the receipt, battery, the U3
refusal, the 5/17 correction, contrast stage/sign/df, the no-receipt
supersession, the duty no-op, classifier drift, the member-5 text fix, the
schedule-boundary caveat, Q6 rank vs max, both carrier-helper defects and a
separate squeeze addendum. Independent agreement on items 1-3, 5-10, 12, 14-21,
24-33 gives cross-family k=3 (S1, S2, Opus).

**Real splits** (lead to rule): D5 (#22, S1 right); seed tag (#23, prefer S2);
U6 (#11, run the m=39 OC first); battery bar (#4); delivery denominator (#13,
prefer S1).

## What both missed

1. **Item 209 (R0-L3) adds a W1 gate.** The #694 rebase onto #699 needs its own
   delta review "before W1, not before R0 or R1". It postdates both seats'
   intake (`be3cc8b68`), so it is not a seat error, but it belongs on the merged list.
2. **U6 at Q6 size.** Neither scaled the OC to m=39 (#11). The U6 decision
   should follow that number, not the m=21 one.
3. **D6 cap fragility.** At 7 benign/pair/window, D6 yields 42. One U1-U3-failed
   window (which removes all 7) leaves 35 < 39. Registration grade then fails
   at the cap with high prior probability. Before W1, prospectively set the
   extension cap (D7/D8) or accept "insufficient calibration" as a likely
   registered outcome. S1 gestures at a count-only amendment; neither sized it.
4. **Proportionality.** Neither seat ranks by claim risk. Science-bearing items
   that should be P0: #5-12, #15, #19, #22-23, #27-33. Items that can be one
   checklist line each instead of new kit code plus mutation suites: #2's forge
   tests, #3's ioreg/OBC parsers (Ed signs the arm), #17, #25, #26. That is
   roughly half the engineering in either list.
5. **Explainer as a registration artifact.** `energy-tripwire.html` is public
   and already states the m≥39 FPR. Whatever rank is chosen, the explainer
   update belongs in the registration packet, not later.

## Recommended merged disposition (for the agreement job)

Adopt S1's text for A0 (lightened), R4, R5, R9 (per-template), R15, R17, A2,
A3, A5, A6 and A9 (max-score per channel). Adopt S2's SEED-TAG and (after the
m=39 OC) U6-PRECISION deviations, plus its item 19 carrier/rank oracle. Mark
S2's "D5 open" as superseded by R0-L2. Add item 209's #694 delta review and
the D6-cap decision to the pre-W1 list.
