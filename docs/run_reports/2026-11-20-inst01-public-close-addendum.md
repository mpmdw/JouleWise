# 2026-11-20 · lm-inst-01 public close-status handoff

Tier 0, public records. Audit base `eaaa1fd560cd457f4e4ccef316be62af920d08e1`. Signing target none. The [addendum](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/inst01-public-close-addendum.md) extends the cold-pass packet from item 475 and gives Opus the proposed piece-1 deviation paragraph.

At `2026-11-20T12:50:48Z`, public main was `b15fb4b090e3ff2c131c27bf4605dea0e861b6dc` with item 481 as the latest public instrument update. [Item 481][481]

| Cutoff | Check-backed | Issued, Check pending | Unissued | Total |
|---|---:|---:|---:|---:|
| 480 | 32 | 2 | 2 | 36 |
| 481 | 34 | 2 | 0 | 36 |

The last public Check is item 481 for `f2-inst-03` L009–L010. It reports both runner-admitted. L011–L012 are the next unfilled positions, issued in item 481 and awaiting a public Check or typed disposition. The two publicly recorded loaded positions are `f2-inst-02` L005 and `f2-inst-03` L007. The addendum carries them as `not_qualified:loaded` and records observed planner overruns in a separate column. The final stage-1 qualified count is pending. [Item 480][480] · [Item 481][481] · [RL-192b][loaded]

Item 473 records the late piece-1 signature and discharge of the operational gate with blinding preserved. Opus has one proposed paragraph to commit only in `docs/process/cadence/looks/lm-inst-01-DEVIATIONS.md` beside the final manifest, under the lead's 22:50 decision confirmed in RL-191 §4(b). Row 7 still needs its evidence bindings. The cold-pass ruling is to name the deviation file's SHA-256 alongside the final manifest's. [Item 473][473] · [RL-190 §3.3][piece] · [RL-191 §4(b)][placement]

## Verification

- PASS for the row and source check. All 36 keys are unique, each kit has 12, each cutoff totals 36, and all 33 distinct pinned anchors resolve. The check also covers the loaded rows, pending cells, timing flags and the single deviation paragraph.
- PASS for `git diff --check` against the audit base. This documentation change uses focused local verification. Hosted CI reports on the draft audit PR head.

## Next step for Opus

Fill L011–L012 against the next public Check or typed disposition. Carry the proposal into the public deviation file when committing the final manifest. Collection accounting, row-7 bindings and the cold-pass ruling remain required by RL-190. [Item 481][481] · [RL-190 §§3.1–3.5][row7]

NEEDS_SPEC: none.

[473]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1250-L1257
[480]: https://github.com/mpmdw/JouleWise/blob/628604d8db4178ef3f8739ae51674d6fef1b98f5/RUN_STATE.md#L1055-L1066
[481]: https://github.com/mpmdw/JouleWise/blob/b15fb4b090e3ff2c131c27bf4605dea0e861b6dc/RUN_STATE.md#L1055-L1076
[row7]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22421-L22466
[piece]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22441-L22448
[placement]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22863-L22868
[loaded]: https://github.com/mpmdw/JouleWise/blob/b4f6b1a11cf1e852bf06210fed16dd36d45a03bf/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23022-L23045
