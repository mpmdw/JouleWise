# hp-02 successor items · 2026-11-19

Builder desk work on `ops/2026-11-19-hp02-successor-items`, based on audit `ea2f55318cbc9806be5570a2b21b362ad12b1db4`. RL-190 §2 carries RUN_STATE 338's four-part line-2 record, including its historical twelve-red comparison, and the independent frozen-byte delta. RUN_STATE 422, 447, 463, 464 and 472 supply the rank and host decision rules. HP remains descriptive only. Refer to the [generated items and desk procedure](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02/README.md).

- Pin `dd206025abb30fd5c07515cd4b34b3e653174810`, kit SHA-256 `7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66`.
- Queue-b at `e3eaa282f9d4cea3b579eeb7bde989ff897df45e`, SHA-256 `078eb24c3149f2a7bc522a432098e51e21bd36278d288b0f41efbb5d57da528f`. It preserves queue-a's 3+4+5 rosters and the kit's seed. Its local interval is November 21 00:00 inclusive to November 30 00:00 exclusive.
- Issue, Start and Run use one decision with fresh scoped records. It checks the finite queue, unspent roster, predecessor and host close, copy disposition, eligible ladder, counted calendar and composed occupancy through outer clearance. Run claims the roster once before the pinned launcher. The lead owns live evidence and issue.
- The original frozen fixtures and occupancy delivery match the supplied bytes. The new unittest module is discoverable by CI.

## Synthetic verification

| Replay | Result |
| --- | --- |
| Executing item decisions | 60/60 frozen original vectors. Fresh Issue, Start and Run observations plus changed-state Start → Run controls. |
| Successor occupancy | 54/54 timing decisions and 1,764 explicit clock cases, with 11 dated-pair decisions and zero native attempts. |
| Frozen runner replay | 43 fake runner traces, including close-restore failure. The plan-only negative control gave the required 27 false permissions in 54 decisions. |
| Legacy held-item replay | 60 vectors × three original items × Bash and zsh, 360/360 matched the frozen legacy expectations. |
| Staging and syntax | 55 local staging cases. Bash and zsh parse all 11 item scripts. |

Selected legacy failures, from the exact original shell functions at `a32eb54ce9ea8a19e348bad6890a15336b8db2e5`:

| Frozen ID | Original result | Successor |
| --- | --- | --- |
| `clear-date-no-qualification` | Waited for a prior same-date qualification span | Eligible |
| `item-24h`, `kit-seven-days`, `other-close-1199s` | Rejected on the retired limits | Eligible |
| `rank-first-stability` | Passed over the first eligible stability leg | Cede to rank 1 |
| `rank-post-R1-F0` | Ceded to retired F0 | Eligible |
| `pair-equality` | Ceded on the old scalar horizon | Eligible at 23:59:59 |
| `pair-plus-one` | Passed with the last counted start blocked | Cede |
| `unproven-group`, `foreign-agent` | Passed the legacy fragment | Hold |
| `marker-dangling-link` | Passed the legacy fragment | Hold at both phases |

Reproduce with `python3.13 -B -m unittest tests.test_hp02_successor_items`. The old replay exercises the two embedded functions only. The frozen clock profile is synthetic. The built items require the desk's demonstrated bounds at issue and at both arm decisions. No measured energy was read.

## Review handoff

NEEDS_SPEC raised by the builder: none. The Friday timing examples use the frozen symbolic queue and the committed queue-b opens Saturday, as directed.

The draft PR is the review vehicle and its gate ledger records the review and CI state. Independent execution at the exact candidate, lead acceptance and the current issuing-desk records remain ahead of any issue. The next lead step is to assign the independent executing review, then evaluate Issue for an eligible local time using current host and look evidence.
