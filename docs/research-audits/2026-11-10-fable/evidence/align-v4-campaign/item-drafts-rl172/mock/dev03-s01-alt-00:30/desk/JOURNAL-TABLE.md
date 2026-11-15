# Desk table: mock-cl-dev-03

Built automatically on the Air at 2026-11-16 02:11:21 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | q0 | True | 201.0 | released | 1067.5 | 1076.0 | 0.99 | 1 | 0 | - | 0 | True | True |
| L002 | q0 | True | 591.0 | released | 1632.1 | 1642.0 | 0.99 | 1 | 0 | - | 0 | True | True |
| L003 | q0 | True | 305.0 | released | 1251.5 | 1156.0 | 1.08 | 1 | 0 | - | 0 | True | True |

## Cells and G0 references (kit v1.1)

| leg | prompt tokens | G0 shape | G0 role | reference | G0 outcome | admitted |
|---|---|---|---|---|---|---|
| L001 | 2000 | own | capture | own capture | released | True |
| L002 | 19458 | span | consume | L001 attempt 1 | released | True |
| L003 | 10000 | own | capture | own capture | released | True |

- span reference: L001 attempt 1, 1 consumer(s)

## Named stops

- none (no page)

## Restore and capture

- result: {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "3/3 legs run"}
- KM003C: {"bad_polls": 0, "elapsed_s": 6081.0263838768005, "polls": 60810, "present": true, "proven_stopped": true, "usb_errors": 0}
