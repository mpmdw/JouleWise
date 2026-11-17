# PROPOSED — dev-04-s02 desk (cq-dev-04-s02-a1, kit cl-dev-04.v1.1)

Desk builder for the magistrate lead, on the MBP. All verdicts are PROPOSED; the lead re-executes this desk and signs.

**Desk: FINAL.** 0 of 114 per-leg and 0 span-level values differ; 6 of 6 included by hand, 6 of 6 admitted by desk; stops.json [] and hand stops []. No named stop open in this span. No leg excluded, none refilled. No redo.

- Data: MBP original `/Users/edr/campaign-out/cl-dev-04/cq-dev-04-s02-a1-20261117T112332Z`, read-only; **221 of 221 manifest entries sha256 OK**, 0 failed. Manifest `/Users/edr/night-custody/offload/cq-dev-04-s02-a1/cq-dev-04-s02-a1.SHA256SUMS` (sha256 `e60459cd7887ae14ba2e37070782f643befa0562e43308d1f9012313a7a43dcc`). Every `./` entry maps directly under the original span directory. No `.air` copy and no `.air`/`.mbp` comparison.
- Kit: `git show fecaf73f3:docs/process/cadence/kits/cl-dev-04.v1.1.json` to `.desk-scratch/cl-dev-04.v1.1.json`; sha256 `1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228` asserted.
- Desk code: `/Users/edr/code/jw-wt/desk-pin-2d347f721` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`; git status empty before and after (saved in `hand/desk-code-status-before.txt` and `hand/desk-code-status-after.txt`). Interpreter `/opt/homebrew/bin/python3.13 -I -B`; `--kit`, never `--adapter`; TMPDIR and explicit lock under this worktree’s `.desk-scratch/`.
- Blinding: `hand/keyscan.py` ran before hand opens; exact inputs in `hand/keyscan.list`, output in `hand/keyscan.out`; hits power-MODE keys only (`ac_powermode`). Every open is logged in OPENED.txt. Sealed files were hash-checked only; no energy, power measurement, hazard, transcript, slot or telemetry content opened.
- Receipt: rc 0, MEASURED_OK / COMPLETE, 31/31 steps rc 0; restore observed 0; 9/9 PASS; agent census 294 polls, 0 hits. Epochs 1794914623.557641–1794923463.325451; batch window `02:00-02:35`. No 00:00 crossing.

| leg | cell | G0 shape | G0 role | G0 s | wall / budget s | OS max | rule 5 longest (s of 60) | realized prefill |
|---|---|---|---|---|---|---|---|---|
| L007 | 2,000 | own | capture | 132.5 | 959.2 / 1,076 | 1 | 3 | 2,024 (+1.20 %) |
| L008 | 19,458 | span | consume | 205.0 | 1,251.2 / 1,642 | 2 | 2 | 19,458 (+0.00 %) |
| L009 | 10,000 | span | consume | 213.2 | 1,139.9 / 1,547 | 2 | 1 | 10,015 (+0.15 %) |
| L010 | 2,000 | span | consume | 147.9 | 977.0 / 1,467 | 2 | 4 | 2,024 (+1.20 %) |
| L011 | 19,458 | span | consume | 215.3 | 1,259.3 / 1,642 | 2 | 3 | 19,458 (+0.00 %) |
| L012 | 10,000 | span | consume | 217.2 | 1,145.1 / 1,547 | 2 | 2 | 10,015 (+0.15 %) |

L007 captures the span reference (status `captured`, source `cadence-cl-dev-04-l007`, record sha256 `0311a7c45acb8b9267a088155543b1b2c1f33c8bd097ed746619a6be4b597f0b`). Consumers’ source, record sha256, fast_c and span_ns agree with this capture; every consumer check is true. Consumers write no own window reference. See hand/hand_table.json for all 19 exact comparisons per leg.

Comparison is exactly the template’s: G0 seconds round to six decimal places, wall seconds to one decimal place, every other pair uses equality. No new tolerance. Realized prefill is separate from the desk’s nominal kit count; no leg exceeds the standing 5% prefill print threshold. OS levels and pm_state are printed, with kit no_drop_by_outcome retained.

LEG_OVERTIME: **no**; max wall/budget 0.8914, below the kit’s 1.5× limit (stop requires two legs). No leg exceeds budget_s.

## Rule 5 and maintenance overlap

MAINTENANCE-OVERLAP.md (RL-171 section 5; print only, gates nothing). Judged by the template's rule 5: >0.5 core held 60 seconds (consecutive journal samples); no_drop_by_outcome, no log-count exclusion.
L010.a1: software-update / MobileAsset scan 05:08-05:09 begins 05:08:45; XProtect and XProtectPluginService finish 05:09:03. Wholly inside L010 turn 05:04:17-05:09:50 (attempt 04:54:39-05:10:56; G0 05:01:49-05:04:17). Within turn: softwareupdated 2,597, mobileassetd 2,045, XProtect* 899 = XProtectPluginService 843 + XProtect 56. This agrees with item 382, whose 843 count explicitly names XProtectPluginService; the template groups both under XProtect*. Tails: mobileassetd 11 and softwareupdated 22 during L010 post-turn (05:09:50-05:10:56), and sparse entries later in L011 pre-G0 (05:13), shown in minute output. Longest >0.5-core run is 4 samples, 05:09:53-05:09:56 (914.2-917.2 s), post-turn; run max 1.013 cores, attempt max 2.361. Does not fire; recorded clean; no redo owed.
All six counted attempts pass: L007 3, L008 2, L009 1, L010 4, L011 3, L012 2 samples of the 60 required. All load journals cover their attempts. No redo, no leg excluded, none refilled; maintenance overlap does not independently exclude a leg.

The template counts consecutive >0.5-core samples as seconds; reported sample endpoint spans and integer run counts are both retained. No alternative elapsed-time bar was introduced. Every attempt’s journal coverage and recorded os_load agree with hand recomputation. Rules 3/4 remain at the look as in the template; receipt instrument-health fields are not a live hardware-validation claim.

See MAINTENANCE-OVERLAP.md for leading-field counts by attempt and phase, hand/maint_burst.out for minute counts, and hand/rule5_place*.out for load-run clock placement.

## dev-04 consumer releases

| span | consumer | G0 outcome | wait s | released against span reference | reference source |
|---|---|---|---|---|---|
| dev-04-s01 | L005 | released | 151.9 | True | cadence-cl-dev-04-l001 (L001 a1) |
| dev-04-s02 | L008 | released | 205.0 | True | cadence-cl-dev-04-l007 (L007 a1) |
| dev-04-s02 | L009 | released | 213.2 | True | cadence-cl-dev-04-l007 (L007 a1) |
| dev-04-s02 | L010 | released | 147.9 | True | cadence-cl-dev-04-l007 (L007 a1) |
| dev-04-s02 | L011 | released | 215.3 | True | cadence-cl-dev-04-l007 (L007 a1) |
| dev-04-s02 | L012 | released | 217.2 | True | cadence-cl-dev-04-l007 (L007 a1) |

**6 of 6 dev-04 consumers released.** L005 released, so its gate holds on that direct fact. L008-L012 released against L007; dev-04 completed span-reference development through its second span. Both reference legs ran attempt 1 and were neither redone nor excluded.

## dev-05 draft gate lines and facts

audit ref and worktree item-drafts-1118/ plus nearby item-drafts*; no dev-05 drafts under 1118 (qualification items there); found current RL-173 D dev-05 drafts in 1115 and older nearby equivalents under rl172. All drafts are read-only. Full exact gate lines and facts, including nearby older equivalents, are in hand/gate_facts.json. These are inputs for the lead, not newly issued items.

| draft location | gate line reads | dev-04 fact |
|---|---|---|
| `item-drafts-1115/ITEM-dev05-s01.md:1` | EARLIEST and clean predecessor dev-04-s02 | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-1115/ITEM-dev05-s01.md:7` | VOID if predecessor dev-04-s02 not clean | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-1115/ITEM-dev05-s01.md:11` | RL-173 D.4: not issuable ahead of dev-04 L005 gate | L005 gate fact: released 151.9 s against L001 capture; Check item 380 agrees. dev-04-s02 ran and closed clean (item 382). Issuance remains lead-owned. |
| `item-drafts-1115/ITEM-dev05-s01.md:14` | dev-04-s02 closed and checked | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-1115/ITEM-dev05-s01.md:18` | dev-04 ran span-shaped to its end (RL-165 §4) | dev-04-s02 ran cl-dev-04.v1.1 L007-L012; L008-L012 released against L007 capture (5/5). dev-04-s01 L005 released 151.9 s against L001 capture; no fallback inference needed. |
| `item-drafts-1115/ITEM-dev05-s01.md:38` | arm-record line 6: prior named stops / restore | These dev-04 desks: auto stops [] and hand stops []; restore proven observed 0 and all close steps rc 0 in both spans. This is historical span evidence; current veto/halt/High Power and other spans remain fresh arm checks. |
| `item-drafts-1115/ITEM-dev05-s01.md:41` | arm-record line 9: two-back desk FINAL | dev-04-s01: proposed Desk FINAL; 0 of 114 per-leg and 0 span-level values differ; 6/6 hand included and desk admitted; stops [] on both sides. Expected ordinal 13 reads two-back span 11; lead verifies as-run ordering and signs. |
| `item-drafts-1115/ITEM-dev05-s01.md:56` | PRIOR_CLOSE_EPOCH: later of receipt close and fence-gone observation | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-1115/ITEM-dev05-s01.md:140` | pred_gate: dev-04-s02, roster L007-L012 | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-1115/ITEM-dev05-s02.md:11` | RL-173 D.4: not issuable ahead of dev-04 L005 gate | L005 gate fact: released 151.9 s against L001 capture; Check item 380 agrees. dev-04-s02 ran and closed clean (item 382). Issuance remains lead-owned. |
| `item-drafts-1115/ITEM-dev05-s02.md:37` | arm-record line 6: prior named stops / restore | These dev-04 desks: auto stops [] and hand stops []; restore proven observed 0 and all close steps rc 0 in both spans. This is historical span evidence; current veto/halt/High Power and other spans remain fresh arm checks. |
| `item-drafts-1115/ITEM-dev05-s02.md:40` | arm-record line 9: two-back desk FINAL | dev-04-s02: proposed Desk FINAL; 0 of 114 per-leg and 0 span-level values differ; 6/6 hand included and desk admitted; stops [] on both sides. Expected ordinal 14 reads two-back span 12; lead verifies as-run ordering and signs. |
| `item-drafts-rl172/ITEM-dev05-s01.md:1` | EARLIEST and clean predecessor dev-04-s02 | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-rl172/ITEM-dev05-s01.md:7` | VOID if predecessor dev-04-s02 not clean | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-rl172/ITEM-dev05-s01.md:13` | dev-04-s02 closed and checked | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-rl172/ITEM-dev05-s01.md:17` | dev-04 ran span-shaped to its end (RL-165 §4) | dev-04-s02 ran cl-dev-04.v1.1 L007-L012; L008-L012 released against L007 capture (5/5). dev-04-s01 L005 released 151.9 s against L001 capture; no fallback inference needed. |
| `item-drafts-rl172/ITEM-dev05-s01.md:37` | arm-record line 6: prior named stops / restore | These dev-04 desks: auto stops [] and hand stops []; restore proven observed 0 and all close steps rc 0 in both spans. This is historical span evidence; current veto/halt/High Power and other spans remain fresh arm checks. |
| `item-drafts-rl172/ITEM-dev05-s01.md:40` | arm-record line 9: two-back desk FINAL | dev-04-s01: proposed Desk FINAL; 0 of 114 per-leg and 0 span-level values differ; 6/6 hand included and desk admitted; stops [] on both sides. Expected ordinal 13 reads two-back span 11; lead verifies as-run ordering and signs. |
| `item-drafts-rl172/ITEM-dev05-s01.md:55` | PRIOR_CLOSE_EPOCH: later of receipt close and fence-gone observation | dev-04-s02 receipt rc 0, 6/6 run/admitted, MEASURED_OK / COMPLETE, close 1794923463.33 (05:51:03 PST); restore observed 0, close steps rc 0; desk and hand stops []. Fence-gone epoch is lead-owned and not inferred from receipt. |
| `item-drafts-rl172/ITEM-dev05-s02.md:36` | arm-record line 6: prior named stops / restore | These dev-04 desks: auto stops [] and hand stops []; restore proven observed 0 and all close steps rc 0 in both spans. This is historical span evidence; current veto/halt/High Power and other spans remain fresh arm checks. |
| `item-drafts-rl172/ITEM-dev05-s02.md:39` | arm-record line 9: two-back desk FINAL | dev-04-s02: proposed Desk FINAL; 0 of 114 per-leg and 0 span-level values differ; 6/6 hand included and desk admitted; stops [] on both sides. Expected ordinal 14 reads two-back span 12; lead verifies as-run ordering and signs. |

No fresh host, fence-gone time, watcher, stop-issue, issuance/expiry or global arm approval supplied by this desk.

## Q1 print

`hand/r1print.out`: soak_reference {'TV0h': 34.23355505307516, 'TV1h': 34.23355505307516} Tf08_last1200s_mean 27.685988540649415. L007 capture TV0h = TV1h 34.235 °C. Each consumer release reading and G0 wait is in RESULT.json RL158_Q1 and the print. none: L007 ran one attempt, was not redone and not excluded; no reference-from-redo or reference-from-excluded-leg mark. Completion record: `evidence/cadence-standing/q1/cq-dev-04-s02-a1.json` (PROPOSED desk-builder signer).

## Check agreement and findings

RUN_STATE item 382: hand table agrees with the recorded roster, releases, redo count, printed waits, max wall/budget, restore and clean receipt. No disagreement with the Check. The finer maintenance phase placement above uses the thermal journals, as the template does.

No data/kit/Check disagreement. XProtectPluginService 843 in item 382 and template-grouped XProtect* 899 are consistent (additional XProtect 56).

## Decisions I made

- Use L007 accepted attempt 1 as this span reference, as the kit/data and template first-leg rule determine; source cadence-cl-dev-04-l007.
- Use kit/data shapes and roles; L001 and L007 are own-shaped captures, L005 and L008-L012 consume their respective span reference.
- Keep hand_table.py numerical comparisons unchanged; no new tolerance or bar.
- Judge maintenance by rule 5 load-journal sustained runs, not log counts; retain kit no_drop_by_outcome.
- Keep all scratch including kit, lock and TMPDIR under .desk-scratch; pass --kit and an explicit scratch lock to pinned desk code.
- Use dev-05 drafts in item-drafts-1115 (RL-173 D); item-drafts-1118 contains qualification drafts. List nearby item-drafts-rl172 equivalents; do not edit or issue items.
- Earlier dev-02-s03 REPORT.md is absent at 4a53c34a4 and audit ref; use its committed RESULT.json, OPENED.txt, maint_judgement.txt and rule5_place_a1.py for the redo method.
- Count L007-L012 attempt 1; no redo or refill.

## Verification and handoff

Manifest hashes 221/221 pass; key scan pass; pinned automatic desk rc 0; independent hand table 0 of 114 per-leg values differ and 0 span-level differences; both stop lists []; sampler has 0 read errors and no cell with no reading (jitter details retained); status empty in pinned checkout before/after. No test suite run, per brief.

Replay commands and cwd/env are in hand/commands.json and OPENED.txt. Hand scripts are copied from the template: hand_table comparison unchanged, r1print adapted for dev-04 roster/capture; sampler/oslevel/maint_overlap/maint_burst/rule5_place/keyscan verbatim. build_result assembly adapted for these spans, redo evidence and consumer/draft-gate facts.

**NEEDS_RULING: none.** Next exact step: the magistrate lead re-executes and signs the proposed desk/Q1 records, verifies campaign ordering, then fills dev-05 draft gate lines under their own current arm rules. No arm authorization is created here.

**Commit handoff:** Sandbox blocked git add before any commit: fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/desk-dev04-cb24533b/index.lock': Operation not permitted (exit 128). No bypass attempted. Both spans and Q1 records remain untracked/uncommitted on audit/2026-11-17-desk-dev04; lead commits one span per commit, excludes .desk-scratch, and does not push on this desk's authority.

## Lead signature (magistrate cb24533b, interim lead under RUN_STATE 384 item 1), 2026-11-17 ~08:50 PST

**Desk: FINAL (signed).** Re-executed on the MBP into a separate scratch directory (custody `/Users/edr/night-custody/magistrate/desk-dev04-cb24533b/reexec/s02`): the kit from `fecaf73f3` (sha256 `1cc6673d…2228`); `scripts/air/cadence_desk.py build` at `2d347f721` gives an `auto/` byte-equal to this one except JOURNAL-TABLE.md's build-time line (that line's fixed text says "on the Air"; it ran on the MBP); `hand/hand_table.py` re-run gives a `hand_table.json` byte-equal to this one (diffs 0, desk stops 0); `shasum -c` of the offload manifest over the original span directory: all entries OK; desk checkout clean after. `hand_table.py` differs from the dev-03-s02 template in comments and the kit name only. Every per-leg G0 wait, the consumer releases, the L006 redo (s01) and the largest wall/budget agree with the magistrate's Check (RUN_STATE 380 / 382), which is separate code.
