**HOLD.** Four synthetic witnesses reproduced:

- Contention-only exclusions still fail the common desk.
- C9–C14 lack U3 policy scope, making healthy reserves inconclusive.
- Terminal-barred windows can pass admission with a nonempty pool.
- Balance reporting drops normalized contention events.

Committed `cc223ad65` on `align/2026-11-08-r11-delta6-sol2`. Clean tree; not pushed.

Changed only the [report](docs/align/v4/R11-DELTA6-sol2.md) and [witness tests](tests/align/test_r11_delta6_sol2.py).

Verification: 86 existing focused tests passed. `python3.13 -B -m unittest tests.align.test_r11_delta6_sol2` ran 11 tests: four intentionally failing witness methods, seven passing controls, no errors. Total test time: about eight minutes. Manifest SHA remains `21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c`.

Next: lead dispositions and a ruling on the U3 replacement comparison budget. Downstream consumption of the contradictory pool was not demonstrated. Native MLX and Python 3.11 remain untested.