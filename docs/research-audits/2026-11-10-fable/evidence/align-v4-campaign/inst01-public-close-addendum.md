# lm-inst-01 public close-status addendum for Opus

This Tier 0 addendum extends the instrument packet's item-475 cutoff. The 36 planned keys are the twelve positions of each of `f2-inst-01`, `f2-inst-02` and `f2-inst-03`. The last public Check is item 481 for `f2-inst-03` L009–L010. Item 481 records issue of the final pair, **L011–L012**, whose Check and dispositions are **pending**. [Packet cutoff, item 475][475] · [Last Check][481-check] · [Final issue][481-issue]

At `2026-11-20T12:50:48Z`, public main was `b15fb4b090e3ff2c131c27bf4605dea0e861b6dc` with item 481 as the latest public instrument update. [Item 481][481]

| Public cutoff | Check-backed | Issued, Check pending | Unissued | Total |
|---|---:|---:|---:|---:|
| 480 | 32 | 2 | 2 | 36 |
| 481 | 34 | 2 | 0 | 36 |

All 36 keys are unique. Check-backed means the cited public Check reports that the position ran. Both loaded positions are Check-backed. “Completed” and “Runner admitted” record what the public Check states. The final stage-1 qualified count is pending. The span labels reproduce the public groupings. Opus still needs the native receipt-bound span IDs and indices, actual attempts, pins, kit digests, references and row-7 evidence for the final review. [Item 480][480] · [Item 481][481] · [RL-190 §§3.1–3.3][roster] · [RL-190 §3.5][review]

The positive wall-time deltas below are observed planner overruns. A dash marks the absence of a listed overrun. RL-190 §3.2 keeps `over_time_budget` as a separate flag and applies ordinary stage-1 predicates below the overtime stop. RL-192b keeps the two loaded rows in the accounting as `not_qualified:loaded`, out of `n_legs`, with zero prints. Both have no redo. [RL-190 §§3.1–3.3][roster] · [RL-190 §4(b)][no-redo] · [RL-192b][loaded]

| Kit | Position | Public span | State at 480 | State at 481 | Public disposition | Planner overrun | Public source |
|---|---|---|---|---|---|---|---|
| f2-inst-01 | L001 | Piece 1, L001–L003 | Check-backed | Check-backed | Completed | +15 s from Check wall and budget | [411][411] |
| f2-inst-01 | L002 | Piece 1, L001–L003 | Check-backed | Check-backed | Completed | — | [411][411] |
| f2-inst-01 | L003 | Piece 1, L001–L003 | Check-backed | Check-backed | Completed | — | [411][411] |
| f2-inst-01 | L004 | L004–L005 | Check-backed | Check-backed | Completed | — | [450][450] |
| f2-inst-01 | L005 | L004–L005 | Check-backed | Check-backed | Completed | — | [450][450] |
| f2-inst-01 | L006 | L006 | Check-backed | Check-backed | Runner admitted | +22 s as reported | [451][451] |
| f2-inst-01 | L007 | L007–L008 | Check-backed | Check-backed | Runner admitted | — | [454][454] |
| f2-inst-01 | L008 | L007–L008 | Check-backed | Check-backed | Runner admitted | — | [454][454] |
| f2-inst-01 | L009 | L009–L010 | Check-backed | Check-backed | Runner admitted | +39.6 s | [455][455] |
| f2-inst-01 | L010 | L009–L010 | Check-backed | Check-backed | Runner admitted | — | [455][455] |
| f2-inst-01 | L011 | L011–L012 | Check-backed | Check-backed | Runner admitted | +17.0 s | [456][456] |
| f2-inst-01 | L012 | L011–L012 | Check-backed | Check-backed | Runner admitted | — | [456][456] |
| f2-inst-02 | L001 | L001–L002 | Check-backed | Check-backed | Runner admitted | — | [457][457] |
| f2-inst-02 | L002 | L001–L002 | Check-backed | Check-backed | Runner admitted | — | [457][457] |
| f2-inst-02 | L003 | L003–L004 | Check-backed | Check-backed | Runner admitted | +15.7 s | [458][458] |
| f2-inst-02 | L004 | L003–L004 | Check-backed | Check-backed | Runner admitted | — | [458][458] |
| f2-inst-02 | L005 | L005–L006 | Check-backed | Check-backed | `not_qualified:loaded` (`cpu_load`), no redo | +7.1 s | [467][467], [471][471], [RL-190 §4(b)][no-redo] |
| f2-inst-02 | L006 | L005–L006 | Check-backed | Check-backed | Runner admitted | — | [467][467] |
| f2-inst-02 | L007 | L007–L008 | Check-backed | Check-backed | Runner admitted | +10.5 s | [469][469] |
| f2-inst-02 | L008 | L007–L008 | Check-backed | Check-backed | Runner admitted | — | [469][469] |
| f2-inst-02 | L009 | L009–L010 | Check-backed | Check-backed | Runner admitted | — | [470][470] |
| f2-inst-02 | L010 | L009–L010 | Check-backed | Check-backed | Runner admitted | +17.6 s | [470][470] |
| f2-inst-02 | L011 | L011–L012 | Check-backed | Check-backed | Runner admitted | — | [474][474] |
| f2-inst-02 | L012 | L011–L012 | Check-backed | Check-backed | Runner admitted | — | [474][474] |
| f2-inst-03 | L001 | L001–L002 | Check-backed | Check-backed | Runner admitted | — | [475][475] |
| f2-inst-03 | L002 | L001–L002 | Check-backed | Check-backed | Runner admitted | — | [475][475] |
| f2-inst-03 | L003 | L003–L004 | Check-backed | Check-backed | Runner admitted | +15.5 s | [476][476] |
| f2-inst-03 | L004 | L003–L004 | Check-backed | Check-backed | Runner admitted | — | [476][476] |
| f2-inst-03 | L005 | L005–L006 | Check-backed | Check-backed | Runner admitted | +19.5 s | [477][477] |
| f2-inst-03 | L006 | L005–L006 | Check-backed | Check-backed | Runner admitted | — | [477][477] |
| f2-inst-03 | L007 | L007–L008 | Check-backed | Check-backed | `not_qualified:loaded` (`cpu_load`), no redo | — | [479][479], [480][480], [RL-192b][loaded] |
| f2-inst-03 | L008 | L007–L008 | Check-backed | Check-backed | Runner admitted | +42.6 s | [479][479] |
| f2-inst-03 | L009 | L009–L010 | Issued, Check pending | Check-backed | Runner admitted | — | [479 issue][479-issue], [481 Check][481-check] |
| f2-inst-03 | L010 | L009–L010 | Issued, Check pending | Check-backed | Runner admitted | +20.8 s | [479 issue][479-issue], [481 Check][481-check] |
| f2-inst-03 | L011 | L011–L012 | Unissued | Issued, Check pending | Pending | Pending | [480 cutoff][480], [481 issue][481-issue] |
| f2-inst-03 | L012 | L011–L012 | Unissued | Issued, Check pending | Pending | Pending | [480 cutoff][480], [481 issue][481-issue] |

## Proposed public piece-1 deviation paragraph

Opus should place the paragraph below only in `docs/process/cadence/looks/lm-inst-01-DEVIATIONS.md`, in the same commit as the final manifest. The lead's 22:50 placement decision, confirmed in RL-191 §4(b), keeps the v2 schema closed and calls for the cold-pass ruling to bind the deviation file's SHA-256 alongside the manifest's. [Item 473][473] · [RL-190 §3.3][piece] · [RL-191 §4(b)][placement]

> 2026-11-19 — The lead signed the `f2-inst-01` piece-1 hand-read in RUN_STATE item 473 against item 411's Check, under RL-190 §3.3 and RL-169a §5. The signature discharged the operational hand-read gate after `f2-inst-01` queue b and `f2-inst-02` had run and the kit issue for `f2-inst-03` was on record (item 465). The required order of the operational gate was missed. Blinding was preserved. Row 7's evidence bindings remain separately required. [Item 411](https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L2401) · [Item 465](https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1288-L1298) · [Item 473](https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1250-L1257) · [RL-190 §3.3](https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22441-L22448) · [RL-191 §4(b)](https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22863-L22868)

## Next public fill

The next observable is a public Check or a typed disposition covering `f2-inst-03` L011 and L012. Opus can then extend the public accounting from that record. RL-190 §3.1 requires all 36 positions to reach a terminal disposition for stage 1. Row 7 and the remaining cold-pass evidence retain their independent gates. [Item 481][481] · [RL-190 §§3.1–3.3][roster] · [RL-190 §3.5][review]

[411]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L2401-L2412
[450]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1615-L1632
[451]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1591-L1608
[454]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1511-L1528
[455]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1482-L1500
[456]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1445-L1463
[457]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1417-L1434
[458]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1390-L1408
[467]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1244-L1261
[469]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1191-L1208
[470]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1164-L1181
[471]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1159
[473]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1250-L1257
[474]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1213-L1227
[475]: https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/RUN_STATE.md#L1055-L1072
[476]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1169-L1172
[477]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1140-L1144
[479]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1084-L1087
[479-issue]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1091
[480]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1055-L1066
[481]: https://github.com/mpmdw/JouleWise/blob/b15fb4b090e3ff2c131c27bf4605dea0e861b6dc/RUN_STATE.md#L1055
[481-check]: https://github.com/mpmdw/JouleWise/blob/b15fb4b090e3ff2c131c27bf4605dea0e861b6dc/RUN_STATE.md#L1069-L1072
[481-issue]: https://github.com/mpmdw/JouleWise/blob/b15fb4b090e3ff2c131c27bf4605dea0e861b6dc/RUN_STATE.md#L1076
[roster]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22421-L22448
[piece]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22441-L22448
[review]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22459-L22466
[no-redo]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22537-L22542
[placement]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22863-L22868
[loaded]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23022-L23045
