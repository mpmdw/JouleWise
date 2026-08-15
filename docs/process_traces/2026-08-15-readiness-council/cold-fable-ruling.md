# COLD FABLE ADJUDICATION — INSTRUMENT-READINESS COUNCIL SITTING (verbatim custody)

Provenance: cold Fable instance (rule-11 pairing, adjudicator seat), fresh session, no loop
context, seated 2026-08-15 over the sealed packet (sha16 e68c7fb9fe88ed0b) + charter v2 +
read-only primary-evidence spot-checks at HEAD 8937dec. Relayed verbatim from the agent's
final ruling; the magistrate did not edit content.

---

**Adjudicator:** cold Fable instance, no loop context, seated 2026-08-15.
**Inputs:** charter v2 (read in full); sealed packet `sitting-packet-FINAL.md` (500 lines, read in full; seal line noted); primary-evidence spot-checks at HEAD 8937dec in a read-only worktree (git delta ac3fe1d..8937dec; `state_kernel.json`; RUN_STATE.md:3433; decision log M-2 entry at :8881; pack `draft_status` bytes; `analysis_engine/inputs.py` load_manifest and the contrast pack's `v3.prospective` schema line; independent re-execution of `committed_pack_tree_sha256` over all three packs; the consistency-sweep record in full; L2 seat report coverage section; both pack-digest implementations).

## A. COUNCIL VERDICT

Per-component (charter verdict form):

| Component | Verdict | Basis |
|---|---|---|
| L1 Authority plane (gating) | NOT-READY | B1 (33/33 evidence receipts expired — executed by A-execution refuter), B2 (kernel fail-open — re-confirmed `active_global_gates: []` and the P2-006 READY [QUIET-MAC] row on primary bytes; confirmed by both DG lenses). B3 folded per §D. |
| L2 Calibration acquisition (gating) | NOT-READY (ruling on the fallen READY) | L2-1 raised to blocker (unbounded `detect_pulses` under the writer lease, confirmed with file:line and executed evidence); L2-COV-1 (denominator refuted); L2-EDQ-1 (open ED-QUAL rows — charter amendment 11 makes seat READY with open ED rows a category error the seat itself committed). |
| L3 Capture + telemetry (gating) | NOT-READY | Seat's own verdict; 3 should-fix, 4 open ED rows; no refutation attacked it. |
| L4 Quantitative claim pipeline (gating) | NOT-READY | B1 confirmed by both ECF lenses with the executed `authoritative_input_invalid` refusal on the pack-pinned spec. |
| L5 Pack/readiness/custody (gating) | NOT-READY | 3 should-fix (incl. self-polluting plan tests, stale dry-run binding), open ED row. |
| L6 Seam reader A (gating) | NOT-READY | B1 confirmed (merged with L8-B1 into one T-0 producer defect), B2 confirmed with the freeze-CLI-cannot-reissue qualification. |
| L7 Seam reader B (gating) | NOT-READY | Should-fix set incl. the unchecked monotonic horizon at consume; 3 ED rows. |
| L8 Operator/recovery (gating) | NOT-READY | B1, B2, B5, B6, B7 confirmed; B3 survives as privilege gap (timing premise dead); B4 STRUCK — refuted by both lenses with an executed canonical-path counter-probe; correct fail-closed wrong-checkout refusal, not a defect. |
| L9 Environmental controls (gating) | NOT-READY | B1, B2 confirmed (consolidated to one census-semantics defect); the hazard-register should-fix stands. |
| L10 Sacrificial lifecycle (gating) | NOT-READY | B1 confirmed by both ECF lenses; independently verified `load_manifest` has no `v3.prospective` branch and the contrast manifest declares exactly that schema — the funded gamma window's claim edge is unbuilt. |
| L11 Retained characterization basis (non-gating) | NOT-READY | Outside launch aggregation; its three should-fixes are paper-integrity defects and enter the work-order program on the paper lane. |

On L2 specifically: the READY fell and stays fallen. L2 is NOT-READY, not UNVERIFIED, because a confirmed blocker suffices for NOT-READY regardless of coverage — but its coverage claim is ruled VOID, its work-order list is ruled non-exhaustive, and a re-scoped L2 re-audit with an independently enumerated universe is a mandatory work order.

Aggregate, mechanically applied: council READY requires no NOT-READY, no UNVERIFIED, all ED-QUALIFICATION rows closed. Ten of ten gating seats are NOT-READY and roughly two dozen ED-QUAL rows are open.

### COUNCIL VERDICT: NOT-READY (+ the work-order program ratified in §F).

No funded window may be armed. T-0 GO is not reached and, per the charter, would be a separate later closure even after a READY.

## B. DISPOSITION 1 — baseline drift: ACCEPTED, with one correction and two conditions

Mechanical facts verified independently: `git diff --stat ac3fe1d..8937dec` = exactly README.md, RUN_STATE.md, `docs/process/audit-baseline-manifest.json`; the three commits are the manifest itself plus two checkpoint commits; HEAD remains 8937dec with a clean tree at seating, so the commit freeze held through harvest and seal.

The disposition's conclusion is correct: no lens result is voided. But rationale point 3 as stated is REJECTED. "README.md and RUN_STATE.md are session-state surfaces in no lens's evidence universe" is false on the packet's own face — L1-B2 cites RUN_STATE.md:3433 as evidence, so RUN_STATE is in L1's universe. The disposition survives on the correct ground, point 4: the entire delta predates fleet launch, the eleven worktrees audited the post-delta tree at 8937dec, and nothing landed after it. A lens result is voided when bytes it audited changed underneath it; here the lenses audited the newest bytes. The magistrate reached the right outcome partly through an overbroad claim — noted in §G.

Conditions:
1. The council record must pin the effective audit baseline as 8937dec = ac3fe1d + {manifest, README, RUN_STATE}, so no successor re-derives the drift question.
2. At the next manifest re-pin (mandatory anyway per §F Phase 3): add the charter-required chain-template sha (sweep S4 — the current manifest omits a binding the charter names) and a `pack_digest_algorithm` field. The digests are correct (all three reproduced exactly via `joulewise.arm_readiness.committed_pack_tree_sha256`), but the unnamed algorithm plus a same-named rglob digest in `tests/test_d117_floor_qwen25_1p5b_plan.py` is precisely what produced a false blocker in the sweep. The magistrate's "the manifest requires NO fix" is rejected as too generous.

No re-runs ordered.

## C. DISPOSITION 2 — retroactive M-2 adjudication

(i) Was the override sound on the merits? YES. The `draft_status: "unfrozen_draft"` / "not armable" strings are generator-owned descriptive text predating the freeze machinery; the authenticated freeze receipts and plan-tree pins are the authoritative state. Reading placeholder prose as NO-GO would have deadlocked: the text cannot be regenerated on a frozen pack without rotating the committed digests and voiding the very receipts that prove the freeze. Trading an unauthenticated byte-level invariant for an authenticated receipt-level one was correct. M-2 is UPHELD on retroactive review.

(ii) Is the landed remedy sound? AS ENGINEERING, YES; AS RECORDED, NO. The M-2 ruling text promises the chain-fix batch "regenerates the sidecar-consistent text via the canonical path." Verified at HEAD: all three packs' bytes still read `"draft_status": "unfrozen_draft"` — #149 shipped `freeze_aware_status()` forward-only under preserve-bytes, and the regeneration deliberately did not happen (sweep S3; L1 nit; L5 nit). Preserving frozen bytes was the right engineering call. But the consequence is that a ruling scoped as transitional is now the standing operative instrument for the current packs, and the policy home never says so. The remedy is ruled incomplete: (a) append the M-2 execution note to the decision log — forward-only; legacy wording on the current frozen packs is overridden by the freeze receipt's presence for their lifetime; (b) the re-freeze / successor-pack work order (mandatory anyway under L1-B1) must produce truthful freeze-aware status text, at which point the M-2 override retires. An override that quietly converts from transitional to permanent without a recorded decision is exactly the drift class this audit exists to catch.

(iii) Reliance re-review? NO backward re-review needed. The override is scoped to one descriptive field; no quantitative consumer reads `draft_status`; L5 independently audited the packs' current text; the arm path refuses at baseline regardless (expiry). The reliance is forward: every arm night until the re-freeze needs M-2 in hand to pass the §5C entry gate (L8-B4's residue). The successor arm packet must therefore carry the M-2 citation explicitly until the re-freeze lands.

(iv) Process consequence of the missed mandatory trigger. The retroactive submission is accepted as cure for this instance only — it does not establish retroactive review as an acceptable substitute for the ex-ante gate. The structural fact: a magistrate under packet-finalization time pressure overrode a NO-GO reading and did not notice the rule-11 trigger; the drafting mechanic's flag caught it later. Consequence ordered: the mechanic's checklist gains a mechanical rule-11 trigger enumeration over every ruling entered in the decision log — any entry containing an override, reversal, or reinterpretation of a stop signal or verdict raises a flag that blocks packet finalization until a cold-gate artifact exists or the magistrate records written dissent for Ed. The C-058 zero-cold-gates-in-span anomaly is confirmed as a real signal, not noise.

## D. SEVERITY SYNTHESIS — L1-B3 authority bifurcation: SHOULD-FIX, remedy launch-gated via L1-B2

The contract lens is right on the specifics: the three "missing" work orders (WO-MINT-ESTIMATOR-VOCAB, WO-COLLECTION-MARGIN-01, WO-ARM-EVIDENCE-AUTHOR-01) are ancestors of HEAD — the scenario's "invisible launch-blocking obligations" are stale registration prose, not live obligations. The execution lens is right on the class: a kernel asserting falsehoods (U11 row "queued/unprojected" against PASS receipts; FCM "continues unmerged" against merged 60d9e42) with no invariant forcing truth is the same structural disease as B2.

Ruling: B3 is should_fix as an independent finding — it adds no launch-block beyond what B2 already imposes — but its remedy is subsumed into the single kernel-reconciliation transaction that B2 (a confirmed blocker) mandates. The execution lens's concern is thereby fully honored: the fix ships launch-gated regardless of the label. Do NOT re-register the shipped WOs; do reconcile the false rows, the stale `latest_report`, the gate table, and (per DG-contract) obtain a formal magistrate ruling retiring P2-006 rather than silently deleting the row — a superseded campaign leaving the kernel without a recorded disposition would be a fresh instance of the same defect.

## E. COVERAGE + FALSELY-CLEAN ADJUDICATION

The L2 precedent is the controlling lesson: a self-enumerated 16-artifact universe survived the seat's own F8 packet and fell only under adversarial refutation, which found omitted contracts, omitted bootstrap/backfill scripts, an omitted 23-test lifecycle module, and a false test count. Every other seat's denominator is the same kind of self-enumeration.

Ruling: all ten gating NOT-READY verdicts stand as NOT-READY; no seat is downgraded to UNVERIFIED. Reasoning: a NOT-READY verdict is conservative with respect to coverage error — undiscovered universe can only add defects, never flip NOT-READY to READY. The unexecuted-obligation lists are detailed, honest, and correctly route privileged/live-only obligations to ED rows rather than silently skipping them; that is adequate for NOT-READY to be trustworthy.

But the falsely-clean risk transfers to closure time, bound as follows: (1) closing a component's work orders does not entitle a component READY — the WO lists inherit the possibly-incomplete denominators, and charter amendment 12 means the fixes themselves void the lens results as they land; (2) the eventual READY re-audit must re-enumerate every universe independently and subject each denominator to the same adversarial coverage attack that killed L2's, as a standing packet element, not a discretionary one; (3) L2 additionally receives a full re-audit work order against the refuter's 251-test universe — its report's clean areas are ruled void, not merely thin.

Seats with the narrowest denominators (L9 at 14/16, L11 at 14/16) are flagged for priority coverage attack at the re-audit; no present re-run is ordered since their verdicts are already adverse.

## F. WORK-ORDER PROGRAM RATIFICATION

The refuter-corrected minimal set is RATIFIED with amendments.

Design rulings required first (Phase 0 — desk, no code until ruled):
- R1 — freeze-evidence lifecycle: durable-freeze-evidence vs successor-pack tool. Both A-lens refuters concur in-place re-author is not D-131-valid and the 24h horizon is implementation policy, not contract text. Design-bearing and contract-adjacent: pre-decision Sol consult mandatory; if it amends D-131/D-134 contract text it is itself a rule-11 cold-gate trigger. Everything in Phase 2 depends on R1.
- R2 — FROZEN_PLAN identity (pack plan_tree sha vs reservation sha vs window.env value) — must precede the B-cluster prose/parser changes.
- R3 — P2-006 formal retirement (per §D).
- R4 — M-2 execution-note amendment (per §C.ii).

Phase 1 — parallelizable code work orders (all ratified):
1. WO-T0-PRODUCER (integrated): ONE work order covering the nine-input acquisition/capture tool (F1+F2 merged), the ≥10-min continuous dwell in `prewindow_check --wait` (do NOT lower the author's 600 s threshold), the D-127 privileged clock route (already ruled, never landed — land it; Ed installs), the four env/chain/manifest mismatches plus the refuter-discovered doubled plan-path defect with a real-pack regression test (mandatory), and the terminal-review-trailer evidence producer (refuter discovery). Largest single item; blocks the dress rehearsal.
2. WO-KERNEL-RECONCILE: one transaction — council gate as an active global gate, false rows corrected, latest_report current, P2-006 disposition per R3, `gen_state` regeneration. Cheap; do first within the phase. (Subsumes sweep B5.)
3. WO-LAUNCH-BINDING: atomic arm-consume-to-launch — reviewed launcher performing consume→exec, plus downstream provenance refusal so an unconsumed launch fails closed at a machine, not at close-out item 5. Ed still performs the physical launch.
4. WO-CONSUMPTION-EDGE: governed prospective-manifest validator + post-collection finalizer + queue row (L10-B1/L4 route). Ratified with ECF's qualification recorded: post-collection implementation is not categorically barred by L1 custody discipline, but carries a heightened proof burden — hence built and rehearsed now, not after a spent window.
5. WO-MARGIN-RECORDER-AUTHZ: governed-vocabulary authorization for exactly the plan-tree-pinned spec path, plus census tests that model the REAL frozen cell shapes (the green-suite-broken-seam specimen must die in the same commit).
6. WO-CENSUS-SEMANTICS: L9-B1+B2 consolidated — activity-based re-shape of MAINTENANCE_CENSUS and the browser/monitor patterns; gated on ED-Q-L9-3's quiet-state baseline fixture so the fix is proven against the state it will actually run in.
7. WO-DETECT-PULSES-BUDGET: bounded evaluation/wall budget → registered invalid-evidence + governed abort (L2-1).
8. WO-L2-REAUDIT: per §E — new item, cold addition.
9. Should-fix batch: L2-2 typed refusal; L2-3 (should-fix per the refuter's raise); L8's arm-context/fuse-documentation/rm-shape/TOCTOU items; L7 monotonic-horizon check at consume; sweep blockers B1 (alpha_arm_readiness re-anchor per its own standing rule), B2/B3 (queue closures + D-130 disposition), B6 (README), and B7 (the 8.611855 J vs 1.869502 J paper contradiction — claim-bearing; registered as a live P1 queue row with owner and trigger). These sweep items remain formally UNVERIFIED findings; the WO is to verify-and-fix.
- Ratified drops: WO-L2-4 (phantom); L8-B4 (dead, both lenses); F4's timing premise (privilege gap survives inside WO-T0-PRODUCER).

Ed-required (sudo/hardware/production-machine; batch per the one-session plan): ED-Q-L8-1 (D-127 sudoers install + one exercise), ED-Q-L8-2 (full dress rehearsal E-4→E-9 + author→arm→verify→consume against scratch custody, timed against the 20-min horizon and 5-min fuse — the program's single most valuable Ed hour), ED-L3-1/2/3, ED-Q-L9-1/2/3, ED-QUAL-L1-1 and L1-2 (production machine; any reboot decision is Ed's), EDQ-L2-2, ED-L7-1/2/3, ED-L10-1 (desk, Ed-held corpus), ED-QUAL-L4-1 (network + ~3h35m, no sudo — schedulable independently). ED-Q-L9-3 comes early (it gates WO-CENSUS-SEMANTICS).

Phase 2 — sequential, after R1 + Phase 1: the re-freeze via the ruled lifecycle route, regenerating truthful freeze-aware status text (retiring M-2), rotating evidence within horizon; then the successor arm packet reissued at the exact reviewed head after an end-to-end pass (D-134 cl.9 already requires it; old packet preserved as custody).

Phase 3 — structural, non-optional: every Phase-1/2 landing voids affected lens results under amendment 12. The program therefore ends with a new baseline manifest (with the two §B condition fields) and a focused re-audit with adversarial coverage re-enumeration (§E), delta re-audits per C-028 on every fix round.

Phase 4: reconvened sitting, fresh cold pairing, for any READY.

## G. OVERREACH FINDINGS

1. The self-performed digest refutation — outcome upheld, practice flagged, one conclusion rejected. The magistrate refuted a blocker in its own sitting's reference artifact with no independent refuter — "never self-grade" exists precisely for this shape. Re-executed cold: all three digests reproduce exactly via `committed_pack_tree_sha256` at this head, so the refutation is factually correct and the sweep scout's algorithm choice (the test file's rglob working-tree hash) was the error. But the closing "the manifest requires NO fix" is overreach: the manifest names no digest algorithm, a same-named divergent digest exists in the tree, the charter-required chain-template sha is absent — and the false blocker itself is the demonstration that these gaps mislead auditors. Fix at re-pin (§B conditions).
2. Disposition 1, rationale point 3 — "in no lens's evidence universe" is contradicted by L1-B2's own citation of RUN_STATE.md:3433. Right outcome, overbroad ground; recorded.
3. The relay-failure episode — honestly recorded, but a standing trigger was eaten again. Five of nine refuter relays wedged ~7 hours before detection. Under the standing doctrine this is a monitoring lapse, and "a turn ending in a waiting state on a scarce open resource" is a mandatory rule-11 trigger that did not raise a consult. Credit: the episode is candidly recorded in the sealed packet, the T5 remedy was applied, and the relaunched refuters completed. Consequence: refuter-fleet liveness checks keyed to output progress with a bounded first-checkpoint deadline become part of the standing refuter protocol, and C-058 records this as the second trigger-eaten instance in one sitting cycle (with M-2) — a pattern, not two accidents.
4. Benign-environment self-rulings on two refuter worktrees (deleted/vanished mid-run). Self-graded, but low-risk: both affected refuters returned verdicts adverse to readiness, so the self-serving direction is absent. Accepted; note that a vanished worktree on a refuter that had confirmed a READY would demand replay, not a benign ruling.
5. No overreach found in: the deferral of the L1-B3 synthesis to this sitting rather than a unilateral magistrate call (correct discipline); the mechanical packet assembly; the commit freeze (held, verified); the seal.

Closing note. The packet is one of the better-assembled adjudication instruments I have reviewed: adverse findings against the magistrate's own launch decision, its own missed trigger, and its own reference manifest were all placed in the sealed record rather than smoothed over. The verdict is nonetheless unambiguous: ten of ten gating components NOT-READY, two structural blockers (the T-0 producer gap and the freeze-evidence expiry lifecycle) that make any funded window either unlaunchable or unconsumable at the audited baseline, and an ED-qualification surface that has never been exercised live. The instrument is not ready; the work-order program in §F is the path, and windows are not scarce.

*Ruling delivered for verbatim custody. The magistrate may overrule only with written dissent that Ed sees.*
