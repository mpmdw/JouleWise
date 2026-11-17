TBD. **Laptop lead (interactive, Opus 5.5), drafted under RL-171 and RL-172 by the items-rl171 builder 2026-11-15 PST (new draft on the hp-01 smoke item; the hp01-ready builder's mirror append), ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm hp-01's THIRD span (RL-157 §3, §8; RL-165 §5 to §7; RL-171; RL-172): kit `cl-hp-01`, legs L008, L009, L010, L011, L012 only, span `hp-01-s03`, runner kind `cadence-legs-v1`, on `dd206025abb30fd5c07515cd4b34b3e653174810` checked out detached in a fresh scratch worktree. One span: a fresh soak in Automatic, then AC powermode 2 (High Power) set by the runner, then 5 type-H legs (type A in High Power: 19,458-token step prompt, decode cap 4,096, band q0), then the close restores Automatic and proves it. They are counted type-H legs of hp-01; hp-01 is description only, never in the fit. No other span, no queue extension, no session, no W1. EARLIEST: the close interval after `hp-01-s02` closed with its fence gone (RL-171 §6.1; 300 s, RL-172 §0) and every gate below holds, and not before 00:30:01 PST Sun 15 Nov (epoch 1794731401). LAUNCH as soon as every gate holds, at any hour, up to 18:22:30 PST Mon 16 Nov (LIMIT, epoch 1794882150), with the worst-case end by the next 00:30 (RL-165 §7, kept by RL-171 §2; the small hours allowed while the lead is present, RL-172 §0): so not from Sun 18:22:30 to Mon 00:30:00, and never 10:50:00-13:15:00 (this pin's soak path waits out 11:45-13:15 unbudgeted). The batch-window argument follows the launch time (RL-171 §3): `13:14-13:15` from 00:30:01 to 02:34:59, `02:00-02:35` from 02:35:00. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies, RL-165 §3).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-17T01:55:00-08:00
on_early_or_refused: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), a High Power marker or a held host night lock at the arm, or a launch that cannot happen inside the bands below (Sun 00:30:01 to Mon 18:22:30 PST, outside the 00:30 rule's evening cut and 10:50:00-13:15:00): NOTHING of this item launches; mail the lead (a later t0 needs a re-issued item). The standing F0 item's refusal rule then applies, unless the stop is RESTORE_UNPROVEN or a host-state stop, which hold everything. A span that ran but ends with any named stop, a receipt rc≠0, restore_proven not true, a High Power marker present or AC powermode not 0 at the Check: nothing relaunches, nothing is re-run, nothing else arms (RESTORE_UNPROVEN holds everything, F0 included); run restore-owed ONLY under "Restore owed" below; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the magistrate's own power reads (AC powermode 0, no marker, no lock holder), the maintenance line, the receipt asserts with restore_proven and the close proof, the D1 lines (admitted per leg, high_power.revoked, high_power.before_restore), the desk bundle, the restore lines, measurement_mode verify again, the RL-157 §1 and §5 prints and the RL-150 R1 start-reference print (none of the prints gates)
```

- **Why.** hp-01's remainder runs after the smoke passed and the lead's hand-read (RL-150 R5; RL-157 §3, §8). `dev-01-s03` ran L004-L007 and `dev-01-s04` L008-L012, so hp-01 mirrors them: `hp-01-s02` L004-L007, then `hp-01-s03` L008-L012 (RL-157 §3, the mirror file `QUEUE-cl-hp-01-dd206025a-append-mirror-4plus5.json`). **Order (RL-165 §1, §2):** on Sunday after `dev-01-s04`: the R1 slot session if READY, then hp-01's spans, then the dev-02 pull, then F0; on Monday after dev-02 closes: the slot session if READY, then the dev-03 pilot, then hp-01's unrun spans, then P, then F0. A leg's calendar day is the local date of its span's t0.
- **Day law (RL-172 (a)).** hp-01 is outside the development-leg count ((a) rule 4), so no `day_gate` runs here; (a) sets no date for hp-01. RL-149 §2.3 gives hp-01 "any day after dev-01".
- **Gate.** All of:
  - **`hp-01-s02` closed clean:** <LEAD FILLS: RUN_STATE <n>: RECEIPT OK, 4 legs run and admitted of 4, restore_proven true, close proof proven, no named stop open, no `high_power.revoked` entry (D1's second line holds this span until the research lead rules), no LEG_OVERTIME pending at the research lead, close epoch>.
  - **Line 9:** this span is campaign span 6, so span 4's desk, the smoke `hp-01-s01` (`cq-hp-01-s01-a1`) must be FINAL.
  - Line 2 as `hp-01-s02`'s: run 43673985768 on `2a8deb7b9`, base + 0.
  - Lines 5, 6 and 7 at the arm (below).
  - **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-172 (f)):** the Check of the latest close of ANYTHING on this host reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (300 s after a campaign close, RL-172 §0; 1,200 s after a Part C or F0, F2, a slot session or W1), from the receipt census that stops on a missing root, any lookup error or an empty result (or OTHER_CLOSE_EPOCH); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the lead's marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). From the lead's record that a v4 session is READY, nothing of lower priority arms and the session takes the next clean close (RL-172 (f)); RL-165 §7's worst-case reservation is retired.
- **Alarm (the lead's watcher, RL-165 §7).** At issue the lead arms an alarm at this span's worst-case end, t0 + 22,050 s (at the forecast t0: 13:45:12; at the LIMIT: Tue 00:30:00), that fires if the fence is still up or no Check is reported, and a second at the fence end, t0 + 23,510 s. The magistrate records t0 so the lead can set it.
- **Counted.** The 5 legs count as type-H legs of hp-01 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8, RL-157 §4): rule 6 is the block's mode, so a leg is admitted only if it recorded AC powermode 2 at its episode start and was not withdrawn. hp-01 has no reserve (RL-157 §4): an excluded type-H leg is not replaced.
- **Bytes, line 2 and condition 13:** as the smoke's item. Measured from `dd206025abb30fd5c07515cd4b34b3e653174810`; the kit is `cl-hp-01.json` from `bbd34dc87`, sha256 `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965`, copied outside the checkout (the in-tree kit at `dd206025a` is the superseded `bd7c8711…`). `dd206025a` has the v1 launcher (no fence check). `verify_r1_executed_sources` must return the full sha. No smoke of its own: the smoke was `hp-01-s01`.
- **What the runner does:** as the smoke's item (docs/process/cadence_queue_design.md §13 and §13.2 at `dd206025a`), with this roster: the host lock, the marker written first, `pmset -c powermode 2` read back, a powermode check before every attempt, per-leg load redo (quota 2), no leg starts inside the batch-window argument (`$ARG`), and the close's `power_last_look`, `restore`, `power_proof` and `host_lock_release`. It reads and writes no energy.
- **Timing.** Plan for this roster (`plan` at `dd206025a` with the argument of each band, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-hp01-s03.txt`): expected 9,405 s, worst case 22,050 s, budget_s 1,251 per leg; fence deadline launch + 23,510 s (worst case + 1,460 s).
  - **Bands (the `pick_arg` function below), Sun and Mon:** 00:30:01-02:34:59 `13:14-13:15`; 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-18:22:30 `02:00-02:35`; none 18:22:30-00:30:00 (the 00:30 rule; the bytes alone would admit `02:00-02:35` to 19:52:30). A mock span at t0 Mon 00:30 with `13:14-13:15`: rc 0, 5 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/hp01-s03-alt-00:30/`; the mock does not model the 11:45-13:15 soak wait).
  - Forecast t0 Sun 07:37:42 (hp-01-s02's expected close 07:32:42 + 5 min), argument `02:00-02:35`: expected end 10:14:27, worst end 13:45:12, fence end 14:09:32 (`/Volumes/JW-EXT/scratch/items-rl171/plans/chain-new.txt`).
  - Pointer deadline = latest fence end (LIMIT + 23,510 s = Tue 00:54:20) + 1 h.
- **Conditions:** as the smoke's item: no agent session on the MBP during the span; the restore lines before the launch and in Check; the High Power preflight (`pmset -g custom` AC powermode 0, no marker file or link, both `pmset -c powermode 0` and `2` sudo rules listed, no `night.lock` holder, `JOULEWISE_HOST_STATE_DIR` unset); `--batch-window "$ARG"` and `--legs L008,L009,L010,L011,L012` written out on every `validate-kit`, `plan` and `launch`; the measurement_mode line; output root `/Users/edr/campaign-out/cl-hp-01/`. Quiet is the per-leg census and rule 5 (RL-171); there is no clock quiet.
- **RESTORE_UNPROVEN holds everything; RL-157 §2 condition 2; LEG_OVERTIME to the research lead; Blinding:** exactly as the smoke's item.
- **May run:** this span, once. **May NOT:** any other hp-01 span (`hp-01-s02` again), any other campaign span, any session, W1, any filler, and `restore-owed` while this span is armed or its fence is live.
- **High Power marker at the arm:** if `/Users/Shared/JouleWise/host-power/high-power.marker` exists, STOP and report. Do not run `restore-owed` at the arm.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. As the smoke's line 1 (kit `cl-hp-01` `7eaf2660…d2965` on `dd206025a`; the Mythos cold and delta seats, the row-1 review, `validate-kit` and the `plan` below).
2. Line 2 in RL-165 §5's four parts, as the smoke's, **with the finished run:** CI `ci` 43673985768 on `2a8deb7b9` (frozen-path diff against `dd206025a` empty) has the same 12 reds as `fe907d0d3`'s run 43600776368, test for test: base + 0. Each of the 12 passes at #777's head (run 43601158271). The recorded diff against `b4b6aeb19` is the five High Power files; the two meter blobs are identical.
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-hp-01-dd206025a-append-mirror-4plus5.json` on audit/2026-11-10-fable at `<LEAD FILLS: commit; the lead commits it when hp-01-s02 is READY>`, sha256 `01687bb7b1206c82657ff018130f8761f249b64b5fa6524f4b3914d0c81a00a5`: the committed one-span queue (`90e042ed…`, `3de39e06a`) with `hp-01-s02` (L004-L007) and `hp-01-s03` (L008-L012) appended, additions only, not_before 2026-11-15, `expires_at` 2026-11-21T23:59-08:00. `validate-queue` ok at `dd206025a` with `--kits-root` a checkout of `bbd34dc87` (kit `7eaf2660…`): plan ids `cq-hp-01-s01-a1`, `cq-hp-01-s02-a1`, `cq-hp-01-s03-a1` (`/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue-hp01.log`). Do NOT run `cadence_queue.py next`; this item names the span. The fallbacks in `/Volumes/JW-EXT/scratch/hp01-ready/queue/` (mirror 3 + 6, fallback 6 + 3, s02 nine legs) are not used.
4. `validate-kit` passes; OUT is outside every v4 registration and custody root (check below).
5. The per-span checks of design doc §4 and §13.2.1 pass at the arm and at the close. Do NOT run `cadence_queue.py checklist`.
6. No named stop, veto or halt open (the `directive` and `cadence-stop` issues; gh via `launchctl asuser`), no RESTORE_UNPROVEN open from any span or Part C run, and no `high_power.revoked` hold: <LEAD FILLS: span ids, their desk `stops.json` result and the time read>.
7. Results-ref watcher live within 24 h: <LEAD FILLS: heartbeat stamp, pid and commit>.
8. The smoke passed and `hp-01-s02` closed clean (Gate above).
9. Line 9, across blocks in run order (RL-165 §6). Expected: this span is campaign span 6, so span 4's desk, the smoke `hp-01-s01` (`cq-hp-01-s01-a1`) must be FINAL. As run: this span is campaign span <LEAD FILLS: N>, and the desk of the span two back, <LEAD FILLS: SPAN ID>, is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded>.

**Start and check (while you are still alive).** From a FRESH scratch worktree detached at the full sha (NOT the canonical clone's checkout, not another smoke worktree, not the smoke's own worktree `cadence-hp01-s01` (a fresh one, as every span), not a dev-01 worktree at `b4b6aeb19`), own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `python3.13 -B -m unittest`, one module at a time; all must be OK: `tests.cadence.test_high_power`, `tests.cadence.test_legs_runner`, `tests.cadence.test_kit`, `tests.cadence.test_stops_desk`, `tests.cadence.test_runner_guards`, `tests.align.test_r1_smoke_launcher`. (At `dd206025a` the in-tree kit is the superseded draft `bd7c8711…`; the armed kit is checked by `validate-kit` below.) Any failure: nothing launches; mail the lead.

```sh
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-hp01
test -e /Users/edr/code/jw-wt/cadence-hp01-s03 || git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/jw-wt/cadence-hp01-s03 dd206025abb30fd5c07515cd4b34b3e653174810   # reused on a retry after a WAIT
cd /Users/edr/code/jw-wt/cadence-hp01-s03
test "$(git rev-parse HEAD)" = dd206025abb30fd5c07515cd4b34b3e653174810 || { echo "STOP: HEAD"; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: dirty tree"; exit 1; }
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"                 # must show the claude process
: "${PRIOR_CLOSE_EPOCH:?Set to the later of hp-01-s02 runner_receipt ended.epoch_s and the epoch its desk fence was seen gone (or the R1 slot session close, if it ran first)}"
QUIET_CAMPAIGN_S=300    # RL-171 §6.1, confirmed by RL-172 §0: 300 s after a campaign close; 1,200 s after F0, F2 or any other close
: "${LAST_CLOSE_KIND:?Set to campaign if the latest close of anything on this host was a campaign span, else other (Part C/F0, F2, slot session, W1)}"
case "$LAST_CLOSE_KIND" in campaign) GAP=$QUIET_CAMPAIGN_S;; other) GAP=1200;; *) echo "STOP: LAST_CLOSE_KIND must be campaign or other"; exit 1;; esac
echo "close interval GAP $GAP s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)"
# ONE newest-close selection over both roots, used by the host gate and by copy_gate (Sol RL-172 re-check 1)
close_census() {
  CENSUS="$("$PY" -I -B - /Users/edr/campaign-out /Users/edr/code/jw-wt <<'PY'
import json, math, os, sys
def fail(e): raise e
found = []
for root in sys.argv[1:]:
    if not os.path.isdir(root): sys.exit('STOP: missing receipt root: ' + root)
    base = root.rstrip('/').count('/')
    for d, dirs, files in os.walk(root, onerror=fail):
        if d.count('/') - base >= 3: dirs[:] = []
        if 'runner_receipt.json' in files:
            p = os.path.join(d, 'runner_receipt.json')
            if '\n' in p: sys.exit('STOP: bad receipt path')
            try:
                with open(p) as handle: ended = json.load(handle)['ended']['epoch_s']
                if (isinstance(ended, bool) or not isinstance(ended, (int, float))
                        or not math.isfinite(ended) or ended <= 0):
                    raise ValueError('invalid ended.epoch_s')
            except (OSError, ValueError, KeyError, TypeError) as e:
                sys.exit('STOP: unreadable receipt close stamp: ' + p + ': ' + str(e))
            found.append((ended, p))
if not found: sys.exit('STOP: empty receipt census')
latest = max(t for t, p in found)
newest = [p for t, p in found if t == latest]
if len(newest) != 1: sys.exit('STOP: ambiguous newest receipt close epoch')
print(math.ceil(latest)); print(newest[0])
PY
)" || return 1
  CENSUS_EPOCH="$(printf '%s\n' "$CENSUS" | sed -n 1p)"
  NEWEST_RECEIPT="$(printf '%s\n' "$CENSUS" | sed -n 2p)"
  case "$CENSUS_EPOCH" in ''|*[!0-9]*) echo "STOP: the receipt census gave no close epoch"; return 1;; esac
  test -n "$NEWEST_RECEIPT" || { echo "STOP: the receipt census gave no receipt path"; return 1; }
}
# The effective close, computed ONCE per gate (Sol confirm P1): max of the census and OTHER_CLOSE_EPOCH, with its path or label.
# The host gate's GAP and copy_gate's kind check both use EFF_EPOCH / EFF_PATH from the same call.
effective_close() {
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) of a session/W1 close, or an explicit 0"; return 1;; esac
  close_census || return 1
  EFF_EPOCH=$CENSUS_EPOCH; EFF_PATH="$NEWEST_RECEIPT"
  if test "$OTHER_CLOSE_EPOCH" -gt "$CENSUS_EPOCH"; then
    EFF_EPOCH=$OTHER_CLOSE_EPOCH; EFF_PATH="OTHER_CLOSE_EPOCH $OTHER_CLOSE_EPOCH (a session or W1 close outside the census roots)"
  fi
}
# Sol items-rl171 P1 and Sol RL-172 re-check 1: the newest close of anything (the census above, or OTHER_CLOSE_EPOCH for a
# session/W1 close outside its roots) must agree with LAST_CLOSE_KIND. After a CAMPAIGN close, that receipt's journal copy must be
# complete and hash-verified on the Air: the lead copies by SSH, verifies, and only then writes
# /Users/Shared/JouleWise/desk-copy/<plan-id>.ok (the copy manifest's sha256 and a `date` stamp). No SSH once a span is armed.
# A marker is only ever derived from a campaign receipt path; after a Part C, F0, F2, session or W1 close the Check covers the copy.
copy_gate() (   # a subshell: it reads EFF_PATH (from effective_close) and LAST_CLOSE_KIND and changes nothing the host gate reads
  test -n "${EFF_PATH:-}" || { echo "STOP: copy_gate needs effective_close first"; exit 1; }
  if printf '%s\n' "$EFF_PATH" | grep -Eq '^/Users/edr/campaign-out/cl-[a-z0-9-]+/cq-[a-z0-9-]+-a[0-9]+-[0-9]{8}T[0-9]{6}Z/runner_receipt\.json$'; then
    newkind=campaign
  else
    newkind=other
  fi
  test "$newkind" = "$LAST_CLOSE_KIND" || { echo "STOP: contradictory LAST_CLOSE_KIND ($LAST_CLOSE_KIND): newest close is $EFF_PATH; mail the lead"; exit 1; }
  if test "$newkind" = other; then
    echo "copy gate: newest close is non-campaign ($EFF_PATH); its Check covers the copy"; exit 0
  fi
  plan_id="$(basename "$(dirname "$EFF_PATH")" | sed -E 's/-[0-9]{8}T[0-9]{6}Z$//')"
  case "$plan_id" in cq-*-a[0-9]*) ;; *) echo "STOP: no campaign plan id in $EFF_PATH"; exit 1;; esac
  copy_ok="/Users/Shared/JouleWise/desk-copy/$plan_id.ok"
  test -s "$copy_ok" || { echo "WAIT: no journal-copy marker $copy_ok for the newest close, campaign span $plan_id ($EFF_PATH): the lead's hash-verified copy is not done; retry at the next activation"; exit 1; }
  echo "journal copy of $plan_id: $(cat "$copy_ok")"     # record this line
)
# The launch bands (Sun 00:30:01 to Mon 18:22:30: the v1 bands of this pin cut by the 00:30 rule (worst-case end by the next 00:30); none 10:50:01-13:14:59)
pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3 bands of this pin's own plan, cut by the 00:30 rule)
  n=$1
  if   [ "$n" -ge 1794731401 ] && [ "$n" -le 1794738899 ]; then echo 13:14-13:15   # Sun 15 Nov 00:30:01 .. Sun 15 Nov 02:34:59 (default-takes-over)
  elif [ "$n" -ge 1794738900 ] && [ "$n" -le 1794768600 ]; then echo 02:00-02:35   # Sun 15 Nov 02:35:00 .. Sun 15 Nov 10:50:00 (soak-wait)
  elif [ "$n" -ge 1794777300 ] && [ "$n" -le 1794795750 ]; then echo 02:00-02:35   # Sun 15 Nov 13:15:00 .. Sun 15 Nov 18:22:30 (00:30 rule)
  elif [ "$n" -ge 1794817801 ] && [ "$n" -le 1794825299 ]; then echo 13:14-13:15   # Mon 16 Nov 00:30:01 .. Mon 16 Nov 02:34:59 (default-takes-over)
  elif [ "$n" -ge 1794825300 ] && [ "$n" -le 1794855000 ]; then echo 02:00-02:35   # Mon 16 Nov 02:35:00 .. Mon 16 Nov 10:50:00 (soak-wait)
  elif [ "$n" -ge 1794863700 ] && [ "$n" -le 1794882150 ]; then echo 02:00-02:35   # Mon 16 Nov 13:15:00 .. Mon 16 Nov 18:22:30 (00:30 rule)
  else echo NONE; fi
}
NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior span's close"; exit 1; }
ARG="$(pick_arg "$NOW")"
test "$ARG" != NONE || { echo "STOP: no admitted launch band now (outside this item's window, or inside 10:50-13:15 where this pin cannot launch); mail the lead"; exit 1; }
export ARG; echo "ARG $ARG (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)"
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"   # the watchdog's fence root (fence + launch spec only)
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
# must print dd206025abb30fd5c07515cd4b34b3e653174810

# Sol P1 and RL-172 (a): before the KIT and OUT exist, so a WAIT here is retried cleanly at the next activation
effective_close || { echo "STOP: the receipt census failed; mail the lead"; exit 1; }
copy_gate || exit 1
# The kit: from PR #789's bbd34dc87 (same blob at the branch head 2a8deb7b9), OUTSIDE the checkout, sha asserted
mkdir -p /Users/edr/campaign-out/kits
KIT=/Users/edr/campaign-out/kits/cl-hp-01-bbd34dc87.json
test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"
git -C /Users/edr/code/JouleWise show bbd34dc876001786c3603d9c4583391639284253:docs/process/cadence/kits/cl-hp-01.json > "$KIT"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = 7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965 || { echo "STOP: kit sha"; exit 1; }
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"
# must print ok true, campaign_id cl-hp-01, frozen_commit dd206025abb30fd5c07515cd4b34b3e653174810,
# frozen_paths_verified true, kit_sha256 7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965, legs 12

# Output root outside every v4 registration and custody root
OUT=/Users/edr/campaign-out/cl-hp-01/cq-hp-01-s03-a1-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')
test ! -e "$OUT" || { echo "STOP: OUT exists"; exit 1; }
case "$OUT" in */restricted/*|*/night-*|*/jw-b5-*|"$REPO"/*|*/configs/campaigns/align_v4*) echo "REFUSE OUT"; exit 1;; esac

# measurement_mode (RL-149 §2.4 campaign-scope stop; RL-150 §2 F5): record every FAIL/WARN line
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify; echo "verify rc $?"
# RULE (lead, RL-150 F5 line): proceed only if every FAIL line is the "agent process present" line and every PID it names is
# in MAGISTRATE_PID's own process tree (record the lines); ANY other FAIL line: STOP, mail the lead. WARN lines are recorded, not gates.
sudo -n systemsetup -getusingnetworktime                 # must say Off
# RL-172 (h): the OS daily batch time computed from the boot time (boot + 12 h + 48 s, then every 24 h). PRINT ONLY: it gates nothing
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*$/\1/')"
case "$BOOT" in
  ''|*[!0-9]*) echo "batch print: kern.boottime unreadable";;
  *) NEXT_BATCH=$((BOOT + 43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH + 86400)); done
     echo "boot $(date -r "$BOOT" '+%Y-%m-%d %H:%M:%S %Z'); next OS batch $(date -r "$NEXT_BATCH" '+%Y-%m-%d %H:%M:%S %Z') (boot + 12 h + 48 s + whole days)";;
esac      # record this line in the arm record
# kernel frequency word: read it as item 308 did; must be 0 (else item 251's remedy, then re-read)
test ! -e "$CUSTODY/desk_fence.json" || { cat "$CUSTODY/desk_fence.json"; echo "STOP: live fence"; exit 1; }
sudo -n -l /bin/kill >/dev/null; echo "sudo kill rc $?"  # must be 0
pgrep -fl 'b6_r12|r12' || echo "no r12"
pgrep -fl 'claude|codex|mcp-server|mcp_server|modelcontextprotocol' | grep -v "^$MAGISTRATE_PID " || echo "no other agent"
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo "no stray monitor"
pgrep -u root -fl powermetrics || echo "no root powermetrics"
launchctl list | grep -E 'com\.joulewise\.(night|align-r0)' || echo "no night/smoke agent"
pmset -g | grep -i powermode                              # 0
"$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO"     # ac_power true

# High Power preflight (design doc §13.2.1; record every line)
test -z "${JOULEWISE_HOST_STATE_DIR:-}" || { echo "STOP: JOULEWISE_HOST_STATE_DIR is set"; exit 1; }
HP_MARKER=/Users/Shared/JouleWise/host-power/high-power.marker
{ test ! -e "$HP_MARKER" && test ! -L "$HP_MARKER"; } || { echo "STOP: High Power marker present; do NOT run restore-owed; mail the lead"; exit 1; }
"$PY" -B -c 'from joulewise.align.apple import powermode as p; v = p.observe_ac_powermode(); print("pmset -g custom AC powermode", v); raise SystemExit(0 if v == 0 else 1)' \
  || { echo "STOP: AC powermode is not 0"; exit 1; }
SUDO_LIST="$(sudo -n -l 2>&1)"
for c in '/usr/bin/pmset -c powermode 0' '/usr/bin/pmset -c powermode 2'; do
  case "$SUDO_LIST" in *"$c"*) echo "sudo rule listed: $c";; *) echo "STOP: sudo rule missing: $c"; exit 1;; esac
done
lsof -- /Users/Shared/JouleWise/host-power/night.lock 2>/dev/null && { echo "STOP: the host night lock has a holder"; exit 1; } || echo "night.lock: no holder"

# The plan (record it whole; batch_windows must be ["$ARG"])
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs L008,L009,L010,L011,L012 --batch-window "$ARG"
# expect legs L008 L009 L010 L011 L012, budget_s 1251 each, expected_s 9405, worst_case_s 22050, blackout_clear true
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+23510)')"
```

NOTE 1 (ADOPTED by the lead; the rule is in the verify line above). `measurement_mode.zsh verify` fails a line "agent process present" for ANY `claude`/`codex`/MCP process (`pgrep -x claude`), which includes this magistrate. While the magistrate runs, verify cannot print "verify OK". Rule: proceed only if every FAIL line is that one agent line and the PIDs it names are the magistrate's own process tree (record the lines); any other FAIL means STOP. WARN lines (battery limit syntax, softwareupdate schedule) are recorded, not gates.

NOTE 2 (ADOPTED by the lead: the fence root stays the watchdog's; all campaign data under OUT). `--custody-root` is the watchdog's fence root (`/Users/edr/night-custody/magistrate`): the launcher writes the fence, the plist, `runner.json` and the LaunchAgent logs there, as every R1 smoke did. All campaign data (soak, legs, receipt, desk bundle) go under OUT.

**Run (your last action):**

```sh
WORST_S=22050
# HOST GATE, immediately before the launch (P1-1). This is separate from the campaign dependency above: it reads the
# latest close of ANYTHING on this host (campaign span, Part C or F0, slot session, W1), not only this item's predecessor.
: "${HOST_RESTORE_OK:?Set to 1 only if the Check of the latest close of anything on this host reported every restore line OK}"
: "${OTHER_CLOSE_EPOCH:?Set to the close epoch (whole seconds, rounded up) of the latest run whose receipt is outside campaign-out and jw-wt/*/.desk (a slot session or W1), or an explicit 0}"
test "$HOST_RESTORE_OK" = 1 || { echo "STOP: the latest close's restore is not proven (restore unproven holds everything); mail the lead"; exit 1; }
test ! -e "$CUSTODY/desk_fence.json" || { echo "STOP: a desk fence is up"; exit 1; }
launchctl list | grep -qE 'com\.joulewise\.(night|align-r0)' && { echo "STOP: a night or smoke agent is loaded"; exit 1; }
{ test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || { echo "STOP: High Power marker"; exit 1; }
case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) or an explicit 0"; exit 1;; esac
# The receipt census: every runner_receipt.json at depth <= 4 under both roots, fractional recorded close epochs, ROUNDED UP.
# Any lookup error, a missing root, or no receipt at all STOPS: missing evidence never becomes 0 (Sol re-check 2, 3).
effective_close || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; exit 1; }
HOST_LAST_CLOSE=$EFF_EPOCH    # the effective close (max of the census and OTHER_CLOSE_EPOCH), computed once (Sol confirm P1)
echo "host last close $HOST_LAST_CLOSE"
copy_gate || exit 1
test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval ($GAP s) after the latest close of anything on this host (RL-171 §6.1)"; exit 1; }
# R1 RESERVATION, fresh at the launch (RL-165 §7; RL-155 R-A; P1-2). Re-read the staged items and RUN_STATE now.
: "${SESSION_READY:?Set to yes if the lead has recorded a v4 session (R1 or W1) as READY, else no (RL-172 (f))}"
test "$SESSION_READY" = no || { echo "CEDE: a READY v4 session takes the next clean close (RL-172 (f); RL-155 R-A); do not launch; mail the lead"; exit 1; }
# RL-172 (f): RL-165 §7's worst-case reservation (launch + worst + 1,200 s <= SESSION_T0) is retired.
# The band and the campaign dependency, last of all
NOW=$(date +%s); test "$(pick_arg "$NOW")" = "$ARG" \
  || { echo "STOP: the clock left ARG $ARG's band (or this item's window) since Start and check; do not launch; mail the lead (a re-issue or a re-plan): the argument chosen in Start and check no longer belongs to the launch time"; exit 1; }
test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval after the prior span's close"; exit 1; }
{ test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || { echo "STOP: marker"; exit 1; }
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" \
  --kit "$KIT" --legs L008,L009,L010,L011,L012 --batch-window "$ARG" \
  --output "$OUT" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"; date +%s    # t0: the lead's alarm is t0 + 22,050 s (worst-case end) and t0 + 23,510 s (fence end)
```

Require exit 0, `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`), and the launch output's `plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check (else report it; the span is not counted until the lead rules). The launcher itself refuses a deadline under the plan's worst case plus reserves, a missing kit and malformed `--legs` / `--batch-window`. Record ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), the batch-time print, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, OUT, DEADLINE, HOST_RESTORE_OK, OTHER_CLOSE_EPOCH, the host last close printed, SESSION_READY, the launch time (t0), the measurement_mode lines, the High Power preflight lines, the preflight sudo read and the plan in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/cadence-hp01-s03-out-<activation>.txt`, (the lead's watcher reads t0 from it for the alarm). Then exit at once, with no other `claude` or `codex` process running.

**Check (next activation, after the fence is gone).** Run the magistrate's own power reads FIRST, so they stand even if a receipt assert fails:

```sh
cd /Users/edr/code/jw-wt/cadence-hp01-s03      # the same checkout at dd206025a (D4: restore-owed exists only at or after it)
test ! -e "$CUSTODY/desk_fence.json"; launchctl list | grep -c 'com.joulewise.align-r0' || true   # expect 0
HP_MARKER=/Users/Shared/JouleWise/host-power/high-power.marker
"$PY" -B -c 'from joulewise.align.apple import powermode as p; print("pmset -g custom AC powermode", p.observe_ac_powermode())'   # must be 0
{ test ! -e "$HP_MARKER" && test ! -L "$HP_MARKER"; } && echo "no High Power marker" || echo "HIGH POWER MARKER PRESENT"
lsof -- /Users/Shared/JouleWise/host-power/night.lock 2>/dev/null || echo "night.lock: no holder"
pmset -g | grep -i powermode                                            # 0
sudo -n systemsetup -getusingnetworktime                                # Off
# kernel frequency word: 0 (item 251 remedy if not)
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo "no stray monitor"
pgrep -u root -fl powermetrics || echo "no root powermetrics"
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify; echo "verify rc $?"   # record lines (NOTE 1 applies)
```

**Maintenance line, after the power reads (RL-171 §5 item 1; as item 331). Print only: it gates nothing and is not a stop.** Set `ARG` to the batch-window argument recorded at the arm (`export ARG=...`); the receipt assert below compares with it. Then one read-only system-log query over the span's interval (from OUT's UTC launch stamp to the receipt's mtime) for the OS maintenance processes, saved BESIDE the journals as `$OUT/maintenance-log.txt`, plus a per-10-minute count printed for the report. Report the counts and which legs' intervals they overlap (from each `leg_summary.json`'s start and end, if present; else say "overlap left to the desk"). A leg hit by a maintenance job is judged by rule 5 as before (RL-171 §2 item 2). With `13:14-13:15` a leg may run through 02:00-02:35 (dasd about 02:08; XProtect to about 02:28): that is the case rule 5 exists for (one redo of about 21 min, quota 2).

```sh
: "${ARG:?Set ARG to the batch-window argument recorded at the arm}"; export ARG
START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\1/')"
START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")"
END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')"
echo "maintenance window $START_LOCAL .. $END_LOCAL"
sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \
  --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd"}' \
  > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err"; echo "log show rc $?"
wc -l < "$OUT/maintenance-log.txt"
# per 10-minute bucket and process: "HH:M0 process count"
awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
```


Then the receipt. It asserts `restore_proven` true in `span/result.json` and in the receipt's `span_result`, the close proof (`high_power.close_proof`: `proven` true, `ac_powermode` 0, `host_marker_present` false, `pmset_error` null, the production marker path), `restore.ok` true and every power step rc 0. It prints the D1 lines (`high_power.revoked`, `high_power.before_restore`) before any assert:

```sh
"$PY" -I -B - "$OUT" L008,L009,L010,L011,L012 /Users/Shared/JouleWise/host-power/high-power.marker <<'PY'
import hashlib, json, sys
from pathlib import Path
root, roster, marker = Path(sys.argv[1]), sys.argv[2].split(","), sys.argv[3]
KIT_SHA = "7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965"
FROZEN = "dd206025abb30fd5c07515cd4b34b3e653174810"
r = json.loads((root / "runner_receipt.json").read_text())
print(json.dumps({k: r.get(k) for k in ("rc", "runner_kind", "roster", "batch_windows", "legs_planned",
                                        "legs_finished", "load_redos_used", "span_result", "meter", "error",
                                        "late_signals")}, sort_keys=True))
print([(s["name"], s["rc"]) for s in r["steps"]])
hp = r.get("high_power") or {}
# D1: the withdrawal and the last look are printed BEFORE any assert, so a failed assert still shows them
print("high_power.revoked", json.dumps(hp.get("revoked")))
print("high_power.before_restore", json.dumps(hp.get("before_restore"), sort_keys=True))
print("high_power.restore", json.dumps(hp.get("restore"), sort_keys=True))
print("high_power.close_proof", json.dumps(hp.get("close_proof"), sort_keys=True))
bundle = root / "desk-bundle"
result = json.loads((bundle / "span/result.json").read_text())
print("result", json.dumps(result, sort_keys=True))
assert r["runner_kind"] == "cadence-legs-v1" and r["roster"] == roster
assert r.get("mock") is False
assert r["kit"]["sha256"] == KIT_SHA and r["kit"]["campaign_id"] == "cl-hp-01"
assert r["kit"]["frozen_commit"] == FROZEN
assert r["batch_windows"] == [__import__("os").environ["ARG"]], r["batch_windows"]   # ARG as recorded at the arm (RL-171)
names = [s["name"] for s in r["steps"]]
for once in ("soak", "frozen", "host_lock", "high_power_marker_absent", "powermode_guard", "high_power",
             "power_last_look", "restore", "power_proof", "host_lock_release"):
    assert names.count(once) == 1, (once, names.count(once))
assert all(s["rc"] == 0 for s in r["steps"] if s["name"] in (
    "frozen", "condition13", "host_lock", "high_power_marker_absent", "read_power", "powermode_guard", "soak",
    "high_power", "power_last_look", "restore", "power_proof", "host_lock_release")), "a power or preflight step rc != 0"
# The High Power close (RL-155 §5.2; design doc §13.2.1): restore proven, the close proof, no marker
assert hp.get("block_power_mode") == 2
assert hp.get("host_marker") == marker, hp.get("host_marker")
cp = hp.get("close_proof") or {}
assert cp.get("proven") is True and cp.get("ac_powermode") == 0 and cp.get("host_marker_present") is False \
    and cp.get("pmset_error") is None and cp.get("host_marker") == marker, cp
assert (hp.get("restore") or {}).get("ok") is True, hp.get("restore")
assert result.get("restore_proven") is True, result
assert (r.get("span_result") or {}).get("restore_proven") is True
for name, feed in r["feeds"].items():
    assert feed["stop"]["proven_stopped"]
    if name == "meter":
        continue   # RL-150 R8: only the runner hashes KM003C stream files; the magistrate does not open them
    for f in feed["files"]:
        with (root / f["path"]).open("rb") as h:
            assert hashlib.file_digest(h, "sha256").hexdigest() == f["sha256"]
files = sorted(p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file())
assert files == [f"legs/{x}/leg_summary.json" for x in roster] + ["span/meter.json", "span/result.json"], files
revoked = {e["leg_id"] for e in (hp.get("revoked") or [])}
for leg in roster:
    s = json.loads((bundle / "legs" / leg / "leg_summary.json").read_text())
    rec = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    mode = (rec.get("result") or {}).get("ac_powermode")
    # D1: admitted is read from the leg summary, never recomputed from the leg record (a withdrawn leg's record
    # still says ac_powermode 2). RL-157 §5's print: g0_s, wall_s, budget_s.
    print(leg, "admitted", s.get("admitted"), "revoked", leg in revoked, "leg_record.ac_powermode", json.dumps(mode),
          "g0_s", s.get("g0_s"), "wall_s", s.get("wall_s"), "budget_s", s.get("budget_s"),
          "over_1.5x", (s.get("wall_s") or 0) > 1.5 * (s.get("budget_s") or 0))
    print(leg, json.dumps(s, sort_keys=True))
print("meter", (bundle / "span/meter.json").read_text().strip())
clean = (r["rc"] == 0 and r["legs_finished"] == len(roster) and not revoked and result.get("restore_proven") is True)
print("RECEIPT OK" if clean else "RECEIPT NOT CLEAN: report in full")
PY

# RL-157 §1 print (gates nothing): seconds from the `high_power` step's end (stage journal) to L008's G0 start
# (the G0 gate row's entry_epoch_s in L008's outputs/align_thermal.jsonl).
"$PY" -I -B - "$OUT" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
rows = [json.loads(line) for line in (root / "chain-stages.jsonl").read_text().splitlines()]
ends, starts = {}, {}
for d in rows:
    (ends if d.get("event") == "end" else starts).setdefault(d["stage_id"], d)
hp_end = (ends.get("high_power") or {}).get("ended_epoch_s")
soak_end = (ends.get("soak") or {}).get("ended_epoch_s")
rec = json.loads((root / "legs" / "L008" / "leg_record.json").read_text())
n = len(rec.get("attempts") or [])
leg_start = (starts.get(f"L008.a{n}") or {}).get("started_epoch_s")
g0_entry = None
bname = (rec.get("result") or {}).get("bundle")
if bname:
    p = root / "legs" / "L008" / "runtime" / bname / "outputs" / "align_thermal.jsonl"
    if p.is_file():
        for line in p.read_text().splitlines():
            d = json.loads(line)
            g = (d.get("values") or {}).get("gate") or {}
            if d.get("module") == "temperature" and d.get("kind") == "align_thermal_gate" and g.get("kind") == "G0":
                g0_entry = g.get("entry_epoch_s"); break
def diff(a, b):
    return None if a is None or b is None else round(a - b, 1)
print("RL-157 §1", json.dumps({"soak_end_epoch_s": soak_end, "high_power_end_epoch_s": hp_end,
      "L008_attempts": n, "L008_attempt_start_epoch_s": leg_start, "L008_g0_entry_epoch_s": g0_entry,
      "soak_end_to_mode_set_s": diff(hp_end, soak_end),
      "mode_set_to_L008_attempt_start_s": diff(leg_start, hp_end),
      "mode_set_to_L008_G0_start_s": diff(g0_entry, hp_end)}, sort_keys=True))
PY

# RL-150 R1 part 3 print (gates nothing): soak reference; each leg's own reference; its G0 release reading;
# TV0h, TV1h, Tf08. Thermal journal values only: soak_reference.json, the soak's sensors journal,
# each leg's outputs/align_window_reference.json and outputs/align_thermal.jsonl. Nothing else is opened.
"$PY" -I -B - "$OUT" <<'PY'
import json, statistics, sys
from pathlib import Path
root = Path(sys.argv[1])
KEYS = ("TV0h", "TV1h", "Tf08")
def rows(path):
    out = []
    for line in path.read_text().splitlines():
        d = json.loads(line)
        if d.get("module") == "temperature" and d.get("kind") in ("reading", "align_thermal_gate"):
            out.append(d)
    return out
def reading(d):
    return d["started"]["monotonic_ns"], (d["values"].get("sensors") or {})
soak = json.loads((root / "soak" / "soak_reference.json").read_text())
sj = [reading(d) for d in rows(root / "soak" / "idle_soak" / "sensors" / "align_thermal.jsonl") if d["kind"] == "reading"]
end = sj[-1][0]
tail = [s for t, s in sj if t > end - 1200 * 10**9]
tf08 = [s["Tf08"] for s in tail if isinstance(s.get("Tf08"), (int, float))]
print("soak_reference", {k: soak["sensors_c"].get(k) for k in ("TV0h", "TV1h")},
      "Tf08_last1200s_mean", statistics.fmean(tf08) if tf08 else None)
for leg in ("L008", "L009", "L010", "L011", "L012"):
    rec = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    bname = (rec.get("result") or {}).get("bundle")
    if not bname:
        print(leg, json.dumps({"no_bundle": True, "leg_status": rec.get("leg_status")})); continue
    out = root / "legs" / leg / "runtime" / bname / "outputs"
    j = rows(out / "align_thermal.jsonl")
    reads = [reading(d) for d in j if d["kind"] == "reading"]
    ref = json.loads((out / "align_window_reference.json").read_text())
    lo, hi = ref["span_ns"]
    ref_tf08 = [s["Tf08"] for t, s in reads if lo <= t <= hi and isinstance(s.get("Tf08"), (int, float))]
    g0 = next((d["values"]["gate"] for d in j if d["kind"] == "align_thermal_gate"
               and d["values"].get("gate", {}).get("kind") == "G0"), None)
    at = next((s for t, s in reads if g0 and t == g0.get("exit_sample_ns")), {})
    print(leg, json.dumps({
        "own_reference": {"status": ref["status"], "TV0h": ref["fast_c"], "TV1h": ref["slow_c"],
                          "Tf08_median": statistics.median(ref_tf08) if ref_tf08 else None},
        "g0": None if g0 is None else {"outcome": g0["outcome"], "duration_s": g0["duration_s"],
                                       "row_reference": g0.get("reference"), "row_release": g0.get("release"),
                                       "release": {k: at.get(k) for k in KEYS}}}, sort_keys=True))
PY
```

The receipt also carries the runner's own close steps (`power_last_look`, `restore`, `power_proof`, `host_lock_release`, `stop-*`, `close-*`); report them as the restore lines. Do not open `hazards/`, any `stream-*.jsonl`, any `powermetrics*` file or any `align_episode.json`.

**Restore owed (Mythos D4 and D3; design doc §13.2.1, §13.2.3).** Only if the Check shows AC powermode not 0, or a marker present, or no receipt / no `span/result.json`:
- **When it is safe (all must hold; record each):** the span's LaunchAgent job has exited (`launchctl list | grep -c com.joulewise.align-r0` prints 0) and its desk fence is gone or stale; no other span, session or night is running or loaded (no `desk_fence.json` under `$CUSTODY`, no `com.joulewise.(night|align-r0)` job: an Automatic span or a plan-0 night holds no lock, so the command cannot see one, D3); `lsof` shows no holder of `night.lock`; the marker's owner names this span (`head -c 4000 "$HP_MARKER"`: R1 crash tag, `writer` `cadence span`, `campaign_id` `cl-hp-01`, `output` = `$OUT`). If the marker is a W1 session's, or names anything else, do NOT run it: mail the lead.
- **The command (D4: from a checkout at or after `dd206025a`; this span's own worktree is one. The dev-01 and dev-02 worktrees at `b4b6aeb19` have no `restore-owed` and exit 2 on usage):**
  ```sh
  cd /Users/edr/code/jw-wt/cadence-hp01-s03 && "$PY" -B scripts/cadence_legs_runner.py restore-owed; echo "restore-owed rc $?"
  ```
  It takes the host night lock without waiting (it defers if anything holds it), runs the narrow rule's `pmset -c powermode 0`, reads 0 back, removes the marker only then, refuses a W1 session's marker, and exits 0 only when powermode 0 and no marker read back. Never a bare `sudo pmset`, never outside the lock. Then read `pmset -g custom` and the marker path again by hand and record both.
- Whatever it prints, RESTORE_UNPROVEN stays open and nothing arms: mail the lead. Only the lead clears the stop, with a RUN_STATE line (and, for an unproven leg child, under RL-157 §2 condition 2).

**Report** (by email to Ed and the lead, and as RUN_STATE TBD+1):
- the magistrate's own power reads (AC powermode, marker present or not, `night.lock` holder) and, if run, the restore-owed output with its "when safe" lines;
- the ARG used, the journal-copy line and the batch-time print from the arm; the maintenance line's counts and the legs they overlap;
- the receipt line, the step list and RECEIPT OK (or the receipt in full if not clean);
- **D1:** each leg's `admitted` from its `leg_summary.json` (never from the leg record), the receipt's `high_power.revoked` and `high_power.before_restore`, as printed;
- each leg's `leg_summary.json` line; `span/result.json` (with `restore_proven`) and `span/meter.json`;
- legs run and admitted (of 5); for any excluded leg, the rule it fell under (from `g0_outcome`, `contaminated_redos`, `leg_status`/decode cap, the leg's `ac_powermode`, and `high_power.revoked`); whether any named stop would fire (the Air desk builds `stops.json` from the bundle);
- whether two legs ran over 1.5 × `budget_s` (LEG_OVERTIME: goes to the RESEARCH LEAD, RL-157 §5);
- the RL-157 §1 print (L008) and the RL-150 R1 print, as printed;
- the restore lines and the measurement_mode verify lines; the receipt's close epoch;
- whether the span crossed 00:00 (the `/private/tmp` walk; not a gate).

The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).**
- **The journal copy:** copy this span's journals to the Air by SSH (never while a fence is up), hash-verify them, then write `/Users/Shared/JouleWise/desk-copy/cq-hp-01-s03-a1.ok` (the copy manifest's sha256 and the `date` stamp). The next campaign arm waits for it.
- **The Air desk (D6):** copy the desk bundle to `/Volumes/JW-EXT/cadence-desk/cq-hp-01-s03-a1/input` and build the table from a checkout at or after `dd206025a`, WITH the kit (never `--adapter`, which leaves RESTORE_UNPROVEN inert). Record the desk FINAL; line 9 needs it for campaign span 8.
- **D1's second line:** any `high_power.revoked` entry holds the next arm until the research lead rules, as a REFUSAL would. LEG_OVERTIME goes to the research lead.
- **Next (RL-165 §2):** the dev-02 pull (`dev-02-s02`, Sunday), then the standing F0. Move `hp-01` in BLOCK-QUEUE to COLLECTED (12 legs), then DESK_FINAL when this desk is final.
