# Exhibit C — the two process texts lane A230 says contradict each other (main `9e0a4995`)

## C1 `docs/phase_2/derivation_night_runbook.md` lines 699–728 (section 0.7, complete)
```
### 0.7 Nothing else is armed or discoverable

No stand-down, no Ed NO, no unresolved owner-authored `directive` issue, no
discoverable prior plan root, no active or indeterminate measurement ownership.
Remove every `REHEARSAL_STUB` plan root before arming any real plan
(`docs/process/MAGISTRATE_WATCHDOG.md`, §"Install handoff").

**Sibling discovery uses one exact glob; installed plists provide a second fence.**
The watchdog enumerates sibling plans by globbing `*/night_plan.json` in the
PARENT of its own state directory — `glob_plans` in `scripts/magistrate_watchdog.py`, whose
state root is `/Users/edr/night-custody/magistrate`, so the enumerated set is
exactly `/Users/edr/night-custody/*/night_plan.json`: one level down, that
filename, nothing else. A plan authored at `$STAGED_PLAN` under
`/Users/edr/night-plan-staging/<PLAN_ID>/` is therefore outside sibling
discovery, which is why §1.1b authors and verifies there. §1.4's `os.replace`
into `$NIGHT_ROOT/night_plan.json`, after the email, makes it discoverable.
Independently, the watchdog reads the `--plan` paths in both installed night
plists and fences their active spans, holding unsafe on unreadable or malformed
inputs. The installer requires the resolved plan path to be
`<custody_root>/night_plan.json`; staging is never an install destination.
The night's own driver never discovers anything — launchd hands
`scripts/run_night.py` the plan path as a
`--plan` argument (its `--plan` is `required=True`), so the driver reads the
file it was installed with and no other.

Check it, and expect no output:

```zsh
print -rl -- /Users/edr/night-custody/*/night_plan.json(N)
```
```

## C2 `docs/process/NIGHT_HANDBACK.md` lines 494–500. Source: a dated addendum inside the handback (a process document with dated operational addenda). Proposition addressed: whether the 2026-09-16 night's root was ruled RETAINED. Non-narrative primary evidence of that ruling does not exist elsewhere; the excerpt is the contiguous paragraph.
```
item 4). `scripts/epoch_equivalence_check.py` from two checkouts at H:
**EPOCH_EQUIVALENCE INCONCLUSIVE (m = 4 < 6)**, records byte-identical. Under
directive issue 316 the ONE next action is one more equivalence night under a
fresh plan id; nothing else. Both night agents were uninstalled from the clone
(rc 0). The clone and the night root are RETAINED (a session opened).
RECORD: harvest and uninstall for this night are complete; the successor
equivalence night is prepared under this handback's §Next lane.
```

## C3 `TASK_QUEUE.md` line 858 (lane A230's registration, verbatim). Proposition addressed: the exact question the lane registered and the two options it named. This is the lane's own text, the object of Q2.
```
| A230 | NIGHT-ROOT-RETENTION-DISCOVERY-01 | P2 Next Slice | READY [AGENT] | docs/phase_2/derivation_night_runbook.md section 0.7 says the arm precondition `print -rl -- /Users/edr/night-custody/*/night_plan.json(N)` must print nothing, while docs/process/NIGHT_HANDBACK.md section Next lane rules that the clone and night root of a night that opened a ledger session are RETAINED (only a refused night's plan root is retired). After the 2026-09-16 night, which opened a session, its root /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916 stays discoverable by that glob, so the two texts contradict each other for every retained root. The watchdog fences only active spans (plan_span_active, plan_is_armed in scripts/magistrate_watchdog.py) and the installer reads no sibling, so a completed retained root arms nothing; the 2026-09-17 arm proceeded on that reading and recorded it (arm record 77). | One rule holds in both documents, chosen by the cold gate or Ed (rule 11): either retained roots move out of discovery to a retained-custody location that is not /Users/edr/night-custody/<plan_id> (with the handback's retention wording and the inventory updated), or section 0.7's precondition is restated as 'no plan whose span is active or whose agents are installed', with the executable check that the watchdog already applies; the runbook and the handback then say the same thing and the arm scripts assert the executable form. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md (section Step 2, discovery bullet); docs/phase_2/derivation_night_runbook.md (section 0.7); docs/process/NIGHT_HANDBACK.md (section Next lane, retention sentence). Authority: [2026-09-17 activation 9853dd2b, arm record 77 (n1-20260917); registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md). Acceptance: [NIGHT-ROOT-RETENTION-DISCOVERY-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: docs contradiction found at the arm; magistrate registration, not a ruling; the 09-16 root was NOT moved (the launch charge forbids moving plan directories this session did not author). Goes to the cold gate or Ed before the next harvest retires or retains a root. 2026-09-18 headless activation f0b608b7 (record 01): the 09-16 harvest archive `~/night-archive/d079-epoch-25g83-derivation-n1-20260916-harvest-20260916/`, found empty by arm record 21, was re-harvested byte-exact from the retained live root (20/20 sums OK against the live root and the copy, `SHA256SUMS` inside the archive, inventories identical); the 09-16 root remains retained under this lane's rule and may now be retired when the lane rules, with a complete archive. The 09-17 plan root was retired 2026-09-18 19:26 (arm record 21, step 0). 2026-09-19 — A third retained, inert night root (the directory holding a completed night's plan and evidence), `d079-epoch-25g83-derivation-n2-20260919`, now remains alongside the 2026-09-16 and `n1-20260919` roots. |
```
