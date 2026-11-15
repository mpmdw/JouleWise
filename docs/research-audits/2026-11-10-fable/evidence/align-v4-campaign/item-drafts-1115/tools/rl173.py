#!/usr/bin/env python3
"""items-1115: finalize the campaign item drafts for RL-173 D (items issued ahead) and resolve the host-independent fills.

Reads the RL-171/172 drafts in /Volumes/JW-EXT/scratch/items-rl171 (never edits them) and writes the finalized texts to
/Volumes/JW-EXT/scratch/items-1115. Every replacement asserts its exact match count, so a drifted draft fails loudly.
"""
import pathlib
import sys

SRC = pathlib.Path("/Volumes/JW-EXT/scratch/items-rl171")
DST = pathlib.Path("/Volumes/JW-EXT/scratch/items-1115")
QCOMMIT = "b7a0d98822865a01e67fc3cc1833c9b186be2181"
STAMP = "items-1115 builder, Sun 15 Nov 2026 PST"


def rep(t, old, new, count=1):
    n = t.count(old)
    if n != count:
        sys.exit(f"anchor count {n} != {count}: {old[:120]!r}")
    return t.replace(old, new)


# ---------------------------------------------------------------- RL-173 D, common to every counted item
PRED_PY = r'''import json, math, os, re, sys
root, camp, span, roster = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",")
d = os.path.join(root, camp)
if not os.path.isdir(d):
    print(f"WAIT: no {d}: the predecessor {span} has not run; retry at the next activation"); sys.exit(1)
pat = re.compile("cq-" + re.escape(span) + r"-a\d+-\d{8}T\d{6}Z")
hits = sorted(n for n in os.listdir(d) if pat.fullmatch(n))
if not hits:
    print(f"WAIT: the predecessor {span} has no output directory under {d}: it has not run; retry at the next activation"); sys.exit(1)
if len(hits) > 1:
    print(f"STOP: the predecessor {span} has {len(hits)} output directories {hits}: a re-run needs the lead; mail the lead"); sys.exit(1)
out = os.path.join(d, hits[0])
p = os.path.join(out, "runner_receipt.json")
if not os.path.isfile(p):
    print(f"WAIT: the predecessor {span} ({out}) has no runner_receipt.json: it has not closed; retry at the next activation"); sys.exit(1)
try:
    r = json.load(open(p))
except (OSError, ValueError):
    print(f"STOP: the predecessor receipt {p} is unreadable; mail the lead"); sys.exit(1)
if not isinstance(r, dict):
    print(f"STOP: the predecessor receipt {p} is unreadable; mail the lead"); sys.exit(1)
num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
bad, n = [], len(roster)
if r.get("rc") != 0: bad.append(f"rc {r.get('rc')!r}")
if r.get("error") not in (None, ""): bad.append("error set")
if r.get("mock") not in (False, None): bad.append("mock receipt")
if r.get("roster") != roster: bad.append(f"roster {r.get('roster')!r}")
if r.get("legs_planned") != n or r.get("legs_finished") != n:
    bad.append(f"legs {r.get('legs_finished')!r} of {r.get('legs_planned')!r}")
sr = r.get("span_result") if isinstance(r.get("span_result"), dict) else {}
if sr.get("outcome") != "MEASURED_OK" or sr.get("chain_outcome") != "COMPLETE" or sr.get("fault") is not False:
    bad.append(f"span_result {sr.get('outcome')!r}/{sr.get('chain_outcome')!r}/fault {sr.get('fault')!r}")
steps = [s for s in (r.get("steps") or []) if isinstance(s, dict)]
close = [s for s in steps if s.get("name") == "restore" or str(s.get("name", "")).startswith(("stop-", "close-"))]
if not any(s.get("name") == "restore" for s in close): bad.append("no restore step")
bad += [f"close step {s.get('name')} rc {s.get('rc')!r}" for s in close if s.get("rc") != 0]
ended = (r.get("ended") or {}).get("epoch_s") if isinstance(r.get("ended"), dict) else None
if not num(ended): bad.append("ended.epoch_s unreadable")
over = redos = 0
for leg in roster:
    sp = os.path.join(out, "desk-bundle", "legs", leg, "leg_summary.json")
    try:
        s = json.load(open(sp))
    except (OSError, ValueError):
        bad.append(f"no readable desk-bundle leg_summary for {leg}"); continue
    w, b, c = s.get("wall_s"), s.get("budget_s"), s.get("contaminated_redos")
    if not (num(w) and num(b) and isinstance(c, int) and not isinstance(c, bool)):
        bad.append(f"{leg} wall_s/budget_s/contaminated_redos unreadable"); continue
    over += w > 1.5 * b
    redos += c
if over >= 2: bad.append(f"LEG_OVERTIME: {over} legs over 1.5 x their budget")
if redos >= 3: bad.append(f"CONTAMINATED_REDOS: {redos} in the span")
if bad:
    print(f"VOID: the predecessor {span} ({out}) did not close clean: {'; '.join(bad)}. RL-173 D.2: this item is VOID and is not skipped; nothing of it launches; mail the lead"); sys.exit(1)
print(f"PRED CLEAN {span} {out}: rc 0, {n} of {n} legs, MEASURED_OK COMPLETE, close steps rc 0, overtime legs {over}, contaminated redos {redos}, close_epoch {math.ceil(ended)}")
'''

FUNCS = '''# RL-173 D.5: this item EXPIRES 24 h after issue (ISSUED_EPOCH is the same moment as ISSUED in the heading).
ISSUED_EPOCH=<LEAD FILLS: the issue time as an epoch, from `date +%s` at issue>
EXPIRES_EPOCH=$((ISSUED_EPOCH + 86400))
expiry_gate() {
  test "$(date +%s)" -le "$EXPIRES_EPOCH" || { echo "VOID: this item expired at $(date -r "$EXPIRES_EPOCH" '+%Y-%m-%d %H:%M:%S %Z') (RL-173 D.5: 24 h after issue); nothing of it launches; mail the lead"; return 1; }
  echo "expiry: this item is valid until $(date -r "$EXPIRES_EPOCH" '+%Y-%m-%d %H:%M:%S %Z') (RL-173 D.5)"
}
# RL-173 D.2: the predecessor by span id and its CLEAN close receipt. No receipt yet is WAIT; a receipt that is not clean
# makes this item VOID (never skipped). Reads only the receipt's rc, error, mock, roster, leg counts, span_result, close
# steps and ended time, and each desk-bundle leg_summary's wall_s, budget_s and contaminated_redos (RL-149 §2.4's
# LEG_OVERTIME and CONTAMINATED_REDOS); no energy, power or meter value.
PRED_SPAN=@PRED@; PRED_CAMP=@CAMP@; PRED_ROSTER=@ROSTER@
pred_gate() {
  PRED_LINE="$("$PY" -I -B - /Users/edr/campaign-out "$PRED_CAMP" "$PRED_SPAN" "$PRED_ROSTER" <<'PY'
@PY@PY
)"
  PRED_RC=$?
  printf '%s\\n' "$PRED_LINE"      # record this line
  test "$PRED_RC" -eq 0 || return 1
  PRED_CLOSE_EPOCH="$(printf '%s\\n' "$PRED_LINE" | sed -n 's/^PRED CLEAN .*close_epoch \\([0-9][0-9]*\\)$/\\1/p')"
  case "$PRED_CLOSE_EPOCH" in ''|*[!0-9]*) echo "STOP: pred_gate gave no close epoch; mail the lead"; return 1;; esac
  if [ -n "${PRIOR_CLOSE_EPOCH:-}" ] && [ "$PRIOR_CLOSE_EPOCH" -lt "$PRED_CLOSE_EPOCH" ]; then
    echo "STOP: PRIOR_CLOSE_EPOCH $PRIOR_CLOSE_EPOCH is before $PRED_SPAN's receipt close $PRED_CLOSE_EPOCH; mail the lead"; return 1
  fi
}
# Line 7 (RL-173 C 5): one watcher observation under 24 h old may serve more than one arm; each arm re-checks it.
WATCH_UNTIL_EPOCH=<LEAD FILLS: line 7's watcher observation stamp + 86,400 s, as an epoch>
watch_gate() {
  test "$(date +%s)" -le "$WATCH_UNTIL_EPOCH" || { echo "STOP: line 7's results-watcher observation is over 24 h old (RL-173 C 5); do not launch; mail the lead"; return 1; }
}
'''


def apply_common(t, it):
    t = rep(t, "The launch is your LAST action and you exit at once.",
            f"ISSUED AHEAD (RL-173 D): this item names its predecessor `{it['pred']}` and requires that span's clean close "
            "receipt, else it is VOID and is not skipped; it EXPIRES 24 h after issue, so its window ends at the earlier of "
            "LIMIT and the expiry. The launch is your LAST action and you exit at once.")
    t = rep(t, "on_early_or_refused: ",
            f"on_early_or_refused: VOID, so that nothing of this item ever launches (mail the lead; a new item is needed), if "
            f"`{it['pred']}` closed without a clean receipt (RL-173 D.2) or once 24 h have passed since the issue (RL-173 D.5). "
            "Otherwise: ")
    bullet = (
        f"- **Issued ahead (RL-173 D; the interim until #800 is admitted; {STAMP}).** (1) At most three counted spans are "
        "issued ahead of the machine, plus the standing F0. (2) **Predecessor: `" + it["pred"] + "`** (" + it["pred_desc"] +
        "). This item requires its clean close receipt: `pred_gate` below reads its `runner_receipt.json` (rc, error, "
        "roster, leg counts, span_result, close steps, close time) and its desk bundle's `leg_summary.json` files (wall "
        "against budget, contaminated redos), never an energy, power or meter value. No receipt yet is WAIT. A receipt "
        "that is not clean makes this item VOID: it is not skipped, nothing launches on its authority, and the lead "
        "decides. (3) Its date window is " + it["date"] + " (RL-172 (a)), and its own argument choice is `pick_arg` "
        "below. (4) Nothing is issued past a class A hand-read or an L002 or L005 gate. " + it["issuable"] + " (5) It "
        "expires 24 h after issue: `expiry_gate` (ISSUED_EPOCH + 86,400 s) runs in Start and check and again just "
        "before the launch.\n")
    t = rep(t, "\n```\n\n- **Why", "\n```\n\n" + bullet + "- **Why")
    funcs = FUNCS.replace("@PRED@", it["pred"]).replace("@CAMP@", it["camp"]).replace("@ROSTER@", it["roster"]).replace("@PY@", PRED_PY)
    t = rep(t, "# RL-172 (a): t0-date caps", funcs + "# RL-172 (a): t0-date caps")
    t = rep(t, "day_gate || exit 1", "day_gate || exit 1\npred_gate || exit 1     # RL-173 D.2\nexpiry_gate || exit 1   # RL-173 D.5", 2)
    t = rep(t, 'NOW=$(date +%s); test "$(pick_arg "$NOW")" = "$ARG"',
            'expiry_gate || exit 1; watch_gate || exit 1   # RL-173 D.5 and C 5, last before the launch\n'
            'NOW=$(date +%s); test "$(pick_arg "$NOW")" = "$ARG"')
    # RL-173 A: the copy marker may come from the MBP's own verified cloud offload
    t = rep(t, "shown by the lead's marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified",
            "shown by the marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified "
            "(by the lead's Air copy, or by the MBP's own verified encrypted cloud offload, items 347 and 348, which RL-173 A "
            "makes the off-host copy permanently; a failed or unverified offload writes no marker and holds the arm, RL-173 A 7)")
    t = rep(t, "# complete and hash-verified on the Air: the lead copies by SSH, verifies, and only then writes",
            "# complete and hash-verified off the MBP (the lead's Air copy, or the MBP's verified cloud offload, RL-173 A), and only then is written")
    t = rep(t, "7. Results-ref watcher live within 24 h: ",
            "7. Results-ref watcher live within 24 h (RL-173 C 5: one observation under 24 h old may serve more than one arm; "
            "`watch_gate` re-checks WATCH_UNTIL_EPOCH at this arm; a GitHub Actions watcher meeting RL-173 C 1-4 may stand "
            "instead, by a re-issue that reads its latest completed run): ")
    t = rep(t, "Record ARG, LAST_CLOSE_KIND,",
            "Record the pred_gate line (RL-173 D.2), the expiry line (D.5), ARG, LAST_CLOSE_KIND,")
    return t


LINE2_FINAL = (
    "CI `ci` run 43664825578 on `9cbb365a6` COMPLETED 2026-11-14 20:47:37 PST, conclusion **failure** (9 of 12 `test` "
    "shards red; every other job success). Shard 11 was not stalled: it finished at 3 h because `tests.test_bytes_analysis` "
    "took 9,107 s and passed. The final red set is **exactly the 12 tests of `fe907d0d3`'s CI 43600776368, test for test, "
    "with no added red** (both sets re-derived from the job logs by the items-1115 builder, Sun 15 Nov 15:03 PST; "
    "evidence/align-v4-campaign/item-drafts-1115/evidence/line2-dev03-red-9cbb365a6.txt and line2-base-red-fe907d0d3.txt)")


def dev03_pilot(t):
    t = rep(t, "EARLIEST: the close interval (RL-171 §6.1) after dev-02's last span (`dev-02-s03`, or `dev-02-s01` if Sunday's pull did not run) closed with its fence gone",
            "EARLIEST: the close interval (RL-171 §6.1) after its predecessor `dev-02-s03` (dev-02's last span: Sunday's `dev-02-s02` ran and closed clean, RUN_STATE 345 and 349, so `dev-02-s01` is withdrawn unarmed) closed clean with its fence gone")
    t = rep(t, "<LEAD FILLS: whether a row-1 delta reading at `2d347f721` is recorded, and where>",
            "**No separate row-1 delta reading at `2d347f721` is recorded** (searched by the items-1115 builder, Sun 15 Nov: "
            "PR #788 has no review or comment; the audit branch's evidence holds only the two Mythos seats on #788; "
            "`/Volumes/JW-EXT/scratch/rev788/REVIEW.md` is the `17f478675` review). The precedent is item 334 (hp-01 at "
            "`dd206025a`): the lead recorded the Mythos delta seat as row 1's delta reading. Executed evidence at this pin: "
            "CI 43664825578 on the frozen-identical head `9cbb365a6` (`test_kit_v11` 30 tests, 0 skipped, line 2 D2) and the "
            "Air `validate-kit` and `plan` at `2d347f721` (items-rl171 `probe/`). <LEAD FILLS: the lead's decision: "
            "\"the Mythos delta seat (ADMIT, `5b8d23727`) stands as row 1's delta reading for `2d347f721`, as item 334\", "
            "or a row-1 delta seat is ordered and this item waits for it>")
    t = rep(t, "<LEAD FILLS: its conclusion; at 20:00 PST Sat one shard (11) was still running after about 2 h 10 min, `/Volumes/JW-EXT/scratch/dev03-line2/LINE2-dev03.md`>",
            LINE2_FINAL)
    t = rep(t, "<LEAD FILLS: the final red set; partial at 20:00, 11 of 12 base reds and no new red, the missing one in the unfinished shard>",
            "final, all 12 shards: the 12 base reds and no other (the twelfth, "
            "`align.test_v4_dynamic_closure.LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace`, "
            "failed in shard 11 as it did in the base); no added red")
    t = rep(t, "on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `403e53f9",
            f"on audit/2026-11-10-fable at `b7a0d9882` (`{QCOMMIT}`, Sun 15 Nov 00:22 PST; validate-queue re-run ok at "
            "`2d347f721` on the committed bytes, Sun 15 Nov 15:05 PST, evidence/align-v4-campaign/item-drafts-1115/evidence/"
            "validate-queue-1115.log), sha256 `403e53f9")
    t = rep(t, "QCOMMIT=<LEAD FILLS: the dev-03 queue's commit on audit/2026-11-10-fable>", f"QCOMMIT={QCOMMIT}")
    t = rep(t, "<LEAD FILLS: the Air checkout path at `2d347f721`>",
            "`/Volumes/JW-EXT/jw-wt/desk-final-pin-2d347f721` (detached at `2d347f721`, clean; checked by the items-1115 "
            "builder Sun 15 Nov), or, under RL-173 B, the MBP's deterministic desk at the same commit in the close interval, "
            "named in the arm record")
    t = rep(t, "If dev-03 is READY with this item, its queue and its worktree staged on the MBP by **Sun 23:30**",
            "If dev-03 is READY with this item, its queue and its worktree staged on the MBP by **Sun 23:30** (staging: "
            "`stage_mbp_span.sh dev-03-s01`, run by the lead over SSH in a close interval, evidence/align-v4-campaign/"
            "item-drafts-1115/stage_mbp_span.sh)")
    return t


def dev02_s03(t):
    t = rep(t, "<LEAD FILLS: `dev-02-s02` ran (RUN_STATE <n>): RECEIPT OK or not, legs run and admitted of 6, no named stop open, restore lines clean; OR `dev-02-s02` never armed (why), so RAN=none>",
            "`dev-02-s02` ran (RUN_STATE 345 launch, 349 Check): RECEIPT OK, 6 of 6 legs run and 6 of 6 admitted, outcome "
            "MEASURED_OK, chain COMPLETE, no fault, no load redo, no LEG_OVERTIME, restore lines clean; receipt close 12:42:45 "
            "PST Sun 15 Nov; journals offloaded and marker `cq-dev-02-s02-a1.ok` written (RUN_STATE 350). So RAN=dev-02-s02 "
            "and this item arms `dev-02-s03` (L007-L012); its named-stop result is line 6")
    t = rep(t, ': "${RAN:?Set RAN to dev-02-s02 if Sunday span dev-02-s02 closed RECEIPT OK with no stop open, or none if it never armed}"',
            "RAN=dev-02-s02   # RUN_STATE 349: dev-02-s02 closed RECEIPT OK; dev-02-s01 was withdrawn unarmed by item 344's arm record")
    t = rep(t, "EARLIEST: 00:00:00 PST Mon 16 Nov (epoch 1794816000; this is dev-02's Monday span, RL-165 §2) and the close interval after the latest close (RL-171 §6.1).",
            "EARLIEST: 00:00:00 PST Mon 16 Nov (epoch 1794816000; this is dev-02's Monday span, RL-165 §2) and the close interval after the latest close (RL-171 §6.1); its predecessor `dev-02-s02` closed clean at 12:42:45 PST Sun 15 Nov (RUN_STATE 349).")
    t = rep(t, "F6 is the lead's, recorded <LEAD FILLS: where>.",
            "F6 is the lead's, recorded as in item 344: the campaign ledger is RUN_STATE, the standing notice is this arm "
            "record (line 3), and the look manifest is PRs #793/#795.")
    t = rep(t, "on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `ad0212ae",
            f"on audit/2026-11-10-fable at `b7a0d9882` (`{QCOMMIT}`, as item 344), sha256 `ad0212ae")
    t = rep(t, "the notice is <LEAD FILLS: where posted>.",
            "the notice is this RUN_STATE item (line 3 names the queue, kit `cl-dev-02` `d963500b…`, legs L007-L012 and the expiry), as item 344.")
    t = rep(t, "QCOMMIT=<LEAD FILLS: the append's commit on audit/2026-11-10-fable>", f"QCOMMIT={QCOMMIT}")
    return t


def dev03_rest(t):
    t = rep(t, "<LEAD FILLS: final conclusion and red set>", LINE2_FINAL)
    t = rep(t, "on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `366662ce",
            f"on audit/2026-11-10-fable at `b7a0d9882` (`{QCOMMIT}`; committed Sun 15 Nov 00:22 PST, before the hand-read: "
            "see the items-1115 STATUS note on RL-161 §2), sha256 `366662ce")
    t = rep(t, "QCOMMIT=<LEAD FILLS: the remainder append's commit on audit/2026-11-10-fable>", f"QCOMMIT={QCOMMIT}")
    return t


def dev0405(t, kit):
    t = rep(t, "<LEAD FILLS: its final conclusion and red set, one result for dev-03 to dev-05 (Mythos F5)>",
            LINE2_FINAL + "; one result for dev-03 to dev-05 (Mythos F5)")
    t = rep(t, "on audit/2026-11-10-fable at `<LEAD FILLS: commit>`, sha256 `",
            f"on audit/2026-11-10-fable at `b7a0d9882` (`{QCOMMIT}`; validate-queue re-run ok at `2d347f721` Sun 15 Nov "
            "15:05 PST), sha256 `")
    t = rep(t, f"QCOMMIT=<LEAD FILLS: the commit of QUEUE-{kit}-2d347f721.json on audit/2026-11-10-fable>", f"QCOMMIT={QCOMMIT}")
    t = rep(t, "<LEAD FILLS: its audit-branch copy>",
            "evidence/align-v4-campaign/mythos-dev04-05.md, audit branch `da8b855b6` (byte-identical to the scratch report)")
    return t


ITEMS = {
    "ITEM-dev02-s03.md": dict(pred="dev-02-s02", camp="cl-dev-02", roster="L001,L002,L003,L004,L005,L006",
                              pred_desc="dev-02's Sunday half; closed clean 12:42:45 PST Sun 15 Nov, RUN_STATE 349",
                              date="Mon 16 Nov",
                              issuable="**Issuable now:** its predecessor has closed clean and no hand-read or L002/L005 gate lies between.",
                              extra=dev02_s03),
    "ITEM-dev03-pilot.md": dict(pred="dev-02-s03", camp="cl-dev-02", roster="L007,L008,L009,L010,L011,L012",
                                pred_desc="dev-02's Monday half, issued ahead with this item",
                                date="Mon 16 Nov",
                                issuable="**Issuable now, with ITEM-dev02-s03** (two counted spans ahead plus the standing F0): no hand-read or L002/L005 gate lies before it; its own class A hand-read comes after it and holds everything span-shaped behind it.",
                                extra=dev03_pilot),
    "ITEM-dev03-rest.md": dict(pred="dev-03-s01", camp="cl-dev-03", roster="L001,L002,L003",
                               pred_desc="the dev-03 pilot",
                               date="Mon 16 Nov",
                               issuable="**Not issuable ahead:** it is issued only after the lead's hand-read records the pilot's R9 PASSED and its class A smoke MET (L002 released its G0), RL-173 D.4.",
                               extra=dev03_rest),
    "ITEM-dev04-s01.md": dict(pred="dev-03-s02", camp="cl-dev-03", roster="L004,L005,L006,L007,L008,L009,L010,L011,L012",
                              pred_desc="dev-03's remainder",
                              date="Tue 17 Nov",
                              issuable="**Not issuable ahead of the dev-03 pilot's hand-read** (RL-173 D.4): its gate needs dev-03's R9 PASSED and class A smoke MET, and its predecessor `dev-03-s02` is itself issued only after that hand-read. Once both are recorded it may be issued together with ITEM-dev03-rest.",
                              extra=lambda t: dev0405(t, "cl-dev-04")),
    "ITEM-dev04-s02.md": dict(pred="dev-04-s01", camp="cl-dev-04", roster="L001,L002,L003,L004,L005,L006",
                              pred_desc="dev-04's first span",
                              date="Tue 17 Nov",
                              issuable="**Not issuable ahead of the L005 gate** (RL-173 D.4): it is issued only after `dev-04-s01`'s Check records L005's G0 outcome (released, or dev-03 released at least four of its five consumers).",
                              extra=lambda t: dev0405(t, "cl-dev-04")),
    "ITEM-dev05-s01.md": dict(pred="dev-04-s02", camp="cl-dev-04", roster="L007,L008,L009,L010,L011,L012",
                              pred_desc="dev-04's second span",
                              date="Wed 18 Nov",
                              issuable="**Not issuable ahead of dev-04's L005 gate** (RL-173 D.4): it follows `dev-04-s02`, which is itself behind that gate.",
                              extra=lambda t: dev0405(t, "cl-dev-05")),
    "ITEM-dev05-s02.md": dict(pred="dev-05-s01", camp="cl-dev-05", roster="L001,L002,L003,L004,L005,L006",
                              pred_desc="dev-05's first span",
                              date="Wed 18 Nov",
                              issuable="**Not issuable ahead of dev-04's L005 gate** (RL-173 D.4), and only within the three-ahead cap.",
                              extra=lambda t: dev0405(t, "cl-dev-05")),
}


def main():
    for name, it in ITEMS.items():
        t = (SRC / name).read_text()
        t = apply_common(t, it)
        t = it["extra"](t)
        (DST / name).write_text(t)
        print(f"{name}: written, {t.count('<LEAD FILLS')} LEAD FILLS left")


if __name__ == "__main__":
    main()
