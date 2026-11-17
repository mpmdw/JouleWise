# Desk table: cq-dev-04-s02-a1

Built automatically on the Air at 2026-11-17 08:40:42 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L007 | q0 | True | 132.5 | released | 959.2 | 1076.0 | 0.89 | 1 | 0 | - | 1 | False | True |
| L008 | q0 | True | 205.0 | released | 1251.2 | 1642.0 | 0.76 | 1 | 0 | - | 2 | False | True |
| L009 | q0 | True | 213.2 | released | 1139.9 | 1547.0 | 0.74 | 1 | 0 | - | 2 | False | True |
| L010 | q0 | True | 147.9 | released | 977.0 | 1467.0 | 0.67 | 1 | 0 | - | 2 | False | True |
| L011 | q0 | True | 215.3 | released | 1259.3 | 1642.0 | 0.77 | 1 | 0 | - | 2 | False | True |
| L012 | q0 | True | 217.2 | released | 1145.1 | 1547.0 | 0.74 | 1 | 0 | - | 2 | False | True |

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
- KM003C: {"bad_polls": 0, "elapsed_s": 8838.811537666, "polls": 44194, "present": true, "proven_stopped": true, "usb_errors": 0}
