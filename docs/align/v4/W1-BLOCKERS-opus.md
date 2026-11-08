# W1 blockers: U3 derivation and B window rule (Opus build)

2026-11-08. Branch `align/2026-11-08-w1-blockers-opus`, based on
`origin/align/2026-11-08-v4-r11` @ `05b6d04cb`. This is the Opus half of the
paired build (RUN_STATE 220-221). The Sol build is on
`align/2026-11-08-w1-blockers-sol`. I did not read it before committing this.

Sources: the two critical-path audits (`perf/2026-11-08-critical-path-sol{1,2}`,
items 5a and 6, and items 2 and 6 respectively), AGREEMENT-FINAL R02/R03,
RUN_STATE 212 R11-2, and the Opus cold review (`v4-opus-cold-review.md`: HIGH
(a)/(b), and section 3 on operability). No pilot, R1 or W1 record was read. All
numbers below come from synthetic draws.

## 0. What was broken, and what changes

| Blocker | At `05b6d04cb` | This branch |
|---|---|---|
| U3 | `validate_u3()` always raises. A signed JSON cannot clear it. `u3_margin` has no margin. | A frozen derivation (§1). `validate_u3` admits only a lead-signed bar with an ADMIT independent gate. Every derived number must recompute from the inputs embedded in the bar. Anything else refuses, including v1/k=3 artifacts, unsigned derivations, edited numbers, wrong scope and synthetic bars outside a dry run. |
| B window | `desk_diagnostics` always emits `bar_pass=None`, so `v4_B_bar` is always False. | A count rule with a stated consequence (§2). A clean W1 passes. Two charging members fail. Missing evidence is unavailable, never a pass. |
| WP22 dry run | Kit refusal: the contrast fit was stale after WP18 was re-measured. After that, the desk crashes on the U3 stop. | `collect` recomputes `contrast_fit` against consistent synthetic R1 X-G evidence. The desk runs on a synthetic registration dir whose signed synthetic bar goes through the real derive, sign and validate path. The manifest carries `delta_slow_c` and stages. The oracle applies the bar and the chair-9 contrast independently. |

Files changed:
- `joulewise/align/apple/v4_registration.py`: U3 procedure, validator, margin, `battery_window`.
- `joulewise/align/apple/thermal_desk.py`: `identical_pair` passes the member model, for the bar's scope.
- `scripts/align_v4_session.py`: harvest battery codes, `battery_evaluated`, and `v4_B_bar` requires `is True`.
- `scripts/align_v4_u3_bar.py`: `derive` and `sign` subcommands.
- `scripts/align_v4_w1_synthetic.py`: contrast refit, synthetic registration, U3 oracle.
- `docs/align/pilot_protocol_v4.md`: rulings 4 and 5, and the U3 row.

Tests: the new `tests/align/test_v4_w1_blockers.py` (20 tests) fails 20/20 on
`05b6d04cb` (6 failures, 21 errors including subtests) and passes here.
Superseded assertions were updated in `test_v4_registration`, `test_v4_r11` and
`test_thermal_desk`. The old descriptive-only U3 script test was deleted, since
its replacement is in the new module.

## 1. U3: the frozen derivation

### 1.1 Inputs (which records)

| Input | Source | Role |
|---|---|---|
| **Derivation pairs** | 30B pilots 4-10. Within-session, token-identical replays, ordinals ≥3 apart, positive turn-owned GPU J. The lead exports these as an explicit `pairs` file; nothing is discovered. | The only multi-pair source available before W1. They fix s₀. |
| **Transfer pairs** | R1's U5 replay pair, `D_spam a`/`D_spam b`, family D. These are adjacent (back to back), so they are not admissible as derivation pairs. They must be token-identical. | Can **refute** use of the 30B bar on D, but never qualifies it. |
| **W1 records** | **None.** | `require_registration` checks the bar before W1 arms. W1's 5/17 and contrast pairs are the bar's first prospective applications, so using them to derive it would be hindsight. |
| Parameters | Lead-frozen before the export is computed: `series_pair_tests` N, `series_false_fail_budget` β, `min_pairs`, `oc_seed`, `oc_reps`. | No defaults exist in code. Calling `derive_u3` without parameters is a TypeError. |

The bar digests the input and parameter file bytes (`source_sha256`), and the
registration receipt binds `u3_bar.json`. The export must label families
exactly `30B` and `D`. Those are the keys `u3_family` maps desk model names to,
and any other label leaves the pairs inconclusive, which fails closed.

### 1.2 Procedure `u3.zero_centred_rms.series_predictive_t.v1`

1. **Unit.** r = (E_late − E_early) / mean(E_early, E_late), signed, late minus early.
2. **Scale.** s₀ = √(Σr²/n), the RMS **about zero** with n df. Any early→late
   drift in the pilots inflates s₀. No fitted drift is ever subtracted or
   credited. Mean and SD are printed only.
3. **Quantile.** Under exchangeable zero-mean normal differences, s₀²n/σ² ~ χ²ₙ.
   The procedure solves for q in
   E_U[1 − (1 − P(|Z| > qU))^N] = β, with U² ~ χ²ₙ/n,
   by Simpson quadrature and bisection. This is the probability that **any** of
   the series' N pair tests fails falsely. It includes the small-sample
   uncertainty of s₀, which every later test shares, so it is not a Šidák
   product of independent t tails. The per-pair predictive false-fail
   P(|tₙ| > q) is also reported. It is exactly the Student-t tail; the test
   checks P(|t₁₀| > 2.228) = .05.
4. **Bar.** A pair fails U3 iff |E_b − E_a| > q·s₀·mean(E_a, E_b), and the existing
   decode-clock ≤0.5% and exact-token checks still apply. The window combines
   pairs as before: any fail fails, and missing evidence is inconclusive.
5. **Scope.** The bar applies to the derivation family (30B). D is in scope only
   when R1's transfer pair has |r_D| ≤ q·s₀ (`not_refuted`). If it has
   `refuted`, or there is no transfer evidence, D pairs are **inconclusive**
   (the `u3_margin` refusal). Unmapped model names are inconclusive too.
6. **OC block.** This is a seeded Monte Carlo of the frozen rule. It depends only on
   (parameters, n), never on data values. Each scenario re-derives s₀ from n
   fresh draws and applies the bar to the N future tests:
   - null normal (checks the quadrature);
   - drift of 0.5σ and 1σ;
   - t₄ heavy tails;
   - ρ = 0.3 dependence: sessions of 3 derivation pairs, plus a W1-shaped cluster of 4 future pairs;
   - future scale ×0.5, ×1.5 and ×2 (transfer);
   - per-pair detection of 3σ, 5σ and 8σ shifts;
   - q by n.
7. **Validation.** `validate_u3` recomputes items 1-6 from the embedded pairs and
   parameters. Floats are compared to 1e-9 relative, and OC rates within
   3/oc_reps. It also requires `status: registered`, a valid
   `lead: <name> <date>` signature and an ADMIT gate under `docs/align/v4/`.
   With `root`, which `require_registration` passes, the gate report's bytes must
   match its digest. `synthetic: true` refuses unless the caller is a dry run.
   Results are memoized per bar content, so desk pair evaluation stays cheap.

### 1.3 Operating characteristics

This is the recommended rule: N = 16, β = .05, 20,000 reps, seed 20261108.
Synthetic draws only.

| n pilot pairs | q | per-pair α | null MC | drift 1σ | t₄ tails | ρ=.3 | D scale ×1.5 | D scale ×2 | detect 5σ |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 4.317 | .0050 | .049 | .024 | .189 | .058 | .236 | .509 | .71 |
| 12 | 3.571 | .0038 | .051 | .018 | .216 | .056 | .345 | .701 | .89 |
| 24 | 3.246 | .0034 | .050 | .015 | .224 | .053 | .430 | .808 | .95 |

q for other values of N, at n = 6/12/24:

| N | β = .05 | β = .10 |
|---|---|---|
| 5 | 3.54 / 3.00 / 2.78 | 2.96 / 2.61 / 2.46 |
| 16 | 4.32 / 3.57 / 3.25 | 3.66 / 3.17 / 2.94 |
| 24 | 4.58 / 3.76 / 3.40 | 3.89 / 3.35 / 3.10 |
| 40 | 4.90 / 4.00 / 3.60 | 4.18 / 3.58 / 3.29 |

Reading:
- The rule controls series false failures under its model. It is robust to drift
  (drift makes it more conservative) and to mild dependence.
- It is **not** robust to heavy tails: t₄ gives about 20% series false-fail.
- It is **not** robust to a D replay scale above the 30B scale: ×1.5 gives
  24-43%. One adjacent R1 pair cannot detect a ×1.5 ratio. This is the main
  scientific risk, and it is why transfer is labelled "not refuted", never
  "qualified".
- A 5σ thermal-control failure in one pair is caught 71-95% of the time, depending on n.

### 1.4 Lead statistics rulings needed (U3), with recommendations

1. **N, the series pair-test count.** Recommend **16**: W1's 4 30B and 1 D pairs,
   plus one D replay pair in each of 8 calibration and 3 test windows. This must
   match the final C/T manifest. If the manifest changes N, re-derive before
   the bar is used. Do not re-derive after a window is read.
2. **β, the series false-fail budget.** Recommend **.05**. A false U3 fail costs a
   window's pool entry and triggers the escalation ladder. Losing two windows
   still leaves m≥39 (R13), so β = .10 is defensible if the lead weighs power more.
3. **Zero-centred RMS versus a drift-centred scale.** Recommend zero-centred, as
   built. A centred scale would credit systematic early→late drift, which is the
   thermal effect U3 exists to detect.
4. **Relative-only versus absolute-plus-relative (F versus O in R03).** Recommend
   **relative only**. Episode energies differ by about 15× between 30B contrast
   members and D members, and a relative unit transfers better. An absolute J
   floor would be an installed constant that the derivation cannot estimate
   from n pairs. The code supports only `relative`. Adopting F's form needs a
   new procedure id.
5. **D transfer.** Recommend: the D bar is admissible only when the R1 pair does
   not refute it, as built. Disclose that this check is weak (§1.3). D-specific
   qualification means a D replay scale estimated from the series' own pre-W1 D
   pairs. None exist before W1, so state "transfer-limited" in the paper.
   Missing or divergent R1 D pair: D U3 is inconclusive, the W1 desk fails, and
   the lead disposes. Do not fall back.
6. **min_pairs.** Recommend **5**. Below that, q exceeds 4.6 at N = 16 and power collapses.
7. **Heavy-tail sensitivity.** Recommend accepting the normal model as primary.
   Report the t₄ row in the registration OC table. If the pilot export shows
   |r|/s₀ > 3 in any pair, the lead considers β = .025 before signing, a rule
   fixed now and applied blind to outcome.
8. **One bar for the whole v4 series, never re-derived from windows it judges.**
   Recommend yes, as built: `limitations` states it.

## 2. B: the battery window rule and consequence

### 2.1 Rule

Chair ruling 4 / R02 makes charging a named **member** exclusion, B
(`battery.member_span`). The window bar was left U. Built rule, per model-window
over all its members:

- **B**: members whose harvest codes include `battery.member_span`, meaning
  charging or AC loss was read inside the member span.
- **Possible B**:
  - members with `battery.unmeasured` or `battery.accumulator_excursion`;
  - members with no harvest battery evaluation. The session desk sets
    `battery_evaluated` only when `archive/derived/exclusions.json` exists.
- **Pass** iff B + possible B ≤ 1. That holds under every resolution of the unknowns.
- **Fail** iff B ≥ 2. **Unavailable** (`bar_pass=None`) otherwise.
- `v4_B_bar` requires `bar_pass is True` for every model-window. Fail and
  unavailable both fail the desk.
- **Battery assist** (discharge on AC) is printed only
  (`assist_members_print_only`). v4's registered residual is GPU energy, and the
  KM003C DC-in channel is SECONDARY in v4 (R11-3). Assist accounting belongs to
  the v5 DC endpoint (D03).

The tolerance of one mirrors U1's "≤1 X1-X4 member per model-window". A single
float top-off is plausible even after a completed top-up. Two in one window
means the arm's top-up did not hold.

### 2.2 Consequence (fail)

- B members stay excluded. That was already the case.
- **Non-B members are not removed.** The thermal gates control temperature
  directly (U1/U2), so charging in a neighbour does not invalidate a member whose
  own span read no charging.
- The window desk fails `v4_B_bar`. The **next arm** waits until three things are
  recorded: a fresh completed top-up and OBC attestation under the arm rule, and
  a lead disposition of the cause. After W1, the next arm is D1.
- No replacement member, no top-up mid-window, no change to m.

An unavailable verdict has the same gate effect and needs a lead disposition of
the missing evidence.

### 2.3 Lead rulings needed (B), with recommendations

1. **Tolerance.** Recommend **1**, for parity with U1. Zero is stricter and would
   make one top-off a full stop.
2. **Window scope for D-series pools.** Recommend that B-fail is an
   **operational** stop, not a pool loss, as built. The alternative is to treat
   it like U4/U5 ("state not controlled", no pool entry). That costs a whole
   calibration window per event, and R13's margin is one window.
3. **`battery.accumulator_excursion` as possible B, not B.** Recommend as built.
   It is charge-accumulator evidence, but it is not a read of IsCharging.
4. **Assist.** Recommend print-only in v4, as built. It gates nothing.

### 2.4 Not changed

The arm predicate (`battery_arm`, top-up ≤1,800 s) is unchanged. The cold
review's MED-3 is about which top-up evidence counts under back-to-back
cadence. That remains a separate lead item and is not part of this build.

## 3. WP22 synthetic W1 dry run

`JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic`

- At `05b6d04cb`: 2 errors. Both window classes' `setUpClass` hit
  `kit.require_ready` with "contrast_fit/contrast_g0_cap_s must bind ...", which
  is cold-review HIGH (a). With that fixed, the desk crashes on the U3 stop
  (HIGH (b)).
- Clearing (a) and (b) exposed three more stale-harness divergences. None of
  them is a pipeline bug:
  1. The synthetic R1 X-G evidence (5 turns) disagreed with the re-measured
     pilot-7 X count (3), so the contrast was correctly pre-declared
     INCONCLUSIVE. A clean synthetic R1 now admits every X turn.
  2. The desk manifest lacked `delta_slow_c` and member `stage`, which the v4
     contrast requires.
  3. The independent contrast oracle still applied FINAL-DESIGN §2.5: df=4, no
     delivery check. It now applies chair 9: the delivery check plus a stage
     term (df=3).
- On this branch it passes. Final status is in §5. In the clean window, all
  members succeed. The desk matches the independent energy oracle.
  - D/W1 U1, U2 and U3 pass. The 5/17 pair has ΔE ≈ −1.4 J against a 134 J margin.
  - All four 30B pairs pass, with |ΔE| ≤ 1.4 J against margins of about 20 J.
  - The contrast verdict matches the oracle.
- In the injected window, the desk runs and every design expectation holds.
  F3 stays the documented expectedFailure.

The dry run's synthetic bar is fixed synthetic data: 12 30B pairs at about 0.15%
relative spread and one D transfer pair at 0.1%. It is labelled
`synthetic: true`, so `require_registration` refuses it. The dry-run desk admits
it only by wrapping `validate_u3` with `allow_synthetic=True`. The oracle reads
q and the signed differences from the bar file and applies the margin itself.

WP22 runs the thermal desk CLI, not the session desk, so B is not exercised
there. The session desk's B and U3 path is covered by the three
`BatteryWindowTests.test_session_desk_*` tests: a clean W1 passes both, two
charging members fail B, and no harvest record means no pass.

Note for the parallel Sonnet fixer on the v4 branch: the contrast-refit hunk in
`collect` is likely to overlap. Take either version; both recompute after the
WP18 update.

## 4. Residual risks outside scope

- Model naming is inconsistent: a failed member's record uses the plan's
  `model_id` (`qwen3.8-27b`), while a read bundle uses `episode.agent_model`.
  That can split one model across two desk groups. `u3_family` maps both to D,
  but the grouping issue predates this branch.
- None of this makes W1 armable alone. Still needed:
  - the signed receipt with Stage A/B;
  - WP19 native;
  - the R1 backfills;
  - the lead's U3 parameters and pilot export, then the signed bar and its gate;
  - the triage producer;
  - the offload freshness policy.

## 5. Verification (this branch)

Each module was run one per process with `python3.13 -B`:

| Module | Result |
|---|---|
| `test_v4_w1_blockers` | 20 OK; 20/20 fail at base |
| `test_v4_registration` | 19 OK |
| `test_v4_r11` | 27 OK |
| `test_thermal_desk` | 25 OK |
| `test_protocol_v4_doc` | 6 OK |
| `test_v4_executed_closure` | 2 OK |
| `test_v4_cadence` | 16 OK |
| `test_r1_round8` | 21 OK |
| `test_v4_kit` | 116 OK |
| `test_v4_estimands`, `test_v4_w1_plan`, `test_r11_review_sol1_witnesses`, `test_r11_review_sol2` | 15, 12, 5 and 4 OK |
| `JW_WP22_FULL=1 test_v4_w1_synthetic` | **18 OK (1 expected failure, F3)**, 129 s; 2 setUpClass errors at base |
| `test_v4_prequal`, `test_v4_powermode_record` | 1 failure each, **identical at base `05b6d04cb`** and outside this scope. The prequal failure is `test_real_launcher_keeps_the_venv`. The powermode failure is a test expecting no `v4_registration_evidence` key from `powermode_desk_check`. |
