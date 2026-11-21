# hp-02 successor audit round 2 repairs · 2026-11-19

The independent round-two execution blocked `5d4ec57e0`. The report is in the lead's scratch seat at `pl-hp02-successor/audit-2/FINAL-MESSAGE.md`. This repair addresses all four verified high findings and the verified medium finding.

| Finding | Disposition and regression |
| --- | --- |
| Restore refusal disappears when an older close returns | The shared admission record retains the most recent close and the exact held close across phases, issues and queues. An older close alone refuses. A failed recovery on close 18 halts each retry, including a return to close 17, a purported clean close 19 and a fresh issue. An unresolved restore requires a successful pinned recovery and stop clearance for the same close. The regressions exercise both continued hold and the allowed recovery path. |
| Confirmed look execution disappears on retry | The gate records scoped positive execution before deciding whether HP can arm. A subsequent negative look snapshot cannot admit HP, including after ceding to a higher rank or publishing another issue. |
| Two receipts share one Check identity | The latest and predecessor Check cannot give the same ID different receipt hashes or end times. The gate also rejects conflicts with identities previously recorded in custody. Start and Run both refuse the audited pair. |
| Later legs are already spent at s01 | Every leg is classified and the whole history must agree with the fixed roster order. An already started or unresolved later roster blocks the earlier span. Observed spent legs survive retries, and an actual later launch claim independently blocks the earlier span. |
| Copied finite instrument adjudication | Each rank-2 row names its exact kit and cites a distinct adjudication. Reusing the -02 identity or evidence in the -03 row fails. |

The admission record sits alongside the shared arm lock and launch claims and is committed to disk before dispatch. It contains operational identities and status, and a new issue or queue reuses the same record. Earlier Start receipts require a fresh Start. A recorded host halt requires lead disposition and cannot be cleared by submitting another arm observation.

The local acceptance suite passed all new executing regressions and the six frozen fixture files were unchanged. The suite replayed all 60 vectors, 54 timing decisions, 1,764 clock cases, 43 runner traces, 11 dated pairs and 360 held-item decisions. Zero native-command attempts in the clocked suite. The hosted suite supplies full CI coverage, since the local environment denies optional archive metadata on discovery.

No medium or low follow-ups and no NEEDS_SPEC issues. The next gate is independent delta execution on the repair commit before acceptance or live issue.
