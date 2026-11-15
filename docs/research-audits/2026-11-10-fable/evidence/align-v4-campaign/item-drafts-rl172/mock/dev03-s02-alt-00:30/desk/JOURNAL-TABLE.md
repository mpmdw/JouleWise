# Desk table: mock-cl-dev-03

Built automatically on the Air at 2026-11-16 04:24:54 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L004 | q0 | True | 98.0 | released | 1044.5 | 1156.0 | 0.90 | 1 | 0 | - | 0 | True | True |
| L005 | q0 | True | 304.0 | released | 1170.5 | 1076.0 | 1.09 | 1 | 0 | - | 0 | True | True |
| L006 | q0 | True | 265.0 | released | 1306.1 | 1251.0 | 1.04 | 1 | 0 | - | 0 | True | True |
| L007 | q0 | True | 299.0 | released | 1245.5 | 1156.0 | 1.08 | 1 | 0 | - | 0 | True | True |
| L008 | q0 | True | 613.0 | released | 1479.5 | 1467.0 | 1.01 | 1 | 0 | - | 0 | True | True |
| L009 | q0 | True | 570.0 | released | 1611.1 | 1642.0 | 0.98 | 1 | 0 | - | 0 | True | True |
| L010 | q0 | True | 611.0 | released | 1477.5 | 1467.0 | 1.01 | 1 | 0 | - | 0 | True | True |
| L011 | q0 | True | 168.0 | released | 1209.1 | 1251.0 | 0.97 | 1 | 0 | - | 0 | True | True |
| L012 | q0 | True | 474.0 | released | 1420.5 | 1547.0 | 0.92 | 1 | 0 | - | 0 | True | True |

## Cells and G0 references (kit v1.1)

| leg | prompt tokens | G0 shape | G0 role | reference | G0 outcome | admitted |
|---|---|---|---|---|---|---|
| L004 | 10000 | span | capture | own capture | released | True |
| L005 | 2000 | own | capture | own capture | released | True |
| L006 | 19458 | own | capture | own capture | released | True |
| L007 | 10000 | own | capture | own capture | released | True |
| L008 | 2000 | span | consume | L004 attempt 1 | released | True |
| L009 | 19458 | span | consume | L004 attempt 1 | released | True |
| L010 | 2000 | span | consume | L004 attempt 1 | released | True |
| L011 | 19458 | own | capture | own capture | released | True |
| L012 | 10000 | span | consume | L004 attempt 1 | released | True |

- span reference: L004 attempt 1, 4 consumer(s)

## Named stops

- none (no page)

## Restore and capture

- result: {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "9/9 legs run"}
- KM003C: {"bad_polls": 0, "elapsed_s": 14094.079151630402, "polls": 140940, "present": true, "proven_stopped": true, "usb_errors": 0}
