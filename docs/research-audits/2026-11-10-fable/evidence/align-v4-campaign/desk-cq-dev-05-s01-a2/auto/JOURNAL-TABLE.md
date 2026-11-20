# Desk table: cq-dev-05-s01-a2

Built automatically on the Air at 2026-11-19 14:14:48 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | q0 | True | 237.6 | released | 1170.2 | 1156.0 | 1.01 | 1 | 0 | - | 1 | False | True |
| L002 | q0 | True | 146.9 | released | 974.1 | 1467.0 | 0.66 | 1 | 0 | - | 0 | True | True |
| L003 | q0 | True | 210.1 | released | 1252.5 | 1642.0 | 0.76 | 1 | 0 | - | 2 | False | True |
| L004 | q0 | True | 148.8 | released | 977.9 | 1076.0 | 0.91 | 2 | 1 | cpu_load | 1 | False | True |
| L005 | q0 | True | 212.2 | released | 1256.4 | 1642.0 | 0.77 | 1 | 0 | - | 2 | False | True |
| L006 | q0 | True | 218.3 | released | 1146.3 | 1547.0 | 0.74 | 1 | 0 | - | 2 | False | True |

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
- KM003C: {"bad_polls": 0, "elapsed_s": 9869.211399375, "polls": 49346, "present": true, "proven_stopped": true, "usb_errors": 0}
