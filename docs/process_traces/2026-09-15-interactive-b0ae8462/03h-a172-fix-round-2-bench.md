# 03h — A172 fix round 2 at the bench (magistrate b0ae8462, 2026-09-15 21:55 PDT)

Delta re-audit 03f found two should-fixes: the R1 (clearance) and R3 (byte-for-byte abort copy) corrections were
prose-only and could be reverted with every test green. Bench cure under rule 9's threshold (two assertions, no
contract): `test_policy_prose_pins_unreadable_thread_is_not_a_stop` (render_policy() and the retry_allowed docstring must
carry the R1 sentences and must NOT carry the old "unreadable veto channel is not clear") and
`test_runbook_pins_byte_for_byte_abort_copy` (the runbook must carry the exact copy instruction). Commit `2daf2b0b`.
Executed: module 27 tests OK; in a `cp -R` copy, reverting the runbook sentence to "the newest abort time" →
`FAILED (failures=1)` (RED), copy discarded.
