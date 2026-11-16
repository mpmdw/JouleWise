# dev-03-s02 desk (cq-dev-03-s02-a1, L004-L012, kit cl-dev-03.v1.1): hand table, rule 5, maintenance overlap, dev-04-s02 gate facts (PROPOSED)

Desk builder for the lead, on the Air. Verdicts below are PROPOSED; the lead signs them.

- Span `cq-dev-03-s02-a1`, nine legs L004-L012, kit `cl-dev-03.v1.1` sha256 `0f535774...e14b`, runner `cadence-legs-v1.1`, batch window `02:00-02:35`; receipt epochs 1794844338-1794856578 (RUN_STATE 369 launch, 370 Check; work order 366). Receipt rc 0, MEASURED_OK, chain COMPLETE, 37/37 steps rc 0, restore observed 0.
- Data: read-only Air copy, 324 manifest entries sha256 OK, `.air` = `.mbp`. Desk code `2d347f721` (clean before and after), kit outside the checkout.
- Blinding: every open is in OPENED.txt; no energy, power, meter-sample, powermetrics, transcript, slot, hazards or telemetry file was opened.

**Desk: FINAL.** automatic desk = hand table on every value: 0 of 171 per-leg and 0 span-level values differ; 9 of 9 included by hand, 9 of 9 admitted by desk; stops.json [] and hand stops []. No named stop open. 9 of 9 admitted by the desk, 9 of 9 included by hand; no excluded leg, no redo, none refilled.

| leg | cell | G0 shape | G0 role | G0 s | wall / budget s | OS max | rule 5 longest run (s of 60) | realized prefill |
|---|---|---|---|---|---|---|---|---|
| L004 | 10,000 | span | capture | 205.0 | 1,133.3 / 1,156 | 2 | 1 | 10,015 (+0.15 %) |
| L005 | 2,000 | own | capture | 152.9 | 982.0 / 1,076 | 2 | 3 | 2,024 (+1.20 %) |
| L006 | 19,458 | own | capture | 204.1 | 1,255.4 / 1,251 | 2 | 12 | 19,458 (+0.00 %) |
| L007 | 10,000 | own | capture | 221.2 | 1,151.8 / 1,156 | 2 | 11 | 10,015 (+0.15 %) |
| L008 | 2,000 | span | consume | 149.9 | 983.2 / 1,467 | 2 | 2 | 2,024 (+1.20 %) |
| L009 | 19,458 | span | consume | 211.1 | 1,255.3 / 1,642 | 2 | 2 | 19,458 (+0.00 %) |
| L010 | 2,000 | span | consume | 145.6 | 973.8 / 1,467 | 2 | 2 | 2,024 (+1.20 %) |
| L011 | 19,458 | own | capture | 211.1 | 1,256.9 / 1,251 | 2 | 2 | 19,458 (+0.00 %) |
| L012 | 10,000 | span | consume | 213.2 | 1,138.6 / 1,547 | 2 | 4 | 10,015 (+0.15 %) |

L004 is span-shaped but first in its span, so it captures the span's reference (record sha256 `3692d95c...fc44`, status captured); L008, L009, L010 and L012 consume it (reference source `cadence-cl-dev-03-l004`, record sha equals L004's own window-reference record sha on all four; G0 row reference fast_c and span_ns equal L004's capture). L005, L006, L007, L011 judge against their own capture. LEG_OVERTIME: no (max wall/budget 1.0047; L006 +4.4 s and L011 +5.9 s over budget_s, far under 1.5x).

## Rule 5 judgements (load-journal sustained-load test, > 0.5 core held 60 s)
All nine pass; hand recomputation equals each recorded os_load; no redo owed. L004 1 s, L005 3 s, L006 12 s, L007 11 s, L008-L011 2 s, L012 4 s of the 60 needed.
- **L006**: the item-370 `mobileassetd` burst (1,360 lines at 09:21) falls in L006's turn; longest run 12 s (max 2.642 cores). Does not fire; recorded clean.
- **L012**: the XProtect + softwareupdated + mobileassetd burst (5,230 lines at 11:09) falls in L012's turn; longest run 4 s (max 3.296 cores). Does not fire; recorded clean.
Both bursts touch a turn (unlike the pilot's, which was post-turn); the kit says no leg is dropped for outcome and rule 5 is the sustained-load test, so both stay in. See MAINTENANCE-OVERLAP.md and RESULT.json `maintenance_overlap`.

## dev-04-s02 gate facts (RUN_STATE 367; ITEM-dev04-s02.md lines 11 and 18)
Wording (RL-165 s4, RL-167): if dev-04-s01's L005 released its G0, dev-04-s02 arms on its own gates; if L005 timed out, it arms on the lead's record only if dev-03 ended with at least four of its five consumers released (L002, L008, L009, L010, L012); fewer than four, it does NOT arm. RL-173 D.4 issues it only after dev-04-s01's Check records L005's G0 outcome (released, or dev-03 released at least four of its five consumers).

| consumer | span | G0 | wait s (timeout 1,200) | released against span reference | reference source |
|---|---|---|---|---|---|
| L002 | dev-03-s01 | released | 209.1 | True | cadence-cl-dev-03-l001 (L001 a1) |
| L008 | dev-03-s02 | released | 149.9 | True | cadence-cl-dev-03-l004 (L004 a1) |
| L009 | dev-03-s02 | released | 211.1 | True | cadence-cl-dev-03-l004 (L004 a1) |
| L010 | dev-03-s02 | released | 145.6 | True | cadence-cl-dev-03-l004 (L004 a1) |
| L012 | dev-03-s02 | released | 213.2 | True | cadence-cl-dev-03-l004 (L004 a1) |

dev-03 consumers released: **5 of 5** (threshold 4). Reference records: pilot L001 `1675f044...bf6e`, this span L004 `3692d95c...fc44`. L005's own G0 outcome: not yet recorded (dev-04-s01, item 367, has not run; it cannot arm before 00:00:00 PST Tue 17 Nov).

**L005 gate: MET (proposed).** Met on the dev-03 count alone (5 of 5 against 4), sufficient whether L005 releases or times out. The lead signs.

## Q1 print
`hand/r1print.out` (soak reference TV0h = TV1h 34.177 C; L004 capture 34.201 C; consumer release readings and G0 waits). Completion record: `evidence/cadence-standing/q1/cq-dev-03-s02-a1.json`. No leg is more than 5 % from its nominal prefill.
