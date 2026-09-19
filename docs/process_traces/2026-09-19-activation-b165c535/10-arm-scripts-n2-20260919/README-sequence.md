# n2-20260919 equivalence night two: bench sequence

Bench adaptation by the magistrate (activation b165c535) of seat 17's 09-19
night-one scripts (`../../2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/`),
for the runbook §2.5 INCONCLUSIVE successor. Candidate triple:
`(d079-epoch-25g83-derivation-n2-20260919, /Users/edr/JouleWise-measurement-20260919-derivation-n2, __H__)`,
t0 2026-09-19 05:00:00 PDT (1789819200).

## What changed from night one's scripts, and why

| File | Change | Reason |
|---|---|---|
| `arm-env.zsh` | `WINDOW_ID=n2`; root `…-derivation-n2`; `T0_EPOCH_S=1789819200`; `LEDGER_SOURCE` = the night-one clone's 126-record ledger, pinned by `LEDGER_SOURCE_EXPECTED_SHA256` | Night one appended 50 rows; the canonical root's copy is stale at 76 and is not touched (record 01 finding 1) |
| `step0-precheck.zsh` (replaces `step0-retire.zsh`) | No retirement. Proves: only the magistrate label loaded, no night plists; discovery = exactly the two RETAINED roots (09-16, n1-20260919); night-one archive 86/86 checksums against the live root; night-one clone at `59d5b076`, clean, ledger digest and pin 126; n2 paths absent; load/power/thermal | Night one opened a session, so its root and clone are retained (handback §Next lane); nothing is refused, nothing to retire |
| `step1-clone.zsh` | Adds the source-digest check and a 126-row count after the byte-equal copy | The copy must be the authenticated ledger, not the canonical stale one |
| `step2-desk.zsh` | unchanged | same desk checks, plan writer v2/2, generator, preflight, render, schedule |
| `step3-notice.zsh` | Notice body gains two sentences: why this night (INCONCLUSIVE m=4; issue 316 / §2.5 one more night; pin 126) and the cadence diagnostic pointer with an explicit "reply NO to wait" | Ed's NO overrides; the diagnosis must be in front of him |
| `step4-publish-install.zsh` | `step4a-successor-evidence.py` call and `successor_arm_allowed` removed; gate is `retry_allowed(now, context, [], notice)` (D-180 R1, empty history = initial arm) | Night one was not a refusal; D-182's zero-capture successor route does not apply |
| `step5-verify-and-exit.zsh` | Exit-rule line computed from `T0_EPOCH_S` | the previous literal named 09-18 23:52 |

Run order: step0 → (H lands on main; fill `H` in `arm-env.zsh`) → step1 → step2 → step3 → magistrate sends the notice with the Gmail tool and fills `notice.json` + `notice-evidence.txt` → step4 → step5 → arm record → exit strictly before 04:52:00 PDT.

## Boundaries

| Boundary | PDT | UTC | Epoch |
|---|---|---|---|
| Install close (excluded) | Sep 19 04:50 | Sep 19 11:50 | 1789818600 |
| REQUEST / exit strictly before | Sep 19 04:52 | 11:52 | 1789818720 |
| TERM | 04:54 | 11:54 | 1789818840 |
| KILL | 04:55 | 11:55 | 1789818900 |
| t0 | 05:00 | 12:00 | 1789819200 |
| Acquisition end | 07:30 | 14:30 | 1789828200 |
| Completion / courier | 07:35 | 14:35 | 1789828500 |
| Daily dead-man | 08:35 | 15:35 | 1789832100 |
