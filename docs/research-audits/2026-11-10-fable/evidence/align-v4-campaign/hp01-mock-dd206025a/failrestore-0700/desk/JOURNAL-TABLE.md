# Desk table: mock-cl-hp-01

Built automatically on the Air at 2026-11-15 08:39:09 PST by joulewise.cadence.desk (leg-summary-v1). Operational fields only. Block AC powermode 2.

## Legs

| leg | band | reached | G0 s | G0 outcome | wall s | budget s | wall/budget | attempts | contaminated redos | redo reasons | OS max | nominal |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | q0 | True | 217.0 | released | 1258.1 | 1251.0 | 1.01 | 1 | 0 | - | 0 | True |
| L002 | q0 | True | 182.0 | released | 1223.1 | 1251.0 | 0.98 | 1 | 0 | - | 0 | True |
| L003 | q0 | True | 293.0 | released | 1334.1 | 1251.0 | 1.07 | 1 | 0 | - | 0 | True |

## Named stops

- **REFUSAL**: chain_exit_code=2 chain_outcome=INCOMPLETE outcome=REFUSED
- **RESTORE_UNPROVEN**: the close did not prove AC powermode 0 and no High Power marker; it holds everything until the lead restores and records it

## Restore and capture

- result: {"chain_exit_code": 2, "chain_outcome": "INCOMPLETE", "fault": false, "outcome": "REFUSED", "restore_proven": false, "verdict": "3/3 legs run"}
- KM003C: {"bad_polls": 0, "elapsed_s": 5949.18638420105, "polls": 59491, "present": true, "proven_stopped": true, "usb_errors": 0}
