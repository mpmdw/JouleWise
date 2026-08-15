# COLD-GATE RULING — REMANDED M-2 (cold Fable adjudicator seat; verbatim custody)

Provenance: cold Fable instance, fresh session, no loop context; independent view formed from
the packet primaries + its own repo spot-checks BEFORE reading the advisory input. Relayed
verbatim except this header; the magistrate did not edit content. The paired Opus refuter's
findings are custodied separately; the composed verdict is recorded only after both seats.

---
## Spot-checks performed by this seat (primary evidence, this session)

1. Decision-log record — the M-2 ruling and R4 execution note (~lines 8881-8905) match the packet's Primary 1/1b byte-for-byte, including the remand citation.
2. Pack bytes at HEAD — all three packs still carry "draft_status": "unfrozen_draft" across their JSON surfaces and "not armable" in their READMEs (the field appears in every order_manifest, producer_contract, plan_tree, etc.).
3. Freeze-receipt chain, all three packs, byte-exact: d117_floor_qwen25_1p5b_v1 receipt sha ddbbb409…1738 == .sha256 sidecar == plan_tree pin (line 37) == generator CURRENT_FROZEN_RECEIPT_SHA256 (line 53); d117_floor_qwen25_7b_v1 a6dec2c2…7870 same four-way identity; d117_contrast_qwen25_1p5b_vs_7b_v1 2ef73bf0…106f same. The packet excerpt's 74ccdaec… line is a different constant (CURRENT_FROZEN_GENERATOR_SHA256, generator line 146, also pinned) — an excerpt-framing artifact, not a discrepancy. No mismatch exists.
4. Consumer census — grep across joulewise/ and scripts/: ZERO code consumers of draft_status/unfrozen_draft. The field is purely descriptive. The only readers are the §5C human gate, the generators themselves, and tests.
5. Remedy mechanics (generate_configs.py, 1p5b, read at the relevant sites): freeze_aware_status() returns draft text iff the latest receipt's sha equals the pinned 2026-08-13 hash; preserve mode passes committed bytes through verbatim (lines 1803, 1987); the non-preserve README branch (line 1449) emits truthful "frozen by D-134 receipt" text still requiring an external arm receipt. main() prints "verified unfrozen draft" on frozen packs — transient stdout only, never committed bytes (L5 F-4's NIT triage affirmed).
6. Tests — test_freeze_aware_successor_contract_is_forward_only (line 311) encodes forward-only semantics as a defect-shaped regression; lines 876-883 pin the frozen packs' legacy bytes, so any re-freeze fails these tests loudly.
7. Record surfaces — the operative reading is recorded in the decision log (via R4), §5C itself (runbook ~277-284), and alpha_arm_readiness.md:30-35. Sweep-S3's ordered fix is discharged.

## RULINGS

### (i) Override sound on the merits — YES. M-2 is UPHELD.

Three independent grounds, each sufficient:
1. The overridden text has no consumers. No gate logic, verifier, or quantitative pipeline reads draft_status (verified). The authoritative state machine is the authenticated chain: freeze receipt + sidecar + plan-tree pin + U11 projection + the external arm receipt that alone can carry GO.
2. The legacy text errs only in the safe direction. "Unfrozen draft"/"not armable" is a false NO, never a false YES. The override removes a spurious refusal; it manufactures no permission. Every affirmative requirement survives intact.
3. The alternative was self-defeating. Repairing committed bytes post-freeze would break the load-bearing --check byte-identity contract and the attested byte state (§5C: "Do not repair those committed bytes"). Reading placeholder prose as NO-GO would have forced byte vandalism or a full re-freeze for cosmetics. Trading an unauthenticated byte-string invariant for an authenticated receipt-level one was correct engineering and correct metrology.

### (ii) Landed remedy sound given forward-only shipping — YES as landed and now recorded; the original wording defect is confirmed and CURED.

The ruling as entered promised regeneration "via the canonical path"; that sentence was internally inconsistent with the byte-preservation the same ruling protects. #149 resolved the inconsistency in the correct direction: forward-only under PRESERVE_CURRENT_FROZEN_BYTES, keyed to the exact three receipt hashes. The mechanism is fail-closed: any receipt other than the three pinned hashes flips the generator to truthful text, so a successor pack frozen without the regeneration pass fails its own --check loudly — legacy text can never silently ride into a successor. The R4 execution note states the truth in the policy home. The drift class feared — a transitional override quietly becoming permanent without a recorded decision — is now foreclosed by the record. Remedy ruled sound and complete as of the R4 note.

### (iii) Reliance re-review — NO backward re-review required.

Everything downstream of M-2 (the 49dcc49 freeze completion, the §5C discharge, the audit-baseline manifest, the eleven-seat audit that recomputed all three pack digests byte-identical at 8937dec) relied on the override's OPERATIVE reading — receipt governs — which this gate upholds. Nothing relied on the unexecuted regeneration sentence. No window armed in the interval. The reliance is forward: every arm packet until retirement must cite M-2 to pass §5C — already mandated by R4, tightened by the scope order below.

### (iv) The rule-11 cure — AFFIRMED, for this instance only.

Two conditions, both satisfied: (1) the substance survives cold review on the merits — the missed gate caused no substantive harm, now verified rather than presumed; (2) the miss was not absorbed as discretion — it is recorded as the same-signature structural finding with mechanical consequences adopted. Expressly non-precedential: retroactive remand is not a substitute for the ex-ante gate. Any future instance of this signature goes to consult, not to a third unilateral ruling.

### Retirement condition — CORRECTLY SPECIFIED IN SUBSTANCE; one scope order entered.

The condition is mechanically real: the code path exists, is regression-tested, and converges. Two clarifications RULED:
1. The override's whole scope is the three receipt hashes ddbbb409…1738, a6dec2c2…7870, 2ef73bf0…106f. It retires PER PACK, at the first of: a successor freeze receipt issuing for that lineage, or the pack's regeneration/supersession. It may never be cited for any pack whose governing receipt hash is not one of these three.
2. Successor-ships-while-legacy-text-persists: mechanically fail-closed (successor with legacy text fails its own --check; the pinned byte-identity tests fail at re-freeze — two independent tripwires; §5C's ordinary NO-GO then applies with NO override available, because scope clause 1 excludes it). The persisting legacy-text doc surfaces are date-scoped and cannot bleed forward. The sole residual risk is human — loose citation of "M-2" for a successor's legacy-looking text — and scope clause 1 closes it. ORDER: at the next ordinary decision-log edit, append one line to the M-2 record enumerating the three receipt hashes as the override's exhaustive scope; the Phase-2 re-freeze work order must include updating the byte-identity tests, whose failure at re-freeze is intended loud behavior.

### Advisory concurrence

Read after this seat's view was formed: concurs with advisory §C on all four questions; adds the four-way hash-chain verification (independently reproduced), the fail-closed successor analysis, the tests-as-tripwire finding, the safe-direction ground, and the receipt-hash scope order. One precision note without disagreement: §C(i)'s "voiding the very receipts" is slightly loose — receipts hash evidence rows, not README bytes — but the substantive point stands. §C(ii)'s ordered remedies (a) and (b) are respectively discharged (R4 entered) and pending-by-design (the re-freeze work order).

Per rule 11: the magistrate may overrule this verdict only with written dissent that Ed sees.
