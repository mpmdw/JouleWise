# f2-inst-03 executing delta · 2026-11-19 · Astra, Air

**PASS for the engineering delta.** Public main items 457–464 contain no executing PASS for this kit. Items 463 and 464 cover clock bands and stability priority. Item 456 covers only `f2-inst-02`. [Latest public items](https://github.com/mpmdw/JouleWise/blob/d09e78d2182bb5e7a0f934679d264dd8f0cf1508/RUN_STATE.md#L1055-L1200) · [Item 456 execution precedent](https://github.com/mpmdw/JouleWise/blob/bdbc3636d99f8a1d630a772034d390a375980585/RUN_STATE.md#L1078-L1085)

| Input | Public commit | SHA-256 of kit bytes |
|---|---|---|
| Source `docs/process/cadence/kits/f2-inst-01.v1.1.json` | `1f683fc634ed6b8722a3976af400920ee1f7dd7d` | `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b` |
| Candidate `E/item-drafts-f2-0203/f2-inst-03/f2-inst-03.v1.1.json` | `9a5a9be30027d90a5ec69f1820b3f8a081d664de` | `286842217313e13ac5f8f25917b3325e3e512cd621b90b78b6201d331e9dcf25` |

`E=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign`. Runner pin `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Audit authority is RL-174 B 17580–17583, RL-175 D.3 17858 and RL-179 F-4 18718–18742 with register rows 1–2 at 18908–18909. The finite roster runs once in order and remains outside campaign counts. Issue-time priority and dated-block protection belong to the magistrate. [Rulings](https://github.com/mpmdw/JouleWise/blob/9a5a9be30027d90a5ec69f1820b3f8a081d664de/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17580-L17583)

**Kit.** All 37 claimed pointer/before/after triples matched, with zero additional differences. Four edits set the campaign ID, ruling, master seed `2026111441` and default decode 256. Regeneration accounts for 12 seeds, 12 decode caps and nine prefill changes. The pinned generator reproduced 12/12 complete leg objects and the seed law. Every piece contains 256, 2,000 and 19,458 once. Each size occupies all three positions across four pieces. The frozen block and inherited prose are byte-identical to source. All 38 frozen paths verified under both batch arguments.

| Queue under `E/fillers-w2` | SHA-256 | Ordered coverage by sequence |
|---|---|---|
| `queues-1leg/f2-inst-03.json` | `8ce447dc0d1ba01b816133e3d9c6d7815bf2a75eb441eef384cfccd4bdadb20e` | 12 singles, seq 1–12 |
| `queues-2leg/f2-inst-03-a.json` | `2d530910e89f9634241a30e0ec0dff9ac90eb06bbef55fa48b3925f68a6526bd` | Six adjacent pairs, seq 1, 3, 5, 7, 9, 11 |
| `queues-2leg/f2-inst-03-b.json` | `a70121e5e241823a674c6c9bcf92cd32d95967e81d702c484e52af55ba16e016` | Five adjacent pairs, seq 2, 4, 6, 8, 10 |

**Queues and plans.** All 3/3 files match the published digests and pass `validate-queue`. Each span binds the exact candidate path and digest. Singles, A alone, and single L001 + B + single L012 each yield exactly L001–L012 once in order. All 23 queue entries passed `plan` at one synthetic t0. L001 expected/worst was 4,507/5,850 s, L001,L002 was 5,846/8,550 s, and L002,L003 was 6,020/8,550 s.

**Synthetic execution.** The clean L001,L002 mock returned 0, with 2/2 admitted, own G0 released, 256/256 decode on each leg, zero redos, faults or stops, Automatic restore rc 0 and 3/3 fake feeds stopped cleanly. Its desk outcome was `MEASURED_OK`. The separate public L002 leg-runtime fixture reached the 256 cap after exactly 600 synthetic quiet seconds. Both injected controls passed. Contamination and G0 timeout each excluded L001, preserved L002 and used zero retries. Three expected refusals returned 1. Appending one newline to the kit changed its digest to `e907c1d0aa8db773bda850342e2ab06767dbfb18b5c6dd9fd80cf63ad2ad9079` and the original A queue refused the mismatch. Both the queue validator and planner refused L013. The pin accepted every valid 256-dose case.

**Execution commands.** From the seat root, these replay the public CLI wrapper and q600 fixture from `E/item-drafts-f2-0203/tests/verify_build.py` lines 15–25 and 82–100. Each run creates fresh seat-local synthetic output. The first log contains every expanded pinned CLI command. It uses `gen-legs --law sha256-cells-v1`, `validate-kit --repo` with both `02:00-02:35` and `13:14-13:15`, all three `validate-queue --kits-root` calls, and `plan --t0 1795123200` plus `mock --t0-local 2026-11-19T13:20:00` under `02:00-02:35`.

```sh
cd /Volumes/JW-EXT/scratch/astra-f2-inst-03-20261119
python3.13 -B scratch/review.py > scratch/replay.log
python3.13 -B scratch/clean.py "$(awk '/^MOCK / {print $NF}' scratch/replay.log)/pair"
python3.13 -B scratch/dose.py
python3.13 -B scratch/controls.py
```

**Magistrate follow-up.** Item 406 defines the original `f2-inst-01` piece-1 hand-read. Item 411 records the operational Check and explicitly leaves the hand-read open. Item 428 places it before the look. No subsequent public item through 464 records that hand-read PASS. The magistrate should locate or record its disposition. Issue, actual close and native gates stay with their authorized roles. [Item 411](https://github.com/mpmdw/JouleWise/blob/d09e78d2182bb5e7a0f934679d264dd8f0cf1508/RUN_STATE.md#L2171) · [Item 428](https://github.com/mpmdw/JouleWise/blob/d09e78d2182bb5e7a0f934679d264dd8f0cf1508/RUN_STATE.md#L1875)

Public main head `d09e78d2182bb5e7a0f934679d264dd8f0cf1508`. The supplied worktree's Git metadata was inaccessible, so verification used an isolated public-source seat. The runner checkout was clean before and after. Source changes 0. CI N/A for this local review. NEEDS_SPEC none.
