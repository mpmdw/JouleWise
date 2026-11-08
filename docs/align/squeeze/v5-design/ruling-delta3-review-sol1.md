# v5 ruling revision 3 — delta review, Sol1

**Verdict: SIGN_WITH_CHANGES. Do not sign revision 3 unchanged.** The evidence
boundary, paired missing-outcome bound, calibration disclaimer, development
audit bill and local quarantine are substantial repairs. Two HIGH inference
issues remain: the betting fallback tests a stronger null than the stated
marginal effect null, and the t-test acceptance rule does not establish the
advertised 5% Holm control. Two MED changes complete the H4 date roster and
capacity accounting. These are repairable charter conditions, not grounds yet
to abandon the native hybrid. Registration still requires G0–G12 evidence.

Seat **sol1**, branch `align/2026-11-08-v5design-ruling-delta3-sol1`.
Candidate **`b606d9788cd0cb25e0c85903ba7c75116edad894`**; reviewed the complete
`git diff 7d2e43464..HEAD`: only `RULING-DRAFT.md`, 273 additions / 187 deletions.
Section/line locators below refer to that candidate. This review changes no
ruling, implementation, coordination state or measurement authorization.

Both round-2 delta reports were read from local Git objects, without fetching:

| Key | Local ref under `origin/align/2026-11-08-` | Commit | File under this directory |
|---|---|---|---|
| DS1 | `v5design-ruling-delta-sol1` | `8c2c6c1cec136c724c83c9526cac1e3ae26a3e18` | `ruling-delta-review-sol1.md` |
| DS2 | `v5design-ruling-delta-sol2` | `94acc5b815d79dbfb8d6a4c31aab50114c69faee` | `ruling-delta-review-sol2.md` |

Also checked AP, D-062, the local intake/safety/orchestration instructions and
R11/R12 in the pinned `319f6a51d5707b96799b9230ec63a446c7a12dab:RUN_STATE.md`.
Item 214 is now inspectable; the same object includes item 215's R12 amendments.
The v5 7–9-date plan is its own design, not a claim to copy v4's 6–8 counts.
No external literature, source-ref freshness, venue dates or native gate was
independently verified.

## 1. Every round-2 finding, both seats

**Resolved** means the requested binding obligation is now stated, with future
implementation/qualification still gated. **Partial** means an operative gap
remains. None of the thirteen numbered findings is wholly unaddressed. §9's
status labels are not substituted for the operative clauses.

| Round-2 finding | Status in revision 3 | Operative quotation and assessment |
|---|---|---|
| DS1 HIGH D1: S/E feature boundary, rerun target, deployable S | **Resolved at ruling level** | §4a: actual counts are “never an active-work feature”; the verifier compares with the “submitted public projection”; “The confirmatory H4 comparator is this deployable S.” CPU/GPU/token/time mappings, matched carriers and frozen component laws are explicit. Receipt coverage remains G0/G12 evidence. See §3. |
| DS1 HIGH D2: adverse paired-effect bound | **Resolved** | §4b: “δ_i takes its minimum over all completions compatible with the known values”; shared scores are completed “coherently in both rules.” Unknown side outcomes are failures for capability. This repairs the paired point bound in both directions; inference is separately R1–R2. |
| DS1 HIGH D3: finite-date t validity and zero variance | **Partial** | §4b fixes arm-date/timezone, “G ≥ 20,” equal date weights and every constant-variance case. But “≤ 1.2 × nominal” and the conditional-mean betting fallback do not establish the stated marginal-null, 5% family guarantee. R1–R2. |
| DS1 MED D4: development audits, cuts, cap, storage, capacity | **Partial overall; ledger substantially resolved** | §5 now bills “G10 48,” “S standardization on dev honest/controls 72,” “G6 12,” an explicit batch line and “GO envelope (cap-inclusive).” Cut 3 reproduces. The CAP formula and yield convention still need R4; the small local cap addition is L1. |
| DS1 LOW D5: descriptive local transfer, roster and quarantine | **Resolved at ruling level** | §4d calls results “transfer,” keeps “the same honest and test roster,” reports availability/truncation/template failures and freezes “Exactly two local configurations”. All ledgers are sealed before release and the access history is explicit. |
| DS2 HIGH D1: paired adverse imputation | **Resolved** | §4b: “Known alarms, unknown side outcome: δ_i = min(0, A^rule − A^comparator).” Separate absolute escape bounds and unknown-as-failure capability handling remove unverified positive rescues. |
| DS2 HIGH D2: date exchangeability versus episode ranks | **Resolved as a claim correction** | §4c explicitly requires “joint exchangeability of the individual honest scores” for the rank argument and says “0.05 is a nominal calibration target, not a distribution-free future-date FPR guarantee.” It reproduces the 1/8 counterexample, stresses calibration and retains empirical honest-test FPR reporting. The general rank-tail formula needs the nonblocking L2 correction. |
| DS2 HIGH D3: exact test, dates, variance and size | **Partial** | §4b's “America/Los_Angeles calendar date of the window's arm time” and “whether all zero or constant nonzero” settle date/zero-variance definitions. The primary inference still needs R1–R2; H4 also needs R3. |
| DS2 HIGH D4: fairness, +∞, integer H4 allocation | **Partial overall; evidence and +∞ repaired** | §4a makes actual counters discrepancy evidence, labels the invocation privilege and declares “DEGENERATE_CALIBRATION.” The new “block of 3 consecutive windows” rule permits 224 total but does not ensure H4's asserted per-date mixture or ≥20 usable H4 dates. R3. |
| DS2 MED D5: resource reconciliation and development coverage | **Resolved for listed planning inputs; small cap follow-through L1** | §5 specifies “48 attack originals + 48 twins,” 966 reruns, batch overhead, separate cap and candidate-specific screen times. “The 12 G6 twins can also go” preserves seeded S reruns. All headline hours, cut savings and cap storage reproduce using the unrounded local estimate. |
| DS2 MED D6: operational CAP acceptance | **Partial** | §5 adds “0.85 × h_v4,” CAP-1b, missing evidence → “HOLD,” CAP-2 ≥60 members / ≥20 helper attacks and remeasurement after G9 changes. The hours/day formula is dimensionally wrong and accepted-only capacity duplicates the yield discount if combined with the reserved ledger. R4. |
| DS2 MED D7: local F/C separation and access history | **Resolved at ruling level** | §4d: “chosen on F only,” “Thresholds come from C only,” “All local score ledgers are sealed before the first release,” and an “append-only access ledger” for every read. Leak rehearsal, common roster and transfer wording are installed. No executed quarantine certification is claimed. |
| DS2 LOW D8: R12 availability, accepted versus complete | **Resolved for authority; completion labels need this delta** | §8 pins “item 214 at origin/main @ 319f6a51d,” which is locally readable. §9 distinguishes resolved/gated/open. Its inference, roster and CAP rows should now be marked Partial pending R1–R4 rather than remain “Resolved.” |

The unnumbered requirements carried in DS1 §§3,5–6 and DS2 §1 also remain in
scope:

| Requirement carried by both reports | Status / operative text |
|---|---|
| D07/D12/R14; denominator; both discordance directions | **Resolved as design obligations.** §4: “all assigned attempts,” directly calibrated scalars, “both rescues and regressions”; §2h: strict “score > cutoff”; §4a defines declared-work time excess. Detector alarm budgets remain separate from Holm α. |
| Cohort definition, success bars and headline conjunction | **Resolved at ruling level, subject to R1–R3.** §4b: “All 336 attacks come from the three frozen optimizers”; the .30 pooled/.20 per-pair bars apply to all attacks and H4, with unknowns as failures. H1–H3, FPR and availability form the strong-result conjunction; H4 adds the software headline. Utility stays reported rather than being reintroduced into D09. |
| Calibration reserve dates, loss margin and count-only stopping | **Resolved.** §4c: “including sessions 8-9” on distinct dates, ≤7/pair/date; both-pair target, cap and INSUFFICIENT_CALIBRATION are explicit. 49→42→49 and cap loss arithmetic reproduce. This is no probability guarantee against arbitrary combined losses. |
| Frozen policies, technical replacement list, immutable failures and no feedback | **Resolved as obligations.** §4b freezes the optimizer/mixture/roster before T1, retains first outcomes, technical-only replacements and “no optional stopping.” The actual list and search budgets remain G12 artifacts, not completed work. |
| Threat taxonomy, matched carriers, realistic qualification, physical guard and replay | **Resolved as future gates.** G0 retains A0–A13; G4 now explicitly requires gold/real-weight parity; G6/G8/G9 retain native exactness, randomized replay placement, battery/tail closure, physical uncertainty guard and serial/concurrent resolution. G10 names oracle-independent graders and failed-policy records. No gate passed in this review. |
| Per-channel audit bill, local configuration scope, v4 and platform boundaries | **Resolved as deliverables/scope.** §6's release cost table enumerates latency, joules, captures/twins/reruns, scoring, storage and availability. §1/§2l preserve one actor/host/batch, shadow detection and no second-architecture substitution; desktop AC-wall is separately labelled and v4 remains unchanged. |
| Novelty, actual NeurIPS dates/eligibility | **Not resolved empirically; appropriately Open.** §1 explicitly says “unverified” and requires authorized primary-source checks before registration. This offline seat supplies no venue or novelty certification; this does not block a bounded development charter. |

## 2. Remaining changes that affect signature

### R1 — HIGH: the betting theorem's null is stronger than the registered effect null

§4b L187 sets `H0: Δ_k ≤ 0`, a marginal mixture effect. L208 correctly says
the fallback is valid “whenever each date's conditional mean is ≤ 0.” That
qualification is mathematically substantive: neither a constant marginal
per-date effect nor G≥20 implies it under serial dependence.

For example, draw one fair sign Z and set every date mean to Z. Every date
has marginal mean zero and the dates are dependent. After the first +1,
the next conditional mean is +1. An ordinary one-sided capital process
`K_G = product_g(1 + 0.5*d_g)` reaches 3,325.256730 at G=20 on that path,
which has probability 1/2, far beyond the first-Holm evidence threshold 80.
This construction is valid under the conditional-mean null, but not under
this allowed marginal-null dependence. It illustrates the missing assumption,
not a claim about an unspecified future hedged-capital implementation or
real v5 dates. More dates do not remove the common sign. Zero-variance
samples route precisely these constant paths to the fallback.

**Required change:** explicitly choose and justify the dependence/null model.
One option is independent dates with the same conditional-on-F/C effect;
another is to adopt and label the stronger sequential conditional-mean null
and narrow the inference accordingly. If the intended null is only a
marginal average under general date dependence, this fallback cannot be its
validity certificate; impose a defensible dependence restriction or redesign
the independent units/claim prospectively. Apply the same model to honest-FPR
uncertainty. Frozen policies alone do not establish independence of host dates.

A complete, valid fallback can be specified before calibration without
implementing it in this review. For example, for a **justified conditional
null**, freeze chronological order, filtration (including development and
calibration), nonnegative predictable bets `0≤λ_g≤1`, `K_0=1` and
`K_g=K_{g-1}(1+λ_g*d_g)`. Then `E[K_g|past]≤K_{g-1}` and K is nonnegative.
At the fixed final G, `p=min(1,1/K_G)` (p=1 when K_G=0) is a valid p-value;
or freeze the running-maximum version if that is intended. A mixture of such
processes is also valid with prespecified weights. One-sided versus hedged/two-sided
capital, betting constraints, weights and Holm conversion must be explicit
G12 acceptance items, not inferred solely from an author citation. No
generic “valid under date dependence” claim follows from this proof.

### R2 — HIGH: the 1.2× gate permits >5% family error and is not a validity proof

§4b L207 permits simulated rejection “≤ 1.2 × nominal.” At the first Holm
threshold .0125 that allows .015. Four independent all-null p-values with
`P(p≤u)=1.2u` in this range have Holm family error
`1−(1−.015)^4 = .058663449`. This is permitted by the proposed per-threshold
criterion but exceeds .05. Even known 1.2-superuniformity would support at
best a correspondingly inflated bound, not the advertised .05 guarantee.

Moreover, a finite registered stress family is useful falsification/power
evidence, not proof for all distributions in the stated mean-null class.
Specify simulation replication counts and an upper Monte Carlo uncertainty
bound; an observed rejection fraction below a cutoff is not certification
of the population size. The full procedure includes the data-dependent
zero-variance switch in L211. Two separately acceptable tests do not
automatically make their switched combination acceptable.

**Required change:** retain Holm/AP, but require valid constituent p-values
under the declared model. Prefer the justified bounded-mean procedure as the
primary, with t as a sensitivity, unless a restricted, prospectively stated
t model actually supplies validity. If a model-qualified approximation is
chosen, label its error guarantee honestly, use conservative calibration
consistent with the declared family level, and qualify the **entire**
t/zero-variance fallback algorithm with Monte Carlo upper bounds. Dividing
thresholds by 1.2 would address a *proved* 1.2 bound; the present simulation
criterion does not itself prove such a uniform bound. G12 must recompute
power for the repaired full Holm decision including bound missingness,
threshold randomness, H4 composition, capability and honest availability.

### R3 — MED: 224 is feasible, but the new rotation does not ensure H4 date support

§4a L170 requires two of each class per cell in three windows; L171 requires
224 subset attempts. Those aggregate constraints are compatible. The first
27 windows supply 216 H4 attempts; window 28 must supply eight (four cover
slots), which must be made explicit in the sealed rotation.

But the rule also allows every cell's three windows to be
`(cover,cover), (external,external), (unrestricted,unrestricted)`.
Repeat nine times, then add a last window with four of each class. This
meets the per-cell block rule and **224 exactly**, yet nine windows have no
H4 attempts and only 19 windows can contribute an H4 date. It cannot supply
G_H4≥20 even if every contributing window has its own date. Less extreme
allowed allocations can omit individual pair/optimizer cells from a date,
making L204's equal-mixture `d_g` undefined without an additional estimator.
Restoring global weights does not fill absent date cells.

**Required change:** bind H4's own usable-date count and estimator. A simple
feasible repair is eight H4 attempts per window, at least one in every
pair×optimizer cell, and stagger the cell patterns
`(cover,external), (cover,unrestricted), (external,unrestricted)` over three
windows. Two cells in each phase give eight H4 attempts every window,
two of each class per cell per block, and 224 overall. Freeze window 28's
phase and the pair/optimizer totals. Define `d_g` as the equal average of
the six cell means, using nonnegative within-cell weights; freeze the
corresponding campaign estimator and qualify it at the actual date roster.
Alternatively provide another explicit estimator/support law at G12. The
existing ≥20-date assertion cannot simply be inherited from the full 336.
Under date heterogeneity, equal-date and per-attempt estimates also differ;
state the constant-effect restriction or choose the intended weights.

### R4 — MED: capacity units and the yield discount must be reconciled

CAP-1 calls its quantity “Usable MBP hours per calendar day” but divides
accepted busy **hours by elapsed calendar hours**. That is a fraction,
at most one for nonoverlapping intervals, and cannot meet “≥12 h/day.”
Multiply by 24, or divide by elapsed calendar days; apply the same correction
to CAP-1b. This is a functional GO-rule error, not just a label.

The numerator excludes rejected/redone windows while the denominator
includes their calendar time. It is therefore capacity **net of observed
loss**. The ledger also multiplies by 1.25 “funds an 80% yield.” In a simple
24-busy-h/day, 80%-accepted example, accepted capacity is 19.2 h/day. A
100-accepted-h job takes 100/19.2 = 5.208333 days, equivalently 125/24.
Using 125/19.2 instead gives 6.510417 days and charges the yield loss twice.
That is conservative, but can trigger unnecessary cuts or a false NO-GO.

**Required change:** use gross available busy hours with the reserved
required-hours ledger, or accepted capacity with the base accepted-work bill
and a separately justified incremental reserve. If the second haircut is
deliberate additional contingency, label it rather than asserting costs are
counted once. Keep the 15% v4→v5 transfer stress distinct from this issue.
CAP-1b must update the same convention under the selected v5 workload.

The other CAP repairs are sound charter conditions: no missing-evidence
substitution of 16, conservative transfer until v5 evidence, measured
member/rerun timing and G9 recheck, both phase/full-plan fits, actual dates,
blocking reviews, post-T3 scoring and no assumed March permission. None is
a measured capacity result. The explicit ≥1,800-s redesign stop governs the
overlapping CAP-2 boundary wording.

## 3. Repairs that should stay closed

**Evidence fairness (§4a): no remaining directional unfairness is established
at ruling level.** Submitted work is E's sole active-work allowance; protected
actual tokens/CPU/GPU are S discrepancy evidence. E cannot credit deleted
generation. S is no longer starved of those receipts, and compares the actual
operator-held invocation with the submission, not with a different benign
prompt. Excluding S's consistency verdict from E-alone and DC-in from S
defines channel ablations; J_SE combines their information. It is not a promise
of identical score features. G0/G2/G6/G12 must still demonstrate deployable
coverage, public projection, private-byte isolation and legitimate-helper
baselines. A strong S that leaves no energy increment is a legitimate G10
failure, not a reason to remove a useful receipt.

**Paired bound (§4b): valid as a lower effect bound.** If C_i is the feasible
completion set containing the true values, `L_i=min_{c∈C_i} δ_i(c)≤δ_i(true)`.
Nonnegative mixture/date weights preserve that inequality. Hypothesis-specific
minima need not share the same worst completion across H1–H4; Holm allows
dependent valid p-values. Shared-channel completions must respect their common
score and frozen thresholds, as the text now requires. The minimum never
increases a feasible paired contribution in the tested rule's favor; it can
retain a positive contribution when every feasible completion is a rescue.
It is conservative for effects, not automatically for a studentized p-value.
For the conditional-mean betting construction above, a measurable lower
bound preserves the conditional inequality under the stated filtration/null.

**DEGENERATE_CALIBRATION (§4a): appropriate and terminal for H4.** With strict
`>`, a +∞ cutoff makes all S alarms false, including score +∞. At m=49/k=48,
two honest +∞ values suffice. Reporting unresolved H4, retaining those
calibrators and forbidding clipping/retry fixes the prior silent-disabled-audit
problem. The implementation must propagate this to J_SE/H4's status; it must
not silently test a disabled comparator. The draft already says H4 unresolved.

**Calibration and local quarantine (§4c–d): substantive repairs.** The count
table, reserve-date rule and downgrade to nominal/empirical FPR answer the
exchangeability objection. The local comparison now has F-only selection,
C-only thresholds, a shared held-out roster, transfer wording, no between-T
scoring, all-ledger sealing and a published append-only access history
(person/process, hash, time, purpose for every score/threshold/ledger read).
This is a sufficient contract for later implementation/rehearsal; it is not
evidence that access controls or the leak check have actually run.

## 4. Arithmetic evidence and nonblocking corrections

Executed `python3.13 -B /private/tmp/jw-v5-delta3-sol1-check.py`: **PASS**.
The temporary script imports only stdlib Fraction/datetime/itertools, takes
literal design counts and synthetic examples, and reads no project/data file.
It exhaustively checks the minimum for all 27 partial observations of three
binary variables, checks the H4 counterexample and a feasible repair, and
asserts the cut arithmetic. These are logical/arithmetic checks, not a G12
operating-characteristic simulation.

Using the **unrounded** 810-transcript local estimate, in hours:

`L = 810*(30000/600 + 1000/35)/3600 = 17.678571429`

`B(t) = 2180*t/3600 + 46 + 966*.4*t/3600 + 6 + L`

`C_cap(t) = 64*t/3600 + 2 + 28*.4*t/3600; reserved = 1.25*(B+C_cap)`.

Selected verbatim script output:

```text
roster dev=372 C=224 adaptive=240 test=1344 measured=2180 scaffold_h=46 S_reruns=966
local810_exact_h=17.678571429 cap_extra28_local_h=0.611111111
t=900 base=711.278571429 reserved=889.098214286 cap_extra_base=20.800000000 cap_base=732.078571429 cap_reserved=915.098214286
t=1200 base=925.145238095 reserved=1156.431547619 cap_extra_base=27.066666667 cap_base=952.211904762 cap_reserved=1190.264880952
t=1800 base=1352.878571429 reserved=1691.098214286 cap_extra_base=39.600000000 cap_base=1392.478571429 cap_reserved=1740.598214286
cuts900=35.000000000,36.000000000,220.500000000,3.000000000,121.600000000 (half_honest,half_adaptive,882_twins,G6_twins,eight_windows)
storage_t=900 members=2244 raw_TB=1.034035200 two_copies_plus25pct_TB=2.585088000
storage_t=1200 members=2244 raw_TB=1.378713600 two_copies_plus25pct_TB=3.446784000
H4_compliant_counterexample total=224 zero_subset_windows=9 nonempty_windows=19 max_H4_dates=19
H4_feasible_repair subset_per_window=8 every_pair_optimizer_cell_nonempty=PASS
adverse_bound partial_observations=27 all_minima_leq_every_compatible_truth=PASS
1.2_size_gate first_Holm_allowed_size=0.015000000 independent_all_null_FWER=0.058663449
CAP_full_utilization literal_hours_over_hours=1.000000000 corrected_hours_per_day=24.000000000
ASSERTIONS PASS: literal arithmetic and synthetic constructions only; no project/data imports
```

Thus **711.3 / 889.1**, **732.1 / 915.1**, and the **1,190.3-h** 1,200-s
cap-inclusive reservation all reproduce. The 925.1/1,156.4 figures use L's
unrounded value; substituting the displayed 17.7 shifts that base/reservation
to 925.2/1,156.5. Preserve precision until the final display.

The test-phase reservation remains 532 h at 900 s (33.25 days at 16 h/day,
44.333333 at 12), and 697.666667 h at 1,200 s (43.604167 days at 16).
Jan 19–Feb 21 has 34 inclusive days; Jan 19–Feb 28 has 41; Dec 7–Feb 28 has
84. These illustrate the need for the CAP-gated schedule, not its feasibility.
The separate batch line, G10 packages, development S transforms, retained G6
reruns and all four nonadditive cuts now reconcile. Actual candidate times,
loads, canaries, quiet return and final workload conversion remain GO inputs.

**L1 — LOW, nonblocking cap coverage:** the cap schedules 126 C originals,
but local scoring bills 98. The eligible roster can exceed 98: per-pair
counts `(49,45)→(56,45)→(63,52)` at sessions 7→8→9 obey the stopping rule
and yield 115 eligible, adding 17 local scores / 0.371032 base h. Scoring
all 126 scheduled C transcripts would instead give 838 rather than 810
total transcripts: an upper planning addition of 0.611111 base / 0.763889
reserved h at the fixed local rate. With that full scheduled scoring bill,
cap totals become **732.689683 / 915.862103** at 900 s and
**952.823016 / 1,191.028770** at 1,200 s, before loads. Actual eligible counts
can be smaller; 126 eligible is incompatible with the count-only stop.
Either bill the actual C roster or specify a prospective shared calibration
subset; do not pick a convenient subset after seeing C. This small correction
does not change this verdict or establish a calendar failure.

**L2 — LOW, nonblocking rank wording:** replace the generic “2/(m+1)” in §4c
with `(m+1−ceil(.95*(m+1)))/(m+1)`. At m=63, k=61, the exchangeable-score
tail is 3/64=.046875, not 2/64. The selected rank is correct; the incorrect
shorthand does not restore the already-disclaimed distribution-free claim.

Cosmetic items: review-round naming and wording compression do not affect
signature. No separate cosmetic edit is requested.

## 5. Handoff and limits

Before signature, the lead should disposition R1–R4, install the null/model
and family-error guarantee, bind H4's per-date support/weights and repair CAP
units/yield accounting. Correct L1–L2 in the next text pass, update §9's
partial statuses, then send that exact candidate to the companion independent
seat and lead adjudication. This is one seat's judgment; no substitute second
seat or authority decision was delegated. If justified inference cannot pass
G12 power within the measured envelope, resize/narrow prospectively or return
REDESIGN. No post-result exception is endorsed.

Changed files: this review and the dated run report
`docs/run_reports/2026-11-07-v5-ruling-delta3-sol1.md`. The ruling and all
coordination state are preserved. The report records final validation and
local commit handoff. No network, weights, real measurements, restricted
directory, external user-tree read, blinded analysis pipeline, process/job
inspection or native probe was used. No full/sharded/unit suite or compileall
was needed for two Markdown files; the standing no-full-suite rule governs.

**Native checks for the lead outside this sandbox:** after implementation,
run the integrated import-gated, tiny-synthetic MLX unittest modules for
operator-held replay/public projection, forced declared-work twins,
history/cache/RNG identity, receipt partitioning, helpers/concurrency/teardown
and tail bounds, one module at a time. This review adds no native tests and
cannot name nonexistent integrated module paths or claim they passed.
Actual capacity, timing, capability, determinism, meter/clock/battery closure
and resolution remain later lead-controlled clean-machine gates; no weights
or real captures are authorized here. Venue/novelty, deployment receipt
coverage and the real date-dependence model remain unverified.
