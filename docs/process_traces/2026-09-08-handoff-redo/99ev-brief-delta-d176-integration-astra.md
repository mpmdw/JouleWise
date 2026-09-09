WRITE_SCOPE: []

# Delta re-audit — D-176 integrated head seats 2+3 (gpt-6-astra, HIGH, genre review, EXECUTION lens; NO repository writes — /tmp only; assert `git status --short` empty at the end)
Branch int/2026-09-08-d176-seats-2-3, head 4d72e524 = main 99a42edb + seat 2 (ad74e36c) + seat 3 (fda090f2) + the
integration commit (seat report at /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99et-seat-d176-integration-astra-report.md). Contract:
docs/contracts/pack_night_go_receipt.md; synthesis /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cm-coldgate-packet-d176-roots-locators/13-magistrate-synthesis.md.
EXECUTE, with TemporaryDirectory fixtures: (1) the end-to-end fixture in tests/test_launch_window.py (~:2031) and, on
top of it, YOUR OWN mutations at each seam: (a) plan bytes altered after GO → consumer refuses on plan_sha256; (b)
pack tree altered after preparation → refused at GO; after GO → refused at consumption; (c) a second, higher-numbered
unconsumed ARM receipt planted → GO refused; (d) GO issued/valid_until moved so the monotonic clock is outside →
refused; (e) a T0_REHEARSAL purpose with custody_root nested under a production window dir → refused
rehearsal_roots_not_disjoint; with custody_root a sibling child named by the prefixed id → accepted; measurement_root
under ~/night-custody → refused; a relative custody_root → refused (name the code); (f) replay a consumed record with
the GO bytes altered → verify_consumed_launch refuses; (g) a v2 consumption record on live replay → refused; with
require_current_boot=False → accepted; (h) run the driver twice in one boot → the second refuses (single consumption
point); (i) confirm night/receipt.json for a REFUSED pack night validates under the FROZEN validator and NO
go_receipt.json exists. Report each as executed/killed with the code observed. (2) Byte-diff the frozen seams vs main.
(3) Any new defect. ≤ 900 words; verdict keys per genre review; header < 8192 bytes.
