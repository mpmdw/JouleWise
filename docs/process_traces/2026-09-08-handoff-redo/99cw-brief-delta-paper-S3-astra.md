# Delta re-audit — paper S3 claim-side bound (gpt-6-astra, HIGH, genre review, READ-ONLY, execution lens)
Branch feat/2026-09-08-paper-S3, head ed44276a; landing = `git diff ac092ccd ed44276a`. It implements the synthesis at
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bb-coldgate-packet-paper-s3/13-magistrate-synthesis.md (read it; 10/11 beside it are evidence). Audit with an
executed check per claim: (1) copy-only: is every sidecar field byte-copied from claim_verdicts (never recomputed)?
Trace the producer; run it on the fixture and diff the numerals; (2) the join: build a v3-shaped manifest + verdicts
fixture where two contrasts share an ordered cell list and confirm injectivity refuses; permute; include a
`refused` resolution; (3) exact equality: mutate one numeral by 1e-13 and by a trailing zero ("4.0" vs "4") — both must
refuse; bool True in place of 1 refuses; (4) the unit blocker: a ratio estimand rendered into a J-typed cell refuses;
(5) the gate re-evaluates from verdicts only (mutate the sidecar's interval while verdicts are unchanged → gate
outcome unchanged; mutate verdicts → gate changes); (6) the 20 kills: run tests/fixtures/paper_custody/run_kills.py and
confirm 20/20 against the head; then add TWO kills of your own devising and report whether they die; (7) the new
contract docs/contracts/paper_claim_side_bound.md: can you rebuild the producer from it alone (list any symbol used
before definition or any formula that differs from code)? (8) any NEW defect. ≤ 900 words; verdict keys per genre
review; no edits; header < 8192 bytes.
