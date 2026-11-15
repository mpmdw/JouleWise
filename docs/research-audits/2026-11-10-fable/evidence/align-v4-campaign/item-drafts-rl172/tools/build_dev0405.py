"""dev-04 s01/s02 and dev-05 s01/s02 items: new drafts on the RL-171 dev-03 remainder item (same pin, same runner, same
script), with each kit's facts. Every number below comes from the pinned `plan` (plans/new/, plans/bands/) or the kits."""
import sys, json
sys.path.insert(0, "/Volumes/JW-EXT/scratch/items-rl171/tools")
from common import *
D = "/Volumes/JW-EXT/scratch/items-rl171"
src = open(f"{D}/ITEM-dev03-rest.md").read()
start = src.index("**Start and check (while you are still alive).**")
report = src.index("**Report** (by email to Ed and the lead")
BODY = src[start:report]
KITC = "fecaf73f3579756c6e735f6a9cc74aab011d293a"
K = {"dev-04": dict(sha="1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228", seed=2026111405,
                    qsha="691319634b268f2d2b9c7c6308fea737d3b0f777bb859a6a14fa1322f1870d72"),
     "dev-05": dict(sha="2747381bf1169471d929d1e91510f7d272ff9cbc973da2c99f11673bea53ca1a", seed=2026111406,
                    qsha="391f438281af05fece9866ec532e7fdb4b0f478b297e403bd99da6153e2fafbb")}
def legs_line(block, a, b):
    import glob
    f = glob.glob(f"{D}/plans/new/plan-{block.replace('-', '')}-L{a:03d}-L{b:03d}-*.json")[0]
    p = json.load(open(f))
    out = []
    for i, l in enumerate(p["legs"]):
        shape = l.get("g0_shape") or "own"
        role = l.get("g0_role") or ("first leg: its capture is the span's reference" if i == 0 else "")
        out.append(f"{l['leg_id']} ({l['prefill_tokens']}, {shape}{', ' + role if role else ''}) {l['budget_s']}")
    cons = [l["leg_id"] for l in p["legs"] if l.get("g0_role") == "consume"]
    return "; ".join(out), cons, p["expected_s"]
SPANS = [
 # block, span, a, b, item file, forecast (t0, arg, end, worst, fence), campaign span number, line-9 span, prior desc, bands item
 ("dev-04", "dev-04-s01", 1, 6, "ITEM-dev04-s01.md", ("Tue 00:00:00 (dev-04's t0-date, RL-172 (a); the last Monday F0 closes 19:36:17)", "13:14-13:15", "02:55:07", "06:52:30", "07:16:50"), 11, "the dev-03 pilot (`dev-03-s01`, campaign span 9)", "dev-03's remainder (`dev-03-s02`)", "dev04-s01"),
 ("dev-04", "dev-04-s02", 7, 12, "ITEM-dev04-s02.md", ("Tue 03:00:07 (dev-04-s01's expected close 02:55:07 + 5 min)", "02:00-02:35", "06:21:18", "09:52:37", "10:16:57"), 12, "dev-03's remainder (`dev-03-s02`, campaign span 10)", "`dev-04-s01`", "dev04-s02"),
 ("dev-05", "dev-05-s01", 1, 6, "ITEM-dev05-s01.md", ("Wed 00:00:00 (dev-05's t0-date, RL-172 (a); the last Tuesday F0 closes 16:25:12)", "13:14-13:15", "03:14:40", "06:52:30", "07:16:50"), 13, "`dev-04-s01` (campaign span 11)", "dev-04's last span (`dev-04-s02`)", "dev05-s01"),
 ("dev-05", "dev-05-s02", 7, 12, "ITEM-dev05-s02.md", ("Wed 03:19:40 (dev-05-s01's expected close 03:14:40 + 5 min)", "02:00-02:35", "06:21:18", "10:12:10", "10:36:30"), 14, "`dev-04-s02` (campaign span 12)", "`dev-05-s01`", "dev05-s02"),
]
for block, span, a, b, fname, fc, num, line9, prior, bitem in SPANS:
    k = K[block]; kid = f"cl-{block}.v1.1"; legs = ",".join(f"L{i:03d}" for i in range(a, b + 1))
    legtxt, cons, expected = legs_line(block, a, b)
    PICK = open(f"{D}/plans/bands/{bitem}.sh").read().rstrip("\n")
    first = f"L{a:03d}"
    s = BODY
    # --- script substitutions from the dev-03 remainder ---
    s = count_sub(s, "fetch origin align/2026-11-14-kit-v1-1\n", f"fetch origin align/2026-11-14-kit-v1-1\ngit -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-dev04-05-kits   # the kit file (not on the pin)\n", 1)
    s = count_sub(s, "/Users/edr/code/jw-wt/cadence-dev03-rest", f"/Users/edr/code/jw-wt/cadence-{span}", 2)
    s = count_sub(s, ': "${PRIOR_CLOSE_EPOCH:?Set to the later of the dev-03 pilot runner_receipt ended.epoch_s and the epoch its fence was seen gone}"',
                  f': "${{PRIOR_CLOSE_EPOCH:?Set to the later of {prior.replace("`", "").replace("'s ", " ")} runner_receipt ended.epoch_s and the epoch its fence was seen gone}}"', 1)
    s = count_sub(s, "# The roster: nine legs at every launch time (RL-171 §3; dev-03-s02b and dev-03-s03b are withdrawn unarmed)\nSPAN=dev-03-s02;  LEGS=L004,L005,L006,L007,L008,L009,L010,L011,L012; DEADLINE_S=34310; WORST_S=32850; EXPECT=\"expected_s 15163, worst_case_s 32850\"",
                  f"# The roster (RL-158 Q6's 6 + 6; the queue's span)\nSPAN={span};  LEGS={legs}; DEADLINE_S=26210; WORST_S=24750; EXPECT=\"expected_s {expected}, worst_case_s 24750\"", 1)
    s = count_sub(s, s[s.index("pick_arg() {"):s.index("  else echo NONE; fi\n}") + len("  else echo NONE; fi\n}")], PICK, 1)
    s = count_sub(s, 'echo "SPAN $SPAN LEGS $LEGS"   # record it; dev-03-s02b and dev-03-s03b are withdrawn unarmed by this arm', 'echo "SPAN $SPAN LEGS $LEGS"', 1)
    s = count_sub(s, "# The kit: from PR #788's head, OUTSIDE the checkout, sha asserted", f"# The kit: from `{KITC[:9]}` (branch align/2026-11-14-dev04-05-kits), OUTSIDE the checkout, sha asserted", 1)
    s = count_sub(s, "KIT=/Users/edr/campaign-out/kits/cl-dev-03.v1.1-9cbb365a6-${SPAN#dev-03-}.json", f"KIT=/Users/edr/campaign-out/kits/{kid}-{KITC[:9]}-${{SPAN#{block}-}}.json", 1)
    s = count_sub(s, "show 9cbb365a6957c3737617d8604ba6d06071ab018c:docs/process/cadence/kits/cl-dev-03.v1.1.json", f"show {KITC}:docs/process/cadence/kits/{kid}.json", 1)
    s = count_sub(s, "0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b", k["sha"], 3)
    s = count_sub(s, "# must print ok true, campaign_id cl-dev-03,", f"# must print ok true, campaign_id cl-{block},", 1)
    s = count_sub(s, "QCOMMIT=<LEAD FILLS: the remainder append's commit on audit/2026-11-10-fable>", f"QCOMMIT=<LEAD FILLS: the commit of QUEUE-cl-{block}-2d347f721.json on audit/2026-11-10-fable>", 1)
    s = count_sub(s, "QUEUE-cl-dev-03-2d347f721-append-both.json | shasum -a 256 | cut -c1-64)\" = 366662cecb9794b9d13dbc67dd5721acd2bdf00b5055cc8df70861c07b593fbb",
                  f"QUEUE-cl-{block}-2d347f721.json | shasum -a 256 | cut -c1-64)\" = {k['qsha']}", 1)
    s = count_sub(s, "/Users/edr/campaign-out/cl-dev-03/cq-${SPAN}-a1-", f"/Users/edr/campaign-out/cl-{block}/cq-${{SPAN}}-a1-", 1)
    old_plan = s[s.index("# nine legs: L004"):s.index("$EXPECT; blackout_clear true")]
    s = count_sub(s, old_plan, f"# {legtxt};\n#   ", 1)
    s = count_sub(s, 'r["kit"]["campaign_id"] == "cl-dev-03"', f'r["kit"]["campaign_id"] == "cl-{block}"', 1)
    s = count_sub(s, "NOTE 1 and NOTE 2 as in item 321", "NOTE 1 and NOTE 2 as in item 321 and the dev-03 items", 1)
    s = count_sub(s, "the two spans withdrawn unarmed (`dev-03-s02b`, `dev-03-s03b`), ", "", 1)
    bad = [l for l in s.split("\n") if "dev-03" in l and "the dev-03 items" not in l and "PRIOR_CLOSE_EPOCH" not in l]
    assert not bad, bad[:3]
    E0 = "1794902400" if block == "dev-05" else "1794816000"
    s = s.replace("# The launch bands (EARLIEST 1794816000 Mon 00:00:00;", f"# The launch bands (EARLIEST {E0} {'Tue' if block == 'dev-05' else 'Mon'} 00:00:00;")
    assert "L004" not in s or a <= 4 <= b
    W = 24750
    E_DAY = "Tue" if block == "dev-05" else "Mon"
    E_LOCAL = "00:00:00 PST Tue 17 Nov" if block == "dev-05" else "00:00:00 PST Mon 16 Nov"
    E_EPOCH = "1794902400" if block == "dev-05" else "1794816000"
    E_WHY = "; dev-05 is a Tuesday block for day balance, as RL-165's plan had it" if block == "dev-05" else ""
    NB = "2026-11-17" if block == "dev-05" else "2026-11-16"
    NBWHY = ("2026-11-17: dev-05 is a Tuesday block (day balance, below)" if block == "dev-05" else "2026-11-16, the earliest day the RL-171 chain can need")
    DAYBAL = ("\n  - **Day balance (coordinator, 11-15; Mythos throughput §3 item 4 as the DEFAULT until the research lead rules; RL-150 R3, RL-149 §2.3: every error is leave-one-day-out, so prompt size must not collect on one day):** at most two development blocks START on this span's local calendar day, counting this block; qualification days hold no development span. "
              + ("dev-05 is a Tuesday block (not before Tue 00:00:00), as in RL-165's plan: Monday already starts dev-03 and dev-04 and holds 30 development legs (dev-02's second half, dev-03, dev-04). <LEAD FILLS: the blocks that started on this span's day, from the ledger>." if block == "dev-05" and a == 1 else
                 "Monday's starts are dev-03 and dev-04 (two); dev-05 waits for Tuesday. <LEAD FILLS: the blocks that started on this span's day, from the ledger>." if a == 1 else
                 "This span starts no block; the rule binds its block's first span.")) 
    head = f"""TBD. **Laptop lead (interactive, Opus 5.5), drafted under RL-171 by the items-rl171 builder 2026-11-15 PST (new draft; the dev-04/05 kits' builder and the Mythos dev-04/05 delta seat supply the facts), ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm {"the FIRST" if a == 1 else "the SECOND"} span of block {block} (RL-158 §3; RL-165 §1, §4; RL-171), span `{span}`, legs {", ".join(legs.split(","))}, kit `{kid}` (sha256 `{k['sha']}`), runner kind `cadence-legs-v1.1`, on `2d347f721552fe03bdd19f113e7bad7a7c24908e` checked out detached in a fresh scratch worktree. One span: a fresh soak, then six legs at their cells ({first} first; consumers {", ".join(cons)} judge their G0 against {first}'s capture), decode cap 4,096, Automatic, band q0. They are counted development legs of {block}. No other span, no queue extension, no session, no W1. EARLIEST: the close interval (RL-171 §6.1) after {prior} closed with its fence gone and its Check reported, and not before {E_LOCAL} (epoch {E_EPOCH}{E_WHY}). LAUNCH as soon as every gate holds, at any hour up to 23:59:59 PST Wed 18 Nov (LIMIT, epoch 1795075199), except 10:50:00-13:15:00 (the pin's `fence_problems` refuses it under either argument). The batch-window argument follows the launch time (RL-171 §3): `02:00-02:35` from 02:35:00 to 10:50:00 and from 13:15:00 to 18:33:10; `13:14-13:15` from 18:33:11 to 02:34:59. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-19T08:17:00-08:00
on_early_or_refused: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), or a launch that cannot happen inside the bands below ({E_DAY} 00:00:00 to Wed 23:59:59 PST, outside 10:50:00-13:15:00): NOTHING of this item launches; mail the lead; a later t0 needs a new item, and the standing F0 item applies meanwhile. A span that ran but ends with any named stop or a receipt rc≠0: nothing relaunches, nothing is re-run, nothing else is queued; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the maintenance line, the receipt asserts, the per-leg admitted lines with g0_role and span_reference, the desk bundle, the restore lines, measurement_mode verify again, and the RL-150 R1 / RL-158 Q1 print (gates nothing)
```

- **Why (RL-158 §3; RL-165 §1; RL-171).** {block} follows at its first legal t0 (RL-165 §1: "dev-04 and dev-05 follow at their first legal t0"; dev-05 is not held for Wednesday). RL-171 retires the 18:33:10 latest t0 (the 01:50 fence) and the 02:40 starts: this pin's fence check is met by the argument `13:14-13:15` from 18:33:11 (RL-171 §3), so the span arms at any t0 outside 10:50-13:15. The 6 + 6 layout is RL-158 Q6's (the kits' builder, `/Volumes/JW-EXT/scratch/dev04-05/README.md`). A leg's calendar day is the local date of its span's t0.
- **Gate.** All of:
  - {prior} closed and checked: <LEAD FILLS: RUN_STATE <n>: RECEIPT OK, legs run and admitted, no named stop open, restore lines clean, close epoch>.
  - **The cold seat's delta on `{kid}`: ADMIT** (Mythos 5.2, Sat 14 Nov 18:25 PST, "neither kit needs a byte changed"; `/Volumes/JW-EXT/scratch/mythos-dev0405-delta/REPORT.md`, <LEAD FILLS: its audit-branch copy>).
  - **Mythos dev-04/05 F1, the two dev-03 records (RL-150 R5; §2.8 line 8 for these kits):** dev-03's R9 **PASSED** and its class A smoke **MET** (L002 released its G0 against L001's capture and ran its turn), each recorded on its own line: <LEAD FILLS: both lines and where recorded>. dev-03 ran on `cl-dev-03.v1.1`, not the own-shaped v1.1a fallback; on that fallback this kit may not arm as built (F1) and the case goes to the research lead.
  - **Q6 (RL-158 Q6; RL-161):** on 6 + 6 {block} has 6 of its 10 warm legs as consumers ({"L005 in span 1; L008-L012 in span 2" if block == "dev-04" else "L002, L003, L005, L006 in span 1; L008, L012 in span 2"}), at least half, and every cut lands on an own-shaped leg (L007). This span's consumers: {", ".join(cons)}.{'''
  - **The L005 gate (RL-165 §4, amending RL-163 §6; RL-167: "at least four of its five"; Mythos dev-04/05 F3).** If `dev-04-s01`'s L005 **released** its G0, this span arms on its own gates. If L005 **timed out** at G0: this span arms on the lead's record only if dev-03 ended with at least four of its five consumers released (L002, L008, L009, L010, L012); with fewer than four it does NOT arm, and dev-04's L007-L012 and dev-05 run own-shaped (new kits). <LEAD FILLS: L005's G0 outcome from `dev-04-s01`'s Check, and, if it timed out, dev-03's released-consumer count and where recorded>. Mythos F3 (five consumers on one reference in this span) is the research lead's question; it does not hold this arm.''' if span == "dev-04-s02" else ""}{'''
  - **dev-04 ran span-shaped to its end:** if dev-04's second span did not arm under the L005 gate (fewer than four of dev-03's consumers released), this item is NOT issued: dev-05 then runs own-shaped (RL-165 §4).''' if span == "dev-05-s01" else ""}
  - Lines 2, 3, 5, 6, 7 and 9 at the arm (below).{DAYBAL}
  - **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-165 §7):** the Check of the latest close of ANYTHING on this host reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is QUIET_CAMPAIGN_S after a campaign span's close, which the lead fills as 300 s once it has confirmed that the Check and the hash-verified copy finish inside 5 min, else 1,200 s; GAP is 1,200 s after a Part C or F0, F2, a slot session or W1), from the receipt census that stops on a missing root, any lookup error or an empty result (or OTHER_CLOSE_EPOCH). Read fresh at the launch: if a v4 slot session is READY and staged for this slot, this span cedes; if a session is staged with an intended t0, this span launches only if launch + its worst case (24,750 s) + 1,200 s is at or before that t0.
- **Counted.** The six legs count as development legs of {block} under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8; rule 2 against the reference the leg's shape names). The kit has no `pilot_counted` rule (dropped by the builder: it described dev-03's smoke; Mythos delta: right). An excluded leg is refilled only from the reserve under RL-149 §2.4. A re-run is a new span with `attempt` + 1 and `rerun_of`, and it needs a ruling.
- **Queue.** `QUEUE-cl-{block}-2d347f721.json`: `cq-cl-{block}`, spans `{block}-s01` (L001-L006) and `{block}-s02` (L007-L012), both not_before {NB}, `expires_at` 2026-11-21T23:59:00-08:00 (the items-rl171 copy: the builder's not_before {"2026-11-17" if block == "dev-04" else "2026-11-18"} moved to {NBWHY}, and the expiry moved from 11-22 to 11-21 so that a commit any time from now is within 7 days, Mythos dev-04/05 F2). Do not run `cadence_queue.py next`: `not_before` and the k+2 desk rule are not enforced in code at this pin (Mythos F4); this item and line 9 carry them.
- **Bytes, CI and condition 13.** Measured from `2d347f721552fe03bdd19f113e7bad7a7c24908e` (the dev-03 pin). The kit is `{kid}.json` from `{KITC}` (branch `align/2026-11-14-dev04-05-kits`, on #788's head `9cbb365a6`; kit files only), sha256 `{k['sha']}`, master seed {k['seed']}, copied outside the checkout. Its frozen block, runner, stop_rules, span_template, checklist, looks and desk are byte-identical to `cl-dev-03.v1.1`'s (Mythos delta). Line 2 is dev-03's, one result for the pin (Mythos F5). `verify_r1_executed_sources` must return the full sha. Same bytes as dev-03, so no smoke of its own: dev-03's pilot was the class A smoke (F1).
- **Timing.** Plan for this roster (`plan` at `2d347f721` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-{bitem}.txt`): expected {expected:,} s, worst case 24,750 s (6 h 52 min 30 s); fence deadline launch + 26,210 s. Budgets: {legtxt}.
  - **Bands (RL-171 §3; the `pick_arg` function below), every day {E_DAY} to Wed:** 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-18:33:10 `02:00-02:35`; 18:33:11-02:34:59 `13:14-13:15` (which admits six legs up to 05:47:10). Checked: with `02:00-02:35` 18:33:10 accepted and 18:33:11 refused; with `13:14-13:15` 05:47:10 accepted and 05:47:11 refused; 10:50:01 refused under either. `validate-kit` ok with either argument. A mock span at t0 Mon 00:30 with `13:14-13:15` across 02:00-02:35: rc 0, 6 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/{span.replace('-', '').replace('dev0', 'dev0')}-alt-00:30/`).
  - Forecast t0 {fc[0]}, argument `{fc[1]}`: expected end {fc[2]}, worst end {fc[3]}, fence end {fc[4]} (`/Volumes/JW-EXT/scratch/items-rl171/plans/chain-new.txt`).
  - Pointer deadline = latest fence end (LIMIT + 26,210 s = Thu 07:16:49) + 1 h.
- **Conditions, blinding and the High Power marker:** as the dev-03 items, with `--legs "$LEGS"` written out and `--batch-window "$ARG"` on every `validate-kit`, `plan` and `launch` (chosen once in Start and check by the launch time, re-checked in Run; RL-171 §3); the arm record shows the plan's `batch_windows` and the measurement_mode line (RL-150 §2 F2, F5; RL-161 §3); output root `/Users/edr/campaign-out/cl-{block}/`. Quiet is the per-leg agent census, process census and rule 5 (RL-171); there is no clock quiet.
- **May run:** this span, once. **May NOT:** any other {block} or dev-05 span{"" if block == "dev-04" else " of dev-04"}, any session, W1, any filler while this span is armed.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. Kit `ruling` is `RL-149 §2`. `{kid}` `{k['sha'][:8]}…{k['sha'][-4:]}` at `2d347f721`: the Mythos 5.2 delta seat against `cl-dev-03.v1.1`, ADMIT (above); dev-03's line 1 (row-1 ADMIT at `17f478675`, Mythos first and delta seats on #788) stands for the shared bytes.
2. As dev-03's line 2 (RL-165 §5's four parts at `2d347f721`; CI run 43664825578 on `9cbb365a6`): <LEAD FILLS: its final conclusion and red set, one result for dev-03 to dev-05 (Mythos F5)>.
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-{block}-2d347f721.json` on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `{k['qsha']}` (`validate-queue` ok at `2d347f721` with `--kits-root` the dev-04/05 kit checkout at `{KITC[:9]}`: plan ids `cq-{block}-s01-a1`, `cq-{block}-s02-a1`; `/Volumes/JW-EXT/scratch/items-rl171/queue/validate-queue.log`).
4. `validate-kit` passes; OUT is outside every v4 registration and custody root (check below).
5. The per-span checks of design doc §4 and §14 pass at the arm and at the close. Do NOT run `cadence_queue.py checklist` or `next`.
6. No named stop, veto or halt open (the `directive` and `cadence-stop` issues; gh via `launchctl asuser`). By hand: no named stop open from any earlier span, no RESTORE_UNPROVEN and no High Power `revoked` hold: <LEAD FILLS: span ids, their desk `stops.json` result and the time read>.
7. Results-ref watcher live within 24 h: <LEAD FILLS: heartbeat stamp, pid and commit>.
8. dev-03's R9 PASSED and its class A smoke MET (Gate above; Mythos F1).
9. Line 9, across blocks in run order (RL-165 §6). Expected: this span is campaign span {num}, so span {num - 2}'s desk, {line9}, must be FINAL. As run: this span is campaign span <LEAD FILLS: N>, and the desk of the span two back, <LEAD FILLS: SPAN ID>, is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded>.

"""
    tail = f"""**Report** (by email to Ed and the lead, and as RUN_STATE TBD+1):
- SPAN and LEGS; the ARG used; the maintenance line's counts and the legs they overlap;
- the receipt line, the step list and RECEIPT OK (or the receipt in full if not clean);
- each leg's `leg_summary.json` line, with `admitted`, `g0_role`, `g0_outcome`, `g0_s` and `span_reference` called out per leg;
- each consumer's G0 outcome against {first}'s capture (released or timed out), and the count released{" (L005's outcome gates `dev-04-s02`)" if span == "dev-04-s01" else ""};
- `span/result.json` and `span/meter.json`;
- legs run and admitted (of 6); for any excluded leg, the inclusion rule it fell under; whether any named stop would fire (LEG_OVERTIME is two legs over 1.5 x their own budget; a missing {first} reference is a REFUSAL that stops the span, RL-158 Q3);
- the RL-150 R1 / RL-158 Q1 print above, as printed;
- the restore lines and the measurement_mode verify lines; the receipt's close epoch;
- whether the span crossed 00:00 (the `/private/tmp` walk; not a gate).

The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).**
- **The Air desk (Mythos #788 delta D1; dev-04/05 F8):** from the checkout at `2d347f721` (or `1b20d3b0e`), with the kit; never a checkout at `b4b6aeb19`, `main` or the hp-01 line. Copy the bundle to `/Volumes/JW-EXT/cadence-desk/cq-{span}-a1/input`.
- **The hand-read print of every v1.1 span (RL-158 Q1):** the soak reference, {first}'s capture, and each consumer's release reading and G0 wait. Mark "reference from a redo" or "from an excluded leg" from the receipt's `span_reference` (RL-158 Q2; RL-161 §4).
- **The realized consumer count (RL-158 Q6):** consumers released over the block; it goes in the ledger row. A block that ends with fewer than four released consumers comes to the research lead (RL-158 Q6); nothing stops on that.
- This desk must be FINAL before campaign span {num + 2} arms (line 9). {"**Next:** `dev-04-s02` arms at this close + the close interval on its own item, under the L005 gate." if span == "dev-04-s01" else "**Next:** `dev-05-s01` arms on its own item at its first legal t0 from Tue 00:00:00 (day balance: dev-05 is a Tuesday block, as in RL-165's plan; the ladder fills the evening). RL-165 §1's \"dev-05 is not held for Wednesday\" still holds." if span == "dev-04-s02" else "**Next:** `dev-05-s02` arms at this close + the close interval on its own item." if span == "dev-05-s01" else "**Next:** development is complete (60 legs over Sat, Sun, Mon and Tue on the forecast path: 7, 11, 30 and 12, as RL-165's plan); freeze 2 is desk work, and the ladder (the slot session if READY, then F0 and F2 if READY) takes the machine."} Ledger: `{block}` {"READY to RUNNING" if a == 1 else "to COLLECTED, then DESK_FINAL when the desk is final"}.
"""
    open(f"{D}/{fname}", "w").write(head + s + tail)
    print(fname, "ok", len(head + s + tail))
