# cl-dev-01 counted pilot (L001-L003): desk, hand-read and RL-150 R9

Desk builder for the lead, on the Air, 2026-11-14 16:36-16:45 PST. Lead's verdict recorded 2026-11-14.

- **Span:** `cq-dev-01-s01-a1`, 14:44:43-16:22:39 PST.
- **OUT:** read-only copy at `/Volumes/JW-EXT/cadence-desk/cl-dev-01/cq-dev-01-s01-a1-20261114T224427Z/`.
- **Code:** `b4b6aeb19`.
- **Kit:** cl-dev-01 at `589748f15`, sha256 c76344c5…66d7, which matches.
- **Blinding:** no energy, power, meter-sample, powermetrics, transcript, slot, KM003C-stream or hazards file was opened. Every open is listed in OPENED.txt (37 lines). Each opened file was key-scanned for energy, power, joule, watt, mW, slot and transcript, and none matched.

## Automatic desk
Command: `scripts/air/cadence_desk.py build --plan-id cq-dev-01-s01-a1 --input <OUT>/desk-bundle --out auto/ --kit kit.json`, run under AIR-QUIET.lock. rc 0, and `stops.json` is `[]`.

| leg | band | reached | G0 s | G0 | wall s | budget | attempts | redos | OS max | nominal | admitted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L001 | q0 | True | 205.9 | released | 1251.5 | 1251 | 1 | 0 | 2 | False | True |
| L002 | q0 | True | 210.2 | released | 1253.2 | 1251 | 1 | 0 | 2 | False | True |
| L003 | q0 | True | 205.1 | released | 1251.4 | 1251 | 1 | 0 | 2 | False | True |

- **Result:** COMPLETE, MEASURED_OK, chain_exit_code 0.
- **KM003C supervision:** 29,375 polls, 0 bad, proven stopped.
- **Inclusion source:** the JOURNAL-TABLE has no admitted column (F8 not built), so inclusion comes from desk_summary.json `admitted`.

## Hand table
Built independently with hand_table.py from the receipt, span_plan, chain-stages, leg_record, the thermal journals and load_journal.json (key-checked).

**Per leg, all three:**
- 1 attempt, no redo;
- G0 released (205.934 / 210.218 / 205.062 s), band q0 reached, with the turn starting about 0.08 s after release;
- decode 4,096 of 4,096, complete;
- wall/budget 1.00.

**Rules, all three legs:**
- rules 1, 2 and 6 hold;
- rule 5 recomputed: no sustained load over 0.5 core for 60 s; the longest runs are 1 s, 1 s and 6 s;
- rules 3 and 4 are judged at a look.

**Included:** all three. **Named stops:** none.

**Span level:**
- receipt rc 0, 25/25 steps rc 0;
- soak rc 0, 1,800.5 s, reference TV0h = TV1h = 34.051 °C, settled;
- feeds proven stopped;
- restore powermode 0 ok;
- agent census: 195 polls, all empty;
- volume census 6/6;
- deadlines empty;
- no open cadence-stop issue.

## Comparison
- **Value differences: none,** inclusion included.
- **Scope differences, not disagreements:**
  - the desk has no inclusion column;
  - "reached" is derived differently, with the same result;
  - rules 3 and 4 are left for the look;
  - the desk omits restore lines and censuses, which the hand table carries clean.

## RL-150 R9: PASS
1. All three legs closed with complete records.
2. 3 of 3 admitted.
3. No exclusions.
4. Hand table and desk agree, inclusion included; no stop open.

`pm_nominal: false` and `os_level_max: 2` are OS thermal-pressure status (about 41-49 % of turn readings at Heavy). They are not the power mode, and RL-149 §2.4 drops no leg for OS level, state or heat.

## RL-156a check
**Lead's reading:** the pilot's R9 record shows no sampler starvation and no inventory gap.
- **Thermal sampler:**
  - Every 1-s cell holds a reading.
  - Max intervals are 1.10, 1.17 and 1.06 s; 0 read errors.
  - Disclosure: `phase_coverage` reports `max_consecutive_empty_cells` 2 for L001 and L002, because readings sat 103-226 ms off the grid (the metric's tolerance is 100 ms). Those cells are before G0 or after the turn, never in G0 or in the turn. This is jitter, not starvation.
- **Load sampler:** max gap 1.27 s against a 5 s bound.
- **Inventory:** the R1 ProcessInventory journal is not run by the cadence-leg kind (`CadenceLegSegment.run` never calls `start_inventory`). So the code behind the CI `test_r1_followup` ProcessSampler red is not executed by dev-01 or dev-02 legs at all. The lead takes this as support for RL-156a §1's reading and tells the research lead.

## RL-150 R1 part 3 print (gates nothing)

| | TV0h | TV1h | Tf08 |
|---|---|---|---|
| soak ref (Tf08 last 1,200 s mean) | 34.051 | 34.051 | 25.847 |
| L001 own ref / G0 release | 34.104 / 34.823 | same | 26.480 / 34.189 |
| L002 own ref / G0 release | 34.712 / 35.019 | same | 32.776 / 36.192 |
| L003 own ref / G0 release | 34.703 / 35.089 | same | 32.660 / 36.686 |

TV0h = TV1h in every reading, so nothing routes under RL-149 §5 item 6.
