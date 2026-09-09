WRITE_SCOPE: []

# Delta re-audit — D-176 seat 4 (gpt-6-astra, HIGH, genre review, EXECUTION lens; NO repository writes — /tmp only; assert `git status --short` empty at the end)
Branch feat/2026-09-08-d176-seat4-rehearsal, head 3032dd93 = int c16a2ac4 (seats 2+3 + census cure + nits) + seat 4 (9bc8861d).
Seat 4's round is `git diff e73e5439 9bc8861d`; report at /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ft-seat-d176-seat4-final-astra-report.md; rulings at
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fe-magistrate-ruling-g7-control.md (items 1–9). EXECUTE with TemporaryDirectory fixtures: (a) PRE-ARM ADMISSION —
with NO ARM receipt on disk, present (i) the six-key rehearsal receipt and (ii) a rehearsal-purpose 26-key GO to a
production plan's launcher: both must refuse launch_go_receipt_invalid with details receipt_class /
rehearsal_purpose_on_production_id, BEFORE any ARM path is touched (instrument the ARM reader to assert zero calls);
(b) the 2×2 purpose/window table at GO production: unprefixed+T0_REHEARSAL refuse; prefixed+other purpose refuse;
prefixed+T0_REHEARSAL+disjoint accept; prefixed+T0_REHEARSAL+not-disjoint refuse; (c) G5: a D-149 receipt → refused,
never grandfathered; a current GO with one condition flipped to FAIL → G5 fails; recomputation ignores the receipt's
own verdict field; (d) G7: run the producer against a completed rehearsal fixture: the control custody is a sibling
child named <window_id>-g7-control, night/g7_refusal.json is create-once 0600 with the exact v1 schema, both
presentations first_refusal true, absence flags true; then mutate: a pre-existing consumption record in the control
custody → absence false → verdict FAIL; a second run → create-once refusal; the completed rehearsal's bytes unchanged
(hash before/after); (e) bundle locator: G7 acceptance re-validates from the bytes; a tampered g7_refusal.json →
refused; (f) frozen seams byte-diff vs main. Any NEW defect. ≤ 800 words; verdict keys per genre review; header < 8192.
