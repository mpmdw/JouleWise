# hp-02 successor audit round 1 repairs · 2026-11-19

The independent round-one execution blocked `6b154a7e1`. The report is in the lead's scratch seat at `pl-hp02-successor/audit-1/FINAL-MESSAGE.md`. This pass repairs all four verified high findings and the verified medium finding. The probe also exercised a boolean AC-mode value, which now refuses in typed observations, host readback and the receipt Check.

| Finding | Disposition and regression |
| --- | --- |
| Run used a sample taken before successful Start | The Start receipt records the passing verdict time and host. Run checks the bound issue, roster, output and host and requires a strictly later observation. The audit's 13:14:00 Start sample, 13:15:00 verdict and 13:14:30 Run sample now refuse, as does a Run sample exactly at the verdict time. A fresh Run reporting that the look ran still refuses. |
| Queue expiry during dispatch | Hashes, custody paths, the queue interval, the observation validity interval and the remaining deadline are checked at handoff after the durable claim. Known pre-dispatch refusals release the unused claim. The last-second Run with a one-second claim-write delay returns `NEED_FRESH_QUEUE` with zero launcher calls. A delay past the observation validity boundary also refuses, and fresh evidence can proceed afterward. |
| Contradictory host, close and recovery records | The Start and Run host identities agree. A named HP Check is bound to that host and the latest close chronology and receipt. A recovery record is always evaluated, including alongside a proved restore flag. Foreign-host records and an inverted predecessor close refuse. Failed recovery with a stale positive restore flag halts and pages. |
| Missing hp-01 dates | The census requires a nonempty list of canonical dates containing the known November 15 date. Empty text, an empty list and a nonempty list omitting November 15 fail at both gates. |
| Missing ladder candidate identity | Every adjudicated rung names a nonempty candidate ID at either status. Both gates refuse the missing unavailable f2-inst-03 ID. The complete rank controls still pass. |

The added regression cases run in `tests.test_hp02_successor_items` at the actual item entry point with the clock, readbacks and launcher simulated. The frozen fixtures and pinned runner remain byte-identical. Verification replayed 60 original vectors, 54 timing decisions, 1,764 clock cases, 43 runner traces, 11 dated pairs and 360 legacy decisions. The occupancy harness recorded zero native-command attempts. Item syntax and state generation passed.

The full suite runs in hosted CI because this local environment denies optional archive metadata needed during discovery. The draft PR body records exact-head CI and the results qualified for the gate ledger.

No round-one medium or low follow-ups and no NEEDS_SPEC issues. The next gate is independent delta execution on the repair commit before lead acceptance or live issue.
