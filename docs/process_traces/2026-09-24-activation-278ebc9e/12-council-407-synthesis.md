# 12 — Synthesis of the D-184 council on directive #407 (magistrate, Opus 5.5, activation 278ebc9e)

Four blind seats answered the same brief (06) on the same packet (04): Sol 6.0 (07), Astra 6 (08), Opus 5.5 (09) and Fable 5.1 (10). No seat saw another's answer. This record is the magistrate's synthesis and proposed rulings. It binds nothing until a cold Fable judge rules on it (packet 13). Q5 is a process rule, so under rule 11 it also goes to Ed after the ruling.

Terms used below:
- **Envelope:** one 600-second measurement slot in a night. A night is 9,000 s with at most twelve envelopes (`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:17-18,98`).
- **KM003C:** a USB-C inline meter. It reads DC voltage and current at the laptop's USB-C input. It does not read mains ("wall") energy.
- **Rails:** the powermetrics CPU + GPU + ANE power sum, which is the project's software instrument.
- **P̄:** mean power over an interval. Energy equals P̄ × duration.

## Where all four seats agree

1. **Q1: no single forced 32k trace.** All four reject it as proposed. One growing trace confounds context position with elapsed time, temperature and fan state. Its quadratic fit has strongly dependent residuals, and a non-significant b does not show that J/token is flat.
   - Fable, Opus and Sol replace it with **context-position rungs**: separate segments started at fixed positions, run in seeded random order, with the estimand per rung.
   - Astra goes further (NO as first night; A3 becomes a conditional follow-up). Astra proposes testing the token-arithmetic premise directly: fit an energy predictor on model, tokens and phase, then judge its held-out error.
   - Fable and Opus drop the third-architecture contrast. Opus corrects the scout: an alternative-attention model IS on disk, Qwen3.5-122B-A10B, a hybrid of linear and full attention at 65 GB. It is also mixture-of-experts, which confounds the contrast, and its MLX support is unverified. It is a later desk-smoke candidate, not night-one material.
2. **Q2: yes to B1, with the boundary stated honestly.** All four note that the KM003C measures DC input, not wall energy, and not DRAM directly. A raw input/rail ratio mixes in conversion loss, the battery, idle load and components outside the rails. So:
   - use an **increment design**: each active segment is paired with its own idle bracket, and the report gives Δinput / Δrails;
   - record battery and charging state;
   - register the meter's clock alignment.
   - Phase (prefill vs decode) goes now. Bit-width waits until non-4-bit weights are admitted and pinned; Opus would substitute context position as the memory-load axis.
3. **Q3: yes to the thinking budget as the independent variable. Votes (A1) are a separate, later registration.** Fable's "nested budgets from one generation" is the concrete form: truncate one seeded generation at each budget, so budgets share a prefix. Opus adds a split: the accuracy runs (many items, no energy claim) need not run in quiet windows; the quiet-window energy nights then measure a budget-forced subsample with per-token timestamps. Sol and Astra both require the staged form: a feasibility pilot, then registration. Q3 amends AP-5M's estimand and the A291 contract's roster roles and levels.
4. **Q4:**
   - **Simulations:** run the D-165 dominance-test and claim-gate-scale simulations now, at the desk. All four agree. Astra warns that simulations generated only from the estimator's own assumptions become tautological.
   - **ABBA:** alternate ABBA and BAAB starts in every NEW registration. Do not regenerate the frozen `_v5` family for this alone. All four agree.
   - **Clock:** do not make the change as a quick fix. Opus says NO outright: powermetrics' own second stamps are wall-clock, so moving only event stamps to monotonic time turns a common NTP shift into a relative one. Sol, Astra and Fable call it prospective at most, with an audited monotonic-to-epoch map.
5. **Q5: tier by semantic effect, not by file name.** The full review tier applies to any change that can alter an observation, a selection, a unit, an uncertainty, a correctness score, or a published sentence. That covers timing, collectors, runner scheduling, calibration, scoring, packers, reducers, estimators, admission and registrations. Elsewhere the tier is one reviewer plus CI, with an impact statement the reviewer checks.
   - It needs matching edits to `docs/orchestration.md` (merge rule `:158-167`), the PR template and the gate-ledger checker, all in one change, or it cannot be installed while `gate-ledger` is a required check on main.
   - It needs a cold gate, and Ed sees the result.
   - Opus adds a 30-day revert trigger: record which tier caught each material defect, and revert if a defect that changes a number gets through the light tier.

## Where they disagree: night order

| Seat | Night 1 | Night 2 | Night 3 |
|---|---|---|---|
| Fable | A3 + B1 combined calibration night | `_v5` collection after a short G2-a probe | MATH pilot under the amended plan |
| Opus | G2-a as registered + KM003C exploratory rider | calibration night (Q1 + Q2) | MATH energy-validation night |
| Sol | G2-a | paired 4-bit input/rail phase night | `_v5` G2-b / transaction |
| Astra | DC-input/rail characterisation | MATH budget feasibility pilot | first A2 collection tranche |

G2-a (lane V5-G2A-PREFILL-PROBE-01, `TASK_QUEUE.md:702`) is READY and non-claim. It selects the `_v5` prefill rung and blocks the `_v5` desk day (`:757`).

## Things the questions missed, raised by two or more seats

- **M1: the equivalence-night rule false-alarms on about half of unchanged nights.** The bench simulation gives P(PASS | no change) = 0.37–0.76 (record 02 line 12). Fable and Opus both raise it. Replace it with a simulated, registered rule (TOST plus a variance-ratio test) before any night whose admission depends on it.
- **M2: report every energy as P̄ × t.** Fable and Opus both ask for this. If P̄ is flat across conditions, energy is a stopwatch, and the paper must show where power varies.
- **M3: the deadline.** Fable and Opus both note that the end-of-November deadline appears only in email. They estimate about 20 clean nights of work, which leaves room for one design iteration. So Q3 must be settled before the first scored night.
- **M4: seeded sampling (Fable).** E3 (decoding) is entangled with nested budgets, which need prefix determinism, and with votes, which need sampling. Decide on seeded sampling with a pinned seed once, for both.

## Proposed rulings (the magistrate's; the cold judge may amend any)

- **R-Q1 AMEND.** The first science night is a **calibration night**, and it combines Q1 and Q2:
  - Models: Qwen3 1.7B and 8B 4-bit, which are admitted.
  - Context-position rungs, e.g. {512, 2k, 8k, 16k, 32k}, subject to a desk smoke of 32k load, duration and memory, run in seeded random order within each envelope, each rung paired with an idle bracket.
  - Estimands per rung and phase: P̄ on rails, P̄ on USB-C input, J/token, tokens/s.
  - Report: the position law, and whether J/token is flat within a pre-registered band.
  - The alternative-attention contrast is dropped from this night.
  - Astra's held-out energy-predictor test is registered as the secondary analysis of the same data.
- **R-Q2 AMEND.** B1 runs inside the calibration night as the increment design (Δinput/Δrails by phase and rung), with battery state and meter alignment registered. The outcome is labelled a DC-input-boundary result, never "wall" accuracy. Bit-width waits for admitted weights.
- **R-Q3 AMEND.** The headline becomes nested thinking budgets from one seeded generation. Accuracy runs happen outside quiet windows; energy nights measure a budget-forced subsample. Votes (A1) go to a later registration. AP-5M draft v4 and the A291 contract are amended to this design. The E2 adoption council then runs on the amended text, and E3/E4 are ruled with it. Seeded sampling with a pinned seed is decided once (M4).
- **R-Q4.**
  - (a) Simulations now: D-165, the claims.py scale, and the equivalence rule (M1). Include at least one generating model that differs from the estimator's assumptions.
  - (b) Alternate ABBA/BAAB in new registrations only.
  - (c) No clock change now. A prospective, audited monotonic-to-epoch design is a separate lane.
- **R-Q5.** Adopt the semantic-impact tiering as a PROPOSED process rule, with the three-file installation and a 30-day revert trigger. This cold judge rules on it, and Ed is informed of the result.
- **R-ORDER.**
  1. Night 1 = G2-a as registered (READY; it unblocks the `_v5` desk day), with a KM003C exploratory rider that cannot affect G2-a's outcome and rehearses meter alignment and battery logging.
  2. Night 2 = the calibration night (R-Q1/R-Q2), once registered.
  3. Night 3 = `_v5` G2-b, or the MATH feasibility pilot, whichever is ready first under its gates.
  - M1's replacement lands before any night whose admission uses the equivalence rule.
- **R-A291.** A291 fix round 2 (the P/K seats on Final texts v4) proceeds now. The defects it cures (a forged roster accepted, the trusted-output cache, mixed parent populations) are structural and survive a roster-role change. The Q3 contract amendment comes after it as a separate A291 contract revision.
- **R-A280.** A280, the scored night kind, proceeds: B0 is parity-only, and B1/B2 are independent of the headline's independent variable.

## Errata (after cold ruling 13/20 §G8)

- §1 wrongly credits rungs to "Fable, Opus and Sol" and says all four reject the 32k trace as proposed. The Fable seat kept forced continuous 32k traces (3 × 1.7B, 2 × 8B, idle bookends) and changed the estimand to P̄(bin). The rungs come from Opus, Sol and Astra.
- §2 lists the increment design as unanimous. Astra made gross ratios primary and increments secondary. R-Q2 now reports both.
- The alternative-attention correction was made by Astra as well as Opus.
- R-Q3 merged two designs without naming the estimand. It is superseded by the ruling's final text R-Q3.
