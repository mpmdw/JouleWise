# Cold-gate packet 24 — contract prose for the epoch-representation allowances (GATE-SENSIBILITY-SWEEP-01, PR #314)

Mechanically assembled by the resident magistrate (activation 96bfeca7) at 2026-09-10 ~05:25 PDT from the sweep branch head
`58d4696b`. Trigger (rule 11, mandatory): the same defect signature — a contract paragraph failing the first-use / replication
bar — survived two consecutive fix rounds on the same two paragraphs (round 2 `58d4696b` answered Opus refuter 21 F2/F4;
delta refuter 23 then found F1/F2/F3 in the rewritten text). The next spend is a consult, not round three.

## The question for the cold seat

Produce the FINAL replacement text for the two paragraphs in Exhibit A (A1 admission containment; A2 cooldown completion
allowance) such that every clause is true of the code in Exhibit B and a reader can rebuild the predicate from the text alone,
with every term of art defined at or before first use (Ed's writing standard: build from physical reality or gloss at first
use; no word does unpaid work). Also rule on one design point raised by Exhibit C F1: the coverage rounding allowance in
`cooldown_gate` is `max(1e-6 s, Σ over positive-overlap readings (ulp(evidence_end) + ulp(clipped_start)) + ulp(coverage_s))`,
which grows with the number of retained readings (13.35 μs at `subwindow_s = 0.75` with 40 readings; ~3.3 μs at the
production `subwindow_s = 5.0` with ≤ 7 readings). Options: (i) keep the code and write prose that states the growth
honestly and bounds it (e.g. "two representable steps per retained reading; at the production policy at most about 3 μs;
always at least four orders of magnitude below one 100 ms sample"); (ii) add a hard ceiling in code (e.g. `min(…, 1e-4)`)
with a defect-shaped test, so a fixed number can be promised; (iii) something better. Give a recommendation with reasoning
sized to the instrument (~100–115 ms sample cadence; ~1 J attribution limit; D-161: fail-closed stays for physics/evidence).

## Exhibits

- `exhibit-A-paragraphs.md` — the two paragraphs as they stand at 58d4696b.
- `exhibit-B-code.md` — `environment_admission.py` (constant + predicates), `controller.py::cooldown_gate` (retained-readings
  loop, rounding accumulation, completion tests), `schemas.py` cooldown policy fields.
- `exhibit-C-delta-refuter-23.md` — delta refuter findings F1 (10 μs coverage claim overstated; reproduction with
  `subwindow_s=0.75`, 40 contributions, 13.35 μs missing coverage recovers), F2 (evidence end / clipped start undefined),
  F3 (duration vs timestamp comparison conflated in A1).
- `exhibit-D-opus-refuter-21.md` — Opus contract/physics lens summary (lens 1 arithmetic: ulp(1.789e9) = 2.384e-7 s;
  production worst case 7 readings → 3.34e-6 s; a full 0.1 s sample would need 209,715 readings in a 30 s window).
- `exhibit-E-seat-A-inventory-02a.md` — the design source (§B R1/R3: why 1 μs; precedent `uncertainty_evidence.py:45–59`).

## Constraints on the ruling

- Prose only for A1 unless a code clause is false. For A2, option (ii) is permitted if you rule it; then give the exact code
  line and the test's admit/refuse inputs.
- Do not change any physics-sized barrier (one 100 ms sample refuses; 30 s span; 80 % coverage; 300 s cap_hit).
- The ruling file is `10-coldgate-fable-ruling.md` in this directory: verdict per finding (F1/F2/F3 of Exhibit C), the
  replacement text for A1 and A2 verbatim inside fenced blocks ready to paste, the design ruling on (i)/(ii)/(iii), and an
  "Executed probes" section with every command you ran and its output.
