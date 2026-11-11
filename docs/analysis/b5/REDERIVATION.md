# Block 5 independent reader: RL-41/RL-42 print authority

**2026-11-11 RL-55 round 5:** D1–D3 are addressed: physical row **1846**
prints the independently replayed 1.7B prefill R_cm at **1.99975**;
the five BYTES coverage reasons name their sealed, outside-Block-5 scope;
and `origin/main` is merged. Both fill checkers pass on the working-tree
paper. The 1,844 earlier rows and RESULTS remain byte-identical. See the
[round-5 report](../../run_reports/2026-11-11-p1-b5-ledger-ext.md#round-5--opus-delta-fixes-d1d3).
The new print-authority commit is recorded there after the implementation commit.
Lead acceptance/event-log audit remain owed.

**2026-11-11 RL-55 round 4 (historical):** 425 append-only rows complete the session
disclosures and required coverage map; see the round-4 section below. The
original 1,419 rows and RESULTS are unchanged. Opus review/lead acceptance
remain owed.

**2026-11-11 RL-52 round 3 (historical):** the Opus cold review is
[ADMIT-WITH-FIXES](../../run_reports/2026-11-11-p1-b5-ledger-ext-opus-coldreview.md).
F1–F4 are addressed in prose and checker code; **no ledger row changed**.
The new print-authority commit is recorded in the round-3 section below.
The second fill must apply the row-pairing instruction for rows 647–651 and
1064–1065. F5's session scope was subsequently authorized by RL-55 and is covered below.

**2026-11-11 RL-52 round 2:** the lead clarified access to exact hash-pinned
descendants, and 618 further rows complete this reader's extension. The ledger
now has **1,419 rows**. Every previously committed row remains byte-identical:
538 original rows at `0b8763f0a`, then 263 round-1 rows at `b9ea4cd11`.
No new mismatch or outside-source hold was found. **The extension still needs
the prescribed Opus cold review and lead adjudication before the second fill.**
See [Rows not printed by RESULTS.md (RL-52)](#rows-not-printed-by-resultsmd-rl-52)
and the [round-2 report and table commit](../../run_reports/2026-11-11-p1-b5-ledger-ext.md#round-2--pinned-descendants-authorized).

## Errata to RESULTS.md

2026-11-10, research lead RL-39. [RESULTS.md](RESULTS.md) remains byte-identical.

- **§2.2, “four different causes”:** four losses, **three distinct causes
  (contention twice, an anchor failure, an admission abort)**. The committed
  attempt index selects the second-seal GAMMA attempt; its authenticated
  `EXC.cells[*].dropped_units[unit_id ends b01 or b06].codes` supplies the four
  stage-opening causes, in stage order: contention, anchor failure, admission
  abort, contention. The index itself contains attempt-level causes, not
  within-attempt stage causes. This is a wording erratum, not a deviation.
- **§1 derived margin, prefill “10.9”:** the third significant digit is
  undetermined at the displayed input precision: `95.807/8.830 = 10.85017`,
  whereas `95.80749/8.83026 = 10.84991`. Paper 1 prints **“about 11”**.
  Under RL-39 a derived ratio uses the fullest released precision, rounds once,
  and prints at most two significant figures. The phase-1 coarse-input check
  does not license “10.9” for the paper.

**Clarification, RL-42 (not an erratum):** §4.1's count is **84 normalized leaf paths; 118 scalar leaves**.
List indices collapse to `*` in the comparator's path unit. DLE-5 was right;
no deviation-log note is added. Paper 1 prints no count; any future count must
carry its unit.

**Clarification, RL-55 (not an erratum):** 1.7B prefill R_cm appears at
`1.9997` in RESULTS (row 277) and `1.99975` in the round-5 extension (row 1846).
Rows 502, 570 and 848 also retain their original four-decimal `1.9997`.
The second fill takes the row with more digits and prints this one at five
decimals, **1.99975**; it is below 2 either way. Other R/R_cm keep four decimals.
This is a last-place precision difference, not a new mismatch.

## Current ledger disposition and printing rule

Sol seat `p1-seat4-p3` applies research-lead **RL-41(b), as amended by RL-42**,
read verbatim from `origin/audit/2026-11-10-fable` at
`2eb2df03699e815e4634ce41fd62ac7d77d0d226`, to the phase-2 ledger and
[Opus cold review](../../run_reports/2026-11-10-p1-seat4-opus-coldreview.md)
at `9159dbf05`. RL-42 corrects RL-41(a). **RL-3's Block 5 number gate is closed
by RL-42**, subject to the row and composition rules below. The ledger commit
recorded in the [seat-p3 report](../../run_reports/2026-11-10-p1-seat4-p3.md)
is the print authority; this report does not supply a new custody check.

The original 538 rows of the [ledger](rederivation.tsv) have **261 exact, 256 within-rounding
(517 together), 6 recorded-judgment, 14 single-source, and 1 MISMATCH**.
Physical TSV row numbers include the header and remain stable.

| Check word / rows | Paper 1 disposition and obligation |
|---|---|
| `exact` / `within-rounding` | `print`, subject to every input row also passing and the exceptions below |
| `recorded-judgment`: 341, 342, 525, 526, 532, 535 | `print-labelled`: attribute the collection-time judgment to its pinned source in the sentence or table note; not re-derived (§4.7) |
| `single-source`: 236-241, 362, 367 | `print-labelled`: “from the independent recomputation only”; never in the abstract or conclusion or as support for a claim word. Duration ratios use two significant figures (RL-39); edge-shift values accompany any whole-machine phase energies, labelled. |
| `single-source`: 348-350 | `print-labelled`: “from the registered disclosure record; not independently recomputed”; same abstract, conclusion and claim-support exclusions |
| 388-395, including `single-source` 392-394 | All `not-printed`: the scaled-allowance line is not registered; none of it prints in Paper 1 |
| `MISMATCH`: 249 | Ruled RL-39 wording erratum above; the original “four different causes” cannot print |

`match` records the check; the new `paper1` column records placement. `print`
alone never clears a mismatch or a failing dependency. A fill must cite its
ledger row, respect its label, and pass by composition. Recorded judgments
and single-source leaves are accepted only with the attribution/labels above.

Rows 530, 531, 533 and 534 are `exact`: the Opus arithmetic applies the
registered outcome rule (estimate exceeds floor gate, both intervals exclude
zero, Holm rejects, leave-one-out keeps sign and floor); the comparator also
agrees. The not-estimable prerequisites remain recorded judgments. Rows
242-244, 490-492 and 528 are arithmetic **over stored flags**, not raw hazard
re-detection. Row 529 is `exact`: compared by the release comparator (189
sensitivity rows agree); the acceptance record's alignment bounds are inputs.
Rows 388-391 and 395 are `within-rounding`, with **“hand check: Opus cold review,
bound argument”**; the prefill bound does not decide the factor for 392-394.

Every committed `difference`, including `source difference=` in ledger notes,
is rounded to **two significant figures** (exact zero stays `0`; missing
differences stay blank). Check words are determined before rounding. The
[157-row hand-check table](hand_checks_phase2.tsv) keeps its original rows and
24 exact / 133 within-rounding check words; the five accepted Opus bound checks
are recorded in the main ledger and review. No history is rewritten.

Both readers have `--repo-only` modes that read the frozen Git tables at
`9159dbf05` and current repository tables. The seat reader regenerates both
tables with the rulings and rounded residuals; its default repository mode
requires byte equality. The Opus reader independently checks residual
serialization, hand-table byte equality, ledger links, counts and placement.
These modes **do not rerun custody arithmetic**. The original custody modes
still require separately authorized access; no custody path was opened for p3.

```sh
python3.13 -I -B docs/analysis/b5/hand_check_phase2.py --repo-only
python3.13 -I -B docs/analysis/b5/opus_coldreview_check.py --repo-only
```

The post-fill sentence check against RL-4's licence constraints remains owed;
RL-27's site-build hold remains, and slides stay under RL-10. RL-42 asks the
lead to tell Ed that full-precision residuals already exist in public history;
this seat records that handoff without sending a message or rewriting history.

## Phase 2 evidence and limits (historical run; dispositions updated above)

Fresh Sol seat `p1-seat4-p2`, branch `p1-seat4-p2`, base
`35b0e98d12cde94d3522419c45da9b417613e2d4`. Authority: RL-3, RL-38 and RL-39,
read verbatim from `origin/audit/2026-11-10-fable` at
`529a6772724faa8e001b0b9e106524e618da1084`. At that run's close RL-3 remained
open; RL-42 subsequently accepted the Opus review and lead event-log audit
and closed the number gate under the current rules above.

All **207 phase-1 input stops were sourced** from the named frozen leaves or
explicit counts over them. At phase-2 close the ledger had 254 exact,
251 within-rounding, 2 MISMATCH and 31 source-outside-unseal. RL-42 resolves
the count's unit, leaving only the known four-versus-three wording mismatch,
and replaces the outside holds with the current dispositions above. Counts
include repeated presentations, definitions and auxiliary checks. The 270 rows
not revisited in phase 2 retain their narrower phase-1 notes and pass only
by the composition rule, not by a blanket certificate.

New columns separate `source_value`/`source_match` from the final `match` and
`hand_check`, preserve `phase1_match`, and record the arithmetic `difference`
(re-derived minus printed, in the printed unit; percentages use percentage
points). Source differences are also in each updated note, now rounded under
RL-42. A copied aggregate can agree without being independently re-derived.
`MISMATCH` now means an actual disagreement; no missing source uses that word.
Physical TSV row numbers include the header and are stable from phase 1.

The [157 hand-check rows](hand_checks_phase2.tsv) give each printed value,
member/quad input key paths, formula, re-derived value at printed precision and
residual. All 157 agree at printed precision. The data-free
[stdlib reader and hand-check script](hand_check_phase2.py) imports no repository
analysis or recompute code. It reconstructs the primary quad differences,
means/SD/SE/t tails/Holm, geometric ratios, intervals and per-token quantities;
the four stratified reported cells and their timing averages; floor box corners
and common-sign dominance replay; request median rail shares; whole-machine
phase means, h and median member shares; and the load-correlated sensitivity
with only the registered load codes ignored. Recorded timing widths, retained
IDs and allowance summaries are named inputs: this does not independently
refit clocks or re-detect raw hazards.

Phase-energy arithmetic is internal, within **M3 Max / MLX / powermetrics SoC
rails**, gross assigned phase energy, one session. Phase attribution is reported
without a measured instrument phase-accounting check (D-177). The whole-machine
phase check uses gross meter-only energy and retains its separate DC-input
boundary; request shares include the battery term. Ratios of cell means are
never substituted for medians of member ratios or geometric quad ratios.

### Row 522: normalized paths and scalar instances (RL-42)

RESULTS §4.1's **84** counts normalized leaf paths, the comparator's unit.
Counting scalar instances in the same DLE-5 groups in frozen FILL gives **118**:

| Contrast | Floor diagnostics | Resolution diagnostics | Entire claim floor-limit object | Total |
|---|---:|---:|---:|---:|
| Decode | 10 | 10 | 24 | 44 |
| Prefill p2048 | 20 | 20 | 34 | 74 |
| Both | 30 | 30 | 58 | **118** |

The scalar count includes strings and booleans in
`FILL.gamma.contrasts[*].floor.point_floor_diagnostics`,
`.floor.resolutions[*].point_floor_diagnostics`, and
`.claim_evaluation.floor_limit`. Numeric leaves alone total 56. An independent
cross-check is 96 mapped comparator leaves (54 numeric diagnostic terms,
36 diagnostic labels/flags, four class/source words, two published floors),
plus 22 newly named exempt discipline leaves. Collapsing list indices gives
44 claim floor-limit paths, 30 floor-diagnostic paths and 10
resolution-diagnostic paths: **84**, also `14 + 10C + 5R` with C=6 and R=2
over both contrasts. The Opus cold review established this unit; RL-42 adopts
it and corrects RL-41(a). Row 522 is `exact`, re-derived/source value 84 and
difference 0. No RESULTS or DLE-5 edit is needed.

### RL-3 item 3 coverage

| Required family / line | Independent check and remaining boundary |
|---|---|
| Monitor cost | All three aggregates sourced; `single-source` under RL-41 with the disclosure label, not independently recomputed. CPU endpoints and probe/phase overlaps are absent from §0 files. |
| Arm and host hazards | Stored member-code recounts reproduce contention totals 4/14/10, over stored flags; this does not re-detect hazards. Arm battery 0 is a `recorded-judgment` attributed to the pinned disclosure. |
| Battery | Zero assist quads is a `recorded-judgment` attributed to the pinned disclosure. Member activity diagnostics do not replace raw `battery.assist` flags and fallback qualification. |
| Battery temperature | All 30 stage reading arrays checked independently: rise=(last-first)/100, last-three range ≤50 centi-C, rise>3 K without plateau. Zero arithmetic/classification differences. No stage temperature value is printed in RESULTS. |
| Reference/corpus/NEG-8 history | Retained-ID lists give five deciding references and a clean corpus of 12, with seven references planned. Raw clean-corpus selection and full screen decision are not independently replayed. |
| Attempt history/G10 | All 11 index entries agree with DISC on attempt and cause key; zero differences. Stage-opening causes come from indexed EXC, not the attempt-level index alone. “Never analysed” and raw G10 execution are not proved by the records' declarations. |
| Selection/full eligibility | All 44 included GAMMA token-provenance records source the output count. Top-up absence, replacements and the L2 ceiling print as attributed `recorded-judgment` inputs, not re-derived eligibility. |
| Printed exempt leaves | RL-41/RL-42 accept the attributed recorded judgments and labelled single-source values; these remain distinct from independent arithmetic. |
| Recompute-only whole-machine phase lines | Means, decode h and all four median member shares independently agree. The two edge-shift maxima are `single-source` and print labelled with any whole-machine phase energies. |
| Recompute-only load sensitivity | Independent member-energy arithmetic reproduces 146.800 [146.439,147.161] J and 101.657 [101.224,102.089] J, each n=8, restoring two/three quads. L9 remains not computable; this is an uncompared check. D-177 applies as above. |
| Recompute-only durations/scaled allowance | Durations/ratios are labelled `single-source`. Opus's bound checks pass rows 388-391 and 395; prefill 392-394 remain `single-source`. All scaled-allowance rows 388-395 are `not-printed`. |

The historical 31-row outside list, all phase-2 custody paths and before/after
hashes are in the [phase-2 run report](../../run_reports/2026-11-10-p1-seat4-p2.md).
The [source manifest](phase2_sources.tsv) contains 12 custody files. All full
§0 pins agree; PROJ-A/B have only truncated pins in §0 and also agree with their
full content-addressed filenames and the full pins in authenticated REC.
VER's SHA-256, absent from §0, is recorded. Every opened custody file was
re-hashed unchanged at the end. Referenced paths stayed inert; no raw archive,
night custody, Block 6, BYTES or ALIGN v4 source was followed.

The historical repository-only report below is retained as phase-1 evidence.
Its “no custody” and “blocked/mismatch” descriptions apply to that earlier run
only; current disposition and vocabulary are above. Its review of RESULTS §6
remains a historical text review. The filled paper's RL-4 licence review is
still the later gate specified by RL-38.

---

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

## Rows not printed by RESULTS.md (RL-52)

### Round 1 (historical access hold)

2026-11-11, Sol seat `p1-b5-ledger-ext`, branch
`analysis/2026-11-11-b5-ledger-ext`. This is a **partial extension**, with
263 new rows at physical TSV lines **540–802**. The new table commit is
recorded in the [run report](../../run_reports/2026-11-11-p1-b5-ledger-ext.md).
The original header and all 538 original rows remain byte-identical to
`0b8763f0a8291bfa5d47fdc18aa64ef3aa33ec1b`; their row numbers do not move.
`RESULTS.md` remains byte-identical, SHA-256
`fb5f81e8741532d79b059b2ca7c44b1c479f0f983c28527ab6e2511d7dfb6f55`.

The source for every new row is **RC**, the already pinned
`release-check-final-20261108T0942Z/recompute.json`, SHA-256
`c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc`.
Every open authenticated the file before JSON parsing and re-hashed it in a
`finally` block. The script follows no path inside it. No file under
`dry-m/dry-run/restricted/` was opened, listed or statted by this seat.

| New rows | Coverage |
|---|---|
| 540–606 | Eight independent R, their 16 terms, eight n and pass words; four comparative floors; four R_cm with numerator, denominator, n and pass; branch and failure counts |
| 607–712 (interleaved by cell) | Three kind averages of B, attribution-floor attaining run and minimum, ALPHA/BETA removed-unit codes and counts, per-cell battery/load numeric lines and counts, four cross-session deltas, half-widths and agree booleans |
| 713–721 | Nine removed contrast quads, each with its codes as a row value, checked by unioning the member codes |
| 722–784 | All three packs' model-specific request-level ρ medians, ranges, quartiles, within-model spreads, consistency words, member counts and hard-band failure counts |
| 785–802 | ALPHA/BETA gross-family NEG-8 corpus/reference counts, both bound terms, bound, spread and allowance |

[hand_check_rl52.py](hand_check_rl52.py) uses independent stdlib arithmetic,
with the earlier reader's stdlib numerical/access helpers. It imports no
repository analysis or recompute code. Each TSV row carries its key path,
source hash, formula, value at ledger precision and residual to two significant
figures. No member energy, current, temperature or timing series is serialized.
Shared trace-sweep widths remain pinned member/quad inputs, as in the earlier
hand checks; scalar member energies do not reconstruct the raw trace sweep.

The dominance point bound is the registered maximum of the envelope and
Student prediction term. Independent-sign corner enumeration supplies the
numerator; the denominator is the unguarded point bound. Comparative floors
apply the small-n guard and gross NEG-8 allowance. R_cm uses one shared sign
with independent local signs. **All eight R pass; three R_cm fail; branch B
is reproduced; no nonpositive denominator is encountered.**

Reported-cell calculations retain fixed weights 0.2 and 0.8. B's three
averages are the clock bound, zero interval-support interpolation bound, and
half the gross allowance. The attaining run is the argmax of the first-kind
bound over kept members; the other two kinds do not have unique attaining
runs. Load restoration requires that a dropped unit's complete nonempty code
set be load-only; a mixed-code unit stays removed. The eight battery-assist
counts are copied recorded inputs, labelled `recorded-judgment`; the numeric
without-assist lines are independently calculated conditional on those inputs.

For cross-session agreement, the rule is
`abs(G-F) <= hypot(h_G,h_F)`. G and h_G use GAMMA **quad-arm means**, while F
and h_F use the registered stratified floor-session estimator. The four deltas
also agree at the precision of original rows **169–172**. These new booleans
are derived words, not recorded judgments. A direct check against DISC's
`cross_window` rows is still blocked by the access question.

New-row words: **118 exact, 137 within-rounding, 8 recorded-judgment**;
zero new MISMATCH and zero source-outside-unseal rows. Whole-table words:
**379 exact, 393 within-rounding, 14 recorded-judgment, 14 single-source,
1 MISMATCH** (the unchanged RL-39 row 249), **801 total**.

The unsourced remainder is the attempt-disclosure causes/counts, arm hazards
and stage temperatures/physics counts, monitor costs, floor-limit class
leaves, full two-family NEG-8 verdict/loss/cap/spare disclosures, and direct
DISC/projection checks for the rows above (including the agree/differ words).
Their files are **inside** the two named roots but under the separately
forbidden real `restricted/` directory. They are authority-blocked, not
factual mismatches or sources known to be outside the unseal; no fabricated
ledger status is assigned. The run report records the question and next step.
The new `paper1` placements describe row-level eligibility only: **the extension
still needs its own Opus cold review and lead adjudication before a second fill.**

### Round 2 (access clarified; reader extension complete)

The resumed brief explicitly supersedes the real-`restricted/` prohibition for
exact hash-pinned descendants of the two RL-38 roots. Round 2 opened only **RC,
FILL, DISC, EXC, PROJ-A and PROJ-B**, at the exact paths and full hashes in
seat 4's phase-2 manifest. No directory was inventoried. Every file was hashed
before JSON parsing and re-hashed unchanged in `finally`, including development
runs. The complete path/hash table and successor print-authority candidate are
in the [round-2 report](../../run_reports/2026-11-11-p1-b5-ledger-ext.md#round-2--pinned-descendants-authorized).

[hand_check_rl52_round2.py](hand_check_rl52_round2.py) appends physical TSV rows
**803–1420** and replays the round-1 arithmetic against its frozen bytes. It
uses only stdlib arithmetic and the earlier independent reader's helpers; no
repository analysis/recompute program is imported or run. It refuses a changed
801-row prefix or an existing differing append. The historical pending-source
notes on round-1 rows remain unchanged; the rows below supply their registered
source counterparts. They are checks/presentations, not 618 independent observations.

| New physical rows | Source and coverage |
|---|---|
| 803–864 | DISC's eight R and four R_cm: each ratio, numerator, denominator, n and complete status, independently reconstructed from member energies/widths; branch and sentence-licence word |
| 865–868 | DISC's four comparative drift-widened minted floors |
| 869–884 | FILL's four arm-resolution and two contrast/claim floor-limit classes and sources; D-078 attribution condition is distinct from the dominance branch |
| 885–949 | ALPHA/BETA attempt counts, cause sets and cause multiplicities, individual verdict/cause/attempt leaves, succeeded and planned counts, including superseded ALPHA history |
| 950–1111 | PROJ-A/B's three B kind averages and attribution-floor attaining run/minimum; removed-unit codes/families; full per-cell primary/without-assist lines; computed cross-session booleans and agree/differ words; load lines, restored counts and registered refusal |
| 1112–1159 | EXC's nine removed contrast quads' codes/families and all 15 triggering members' code/family sets as row values |
| 1160–1287 | ALPHA arm measurements/verdicts, physics counts, monitor cost, ten stages' temperature summaries, per-model request-level ρ, both NEG-8 family bounds/screens/allowances, retained/lost references, spare-record count and corpus loss/cap counts |
| 1288–1420 | Corresponding BETA window disclosures, including its five corpus physics drops |

Both gross and idle-subtracted NEG-8 checks use member-level inputs: gross
request energy from `RC.members`; idle-subtracted rail request energy from
`RC.disclosures.whole_machine.windows[*].members[*].phases.request.rail_delta_J`.
The envelope and Student terms use the realised endpoint sizes. Screen words
are derived by comparing the independent endpoint difference with the bound;
the overall word requires both families. Midpoint movement affects the
allowance, not the endpoint screen. Raw clean-corpus selection remains a
recorded input; its membership counts, drop-code counts and first-12 desk cap
are independently checked. Separate counts give no disclosed measured spare
records and no deciding spares; this does not replay raw retry logs outside
the pinned record.

The four cross-session words are computed from `abs(G-F) <= hypot(h_G,h_F)` and
checked against DISC's boolean and sentence. This gives three **agree**, one
**differ**; the latter is 8B decode. The original unchanged physical rows 169–172
are replayed as part of this check. No agree/differ word is a recorded judgment.

B's first kind is the stratified mean of clock bounds, the second is zero
interval-support interpolation, and the third is half the window's gross
allowance. The **attribution floor**, a maximum rather than a kind average,
has the recorded attaining run. The two constant kinds do not have unique
attaining runs; the projection defines no such extra fields.

The registered load line exists for ALPHA prefill and both BETA cells, but not
ALPHA decode. ALPHA prefill and BETA prefill agree numerically with independent
restoration/re-estimation. **BETA decode is refused by the registered pipeline**
with `whole_window_verdict_provenance_invalid`. Its round-1 RC numeric line
remains independently hand-checked and **uncompared**. A fill must state the
registered refusal beside that numeric line; it must not imply a registered
numeric comparison. The refusal/status rows source metadata exactly; this
reader does not reproduce the pipeline's provenance failure.

**Second-fill instruction (Opus F4):** physical rows **647–651** retain their
historical bare `print` placement and pending-source note. Print those rows
only paired with the registered refusal in rows **1064–1065**, labelled
**"recompute only; not compared"**. The row-level placement alone does not
license an unqualified numeric load line. This instruction is for the second
fill; the paper and every ledger row remain unchanged in round 3.

Arm probe readings/verdicts, assist flags, harvest stage flags and attempt
verdict/cause leaves remain attributed `recorded-judgment` inputs. Stage rises,
plateaux, diagnostic flags and physics counts are arithmetic over those stored
inputs. Monitor cost and earlier attempts' non-null succeeded/planned counts
are `single-source`, labelled **"from the registered disclosure record; not
independently recomputed"**. Analysed-attempt counts are independently recounted
from the pinned member records. No raw archive eligibility or live hazard is
re-detected. No temperature reading array or member energy is serialized.

| Ledger word | Round 2 | Whole ledger |
|---|---:|---:|
| exact | 352 | 731 |
| within-rounding | 162 | 555 |
| recorded-judgment | 84 | 98 |
| single-source | 20 | 34 |
| MISMATCH | 0 | 1 |
| source-outside-unseal | 0 | 0 |
| Total | 618 | 1419 |

The sole MISMATCH is unchanged physical row **249**, the ruled RL-39
"four different causes" wording erratum. No outside-source row remains for
this assignment. This is the Sol reader's completed extension, not the Opus
cold review or the lead's final acceptance/print licence.

### Round 3 (Opus F1–F4; repo-only)

**NEW PRINT AUTHORITY SHA:** `60f66800fabe02c574dab41b2a61f38623c47a0c`
(`fix: address RL-52 ledger cold-review findings F1-F4`). This is the final
round-3 fixes/table commit; a documentation-only follow-up records its SHA.
The unchanged ledger is the reviewed 1,419-row table, with F4's composition
rule below. This records no new custody validation or second-fill acceptance.

The XWIN **differ** cell is **8B decode**; round-2 prose above and the run
report are corrected. Physical rows 647–651 remain immutable and are
**recompute-only** in the second fill: pair them with refusal rows 1064–1065
and label **"recompute only; not compared"** as instructed above.

The full 1,419-row ledger remains SHA-256
`5546bfd273fee3fc1f5277fed6d8ea8492f6ee02465541e10ba00a4363026008`.
`docs/paper/paper1/fill_check_b5.py` pins that complete table and separately
requires the header plus original 538 rows to equal the bytes at
`0b8763f0a8291bfa5d47fdc18aa64ef3aa33ec1b` (SHA-256 `0462f814…b84343`).
Tests reject independent perturbations of every ledger printed-value cell
and every row value cited by the existing first fill.

All five Python checkers in this directory support `--repo-only`. Round 1
checks physical rows 540–802 and the original prefix; its custody replay is
also scoped to that range. Round 2 checks the entire frozen ledger. The Opus
RL-52 checker independently compares the reviewed bytes and extension
residual precision. These modes check repository bytes and serialization;
they do **not** rerun custody arithmetic or source comparisons. Custody modes
require separate authority and were not run in round 3.

The round-3 [run report](../../run_reports/2026-11-11-p1-b5-ledger-ext.md#round-3--opus-cold-review-f1f4-repo-only)
records the commit, verification and the base branch's pre-first-fill paper
limitation. The paper was not edited.

## Round 4 — RL-55 disclosure extension and fill coverage

Round 4 appends **425 rows**, physical TSV lines **1421–1845**, for **1,844
rows** in total. The header and all **1,419** existing rows remain byte-identical
to round-3 authority `60f66800fabe02c574dab41b2a61f38623c47a0c`. RESULTS is
unchanged. **NEW PRINT AUTHORITY SHA:** `ffe8137beef723e06c381c91267df099f9665261`
(`docs: extend Block 5 ledger and fill coverage under RL-55`). A documentation-only
follow-up records this implementation/table commit; it changes no ledger or code. Lead acceptance and the
prescribed Opus cold review remain separate gates.

| New physical rows | Content |
|---|---|
| 1421–1504 | ALPHA/BETA window battery counts, unread-arm counts, lost-reference identity/slot, stage names and removed-unit position metadata |
| 1505–1535 | GAMMA window battery counts, unread-arm count, nine arm probe lines, physics counts and lost-reference names/slots |
| 1536–1605 | Ten GAMMA stage names, rises, plateau/diagnostic/harvest flags; no reading arrays |
| 1606–1642 | GAMMA gross and idle-subtracted NEG-8 bound terms, screens, allowances, references, lost/spare/midpoint and corpus/drop/cap counts/reasons |
| 1643–1650 | GAMMA attempt count, causes/multiplicity, attempt, verdict and succeeded/planned counts |
| 1651–1793 | All 24 comparator families: pass/fail/compared counts, applicable absolute/relative bars, numeric largest differences and agreement words |
| 1794–1809 | Sixteen removed reported-unit names as printable values |
| 1810–1845 | Nine removed contrast-quad names, strata, stages and positions as printable values |

The three pinned files and their before/after hashes are recorded in
[round4_sources.tsv](round4_sources.tsv) and the round-4 run report. Only RC,
DISC and CMP are opened. The new [hand checker](hand_check_rl55_round4.py)
uses independent stdlib arithmetic from the round-2 checker. GAMMA NEG-8
uses the realised endpoint counts and both energy families, with the same
registered bound, screen and allowance rules as ALPHA/BETA. Temperature
rises and flags are calculated without serializing thermistor readings.
A `none` rise means fewer than two readable readings; it does not itself mean
that the stage had no temperature reading.

Window battery counts are sums of disclosed per-code flag-count records,
cross-checked against RC's by-code counts. These are arithmetic over stored
flags, not a new detection of assist. All three packs have zero
`<module>.arm_unmeasured` flags. Empty arm measurement maps alone do not imply
an unread hazard. Arm readings/verdicts and stage harvest flags retain
`recorded-judgment` with attribution. GAMMA succeeded/planned counts are
independently recounted from pinned member rosters. Comparator counts,
numeric differences and words are recalculated from its issued comparisons;
no analysis pipeline or comparator implementation is run. `window_edge_s`
has zero comparisons and the word **not-compared**. It has no observed maximum;
categorical families likewise have no numerical maximum.

| Ledger word | Round 4 | Whole ledger |
|---|---:|---:|
| exact | 370 | 1101 |
| within-rounding | 25 | 580 |
| recorded-judgment | 30 | 128 |
| single-source | 0 | 34 |
| MISMATCH | 0 | 1 |
| source-outside-unseal | 0 | 0 |
| Total | 425 | 1844 |

The sole MISMATCH remains physical row **249**, RL-39's ruled wording erratum.
All new residuals have at most two significant figures. No new mismatch or
source-outside-unseal row was found. Shared trace-sweep widths, raw selection
eligibility and collection-time judgments retain the earlier limitations.
The full ledger SHA-256 is
`2f15d0810ae6123c42871e7101e880440e4c46ad350f707058d3fd5e7a988469`.

### Required coverage table (RL-55)

[fill_coverage.tsv](fill_coverage.tsv) is the complete **element-by-element**
map, updated in round 5: **1,582 elements**, **65 placeholders**, comprising all **57** still-pending
Block 5 ids plus the primary-block parts of **8** mixed placeholders. It
pins the merged paper snapshot
`9fb42569069b4b7f47b020ec794864101410e8c8` and verifies that the working-tree
paper equals it, including each FILL's full description and source line.
No Block 6, BYTES or v4 output was read. Mixed placeholders
are inventoried for completeness; this does not authorize their second fill.

Every mapped leaf has a physical ledger row. Every other element has one
of RL-55's three reasons or D2's explicit sealed-BYTES scope label,
with its committed file where applicable:
**1,540** element/row entries, **22** names from committed files, **11** needing
Block 6, **5** outside Block 5 (BYTES; sealed), **4** not leaves of the registered
Block 5 outputs. The last group
contains the unissued refusal of an unselected branch, the explicitly
dropped B-share and cross-block/publication/probe
items outside this ledger, not a missing registered Block 5 result. There is
**no unsupplied registered Block 5 output element** in the 57 pending ids.
The abstract/conclusion retain their replication/freeze/author gates.

The table below is a per-placeholder index. The machine file supplies the
individual element, exact row, attribution/conditional sentence and exception;
it is not enough to cite the union of a composite's rows without those rules.
In particular: BETA decode load rows 647–651 must be paired with 1064–1065 and
labelled **“recompute only; not compared”**. The three agree words and the
8B decode **differ** sentence are registered computed results. The latter's
full sentence belongs in results prose (RL-55). No central band or later
inside-band count is issued when there is no clean window; no missing-reference,
spare, unread-hazard or below-minimum sentence is invented when its count is zero.

| Pending id | Elements requested (verbatim FILL description) | Physical ledger rows; other disposition |
|---|---|---|
| `P1-ABS-PART1` | one or two sentences summarising Part 1, assembled from the issued outcome fields only: the four reported cells' L1 statement with intervals (CP-X05-*), the dominance branch (CP-X02-abstract / CP-X03-abstract), the decode and prefill contrast outcome words and, only where the claim gate returns L2, the registered direction (CP-X08-*-abstract), and the replication word per contrast (P1-B6-REPWORD-decode, P1-B6-REPWORD-prefill) | 133–168, 530–535, 863–864; needs Block 6 |
| `P1-ID-OS` | operating-system build(s) of the primary-block sessions and of each replication session, from the identity pins and per-session records | a name from a committed file; needs Block 6 |
| `P1-M-RECORD-WIDTH` | median record width and its range in the pre-collection probe sessions, from the registration's instrument description | not a leaf of a registered output |
| `P1-B5-METER` | per pack and model: median, range and interquartile range of the rails' share ρ; member windows outside the hard plausibility band, each listed with its meter flags; within-model spread; the central band from the first clean session and the count of later member windows inside it; or "no clean session, no central band" | 528, 722–784 |
| `P1-M-ACCEPT` | the registered acceptance constants for each block: pre-capture screen, bracket screen and drift limit, from the acceptance files named in the registrations | a name from a committed file; needs Block 6; outside Block 5 (BYTES; sealed) |
| `CP-X01-identity` | model identities and revisions, runtime and library versions, tokenizer and chat-template digests, from the identity pins and prompt pin | a name from a committed file |
| `CP-X01-length` | the selection record that fixed the 2,048-token length, with its digest | a name from a committed file |
| `P1-LEDGER` | per-attempt verdicts (counting or not, with cause family) for every primary, replication and BYTES attempt, from the harvest verdicts and attempt histories | 885–949, 1643–1650; needs Block 6; outside Block 5 (BYTES; sealed) |
| `P1-DEV-LIST` | dated list of every erratum, deviation, interpretation and disclosed repair with applicability and blind status: primary-block SEAL_RECORD.md (two seals, three prospective errata), L9 rulings and addenda including the 2026-10-12 J5 floor-drift correction, docs/analysis/b5/DEVIATION-LOG.md DLE-0 through DLE-10, docs/decision_log.md D-188 through D-190, replication §17 and BYTES addenda | a name from a committed file; needs Block 6; outside Block 5 (BYTES; sealed) |
| `P1-RELEASE` | dates of the primary-block release event, the replication-block release and the BYTES stage-1 commitment and stage-2 release, with the digests each record ties, from the seal-record "Release event" section and the release records | a name from a committed file; needs Block 6; outside Block 5 (BYTES; sealed) |
| `P1-RECOMPUTE` | per block and compared family: applicable bar, number compared, observed largest difference and agreement word; name uncovered quantities and their separate reader checks; Block 5 uses recompute_bars.json fixed blind under DLE-0, Block 6 uses §12.3; checked by one executing reader before printing | 523, 1651–1793; a name from a committed file; needs Block 6 |
| `P1-B5-ATTEMPTS` | attempt history of each primary-block pack: number of attempts, each with its verdict and cause family, and "collected X of Y planned runs"; the three superseded first-seal attempts listed separately as inputs to no number; from the harvest records and analysis-plan disclosure producer | 885–949, 1643–1650; a name from a committed file |
| `P1-B5-ANALYSED` | identifiers and dates of the analysed attempt of each pack | a name from a committed file |
| `P1-B5-RM-1p7B-decode` | removed units | 955–958, 1440–1445, 1794–1795 |
| `P1-B5-RM-1p7B-prefill` | removed units | 985–990, 1446–1454, 1796–1798 |
| `P1-B5-RM-8B-decode` | removed units | 1027–1038, 1472–1489, 1799–1804 |
| `P1-B5-RM-8B-prefill` | removed units | 1071–1080, 1490–1504, 1805–1809 |
| `P1-B5-RM-ctr-decode` | removed quads | 198–201, 1112–1119, 1130–1137, 1810–1825 |
| `P1-B5-RM-ctr-prefill` | removed quads | 202–208, 1120–1129, 1138–1151, 1826–1845 |
| `P1-B5-HAZARDS` | per session: hazard measurements at arm (naming any hazard whose probe returned no reading), counts of each physics-in-span code, battery-assist counts, and the battery-temperature rise per stage, from the disclosure producer | 242–244, 1163–1242, 1291–1370, 1421–1427, 1430–1439, 1455–1471, 1505–1531, 1536–1605 |
| `P1-B5-INTERVAL-PARTS` | per cell: h, B and its three kind averages, and the run attaining the attribution floor with the smallest first-kind bound over kept runs | 136–137, 145–146, 154–155, 163–164, 950–954, 980–984, 1022–1026, 1066–1070 |
| `P1-B5-B-SHARE` | per cell, B ÷ (h + B), derived from the same record | not a leaf of a registered output |
| `P1-B5-BATT-LINE` | per cell: mean and interval over units with no assisted run, with n_r, n_b and the count of assisted runs per stratum; "below the registered minimum of 5 units" where applicable | 959–973, 991–1005, 1039–1053, 1081–1095 |
| `P1-B5-LOAD-LINE` | per cell where any unit was removed by a thermal-pressure or outside-process code: the same estimator with those units restored, with n_r and n_b; or "no such removal" | 647–651, 979, 1011–1021, 1059–1065, 1101–1111 |
| `F_1p7B_decode_cmp_J` | comparative operative floor | 550 |
| `P1-B5-FN-1p7B-decode` | n of each form | 543, 548 |
| `F_1p7B_prefill_p2048_cmp_J` | comparative | 566 |
| `P1-B5-FN-1p7B-prefill` | n | 559, 564 |
| `F_8B_decode_cmp_J` | comparative | 582 |
| `P1-B5-FN-8B-decode` | n | 575, 580 |
| `F_8B_prefill_p2048_cmp_J` | comparative | 598 |
| `P1-B5-FN-8B-prefill` | n | 591, 596 |
| `R_1p7B_decode_abs` | ratio | 540 |
| `R_1p7B_decode_cmp` | ratio | 545 |
| `TERM_A_1p7B_decode_abs_J` | point | 542 |
| `TERM_A_1p7B_decode_cmp_J` | point | 547 |
| `TERM_B_1p7B_decode_abs_J` | corner | 541 |
| `TERM_B_1p7B_decode_cmp_J` | corner | 546 |
| `R_1p7B_prefill_p2048_abs` | ratio | 556 |
| `R_1p7B_prefill_p2048_cmp` | ratio | 561 |
| `TERM_A_1p7B_prefill_p2048_abs_J` | point | 558 |
| `TERM_A_1p7B_prefill_p2048_cmp_J` | point | 563 |
| `TERM_B_1p7B_prefill_p2048_abs_J` | corner | 557 |
| `TERM_B_1p7B_prefill_p2048_cmp_J` | corner | 562 |
| `R_8B_decode_abs` | ratio | 572 |
| `R_8B_decode_cmp` | ratio | 577 |
| `TERM_A_8B_decode_abs_J` | point | 574 |
| `TERM_A_8B_decode_cmp_J` | point | 579 |
| `TERM_B_8B_decode_abs_J` | corner | 573 |
| `TERM_B_8B_decode_cmp_J` | corner | 578 |
| `R_8B_prefill_p2048_abs` | ratio | 588 |
| `R_8B_prefill_p2048_cmp` | ratio | 593 |
| `TERM_A_8B_prefill_p2048_abs_J` | point | 590 |
| `TERM_A_8B_prefill_p2048_cmp_J` | point | 595 |
| `TERM_B_8B_prefill_p2048_abs_J` | corner | 589 |
| `TERM_B_8B_prefill_p2048_cmp_J` | corner | 594 |
| `P1-B5-DOM-FAILED` | list of each ratio below 2, with model, phase, form, value, numerator and denominator | 540–606, 803–864, 1846 |
| `P1-B5-DOM-REFUSED` | component and refusal code | 803–862; not a leaf of a registered output |
| `P1-B5-XWIN` | per model and phase: "agree within their within-session intervals (difference Δ J)" or "differ by Δ J, more than their within-session intervals cover; the reported intervals understate between-session variation, which includes different interleaving and thermal history" | 974–978, 1006–1010, 1054–1058, 1096–1100 |
| `P1-B5-NEG8` | per session: drift-screen verdict on both energy families, the corpus size the deciding bound rested on and the corpus runs left out by reason, realised reference counts against the planned (3, 1, 3), each lost reference, each spare used, any lost midpoint with its fixed sentence, and the allowance; the bound's two terms printed with the other energies | 1255–1287, 1383–1420, 1428–1429, 1532–1535, 1606–1642 |
| `P1-B5-MONITOR` | per session: monitor and meter-reader CPU time, and the number of monitor probes that fell inside target phases | 348–350, 1160–1162, 1288–1290 |
| `P1-RECOMPUTE-SUMMARY` | one paragraph per block: compared families and counts, largest differences against that block's applicable bars (Block 5 recompute_bars.json fixed blind under DLE-0; Block 6 §12.3), uncovered quantities and separate reader checks; any disclosed repair with its date and effect | 523, 1651–1793; a name from a committed file; needs Block 6 |
| `CP-X02-conclusion` | under branch A: "On this stack, timing attribution, not repeatability, limits phase-energy measurement: allowing each value to move within its registered timing uncertainty at least doubled every detection floor." Under branch B: "Timing attribution at least doubled the detection floor for some components and not others (the failing components named), so neither timing nor repeatability alone limits these measurements." | 843–864, 1846 |
| `CP-X08-decode-a-conclusion` | one sentence per contrast in the registered wording for its outcome and claim level (Section 6.5 branch), with the replication word (Section 6.8) | 530–535; needs Block 6 |
| `P1-AVAIL` | public release: repository revision, archive locator and SHA-256 manifest of registrations, sealed inventories, flag catalogs, analysis and recomputation code, harvest records, released energies and figure sources; primary-block custody locator, dry-run record digest, released bundle SHA256SUMS and release-event binding; which raw captures are and are not released; locators must be supplied by the authorized release record, never inferred | a name from a committed file; needs Block 6; not a leaf of a registered output; outside Block 5 (BYTES; sealed) |

The [coverage checker](fill_coverage_b5.py) reproduces the explicit element map
from repository files, rejects missing/new Block 5 placeholders and
nonprintable row references, and requires byte-identical machine output.
Historical checkers are scoped to their frozen physical row prefixes, so
later appends do not invalidate their replay. This preserves what each older
review checked; it does not confer that review on the new rows.

`fill_check_b5.py` pins the final full ledger hash and independently preserves
the header plus original 538 rows from `0b8763f0a`. `--paper-ref` can explicitly
check a local Git snapshot. `--repo-only` checks the ledger/branch arithmetic
without checking a paper. Both fill checkers now pass in their default modes
against the merged working-tree paper.

## Round 5 — five-decimal R_cm and delta fixes

[hand_check_rl55_round5.py](hand_check_rl55_round5.py) opens only the pinned
RC file. Its independent stdlib arithmetic reconstructs eight kept prefill
quad differences and local widths from ALPHA member leaves, takes the pinned
shared widths as inputs, and enumerates all 512 shared/local sign corners.
The point floor uses the registered df=7 Student multiplier 2.365. The replayed
numerator, denominator and ratio agree with RC's full-precision terms and
`R_cm` leaf; a separate Decimal division checks those terms too. No raw
trace or embedded source path is followed. Only aggregate values at ledger
precision are serialized.

The sole append is physical row **1846**:
`RC.dominance.common_mode[Qwen3-1.7B-4bit/prefill].R_cm`, printed and
re-derived **1.99975**, `within-rounding`, residual **-1.7e-06** (two
significant figures, RL-42). Prior rows are immutable. CP-X02-conclusion and
P1-B5-DOM-FAILED cite this row for the fuller precision. The ratio remains
below 2 and branch B is unchanged.

Current ledger: **1,845 rows** = **1,101 exact**, **581 within-rounding**,
**128 recorded-judgment**, **34 single-source**, **1 MISMATCH**. The sole
MISMATCH remains physical row 249, the ruled RL-39 wording erratum.
No new MISMATCH or `source-outside-unseal` row arose. The full ledger SHA-256
is `41b7e577a7be494245ed42ba38190da9de860430a75f5dc6d0987a15de79060f`.
