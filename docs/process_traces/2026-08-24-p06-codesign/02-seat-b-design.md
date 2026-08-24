# P06 — Frozen characterization-result schema

**Status: design proposal, not a frozen artifact.** No repository files were changed. The current paper has six characterization rows and permits only “protocol incomplete” until pre-collection evidence rules are fixed. `docs/paper/draft-v1.md:329-342` The current fill registry likewise marks every characterization output and outcome supplier unknown, so it must stop filling rather than infer values. `docs/paper/results-fill-registry.md:242-276`

The retained 25 July diagnostic is context, not a threshold source: its primary record identifies 30 a10 phase members with 25.62–31.07 ms bounds and says the familiar ~33 W is a derived quotient, not a measured power step. `docs/process_traces/2026-08-15-readiness-council/seat-reports/L11-retained-characterization-basis-report.md:35-43` Historical evidence is expressly not a supplier for the registry. `docs/paper/results-fill-registry.md:20-24`

## 1. Row set

**Proposal: retain the six public Table 1 rows, with eight internal subtests. Do not add public rows.**

| Public row ID | Table 1 property | Decision | Internal required subtests | Why |
|---|---|---|---|---|
| C1 | Workload response | Keep | request-energy response; decode-energy response | This is exactly Table 1’s two-metric fit. `docs/paper/draft-v1.md:335` |
| C2 | Identical-condition null response | Keep | independent floor-derivation subset; held-out null-validation subset, at each magnitude | A null must test an independently derived false-effect bound; otherwise comparing the same blocks that created the bound is circular. |
| C3 | Deliberate small-difference challenge | Keep | negative-control and positive-control directions at each derived increment | Table 1 already requires a prewritten outcome map. `docs/paper/draft-v1.md:337` |
| C4 | Phase accounting | Keep | phase closure; prefill-versus-later-output invariance | Table 1 already contains both estimands; aggregation must be conjunctive. `docs/paper/draft-v1.md:338` |
| C5 | Drift and recovery | Keep | held-out drift containment; recovery-time support for the settling convention | Table 1 already contains both estimands; the drift points used to build an allowance cannot validate it. `docs/paper/draft-v1.md:339`, `docs/paper/draft-v1.md:244-250` |
| C6 | Between-session stability | Keep | calibration/floor corridor; repeated-null concordance | Table 1 already requires at least three independently calibrated sessions. `docs/paper/draft-v1.md:340` |

This preserves the registry’s six existing public outcome anchors—linearity, null, floor, phase, drift, and between-session—rather than creating unbound paper tokens. `docs/paper/results-fill-registry.md:265-270` C4 and C5 are internally split because a pass in only one component must not make the combined Table 1 row appear to pass.

The existing instruments supply the needed measurement types: the metrology suite already plans a five-level, 40-member linearity ramp; three null magnitudes; 24 additivity bundles carrying all three energies; and long-hold/recovery observations. `configs/campaigns/metrology_v1/linearity_ramp/README.md:10-12` `configs/campaigns/metrology_v1/null_ladder/README.md:10-12` `configs/campaigns/metrology_v1/additivity_shapes/README.md:10-12` `configs/campaigns/metrology_v1/long_holds/README.md:10-23` This proposal requires no new sensor, counter, or measurement boundary—only frozen role assignments and deterministic reduction over those artifacts.

## 2. Per-row schema, criteria, outcomes, and bindings

### Common result-state rule

**Proposal:** each row has two fields:

- `verdict`: `READY`, `NOT_READY`, or `UNVERIFIED`, matching the project’s per-component readiness vocabulary; do not add a primary `DEGRADED` or `READY-WITH-CONDITIONS` state. `READY-WITH-CONDITIONS` is explicitly deleted. `docs/process/instrument-readiness-audit-charter.md:79-91`
- `publication_class`:
  - `RESULT` — only `READY`;
  - `PUBLISHABLE_REFUSAL` — complete, authenticated evidence exists but a preregistered criterion failed (`NOT_READY`);
  - `DIAGNOSTIC_ONLY` — preserved, named partial evidence; never supports the row’s conclusion;
  - `PROTOCOL_INCOMPLETE` — no frozen schema/plan or missing required binding (`UNVERIFIED`).

A row may never become `READY` by omitting a failed subtest. A failed, complete row is a publishable refusal; it is not evidence of equality or zero effect. `docs/paper/draft-v1.md:394-398` Missing, malformed, stale, or unknown input is `UNVERIFIED`, not a numerical substitution: the registry’s `STOP_FILL` rule requires this. `docs/paper/results-fill-registry.md:28-41`

All `floor_j` fields must carry `floor_source` and, if attribution-limited, the required disclosure `floor_j + claim_side_bound_j`. That sum is reader disclosure, not a replacement acceptance gate. `docs/decision_log.md:4741-4752` `docs/decision_log.md:5231-5259`

### C1 — workload response

**Inputs and estimator.** Five runtime-observed output-token levels, exactly eight strict-valid bundles per level, with request and decode energy intervals from each bundle. Fit ordinary least squares separately for request and decode:

\[
E=a+bT.
\]

Report `a_j`, `b_j_per_token`, every level mean, and

\[
R_{\max}=\max_{\ell}\sup\left|\bar E_{\ell}-(a+bT_{\ell})\right|.
\]

The supremum is evaluated over the authenticated energy intervals, not only midpoint estimates. Units are J for intercept/residual and J/token for slope. This implements Table 1’s stated estimands. `docs/paper/draft-v1.md:335`

**Pass criterion.** For both metrics: all 40 planned bundles present; all five levels have eight admitted bundles; the all-corners slope lower bound is \(>0\); and \(R_{\max}\le H\), where

\[
H=\max_i\frac{E_{i,\mathrm{upper}}-E_{i,\mathrm{lower}}}{2}.
\]

`H` is a pre-registered, data-derived resolution limit: the largest admitted single-bundle energy half-width for that metric. The conclusion is therefore precisely “linear to no worse than one admitted bundle’s timing-resolution half-width over the tested range,” not universal physical linearity.

**Outcomes.** `NOT_READY/PUBLISHABLE_REFUSAL` if either metric violates its inequality; `UNVERIFIED` if any required level/bundle/interval is absent; otherwise `READY/RESULT`.

**Evidence binding.** `linearity_ramp` order manifest and campaign log, bundle manifest with hashes, whole-window verdict, calibration bracket/acceptance artifact, and the report’s exact input-bundle list. The suite already assigns this campaign a fixed evidence root and log. `configs/campaigns/metrology_v1/README.md:14-27`

**Ruling request R1.** Approve the conservative conclusion wording above. There is no pre-ruled physical “maximum allowed nonlinearity”; calling this merely “linear” without the resolution qualifier would overstate what \(R_{\max}\le H\) establishes.

### C2 — identical-condition null response

**Necessary design repair.** The current plan has five same-condition ABBA blocks per magnitude. `configs/campaigns/metrology_v1/null_ladder/README.md:10-12` **Proposal:** freeze ten blocks per magnitude: blocks 1–5 are `floor_train`; blocks 6–10 are `null_test`. This is extra use of the existing ABBA instrument, not a new measurement capability.

**Estimator.** For each block:

\[
\delta_i=(B_1+B_2-A_1-A_2)/2,
\]

then report held-out \(\bar\delta\), its complete deterministic interval \(I_{\bar\delta}\), and \(M=\max_i\sup|\delta_i|\), all in J. This is the project’s defined ABBA statistic. `docs/paper/draft-v1.md:180-193`

Derive \(F_{\mathrm{train}}\) solely from blocks 1–5 using the existing comparative point guard, its corner widening, and guard factor; test blocks 6–10 must not occur in that derivation. The existing method defines the comparative guard and treats fewer than five blocks as development-only. `docs/paper/draft-v1.md:188-200`

**Pass criterion, for every magnitude.**

\[
0\in I_{\delta_i}\ \forall i,\qquad
I_{\bar\delta}\subseteq[-F_{\mathrm{train}},F_{\mathrm{train}}],\qquad
M\le F_{\mathrm{train}}.
\]

This is fail-closed because the validation blocks are independent of the floor-derivation blocks. It meets Table 1’s two requirements—null-interval containment and a floor relation—without treating failure to reject zero as success. `docs/paper/draft-v1.md:336`

**Outcomes and custody.** A completed violation is `NOT_READY/PUBLISHABLE_REFUSAL` with its magnitude, held-out block IDs, \(F_{\mathrm{train}}\), and failed predicate. Missing any train/test block, exact alias binding, or whole-window evidence is `UNVERIFIED`. Bind the train-floor derivation, held-out reduction, ABBA order manifest, all 40 bundle hashes per magnitude, and the governing whole-window verdict.

### C3 — deliberate small-difference challenge

**Inputs and estimator.** C3 consumes the separately issued C1 decode slope \(b\) and an authenticated seed null floor \(F_{\mathrm{seed}}\); it may not estimate either from C3 blocks. The current micro-delta plan correctly marks its current `k0064` shape as draft-pending-slope and forbids measurement before slope ratification. `configs/campaigns/metrology_v1/micro_delta/README.md:1-4`

Freeze four target ratios \(r\in\{0.5,1.0,1.5,3.0\}\). For each, generate integer token increment:

\[
k_r=
\begin{cases}
\lfloor rF_{\mathrm{seed}}/b\rfloor & r\le1,\\
\lceil rF_{\mathrm{seed}}/b\rceil & r>1.
\end{cases}
\]

Refuse that target if \(b\le0\), \(k_r<1\), or the resulting configuration is outside the frozen context limit. Freeze both directions: A=512/B=\(512+k_r\), and A=\(512+k_r\)/B=512. The present draft only specifies B-minus-A orientation, so the mirrored arm is a required plan addition, not a new instrument. `configs/campaigns/metrology_v1/micro_delta/README.md:48-64`

For every target/direction, bind a **disjoint**, exact-configuration floor pair and set:

\[
F_r=\max(F_{A,r},F_{B,r}), \quad
Q_r=|\hat\delta_r|/F_r.
\]

This armwise maximum follows existing claim-floor composition. `docs/paper/results-fill-registry.md:214-223`

**Prewritten gate map.**

- \(r=0.5,1.0\): expected `floor-gate refusal`; pass the control only if the measured contrast does **not** clear \(F_r\).
- \(r=1.5,3.0\): expected `two-gate passage`; pass the control only if \(|\hat\delta_r|>F_r\) and the complete interval supports the preregistered sign.
- Any absent/disjointness-invalid floor pair is `UNVERIFIED`, never replaced by a floor from another condition. A floor is cell-specific. `docs/paper/draft-v1.md:269-275`

The row is `READY` only if all valid targets match their map in both directions. It reports `min(Q_r)` and `max(Q_r)` as dimensionless diagnostics. A mapping failure is `NOT_READY/PUBLISHABLE_REFUSAL`.

### C4 — phase accounting

**Closure subtest.** For every one of the 24 planned additivity bundles, report:

\[
D=E_{\mathrm{prefill}}+E_{\mathrm{decode}}-E_{\mathrm{request}}
\]

in J and its full endpoint interval \(I_D\). The same bundles are intended to carry all three energies. `configs/campaigns/metrology_v1/additivity_shapes/README.md:10-12`

Pass iff every \(0\in I_D\) and every point residual satisfies

\[
|D|\le h_{\mathrm{prefill}}+h_{\mathrm{decode}}+h_{\mathrm{request}},
\]

where each \(h\) is that bundle’s authenticated energy half-width. This is an exact derived bound, not an adjective.

**Leakage/invariance subtest.** Use C1’s fixed-prompt 128-token ramp, fit prefill energy versus later runtime-observed output tokens, and report \(b_{\mathrm{prefill}}\) in J/token. Let

\[
L_{\mathrm{leak}}=
\frac{\max_i h_{\mathrm{prefill},i}}
     {T_{\max}-T_{\min}}.
\]

Pass iff the complete slope interval lies inside
\([-L_{\mathrm{leak}},L_{\mathrm{leak}}]\). It states a modest, replicable result: no prefill dependence on later work larger than one admitted prefill half-width across the entire observed output span.

**Row decision.** C4 is `READY` only if both subtests pass; otherwise `NOT_READY/PUBLISHABLE_REFUSAL`. Bind the 24 additivity bundle hashes for closure and the C1 bundle/fitted-slope artifact for invariance. This matches Table 1’s dual requirement rather than allowing an additivity pass to hide phase leakage. `docs/paper/draft-v1.md:338`

### C5 — drift and recovery

**Drift subtest.** Compute \(A_{\mathrm{drift}}=\max(X,R_c)\) separately for gross and idle-subtracted request energy, using the existing 3+1+3 start/mid/end references and settled-corpus rule. `docs/paper/draft-v1.md:225-247` Add three frozen `held_out_reference` members after the end-reference group; they are excluded from \(X\) and \(A_{\mathrm{drift}}\). For each family, define:

\[
D_{\mathrm{hold}}=\max_j|H_j-M|.
\]

Pass iff \(D_{\mathrm{hold}}\le A_{\mathrm{drift}}\) in both families. This is the required non-circular containment test: the source explicitly says construction points cannot validate the allowance and requires held-out probes or later sessions. `docs/paper/draft-v1.md:250`

**Recovery subtest.** After each of the three existing 4096-token holds, record the first elapsed second \(t_j\) at which the complete cooldown-exit predicate passes. The predicate is already explicit: 30-s rolling window, 80% coverage, mean power no more than 1.10× reference, nominal thermal state, and a 300-s refusal cap. `docs/paper/draft-v1.md:142-145` Pass iff:

\[
\max_j t_j\le180\text{ s}.
\]

This tests support for the existing 180-s settling convention, which the runbook directs operators to use unless a frozen plan says otherwise. `docs/phase_2/window_runbook.md:49-52`

C5 is `READY` only if both subtests pass. No duration-scaling law is permitted; the paper says the evidence does not identify one. `docs/paper/draft-v1.md:250`

### C6 — between-session stability

**Inputs.** Three independently calibrated, wholly admitted sessions with identical full stack identity. For each session report calibration bound, exact configuration hash, operative floor(s), and its C2 held-out null result. This follows Table 1’s required set. `docs/paper/draft-v1.md:340`

**Pass criterion.**

1. all three sessions’ C2 and C5 rows are `READY`;
2. every session has a matching current capture-method/estimator identity;
3. for every repeated floor role, \(\max(F_{\mathrm{cell}})/\min(F_{\mathrm{cell}})\le1.25\);
4. no session’s revalidation record shows a new residual/contrast component above the prior floor or a new quality, cooldown, sampling, or manifest change.

Items 3–4 deliberately reuse the existing 1.25× stale-floor sentinel and its associated change checks. `docs/phase_2/detection_floor.md:389-408`

**Outcome.** Any mismatch, failed session verdict, failed C2/C5 row, or corridor breach is `NOT_READY/PUBLISHABLE_REFUSAL`; missing a qualifying third session is `UNVERIFIED`.

**Ruling request R2.** The existing 1.25× rule is explicitly an operational stale-floor sentinel, not a statistical overlap test. `docs/phase_2/detection_floor.md:406-408` Approve only the narrow result wording “stable enough for the stated reuse corridor across these three sessions,” not a general statistical stability claim. If a broader inferential stability claim is wanted, Ed/advisor must rule a different criterion before collection.

## 3. Freeze mechanics and paper consumption

**Proposal: two immutable artifacts.**

1. `docs/contracts/characterization_result_schema_v1.md` — reader-facing normative definitions, formulas, outcome semantics, glossary, and refusal form.
2. `configs/campaigns/metrology_v1/characterization_result_schema_v1.json` — machine-readable frozen row roster, field names, formulas, exact campaign roles, source paths, result-token mapping, and SHA-256 of the contract text.

The metrology plans are currently drafts requiring ratification before measurement. `configs/campaigns/metrology_v1/README.md:3-10` Therefore neither artifact may be backfilled into a collected corpus.

**Freeze record.** Before the first characterization bundle exists, a successor frozen plan must bind:

- `schema_id`, `schema_version`, and both schema SHA-256 values;
- the exact campaign-plan, order-manifest, condition-family, calibration-acceptance, and analysis-source hashes;
- every required row/member role, including C2 train/test partition and C5 held-outs;
- the report renderer revision and exact result-fill-registry revision;
- a `no_historical_supplier=true` assertion.

This follows the project’s defined meaning of “fixed”: exact bytes and a fingerprint recorded before outcomes. `docs/paper/draft-v1.md:38` Plans are append-only; an updated method requires a predecessor-linked new plan, not rewriting the old one. `docs/paper/draft-v1.md:321-325`

**Issued result artifact.** After collection, a single `characterization_result_report.json` is issued with:

```text
schema_id, schema_sha256, report_sha256
whole_window_verdict {path, sha256, status, member_failures, conditions}
stack_identity {all required fields, sha256}
rows[row_id] {
  verdict, publication_class, failure_class,
  estimator_id, units, criteria {formula, inputs, threshold_or_rule},
  observed_values, subtests, evidence_bindings[], diagnostic_presence
}
```

Every `evidence_bindings[]` item contains an artifact path, SHA-256, parent role, and exact field path. The existing report ecosystem already distinguishes whole-window status/failures/conditions, floor components and eligibility, and contrast estimate/interval/verdict fields. `docs/paper/results-fill-registry.md:65-80`

**Paper consumption.** The fill registry should bind its existing C1–C6 tokens only to `characterization_result_report.json` paths, never raw bundles. This is required because the figures plan forbids figures from reading raw bundles directly. `docs/paper/figures-plan.md:208-212` The needed current tokens are already enumerated, but presently have unknown suppliers. `docs/paper/results-fill-registry.md:251-276`

For example:

| Existing token | Proposed issued report path |
|---|---|
| `[S_C_linearity_decode_J_per_token]` | `rows.C1.observed_values.decode.slope_j_per_token` |
| `[D_C_null_max_abs_J]` | `rows.C2.observed_values.max_abs_heldout_delta_j` |
| `[R_C_micro_min_x_floor]`, `[R_C_micro_max_x_floor]` | `rows.C3.observed_values.min_ratio`, `.max_ratio` |
| `[D_C_additivity_J]` | `rows.C4.observed_values.max_abs_additivity_residual_j` |
| `[S_C_prompt_invariance_J_per_token]` | `rows.C4.observed_values.prefill_slope_j_per_token` |
| `[D_C_reference_excursion_J]`, `[T_C_recovery_s]` | `rows.C5.observed_values.max_heldout_excursion_j`, `.max_recovery_s` |
| `[N_C_eligible_sessions]` | `rows.C6.observed_values.eligible_session_count` |
| `[PLAIN_LANGUAGE_RESULT_*]` | deterministic rendering of `rows.<id>.verdict` and `publication_class` |

A missing report, unknown refusal class, or failed hash predicate remains `STOP_FILL`, not prose assembled from a nearby field. `docs/paper/results-fill-registry.md:28-41`

## 4. Failed-row reporting form

**Proposal: required publication form for every `NOT_READY/PUBLISHABLE_REFUSAL` row.**

```markdown
### Characterization refusal — [C# / property]

Outcome: NOT_READY — PUBLISHABLE_REFUSAL
What was tested: [one-sentence frozen estimand and stack identity]
Why it cannot support the stated result: [failure_class; exact failed predicate]
Observed, authenticated diagnostic:
- Estimator: [estimator_id and formula]
- Value and unit: [observed statistic]
- Frozen comparator: [number or exact derivation rule]
- Required basis: [planned / admitted / present counts]
- Result: [inequality with substituted values]

Custody:
- Issued characterization report: [path, SHA-256, row JSON pointer]
- Whole-window verdict: [path, SHA-256, status, source refusal codes]
- Input manifest: [path, SHA-256]
- Frozen schema and plan: [paths, SHA-256]

Interpretation limit:
This refusal does not show no effect, equality, or instrument validity outside the
named stack and conditions. It shows that this implementation could not support
the named characterization conclusion from this frozen basis.
```

`failure_class` is closed in the schema: `CRITERION_NOT_MET`, `EVIDENCE_REFUSAL`, `MISSING_REQUIRED_BINDING`, `SCHEMA_PIN_MISMATCH`, or `PROTOCOL_INCOMPLETE`. The raw source refusal codes are preserved verbatim; an unrecognized code stops rendering until explicitly registered, consistent with the registry’s fail-closed handling of unknown codes. `docs/paper/results-fill-registry.md:153-171`

This form makes failed characterization scientifically publishable without converting it into a positive finding. That is consistent with the paper’s stated doctrine that a preserved refusal maps the operating domain rather than proving equality. `docs/paper/draft-v1.md:394-398`

## 5. Glossary compliance

The normative contract must repeat these definitions at first use in §5 and in the schema. Existing paper terms—window, bundle, member, corpus, verdict, reduction, and issued—are already defined in §2. `docs/paper/draft-v1.md:38` The phase boundary and energy integration boundary are also already explicit. `docs/paper/draft-v1.md:40-46`

| Term | Required definition |
|---|---|
| **Admitted bundle** | One member bundle that passed the frozen entry and verification checks. |
| **ABBA block** | Four runs ordered A, B, B, A; its signed difference is \((B_1+B_2-A_1-A_2)/2\). `docs/paper/draft-v1.md:180-186` |
| **Characterization row** | One of C1–C6, with all listed subtests required for `READY`. |
| **Estimator** | The named formula and exact authenticated inputs used to compute a reported quantity. |
| **Held-out** | An authenticated bundle deliberately excluded from constructing the comparator it tests. |
| **Operative floor** | The greater of the absolute and comparative floor components for one exact cell; components are not summed. `docs/paper/draft-v1.md:257-263` |
| **Pass criterion** | A numeric inequality or frozen derivation rule evaluated without outcome-dependent changes. |
| **Publishable refusal** | A complete authenticated result whose frozen criterion failed; it reports the failure and does not assert equality. |
| **Resolution-qualified linearity** | No nonlinearity larger than the C1 derived half-width limit over the tested range; not universal linearity. |
| **Whole-window verdict** | The authenticated accept/refuse decision over the complete planned evidence basis, including membership and environmental conditions. `docs/paper/draft-v1.md:315-321` |

Finally, the §5 discussion should state the attribution limit plainly but avoid converting the historical ~1 J diagnostic into a universal threshold. The retained evidence establishes a phase-bound range and diagnostic envelopes; it does not authorize a new acceptance constant. `docs/paper/draft-v1.md:213-215`