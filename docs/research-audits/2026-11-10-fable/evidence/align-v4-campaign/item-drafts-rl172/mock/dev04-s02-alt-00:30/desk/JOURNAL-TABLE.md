# Desk table: mock-cl-dev-04

Built automatically on the Air at 2026-11-16 03:29:05 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L007 | q0 | True | 303.0 | released | 1169.5 | 1076.0 | 1.09 | 1 | 0 | - | 0 | True | True |
| L008 | q0 | True | 619.0 | released | 1660.1 | 1642.0 | 1.01 | 1 | 0 | - | 0 | True | True |
| L009 | q0 | True | 620.0 | released | 1566.5 | 1547.0 | 1.01 | 1 | 0 | - | 0 | True | True |
| L010 | q0 | True | 398.0 | released | 1264.5 | 1467.0 | 0.86 | 1 | 0 | - | 0 | True | True |
| L011 | q0 | True | 562.0 | released | 1603.1 | 1642.0 | 0.98 | 1 | 0 | - | 0 | True | True |
| L012 | q0 | True | 405.0 | released | 1351.5 | 1547.0 | 0.87 | 1 | 0 | - | 0 | True | True |

## Cells and G0 references (kit v1.1)

| leg | prompt tokens | G0 shape | G0 role | reference | G0 outcome | admitted |
|---|---|---|---|---|---|---|
| L007 | 2000 | own | capture | own capture | released | True |
| L008 | 19458 | span | consume | L007 attempt 1 | released | True |
| L009 | 10000 | span | consume | L007 attempt 1 | released | True |
| L010 | 2000 | span | consume | L007 attempt 1 | released | True |
| L011 | 19458 | span | consume | L007 attempt 1 | released | True |
| L012 | 10000 | span | consume | L007 attempt 1 | released | True |

- span reference: L007 attempt 1, 5 consumer(s)

## Named stops

- none (no page)

## Restore and capture

- result: {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "6/6 legs run"}
- KM003C: {"bad_polls": 0, "elapsed_s": 10745.052767753601, "polls": 107450, "present": true, "proven_stopped": true, "usb_errors": 0}
