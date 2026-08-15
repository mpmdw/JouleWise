# OPUS CONTRACT-LENS REFUTER — REMANDED M-2 COLD GATE (verbatim custody)

Provenance: Opus contract-lens refuter, fresh session, no loop context; verified every packet
primary against the live repo at HEAD 62d4479 (worktree clean, read-only throughout). Relayed
verbatim except this header; the magistrate did not edit findings. The magistrate's rule-1
verification of B1/B2/B3 is appended at the end.

---

## BLOCKERS

**B1 — The packet's "PRIMARY 2 — the overridden §5C gate text" is not §5C, and is text the remedy under review wrote about itself.**
The packet labels window_runbook.md:265-290 as the overridden §5C gate. §5C begins at docs/phase_2/window_runbook.md:686 — 396 lines below. Lines 266-290 are §4 (freeze procedure / pack-digest framing). Worse, the one paragraph in that block that bears on M-2 (window_runbook.md:271-278, "For the three packs frozen on 2026-08-13, the committed D-134 freeze receipt … are authoritative over the legacy `unfrozen_draft` wording … Do not repair those committed bytes") was **added by ac3fe1d (#149)** — the very chain-fix batch that constitutes the M-2 remedy (git log -L 271,278). The council specifically enumerated "the overridden §5C gate text" as a required primary. What was attached instead is the remedy's own post-hoc justification, presented as the pre-existing gate. A pairing reading only the packet would conclude the runbook independently corroborates M-2; it does not — that sentence IS M-2, restated by its author after the fact. This alone defeats the header's claim of "scripted extraction; zero magistrate prose": no script keyed to "§5C" produces line 265.

**B2 — The remedy can never satisfy its own retirement condition: draft_status is hardwired and freeze_aware_status() does not touch it.**
freeze_aware_status() (generate_configs.py:149-157, 1p5b) feeds only PACK_STATUS (:169), and PACK_STATUS is consumed at exactly three sites: successor-rule prose (:187), README selection (:1449), and the stdout line (:2169). Every JSON emission of the field is bound to the literal constant DRAFT_STATUS = "unfrozen_draft" (:51) — 1.5B at :1213, 1300, 1554, 1712, 1732, 1823; 7B at :825, 900, 1571, 1855, 2068, 2093; contrast at :381, 407, 523, 1174, 1301, 1417, 1551, 1589. **Twenty emission sites, zero freeze-aware.** Therefore a future regenerated, newly-frozen pack will STILL emit "draft_status": "unfrozen_draft". The council's Phase 2 states the re-freeze produces "truthful freeze-aware status text (retires M-2)"; the execution note says the override "RETIRES" at that point. On the landed code that is unreachable. An override recorded as transitional, then as standing-for-the-packs'-lifetime, is in fact **permanent by code silence** — the exact drift class the cold adjudicator named at §C(ii) and then failed to detect. The forward-only remedy is not merely incomplete as recorded; it is incomplete as BUILT.

**B3 — The override overrides a reading no machine performs and no gate states — yet is now a standing instrument every arm packet must cite.**
Independent sweep: **zero** read-and-branch sites on draft_status anywhere in executable code. The arm-readiness machinery contains no occurrence of draft_status/armable/unfrozen; its closed refusal vocabulary (arm_readiness.py:60-127) has no code expressible for descriptive text. generate_configs.py --check (:2135-2142) is whole-file byte equality, no semantic field inspection. And §5C's actual "placeholder" clause (window_runbook.md:709-714) enumerates RECEIPT properties: "A missing receipt, placeholder, stale HEAD or pack digest, bad sidecar, incomplete row set, refusal, predecessor with a semantic successor, or already-consumed capability is NO-GO." Every member is an arm-receipt attribute. There is no "placeholder-text NO-GO reading" in §5C to override. The magistrate's own disposition asserts "M-2 overrode a NO-GO reading" — that premise is unsupported by the gate text. The live consequence: decision_log.md:8902-8904 now requires that "Every arm packet must cite this ruling", manufacturing a standing procedural dependency on an override of a nonexistent gate. Phantom authority accreting into the arm path.

## SHOULD-FIX

**S4 — "GENERATOR-OWNED DESCRIPTIVE TEXT" is false for the contrast pack: its frozen bytes carry live, unratified placeholders.**
d117_contrast_qwen25_1p5b_vs_7b_v1/prefill_prompt_candidate.json:3-7 reads "draft_status": "unfrozen_draft", "candidate_status": "PROPOSED-PENDING-LEAD-RATIFICATION", and — literally — "prompt_text": "TODO(lead): no named authority pins text" under authority. PROPOSED-PENDING-LEAD-RATIFICATION persists at 20+ frozen sites (calibration_plan.json:556, analysis_manifest_v3.json:1023, ten 03_prefill_p256_contrast_blocks_01_05/*.json:55). The pack README (:1,10,17,20) titles itself "unfrozen draft", says "pending lead ratification at freeze", and declares "Identity pins remain EMPTY pending U11". For this pack the unfrozen_draft marker was not stale residue — it **accurately described the artifact**, and a fail-closed reading would have surfaced a TODO(lead) inside a frozen pack. M-2's factual premise does not hold for one of the three packs it governs; the packet quotes ONLY this pack in Primary 4 and surfaces none of it.

**S5 — The "not armable" README lines were true at ruling time and remain true at HEAD.** Per §5C(1) and alpha_arm_readiness.md:20-28, the in-pack freeze receipt "is non-authorizing and cannot carry GO"; only an external arm receipt may. The pack alone is genuinely not armable. The generator's freeze-aware replacement preserves the meaning, which concedes the point.

**S6 — Primary 4 is materially under-inclusive, and the README half of the ruling is entirely absent.** 32 draft_status occurrences exist across all three packs; the packet shows 6 lines from one pack; zero README bytes attached; the two floor packs (the packs actually queued to arm) appear nowhere.

**S7 — The #149 remedy is not text-only: it silently changed the reservation argv under the same predicate.**
freeze_aware_reservation_plan_arguments() (1p5b generate_configs.py:711-716), introduced by ac3fe1d, returns [] when PRESERVE_CURRENT_FROZEN_BYTES is true — **omitting --plan <calibration_plan.json>** from bracket_args (:726, consumed :767). True for all three current packs. Meanwhile §5C E-9 still instructs the full governed argv superset including --plan "$FROZEN_PLAN" (window_runbook.md:792-795). The generated chain and the manual §5C step now disagree on a governed argument, for exactly the frozen packs, as a consequence of a batch ruled to be a cosmetic-text fix. (R2's FROZEN_PLAN ruling may be converging; not reconciled at HEAD.)

**S8 — The R4 execution note expands scope while the underlying override is sub judice, entered by the party under review.** Authority chain exists and the note flags the remand — not unauthorized — but it simultaneously decides the remedy question this gate was convened to rule on, and grants standing force pending the ruling. Given B2, that standing force is indefinite.

**S9 — The advisory §C manufactures a forward reliance that does not exist.** "Every arm night until the re-freeze needs M-2 in hand to pass the §5C entry gate" — per B3 the gate does not read draft_status; nothing needs M-2 to pass it. The advisory converts a documentation nicety into a launch-path dependency, and the council verdict propagated it.

**S10 — The freeze-aware README branch is a substantive content regression.** generate_configs.py:1447-1455 replaces a ~20-line README with four lines, dropping the receipt-oracle derivation, the arm-time evidence note, the U11 projection requirement, and the lead-review-before-release line.

**S11 — "Assembly is scripted extraction" is unverifiable and, per B1, false.** The trace dir contains packet.md and nothing else; no extraction script custodied; the mechanicality claim that cures Opus B3 cannot itself be checked.

## NOTES

**N12 — Reliance is nil in operation.** No arm receipt exists anywhere under ~/JouleWise-window-custody/ (find → empty). The window slipped and the council returned NOT-READY. No collection, verdict, or claim consumed the override. The operative arm packet predates the ruling and lists "M-2 draft_status contradiction ruling" as Ed-owed at arm — i.e. the record M-2 resolved was an open fail-closed hold, closed unilaterally.

**N13 — The one primary that is dispositive and favourable to the magistrate was also omitted.** L1-AUTHORITY-PLANE-report.md:88 — plan_tree draft_status persists in frozen bytes; no code consumer (verified); the M-2 scoped override is now permanent for these packs. Corroborates B3 and pre-states B2. Its absence is not self-serving — the extraction failure reads as sloppy rather than adversarial — but it confirms the packet was not assembled by any complete rule.

**N14 — Primary 5 and Primary 3 are truncated mid-token.** Primary 5 opens mid-sentence inside L5's F-3, silently dropping a SHOULD-FIX; Primary 3 ends mid-identifier and never identifies which generator is quoted.

**N15 — M-2's "exactly this field" scoping is incoherent against its own fact pattern.** The ruling covers two artifacts (draft_status + README) but the execution note narrows to one field, while the sibling staleness markers in the same frozen packs — PROPOSED-PENDING-LEAD-RATIFICATION, "EMPTY pending U11", TODO(lead) — carry an identical staleness argument and remain un-ruled.

## VERDICT

**UPHOLD-WITH-CONDITIONS — narrowed to the engineering holding only; the instrument as recorded should be vacated and re-entered.** The single defensible core of M-2 is that authenticated D-134 freeze receipts and plan-tree pins govern over unauthenticated descriptive bytes, and that repairing frozen bytes would rotate committed_pack_tree_sha256 and void the receipts proving the freeze — that reasoning is sound and could not be refuted. Everything built on top fails contract lens: the override overrode nothing (B3); its factual premise is false for the contrast pack (S4); and the remedy cannot retire (B2). Conditions for upholding: (1) strike the "overrode a NO-GO reading" premise and the "Every arm packet must cite this ruling" duty, replacing them with a finding that no gate ever read the field; (2) either extend the generator so draft_status is genuinely freeze-aware, or record explicitly that the override is permanent for these packs and delete the false retirement clause; (3) rule the contrast pack's TODO(lead)/pending-ratification markers separately and on their merits — they are not covered by M-2 and are not cosmetic; (4) reconcile the --plan argv divergence (S7) before any arm. Backward reliance re-review is NOT required (N12). The rule-11 cure holds for this instance only — but the same-signature structural finding is strengthened, not discharged, by B1: the cure for "the reviewed party wrote the charge sheet" was itself written by the reviewed party, and it substituted that party's own post-hoc text for the mandated primary. **The packet was NOT complete** (B1, S6, N13, N14, S11). Re-assembly should be performed by a party with no authorship interest, with the extraction script committed alongside.

---

## MAGISTRATE RULE-1 VERIFICATION (2026-08-15, before synthesis)

All three blockers verified against source this session: (B1) §5C begins at runbook:686; lines
271-278 were added by ac3fe1d — the packet's Primary 2 line range was hand-chosen by the
magistrate from an earlier refuter citation, not script-derived from "§5C"; defect acknowledged
as the magistrate's own. (B2) all six JSON "draft_status" emissions in the 1p5b generator bind
the literal DRAFT_STATUS constant; freeze_aware_status()/PACK_STATUS feed only prose/README/
stdout (sites :187, :1449, :2169) — the retirement clause is unreachable on landed code.
(B3) the §5C machine-gate clause at :709-714 enumerates arm-receipt properties only; the
"placeholder-text NO-GO reading" premise traced to fleet finding L8-B4, which the council's own
refuters struck as a wrong-path artifact.
