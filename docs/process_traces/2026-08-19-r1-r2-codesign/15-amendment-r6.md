# AMENDMENT (2026-08-19, magistrate) — r6 supersedes r5 as the family's bound generation

The ratified R2 ruling (14-r2-ruling.md) states in S7/S8 that the `_v3`
family binds r5 and, at S8's close, that "R2's files do not intersect
r4/r5's four estimator pins ⇒ no r6 (both seats verified)." That
verification was TRUE OF THE DESIGN and FALSIFIED BY A FIX ROUND: S1 fix
round 2 (commit 3038eeb), executing the two-lens blocker verdict
(BLOCKER-2 predicate inversion; the S3 taxonomy split), edited
`joulewise/uncertainty_evidence.py` and `joulewise/reduce.py` — two of the
four D-079-pinned estimator sources — and therefore forced the
science-neutral r6 reissue in the same commit (19-member replay, zero
mismatches; custody in the session scratchpad `r6-issuance/`, digest
`0227bca3…`).

AMENDED READINGS (the ruling text is preserved unedited; this addendum
governs where they conflict):

- S7: the `_v3` family binds **r6** at birth (executed:
  `configs/campaigns/d117_*_v3/generate_configs.py` SUCCESSOR_ACCEPTANCE_ID
  = `d079_calibration_acceptance_v2_n17_r6`).
- S8 sequencing: S1 produced r5; the fix rounds produced r6 BEFORE S2, so
  the goldens wave and the family emission both consumed r6 — the "goldens
  once" property held (one wave, against r6).
- S8 final claim: the no-r6 verification was correct against the DESIGN's
  file set; the blocker fixes ratified after the lens reviews expanded the
  edited set. Recorded as an instance of the general rule that fix rounds
  can invalidate design-time verifications, which is why the delta
  re-audit re-verified the pin state (S1 contract lens: all four pins
  match head bytes at every commit boundary).

r5 remains registered, byte-identical history — exactly as r3/r4.
Decision-log rows D-145/D-147 carry pointers to this amendment.
