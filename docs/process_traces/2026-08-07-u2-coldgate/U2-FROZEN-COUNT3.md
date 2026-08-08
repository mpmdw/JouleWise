# U2 successor: FROZEN at count 3 — cold-gate item, not another loop fix (2026-08-08)

**Ruling (magistrate, knowing-when-to-stop):** the attestation-binding
class ("lineage/judgment attestation validated as well-formed, not as
true") reached COUNT 3. The standing escalation trigger already fired at
count 2 and produced ATTESTATION-CONSULT.md. A third same-signature
failure is exactly the disposition the doctrine forbids answering with a
reactive round. U2 successor work is FROZEN on this branch pending a
deliberate cold-gate-shaped resolution — NOT another Sol implementation
round launched from inside this loop.

**Why freezing costs the paper nothing (this is the load-bearing fact):**
U2 successor issuance was ALREADY gated behind Q12 (open, awaiting a
full-register re-presentation) and the third cold-gate convening — neither
has happened. No successor can issue for the 40-hour window regardless;
the three windows (alpha/beta/gamma) are governed by the ISSUED D-079
artifact, and successors matter only if a mid-campaign trigger fires,
which requires new same-epoch captures the window will not produce.
Freezing U2 removes zero night-critical value.

**The diagnosed root cause (ATTESTATION-DELTA-COUNT3.md, executed
probe):** the count-3 instance is not a new site — it is the SAME root
one level deeper. The enrollment registry ACCEPTANCE_ATTESTATION_FIELDS
is AUTO-GENERATED from the schema leaf set with verifiers that always
return True (calibration_acceptance_attestation.py:247/348/395). A
ledger-absent epoch_catalog entry with a correctly self-derived key
passed standalone validation, full parent-aware registry load, AND
ledger-residue VerifiedAcceptance. The exact-set test therefore proves
nothing: adding future_authority_leaf auto-enrolls it VERIFIED/POLICY/S
with a passing verifier. The design (real per-field recompute-and-compare
against authenticated sources) was sound; the implementation built a
Potemkin enrollment. The 133-field forge harness also does not re-pin
downstream (only derivation_sha256), so it never exercised collection-
membership forgeries — which is why it reported clean.

**What a resolution must establish (packet for the cold gate / next
deliberate design step, when U2 is scheduled — post-window is fine):**
1. Every verifier does the RULED recomputation against its authenticated
   source (parent bytes / ledger / registry / repo code), not a stub;
   the source/layer metadata matches ATTESTATION-CONSULT.md's table
   verbatim (the delta lists five current disagreements).
2. epoch_catalog membership == distinct ledger epochs through cutoff
   (reject unreferenced entries) — the specific count-3 hole.
3. The exact-set test must FORCE a new leaf through explicit
   classification + a real verifier (a new schema leaf must FAIL until a
   human enrolls it with a non-trivial verifier), not auto-enroll it.
4. The forge harness re-pins ALL downstream hashes per field and includes
   collection-membership (extra/missing element) forgeries.
5. Cold-gate shape per topology rule 11: a fresh instance on a
   mechanically-assembled packet, since this is the magistrate's own
   adjudication of a thrice-failed class.

**What DID land and is sound (preserve on resume):** trigger-set
recomputation (delta charge 2 PASS), the four non-class closures (charge
5 PASS: fsync partial-order, active-cardinality, /private/tmp skips
removed, missing-operative runtime refusal), the bench five-ID resolution
test, the clean integration merge, and all must-not-change items (FIX-1
equality, D-125 arithmetic byte-identical, issued SHA, genesis pin). The
frozen head is f5e9196; the branch stays pushed as the resume substrate.

**Branch state:** impl/d117-u2-successor @ f5e9196, pushed, EXHIBIT/FROZEN
(never a PR until the cold gate clears). No successor issued. Full suite
2837 OK at the delta's audit.
