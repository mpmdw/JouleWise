# Magistrate adjudication — what the floor artifact can honestly claim (2026-08-07)

Two independent apex reviews reached the same place from opposite ends.
This is the most consequential finding of the session and it is a
PAPER-LEVEL finding, not only a code one.

## The two reports

**Opus post-merge counter-review:** the mint authenticates pins against
`component.report["floor_mint_postcollection"]`, and NOTHING in the
repository produces that block (three read sites, zero writers; the only
writer is a test fixture). So in production the block would be authored
by the same operator authoring the pins.

**Fable apex diff gate:** given the block, the nine equality comparisons
ARE real and the composition invariants hold — but the trust chain
terminates in three operator-controlled places: the pinset hash is a CLI
argument; the ledger head pin must byte-match `git show HEAD:` OF THE
LOCAL CHECKOUT; and `project_commit` / `project_tree_state` are
operator-typed CLI strings, shape-checked only — the mint never runs git
to learn its own commit.

**They are consistent.** Opus found the producer missing; Fable found
that even with a producer the root is reachable by the operator. The
combined, honest characterization is Fable's, and it is adopted:

> The floor artifact is **operator-attested, with machine-checked
> internal consistency and git-anchored tamper evidence.** It is not
> machine-verified provenance.

## Why this is the right characterization, not a failure

Against the failure mode this project actually has — honest-operator
error — it is a hard, named-reason gate, and that is what floors are for.
Against a dishonest operator, its value is that fabrication now requires
forging a self-consistent COMMITTED history that survives review of
pushed main; the pre-fix state left no committed trace at all. That is a
material elevation and a defensible design for a single-operator
instrument.

What is NOT defensible is calling it more than it is.

## BINDING CONSEQUENCES

1. **PAPER (required before any advisor circulation).** No claims surface
   may describe this as machine-verified or independently verifiable
   provenance. `docs/paper/draft-v1.md` §5 and §11 must state the trust
   model plainly: hashes bind the evidence the analysis consumes and make
   post-hoc substitution detectable; the root of that chain is the
   experimenters' own committed repository, so the guarantee is
   tamper-evidence and internal consistency, not third-party
   verifiability. A metrology-expert advisor will ask this question
   directly; the paper should answer it before being asked.
2. **CODE (cheap, do it):** derive `project_commit`/`project_tree_state`
   by running git inside the mint rather than accepting typed strings
   (~15 lines); record at mint time whether the head-pin commit is
   contained in `origin/main`; put the trust-model statement IN the
   artifact rather than in a source comment.
3. **The escalation consult already in flight carries this as its
   question 4** and was told the honest answer outranks a clever one —
   including the outcome "no trust root on a single-operator laptop can
   place this outside the operator's reach." That answer is now
   effectively pre-adjudicated by these two reviews; the consult's job
   narrows to WHO PRODUCES the postcollection block and what the
   artifact/paper may claim.
4. **The mint stays BARRED from issuing** (per ESCALATION-U3-
   AUTHENTICATION.md) until the block has a real producer.

## Other adopted U3 findings

- **F2 (HIGH):** the two-stage pin freeze has NO stage linkage — nothing
  compares a final pinset against its desk freeze, so the "declared
  before collection" property is a git-diff a human must remember.
  Either build `verify-desk-freeze` or rule it a checklist item; do not
  leave it implied.
- **F3 (HIGH):** the 919-line `schema_v2.json` has ZERO discriminating
  power in practice (jsonschema is not a dependency per D-009; no test
  validates an instance; runtime skips it by filename). It is the second
  of three hand-synchronized encodings of one shape and a drift plane
  that has ALREADY drifted once. Arm it (+40 test lines) or delete it
  (-919). The prune gate was owed and would have caught this.
- **F4 (MED):** consumer loosening — `_validate_comparative` moved from
  exact plan-sha equality to set membership, so the claim-ingestion
  validator now accepts a cell whose comparative blocks are attributed to
  the other producer's plan. ~20-line fix.
- **F5:** cardinality hardcoded at ~12 sites across three encodings —
  record as the explicit P3 sacrifice (portfolio rule R1 already fences
  it).
