# Opus contract-lens review — CLAIM-NONISSUANCE-RECEIPT-01 design spec

Reviewing `01-design-spec-sol.md` at worktree head `6cece4f5` (base `913bf3f7`).
All anchors below were opened this session; sibling-commit anchors carry `@<sha>`.

## VERDICT: AMEND

The producer siting is right, the "no reason code reaches prose" discipline is
right, and the source-mismatch correction is right. One blocker: the trigger
predicate cannot distinguish legitimate non-issuance from a tampered input, so a
forged floor artifact would mint a governed receipt whose registered sentence then
issues into the paper. Two further defects: the acceptance test is short of the
mandated three-part census, and the amendment list omits the contract rule that
actually fixes the family's role set.

### What is sound (do not re-litigate)

- **Source-mismatch correction.** `joulewise/claims.py` does not exist (`ls` fails);
  the owner is `joulewise/analysis_engine/claims.py`, whose `CLAIM_OUTCOMES` at
  `:22-30` already carries `not_estimable`, `not_resolvable`, `unresolved`.
  Keeping scientific null outcomes inside v1 and making this a *sibling negative
  artifact* is the correct boundary; it preserves
  `07-magistrate-rulings-addendum.md:4` (v1 stays the production artifact) rather
  than reviving the vetoed v2.
- **Call site.** `joulewise/cli.py:2003` is `_cmd_analyze_claims`; the
  `analyze_claims` call is at `:2010-2019` and the `AnalysisInputError` catch at
  `:2020-2022` returns 2. Replacing that call with a close-out is the right seam:
  it is the only production entry point, and `docs/process/v5-artifact-flow.md:23`
  registers exactly `joulewise/cli.py:2003` as the claim-gate command. Direct
  library calls to `analyze_claims` staying pure derivations is correct
  (`joulewise/analysis_engine/__init__.py:1661-1665`).
- **No reason and no number reaches prose.** DS-32's branch-1 text
  (`docs/paper/results-fill-registry.md:885`) and PG-08's twin (`:894`) are
  **fixed bytes** with no interpolated field, so the receipt's existence alone
  licenses them; the spec forbids rendering `analysis_inputs_refused`
  (01-design-spec-sol.md:161). This is a materially better position than the
  sibling whole-window lane, which must interpolate a reason.
- **Role-only ingress preserved.** `ClaimEvidenceRef` staying `{role, runs_root}`
  with the git-anchored map selecting the variant is exactly
  `16-magistrate-rulings-addendum-5.md:5` and
  `docs/decision_log.md@2e3349e1:10914-10919`. The supply map's existing shape
  (`configs/paper_supply/supply_map.json@2e3349e1`, key `fixture.claim_evidence`)
  confirms a role key already names a whole pinned input set, so a variant is a
  map-side change, not a caller-side one. Correct.

## Amendments (numbered, all required before an implementation seat)

**B1 — the trigger cannot distinguish non-issuance from tampering (blocker).**
Step 3 (01-design-spec-sol.md:98-100) catches *any* post-step-1
`AnalysisInputError`. That exception's registered meaning is broader than the
receipt's claimed meaning: `joulewise/analysis_engine/inputs.py:231-232` defines it
as "Invalid process input", and `joulewise/analysis_engine/__init__.py:1663-1665`
raises it for "invalid manifest/floor/strict input structure" — which includes a
**malformed or forged floor artifact or strict bundle**. Under this design a
tampered floor file therefore produces a *governed, validator-clean, custody-bound*
non-issuance receipt, and the paper renders "not evaluated — required
token-generation verdict absent" for what is actually an evidence-integrity
failure. D-161's operator-only-adversary prune does not cover this: it explicitly
retains fail-closed for physics and evidence. AMEND: the receipt may not issue on
an undifferentiated `AnalysisInputError`. Either (a) land the structured
`AnalysisInputError.reason_code` contract *first* — the spec already names it at
`:66-67` as future work — and issue only for an enumerated set of
non-integrity causes; or (b) narrow step 3 to a new, distinct exception raised
only at the enumerated non-issuance sites, leaving every other
`AnalysisInputError` at rc 2 with no artifact. Parsing exception text stays
forbidden either way; that part of the spec is right.

**B2 — the acceptance test is short of the mandated census (blocker).**
`15-magistrate-ruling-custody-seam.md:9` requires, per family, "raw byte mutation,
full caller resealing, and replay-to-reopen replacement, each yielding the exact
refusal code and zero rendered output"; the third arm tests contract step 7
(`docs/contracts/paper_supply_custody.md@2e3349e1:196-199`). The spec's two arms
(01-design-spec-sol.md:165-177) are a control plus one blended mutate-and-reseal
arm: no replacement arm, and mutation is not separated from reseal, so a pass
cannot say which check fired. AMEND to three counterfactual
arms with three distinct expected codes: `paper_custody_digest_mismatch` (raw
mutation), `paper_custody_digest_mismatch` on role `validator_receipt` (full
reseal with the map pin held fixed), and `paper_custody_input_changed`
(post-replay replacement). The nominated required counterfactual — full reseal
with the clean-Git map unchanged — is the *right* one and should remain the
headline arm, because it is the only arm that tests D-173's actual authority claim
(`docs/decision_log.md@2e3349e1:10914-10919`).

**B3 — the amendment list misses the rule that blocks the variant (should-fix).**
The spec lists contract amendments at `:62`, `:150-159`, `:223-226`. It omits
`docs/contracts/paper_supply_custody.md@2e3349e1:170-174`, which requires inventory
rows to be "exactly the family input roles plus `validator_receipt`; duplicates or
omissions refuse" — a *fixed per-family* role set that a two-variant family
violates by construction. AMEND: add `:170-174` to the amendment list and state
how the inventory declares which variant it is (the map entry's role list is the
only authority that may say so; an inventory-declared or receipt-declared
discriminator would re-open the caller-authority hole).

**B4 — OR-01 residual is unregistered (should-fix).** The spec claims DS-32
(`:885`) and PG-08 (`:894`) but is silent on OR-01
(`docs/paper/results-fill-registry.md:921`), which requires "the reason issued by
that governing evidence" and "include a Qwen-pair verdict only when its absence is
the stop reason" — i.e. exactly this artifact's case. Since the spec forbids
rendering `analysis_inputs_refused` and registers no code→sentence map, OR-01
remains STOP_FILL after this mission. `docs/paper/results-fill-registry.md` is
already in the proposed WRITE_SCOPE, so AMEND: register that residual on the OR-01
row naming the follow-on, rather than leaving a later seat to invent a sentence —
the failure class D-173 was written against
(`docs/decision_log.md@2e3349e1:10905-10909`).

**B5 — cross-lane branch precedence is undefined (should-fix).** DS-32 `:885`
carries two absence branches and this design serves only the first; the sibling
WHOLE-WINDOW-STOP-RECEIPT-01 serves the second. Both governed artifacts can exist
for one campaign. `06-magistrate-contract-rulings.md:26` already registers the
stage order (a before-comparison stop wins over a close-out stop) and neither
design cites it. AMEND: bind the DS-32/PG-08 branch predicate to that registered
order by reference, and add one gamma-side test arm where both artifacts are
present and the before-comparison branch renders.

**B6 — `claim_nonissuance_receipt_id` is a self-asserted field (should-fix).**
The map pins `sha256(rendered_bytes)` (01-design-spec-sol.md:81) — the real content
address; the `cnr-` body hash adds a second, weaker identity the validator must
then defend. The sibling whole-window spec reaches the opposite conclusion ("store
no self-asserted ID") for the same reason. AMEND: drop the field, or record in the
D-173 amendment why the two subtypes differ. Related nit: nesting
`"schema_version": "joulewise.claim_verdicts.v1"` in a non-v1 artifact (`:47`)
makes a grep for the v1 schema match a document that is not one.

**B7 — one anchor to confirm at the seat (nit).** The spec copies
`manifest.evidence.whole_window_verdict.evaluation_basis_sha256` (`:71-74`). The
field is registered (`joulewise/analysis_manifest_v3.py:220`, set at `:3819`) and
`evidence` is built at `:3939-3942`, but the exact nested path was not confirmed
at this base. Have the seat assert it, not assume it.

## Answers to the five contract questions

1. **Authority chain:** closed against a caller-authored or replayed receipt — the
   map pin plus step-7 reopen (`@2e3349e1:175-177`, `:196-199`) do that work, and
   nothing in this design lets a caller name a digest. It is **not** closed against
   a tampered *producer input* (B1). The production supply-map row minting step is
   likewise unnamed, but the spec correctly puts live map values outside the seat
   (01-design-spec-sol.md:245-247) — state explicitly that production reads return
   `paper_custody_receipt_unissued` until that gate lands.
2. **Registered-contract contradiction:** yes — `@2e3349e1:170-174` (B3). The four
   conflicts the spec itself lists (`docs/contracts/claims_ladder.md:21-30`,
   `docs/process/v5-artifact-flow.md:21,23`, custody census, `inputs.py:231-232`)
   all verified as stated.
3. **Unissued value reaching prose:** no, on the intended path — DS-32/PG-08
   branch-1 text is fixed bytes and no receipt field is interpolated. B1 is the
   exception: the *predicate* licensing that text can be true for the wrong reason.
4. **Counterfactual:** the nominated one is right; the test is incomplete (B2).
5. **Decision-log:** fits under D-173 as an amendment
   (`docs/decision_log.md@2e3349e1:10903-10932`); no new number. The spec's
   sequencing — lead lands the amendment before the seat opens — matches
   `15-magistrate-ruling-custody-seam.md:11` (D-173 is provisional and goes before
   the paper-supply cold gate before any supplier merges). Correct, and correctly
   keeps `docs/decision_log.md` out of the seat's WRITE_SCOPE.
