# Synthesis 25 — cold gate QPE01-DAEMON-CONTAMINATION-01, round 2 (Q4 observer floor): SPLIT, refuter's factual finding VERIFIED, round 3 convened (magistrate a022aecc, 2026-09-23 00:35 PDT)

Inputs: charge 20 (sha `fbf4b9b9…`), Fable ruling 21 (`21-coldgate-fable-observer-floor-ruling.md`), Opus refuter 22 (`22-opus-contract-refuter-observer-floor.md`), exhibit D; this synthesis adds exhibit G (magistrate-executed).

## The split

- Ruling 21 AFFIRMS option (a) (a joule tolerance on the observer-floor stop branch) with corrected lineage for the rate (0.3194 W per core, a registered constant) and a rate-independent share ceiling of 0.10 cores; its regression (i) expects the cause ABSENT on both archived nights.
- Refuter 22 DISSENTS: (B1) the reported floor (0.053 cores) counts only the round's worker block and omits the 100 ms power recorder; the whole-envelope accounting the registration's own `observer_definition` describes gives 0.178 (clean night) and 0.161 (tonight) cores — three times the 0.05 level; (B2) so (a) gives no relief (16–19 J excess at any rate) and regression (i) would pin a wrong answer; (B3) in a paired idle-load-idle bracket a constant observer differences out, and the guard should be on the observer's arm-to-arm VARIATION (sd 0.0023–0.0028 cores across envelopes) against the level's own tolerance, not on joules — proposed option (f); (M3) `block_two.authored_after_pilot` is true and "holdable" is named but never defined, so the pilot is stopped by a placeholder of an unauthored block.

## Magistrate's verification (exhibit G, executed)

B1 is TRUE. `pilot_summary` sums `observer_cpu_s` (the round's worker block, ≈ 31.4 s per envelope) and never reads `whole_envelope_observer_cpu_s` (≈ 94–107 s, "including power recorder"). Whole-envelope floor over the same support: 0.17789 (clean night) and 0.16135 (tonight) cores; per-envelope sd 0.0023 / 0.0028 cores. The registration's `observer_definition` string ("SELF + reaped CHILDREN, including collector, recorder, sampler and census") does not describe the number the stop branch reads. Consequently ruling 21's (a) is built on an input that under-reports the observer by 3×; as ruled it would stop nothing it should and its regression (i) asserts a value the corrected statistic cannot produce. The judge could not have seen this: charge 20 and exhibit D presented the reported floor as the floor. That is the packet assembler's error, recorded here.

## Adjudication

1. Ruling 21's option (a) is NOT adopted as ruled: its deciding input was wrong. Its corrections that survive on their own evidence are adopted: the 0.3125 W figure is withdrawn everywhere in favour of C8's 0.3194 W (median) with the 1.0349 W envelope-01 rate as the sensitivity bound; "the pilot records the rate" is false and no rule may depend on it.
2. Refuter 22's option (f) is a new option no judge has ruled; under rule 11 the magistrate does not adopt it alone.
3. Two consecutive rounds have failed on the same signature — a false premise about what the observer accounting measures (round 1: the observer flag is never set; round 2: the floor omits the recorder). The standing escalation trigger applies: the next spend is a CONSULT-shaped round on the design question, not a third narrow charge. Charge 30 asks what the observer floor is for in block two's design, what statistic answers it, and what stop rule follows, with rulings 21 and 22 as exhibits and exhibit G as the verified accounting.
4. Lane QPE01-NONOBSERVER-PREDICATE-01 proceeds NOW on round 1's ruled items (brief 04 items 1–5); item 6 (the observer-floor rule) and the v3 digest pin wait for round 3.
5. Both archived summaries' `observer_floor_cores` are under-reported by the same code; they are NOT rewritten. The corrected values live in exhibit G and go into the harvest records as dated addenda; v3 carries a supersession note naming the v2 statistic (refuter 22, adopted).
