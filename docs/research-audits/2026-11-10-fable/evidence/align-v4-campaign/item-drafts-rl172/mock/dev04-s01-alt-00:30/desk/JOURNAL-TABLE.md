# Desk table: mock-cl-dev-04

Built automatically on the Air at 2026-11-16 03:04:32 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | q0 | True | 140.0 | released | 1086.5 | 1156.0 | 0.94 | 1 | 0 | - | 0 | True | True |
| L002 | q0 | True | 274.0 | released | 1315.1 | 1251.0 | 1.05 | 1 | 0 | - | 0 | True | True |
| L003 | q0 | True | 195.0 | released | 1061.5 | 1076.0 | 0.99 | 1 | 0 | - | 0 | True | True |
| L004 | q0 | True | 153.0 | released | 1099.5 | 1156.0 | 0.95 | 1 | 0 | - | 0 | True | True |
| L005 | q0 | True | 475.0 | released | 1341.5 | 1467.0 | 0.91 | 1 | 0 | - | 0 | True | True |
| L006 | q0 | True | 197.0 | released | 1238.1 | 1251.0 | 0.99 | 1 | 0 | - | 0 | True | True |

## Cells and G0 references (kit v1.1)

| leg | prompt tokens | G0 shape | G0 role | reference | G0 outcome | admitted |
|---|---|---|---|---|---|---|
| L001 | 10000 | own | capture | own capture | released | True |
| L002 | 19458 | own | capture | own capture | released | True |
| L003 | 2000 | own | capture | own capture | released | True |
| L004 | 10000 | own | capture | own capture | released | True |
| L005 | 2000 | span | consume | L001 attempt 1 | released | True |
| L006 | 19458 | own | capture | own capture | released | True |

- span reference: L001 attempt 1, 1 consumer(s)

## Named stops

- none (no page)

## Restore and capture

- result: {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "6/6 legs run"}
- KM003C: {"bad_polls": 0, "elapsed_s": 9272.052767753601, "polls": 92720, "present": true, "proven_stopped": true, "usb_errors": 0}
