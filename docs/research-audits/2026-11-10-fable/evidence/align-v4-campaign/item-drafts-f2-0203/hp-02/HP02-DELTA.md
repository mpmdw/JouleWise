# hp-02 independent executing delta — 19 November 2026, Air

**ADMIT the kit delta on the reviewed bytes.** The public hp-02 file differs from the public as-run hp-01 source in exactly 15 JSON leaves and exactly 15 physical lines. All 37 frozen path digests match their blobs at the admitted runner commit. The native validator, deterministic leg generator, three rosters, planner and synthetic restore controls passed. **The three unissued items are on HOLD.** Their shell decisions and the HP queue need a successor before Friday use. Current live admission remains with Opus and the issuing desk. [Item-gate specification](ITEM-GATES-SPEC.md)

## Inputs and prior work

| Object | Immutable identity |
|---|---|
| Audit head and decision log | `9a5a9be30027d90a5ec69f1820b3f8a081d664de` |
| Public main used for administrative facts | `6640a66719a2ff1f8cc38dbce3e8231f419e79d8` |
| Commit introducing the hp-02 directory | `a32eb54ce9ea8a19e348bad6890a15336b8db2e5` |
| hp-01 source at `docs/process/cadence/kits/cl-hp-01.json` | `bbd34dc876001786c3603d9c4583391639284253` · SHA-256 `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965` |
| hp-02 at `item-drafts-f2-0203/hp-02/cl-hp-02.json` | SHA-256 `7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66` |
| HP runner and 37-path frozen map, both kits | `dd206025abb30fd5c07515cd4b34b3e653174810` |
| HP queue `cq-hp-02-a` at the audit head | SHA-256 `6489297e89e0cf02fe8d0f4050fe6f0492e175724d4902173fd2d7e7b5d54286` |

The public audit tree and its HP path history contained only the builder commit for this directory. The public refs, main, the November 19 dispatcher seat index and its earlier LANES entries yielded the original Sol builder, Mythos’s hp-01 delta, separate F2 seats, and this HP assignment. I found no independent report or corrected item covering this hp-02 hash. I reused the builder’s expected deltas, shell test and public mock, then computed fresh results. Item 447 and PR #858 at `c4b4f42651d93023236db50f0e23d19e034b851c` list F2 queues through December 8. Neither the three HP entries nor their queue hash occurs in that renewal. [HP source and builder checklist](https://github.com/mpmdw/JouleWise/blob/9a5a9be30027d90a5ec69f1820b3f8a081d664de/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/DELTA-CHECK.md#L3-L7) · [F2 renewal](https://github.com/mpmdw/JouleWise/blob/6640a66719a2ff1f8cc38dbce3e8231f419e79d8/RUN_STATE.md#L1420-L1433)

## Exact byte delta

The replay walked both documents, compared their complete sets of leaf paths and matched the following triples to DELTA-CHECK lines 108–122. As a separate check it required every physical line to match, allowing only the following individual value-token substitutions. The title, explanatory text, ordering, encoding, indentation and frozen block therefore survive byte for byte. Native gen-legs regenerated the complete ordered leg objects and seed law from campaign ID, master seed, 12 legs, q0, 19,458 prefill and 4,096 decode. [Source table](https://github.com/mpmdw/JouleWise/blob/9a5a9be30027d90a5ec69f1820b3f8a081d664de/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/DELTA-CHECK.md#L102-L129)

| JSON pointer | hp-01 | hp-02 |
|---|---|---|
| /campaign_id | cl-hp-01 | cl-hp-02 |
| /ruling/id | RL-149 §2 | RL-174 |
| /seed_law/master_seed | 2026111404 | 2026111601 |
| /legs/0/seed | 4048693807 | 3647512302 |
| /legs/1/seed | 1251089132 | 1603347076 |
| /legs/2/seed | 3543179003 | 2027507057 |
| /legs/3/seed | 954626506 | 1851779591 |
| /legs/4/seed | 983646378 | 3584571682 |
| /legs/5/seed | 2048410933 | 3643703426 |
| /legs/6/seed | 1350544700 | 2878738608 |
| /legs/7/seed | 1180804720 | 825084403 |
| /legs/8/seed | 3701535075 | 3292754346 |
| /legs/9/seed | 2827066148 | 1256642238 |
| /legs/10/seed | 2178814401 | 1933637934 |
| /legs/11/seed | 1042807770 | 397751866 |

## Pinned plans and synthetic controls

| Span and roster, attempt 1 | Expected | Work worst | Pinned minimum fence | Draft fence |
|---|---:|---:|---:|---:|
| s01 · L001–L003 | 6,903 s · 1:55:03 | 16,650 s · 4:37:30 | 17,210 s | 18,110 s |
| s02 · L004–L007 | 8,154 s · 2:15:54 | 19,350 s · 5:22:30 | 19,910 s | 20,810 s |
| s03 · L008–L012 | 9,405 s · 2:36:45 | 22,050 s · 6:07:30 | 22,610 s | 23,510 s |

Expected total is 6:47:42. Summed work worst is 16:07:30. These are model durations for twelve legs. Confirmed schedulable hours from this review are **zero**. Each span has a new Automatic soak. Cold positions are L001, L004 and L008. The four triplets printed at DELTA-CHECK line 124 group the constant prompt-size list. Actual span boundaries come from queue-a.json lines 8–60, generator lines 87–93, and the pinned plans. Expected seconds equal 1,950 + 1,200 + 1,251 × roster length. Work worst equals 1,950 + 1,200 + 2,700 × (roster length + 2 redo attempts). The pin adds 560 s to the work deadline. The draft separately allows 1,460 s above work worst at launch. A planner must reserve the applicable fence and close before another arm. [Queue and rosters](https://github.com/mpmdw/JouleWise/blob/9a5a9be30027d90a5ec69f1820b3f8a081d664de/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02/queue-a.json#L8-L60) · [Pinned plan](https://github.com/mpmdw/JouleWise/blob/dd206025abb30fd5c07515cd4b34b3e653174810/joulewise/cadence/legs.py#L244-L279)

| Executed check | Observed |
|---|---|
| validate-kit with frozen repository verification for each of `02:00-02:35` and `13:14-13:15`. Independent byte hashes over all 37 materialized paths. validate-queue with the actual kit root. | Both validators returned the bound kit SHA. All frozen hashes matched. Queue contained exactly the three ordered attempt-1 rosters, no repeats or rerun links. |
| Three plans at both ends of each legacy admitted band, Friday 13:20 with default and Friday 23:30 with alternate, all invented t0s | 24 positive cases. All rosters, budget values and arguments matched. All three 23:30 default plans refused for blackout as expected. |
| Unchanged pinned mock at 23:30 Friday with alternate on s01/s02/s03 | 3/3 clean mocks returned rc 0, with the expected rosters, all feeds stopped, Automatic read back, marker absent and restore proven. |
| s01 contamination and G0 timeout separately, as in the public verification code | rc 0 for each, clean restore and no named stop. A clean close alone says nothing about inclusion of an individual leg. |
| s01 persistent synthetic close-restore failure | rc 2, three internal attempts, mode 2, marker present, proof false, RESTORE_UNPROVEN. Correct negative control. |
| Pure pinned queue decision, empty invented span history with clocks expiry−1, expiry, expiry+1 | Returned `arm / arm / halt`. Its comparator is strict `>`. The item and stager require `now < expiry`, so use the exclusive boundary at 1795420800. This probe confers no arm authority. |

Replay from the seat using `python3.13 -B fixtures/review_kit.py`. The script calls only the public validation, generation, plan, mock and isolated queue decision paths. It uses a source-only copy at the verified Git object and writes temporary mock outputs under the seat. The mock selects FakeClock, FakeHost, FakeFeed and FakeLegRuntime. Separate blob verification covers what the mock itself skips. All saved results are synthetic. [Replay](fixtures/review_kit.py) · [Results](tmp/runtime/kit.txt) · [Public mock wiring](https://github.com/mpmdw/JouleWise/blob/dd206025abb30fd5c07515cd4b34b3e653174810/scripts/cadence_legs_runner.py#L1013-L1039)

RL-175 D.3 resolves the builder’s first two HP questions. Keep the inherited literals in the kit and annotate them in the item. hp-01’s Class A smoke serves. HP contributes to neither the 132 cap, day count, line 9 nor a fit. HP has no replacement reserve, and the subsequent HP description look must name both blocks and actual receipts before any HP read. These are settled constraints. The historical line-2 disposition and prospective paper/manifest questions are recorded in the item spec. [RL-175 D.3](https://github.com/mpmdw/JouleWise/blob/9a5a9be30027d90a5ec69f1820b3f8a081d664de/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17854-L17862)

The incoming shared worktree’s .git pointer could not be resolved. There is no PR for this seat. I verified the public refs over HTTPS and kept the exact-pin source and scratch in the seat. This review creates no commit and triggers no CI. Historical CI run 43673985768 completed with conclusion `failure` on `2a8deb7b9c99c444a00bff639e7e8478935d7c5f`. Main item 338 line 8153 records its 12 test failures as base + 0, the passing runs at PR #777’s head, and frozen-path comparisons. That is the historical hp-01 record. [CI run](https://github.com/mpmdw/JouleWise/actions/runs/43673985768) · [Main item 338](https://github.com/mpmdw/JouleWise/blob/6640a66719a2ff1f8cc38dbce3e8231f419e79d8/RUN_STATE.md#L8151-L8159)

At the closing public recheck the audit head was `49911cb3526043b312b1f540e487ee3fe61d9fce` and main was `489c8465089981ddcd1d861afca9d5c8b83ff72c`. Both advanced from the reviewed heads. The new audit review is for f2-inst-03 only; the hp-02 directory history and bytes are identical. Items 462–465 resume the Air, refine the F2 clock/priority handoff and accept the -03 delta. The public main filler registry also names the reviewed HP kit SHA. Neither development proves a negative look status or fills an HP item. [Main item 465](https://github.com/mpmdw/JouleWise/blob/489c8465089981ddcd1d861afca9d5c8b83ff72c/RUN_STATE.md#L1055-L1078)
