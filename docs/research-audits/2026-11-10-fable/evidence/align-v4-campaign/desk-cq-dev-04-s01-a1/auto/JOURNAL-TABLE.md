# Desk table: cq-dev-04-s01-a1

Built automatically on the Air at 2026-11-17 08:40:38 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | q0 | True | 201.0 | released | 1121.7 | 1156.0 | 0.97 | 1 | 0 | - | 2 | False | True |
| L002 | q0 | True | 202.0 | released | 1245.3 | 1251.0 | 1.00 | 1 | 0 | - | 2 | False | True |
| L003 | q0 | True | 145.7 | released | 977.2 | 1076.0 | 0.91 | 1 | 0 | - | 2 | False | True |
| L004 | q0 | True | 221.3 | released | 1155.0 | 1156.0 | 1.00 | 1 | 0 | - | 2 | False | True |
| L005 | q0 | True | 151.9 | released | 980.8 | 1467.0 | 0.67 | 1 | 0 | - | 2 | False | True |
| L006 | q0 | True | 215.3 | released | 1266.1 | 1251.0 | 1.01 | 2 | 1 | cpu_load | 2 | False | True |

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
- KM003C: {"bad_polls": 0, "elapsed_s": 10109.807637541, "polls": 50549, "present": true, "proven_stopped": true, "usb_errors": 0}
