# Pedagogy + fidelity review — docs/contracts/window_liveness.md (gpt-6-astra, medium, genre review, READ-ONLY)
Head 655b3368 on docs/2026-09-08-window-liveness-docs. Review docs/contracts/window_liveness.md (and the four pointer edits in
`git diff ac092ccd 655b3368`) against TWO lenses, reported separately:
LENS A — the writing standard (binding, verbatim): "The bar: a reader should be able to REPLICATE the mechanism from
the text alone — rebuild it, not follow the gist. First-use test (run mechanically): every term of art, criteria
word, or verb doing technical work ('converge,' 'admissible,' 'ruled out,' 'custody,' 'threshold', 'stale',
'indeterminate', 'dead-man', 'token'…) is either (a) built from physical reality before first use, (b) glossed in
plain words AT first use, or (c) deleted. A term whose meaning arrives only in later text fails the draft. Why-chain:
every mechanism gets its forcing problem, a concrete worked example with real numbers, and — for anything spatial or
algorithmic — a diagram in which every visual element is named. No word does unpaid work." Walk the document in
reading order and list EVERY term that fails the first-use test with its line; judge whether the worked example lets
a reader rebuild the probe and the census; judge whether the publish decision table is complete (every
LIVE/DEAD/UNKNOWN × marker-state × registry-state combination has a row).
LENS B — fidelity to code: for each mechanism sentence, cite the joulewise/measurement_liveness.py, scripts/run_night.py,
scripts/run_campaign.py or scripts/window_status.sh line that implements it; name any sentence the code contradicts
(e.g. rc semantics of the probe, the atomic-replace sequence, what happens when the custody parent is missing).
≤ 700 words; verdict keys per genre review; severity per finding; no edits; header < 8192 bytes.
