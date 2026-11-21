# hp-02 successor round-six repairs · 2026-11-20

Audit 5 blocked published head 23cd19cb7 when a later observation could erase a confirmed look, a reservation, a same-date hp-01 entry or an unproven stop. It also identified an omitted 600-second runway boundary. The lead supplied L1 and the G1 and G2 revisions for round six. The probes and traces are indexed in the lead's scratch report at pl-hp02-successor/audit-5/FINAL-MESSAGE.md.

**L1.** An append-only per-issue ledger keeps the blocking fact, source digest, observation time and hold ID. A stable issue record ID carries the ledger from proposal through Issue, Start and Run. A final Run refusal records new facts before releasing its unused claim. An incomplete initial ledger read retains a custody marker, and a failed final write retains the claim. A changed immutable receipt projection latches under the original digest. A later clean observation cannot clear either kind of hold.

Clearance requires a typed disposition that names the exact issue, hold and source. The gate verifies the owner and chronology of the cited RUN_STATE item, the exact disposition payload and the authority commit's ancestry on published main. It persists accepted clearances as additional events. Current eligibility still applies.

**G1 and G2.** The dynamic guard now includes each applicable expiry minus 600 seconds and the latest startup anchor. The item's successful final path stays write-free up to launcher invocation. The frozen launcher then writes its runner specification, plist and fence before bootstrap. A state change after the final read remains the residual risk under the quiet-MBP and magistrate assumptions.

The local CI-discovered tests cover 40 phase and blocking-fact combinations, forged or mismatched and published clearances, receipt tamper and partial clearance, custody write failures, 80,442 guard offsets, 32 launcher-boundary cases and 24 read-last cases. The original R1–R3 properties, 60 contract decisions, 54 occupancy decisions, 1,764 clock cases, 43 runner traces and legacy replay also passed. All six frozen files match byte for byte. The verification uses synthetic fixtures with zero native-command attempts. No measured energy data was accessed. Hosted CI supplies the full suite per CANONICAL.

The first hosted run caught direct Git initialization in the synthetic authority test. The test now uses the repository's shared fixture initializer, and the targeted fixture-maintenance check passed.

Independent delta execution on the pushed repair remains the next gate.
