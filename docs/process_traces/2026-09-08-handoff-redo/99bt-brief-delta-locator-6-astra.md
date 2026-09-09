# Delta re-audit — ICLOUD-CUSTODY-LOCATOR-01 part 6 (gpt-6-astra, HIGH, genre review, READ-ONLY)
Branch fix/2026-09-08-icloud-custody-locator, head b598113e; the round is `git diff 96bfb448 b598113e`. It answers the Opus
refutation at /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bi-ref-locator-5-opus-contract-review.md
and the Astra delta at /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bj-delta-locator-5-astra-report.md
under the brief /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bk-brief-locator-part6-astra.md.
Audit with file:line and an executed or in-memory check per claim:
1. CENSUS: run the shipped inventory against each escape shape from the previous delta (local literal, assignment
   alias incl. callable alias, factory kwargs, forwarded kwargs, second call in an allowlisted function, shared(mode)
   with replay from an issuing entry, positional mode) and against three NEW shapes of your own devising; report
   which are detected and which are not; is every undetectable shape covered by the runtime guard test?
2. ALLOWLIST: for each of the 14 rows, trace the chain yourself and confirm it is genuinely replay-only OR guarded
   before append/mint; name any row whose reason text overclaims.
3. CANDIDATE DISCOVERY: with a non-empty override, original absent, planted replacement, does an ISSUING session's
   discovery observe ABSENT everywhere in the chain (calibration_bracketing.py :1081/:1237/:1309/:2018 and
   whole_window.py :697), and does the replay session observe the replacement? Execute the regression and one
   in-memory counterfactual.
4. ABORT-SESSION guard (calibration_ledger.py ~:5400): does it fire before the lease and before any status probe;
   can abort be reached by another public route that skips it?
5. CAMPAIGN opt-in (run_campaign.py ~:5257): trace both branches to their entries; confirm neither reaches the four
   issuing categories; confirm the ordinary wrapper leaves whole_window=False.
6. Any NEW defect (fix rounds introduce defects). Verdict keys per genre review; ≤ 800 words; no edits; header < 8192 bytes.
