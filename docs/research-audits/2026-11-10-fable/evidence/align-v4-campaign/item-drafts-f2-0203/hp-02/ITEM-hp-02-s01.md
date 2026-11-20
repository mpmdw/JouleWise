TBD. **Successor ready for the issuing desk under RL-190 §2 and ITEM-GATES-SPEC. Lead issues one attempt for `hp-02-s01` on `dd206025abb30fd5c07515cd4b34b3e653174810`, ordered roster `L001,L002,L003`. Require the latest unambiguous clean host Check, named in the issue record and refreshed at arm. Exit the magistrate immediately when the launcher claims the shared fence.**

```pointer
owner: magistrate
wait: none
deadline: from the lead's typed issue Check deadline
on_early_or_refused: record the decision and re-rank on current eligible entries. Stop the host on unproven restore; follow the recovery procedure below. A started or ambiguously consumed leg stays held. Never skip a predecessor or replace a leg.
next_observable: the first activation after fence clearance runs Check and sends the operational verdict and close record to the lead
```

**Issue.** Bind the accepted spec and occupancy addendum, exact kit `cl-hp-02` SHA-256 `7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66`, rank 3, attempt 1, sequence 1, ordered unrun leg IDs, prior Check, current close, named magistrate Check target and Check deadline. Name the admitted `queue-b.json` at `e3eaa282f9d4cea3b579eeb7bde989ff897df45e`, path `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203/hp-02/queue-b.json`, SHA-256 `078eb24c3149f2a7bc522a432098e51e21bd36278d288b0f41efbb5d57da528f`. Its local interval opens at `2026-11-21T00:00:00-08:00` and expires exclusively at `2026-11-30T00:00:00-08:00`. The kit master seed is 2026111601 versus hp-01's 2026111404.

For `LINE2_OK=yes`, record all three:

1. RUN_STATE item 338 at `6640a66719a2ff1f8cc38dbce3e8231f419e79d8`, hp-01 kit digest `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965`, and its four-part line-2 record. CI 43673985768 at `2a8deb7b9` carries the twelve reds of 43600776368 at `fe907d0d3`, test for test. All twelve passed at PR #777's head in 43601158271. Preserve the historical record.
2. The independent [HP02-DELTA.md](HP02-DELTA.md) at `e3eaa282f9d4cea3b579eeb7bde989ff897df45e` and its finding that hp-02's `frozen` block is byte-equal to hp-01's.
3. Line 2 for `cl-hp-02` (`7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66`) is `cl-hp-01`'s record under RL-165 §5; no frozen byte differs (RL-190 2).

Use the inherited Class A smoke accepted in RUN_STATE 337–338. The issuing desk confirms that `lm-hp-01` has neither started nor been reserved across the execution register and both custody roots, and records the census of hp-01 local t0-dates. This descriptive block is outside the 132 cap, day count, line 9, and every fit, and carries zero reserve. The future manifest lists both HP blocks by kit and receipt, roster and as-run position before any HP read. This supersedes the inherited kit prose about the interim look and reserve.

**Issue, Start and Run.** Invoke the same gate with a separate current observation for each phase. See [README.md](README.md) for the record fields and staging. The eligible ladder is effective READY, counted work, first stability leg of that local date from the lowest eligible kit 01–14, the finite instrument kits 01 → 02 → 03, this HP roster, then further stability. Re-rank at every clean close and at arm. The dated calendar contains every remaining counted start, including outstanding halves, on its actual allowed pin windows. A last counted start may be 23:59:59 and finish the next day.

The gate selects the explicit argument on the actual clock. It tries `02:00-02:35` first and uses `13:14-13:15` only after a window-only refusal. Expected work 6,903 s, plan worst 16,650 s, shared fence 18,110 s. Fit the composed timing through outer clearance inside that fence, and reserve the entire fence plus any transfer outside it against dated starts. Supply demonstrable setup, wait, close, restore and clearance bounds with each phase. HP may run at any hour the pin admits. The runner soaks in Automatic on AC, applies G0 and load checks, sets the marker before changing to mode 2, verifies mode 2 across every included leg and keeps leg children from changing mode.

Before each phase, record current mode rules and measurement mode verification, the four RL-174 C lines, AC and floating battery, network time off, frequency zero, no lock, no maintenance or veto, disk floor, collector and meter, latest operational receipt, proven stop of every feed and group, and current independent group and case-insensitive agent census. Only the documented own-tree and jobs exceptions apply. A contradictory receipt cannot be overwritten with an empty census. Verify the latest copy by typed manifest and ciphertext digests, size and provider readback. At 600 s carry unresolved debt only after proving the transfer stopped. Preserve originals, page at 2 h and daily thereafter, and retain the original until two verified off-host copies and the off-host key exist.

**Start and check** (authorized desk only). Use a reviewed successor audit checkout and the detached measurement checkout below. Fill `HP_ISSUE` and its approved SHA, the staged `QUEUE_FILE`, the pinned `PY`, the desk PID and fresh phase record paths. Choose a new `OUT` under the HP campaign root. At Issue use `hp_gate Issue "$HP_ISSUE_OBSERVATION"` in place of the Start invocation, then have the lead record the passed decision and issue the item. At Start, the issue record must be ISSUED.

```sh
set -eu
set -o pipefail
SPAN=hp-02-s01
LEGS=L001,L002,L003
REPO=/Users/edr/code/jw-wt/cadence-hp-02-s01
KIT=/Users/edr/campaign-out/kits/cl-hp-02-RL174B.json
CUSTODY=/Users/edr/night-custody/magistrate
: "${HP_DRAFTS:?absolute path to the reviewed item-drafts-f2-0203 directory}"
: "${OUT:?fresh HP output path}"
. "$HP_DRAFTS/hp-02/gates.sh"
hp_gate Start "$HP_START_OBSERVATION" || exit 1
```

**Run.** Refresh the records, native census, marker, fence and clock after Start. Invoke the same gate with the Run observation immediately before launch. Run requires evidence sampled after the successful Start verdict on the same host. The shared admission record retains observed close, restore, look-execution and spent-leg facts across issues and retries. The gate reserves the roster, then rechecks the handoff clock after the claim is durable. The claim records the exact argument, t0 and deadline. On bootstrap refusal hold this attempt for the lead. Exit the session as soon as the launcher reports a claimed fence.

```sh
hp_gate Run "$HP_RUN_OBSERVATION" || exit 1
```

**Check.** Wait for shared fence clearance, including a dangling link check. Use the recorded output and `ARG` from the Run claim. Verify the operational receipt and run the pinned automatic desk against the operational projection only. Record the desk verdict, mode-to-first-G0 delay, per-leg wall/budget, revocation and all named stops. Report `LEG_OVERTIME` or fewer than nine included HP legs to the research lead as applicable. Check mode 0, no marker or host lock, network time off, frequency zero, independent group absence and measurement-mode verification. Record actual close and fence-gone times. A failed child stays unadmitted.

```sh
test ! -e "$CUSTODY/desk_fence.json" && test ! -L "$CUSTODY/desk_fence.json" || exit 1
"$PY" -I -B - "$OUT" "$LEGS" "$ARG" <<'PY'
import json, sys
from pathlib import Path
out=Path(sys.argv[1]); roster=sys.argv[2].split(',')
r=json.loads((out/'runner_receipt.json').read_text())
assert r.get('mock') in (None,False), 'synthetic receipt is not live evidence'
assert r['runner_kind']=='cadence-legs-v1' and r['roster']==roster
assert r['batch_windows']==[sys.argv[3]]
assert r['kit']['campaign_id']=='cl-hp-02' and r['kit']['sha256']=='7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66'
assert r['kit']['frozen_commit']=='dd206025abb30fd5c07515cd4b34b3e653174810'
assert r['rc']==0 and not r.get('error') and r['legs_finished']==len(roster)==r['legs_planned']
assert r['span_result']['outcome']=='MEASURED_OK' and r['span_result']['chain_outcome']=='COMPLETE'
hp=r['high_power']; proof=hp['close_proof']
assert proof['proven'] is True and type(proof['ac_powermode']) is int and proof['ac_powermode']==0
assert proof['host_marker_present'] is False
assert not hp.get('revoked'), 'HP admission revoked: hold for the research lead'
assert set(r['feeds'])=={'agents','meter','volumes'}
assert all(f['stop']['proven_stopped'] is True for f in r['feeds'].values())
assert all(sum(s['name']==name for s in r['steps'])==1 for name in ('restore','stop-agents','stop-meter','stop-volumes','power_proof','host_lock_release'))
assert all(s['rc']==0 for s in r['steps'] if s['name']=='restore' or s['name'].startswith(('stop-','close-','power_','host_lock_release')))
span=json.loads((out/'desk-bundle/span/result.json').read_text()); assert span['restore_proven'] is True
print('operational receipt',r['rc'],r['legs_finished'],r['ended'],'power close',proof)
for leg in roster:
    rec=json.loads((out/'legs'/leg/'leg_record.json').read_text())
    result=rec.get('result') or {}
    summary=json.loads((out/'desk-bundle/legs'/leg/'leg_summary.json').read_text())
    print(leg,{k:result.get(k) for k in ('leg_status','g0_outcome','g0_wait_s','decode_tokens','decode_cap_reached','prefill_tokens','ac_powermode')},
          {k:summary.get(k) for k in ('admitted','wall_s','budget_s','contaminated_redos','g0_outcome')})
print('RECEIPT OK; this is operational verification, never an energy read')
PY
```

**Restore owed.** If the close leaves restoration unproven, or a marker has no owner, hold the host. Once the measuring job and shared fence are clear, invoke the pinned `scripts/cadence_legs_runner.py restore-owed` once from the detached checkout and independently read back every restore line. The pin defers under the host lock and refuses W1 markers. Never delete a marker or recover during arm. If restoration still cannot be proven halt the host and page Ed and the lead. A proven recovery clears only its restore stop. Keep any receipt refusal, revocation or unresolved group open until positively dispositioned. Give the lead the Check before any successor arms.
