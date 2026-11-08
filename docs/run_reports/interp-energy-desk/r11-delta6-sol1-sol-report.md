**HOLD.**

- Contention-only exclusions still fail the full desk and can block C1 after W1.
- The balance check drops disclosed contention events, reporting 0 instead of 2 in the witness.
- R24 drift prose also needs correction.

Manifest SHA remains `21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c`.

Added only the [report](/Users/edr/code/CapstoneProject/jw-wt/sol-r11-delta6-sol1/docs/align/v4/R11-DELTA6-sol1.md) and [witnesses](/Users/edr/code/CapstoneProject/jw-wt/sol-r11-delta6-sol1/tests/align/test_r11_delta6_sol1.py). The report contains exact commands and failure scenarios.

Verification: 76 focused tests—73 passed, 3 expected failures. Undecorated replay confirmed all three intended failures. Total test time: under eight minutes. Synthetic only; no native validation or open ruling questions.

Committed locally as `7010a8cf5` on `align/2026-11-08-r11-delta6-sol1`; not pushed. Next: lead fixes both findings and reruns the witnesses.