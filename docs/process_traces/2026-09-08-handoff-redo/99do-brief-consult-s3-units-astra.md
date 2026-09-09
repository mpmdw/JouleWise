# Consult — S3 claim-side bound: which unit vocabulary binds the sidecar's `unit` field? (gpt-6-astra, HIGH, genre review, READ-ONLY)
Rule-11 standing trigger: the unit vocabulary has been wrong twice on this lane (Opus 99cz finding 2 said "J/token"
does not exist and pointed at AP-spec estimand units; the S3 fix pinned _UNITS to those; Opus 99dn N-B1 then found the
verdict-side authority joulewise/analysis_manifest.py ~:397 and ~:1320–1321 requires 'J/token' for ratio estimands and
retracted). Read both reviews at absolute paths /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cz-ref-paper-S3-opus-contract-review.md and
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99dn-delta-paper-S3-fix-opus-review.md, then the code: joulewise/analysis_engine/claim_side_bound.py (~:24, :125–135),
joulewise/analysis_manifest.py (:397, :1320–1321 and every other place a unit is validated), joulewise/analysis_engine/artifact.py
(validate_claim_verdicts — does it impose ANY unit vocabulary?), joulewise/analysis_engine/ratio.py (RATIO_ESTIMAND_KEYS,
RATIO_FORMS, any unit field), configs/analysis_registry/ap_spec_draft_front.v2.json and ap_spec_native_mtp_front.v2.json
(estimand units J/committed_output_token, J/accepted_draft_token), tests/test_analysis_claims.py ~:1721–1723 (the verdict
shape actually built). Answer with file:line: (1) at which layer does a unit string originate for a ratio contrast
(AP-spec estimand → manifest → verdict), and is it transformed between layers (e.g. the manifest normalises every
per-token unit to 'J/token', or the AP-spec unit is carried through)? (2) therefore, what EXACT vocabulary must the
sidecar (which copies from claim_verdicts) accept, and what must it refuse; (3) is there ONE authoritative source the
sidecar can import (a constant or validator) so the vocabulary is never pinned twice; (4) the regression that makes the
membership guard bite (a valid B8 mapping with a foreign unit must refuse; a valid B8 with the authoritative unit must
pass). ≤ 600 words; verdict keys per genre review; no edits; header < 8192 bytes.
