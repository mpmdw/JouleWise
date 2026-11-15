# Desk table: mock-cl-dev-05

Built automatically on the Air at 2026-11-16 03:07:55 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L007 | q0 | True | 309.0 | released | 1350.1 | 1251.0 | 1.08 | 1 | 0 | - | 0 | True | True |
| L008 | q0 | True | 439.0 | released | 1305.5 | 1467.0 | 0.89 | 1 | 0 | - | 0 | True | True |
| L009 | q0 | True | 135.0 | released | 1081.5 | 1156.0 | 0.94 | 1 | 0 | - | 0 | True | True |
| L010 | q0 | True | 99.0 | released | 965.5 | 1076.0 | 0.90 | 1 | 0 | - | 0 | True | True |
| L011 | q0 | True | 249.0 | released | 1290.1 | 1251.0 | 1.03 | 1 | 0 | - | 0 | True | True |
| L012 | q0 | True | 406.0 | released | 1352.5 | 1547.0 | 0.87 | 1 | 0 | - | 0 | True | True |

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
- KM003C: {"bad_polls": 0, "elapsed_s": 9475.052767753601, "polls": 94750, "present": true, "proven_stopped": true, "usb_errors": 0}
