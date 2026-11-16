# cl-dev-03.v1.1 counted pilot (cq-dev-03-s01-a1, L001-L003): desk, hand table, R9 and class A smoke (PROPOSED)

Desk builder for the lead, on the Air. Verdicts below are PROPOSED; the lead signs them (RUN_STATE 355 "After").

- Span `cq-dev-03-s01-a1`, kit `cl-dev-03.v1.1` sha256 `0f535774…e14b`, runner `cadence-legs-v1.1`, batch window `02:00-02:35`; receipt 03:38:43-05:10:07 PST (RUN_STATE 362 launch, 363 Check).
- Data: read-only Air copy, 123 manifest entries sha256 OK, `.air` = `.mbp`. Desk code `2d347f721` (clean), kit outside the checkout.
- Blinding: every open is in OPENED.txt; no energy, power, meter-sample, powermetrics, transcript, slot, hazards or telemetry file was opened.

**R9: PASSED (proposed)** and **smoke: MET (proposed)**. Details in RESULT.json (`R9_proposed`, `smoke_proposed`).

## R9 table
| line | value |
|---|---|
| closes with complete records | 3 of 3; receipt rc 0, MEASURED_OK, chain COMPLETE, 25/25 steps rc 0, decode 4,096/4,096 each |
| admitted | 3 of 3 (desk, each leg_summary.json); 3 of 3 included by hand |
| excluded legs | none; no redo; none refilled |
| hand table = desk | 0 of 57 per-leg and 0 of 6 span-level values differ, inclusion included; stops.json [] and hand [] |

| leg | cell | role | G0 s | wall / budget s | OS max | rule 5 longest run (s of 60) | realized prefill |
|---|---|---|---|---|---|---|---|
| L001 | 2,000 own | capture | 136.5 | 970.2 / 1,076 | 1 | 2 | 2,024 (+1.2 %) |
| L002 | 19,458 span | consume | 209.1 | 1,251.9 / 1,642 | 2 | 2 | 19,458 (0.0 %) |
| L003 | 10,000 own | capture | 221.5 | 1,155.4 / 1,156 | 2 | 6 | 10,015 (+0.15 %) |

## Class A smoke (RL-161 section 2, RL-158 section 2)
L002 (consume, span-shaped) released its G0 after 209.095 s (timeout 1,200 s) against L001's capture and ran its turn (turn began 0.085 s after the release; decode 4,096/4,096, complete, admitted). Evidence: `g0_reference_source` `cadence-cl-dev-03-l001`; `g0_reference_record_sha256` `1675f044…bf6e` equals the `record_sha256` in L001's own `align_window_reference.json` (status captured); L002's G0 gate row reference (TV 34.174 C, span_ns) equals L001's capture; `span_reference` = L001 attempt 1, not excluded, not redone (no mark). L002 writes no window reference of its own (by design).

## Rule 5, the 05:00 maintenance bucket
softwareupdated 2,598, mobileassetd 2,217, XProtect* 612 all fall in L003's post-turn phase (burst 05:08:54-05:08:56; the turn ended 05:08:41). By the load journal: longest run over 0.5 core is 6 s (max 3.764 cores) of the 60 s needed; does not fire; recorded clean; hand agrees. Rule 5 passes; no redo owed. See MAINTENANCE-OVERLAP.md and RESULT.json `maintenance_overlap`.

## Q1 print and Q5
`hand/r1print.out` (soak reference TV0h = TV1h 34.159 C; L001 capture; L002 release reading TV 35.019 C, Tf08 35.903 C, G0 wait 209.1 s). No leg is more than 5 % from its nominal prefill. Completion record: `evidence/cadence-standing/q1/cq-dev-03-s01-a1.json`.
