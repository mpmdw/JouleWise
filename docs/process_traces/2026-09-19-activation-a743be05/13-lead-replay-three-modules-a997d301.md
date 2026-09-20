# Record 13 — lead replay outside the sandbox at `a997d301`: composed arm-sequence test + the three modules the seat's sandbox could not clear (22:00–22:12 PDT 2026-09-19)

Command (unpiped, `wt-fix-renderonly`, untouched during the run):
```
PATH=.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=$PWD python -B -m unittest tests.test_evidence_arm_sequence tests.test_night_agent_install tests.test_axi_controller_events tests.test_run_night
```
Tail: `Ran 309 tests in 741.254s` / `FAILED (failures=1)` (log: `13-lead-replay-three-modules-a997d301.log.gz`).

- The sandbox failures were environmental as the seat said: `test_cleanup_refusal_reports_the_failure_it_interrupted` (sysmond/`/bin/ps`), the two `test_axi_controller_events` campaign tests (`/bin/ps` PermissionError) and `test_blocked_journal_never_blocks_deadline_or_grants_go` (8 s watchdog) all PASS outside the sandbox.
- The composed test `tests/test_evidence_arm_sequence.py` PASSES (real installer render-only twice, real bindings, real `probe_night` supervisor through the fixture venv, receipt admitted, `validate_install`, plist assertions).
- ONE real failure, pre-existing on main since `0959e613`: `tests.test_run_night.CourierDeliveryBoundaryTests.test_fallback_recipient_constant_matches_the_courier_template` parses the recipient from `NIGHT_COURIER_PROMPT.md` with `r'Email Ed at ([^\s]+)\.'`; Ed's prompt edit ends the address with a comma, so the greedy match backtracks to the last period and yields `claude2.glaring610@passmail` (on main the constant is still the old alias, so main is red on this test regardless). Bench closure `7ea54846` (test-only): the regex matches the address itself. `CourierDeliveryBoundaryTests` alone at `7ea54846`: 18 tests OK.

Final head for the refuters' delta: `7ea54846` = `a997d301` + that one test-regex commit (production code identical).
