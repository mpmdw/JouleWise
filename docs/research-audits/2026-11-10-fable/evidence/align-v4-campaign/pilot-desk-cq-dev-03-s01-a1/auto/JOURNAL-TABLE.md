# Desk table: cq-dev-03-s01-a1

Built automatically on the Air at 2026-11-16 05:33:58 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | q0 | True | 136.5 | released | 970.2 | 1076.0 | 0.90 | 1 | 0 | - | 1 | False | True |
| L002 | q0 | True | 209.1 | released | 1251.9 | 1642.0 | 0.76 | 1 | 0 | - | 2 | False | True |
| L003 | q0 | True | 221.5 | released | 1155.4 | 1156.0 | 1.00 | 1 | 0 | - | 2 | False | True |

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
- KM003C: {"bad_polls": 0, "elapsed_s": 5482.812866542, "polls": 27414, "present": true, "proven_stopped": true, "usb_errors": 0}
