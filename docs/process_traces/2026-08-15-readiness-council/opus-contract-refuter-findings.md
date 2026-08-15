# CONTRACT-LENS REFUTER FINDINGS — readiness council sitting, 2026-08-15 (verbatim custody)

Provenance: Opus contract-lens refuter (rule-11 pairing, cross-model diversity seat), fresh
session, no loop context, over the sealed packet + charter v2 + read-only primary-evidence
spot-checks at HEAD 8937dec. Relayed verbatim; the magistrate did not edit content.

---

Baseline for all spot-checks: `/Users/edr/code/JouleWise` at `8937dec` (== `main` == `origin/main`, verified).

## BLOCKERS

**B1 — The sealed packet is not in custody; the entire evidentiary base is in an ephemeral scratchpad.**
Charter:88 requires "sealed-packet custody under `docs/process_traces/<date>-readiness-council/`". Checked: no such directory exists — `docs/process_traces/` ends at `2026-08-14-readiness-charter-consult`. The packet, all eleven seat reports (149 KB), `triage.json` (98 KB), `consistency-sweep-findings.md`, and `magistrate-dispositions-for-sitting.md` exist only under `/private/tmp/claude-501/.../scratchpad/`. Every sha16 in packet §1 binds a file that a session cleanup deletes. 2.4 M tokens of fleet output and the entire basis for ~20 work orders are one `rm` from unreconstructable, and the verdict would be unauditable by anyone who was not in the session.
Cure (before recording anything): commit `docs/process_traces/2026-08-15-readiness-council/` containing the packet, the eleven seat reports, the nine refuter outputs, the consistency-sweep findings, the dispositions file, and this refuter report; re-verify the sha16s post-copy.

**B2 — Mandatory packet contents are incomplete: six untriaged consistency-sweep blockers are excluded, and the only one shown is the one the reviewed party killed.**
Packet:358-359 compresses a 23-finding document (7 blockers / 10 should-fix / 6 nits) into one line plus a sha16 of an uncustodied file. Three of the omitted items bear directly on this sitting:
- sweep-B1: `docs/phase_2/alpha_arm_readiness.md` is anchored at T4-late and asserts NO-GO for gates that have since closed — inside the pinned audit baseline. It is a false-dirty generator for lens findings, the exact mirror of the false-clean risk charter:67-68 orders the sitting to adjudicate. The sitting has no way to test whether any fleet finding was induced by it.
- sweep-S3: the decision log's M-2 remedy "describes a regeneration that deliberately did not happen" (shipped behaviour is forward-only under `PRESERVE_CURRENT_FROZEN_BYTES`; the frozen packs still read `draft_status: "unfrozen_draft"`). That is precisely Disposition 2 scope (b) — and it is withheld from the pairing asked to rule on it.
- sweep-B5: state kernel stale / no active gates — independent corroboration of fleet blocker L1-B2, which the packet does not record as corroborated.
A packet whose visible triage of an input consists of the single finding the reviewed party refuted is not "mechanically assembled" in the rule-11 sense (§7, §8, §9 are all curated).
Cure: fold the sweep's full finding list into the packet as §8 proper, with per-finding triage state.

**B3 — Disposition 2 (M-2) cannot be discharged on this packet: no primary record is attached.**
Packet supplies the M-2 fact pattern only as the magistrate's own prose. Absent: the decision-log entry itself (`docs/decision_log.md:8881-8893` — retrieved; the pairing was not given it), the §5C gate text that was overridden, the #149 generator diff constituting the remedy, and L5's independent finding on the packs' current text. Rule 11 requires a mechanically-assembled packet because the reviewed party is the magistrate; here the reviewed party wrote the charge sheet, set the scope, and characterised the exposure ("bounded"), while the one document that contradicts the remedy narrative (sweep-S3) was left out. Referral is proper — self-referral is what rule 11 wants — but scope (a)/(b)/(c) are not adjudicable on these contents.
Cure: record the readiness verdict now; do not record M-2 as adjudicated. Re-submit M-2 as its own cold-gate artifact with primaries attached and its own verdict line.

**B4 — Charter:67-68's coverage adjudication is undischarged for 10 of 11 seats, and the one seat tested failed it.**
Every denominator is a self-nominated "universe class" count. The single seat subjected to an external false-clean attack had its denominator refuted outright (L2-COV-1: real direct test universe 251 vs claimed 16). One for one against the method. The verdict direction is not at risk (more coverage only finds more defects) — but the work-order program's completeness is, and a NOT-READY record that implies "close these and we are READY" would be false.
Cure: the verdict must be recorded with an explicit clause that the work-order program is not certified complete, plus a named work order to re-derive audited evidence universes for all seats before any READY-candidate sitting.

## SHOULD-FIX

**S5 — Disposition 1 reaches the right answer through a false premise.**
Mechanical fact 3 asserts README.md and RUN_STATE.md are "session-state surfaces in no lens's evidence universe". False for L1: packet:55 cites `RUN_STATE.md:3433` as an `at:` location for blocker L1-B2, verified at HEAD that line 3433 is exactly the P2-006 READY row the finding rests on. Both post-baseline commits touched that file. So the drift did land in a lens's evidence universe, and the disposition applied the wrong test ("is the file in a universe?") instead of the right one ("did the lens read pre- or post-drift bytes?"). It survived by luck.
The correct proof, executed and strictly stronger — substitute it: (a) all eleven lens worktrees were at `8937dec`, which is `main` == `origin/main`, i.e. the final head — no lens result can be stale against a head it read; (b) every manifest binding verifies byte-identical at that head — `runbook_sha256` ✓ and `state_kernel_sha256` ✓ recomputed, all three `pack_digests` recomputed via `joulewise.arm_readiness.committed_pack_tree_sha256` (exact match), registry/acceptance/freeze-manifest recomputed MATCH by the sweep. Conclusion (zero lens results invalidated) stands on that argument.

**S6 — Disposition 1's fact 4 over-reaches.** The "manifest-after-its-own-head is charter-BY-CONSTRUCTION" argument licenses exactly one post-manifest commit — the manifest's own. It is deployed to soften a three-commit gap; the other two commits are governed by the plain rule and survive only on S5's corrected proof.

**S7 — Four blocker-level claims rest on a single lens.** Affirmatively cleared: all 16 fleet blockers got two distinct lenses (clusters A/B/DG/ECF ×2 each), and all five relaunched relays returned envelopes, so no verdict lost a lens to the relay failure. Not cleared: the three blockers raised by the L2 attack (L2-1, L2-COV-1, L2-EDQ-1) come from one run, which itself had an environment gap; and the terminal-review-trailer producer gap from B-execution alone. Lead relay corroboration of counts is not a distinct lens. Label these SINGLE-LENS in the record or run a second lens before they drive work orders — L2-1 in particular, since its remedy changes governed-abort semantics.

**S8 — L9-B1/B2's empirical basis is single-source and unreplayed.** Both refuters confirmed by regex/launchd static analysis because the sandbox denied live `pgrep`; the "~20 matches observed live" claim exists only in the L9 seat's own run. Two lenses agree on the analysis, not the observation. The remedy redefines what "quiet" means, which is claim-bearing — a loosened census admits contaminated windows. Bind ED-Q-L9-3's fixture as a hard precondition to WO-L9-1/2.

**S9 — Packet §2 is stale against §9, and L2's disposition is incomplete.** The table still shows L2 READY and the aggregate "1 READY / 10 NOT_READY", while §9 records the READY fell. Correct aggregate: 0 READY / 11 NOT-READY. Further, charter:81-82 makes NOT-READY and UNVERIFIED distinct verdicts with different remedies: L2 earns both — NOT-READY for L2-1, and UNVERIFIED on coverage because its denominator was refuted. Record both or the re-audit obligation disappears.

**S10 — L1-B3's severity synthesis should be ruled at the pairing, not in-loop.** (Discharged: the cold adjudicator ruled it.)

**S11 — The audit-baseline manifest is itself non-conformant to charter:22-23.** It omits the required chain-template sha and carries an unchartered `freeze_manifest_sha256`. The chain template is embedded in the runbook §6, so `runbook_sha256` substantively covers it — but the manifest nowhere says so; it names no digest algorithm for `pack_digests`; and it gives no paths for three of its bindings. A lens ordered to "cite it" cannot mechanically re-verify three of its bindings. The missing algorithm field is what generated the sweep's false blocker and the lead-refutation cycle.

**S12 — Charter:77-78 is violated, and is unsatisfiable as written.** "Only T0 rows may remain open at the sitting", yet 23 ED-QUALIFICATION rows are open and none was performed pre-sitting. But the fleet is what enumerates the ED-QUAL universe, so those rows could not have pre-existed it — the rule is impossible on a first sitting. This is a charter defect. Amending it is "any proposed process rule" — a rule-11 mandatory cold-gate item — so this pairing is the correct venue: distinguish an ENUMERATING sitting (output includes the ED-QUAL universe) from a READY-CANDIDATE sitting, and bind charter:77-78 to the latter only.

**S13 — Rule-11 sweep: the same signature has now fired twice in one span.** M-2 (a stop-signal override ruled unilaterally, referred retroactively) and the baseline-drift disposition (an invalidation rule — itself a stop signal — interpreted not to fire, acted upon by continuing the fleet, then referred) are the same shape: magistrate rules a stop-signal question alone under packet-finalization time pressure, refers after the fact. Rule 11's STANDING ESCALATION TRIGGER — two consecutive failures with the same signature — is met. Record it as structural in the council entry, not as two unrelated misses. (Not itself a rule-11 violation: "continuing past an escalation trigger" is enumerated on the lieutenant's forbidden list, not the magistrate's mandatory-trigger list. The referral was proper; the acting-before-ruling is the finding.)

## WORK-ORDER PROGRAM — items requiring a ruling, consult, or Ed before implementation

**W1 (gating, blocker-class).** Freeze-evidence lifecycle: durable-freeze-evidence vs successor-pack tool; in-place re-author not contract-valid under D-131; the 24 h horizon is implementation policy, not contract text. Contract change → rule 3 council trigger + rule 2 mandatory pre-decision design consult. No code on the expiry cluster until ruled.

**W2 (program ordering — the sharpest omission).** The re-freeze remedy rotates pack digests and therefore voids this audit's own baseline manifest. The program must be ordered: all non-pack-byte repairs land first → re-freeze happens once, atomically, last → a new baseline manifest is cut → the pack/custody-bearing seats (L1, L5, L7 minimum) are re-audited against it. Absent that ordering the next sitting will discover its baseline is already dead. Re-freeze is also "anything irreversible" → magistrate/Ed, not lieutenant.

**W3.** P2-006 retirement needs a ruling, not deletion; the kernel reconciliation edits the declared sole work-selection authority (DOC-008) — a meta-process edit, lieutenant-forbidden alone.

**W4.** `FROZEN_PLAN` semantics need a ruling before changing prose or parser; blocks the env/chain/plan-path work order including the doubled-plan-path defect.

**W5.** D-127 sudoers install: widening NOPASSWD beyond `/usr/bin/powermetrics` amends D-004's privilege posture. Ed-only (hardware/sudo) and deserving explicit ratification, not a work-order side effect.

**W6.** Rule-2 pre-decision design consults required: the governed prospective analysis-manifest validator + post-collection finalizer, and the margin recorder's governed-vocabulary authorization — the latter widens an authentication allowlist inside the authority plane.

**W7.** L8-B7 remedy (launcher consume→exec binding + downstream provenance refusal) adds an enforcement gate to the launch path and changes the operator's night sequence — contract-bearing, council trigger.

**W8.** Successor arm packet (D-134 cl.9): magistrate-reviewed, cuttable only after the integrated T-0 repair passes end-to-end at the exact reviewed head. Record as a hard dependency or L8-B5 recurs verbatim.

**W9.** L9 census re-shape gated on ED-Q-L9-3's real quiet-state fixture (see S8).

## NOTES

**N1.** The record says five of nine refuter relays died (4 first-wave deliveries + 5 relaunched); use the packet's number.
**N2.** Disposition 1's rejection remedy says "re-pin the manifest" — charter:20 calls it immutable. Word it as supersession (new manifest, original retained).
**N3.** There is no packet index, which charter:88 requires. That absence is why B2's omission passed unnoticed. Also unevidenced anywhere in the packet: per-seat effort tiers and charter:98's "no ultra sessions".
**N4 (affirmative clearances).** The commit freeze held — `main == origin/main == 8937dec`, delta from `ac3fe1d` is exactly the three named files. And the record's one downward severity adjudication — the lead's refutation of sweep-B4 "pack digests reproduce under no algorithm" — is correct: independently recomputed all three via `committed_pack_tree_sha256`, exact match. The drift check is runnable; the sweep's proposed manifest fix is properly void.

## OVERALL JUDGMENT

The NOT-READY direction is safe and over-determined — ten of eleven gating seats self-falsified, sixteen blockers each survived two genuinely distinct refuter lenses, several with executed refusals, and the eleventh seat's READY did not survive the only false-clean attack anyone ran. Nothing found moves the verdict toward READY, and the two magistrate dispositions reach defensible conclusions: Disposition 1's conclusion is correct (though its stated reasoning is not — substitute the S5 proof), and Disposition 2's referral is proper. Not safe to record as-is, all cheaply curable: (1) no custody — cure before recording; (2) packet missing mandatory contents (six untriaged sweep blockers); (3) M-2 must not be recorded as adjudicated on this packet — re-submit as its own cold-gate artifact; (4) the verdict text must state the work-order program is not certified complete. Add to the record: the corrected drift proof (S5/S6), L2 as both NOT-READY and UNVERIFIED (S9), L1-B3's split synthesis (S10 — discharged by the adjudicator), the charter amendment separating enumerating from READY-candidate sittings (S12), the same-signature structural finding (S13), and the W2 program ordering, since the top-priority remedy mechanically destroys the baseline that produced it.
