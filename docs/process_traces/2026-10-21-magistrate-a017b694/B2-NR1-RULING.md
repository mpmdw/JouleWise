# B2 NR1: lead ruling (activation a017b694, Opus 5.5, 2026-10-21)

Question (B2 round 4, `lane/2026-10-20-bytes-analysis-a8` 1d6f18fbf): a 5 to 9 µs clock-fit shift moved one whole
100 ms meter sample into every decode window of the resident world (5.87 J at 58.9 W). Is it a fixture defect or a real
effect the registered H2 DC-input and rest coefficient intervals must carry?

Council (record af419b16): Opus cloud seat (fixture knife edge; disclosure only) and Sol 6.1 xhigh (attribution effect;
propagate the whole of B as an alternative). They disagreed on a science question, so a cold Fable 5.1 judge ran
(JouleWise-data `claude/b2-nr1-judge-7n0s7d`, `reports/b2-nr1-judge/fable.md`, probes in `probe/`). The judge executed
254 synthetic campaigns through `archive_campaign` and the real `bytes_analyze --stage all`. No BYTES data exist, so the
ruling is prospective registration text.

## Ruling: the judge's section 1 is adopted as written

1. **Fixture** (judge section 4 diff): samples 50 ms inside the interval; science-run edges at a uniform random offset
   inside the interval on their own RNG stream; a 10 ms minimum receive latency on every batch. Each knob carries its
   derivation in the diff's comment.
2. **Registered H2 intervals unchanged** (coefficient ± t·SE_HC3, OLS beside it, k as Addendum 3.6).
3. **Labelled alternative** beside every H2 coefficient at DC input and rest: β_j ± (t·SE_HC3,j + C_j), with
   C_j = Σ_i |A_ji| · max(P_start,i, P_end,i) · (r_max,i + Δt_meter) / T_i, per-pass terms averaged as B is. Zero and
   sign statements at DC input and rest print both decisions. Rails has no C term.
4. **Disclosure** with the H2 DC/rest table: δ unmeasured (block-6 M13), structural bound 22 to 25 ms at 50 SPS, and
   dβ_j/dδ printed in J/GB per ms.
5. **Code:** Sol's `response_bounds` plumbing in `ols` with the judge's per-point substitution and field names
   (`coefficient_C`, `offset_intervals`, `offset_ols_intervals`, `resident_adds_nothing_offset`); the one regression
   `test_nr1_offset_term_covers_constant_label_offset` with its mutation check.
6. **Not adopted:** Sol's full-B box (120 to 470× the clean half-width; no cross-model coherence established for the
   drift, rails-anchor and h terms) and disclosure alone (the project's own δ bound puts the bias at 2.7 to 5.3× the
   clean half-width at 20 ms).
7. The fixture stays at 10 Hz, recorded as a flag in the round's report; the judge states its bias direction (the
   registered interval self-protects more at 10 Hz than it will at 50 SPS).

**Why adopt without change.** The judge reproduced both seats' numbers to the printed digit, located the 3.5× versus
164-454× disagreement in a denominator inflated by the defect itself (section 2.7), and introduced no new constant: the
time factor (r_max + Δt) is Addendum 1.2's, the 10 ms stress size is the recorded USB latency's lower end, and the
regression's bars are the Addendum 8 1% bar and a binomial 3σ on the flip fraction. Variant C (knob 2 alone changes
nothing) and variant B (knob 1 alone exercises the effect at zero) show why all three knobs are needed.

**Number check (CLAUDE.local "No silly numbers").** Every bar in the adopted text is derived: 1% of the HC3 half-width
(Addendum 8), 3σ binomial on δ/Δt, 50 ms (farthest from both edges), 10 ms (recorded latency). None is a seat's own bar.

## Follow-ups

- Sol 6.1 high fix round on `lane/2026-10-20-bytes-analysis-a8`: fixture, code, regression, Addendum 9 into
  `docs/design/bytes_pack_design.md`, and the 60-campaign test, p03 and CLI counterexample rerun (brief in the record).
- The registration draft (`docs/2026-10-20-bytes-registration`, `docs/registrations/bytes_pack_v1.md`) takes items 3
  and 4 at its H2 section and adds Addendum 9 to its authority list and §20 map.
- Merge path unchanged: B2, then B4, then B3 twin, B5 kit, item G; claim-path merges get cold Fable and Opus passes.

## Executed evidence

The lead re-ran the judge's probe for variant A (knobs 1+2+3, δ = 10 ms) on resident seed 3100, at the B2 lane head
`1d6f18fbf` in a detached worktree, with the judge's `probe/probe2.py` (JouleWise-data `claude/b2-nr1-judge-7n0s7d`),
on the Mac, `JW_B5_SYNTHETIC_ONLY=1`, fresh TMPDIR. Output kept at `/Users/edr/night-archive/a017-b2probe/`.

```
$ python3.13 -I probe2.py /Users/edr/code/JouleWise-wt-a017-b2probe resident 3100 on 50 10 1 resident_3100_on_ph50_L10_r1.json
wrote /Users/edr/night-archive/a017-b2probe/resident_3100_on_ph50_L10_r1.json
exit 0
```

Read back: 1,000 science runs; 119 have |meter − 2·rails| above half of one sample's energy at the edge power (a whole-
sample flip), fraction 0.119 against the expected δ/Δt = 0.10 (binomial σ = √(0.1 × 0.9 / 1000) = 0.0095, so +2.0σ,
inside the ruling's 3σ bar); largest error 5.856 J (one 100 ms sample at about 58.6 W); fitted label offset 9.991 and
9.995 ms on the two passes (the 10 ms knob). This agrees with the judge's variant A (flip fraction 10.1 to 10.5% per
world over 20 seeds; max error 5.878 J resident).
