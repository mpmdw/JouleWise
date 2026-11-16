# Desk table: cq-dev-03-s02-a1

Built automatically on the Air at 2026-11-16 11:37:34 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L004 | q0 | True | 205.0 | released | 1133.3 | 1156.0 | 0.98 | 1 | 0 | - | 2 | False | True |
| L005 | q0 | True | 152.9 | released | 982.0 | 1076.0 | 0.91 | 1 | 0 | - | 2 | False | True |
| L006 | q0 | True | 204.1 | released | 1255.4 | 1251.0 | 1.00 | 1 | 0 | - | 2 | False | True |
| L007 | q0 | True | 221.2 | released | 1151.8 | 1156.0 | 1.00 | 1 | 0 | - | 2 | False | True |
| L008 | q0 | True | 149.9 | released | 983.2 | 1467.0 | 0.67 | 1 | 0 | - | 2 | False | True |
| L009 | q0 | True | 211.1 | released | 1255.3 | 1642.0 | 0.76 | 1 | 0 | - | 2 | False | True |
| L010 | q0 | True | 145.6 | released | 973.8 | 1467.0 | 0.66 | 1 | 0 | - | 2 | False | True |
| L011 | q0 | True | 211.1 | released | 1256.9 | 1251.0 | 1.00 | 1 | 0 | - | 2 | False | True |
| L012 | q0 | True | 213.2 | released | 1138.6 | 1547.0 | 0.74 | 1 | 0 | - | 2 | False | True |

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
- KM003C: {"bad_polls": 0, "elapsed_s": 12239.411014292, "polls": 61197, "present": true, "proven_stopped": true, "usb_errors": 0}
