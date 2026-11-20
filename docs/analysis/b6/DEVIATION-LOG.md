# Block 6 (replication) reporting deviation log

Block 6's registered deviations are dated entries in its registration's §17
(`docs/registrations/block6_replication_DRAFT.md`), which is not edited after the release
(2026-11-13 18:54:56 PST, PR #769, merge `66469ccf4`). This file records the reporting deviations decided after
the release, while Paper 1's Block 6 fill was written (PR #772). Its first three lines are the ones RL-147 §11
item 4 orders. Each was decided after Block 5 and Block 6 outcomes were known.

| Id | Date | Kind | Deviation | Authority |
|---|---|---|---|---|
| B6-DL-1 | 2026-11-13 | Reporting | Registration §12.3 item 4 and runbook step 15 expect the largest observed difference per comparator class to print beside its bar. The pinned program computed it (`compare()`, `max_observed_difference`) and did not retain it: `recompute_block` stores only the public comparator. Paper 1 prints the counts and the bound (every compared row passed, so each class's largest difference is no larger than its bar). The run is not repeated (RL-134 §16 item 1). Follow-up on `main`, not applied to the pinned run (RL-134 §16 item 3): the next revision of the program keeps the per-class `max_observed_difference`. Decided after Block 5 and Block 6 outcomes were known. | RL-147 §1 |
| B6-DL-2 | 2026-11-13 | Reporting (release record) | The Block 5 release-event record, owed in the seal record's "Release event" section at the event (2026-11-08 11:17 PST, `RUN_STATE.md` item 231), was written late, on `main`, on 13 November 2026 (PR #773, merge `fd43dcdf4`, 19:56 PST), five days after the event. The event and the released bytes are unchanged. Paper 1's `P1-RELEASE` is filled from that section and the Block 6 release record; the BYTES clause is split off as the pending marker `P1-RELEASE-BYTES`. Decided after Block 5 and Block 6 outcomes were known. | RL-147 §4 |
| B6-DL-3 | 2026-11-13 | Reporting | The plain-mean scaling factor of the scaled drift allowance, registered (RL-25 8a-i; registration §17-R9) to print beside the registered factor where a cell lost unequal numbers of units, is not in the released output and is not printed; such cells exist (for example r3-alpha decode, 10 repeats and 9 quads). Paper 1's scaled-allowance line says so. Follow-up with B6-DL-1. Decided after Block 5 and Block 6 outcomes were known. | RL-147 §6 |
