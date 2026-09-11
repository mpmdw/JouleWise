# Cold-gate sitting — paired Opus contract-lens refuter brief (verbatim)

Refuter: Opus instance, contract lens, packet + repo reading, read-only.
This brief triggered the revised sitting. Recorded verbatim by the
magistrate. The three decisive factual claims were bench-verified by the
magistrate before the revised sitting (mint scripts: zero "estimator"
occurrences; no estimator_registration consumer outside the two owning
modules; artifact.py:939-944 binds expected_sha256 + expected_artifact_id).

## FRAMING DEFECTS

1. The "impossible in principle" claim is true of the wrong proposition —
D-120 already declares "single-authority, hash-bound, fail-closed
consistency — never operator independence" as the trust model;
forger-runs-repo-code is conceded repo-wide, so it cannot license the
custody re-statement. What FCM6-01 actually exhibits is narrower: the
consumption profile admits a key with no producer and no domain-owner
verification — verbatim D-120's own defect class, whose adopted remedy was
DELETING the key from production and fixture vocabulary, not validating it
harder.
2. The delta's V3 omitted expected_sha256; the production path binds it
and refuses the forgery (the mutation changes the file sha). Nothing
outside detection_floor.py and floor_extraction.py reads
estimator_registration — the stamp is functionally inert; the packet never
states the attacker's gain.
3. The packet under-states the defect in the other direction: round 6
registered a FALSE provenance claim into pre-registered paper-facing text
(registered_result_provenance_rule =
"registered_results_exist_only_as_governed_extraction_artifacts", hashed
into the rotated sha, pre-registered into committed pack specs). A prior
cold gate banked "registered text may claim only what its committed oracle
exercises"; the refuter-authored oracle exercises arithmetic, not surface
closure.
4. exact_understatement_found=false is a non-finding — the lenses never
ran; the stopping-rule branch cannot be evaluated in either direction on
this evidence.
5. The convergence yardstick was silently swapped: D-132 certified a
magnitude series; FCM6-01 has no magnitude.
6. The (i)/(ii) binary is a construction; the texts leave an unruled
class — the adjudicator makes new law, not applies it.

## STRONGEST CASE FOR (i)

Paper cost of (ii) larger than packeted: re-spec "COSTS the funded p256
prefill contrast's claim capability — the gamma arm likely publishes as
unresolvable" (RUN_STATE); 8.611855 J vs 1.869502 J (~4.6x). Round 6 did
permanently close round 5's class (public surface deleted; namespace-
absence + extraction-only inventory tests). Custody-by-sha-pin partially
reuses existing gauntleted machinery (extraction_report_sha256 vs frozen
U10 literals; file_sha256+artifact_id binding). Ed's cost criterion
satisfied (desk thread).

## STRONGEST CASE FOR (ii)

Same-signature recurrence with the D-120 precedent for where it ends
(three relocations, terminated by vocabulary deletion). A prior cold gate
banked class-keyed same-signature counting; under it rounds 5+6 are one
class and D-132's own doom-loop definition is met. (i) re-opens
registration (sixth rotation + pack regeneration + a new cross-artifact
check to gauntlet — added audit surface the D-124 relicense was ending).
Round 6's arithmetic MOVED (+497 lines) and was unaudited (rule 9). The
tighter floor cannot reach a minted artifact today regardless: zero
estimator vocabulary in either mint script; the v2 mint recomputes with
the default core under exact equality.

## SUPERIOR ALTERNATIVE — ALT-D120 (delete the serialized registration vocabulary)

1. CellReport.as_row() stops writing estimator_registration; registration
   stays in-process on extraction-produced CellReports only.
2. Remove the key from _D117_MINT_FLOOR_OPTIONAL_KEYS — closed keys then
   REFUSE any report carrying it (the delta's V2 forgery dies unknown-key).
3. Remove from _CMP_OPTIONAL_KEYS + delete the self-equality branch —
   validate_floor_artifact errors and authenticate_floor_artifact_bytes
   raises BEFORE returning (V3 dies at the same seam).
4. Registration lives where already governed: the committed pre-registered
   extraction specs; provenance is RE-DERIVED, not read (the mint
   independently recomputes floors from authenticated members and pins
   extraction_report_sha256 vs frozen U10 literals).
5. Restate the provenance rule to what the design enforces; rotate once.
Honest limits: artifact no longer self-describes its estimator; does NOT
deliver the tighter floor (mint vocabulary absent); does NOT repair the
unaudited moved arithmetic (full fresh delta owed). Nothing shipped
breaks: zero occurrences of the key in the mint1 artifact or committed
fixtures. Tell: the mint floor profile has no estimator key at all — the
registration stamp is vestigial asymmetry.

## HYBRID (schedule/soundness separation)

Merge the fallback now (freeze lane unblocks); keep FCM-01 alive unmerged
executing ALT-D120 + the owed full delta + the mint-estimator workstream;
re-spec back only if all three land before the freeze wave. D-132 forbids
stopping work, not deferring consumption. Cost: one further mechanical
pack regeneration.

## OMISSIONS (the twelve, abridged)

G1 means the moved arithmetic is unaudited (full fresh delta required for
ANY landing). exact_understatement_found=false is not a finding. No
consumer reads the forged field. The delta's authenticate call omitted
expected_sha256. The mint has no estimator vocabulary at all (changes the
value of both branches; absent from packet, D-132, and the round-6
report). The paper stake unquantified (8.611855 vs 1.869502 J, ~4.6x;
gamma arm likely unresolvable). Round 6 rotated the sha and added the
falsified provenance claim into pre-registered paper-facing text. Banked
cold-gate recommendations not quoted (registered-text/oracle rule;
class-keyed counting; ulp-units delta reporting). The fallback's own gate
status unstated. RUN_STATE's "FLOOR-COMMONMODE-01 BANKED UNGATED 425f75f"
debt absent from the packet. Ed's quoted ruling answered the round-5
question and carries the pre-committed stopping rule in the same passage.
F2 (5.1e-15) was lead-adjudicated in a commit message, self-graded.
