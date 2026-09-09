# Delta re-audit — D-176 seat 2 producer landing (gpt-6-astra, HIGH, genre review, READ-ONLY, execution lens)
Branch feat/2026-09-08-d176-seat2-producer, head 4b25d29f; the landing is `git diff 0a7c5858 4b25d29f` (the contract
docs/contracts/pack_night_go_receipt.md §§2–6, §7.1 seat-2 row, §10–§10.3 governs; the roots/locators synthesis is at
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cm-coldgate-packet-d176-roots-locators/13-magistrate-synthesis.md; the seat report is /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99dq-seat-d176-seat2-final-astra-report.md).
Audit by EXECUTING, not reading: (1) build a synthetic home + inventory and resolve PRODUCTION_CUSTODY_ROOTS; try a
rehearsal custody_root that is nested, equal-to-parent, wrong basename, symlinked, and a sibling child with the prefixed
id — assert each outcome; try JOULEWISE_BACKUP_ROOTS="" and a non-empty override and confirm the census does not shrink;
(2) G6: a manifest production_roots list that differs from the derived census must raise BundleLoadError; (3) the
driver sequence in scripts/run_night.py: with fixtures, prove (a) GO is never written before ARM verify, (b) a refused
night writes night/receipt.json in the unchanged shape and NO go_receipt.json, (c) pack_root digest mismatch at
preparation and at GO refuses with the ruled codes, (d) the ARM receipt presented is exactly the one the driver wrote
this night (plant a higher-numbered unconsumed receipt → refuse), (e) a second manifest candidate or a symlinked
manifest refuses, (f) the launcher argv contains all eight flags and stdin=DEVNULL, (g) the chain.started marker
sequence from WINDOW-STATUS-GUARD-CENSUS-01 is unchanged (complete marker before any probe; atomic replace); (4) the
night_gate receipt validator and _RECEIPT_KEYS are byte-unchanged (diff them); (5) the 26-key GO set matches the
contract's key table exactly (enumerate); (6) any NEW defect. ≤ 900 words; verdict keys per genre review; no edits;
header < 8192 bytes.
