# hp-02 successor audit round 3 repairs · 2026-11-19

The independent round-three execution blocked `b298c24b8`. The report and probes are in the lead's scratch seat at `pl-hp02-successor/audit-3/FINAL-MESSAGE.md`. The lead's R1–R3 rules govern these repairs.

| Rule | Implementation and verification |
| --- | --- |
| R1 · launch latency and expiries | Run requires an open bound queue and at least 600 seconds until each expiry it relies on. This includes admission validity, finite item and issue expiries, and a watcher if supplied as Run evidence. The declared startup bound must land strictly before each expiry. Recheck after durable claim I/O and release an unused claim when the check refuses. The regression sweeps 175 combinations across five expiry sources, seven runway values and startup latencies of 0, 1, 599, 600 and 601 seconds. The pinned planner supplies the simulated launcher clock in admitted cases. |
| R2 · sample after Start publication | Start links the complete digest-verifiable receipt into custody after syncing its bytes, then seals a clock sampled after that durable publication to the exact receipt bytes. Run verifies the receipt and seal before reading the observation file. The read is after publication and every current observation has a sample strictly after publication and at or before the read. The 256 configurations on a one-second grid cover every ordering and tie of Start sample, Start publication, Run sample and Run read. Separate regressions remove or corrupt the receipt proof and remove or backdate each current observation's sample. |
| R3 · rank-one completion and MED | Rank one uses the RS464 and RL-190 §1.4 pool `f2-stab-01..14` on `2d347f721`. A spent-for-date entry cites a matching completed leg and the correct day's completion record. A genuinely ineligible pool uses a dated complete adjudication. The regression removes each fact from the frozen case's adapter input and each mandatory completion field, then checks all 16 kit IDs and invalid date, leg, pin and status controls in each phase. |

Earlier Start receipts require a fresh Start with this gate. A Run evidence envelope supplies `observed_epoch_s` for its earliest current observation and `sampled_at` for each of its required evidence objects. An alarm-only watcher adds no arm dependency.

The six frozen files were checked byte-for-byte. The historical acceptance, occupancy, runner and legacy fixtures replay their original outcomes, including the old last-second planning permission. The new executing regressions verify that Run refuses that dispatch. Verification used synthetic fixtures and administrative source records. Hosted CI supplies the full suite because local discovery encounters protected optional archive paths.

No outstanding MED or LOW findings and no NEEDS_SPEC issues. Next gate is independent delta execution on the repair commit.
