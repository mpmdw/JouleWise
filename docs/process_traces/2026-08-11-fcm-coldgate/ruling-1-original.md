# Cold-gate sitting 1 — original ruling (WITHDRAWN by the revised sitting)

Adjudicator: fresh Fable instance, no loop context (packet-only). Recorded
verbatim from the adjudication transcript by the magistrate; the revised
ruling in ruling-3-revised.md supersedes this document.

## VERDICT

**(i) AUTHORIZE ROUND 7 under the custody-closure design** — with a
hardened claim re-statement, a single-seam check obligation, and a
re-armed pre-committed terminal rule: this is the last round for this
defect class. If the round-7 delta finds any admission of registered
identity whose artifact sha is absent from the committed custody record,
or any exact understatement at an admitted input, fallback 681ab49 merges
automatically — no further rounds, no further gate sittings.

## REASONING (abridged headings; full text in the session transcript)

1. FCM6-01 reproduced bit-for-bit (V2/V3 re-executed; forged artifact sha
   8afdcb51...9ddaaa carrying registration sha dea20dc0...).
2. The in-principle claim held as stated: no validator-only fix can close
   a serialization boundary under repo-trust; only a committed sha pin
   (custody) closes an identity claim. Round 5/round 6 share one
   signature: construction-closure of a serialization boundary was the
   wrong theory both times; the sitting IS the mandated consult.
3. Custody-closure is the repo's own D-120 pattern; the floor-artifact
   class is the outlier lacking a pin registry.
4. The design is checkable at the claim boundary (artifact.py ~941;
   inputs.py ~1279); no committed artifact carries estimator_registration,
   so the custody record starts empty and maximally strict.
5. Fallback-now rejected: exact_understatement_found=false (LATER
   CONCEDED a non-finding), D-132's terms, Ed's cost logic.

## OBLIGATIONS (as originally issued)

O1 claim text custody-honest (never "closed by construction"); O2 byte-sha
seam check with producer/consumer separation; O3 full re-execution of the
interrupted lenses + F2 adjudication on the record; O4 terminal rule (one
round); pack-freeze stays gated on the round-7 delta.

## REVERSAL-CONDITIONS (as originally issued)

Bypass path around the byte seam; pin instability; producer/consumer
collapse; any exact understatement; Ed withdrawing D-132 or ruling the
tighter-margin value immaterial.
