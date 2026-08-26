# O-1 MAGISTRATE RULING — pinset growth under the `_v4` changed-set contract (2026-08-22)

Cold-gate arc: mechanically-assembled packet (`o1-packet.md`) → cold Fable
adjudicator + Opus contract-lens refuter, blind round 1 → cross-exchange
round 2 (full double-crossover: each seat abandoned its own round-1
position on reading the other) → bounded round 3 (Opus final) →
this synthesis. All rounds preserved unedited in
`cold-fable-verdict.md` and `opus-contract-refutation.md` in this
directory. Per rule 11 this gate was mandatory: both colliding
obligations (RH-8's post-freeze pinset rows + the 112-path contract;
the histsem byte-pin with no update lane) are cold-ratified.

## Ruling

**Option 1 (112→113, allowlisting `tests/test_receipt_histsem.py`) is
REFUTED on V-1(iii)/(vi) mechanism grounds** — not as a covert waiver
of detectability (both seats' final formulation, concurring):

- The static allowlist exists on the recorded condition that ALL
  allowed bytes carry independent authentication (r5 V-1.iii, Sol's
  concession condition). A test-source path cannot satisfy it: its
  final bytes are post-derivation, so no digest condition can be
  pre-committed — cold Fable's own impossibility theorem, turned on
  its round-1 verdict.
- The allowlist is path-granular. Subtracting the test file subtracts
  the ENTIRE histsem normative suite for the window — including the
  coherent-tamper control and the vocabulary-closure tests — while
  Ed's step-6 confirmation covers one literal. The coherent two-file
  substitution (rows + `PINSET_SHA256` together) then crosses every
  mechanical gate (verified against `arm_readiness.py:3916-3964`,
  `:4038-4049`; both seats concur it succeeds mechanically).
- Per the ruled V-1(vi) failure semantics, an unauthenticatable
  allowlist class is a MECHANISM FAILURE routing to the derived
  manifest — never an amendable cost.

**Adopted: O-1-D — versioned-successor pinset with post-window
fixation**, under the merged nine-condition set at
`opus-contract-refutation.md` §4 (round 3), which is INCORPORATED AS
NORMATIVE. Its spine:

1. Pre-derivation reviewed candidate carries the contract amendment
   (governed pinset → closed, ordered, code-enumerated chain), the
   chain-read code delta (constant → tuple, gate loops, `verify_all`
   union, existing refusal codes; CLI and activation model unchanged),
   and the allowlist at **112 with the successor pinset's exact path
   as the 112th entry**. No ruled number is amended.
2. The successor class is DIGEST-CONDITIONAL against Ed's step-6
   confirmation-table digest — V-1(vi) exercised, not waived; this is
   what makes O-1-D lawful where Option 1 is not. No probe may record
   "the test run itself" as an authenticator.
3. Fixation = the first commit after window close (r4-3 commit-freeze):
   successor SHA literal + counts land as NEW assertions touching no
   v1 assertion; independent reviewer recomputes the SHA against Ed's
   step-6 table; the same commit renames the then-false
   `test_differential_self_test_all_nine_packs`.
4. TWO-PART GREEN (material): local suite green is
   forged-`origin/main`-conditional (`s0-runsheet.md:325`;
   `tests/test_receipt_histsem.py:92-103` runs
   `require_published=True`) and must be recorded with the forged OID;
   acceptance closure requires PUBLISHED green. No transcript may
   report local green as "the suite is green."
5. The mint→fixation interval is a REGISTERED RESIDUAL under the
   truth boundary / D-139 A1 with the phase-by-phase controls listed;
   no claim-bearing arm occurs in it (r4-3: dry-run only until
   publication).

   **AMENDED 2026-08-26 under D-155 (NR-7). Re-scoped, not struck; the
   original clause is preserved immediately above.** D-153 A4 amended this
   same clause by re-pricing the interval as mint → *post-window* fixation
   (up to about eight days). That longer interval contains every campaign
   window, and campaign-window arms are claim-bearing — so the
   parenthetical "no claim-bearing arm occurs in it" is false of the
   re-priced interval as a whole. It remains true, and load-bearing, of a
   sub-interval. The terra seat used the literal reading of this clause as
   one of two grounds for killing option beta, so it is a clause that has
   demonstrably driven a real disposition, not inert prose; that is why it
   is restated rather than deleted. This is the ONE home for the re-scoped
   text (`docs/decision_log.md`'s D-151 index row carries a pointer, not a
   second definition). Condition 5 now reads:

   > 5. The residual runs **mint → post-window fixation** (≤ ~8 days worst
   > case, D-153 A4), with the per-phase controls named. Within it: the
   > sub-interval **mint → the first consuming arm** carries no arm of any
   > kind (r4-3 / B-4: dry-run ceremony only); the sub-interval **first
   > consuming arm → post-window fixation** carries the campaign's
   > claim-bearing arms under the published marker and confirmed table,
   > which is the controlled state the residual prices.
6. Chain integrity: closed enumeration (un-enumerated pinset files
   govern nothing); cross-member duplicate `(pack_id, pack_path)`
   refuses `histsem_pinset_invalid`; absent enumerated member keeps
   the rule-11-settled `:36` absence semantics UNCHANGED.
7. FIXED-POINT PRINCIPLE (standing rule, all future transactions):
   **no authenticator path ever enters any allowlist, in any
   transaction.** A proposal to add one is a V-1(vi) tripwire event
   routing to the V-1(vii) derived manifest, not an amendment. `_v5`
   repeats this shape with its own successor artifact.
8. Endorsed out-of-scope defects (to the S-0 runsheet r2 revision):
   the `freeze_evidence_lifecycle.irrelevant_path_allowlist` key is
   absent at HEAD (candidate must author it; `s0-runsheet.md:628`
   would `KeyError`); and the record that the changed-set contract is
   a WINDOW PROPERTY, not a standing repo invariant — the unstated
   fact whose absence generated O-1.
9. Cold Fable's round-2 history-dependent absence tightening is
   **STRUCK** (Opus round 3, magistrate-verified: it inverts the
   rule-11-settled `test_committed_pinset_deletion_gate_returns_normally`
   at `tests/test_receipt_histsem.py:368`, is not entailed by RH-8 per
   the runsheet's own `:792` reconciliation, and fails open on shallow
   history and history rewrite). The contingent condition set
   (merged §4 item 9) governs if a tightening is ever proposed —
   Ed/magistrate sign-off required.

## Recorded dissents and doubts (preserved, not resolved)

- V-1(vii)'s derived, digest-authenticated manifest remains the
  standing structural dissent/alternative (both seats).
- Cold Fable round-1's Option-1 grounds stand unedited as the record
  of a position taken and conceded; likewise Opus round-2's concession.
- The double-crossover itself is recorded as evidence the packet's
  option framing was under-determined; the missing fact (window
  property vs standing invariant) is condition 8's second clause.

## Magistrate verification of record

Replayed at the bench before ruling: the normative test name/assertion
at `tests/test_receipt_histsem.py:368`; the runsheet `:792`
absence-semantics reconciliation; the V-1(iii)/(vi) ruled sentences in
`rulings-r5-consolidation.md:78-107`. The synthesis adopts the
converged verdict on audited grounds — votes were not counted
(round-2 unanimity was a crossover artifact and was treated as such).

## Consequences (work orders)

- The S-1 candidate design incorporates conditions 1, 2, 6, 8 (chain
  contract amendment + chain-read delta + registry allowlist key +
  successor path naming).
- The S-0 runsheet gets an r2 revision: successor-pinset path as the
  112th entry (§2.1 generator), §3.7 rewritten to mint into the
  successor artifact, §4(d) registry-key fix, two-part-green
  transcript language (condition 4), dead option-(b) marker branch
  removed per D-150.
- Fixation and its reviewer step join the transaction runbook at the
  first-post-window-close slot.
