# Block 5 independent reader: repository-only re-derivation

2026-11-10 · Sol seat `p1-seat4` · reviewer: research lead · **RL-3 gate NOT PASSED**

This is an internal reader report about [RESULTS.md](RESULTS.md), not permission to
print its numbers. The [machine ledger](rederivation.tsv) records the available
checks and the blocked leaves. No analysis implementation or result text was
changed.

The brief prohibits custody access and real-measurement analysis, while RL-3 and
RL-24 seat 4 require a source check against the frozen artifacts. The named
artifacts are not exposed as files in the checked Git trees. This reader stopped
at each missing input. A definition and a consistent calculation on the text
under review do **not** independently establish the input value.

## Scope, authority, and evidence

The base is `a9dd335b38e6777afcd31c4dc0a812e4bc9906e0`, initially identical to
`origin/main`, on `analysis/2026-11-10-b5-rederivation`. The worktree was clean at
intake. The reviewed RESULTS bytes equal the original results branch
`0b0658a207923c52db760118cf9884953824d329`; their SHA-256 is
`fb5f81e8741532d79b059b2ca7c44b1c479f0f983c28527ab6e2511d7dfb6f55`.

Authority read:

- RL-3, RL-4 and RL-24 seat 4 in
  `origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`
  at `24b549f25ace51f1cf7059f913503930419db316`, and its `paper-audit.md`.
- The ten licence constraints in
  `origin/research/2026-11-07-b5-release-to-paper:docs/research-audits/2026-11-07/b5-release-to-paper.md`,
  §2 D; RL-4's later reporting interpretations apply.
- [Registered estimators](../../../configs/campaigns/v5_claim_25g83/analysis_plan_block5.md)
  §§4–8, [registration](../../../configs/campaigns/v5_claim_25g83/registration_block5.md)
  §§0.5, 0.14, 1, 6.3–6.6,
  [coverage audit](LEAN-COVERAGE-AUDIT.md),
  [deviations](DEVIATION-LOG.md), and relevant D-177/D-179/D-188–D-190 text.
- The committed [attempt index](../../../configs/analysis/b5/analysed_windows.json),
  [bars](../../../configs/analysis/b5/recompute_bars.json), flag catalog,
  identity/sizing pins, seal history, and the three analysed-window process records.

No primary analysis function was imported, called, copied, or used as an oracle.
The arithmetic used fresh standard-library Python (`math`, `statistics`, `csv`,
`json`, `re`, and Git subprocess reads). The incomplete-beta evaluation below was
written for this read. Neither L9, the independent recompute, the comparator, nor
any release/harvest program was executed. Small portions of the **independent**
recompute's source at `02ef89f5c` were read to identify its disclosure estimands;
they were not executed. Its Git blob hashes to
`d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`, matching
RESULTS' program identifier. A program digest verifies identity, not execution.

No network, model loading/download, hardware measurement, real `restricted/`
directory, external home-directory path, or custody/archive path was accessed.
Paths inside committed documents/configurations were treated only as text.
Coordination state was not edited. The speed toolbox was read; this task changes
no throughput or measurement behavior.

## How to read the machine ledger

The TSV has the requested six columns: `printed_value`, `key/leaf`, `source`,
`rederived_value`, `match`, `note`. Keys include RESULTS line locations at the
above pinned blob. A `numeric[i]` suffix identifies the zero-based printed
numeric token on that physical line after omitting identity/reference syntax.
Decoded field names are used where available; `check.*` rows are additional
consistency checks, not independent source leaves.

There are **538 rows**: **181 exact**, **149 within-rounding**, and **208 MISMATCH**.
Of the latter, **207 are explicitly `BLOCKED_INPUT`**, with `UNAVAILABLE` as the
rederived value. The remaining row is the distinct-cause wording discrepancy
below. These are counts of ledger rows, including repeated presentations and
auxiliary checks; they are not counts of independent registered leaves.

The status vocabulary is restricted to the three labels requested in the brief.
Consequently an unavailable source uses `MISMATCH`, rather than inventing a fourth
status or passing a value copied from RESULTS. It means **unverified**, not that
the unavailable artifact has been proved numerically wrong.

The note prefix is essential:

| Prefix | What the check establishes |
|---|---|
| `DEFINITION` | A registered design constant or calculation rule; no proof that a run realized it |
| `REPO_SOURCE` | A named committed second record supports the assertion, with its stated limits |
| `GIT` | A blob digest; no proof of execution or measurement |
| `ARITHMETIC_CONDITIONAL` | Arithmetic on released printed operands, conditional on their accuracy |
| `PROVENANCE` / `IDENTITY` | Historical entry count or table indexing; no energy validation |
| `BLOCKED_INPUT` | A specific needed input is absent; leaf remains not printable under RL-3 |
| `DISCREPANCY` | An actual conflict visible in the released text |

`within-rounding` includes **propagated input rounding**, explicitly quantified in
the note where needed. It must not be read as recovery of all digits printed by
the primary output. In particular the three-decimal `d_k` list cannot reproduce
five-decimal means or tiny p-values at their printed precision.

Coverage includes the numerical assertions in §§1, 1.1, 1.2, 2, 4.4, 4.5 and 5,
their rounded repetitions in §§3, 6 and 7, and the numerical floor, dominance and
release claims in §§4.1–4.3. Numerals in section/step/decision references, dates,
hashes, model names, version names, stage/member IDs, and list numbering are
locators rather than estimated quantities. They are not counted as successful
numeric re-derivations. Relevant Git identities and historical counts are checked
separately. Spelled-out substantive counts, such as the distinct causes, are
included. An executed numeric-token inventory found no unclassified numeric
lines outside the documented reference/identity exclusions.

## Arithmetic that is possible from the released text

All energy calculations in this section are conditional on RESULTS' printed
inputs. Boundary: **M3 Max / MLX / powermetrics SoC rails**, gross phase energy;
one GAMMA session. Phase attribution is reported without a measured instrument
phase-accounting check (D-177). This is an internal consistency exercise, not a
fresh measurement or an L2 eligibility determination.

### Contrast statistics and intervals

The registered difference is `(B1+B2-A1-A2)/2`, followed by its sample mean and
sample standard deviation over kept quads. The phase metrics have no added
random metrology variance: `SE = s_d/sqrt(n)`. The multiplier is the Student
0.975 quantile **rounded to three decimal places**, not the exact quantile.

| Calculation from the printed three-decimal `d_k` | Decode | Prefill p2048 |
|---|---:|---:|
| Count | 6 | 5 |
| Sum (J) | 879.776 | 509.047 |
| Mean (J) | 146.629333333333 | 101.809400000000 |
| Sample SD (J) | 0.180218386039 | 0.297130947564 |
| SE (J) | 0.073573848011 | 0.132880999394 |
| df | 5 | 4 |
| Exact t quantile, approximately | 2.5705818356 | 2.7764451052 |
| Registered rounded t* | 2.571 | 2.776 |
| LOO mean range (J) | 146.5700–146.6674 | 101.68275–101.86475 |

Each printed `d_k` is uncertain by up to 0.0005 J from rounding alone. This bounds
the mean error by 0.0005 J, SD error by `0.0005*sqrt(n/(n-1))`, and SE error by
`0.0005/sqrt(n-1)`. All the printed summary values are consistent with these
bounds. Their unrounded values remain blocked. The SD discrepancy must not be
hidden by claiming exact agreement with the rounded list.

Using instead RESULTS' more precise summary operands:

- Decode statistical half-width: `2.571*0.073524 = 0.189030204` J; subtract/add
  from `146.62940` J to obtain `[146.440369796,146.818430204]` J.
- Prefill statistical half-width: `2.776*0.132867 = 0.368839992` J; subtract/add
  from `101.80943` J to obtain `[101.440590008,102.178269992]` J. The printed
  lower endpoint `101.44060` is consistent with rounding in the SE input.
- Decode timing terms: `4.11056+0+0.97352 = 5.08408` J versus printed `5.08409` J;
  the discrepancy is within the combined operand rounding. Prefill gives
  `4.65958+0+0.97352 = 5.63310` J.
- Widening the printed statistical endpoints by printed D gives decode
  `[141.35628,151.90252]` J and prefill `[95.80750,107.81137]` J. The printed
  prefill endpoints `[95.80749,107.81138]` are consistent with source rounding.
- Decision half-widths from the printed endpoints are `5.27312` and `6.001945` J.
  Thus the relative widths are about `3.5962%` and `5.8953%`; D contributes about
  `96.4152%` and `93.8546%`. Clock/D is about `80.8514%` and `82.7179%`.

The independently evaluated two-sided t tail from the summary operands is
approximately `6.0164877444e-16` and `1.7404550527e-11`. Propagating the printed
SE's ±0.0000005 J and mean's ±0.000005 J covers the p-values in RESULTS. Holm's
two-test calculation on the printed raw p-values is directly checkable:
`2*6.0165e-16 = 1.2033e-15`, and
`max(1.2033e-15,1.7404e-11) = 1.7404e-11`.

The largest LOO mean movements from the rounded lists are about `0.05933` and
`0.12665` J, below `0.25*10.17807 = 2.5445175` and
`0.25*8.83026 = 2.207565` J. This supports the printed magnitude-influence
description conditionally. It does not recover every LOO timing term, floor
binding, Holm row, or eligibility judgment.

The geometric energy ratios and their intervals cannot be obtained from `d_k`
alone: the per-quad **two arm means** are required. Dividing aggregate means
does not implement the registered log-ratio estimator. The six ratio numbers
are therefore blocked even though the printed values look plausible.

### Per-token numbers and the four L1 cells

The registered denominators are 512 **total runtime-observed output tokens** and
2048 prompt tokens. The decode phase generates 511 of the 512 output tokens;
the denominator remains 512. Observed per-bundle counts are not available here.
For all phase-energy values below the boundary is the SoC rails and the D-177
limitation above applies. The ALPHA/BETA values are L1, separate windows in a
fixed order; no difference of their cells is asserted.

Examples of the hand arithmetic:

- `146.62940/512 = 0.286385546875`, printing `0.286386` J/output token.
- `101.80943/2048 = 0.0497116357421875`, printing `0.049712` J/prompt token.
- Divide each statistical and decision endpoint by the same denominator; all
  twelve per-token endpoint presentations in §§1.1 and 5 agree within rounding.
- L1 endpoints use `m-h-B` and `m+h+B`, not a second addition of the attribution
  floor. For ALPHA decode, `51.20643-0.09802-2.17881 = 48.92960` and the upper
  endpoint is `53.48326` J. ALPHA prefill's printed `h+B` is `2.92648` J, giving
  `[23.32743,29.18039]` J; RESULTS' endpoints differ by 0.00001 J and are covered
  by the three inputs' rounding. Both BETA endpoint pairs reproduce as printed.
- The four L1 per-token divisions are `51.20643/512`, `26.25391/2048`,
  `198.36172/512`, and `128.28329/2048`; they print `0.100013`, `0.0128193`,
  `0.387425`, and `0.0626383` respectively.
- The BETA floor compositions reproduce: `9.01530+1.16277 = 10.17807` J and
  `7.66749+1.16277 = 8.83026` J. This checks addition, not the null-floor or
  NEG-8 input values. `max(5.76593,10.17807)` and `max(8.21484,8.83026)` give
  the two printed active gates.
- The cross-window identity gives
  `(198.36172-0.42167)-(51.20643+0.10423) = 146.62939` J and
  `(128.28329-0.26101)-(26.25391-0.04107) = 101.80944` J. Differences of
  0.00001 J from the contrast estimates fit the four inputs' rounding. This
  checks a GAMMA identity, not an ALPHA-versus-BETA comparison. The deltas and
  their agree/differ decisions still need the actual GAMMA arm means/half-widths.

### Exclusion counts and restored-unit arithmetic

Recounting the **printed** removed-member table gives nine distinct removed
quads: four decode and five prefill. Therefore `9*4 = 36` removed bundles,
`9*2 = 18` per model; decode loses eight bundles per model, prefill ten. Kept
counts are `10-4 = 6` and `10-5 = 5`, the latter exactly the registered minimum.
The lost-quad fraction is `9/20 = 45%`.

There are eleven distinct triggering contrast members. Counts by side are
eight B and three A; by position, B1=5, B2=3, A1=1, A2=2. Contention contributes
five B and one A; admission contributes two of each; the anchor failure is B.
The triggering-member fraction is `11/(20*4) = 13.75%`. Six contrast contention
members plus two named corpus and two named endpoint-reference members explain
the reported GAMMA total of ten **conditionally on a complete transcription**.
ALPHA's four and BETA's fourteen flags cannot be recounted from this table.

By stage, unique removed quads count `2,2,2,3`. Removing only the registered
load-correlated code exclusions restores decode b01/b05 (`6+2 = 8`) and prefill
b04/b06/b10 (`5+3 = 8`). Prefill b09 remains excluded because its admission flag
is retained. The restored **energies and intervals** are unavailable; the count
check does not verify `146.800` or `101.657` J.

The [committed attempt index](../../../configs/analysis/b5/analysed_windows.json)
and the [collection history](../../process_traces/2026-10-block5/seal2-gamma-a1-window.md)
independently of RESULTS support the attempt numbers: second-seal ALPHA=1,
BETA=6, GAMMA=1, five earlier unusable BETA attempts, and three superseded
first-seal ALPHA attempts. They are historical records, not an independent
traversal of the underlying archives or proof that no energy was ever read.

### Discrepancies and precision cautions for the lead

1. **Distinct causes:** RESULTS lines 239–240 say “four different causes”. The
   four stage-opening losses have the sequence contention, anchor failure,
   admission abort, contention: **three distinct categories**. The ledger marks
   this as the one non-blocked `MISMATCH`. No repair is made by this seat.
2. **Rounding order:** the displayed prefill lower-end/floor formula is
   `95.807/8.830 = 10.8501698754`, which rounds to **10.9** as printed. Using
   the fuller displayed inputs gives `95.80749/8.83026 = 10.8499058918`, which
   rounds to **10.8**. Thus the explicit coarse formula checks, but the last
   digit is not stable under the more precise source. The TSV explains this
   instead of labelling it an unexplained arithmetic failure.
3. **Collected versus succeeded:** RESULTS calls 103 of 107 members “collected”
   and four “not collected”. The collection record at lines 24–28 instead says
   **107 present, 107 raw-valid, 103 succeeded**. The numeric difference of four
   is supported; claiming four missing bundle files is not. The lead should
   settle the intended term before copying this sentence.
4. **Ratios have different estimands:** geometric per-quad energy ratio,
   request-level median idle-subtracted rail share, and median member gross
   phase share are three different quantities. In the pinned independent
   recompute, `phase_machine_mean` takes `median(member.gross_share)`.
   Dividing the printed L1 rail/meter means yields approximately `0.3422`,
   `0.3366`, `0.4538`, `0.4491`, agreeing coarsely with `0.34/0.34/0.45/0.45`;
   that is **not** an independent derivation of the published median shares.
5. **Catalog revision terminology:** the digest is verified at all seven Git
   pins; the JSON catalog has no numeric revision-12 field. Revision 12 is the
   governing registration revision. This does not affect the verified byte
   identity, but the phrase “catalog revision 12” should not be treated as a
   separately observed numeric catalog property.

## Missing inputs: stop list and item-83 hand-check requirements

The inventory used Git tree metadata, without filesystem traversal of any
restricted directory. At HEAD and the original results and lessons refs there
are no files named `recompute.json`, `comparison.json`, `verdict.json`, or
`B5-BLIND-DRY-RUN-RECORD.json`, nor filenames carrying the named result-artifact
hash prefixes in RESULTS §0. This is an absence finding about those named
sources in those refs, not a claim that every blob in every branch was searched.
Only synthetic test outputs are not acceptable substitutes for released inputs.

| Printed leaves/family | Released source needed; independent hand calculation | Disposition here |
|---|---|---|
| Core means, SD/SE, intervals, raw p, per-quad values | FILL/CV and committed RC values, with unrounded `d_k` and kept IDs; compute mean, sample SD, t tail and intervals by §7.1 | Rounded-text arithmetic only; root inputs blocked |
| L1 mean, h, B, attribution floor, kept counts | SENS/PROJ-A/PROJ-B and RC cells; kept repeat energies, quad means and timing-kind summaries; `m=.2*mean(r)+.8*mean(b)`, `V=.04*s_r²/n_r+.64*s_b²/n_b`, `h=t*sqrt(V)`, attribution floor from the largest member bound | Endpoint/per-token arithmetic only; component derivations blocked |
| Absolute/comparative floors, point diagnostics, R/R_cm | Released null values, admissible widths, guard/allowance, and common-mode replay numerators/denominators | Compose displayed operands only; 0.59–1.01 J diagnostics and four R_cm values blocked |
| Descriptive geometric ratios/intervals | Per-quad A/B means; average `log(B/A)`, take sample SD, exponentiate mean and exact-t endpoints (§7.3) | All six values blocked |
| Exclusion functions, all-window flag totals | EXC and the released stored-flag/roster list; apply catalog effects and drop whole units, deduplicate flag/member counts | Printed-table recount only; no independent flag detection or raw hazard read |
| Release evidence: 390, 78,389, 249, 403, 84, worker/exit values, all family row counts, zero counts and max residuals | REC/VER/CMP with their authenticated output manifests; count actual rows and compute `max(abs(difference))` per family | Blocked; implementation and prose cannot supply these counts |
| Monitor cost (uncovered family 1) | Named independent record of monitor/meter cumulative CPU-time endpoints and phase-probe count inputs; subtract endpoints and count probe/phase overlaps | 209.46 CPU-s, 94.02 CPU-s, 568 probes blocked |
| Arm/host hazards (family 2) | Released arm readings, rule inputs and per-window flags, with a separate source-check record | Arm battery amperage zero and hazard-dependent eligibility blocked |
| Battery (family 3) | Assist flags plus current/discharge qualification; count assisted kept quads and recompute without them | Zero assist quads and equality to primary blocked |
| Battery temperature (family 4) | Stage readings and plateau/rise classification inputs | No numerical temperature value is printed in RESULTS; no certification of the family's correctness |
| Reference/corpus/NEG-8 history (family 5) | Released retained/lost/capped member lists, reference values, survivor screen and allowance terms; count survivors and recompute screen | Planned seven is a definition; five survivors is conditional; clean corpus 12, screen and allowance sources blocked |
| Attempt history/G10 (family 6) | Committed index plus named contemporaneous collection records and a custody-reader check of their underlying inputs | Attempt ordinals/cause categories checked in committed second records; actual yields/G10 and “never analysed” claims not re-derived |
| Selection/full eligibility (family 7) | Frozen selected prompt/panel record and full top-up/replacement/current/transport checks | Design counts verified; realized tokens, clean sensitivity status, absence of top-ups and L2 ceiling blocked |
| Request whole-machine medians/ranges/reference share and plausibility/no-band counts | Released per-member `delta_rail`, `delta_machine`, meter/battery flags; `rho_i=delta_rail_i/delta_machine_i`, median/min/max, hard-band count and first-clean-window rule (§8.2) | 0.3606, 0.3532–0.3828, 0.3649, 0.3268–0.3842, 0.3912 and 0/103 blocked |
| Whole-machine phase energy/h/edge-shift/median share (RC-only) | RC per-member **gross meter-only** phase summaries and kept strata; estimator-1 mean/h, clock-shift envelope, median of member rail/meter ratios; final item-37 amendment governs | 149.65/589.25/57.85/285.62 J, h=0.17/0.57, edge bounds 9.07/12.17 J and four shares blocked |
| Load-correlated sensitivity (RC-only, exempt) | Restored-unit unrounded `d_k` and flags; retain other exclusion causes, then recompute §7.1 at n=8 | Restored counts checked conditionally; means and all four interval ends blocked |
| Scaled allowance and durations (RC-only) | Reference energy/duration means, arm phase energy/duration means, allowance and floor ingredients; factor `max(1,E_a/E_ref,E_b/E_ref,T_a/T_ref,T_b/T_ref)` for GAMMA; multiply only the allowance contribution, rebuild D/floors | 6.574/1.990/2.678/0.620 s, D=9.345/8.045 J and floor=15.228/11.685 J blocked; displayed scaled decision endpoints consistent with rounded D |

For the floor hand check, §5 defines an unguarded point floor as the maximum of
the largest deviation and the Student prediction bound, then takes the maximum
over the admissible corners and applies the small-sample guard. The operative
guarded floor receives the floor window's allowance before armwise maxima are
taken (RL-5(1)). None of the required null arrays/widths is in RESULTS. Solving
backwards from the printed floor would not be an independent check.

The known-bytes “about 76%” in RESULTS §7 is outside Block 5. Its named second
source is the admitted, non-claim
[slot fill](../../process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md),
line 60: `f=0.238`, hence `100*(1-f)=76.2%`, about 76%. This source check does not
open BYTES held-out data and does not equate the known-bytes contrast share with
Block 5's request/phase shares.

## The ten licence constraints checked against RESULTS §6

This reviews the existing proposed paragraph, table/caption and slide; it does
not edit them or review a filled paper that does not yet exist.

| # | Constraint from release-to-paper §2 D | Finding for §6 |
|---|---|---|
| 1 | ALPHA/BETA L1, separate windows/fixed order, never a comparison | No ALPHA/BETA cell comparison appears in §6. Their L1 cells remain correctly limited in §§1.2/5. |
| 2 | GAMMA L2 only when the claim gate allows | The paragraph says L2. The printed numerical inequalities support direction conditionally, but the gate/eligibility source is unavailable: **HOLD**. |
| 3 | Claims-ladder forbidden words | No affirmative scaling law, generality, per-parameter or whole-machine efficiency claim is made. The negated limitations are not forbidden assertions. Slide “cost” would be clearer as assigned phase energy. |
| 4 | Print both contrasts, select none; refusal is not equality | Both appear in paragraph, table and slide. No unresolved/zero substitution. **Text passes.** |
| 5 | Dominance sentence/subtitle only branch A; ratios with numerator, denominator, n and point-diagnostic label | §6 makes no dominance claim. Its caption's ratios are geometric energy ratios, not R/R_cm. Elsewhere RESULTS' four R_cm values lack their numerator/denominator/n, so they are not ready to copy as public diagnostic rows. |
| 6 | Fixed sentences verbatim or under the later interpretation | §6 paraphrases several fixed sentences without label citations and supplies no verbatim appendix. RL-4(xi) requires both the appendix and body label citations: **not ready**. |
| 7 | D-177 next to phase-energy statements, as interpreted by RL-4(x) | Table caption includes the instrument-check limitation. The proposed paragraph and standalone slide omit it: **not ready**. |
| 8 | Exact SoC boundary label; whole-machine meter only descriptive | Table caption has the exact label. The paragraph describes the rail boundary, but the standalone slide gives only “Rails”. Its boundary is insufficient. The request-share sentence also needs the DC-input-plus-battery/adapter-loss boundary and source check. |
| 9 | Sensitivity never replaces the result | §6 uses primary values and no sensitivity values. Elsewhere §4.5 labels RC-only lines uncompared/not paper-ready. **Text passes this distinction**; sensitivity sources still blocked. |
| 10 | Seven uncovered families only after hand check | The rounded whole-machine share in the paragraph has no completed source hand check here. Attempt/monitor and other missing leaves cannot be licensed by this report: **HOLD**. |

Additional later RL-4 checks: the proposed paragraph prints an adjusted-p bound
outside the results table, contrary to (ii); the slide lacks kept/planned counts
and the exact boundary, contrary to (iii); the paragraph states 9/20 loss and the
prefill minimum but omits the **8-of-11 triggering-member skew**, required by (v).
The paragraph's prefill parenthesis does not itself name the decision interval;
the table labels it clearly, but the prose should do so under (i). The slide's
unqualified “independently recomputed” needs the coverage qualification under
(vii). These findings are for the lead's repair/fill seats; this reader made no
prose correction. The proposed paragraph does retain the single-session and
unreleased-replication caveats.

## Next exact step / NEEDS_RULING

**Question for the lead:** will the missing source checks be supplied as a
committed, released-only verification packet, or completed by a separately
authorized custody reader with a committed hand-check record?

**Options considered:** (a) treat internal arithmetic and copied summaries as
completion; (b) obtain the released source leaves and independent hand-check
inputs/records; (c) open custody here. Option (a) does not satisfy RL-3. Option
(c) is forbidden by the brief and is not requested.

**Recommendation:** (b), retaining this seat's access limits. A packet should
bind FILL/CV/EXC/DISC/SENS/PROJ/STEP/REC/RC/CMP/VER to the SHA-256s in RESULTS,
name the second source for every uncovered leaf, and contain only approved
released aggregates. Raw-measurement checks that cannot be made from those
aggregates belong to the separately authorized reader. Re-run the ledger against
that packet, disposition the distinct-cause/wording findings, and have the
research lead adjudicate. Until then, no gate-passing or paper-fill claim follows
from the `exact`/`within-rounding` rows.

**Blocked work:** the 207 `BLOCKED_INPUT` ledger rows and full source validation
of dependent outputs; resolution of the one visible discrepancy and the §6
licence findings is lead-owned. No unexplained numerical mismatch was concealed,
and no absent input was replaced with fixture evidence.

## Reproducible independent arithmetic kernel

This code uses literal released printed inputs only, imports no repository
module, opens no file, and can be run with `python3.13 -I -B`. It demonstrates the
calculation independently of both implementations. TSV notes give the remaining
individual additions/divisions/counts and their exact input sources.

```python
import math
import statistics as st

def student_two_sided(t, df):
    # Integrate the t tail using I_x(a,b)'s direct power series.
    a, b = df / 2, 0.5
    x = df / (df + t*t)
    term = total = 1.0
    for k in range(1, 10000):
        term *= (a+k-1)*(1-b+k-1)*x / ((a+k)*k)
        total += term
        if abs(term) < abs(total)*1e-16:
            break
    else:
        raise ArithmeticError("beta series did not converge")
    return math.exp(a*math.log(x)-math.log(a)-math.lgamma(a)
                    - math.lgamma(b)+math.lgamma(a+b))*total

def t975(df):
    lo, hi = 1.0, 10.0
    for _ in range(80):
        mid = (lo+hi)/2
        if student_two_sided(mid, df) > 0.05:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2

assert abs(student_two_sided(1, 1)-0.5) < 1e-14
assert abs(student_two_sided(1, 2)-(1-1/math.sqrt(3))) < 1e-14
cases = [
    ([146.637,146.443,146.646,146.439,146.685,146.926],
     146.62940,0.073524,5.08409,512),
    ([101.588,101.737,101.604,101.802,102.316],
     101.80943,0.132867,5.63310,2048),
]
for ds, mu, se, bound, tokens in cases:
    n = len(ds)
    mult = round(t975(n-1), 3)
    half = mult*se
    loo = [st.mean(ds[:i]+ds[i+1:]) for i in range(n)]
    print("rounded-d_k stats", st.mean(ds), st.stdev(ds),
          st.stdev(ds)/math.sqrt(n))
    print("summary-input CI", mu-half, mu+half)
    print("summary-input decision", mu-half-bound, mu+half+bound)
    print("p", student_two_sided(mu/se,n-1))
    print("per token", mu/tokens, "LOO", min(loo), max(loo))
```
