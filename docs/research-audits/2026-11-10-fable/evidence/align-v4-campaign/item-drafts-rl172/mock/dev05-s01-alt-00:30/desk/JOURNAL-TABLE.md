# Desk table: mock-cl-dev-05

Built automatically on the Air at 2026-11-16 03:26:25 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | q0 | True | 275.0 | released | 1221.5 | 1156.0 | 1.06 | 1 | 0 | - | 0 | True | True |
| L002 | q0 | True | 614.0 | released | 1480.5 | 1467.0 | 1.01 | 1 | 0 | - | 0 | True | True |
| L003 | q0 | True | 605.0 | released | 1646.1 | 1642.0 | 1.00 | 1 | 0 | - | 0 | True | True |
| L004 | q0 | True | 323.0 | released | 1189.5 | 1076.0 | 1.11 | 1 | 0 | - | 0 | True | True |
| L005 | q0 | True | 447.0 | released | 1488.1 | 1642.0 | 0.91 | 1 | 0 | - | 0 | True | True |
| L006 | q0 | True | 483.0 | released | 1429.5 | 1547.0 | 0.92 | 1 | 0 | - | 0 | True | True |

## Cells and G0 references (kit v1.1)

| leg | prompt tokens | G0 shape | G0 role | reference | G0 outcome | admitted |
|---|---|---|---|---|---|---|
| L001 | 10000 | own | capture | own capture | released | True |
| L002 | 2000 | span | consume | L001 attempt 1 | released | True |
| L003 | 19458 | span | consume | L001 attempt 1 | released | True |
| L004 | 2000 | own | capture | own capture | released | True |
| L005 | 19458 | span | consume | L001 attempt 1 | released | True |
| L006 | 10000 | span | consume | L001 attempt 1 | released | True |

- span reference: L001 attempt 1, 4 consumer(s)

## Named stops

- none (no page)

## Restore and capture

- result: {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "6/6 legs run"}
- KM003C: {"bad_polls": 0, "elapsed_s": 10585.052767753601, "polls": 105850, "present": true, "proven_stopped": true, "usb_errors": 0}
