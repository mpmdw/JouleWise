# cl-dev-01 sub-span s03 (L004-L007): desk hand-read

Desk builder on the Air, 21:18-21:28 PST on 11-14, by the pilot's method. Saved by the lead from the builder's hand-back (the builder could not write report files).

- **Span:** cq-dev-01-s03-a1, 19:03:13-21:01:49 PST.
- **OUT:** read-only copy at /Volumes/JW-EXT/cadence-desk/cl-dev-01/cq-dev-01-s03-a1-20261115T030242Z.
- **Code and kit:** code b4b6aeb19; kit c76344c5…66d7, matching the receipt.
- **Magistrate:** RUN_STATE 326 (RECEIPT OK, 4/4 admitted).
- **Blinding:** every file was key-scanned. The only hit was ac_powermode (the pmset mode). No energy, power, meter-sample, powermetrics, transcript or slot file was opened. The list of opened files is in ../OPENED.txt.

**Automatic desk:** rc 0, stops [], COMPLETE, MEASURED_OK; KM003C 35,574 polls, 0 bad.

| leg | band | reached | G0 s | wall s | budget | attempts | redos | OS max | nominal |
|---|---|---|---|---|---|---|---|---|---|
| L004 | q0 | T | 201.9 released | 1245.7 | 1251 | 1 | 0 | 2 | F |
| L005 | q0 | T | 209.0 released | 1253.1 | 1251 | 1 | 0 | 2 | F |
| L006 | q0 | T | 210.1 released | 1251.9 | 1251 | 1 | 0 | 2 | F |
| L007 | q0 | T | 200.0 released | 1244.3 | 1251 | 1 | 0 | 2 | F |

**Hand table** (the pilot's hand_table.py verbatim):
- All four legs: 1 attempt, 0 contaminated, decode 4096/4096, ac_powermode 0.
- Rules 1, 2 and 6 hold.
- Rule 5 recomputed: the longest run over 0.5 core is 7/4/2/2 s, under the 60 s bar.
- Rules 3 and 4 are left for the look.
- Included: 4/4. Named stops: none.
- Span level: 27/27 steps rc 0; soak rc 0 (TV0h = TV1h = 34.157 °C); restore ok; agent census 236 polls, 0 hits; volume census 7/7; deadlines empty; no open cadence-stop issue.

**Comparison:** 0 value differences, inclusion included. The scope differences are the same as the pilot's.

**DESK FINAL: hand table = desk (inclusion included), no stop open.**

**R1 part 3 print** (TV0h = TV1h everywhere):
- Soak reference 34.157; Tf08 27.026.
- Own reference / G0 release, TV0h:
  - L004: 34.172 / 34.861
  - L005: 34.730 / 35.052
  - L006: 34.767 / 35.062
  - L007: 34.714 / 35.109

**RL-156a:** no starvation and no inventory gap.
- Every 1-s cell holds a reading; maximum intervals 1.07-1.26 s.
- Disclosed: 6 cells read 103-298 ms off-grid, all after the turn.
- The cadence-leg kind does not run start_inventory.
