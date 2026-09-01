# 59e — Opus 5 contract-lens refuter, cold gate #3 Packet C (skeleton first-use class)

Seat: Opus 5, read-only, paired with the cold Fable seat (verdict 59d). Raw report follows.

---

**Contract-lens ruling on Packet C** (read: packet; 57 verbatim; 36b; 48c §Packet 2; skeleton §2 :110-157, §4 :490-570, ledger :1189-1248; all first-occurrence lines grep-verified outside HTML comments).

**(1) Per-term: does the standard require a gloss?** The standard's failure condition is literal — "a term whose meaning arrives only in later text fails the draft" — so the question per term is only whether it is a term of art / criteria word / technical verb.

| Term | First body line | Required? | Why |
|---|---|---|---|
| warm-up pulses | 122 | **YES** | Their defining property (excluded from the measured train) arrives at :140 only. |
| base-two varied-gap schedule | 122 | **YES** | "base-two" is never built anywhere in the draft; unreplicable. |
| sampler cadence | 122 | no | Ordinary English, self-decorated by "requested 100-ms"; luna's gloss adds nothing. |
| quiet trace | 122 | **YES** | "quiet" is a criteria word (an acceptance check at :124); ambiguous between "no commanded pulse" and machine-state quiescence. |
| clock-anchor bound | 124 | **YES** | Built in the *next* paragraph (:126) — textbook "meaning arrives only in later text". |
| \(t_{0.995,16}\) / 99% quantile | 128 | **YES** (notation) | "99%" vs subscript 0.995 is never reconciled; the notation is never decoded. |
| sample standard deviation | 128 | **YES** | No formula at first use; §4 :507 doesn't define it either. |
| corpus range | 128 | no | "range" is unambiguous statistical English; referent bound two sentences earlier. |
| directional comparison | 501 | **YES** | Highest-cost item: "directional" sits inside "two-sided Holm" in the same sentence; meaning only at :566. |
| Holm step-down correction | 502 | no | Function *is* glossed at first use ("keeps the chance of any false direction claim at 0.05"); mechanics + worked example at :552-557. Standard requires a gloss at first use, not the mechanism. |
| measurement variance | 508 | **YES** | Load-bearing distinction of the paragraph (vs repeat scatter), unglossed. |
| direction gate | 559 | no | Explicitly signposted forward ("in the next paragraph") and built at :566-569 — and that clause was *dictated* by the lead as round-3 item 13. |

8 of 12 are real failures under the binding text; luna over-reaches on 4. The contract finding is not "luna is strict" — it is that **an enumerated cure cannot discharge a universally-quantified rule**, so round 4 is predicted to yield residue list #4.

**(2) Ledger status: self-grading, and already falsified.** Written by the fixer seats, closing "Terms the final first-use audit could not build: none" — unfalsifiable in form, false in fact: six F2 terms have no row, and row :1216 claims home "Section 4" for *sample standard deviation* whose first body occurrence is :128 in §2. That falsifiability is exactly what makes it usable as a fixture. A test **can** assert, mechanically: (a) each row's term string occurs in the body (comment-stripped) and its **first** occurrence line falls inside the line range of its named home `## ` section — this fails today on :1216; (b) every row has a nonempty disposition; no duplicate/orphan rows; (c) **closure**: every candidate term-of-art token (bolded, `*italic*` introductions, defined \(macros\)) is a subset of ledger terms, so a later edit introducing a new term fails the build until a row is added. Extend `tests/test_paper_terms_lint.py` (3 tests today). A test **cannot** assert that a gloss is adequate, plain, or physically *correct* — 36b's PED-FU-02 was a dictated gloss that was factually wrong; no lint catches that. The test is a drift-and-omission guard; seat judgment stays the acceptance authority for gloss quality.

**(3) Doctrine.** Option (i) is what the STANDING ESCALATION TRIGGER forbids as the next spend — the consult must yield a reshape, not round three-again. (ii) is the compliant reshape: it changes the defect class from "did the fixer catch this term" to "is the inventory closed", with a mechanical guard. (iii) **is** a reinterpretation of a live SHOULD-FIX verdict *and* touches an enumerated irreversible (merge) — so the lieutenant may not choose it alone, but a cold gate may, and this packet is the correct venue. It fails on merit, not doctrine: §2 :110-157 and §4 :490-570 contain **zero** `[FILL:` placements (70 exist elsewhere), so the packet's "will be rewritten at fill time" premise does not hold for the two passages at issue.

**(4) Cold gate #1's waiver: mis-ruled, not missed.** The trigger's predicate is *signature*; 48c substituted *convergence in counts* ("23 → 3, 9 → 3"). Falling counts are motion, which is the disposition the trigger exists to catch. Governance-wise it was not a missed trigger — the trigger fired and the designated organ ruled, and it ordered a RESHAPE — but the reshape aimed at *replication targets*, not first-use closure, which is why round 3 failed identically. Record it in the trace as **mis-ruled**, with the note that count convergence is not a defense against a signature.

**Recommendation:** take (ii), keep the inventory in the existing ledger, land the mechanical home-section + closure test with it, and decouple the merge decision from the class.

VERDICT: (ii) — reshape to a closed term inventory in the existing ledger, cured to zero FAILS, guarded by a first-occurrence/home-section and closure test; (i) is doctrinally barred and (iii)'s deferral premise is falsified by zero FILL placements in §2 :110-157 and §4 :490-570.
