# W1 blockers — independent SOL build, 2026-11-08

Status: **implemented candidate; scientific adoption and native gates pending**.
Branch `align/2026-11-08-w1-blockers-sol`, base `05b6d04cba4868531cc03da187689a3dc187e0eb`.
No real measurements, Block-5 outcomes, model weights, network or hardware probes
were accessed. No coordination state was edited. This is the independent SOL
design; it does not assert agreement with an Opus build.

Both critical-path audits were read from local Git objects:
`origin/perf/2026-11-08-critical-path-sol1:docs/perf/2026-11-08-critical-path-sol1.md`
and the corresponding `sol2` report. Their two deterministic blockers are
removed in the candidate: U3 can accept a reproducible signed derivation, and
an observed clean battery window can return `bar_pass=True`. Production remains
fail-closed until the lead supplies the scientific decisions and evidence below.

Authority: [protocol instrument checks](../pilot_protocol_v4.md#instrument-checks-acceptance-and-exclusions),
[registration installation §§4–5](../pilot_protocol_v4.md#w1-registration-installation-2026-11-08),
[R11 dispositions R02/R03](../council-2026-11-06-v4-review/LEAD-RULINGS-2.md),
and AGREEMENT-FINAL R02/R03 at local ref
`origin/align/2026-11-07-squeeze-agreement-final` (`4526de7d5`). R11-2 installs
no k=3/2.576. R02's numeric window consequence and R03's bar/transfer remain U.
This document proposes those choices; it does not issue their ruling.

## U3 inputs and prospective freeze

The authorized lead exports a JSON object with `pairs` and `policy`; no discovery
or direct measurement access is added to the derivation command. Use the
`turn_owned_j` GPU estimand, not gross energy or DC-in. Each pair includes
`session`, `phase`, `population`, ordered positive `ordinals`, `energies_j`,
`token_identical`, `clock_difference_fraction`, `eligible`, `source_sha256` and
`configuration_sha256`. Exact full prompt/output IDs, transcript/tool order,
cached/fed accounting, seeds and calibration/clock/exclusion evidence are checked
by the export's independent reviewer, not inferred from the two energies.

| Records | Use | Excluded use |
|---|---|---|
| Authorized 30B pilot 4–10 replay summaries, one prespecified eligible pair per session, ordinal separation ≥3 | Fit the signed relative-difference distribution; at least 3 independent sessions, positive nonzero sample SD | Treating several pairs in one session as independent; choosing the smallest difference after looking |
| Closed R1 `D_spam a` / `D_spam b` bundles, their runtime results/custody and final-policy comparison | One D transfer screen. Runtime `energy_j` is `turn_owned_j` (`r1_runtime.py:k_d_gated`); independently verify clocks/tokens/eligibility from bundles | Fitting a D variance or claiming separated-ordinal validation |
| R1 step-D/slots, selected series mode and effective model/stack/thermal configuration | Bind source and intended final D configuration and a hashed transfer justification | Treating a different quantization, budget or thermal policy as equivalent without review |
| W1 D ordinals **5/17** and X/Y same-arm separated replays, plus required source comparisons in the final plan | Test the already frozen U3 bar | Training, selecting a transfer factor, changing alpha or choosing a wider bar after W1 |
| W1 ordinal 18 | Existing alternate-sentinel rules only | Replacing 17 or manufacturing a singleton reference |

Important feasibility finding: the R1 runtime contract's order is D_bank,
D_spam a, D_spam b, X-G, with matched D predecessors. The D pair is adjacent,
not a separated-ordinal replicate. It must carry `qualification_only:true`;
the required policy label is `adjacent_matched_predecessor_screen_only`.
It checks consistency with a prospective transferred bound. It cannot establish
D's distribution or tail probability. This distinction prevents inventing an
R1 prerequisite that the already scheduled R1 cannot supply.

The D source fingerprint and final target fingerprint are explicit separate
policy fields. Fingerprint = SHA-256 of sorted compact JSON of
`cohort_identity(config, spec, observed_runtime)`. It includes actual stack/model
identity and effective execution/thermal controls; the per-window custody
locator is removed by the existing projection. A hashed transfer justification
must discuss every source→target policy difference, including the R1 G0 cap.
The desk compares both members' observed target fingerprints to the frozen one.

Freeze the session/pair selection and source identities prospectively before
opening the energies. Do not replace an ineligible selected pair with the best
remaining pair: disclose unavailable input and return unresolved. All historical
access remains in the lead's anti-hindsight record. This build supplies no claim
that those deadlines were met.

## Frozen candidate calculation

Method `session_student_t_predictive_v1` is relative, without a fixed joule floor.
For each of n independent prespecified pilot sessions:

```
r_i = (E_late - E_early) / ((E_late + E_early)/2)
mu = mean(r_i); s = sample_SD(r_i); df = n - 1
M = sum of 30B and D comparison counts over every frozen window
a = series_alpha / M
h = t_(1-a/2, df) * s * sqrt(1 + 1/n)
q_30B = abs(mu) + h
q_D = d_transfer_factor * q_30B
margin_J = pair_mean_energy_J * q_population
```

The predictive interval is `[mu-h,mu+h]`; the symmetric U3 bar encloses it.
Nonzero mean is included, rather than centered away at test time. The t
quantile is numerically inverted from the incomplete-beta tail, with small
sample degrees of freedom. There is no installed k, normal quantile or 2.97 J
floor in this path. The legacy v3 calculation is unchanged.

Under independent identically distributed normal pilot session differences and
a new difference from the same law, the predictive interval has marginal
coverage 1−a, including estimation of location and scale. The symmetric bar
is conservative relative to that interval. A union bound across M comparisons
does not require independent future comparisons. **Calibration sessions still
must be independent, and the D transfer law is an extra assumption.** This is
not a conditional guarantee at a particular realized small sample, nor a
hardware guarantee. A single passing R1 pair cannot establish that transfer law.
The distribution-free sample-maximum alternative is inadequate at this n:
seven exchangeable absolute differences give only 7/8 marginal coverage for a
new one. At a=.05/16, that construction needs at least 319 independent calibration
differences. Small-n extrapolation therefore requires a distributional assumption
or substantially more measurements; it cannot manufacture distribution-free
assurance from seven sessions.

`series_alpha`, `checks_by_window`, transfer inflation factor (≥1), source/target fingerprints,
transfer-justification digest, simulation seed/count and selection rule are
explicit inputs. Alpha must be positive and ≤15%, the chair's whole-series
ceiling; allocating that entire ceiling to U3 would leave none for other checks.
Recommend a **5% U3 allocation**, subject to the lead's joint U1–U5 OC budget.
Each window must name counts for both populations. The desk refuses U3 scope
when actual comparisons exceed the frozen count or the window is absent. Count
all registered comparisons, including cross-session comparisons if used. An
extra recovery/test window needs prospective scope before observing its U3.

The single prespecified R1 D pair must clear q_D, with valid identity, clock and eligibility.
That screen does not refit q. Future D replays must match the target configuration.
Zero scale, missing evidence, unsigned/pending records, old v1 bars, failed R1
screen, mismatched configuration and drifted arithmetic/OC produce refusal or
INCONCLUSIVE at the desk. Exact tokens and active-clock ≤0.5% remain required.
Charging/missing-battery replays are not usable U3 evidence. Failed windows are
retained; no reduced m or replacement is created.

## Predictive OC and sensitivity

The versioned simulator regenerates n calibration observations in **every**
replicate, fits that replicate's bar and reuses it through the entire frozen
series. It reports pair, per-window and series failure rates with Monte Carlo
SE. This avoids treating an estimated small-sample SD as known population scale.
Its frozen scenarios are:

- unit-normal independent calibration and future differences;
- future within-window correlation 0.5 and whole-series correlation 0.9;
- calibration correlation 0.5 (an independence violation);
- unit-variance Student-t(3) and centered exponential differences;
- D scale at the assumed factor and at twice that factor;
- D drifts of two and eight pilot standard deviations, with per-population
  rejection rates to distinguish D sensitivity from unrelated 30B failures.

The synthetic fixture uses seven pilot sessions, 16 comparisons (W1:4+1,
C1–C8:1 each, T1–T3:1 each), alpha=.05 and transfer factor=2, with 1,000
replicates/seed 2203. These are **test inputs**, not an adopted series roster or
an evidence-based choice of factor 2. The companion `W1-BLOCKERS-sol-OC.json`
records outputs, including n=3/5/7 predictive-width sensitivity. The final lead
export reruns OC with the final roster and actual n, and should use ≥10,000
replicates for a more precise report. Do not tune scientific decisions to the
seed. Correlation, heavy tails and excess D scale can invalidate a nominal
normal-law assurance; the outputs are sensitivity diagnostics, not a simulated
waiver. This U3 simulator does not claim to implement the full joint U1–U5 OC.
The test fixture's nominal series rejection is 0.4%, heavy-tail/skew scenarios
give 5.1%/6.4%, and doubling the assumed D scale gives 22.8% (1,000 draws,
Monte Carlo uncertainty applies). Those alternatives invalidate a blanket
nominal-law assurance. The small-sample prediction is also wide: a two-pilot-SD
D drift is seldom detected. The lead must judge both sensitivity and error
budget; a low false-failure rate alone does not establish adequate state control.

## Custody and use

Derive (explicit authorized export/report copies in this repository):

```sh
python3.13 -B scripts/align_v4_u3_bar.py \
  --input configs/campaigns/align_v4/registration/u3_sources/pairs.json \
  --supporting-source docs/align/v4/U3-transfer.md \
  --output configs/campaigns/align_v4/registration/u3-draft.json
```

This emits PENDING. An independent JSON gate under `docs/align/v4/` must contain
`verdict:"ADMIT"` and the exact `derivation_sha256`. The lead can then supply:

```sh
python3.13 -B scripts/align_v4_u3_bar.py \
  --adopt-draft configs/campaigns/align_v4/registration/u3-draft.json \
  --gate docs/align/v4/U3-gate.json \
  --lead-signature 'lead: <actual-name-or-session> <YYYY-MM-DD>' \
  --output configs/campaigns/align_v4/registration/u3_bar.json
```

Outputs use exclusive creation. Adoption does not fabricate a signature/gate.
The validator recomputes prediction, OC and canonical digest; signature syntax
follows the existing lead assertion convention, not public-key cryptography.
The exact-candidate registration binds u3_bar, new modules and battery policy.
It also verifies the export, supporting report and gate against working bytes
**and that same registration commit**. Traversal, absolute paths, symlinks and
protected path components are refused. The detached desk verifies local source
bytes; the outer registration owns commit/gate authority. No root scan occurs.

The test-only WP22 builder writes separate synthetic source/report/gate/bar,
WP19 and battery policy under its temporary output. It never fills the checked-in
registration or creates a live arm receipt. Its fixed calibration energies are
independent of the synthetic W1 energies.

## Battery window candidate

Keep the installed arm predicate unchanged: completed top-up ≤30 min, AC,
≥99% SoC, not charging, required InstantAmperage within ±200 mA, observation
age 0–180 s, OBC-off attestation. UpdateTime never substitutes for completion.
R1 drain/charge-resume outputs and Ed's D1 charge hold remain required.

Recommend policy `zero_B_disclose_assist_v1`, explicitly signed in
`battery_window_policy.json` (the repository template stays PENDING):

| Span result | GPU member | Model-window consequence |
|---|---|---|
| Complete observed clean evidence | Retain | B_count=0, `bar_pass=True` |
| Discharge on AC/not charging (`battery.assist`) | Retain, disclose assist/energy and print no-assist member sensitivity | Pass if no charging/AC-loss B and no missing span; do not exclude high-load members merely because the battery assists |
| Assist only outside request | Disclose | Same; it decides no GPU exclusion |
| Charging, AC loss, charge-accumulator excursion | Existing named B exclusion retained | Any B → `bar_pass=False`; no pool entry from that model-window; remedy/adjudicate before next arm |
| Missing/unobserved span or malformed journal | Exclude unavailable evidence | INCONCLUSIVE, `bar_pass=None`, session check false |
| No signed policy | No new scientific consequence installed | INCONCLUSIVE, session check false |

Zero B is a **new proposed window rule**, not the withdrawn ≤1 builder rule.
The discharge treatment follows the existing shared battery-assist rule and
the downstream GPU endpoint. Secondary DC-in never becomes the primary endpoint;
its correction/qualification still owns battery flow and unavailable DC evidence.
No counted calibration window is replaced or topped up by this policy.

Both desks replay the existing `battery_join` on the explicit closed journal
`hazards/monitor/battery.jsonl`, using controller `member_spans(metadata,events)`
(the sampler/battery-span hull, not just model decode). Existing current, gap,
accumulator and SMC/fallback semantics are reused without changing shared
Block-5 code. The standalone manifest names `battery_journal` explicitly;
the session desk uses its authenticated custody root. Empty flags, an arm float,
or a missing journal can never prove a clean member. Raw journal, metadata and
events digests, SoC/charger observations and flags accompany the derived result.
Reports are per **model/window**, including ungated anchors. An empty report
cannot pass `all([])`.

## NEEDS_RULING — lead/statistics handoff

| Question | Options considered | SOL recommendation | Work blocked until ruled |
|---|---|---|---|
| Relative versus additive-plus-relative energy law? | Relative predictive bound; fitted additive component; new D-specific separated replays | Relative candidate above, no unestimated floor; explicitly limit transfer | Live U3 adoption |
| Predictive population/selection? | Many correlated pairs; one fixed pair/session; hierarchical variance fit | One prospectively named pair/session; normal assumption with misspecification OC; no energy-based selection | Authorized pilot export/freeze |
| Joint error budget and horizon? | Per-pair constant; whole-series allocation; adaptive extension | Recommend U3=.05 within chair's ≤.15 joint budget; final explicit comparison roster including any required reference comparisons | Final bar and series arm scope |
| D transfer, including adjacent R1 pair and source→target changes? | Infer scale from one pair; explicit external bound plus screen; collect new separated D evidence | Do not infer a factor from one pair. Lead must justify a finite factor and policy comparability, or require new D qualification. Factor 2 is synthetic only | W1 U3 admission if transfer cannot be defended |
| What B window consequence? | Withdrawn ≤1 rule; zero charging/AC-loss B; member-only exclusions | Zero-B candidate, retain AC discharge and its sensitivity; missing evidence stays unavailable | Signing battery policy/live desk pass |

The builder has completed the independent executable candidate and synthetic
checks; these decisions remain the lead's. The exact next action is to compare
this proposal with the independent Opus build, rule the table, obtain the
authorized source export/transfer justification, and generate the signed artifacts
at the reviewed final head before W1. Native top-up, journal/clock/SMC coverage,
exact-head PREQUAL, native W1 smoke and final independent registration gates
remain lead-controlled and must run outside active measurement/agent load.
No new MLX implementation was needed here; no native MLX behavior was tested.
