# Desk table: cq-dev-05-s02-a1

Built automatically on the Air at 2026-11-19 14:14:49 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L007 | q0 | True | 206.0 | released | 1247.9 | 1251.0 | 1.00 | 1 | 0 | - | 1 | False | True |
| L008 | q0 | True | 143.7 | released | 973.1 | 1467.0 | 0.66 | 1 | 0 | - | 1 | False | True |
| L009 | q0 | True | 227.4 | released | 1163.1 | 1156.0 | 1.01 | 1 | 0 | - | 2 | False | True |
| L010 | q0 | True | 142.7 | released | 973.2 | 1076.0 | 0.90 | 1 | 0 | - | 1 | False | True |
| L011 | q0 | True | 207.2 | released | 1248.6 | 1251.0 | 1.00 | 1 | 0 | - | 2 | False | True |
| L012 | q0 | True | 221.4 | released | 1148.3 | 1547.0 | 0.74 | 1 | 0 | - | 2 | False | True |

## Cells and G0 references (kit v1.1)

| leg | prompt tokens | G0 shape | G0 role | reference | G0 outcome | admitted |
|---|---|---|---|---|---|---|
| L007 | 19458 | own | capture | own capture | released | True |
| L008 | 2000 | span | consume | L007 attempt 1 | released | True |
| L009 | 10000 | own | capture | own capture | released | True |
| L010 | 2000 | own | capture | own capture | released | True |
| L011 | 19458 | own | capture | own capture | released | True |
| L012 | 10000 | span | consume | L007 attempt 1 | released | True |

- span reference: L007 attempt 1, 2 consumer(s)

## Named stops

- none (no page)

## Restore and capture

- result: {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "6/6 legs run"}
- KM003C: {"bad_polls": 0, "elapsed_s": 8861.412942667, "polls": 44307, "present": true, "proven_stopped": true, "usb_errors": 0}
