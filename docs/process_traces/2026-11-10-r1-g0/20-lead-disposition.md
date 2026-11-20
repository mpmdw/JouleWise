# Lead disposition: R1 G0 ruling (magistrate 5515349e, Opus 5.5), 2026-11-10 19:45 PST

Inputs: `10-fable52-ruling.md` (Fable 5.2, ruler), `11-sol-findings.md` (Sol 6.1
xhigh, finder), blind to each other.

**Adopted: Fable 5.2 ruling sections 1, 3 and 7 as written, including its late revision (A-B-A legs and d-4bit arm their deadman after G0).** Under Ed's 11-10
rule, Fable 5.2 has the final say on paper-bound work.
1. R_op: the WP14(b) pre-warmup 60 s median of the accepted step-30b member
   becomes the reference for every later R1 gate.
2. δ_slow = 1.5 C as slot S6, with a tuning receipt from S5 = 1.0. This follows
   the registered 0.5 C ladder (maximum 2.0 C).
3. The G0 cap is 1,200 s for every model member.

Bounds and `window_max_s` are recomputed from these values.

**Agreement between the seats.**
- Both found the reference/operating-point mismatch, about +1.06 to +1.08 C.
- Both found that changing the reference alone still times out at 600 s.
- Both chose 1,200 s, the existing ceiling, for step-30b.
- Both rejected swapping s_slow, sizing the band from spread, and per-member
  self-capture as a general rule.

**Dissent recorded (Sol):** keep δ_slow at 1.0 C and test the 1,200 s cap with
explicit censoring, so that the band is not widened to admit the recorded tail.
Fable's tail models (A to D) put release at 907 to 1,299 s with 1.0 C and
1,200 s, so two of the four models would time out. 1.5 C is the smallest
registered step that fits within 1.25 x the longest predicted wait. The night
records each tail down to 1.5 C, so the 1.0 C gate can be replayed exactly
afterwards. That replay answers Sol's concern without spending another night.

**Sol's F2 (the energy cost of residual heat is not bounded at 1 J)** stands
as a known limit. R1's designed start states measure β_T, and the registered
U5 check is evaluated at 1.5 C (Fable 7.7).

**NR-1 (which reference the gated D runs and X-G use): deferred** to the v4
window design council (item 252) before W1. Fable shows that an R1 night can
run first: unreleased gated runs are recorded as inconclusive, and the 1 Hz
tails allow either reference to be replayed. The build keeps the current
mechanism for those runs, with R_op substituted for the soak mean. It adds no
new refusal.

**Path:** build on a branch from `20e9edbc4`, then an executing review, cold
passes (Fable and Opus, blind, executing) and CI. Then re-pin `$M` and re-arm
R1 with a fresh custody root and an arm notice. Zero the kernel frequency
word first (item 251).
