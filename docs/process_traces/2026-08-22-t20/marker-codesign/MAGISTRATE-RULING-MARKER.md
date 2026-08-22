# `_v4` FAMILY-PUBLICATION MARKER — D-144-class co-design ruling (2026-08-22)

Round shape per r5 V-6 (this design is a schema/contract design; no
waiver): two blind seats (Sol xhigh `marker-design-sol.md`, 1028 lines;
Opus `marker-design-opus.md`, 1269 lines — both custodied in this
directory, rounds preserved unedited) → one debate exchange → this
magistrate ruling. Ed's D-150 constraints bound both seats: option (a)
build-at-boundary, CUSTODY-EXTERNAL, changed-set contract stays 112.

## Converged design (ratified as the implementation baseline)

The debate converged on, and this ruling RATIFIES:

1. **Two artifacts.** The marker
   (`joulewise.d117_family_publication_marker.v1`, strict canonical
   JSON + GNU sha256 sidecar) is IMMUTABLE FROM BUILD; Ed's
   confirmation lives in a separate step-6 confirmation table (below).
   The Opus seat's embedded-confirmation field was conceded as a
   genuine hash cycle; the marker binds only the confirmation
   CONTRACT (schema id + required YES), never the table's digest,
   path, or time.
2. **THE UNIFIED STEP-6 TABLE (the D-151 join): one artifact,**
   `joulewise.d117_step6_confirmation_table.v1`, with TWO sections
   (family-publication + successor-pinset). One Ed yes over the table
   digest `hC` authenticates BOTH the marker (edge C→M) and D-151's
   successor pinset (edge C→S). Acyclic by construction. Contract
   home: `docs/contracts/d117_step6_confirmation_table.md` (ONE home;
   neither consumer's contract may restate it). Under D-151's
   fixed-point rule the table is an AUTHENTICATOR and may never enter
   any allowlist, in any transaction. Candidate-mode green recorded as
   forged-`origin/main`-conditional, never reported as published PASS
   (D-151 condition 4 extends to this verifier).
3. **Custody layout** `candidate/` → `published/` in transaction
   custody; verification = digest equality PLUS semantic replay of the
   three freeze-0004 receipts (complements, not rivals): publication
   and scheduler pre-arm run both (pre-arm as fail-early, the arm's
   own replay remaining the load-bearing check per r5 V-1.iv); T-0
   full re-verify; execve hash-equality only.
4. **Refusal vocabulary:** the RULED `readiness_r1_family_publication`
   (typed CUSTODY per r4-5's V4 allocation), REGISTERED in
   `READINESS_REASON_CODES`/`REASON_TYPE_BY_CODE` with a
   registry-load closure check — curing the explosion hole BOTH blind
   seats shared (`_receipt_refusal` raises `readiness_internal_error`
   on any unregistered code, arm_readiness.py:4454/:1466, while the
   registry validator only shape-checks spellings ~:1795; replayed by
   both delegating sessions). The Opus seat's alternative spelling was
   withdrawn as reopening a ruled vocabulary. Diagnostic granularity
   comes from a CLOSED, code-enumerated `check_id` frozenset, not new
   reason codes.
5. **Engagement** is bound to tracked registry bytes (committed
   successor roster), NEVER to marker presence — deleting the marker
   REFUSES rather than disengages. Freeze-time engagement is
   predecessor-only (the bootstrap cure: the pack being minted is
   never gated on its own unbuilt publication).
6. **Scheduler gate receipt bumps to
   `window_scheduler_gate_receipt.v2`** with an EXPLICIT G7
   family-publication gate (exact-key `family_publication` block,
   GATE_IDS seven wide, G7 reason set in the scheduler vocabulary,
   nulls-on-refusal). Both seats concur the bump is
   MAGISTRATE-adjudicated under V-6 ownership — adjudicated HERE.
   **Amendment, by this ruling's authority:** `schedgate-ruling.md`'s
   six-gate enumeration is AMENDED to seven (G7 =
   family-publication); a dated amendment line goes on that doc this
   session.

## Adjudicated splits

- **S-1 Head binding (Sol position adopted):** STRICT FOUR-WAY
  EQUALITY (publication head == HEAD == local main == origin/main,
  clean tree) at all three live consult points (publication,
  scheduler pre-arm, T-0). The Sol seat's rollback refuter is
  decisive: ancestry-only admits a checkout of an OLD published head
  after origin advances (trivially an ancestor of both). The V-3(c)
  push freeze makes strictness free during the campaign span.
  Ancestry + dual-coordinate byte mode survives ONLY for archival /
  future-`_v5` predecessor verification. The Opus seat's own recorded
  strict-variant dissent is thereby promoted; its ancestry rule is
  the recorded dissent.
- **S-2 Freeze-engagement predicate (Sol repair adopted):** the
  literal predecessor-in-current-roster predicate is FALSE across
  adjacent generations at mint time; the repair is a TRACKED
  GENERATION-THRESHOLD CONSTANT (reviewed registry value, not code
  prose). The Opus predecessor-only principle stands; its literal
  predicate is repaired, not discarded.
- **S-3 Library-boundary gate (Opus position adopted):** the
  publication gate binds at the ARM/FREEZE LIBRARY BOUNDARY, not only
  in the scheduler — a direct arm invocation must refuse an
  unpublished family without the scheduler's help. Scheduler G7
  remains the fail-early layer. (Sol's scheduler-only integration was
  the hole; its own engagement adoption implies this cure.)
- **S-4 TERMINAL_REVIEW binding (Opus position adopted):** the
  marker's terminal-review reference binds `head_tree_oid` — Ed's
  step-6 review is bound to the exact tree, not just a commit id.
- **S-5 Tool self-hash in S-0 (Opus's defect, cured as Sol's
  candidate mode):** committed-blob equality is the PRODUCTION rule;
  S-0 candidate mode verifies against the reviewed `$INPUT` manifest
  sidecars instead (the tools do not exist at the pinned HEAD — the
  literal rule would refuse the clone proof). The dual proof
  (candidate PASS + production-gate refusal) is required in S-0.
- **S-6 `publication_state` nit:** implementer's choice within the
  ratified schema; not ruled.

## Consequences (work orders)

- The S-1 reviewed candidate incorporates: marker schema + builder +
  verifier per the converged design; the unified step-6 table contract
  doc (new ONE home); the reason-code registration + closure check;
  the scheduler v2 receipt + G7; the generation-threshold constant;
  the library-boundary gate; regression set = the union of both
  seats' lists (Sol's 9-item list + Opus's 27 tamper cases, deduped
  by the implementer, writer≠reviewer audit applies).
- `schedgate-ruling.md` amendment line (this session, supersession
  discipline).
- The S-0 runsheet r2 revision (already ordered by D-151) adds:
  §3.8's dead option-(b) branch removed; candidate-mode tool-hash
  semantics; the marker verification transcript fields
  (`lane`/`gate_admissible` per the Opus errata).

Design custody: both seats' full files with debate sections, this
directory. The seats' delegating sessions replayed every load-bearing
code claim cited above; the magistrate audited the refuters that
decided each split rather than counting concessions.
