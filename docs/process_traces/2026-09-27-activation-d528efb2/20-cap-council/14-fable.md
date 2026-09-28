SEAT: Fable 5.1 — CAP-COUNCIL-25G83-01

Preloaded, not chosen: the harness injected the owner's global and project instruction files and the memory index; I opened none of them, nor any barred file.
Values seen: the ruling's table prints all 20 B values; my own scripts read cells, frame lengths, clock stamps and compute time only. No repository file changed. Scratch and raw outputs: `/tmp/cap-council-d528efb2/fable/evidence.md` (E1–E4).

**Words.** *Frame*: one power sample (asked 100 ms, delivered ≈128–130 ms). *Cell*: one rectangle of candidate pulse-edge timings the estimator tests. *Cap*: the limit on cells per capture. *Need*: cells a healthy capture uses when the cap is lifted. *B*: the one timing-uncertainty number a capture yields.

## 1. What the cap is for

It is a runaway guard, nothing else. The estimator maps which edge timings fit the data by splitting a 1.5 s × 1.5 s square down to 0.1 ms cells (`powermetrics_fiducial.py:73,76,657–696`). If the data cannot rule timings out (a "flat" surface), one pulse alone costs (1.5 s ÷ 0.1 ms)² = 225,000,000 cells. The code says the cap exists to stop that "after finite reproducible work" (`:84–85`). The cell count is preferred over a time limit because it gives the same verdict on any machine; the 120 s wall deadline is only a backstop (`decision_log.md:10162–10171`). It is not a memory or quality gate: it cannot change a finished B (A1 §2).

Measured by me (E1): healthy pulses need 1,073–4,255 cells each; a cell costs 10.6 µs; the whole 165,000-cell cap buys 1.8 s of a 13.8 s estimator run. So healthy work (~10⁵ cells) and a runaway (≥10⁸) are three orders of magnitude apart, yet the cap sits inside the healthy range (members used 87–99 % of it). **The purpose does not need a number near the need.** No formula is required either: a constant placed by the purpose covers every cadence in the registered regime. A formula costs the same D-138 event (one pinned-file change, one re-issue) but adds a code path and makes the verdict depend on a per-capture measurement. I advise against it.

## 2. Route

**Route R, sized top-down** (§3). Cost: one D-138 transaction plus two non-claim windows of 12 slots (about 2 h each; W1 and W2 both ran on one day, E3). About 2–3 days with gates. Route M costs no transaction but loses a third of captures in every window forever, about 44 % bracket completion on the cap alone (A1 §6 N-3), and leaves the claim conditional.

## 3. The sizing rule (written before any value)

Symbols: *n*, *F* = a capture's need and median frame length. *t* = slowest measured seconds per cell, *T* = slowest measured estimator time outside the cell loop, both from replaying stored captures on the measurement machine.

1. **Ceiling from purpose.** K₁ = (60 s − T) ÷ t, so the reproducible stop fires with half the 120 s deadline unused. K₂ = 1 % of 225,000,000. **Cap = the smaller of K₁ and K₂, rounded down to 100,000**, frozen as an integer.
2. **Covered range: 100 ms ≤ F ≤ 150 ms.** 100 is the requested interval (`:66`); 150 is the registration's existing cadence stop (registration line 612).
3. **Coverage check.** Growth exponent p = the largest ln(need ratio) ÷ ln(frame ratio) between any two capture groups whose median frames differ by ≥ 1.5 ms. Every capture's n × (150 ÷ F)ᵖ must be ≤ Cap ÷ 2. On failure the upper range limit is lowered until it passes; the cap is never raised past step 1.
4. **Outside the range** the estimator still runs, the capture is flagged by cause and is not used as member or bracket until the council extends the range with data taken at that frame length.
5. **Tripwire.** Every harvest reports the largest n ÷ Cap. Above 50 %: re-sizing review before the next claim window. Any cap stop inside the range: claim windows halt.

**Evidence allowed:** cells and frames of the 34 August captures (frames recomputed from archived raw bytes), the 20 W1/W2 captures, and the launch-context files if they hold pulse captures; compute time. No B. Compute time is not a cell count; I add it openly because the purpose is a time bound.

**How it avoids the trap.** August sized upward from need, so any cadence shift could reach it. This rule sizes downward from the purpose, and uses need only to check a stated range. Illustration, not the value: t = 10.6 µs, T = 12.5 s give K₁ ≈ 4.5 million, K₂ = 2.25 million, Cap 2,200,000; worst scaled need at 150 ms with p = 7.55 is 549,917 (E2).

## 4. Membership

Two steps.

- **Interim: the same 12, B unchanged**, re-issued inside the cap transaction (precedent: D-143's in-place re-issue). Gate: the new bytes reproduce all 12 B to the last digit. The 8 never enter: their ledger rows are immutable, and adding them is known to lower C from 19.021 to 17.118 ms (ruling §2.3). A choice whose benefit is known beforehand is not blind.
- **Final: a fresh corpus.** The ≥ 24 non-claim captures are required anyway; register them as a successor derivation that replaces the interim whatever it shows. Reason: the 12 are 25 % long-frame against 45 % in the unfiltered population that brackets will come from once the cap lifts (A1 §5.2). Extra cost: one registration and one plain issuance.

## 5. Order

1. Issue `dbad7cc7` unchanged (B1–B4).
2. Council rules in writing: sizing rule, membership, clock cure.
3. Compute cells, frames, time; fix the value; run the coverage check.
4. One D-138 branch: the cap, plus any staged estimator branch that passed its gauntlet and reproduces the 12 B exactly. One staleness event, not five. What those branches change: NOT EXECUTED.
5. Execute it; interim re-issue.
6. Three-family audit now, on final estimator bytes and before the fresh captures, so a finding cannot stale the new corpus. (Directive #416 known only as charged.)
7. Two non-claim windows under the new cap; zero cap stops.
8. Successor issuance; written ruling closes the hold.

## 6. Clock steps: cause found, no capture needed

The capture stamps already in custody show it (E3). The wall clock's offset from the monotonic clock drifts smoothly at 4–8 ppm, then jumps 5–53 ms while its rate changes. Six jumps in the 4 h of windows: three inside captures (the three exclusions), three in gaps. The system log names the source (E4): the macOS time daemon `timed` fetched network time and applied **+0.053198 s at 01:53:09** (inside w1-d08) and **−0.035939 s at 10:11:29** (inside w2-d07), rescheduling itself 26.5 minutes ahead each time. Captures occupy 197 s, so 197 ÷ 1,590 = 12.4 % should be hit; 3 of 24 is 12.5 %. Sleep is excluded: one step is negative.

The network time itself is logged as ±0.02 s, so these corrections are the size of its own noise. **The 5 ms limit is sound physics**: a step displaces wall-stamped pulse commands against frames by its full size, healthy drift is ≤ 1.54 ms, and S is 13.7 ms. Keep it. Cure the cause: switch network time off for the window and restore it after (captures taken that way exist, `uncertainty_evidence.py:57–58`). That needs sudo, an owner action. NOT EXECUTED: the log for the other four corrections.

## 7. Where I disagree

- **A1 §5's line** is fitted across two clusters 1.8 ms apart. Carried back to 120.2 ms it predicts 96,024 cells, below every August capture (minimum 112,205). Growth looks like a power of 3.4–4.2 between epochs and 7.6 within this one (E2), so the line could under-predict. Its conclusion stands; its numbers should not be reused.
- **H2's word "re-sized"** assumes sizing from need. That, not the 20.3 %, was August's error. D-143's own record warned "Recalibrate on any new … cadence class" (`03-budget-calibration-sweep.md`, flag F1), and nothing was installed to trigger it. Hence the tripwire.
- **H4 "the same kind of filter"**: only partly. The clock steps follow a daemon's timer, not machine load (inference), so they thin captures at random. Record by cause, but the risk is lower than the cadence filter's.
- **D-078's cost figure** of 2.7 µs per cell came from a synthetic trace; real traces cost 10.6 µs, and the deadline clock starts before the 12 s of fitting (`powermetrics_fiducial.py:976–979`). The backstop margin is about 60×, not 440×.
