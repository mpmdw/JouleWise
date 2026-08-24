# MVP paper figures plan

This plan is intentionally number-free. It specifies result figures only; it
does not authorize a fill, chart implementation, or interpretation. Every
panel remains `STOP_FILL` until all cited registry rows are renderable from
issued artifacts. Captions must keep the D-119 conservative disclosure line
verbatim or replace it only with weaker wording.

The data-source authority is
`docs/paper/results-fill-registry.md`. Token names below are registry row keys,
not values.

## Figure A — phase-floor composition

**Purpose.** Show which absolute or comparative component controls the
operative detection floor for each model and phase without suggesting that the
components are additive.

**Registry rows consumed.**

- `[F_1p5B_prompt_abs_J]`, `[F_1p5B_prompt_cmp_J]`,
  `[F_1p5B_prompt_operative_J]`
- `[F_1p5B_decode_abs_J]`, `[F_1p5B_decode_cmp_J]`,
  `[F_1p5B_decode_operative_J]`
- `[F_7B_prompt_abs_J]`, `[F_7B_prompt_cmp_J]`,
  `[F_7B_prompt_operative_J]`
- `[F_7B_decode_abs_J]`, `[F_7B_decode_cmp_J]`,
  `[F_7B_decode_operative_J]`

**Axes and units.** Horizontal: model-and-phase cell. Vertical: energy in
joules. Marks: absolute component, comparative component, and operative
component maximum. Do not stack components.

**Number-free caption stub.** Absolute, comparative, and operative detection
floors for the prospectively collected prompt-processing and token-generation
cells. The operative floor is the larger authenticated component, never their
sum; any attribution-limited label and point-only diagnostic are rendered only
through the selected cell branch.

**Mandatory D-119 disclosure line.** These floors characterize only the named
physical unit, software stack, telemetry boundary, and prospective alpha or
beta evidence; they do not validate absolute whole-system scale or rank a
hardware class.

**Render gate.** Every cited component must be exact and authenticated, each
cell must select its licensed publication branch, and the derived maximum must
match the artifact's `floor_gate_j`; otherwise omit or refuse the affected
cell exactly as the registry directs.

## Figure B — phase-energy means and composed intervals

**Purpose.** Compare reader-facing prompt-processing and token-generation
energy per request across the two model sizes while showing the fully composed
measurement intervals.

**Registry rows consumed.**

- `[E_1p5B_prompt_J_per_request]`, `[E_1p5B_prompt_lower_J]`,
  `[E_1p5B_prompt_upper_J]`, `[E_1p5B_prompt_J_per_token]`
- `[E_1p5B_decode_J_per_request]`, `[E_1p5B_decode_lower_J]`,
  `[E_1p5B_decode_upper_J]`, `[E_1p5B_decode_J_per_token]`
- `[E_7B_prompt_J_per_request]`, `[E_7B_prompt_lower_J]`,
  `[E_7B_prompt_upper_J]`, `[E_7B_prompt_J_per_token]`
- `[E_7B_decode_J_per_request]`, `[E_7B_decode_lower_J]`,
  `[E_7B_decode_upper_J]`, `[E_7B_decode_J_per_token]`
- `[N_bundles_1p5B_prompt]`, `[N_bundles_1p5B_decode]`,
  `[N_bundles_7B_prompt]`, `[N_bundles_7B_decode]`
- The four operative-floor tokens from Figure A, only as clearly distinct
  floor references rather than interval endpoints

**Axes and units.** Horizontal: phase, grouped by model. Vertical: gross energy
per request in joules. Marks: reported mean and fully composed lower-to-upper
interval. If shown, floor references use a visually distinct glyph and are not
error bars.

**Number-free caption stub.** Reader-facing phase-energy means and fully
composed measurement intervals from the prospectively registered alpha and
beta reported-mean cells. Independent valid-bundle counts accompany the marks;
token-normalized companions remain table annotations under the recorded-
token and same-tokenizer rules.

**Mandatory D-119 disclosure line.** The plotted means are internal to the
named software-counter boundary and become demonstrated results only when the
D-123 reported-mean artifact and its authenticated member basis issue; until
then this figure has no data supplier.

**Render gate.** Currently `STOP_FILL`: the registry marks every D-123 mean,
interval, companion, and count supplier `UNKNOWN`. Do not substitute the
absolute floor component's internal mean or count.

## Figure C — registered model-size contrasts and separate gates

**Purpose.** Show the signed model-size effect, its fully composed interval,
and the relevant armwise floor while keeping floor clearance and directional
support as separate decisions.

**Registry rows consumed.**

- `[E_decode_contrast_signed_J_per_request]`,
  `[E_decode_contrast_lower_J]`, `[E_decode_contrast_upper_J]`
- `[M_decode_contrast_abs_J_per_request]`,
  `[F_claim_decode_armwise_max_J]`, `[C_decode_floor_clearance_J]`,
  `[S_decode_floor_shortfall_J]`, `[R_decode_effect_x_floor]`
- `[B_decode_claim_J]` and `[S_decode_joint_J]` for caption disclosure only,
  never as a plotted acceptance threshold
- The registry's “Gamma prompt-processing contrast” discrepancy row, pending a
  D-122-compliant prompt token family

**Axes and units.** Horizontal: registered phase contrast. Vertical: signed
model-size difference in joules per request, oriented larger model minus
smaller model. Marks: point estimate and fully composed interval. A separate
floor-magnitude reference may be shown symmetrically around zero; do not draw
the floor-plus-claim-bound disclosure as a decision threshold.

**Number-free caption stub.** Prospectively registered model-size contrasts on
the named stack, with signed point estimates, fully composed intervals, and
armwise detection floors. Floor clearance is evaluated on magnitude, while
direction is evaluated from the interval and registered direction; an
unresolved or refused contrast is not equality or zero effect.

**Mandatory D-119 disclosure line.** A directional statement appears only for
a contrast whose authenticated claim artifact passes every applicable floor,
interval-direction, multiplicity, and evidence gate; otherwise the figure uses
the weaker refusal or unresolved wording carried by that artifact.

**Render gate.** Decode remains blocked on the unknown claim-side-bound binding
where that disclosure is used. Prompt processing remains `STOP_FILL` until the
lead-owned draft/template train adds the D-122 token family and gamma supplies
the corresponding issued contrast row.

## Figure D — known-signal characterization

**Purpose.** Test whether the measurement path responds to registered known
signals without creating false contrasts across the tested range.

**Registry rows consumed.**

- Linearity: `[S_C_linearity_request_J_per_token]`,
  `[S_C_linearity_decode_J_per_token]`, `[R_C_linearity_limit_J]`
- Null response: `[D_C_null_max_abs_J]`
- Empirical floor: `[R_C_micro_min_x_floor]`,
  `[R_C_micro_max_x_floor]`
- Mixed/refused branches: `[PLAIN_LANGUAGE_RESULT_linearity]`,
  `[PLAIN_LANGUAGE_RESULT_null]`, `[PLAIN_LANGUAGE_RESULT_floor]`,
  `[D_C_linearity_diagnostic_J_per_token]`,
  `[D_C_null_diagnostic_J]`, `[D_C_micro_diagnostic_x_floor]`

**Axes and units.** Linearity panel: horizontal runtime-observed output tokens;
vertical energy in joules, with fitted slope annotated in joules per token.
Null panel: horizontal registered output-magnitude condition; vertical signed
ABBA difference in joules. Empirical-floor panel: horizontal registered
micro-difference condition; vertical effect divided by operative floor,
dimensionless. Any acceptance band is drawn only from a frozen criterion.

**Number-free caption stub.** Characterization of response linearity, null
behavior across registered magnitudes, and empirical behavior around the
operative floor. Panels report the issued row outcome and show numeric
diagnostics only when the row-specific presence guard licenses them.

**Mandatory D-119 disclosure line.** These panels demonstrate instrument
behavior only if the separately governed characterization window passes its
whole-window verdict and the corresponding registered row is supported; any
partial value from a refused or mixed row remains explicitly diagnostic.

**Render gate.** Currently `STOP_FILL`: the characterization report schema and
all cited output fields are `SUPPLIER_UNKNOWN` in the registry.

## Figure E — phase consistency, drift, and settling

**Purpose.** Show whether phase accounting is internally consistent and
whether the admitted window's temporal behavior supports the registered drift
and recovery claims.

**Registry rows consumed.**

- Phase consistency: `[D_C_additivity_J]`,
  `[S_C_prompt_invariance_J_per_token]`,
  `[B_C_prompt_invariance_J_per_token]`
- Drift and settling: `[D_C_reference_excursion_J]`, `[T_C_recovery_s]`
- Row outcomes and refused-window diagnostics:
  `[PLAIN_LANGUAGE_RESULT_phase]`, `[PLAIN_LANGUAGE_RESULT_drift]`,
  `[D_C_phase_diagnostic_J]`, `[D_C_drift_diagnostic_J]`
- Between-session context: `[PLAIN_LANGUAGE_RESULT_between_sessions]` and
  `[N_C_eligible_sessions]`

**Axes and units.** Phase-consistency panel: categorical registered diagnostic
on the horizontal axis; additivity residual in joules or prompt-invariance
slope in joules per token on separate vertical scales. Temporal panel:
registered reference/recovery diagnostic on the horizontal axis; reference
excursion in joules and recovery time in seconds on separate panels, never a
dual-scale overlay. Between-session eligibility is caption context, not a
continuous numeric axis.

**Number-free caption stub.** Internal phase-accounting, drift, and settling
diagnostics from the governed characterization campaign. Additivity and
prompt-invariance test phase assignment; reference excursion and recovery test
the admitted temporal regime; between-session language follows only the
registered eligibility rule.

**Mandatory D-119 disclosure line.** These diagnostics test internal
consistency and stability under the recorded stack and admitted sessions; they
do not validate the software counter's external gain, establish unrestricted
cross-session transfer, or convert a refused window into evidence of stability.

**Render gate.** Currently `STOP_FILL`: the characterization schema, row
outcomes, presence flags, and numeric fields are all unresolved suppliers.

## Cross-figure production rules

- No figure may read raw bundles directly. It consumes only the issued artifact
  fields or deterministic renderer products named in the registry.
- Missing, stale, inconsistent, contaminated, or unknown evidence removes or
  refuses the affected panel; it never becomes zero and never selects a more
  favorable branch.
- Every figure labels the physical unit, operating-system build, runtime and
  relevant libraries, model artifact and quantization, tokenizer, sampler and
  output policy, concurrency policy, telemetry backend, and measurement
  boundary from authenticated stack metadata.
- Point-only repeatability diagnostics are visually and verbally distinct from
  published operative floors and never support a claim.
- Floor and claim-side uncertainty retain their separate roles. Their sum may
  appear only as a sizing disclosure and is never rendered as an acceptance
  gate.
- The D-124 common-mode estimator identity and its block-timescale
  stationarity/transfer assumption must be disclosed beside any contrast that
  consumes it; the caption must also state that historical evidence bounded
  the errors but did not observe realized member-level edge errors.
- If a stronger caption sentence is proposed, D-119 requires the supporting
  evidence to be named in the same sentence. Otherwise use the weaker wording
  already specified here.

## Schematic figures (no measured data)

A separate class of figure explains mechanism rather than reporting evidence.
These are drawings, not renderings of artifacts. They live in
`docs/paper/figures/` and are described one paragraph each in
`docs/paper/figures/README.md`:

- `docs/paper/figures/fig1_boundary_attribution.svg` — phase-boundary timing
  uncertainty and the energy that migrates between prompt processing and token
  generation (belongs to Section 3).
- `docs/paper/figures/fig2_window_timeline.svg` — measurement-window structure,
  the calibration bracket, and how ABBA order cancels steady drift (belongs to
  Section 2).
- `docs/paper/figures/fig3_decision_gates.svg` — the floor gate and the
  interval-direction gate as separate checks, with the four outcomes (belongs
  to Section 3).

Rules for this class:

- They consume no registry row and have no data supplier, so they are exempt
  from the `STOP_FILL` registry and from the render gates above. Nothing in
  them may be presented as, or later replaced by, a measured value; a figure
  that acquires a measured quantity leaves this class and becomes a results
  figure governed by the sections above.
- Every numeric annotation in them is illustrative and is labelled as such on
  the figure itself, alongside a statement that the figure contains no measured
  data. Axis scales, interval widths, timing bounds, and power steps are chosen
  for legibility, not measured.
- Captions in the paper must not use internal decision-log identifiers,
  registry row keys, campaign codenames, or window labels. They stay in plain
  language, name the figure as schematic, and repeat that its values are
  illustrative.
- The D-119 disclosure lines above are not required for these figures, because
  they make no empirical claim; a schematic figure must not be used to imply
  one.
