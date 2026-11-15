"""ITEM-hp01-s02.md and ITEM-hp01-s03.md: the hp-01 remainder (mirror 4 + 5), built on the RL-171/RL-172 hp-01 smoke item
(run after tools/rl172.py). The script blocks are the smoke's with this span's roster, bands, worst case and plan id."""
import sys, re
sys.path.insert(0, "/Volumes/JW-EXT/scratch/items-rl171/tools")
from common import count_sub
D = "/Volumes/JW-EXT/scratch/items-rl171"
src = open(f"{D}/ITEM-hp01-s01.md").read()
BODY = src[src.index("**Start and check (while you are still alive).**"):src.index("**Report** (by email to Ed and the lead")]
QSHA = "01687bb7b1206c82657ff018130f8761f249b64b5fa6524f4b3914d0c81a00a5"
SPANS = {
 "s02": dict(legs="L004,L005,L006,L007", n=4, W=19350, DL=20810, exp=8154, lim=1794884850, lim_local="19:07:30",
             fc=("Sun 05:16:48 (the smoke's expected close 04:56:48 + a 20-min hand-read)", "02:00-02:35", "07:32:42", "10:39:18", "11:03:38"),
             span_no=5, line9="span 3's desk, `dev-01-s04` (`cq-dev-01-s04-a1`)", prior="hp-01-s01 (the smoke)", ptr="2026-11-17T01:55:00-08:00"),
 "s03": dict(legs="L008,L009,L010,L011,L012", n=5, W=22050, DL=23510, exp=9405, lim=1794882150, lim_local="18:22:30",
             fc=("Sun 07:37:42 (hp-01-s02's expected close 07:32:42 + 5 min)", "02:00-02:35", "10:14:27", "13:45:12", "14:09:32"),
             span_no=6, line9="span 4's desk, the smoke `hp-01-s01` (`cq-hp-01-s01-a1`)", prior="hp-01-s02", ptr="2026-11-17T01:55:00-08:00"),
}
for key, c in SPANS.items():
    span = f"hp-01-{key}"; legs = c["legs"]; first = legs.split(",")[0]; tup = ", ".join(f'"{x}"' for x in legs.split(","))
    PICK = open(f"{D}/plans/bands/hp01-{key}.sh").read().rstrip("\n")
    s = BODY
    s = count_sub(s, "/Users/edr/code/jw-wt/cadence-hp01-s01", f"/Users/edr/code/jw-wt/cadence-hp01-{key}", 5)
    s = count_sub(s, "not another smoke worktree, not a dev-01 worktree at `b4b6aeb19`", "not another smoke worktree, not the smoke's own worktree `cadence-hp01-s01` (a fresh one, as every span), not a dev-01 worktree at `b4b6aeb19`", 1)
    s = count_sub(s, ': "${PRIOR_CLOSE_EPOCH:?Set to the later of dev-01-s04 runner_receipt ended.epoch_s and the epoch its desk fence was seen gone (or the R1 slot session close, if it ran first)}"',
                  f': "${{PRIOR_CLOSE_EPOCH:?Set to the later of {span.replace("s03", "s02") if key == "s03" else "hp-01-s01"} runner_receipt ended.epoch_s and the epoch its desk fence was seen gone (or the R1 slot session close, if it ran first)}}"', 1)
    s = count_sub(s, s[s.index("# The launch bands (EARLIEST"):s.index("  else echo NONE; fi\n}") + len("  else echo NONE; fi\n}")],
                  f"# The launch bands (Sun 00:30:01 to Mon {c['lim_local']}: the v1 bands of this pin cut by the 00:30 rule (worst-case end by the next 00:30); none 10:50:01-13:14:59)\n" + PICK, 1)
    s = count_sub(s, "--legs L001,L002,L003", f"--legs {legs}", 2)
    s = count_sub(s, "# expect legs L001 L002 L003, budget_s 1251 each, expected_s 6903, worst_case_s 16650, blackout_clear true",
                  f"# expect legs {legs.replace(',', ' ')}, budget_s 1251 each, expected_s {c['exp']}, worst_case_s {c['W']}, blackout_clear true", 1)
    s = count_sub(s, "print(time.time()+18110)", f"print(time.time()+{c['DL']})", 1)
    s = count_sub(s, "WORST_S=16650", f"WORST_S={c['W']}", 1)
    s = count_sub(s, "the lead's alarm is t0 + 16,650 s (worst-case end) and t0 + 18,110 s (fence end)",
                  f"the lead's alarm is t0 + {c['W']:,} s (worst-case end) and t0 + {c['DL']:,} s (fence end)", 1)
    s = count_sub(s, "cq-hp-01-s01-a1", f"cq-hp-01-{key}-a1", None) if "cq-hp-01-s01-a1" in s else s
    s = count_sub(s, "cadence-hp01-s01-out", f"cadence-hp01-{key}-out", 1)
    s = count_sub(s, '"$OUT" L001,L002,L003 /Users/Shared', f'"$OUT" {legs} /Users/Shared', 1)
    s = count_sub(s, 'for leg in ("L001", "L002", "L003"):', f"for leg in ({tup}):", 1)
    # RL-157 §1's print is the smoke's (mode set to L001's G0 start); here it reads this span's first leg
    s = s.replace("to L001's G0 start", f"to {first}'s G0 start").replace("in L001's outputs/align_thermal.jsonl", f"in {first}'s outputs/align_thermal.jsonl")
    s = s.replace('root / "legs" / "L001"', f'root / "legs" / "{first}"').replace('f"L001.a{n}"', f'f"{first}.a{{n}}"')
    s = s.replace('"L001_attempts"', f'"{first}_attempts"').replace('"L001_attempt_start_epoch_s"', f'"{first}_attempt_start_epoch_s"')
    s = s.replace('"L001_g0_entry_epoch_s"', f'"{first}_g0_entry_epoch_s"').replace('"mode_set_to_L001_attempt_start_s"', f'"mode_set_to_{first}_attempt_start_s"')
    s = s.replace('"mode_set_to_L001_G0_start_s"', f'"mode_set_to_{first}_G0_start_s"')
    assert "L001" not in s and "L002" not in s and "L003" not in s, [l[:100] for l in s.split("\n") if re.search("L00[123]", l)][:5]
    assert "16650" not in s and "18110" not in s
    head = f"""TBD. **Laptop lead (interactive, Opus 5.5), drafted under RL-171 and RL-172 by the items-rl171 builder 2026-11-15 PST (new draft on the hp-01 smoke item; the hp01-ready builder's mirror append), ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm hp-01's {"SECOND" if key == "s02" else "THIRD"} span (RL-157 §3, §8; RL-165 §5 to §7; RL-171; RL-172): kit `cl-hp-01`, legs {", ".join(legs.split(","))} only, span `{span}`, runner kind `cadence-legs-v1`, on `dd206025abb30fd5c07515cd4b34b3e653174810` checked out detached in a fresh scratch worktree. One span: a fresh soak in Automatic, then AC powermode 2 (High Power) set by the runner, then {c['n']} type-H legs (type A in High Power: 19,458-token step prompt, decode cap 4,096, band q0), then the close restores Automatic and proves it. They are counted type-H legs of hp-01; hp-01 is description only, never in the fit. No other span, no queue extension, no session, no W1. EARLIEST: the close interval after `{c['prior'].split(' ')[0]}` closed with its fence gone (RL-171 §6.1; 300 s, RL-172 §0) and every gate below holds, and not before 00:30:01 PST Sun 15 Nov (epoch 1794731401). LAUNCH as soon as every gate holds, at any hour, up to {c['lim_local']} PST Mon 16 Nov (LIMIT, epoch {c['lim']}), with the worst-case end by the next 00:30 (RL-165 §7, kept by RL-171 §2; the small hours allowed while the lead is present, RL-172 §0): so not from Sun {c['lim_local']} to Mon 00:30:00, and never 10:50:00-13:15:00 (this pin's soak path waits out 11:45-13:15 unbudgeted). The batch-window argument follows the launch time (RL-171 §3): `13:14-13:15` from 00:30:01 to 02:34:59, `02:00-02:35` from 02:35:00. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies, RL-165 §3).**

```pointer
owner: magistrate
wait: none
deadline: {c['ptr']}
on_early_or_refused: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), a High Power marker or a held host night lock at the arm, or a launch that cannot happen inside the bands below (Sun 00:30:01 to Mon {c['lim_local']} PST, outside the 00:30 rule's evening cut and 10:50:00-13:15:00): NOTHING of this item launches; mail the lead (a later t0 needs a re-issued item). The standing F0 item's refusal rule then applies, unless the stop is RESTORE_UNPROVEN or a host-state stop, which hold everything. A span that ran but ends with any named stop, a receipt rc≠0, restore_proven not true, a High Power marker present or AC powermode not 0 at the Check: nothing relaunches, nothing is re-run, nothing else arms (RESTORE_UNPROVEN holds everything, F0 included); run restore-owed ONLY under "Restore owed" below; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the magistrate's own power reads (AC powermode 0, no marker, no lock holder), the maintenance line, the receipt asserts with restore_proven and the close proof, the D1 lines (admitted per leg, high_power.revoked, high_power.before_restore), the desk bundle, the restore lines, measurement_mode verify again, the RL-157 §1 and §5 prints and the RL-150 R1 start-reference print (none of the prints gates)
```

- **Why.** hp-01's remainder runs after the smoke passed and the lead's hand-read (RL-150 R5; RL-157 §3, §8). `dev-01-s03` ran L004-L007 and `dev-01-s04` L008-L012, so hp-01 mirrors them: `hp-01-s02` L004-L007, then `hp-01-s03` L008-L012 (RL-157 §3, the mirror file `QUEUE-cl-hp-01-dd206025a-append-mirror-4plus5.json`). **Order (RL-165 §1, §2):** on Sunday after `dev-01-s04`: the R1 slot session if READY, then hp-01's spans, then the dev-02 pull, then F0; on Monday after dev-02 closes: the slot session if READY, then the dev-03 pilot, then hp-01's unrun spans, then P, then F0. A leg's calendar day is the local date of its span's t0.
- **Day law (RL-172 (a)).** hp-01 is outside the development-leg count ((a) rule 4), so no `day_gate` runs here; (a) sets no date for hp-01. RL-149 §2.3 gives hp-01 "any day after dev-01".
- **Gate.** All of:{'''
  - **The smoke (`hp-01-s01`) closed and checked:** <LEAD FILLS: RUN_STATE <n>: RECEIPT OK, 3 legs run and admitted of 3, restore_proven true, close proof proven, no named stop open, no `high_power.revoked` entry, close epoch>.
  - **The smoke passed and the lead's hand-read is recorded (RL-150 R5, R9 with rule 6 meaning High Power; RL-157 §1, §5; Mythos D1, D5):** <LEAD FILLS: R9's four conditions VERDICT PASSED, the hand table and the automatic desk agree (inclusion included), the restated remainder time; where recorded>. **D1's second line:** any `high_power.revoked` entry holds this span until the research lead rules. **LEG_OVERTIME** on the smoke goes to the research lead before this span arms (RL-157 §5).
  - **Line 2's exception is closed (RL-165 §5):** the finished CI run on `2a8deb7b9`, `ci` 43673985768, shows the base set plus 0: the same 12 reds as `fe907d0d3`'s run 43600776368, test for test (confirmed by the lead, 11-15). This item does not arm on run 43664752637's base + 1.
  - **Line 9:** this span is campaign span 5, so ''' + c['line9'] + ''' must be FINAL.
  - **The mirror append is committed** on audit/2026-11-10-fable (line 3; the lead commits it when this span is READY).''' if key == "s02" else '''
  - **`hp-01-s02` closed clean:** <LEAD FILLS: RUN_STATE <n>: RECEIPT OK, 4 legs run and admitted of 4, restore_proven true, close proof proven, no named stop open, no `high_power.revoked` entry (D1's second line holds this span until the research lead rules), no LEG_OVERTIME pending at the research lead, close epoch>.
  - **Line 9:** this span is campaign span 6, so ''' + c['line9'] + ''' must be FINAL.
  - Line 2 as `hp-01-s02`'s: run 43673985768 on `2a8deb7b9`, base + 0.'''}
  - Lines 5, 6 and 7 at the arm (below).
  - **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-172 (f)):** the Check of the latest close of ANYTHING on this host reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (300 s after a campaign close, RL-172 §0; 1,200 s after a Part C or F0, F2, a slot session or W1), from the receipt census that stops on a missing root, any lookup error or an empty result (or OTHER_CLOSE_EPOCH); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the lead's marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). From the lead's record that a v4 session is READY, nothing of lower priority arms and the session takes the next clean close (RL-172 (f)); RL-165 §7's worst-case reservation is retired.
- **Alarm (the lead's watcher, RL-165 §7).** At issue the lead arms an alarm at this span's worst-case end, t0 + {c['W']:,} s (at the forecast t0: {c['fc'][3]}; at the LIMIT: Tue 00:30:00), that fires if the fence is still up or no Check is reported, and a second at the fence end, t0 + {c['DL']:,} s. The magistrate records t0 so the lead can set it.
- **Counted.** The {c['n']} legs count as type-H legs of hp-01 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8, RL-157 §4): rule 6 is the block's mode, so a leg is admitted only if it recorded AC powermode 2 at its episode start and was not withdrawn. hp-01 has no reserve (RL-157 §4): an excluded type-H leg is not replaced.
- **Bytes, line 2 and condition 13:** as the smoke's item. Measured from `dd206025abb30fd5c07515cd4b34b3e653174810`; the kit is `cl-hp-01.json` from `bbd34dc87`, sha256 `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965`, copied outside the checkout (the in-tree kit at `dd206025a` is the superseded `bd7c8711…`). `dd206025a` has the v1 launcher (no fence check). `verify_r1_executed_sources` must return the full sha. No smoke of its own: the smoke was `hp-01-s01`.
- **What the runner does:** as the smoke's item (docs/process/cadence_queue_design.md §13 and §13.2 at `dd206025a`), with this roster: the host lock, the marker written first, `pmset -c powermode 2` read back, a powermode check before every attempt, per-leg load redo (quota 2), no leg starts inside the batch-window argument (`$ARG`), and the close's `power_last_look`, `restore`, `power_proof` and `host_lock_release`. It reads and writes no energy.
- **Timing.** Plan for this roster (`plan` at `dd206025a` with the argument of each band, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-hp01-{key}.txt`): expected {c['exp']:,} s, worst case {c['W']:,} s, budget_s 1,251 per leg; fence deadline launch + {c['DL']:,} s (worst case + 1,460 s).
  - **Bands (the `pick_arg` function below), Sun and Mon:** 00:30:01-02:34:59 `13:14-13:15`; 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-{c['lim_local']} `02:00-02:35`; none {c['lim_local']}-00:30:00 (the 00:30 rule; the bytes alone would admit `02:00-02:35` to {"20:37:30" if key == "s02" else "19:52:30"}). A mock span at t0 Mon 00:30 with `13:14-13:15`: rc 0, {c['n']} legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/hp01-{key}-alt-00:30/`; the mock does not model the 11:45-13:15 soak wait).
  - Forecast t0 {c['fc'][0]}, argument `{c['fc'][1]}`: expected end {c['fc'][2]}, worst end {c['fc'][3]}, fence end {c['fc'][4]} (`/Volumes/JW-EXT/scratch/items-rl171/plans/chain-new.txt`).
  - Pointer deadline = latest fence end (LIMIT + {c['DL']:,} s = Tue 00:54:20) + 1 h.
- **Conditions:** as the smoke's item: no agent session on the MBP during the span; the restore lines before the launch and in Check; the High Power preflight (`pmset -g custom` AC powermode 0, no marker file or link, both `pmset -c powermode 0` and `2` sudo rules listed, no `night.lock` holder, `JOULEWISE_HOST_STATE_DIR` unset); `--batch-window "$ARG"` and `--legs {legs}` written out on every `validate-kit`, `plan` and `launch`; the measurement_mode line; output root `/Users/edr/campaign-out/cl-hp-01/`. Quiet is the per-leg census and rule 5 (RL-171); there is no clock quiet.
- **RESTORE_UNPROVEN holds everything; RL-157 §2 condition 2; LEG_OVERTIME to the research lead; Blinding:** exactly as the smoke's item.
- **May run:** this span, once. **May NOT:** any other hp-01 span ({"`hp-01-s03`" if key == "s02" else "`hp-01-s02` again"}), any other campaign span, any session, W1, any filler, and `restore-owed` while this span is armed or its fence is live.
- **High Power marker at the arm:** if `/Users/Shared/JouleWise/host-power/high-power.marker` exists, STOP and report. Do not run `restore-owed` at the arm.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. As the smoke's line 1 (kit `cl-hp-01` `7eaf2660…d2965` on `dd206025a`; the Mythos cold and delta seats, the row-1 review, `validate-kit` and the `plan` below).
2. Line 2 in RL-165 §5's four parts, as the smoke's, **with the finished run:** CI `ci` 43673985768 on `2a8deb7b9` (frozen-path diff against `dd206025a` empty) has the same 12 reds as `fe907d0d3`'s run 43600776368, test for test: base + 0. Each of the 12 passes at #777's head (run 43601158271). The recorded diff against `b4b6aeb19` is the five High Power files; the two meter blobs are identical.
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-hp-01-dd206025a-append-mirror-4plus5.json` on audit/2026-11-10-fable at `<LEAD FILLS: commit; the lead commits it when hp-01-s02 is READY>`, sha256 `{QSHA}`: the committed one-span queue (`90e042ed…`, `3de39e06a`) with `hp-01-s02` (L004-L007) and `hp-01-s03` (L008-L012) appended, additions only, not_before 2026-11-15, `expires_at` 2026-11-21T23:59-08:00. `validate-queue` ok at `dd206025a` with `--kits-root` a checkout of `bbd34dc87` (kit `7eaf2660…`): plan ids `cq-hp-01-s01-a1`, `cq-hp-01-s02-a1`, `cq-hp-01-s03-a1` (`/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue-hp01.log`). Do NOT run `cadence_queue.py next`; this item names the span. The fallbacks in `/Volumes/JW-EXT/scratch/hp01-ready/queue/` (mirror 3 + 6, fallback 6 + 3, s02 nine legs) are not used.
4. `validate-kit` passes; OUT is outside every v4 registration and custody root (check below).
5. The per-span checks of design doc §4 and §13.2.1 pass at the arm and at the close. Do NOT run `cadence_queue.py checklist`.
6. No named stop, veto or halt open (the `directive` and `cadence-stop` issues; gh via `launchctl asuser`), no RESTORE_UNPROVEN open from any span or Part C run, and no `high_power.revoked` hold: <LEAD FILLS: span ids, their desk `stops.json` result and the time read>.
7. Results-ref watcher live within 24 h: <LEAD FILLS: heartbeat stamp, pid and commit>.
8. {"The smoke passed (R9 with rule 6 meaning High Power) and the lead's hand-read is recorded (Gate above)." if key == "s02" else "The smoke passed and `hp-01-s02` closed clean (Gate above)."}
9. Line 9, across blocks in run order (RL-165 §6). Expected: this span is campaign span {c['span_no']}, so {c['line9']} must be FINAL. As run: this span is campaign span <LEAD FILLS: N>, and the desk of the span two back, <LEAD FILLS: SPAN ID>, is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded>.

"""
    tail = f"""**Report** (by email to Ed and the lead, and as RUN_STATE TBD+1):
- the magistrate's own power reads (AC powermode, marker present or not, `night.lock` holder) and, if run, the restore-owed output with its "when safe" lines;
- the ARG used, the journal-copy line and the batch-time print from the arm; the maintenance line's counts and the legs they overlap;
- the receipt line, the step list and RECEIPT OK (or the receipt in full if not clean);
- **D1:** each leg's `admitted` from its `leg_summary.json` (never from the leg record), the receipt's `high_power.revoked` and `high_power.before_restore`, as printed;
- each leg's `leg_summary.json` line; `span/result.json` (with `restore_proven`) and `span/meter.json`;
- legs run and admitted (of {c['n']}); for any excluded leg, the rule it fell under (from `g0_outcome`, `contaminated_redos`, `leg_status`/decode cap, the leg's `ac_powermode`, and `high_power.revoked`); whether any named stop would fire (the Air desk builds `stops.json` from the bundle);
- whether two legs ran over 1.5 × `budget_s` (LEG_OVERTIME: goes to the RESEARCH LEAD, RL-157 §5);
- the RL-157 §1 print ({first}) and the RL-150 R1 print, as printed;
- the restore lines and the measurement_mode verify lines; the receipt's close epoch;
- whether the span crossed 00:00 (the `/private/tmp` walk; not a gate).

The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).**
- **The journal copy:** copy this span's journals to the Air by SSH (never while a fence is up), hash-verify them, then write `/Users/Shared/JouleWise/desk-copy/cq-hp-01-{key}-a1.ok` (the copy manifest's sha256 and the `date` stamp). The next campaign arm waits for it.
- **The Air desk (D6):** copy the desk bundle to `/Volumes/JW-EXT/cadence-desk/cq-hp-01-{key}-a1/input` and build the table from a checkout at or after `dd206025a`, WITH the kit (never `--adapter`, which leaves RESTORE_UNPROVEN inert). Record the desk FINAL; line 9 needs it for campaign span {c['span_no'] + 2}.
- **D1's second line:** any `high_power.revoked` entry holds {"`hp-01-s03`" if key == "s02" else "the next arm"} until the research lead rules, as a REFUSAL would. LEG_OVERTIME goes to the research lead.
- {"**Next:** `hp-01-s03` (L008-L012) arms at this close + 300 s on its own item, once this span closed clean; then, on Sunday, the dev-02 pull (RL-165 §2)." if key == "s02" else "**Next (RL-165 §2):** the dev-02 pull (`dev-02-s02`, Sunday), then the standing F0. Move `hp-01` in BLOCK-QUEUE to COLLECTED (12 legs), then DESK_FINAL when this desk is final."}
"""
    open(f"{D}/ITEM-hp01-{key}.md", "w").write(head + s + tail)
    print(f"ITEM-hp01-{key}.md", len(head + s + tail))
