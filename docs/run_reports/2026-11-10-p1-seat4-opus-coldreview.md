# Paper 1 seat 4 phase 2: Opus cold review of the hand checks

2026-11-10 23:49 PST · Opus 5.5 cold reviewer (RL-38 condition 9) · branch
`analysis/2026-11-10-b5-rederivation` @ `73160e893`. Authority: RL-3, RL-38 and RL-39, read verbatim from
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
Not a repair seat. `RESULTS.md`, the analysis code, the seat's ledger files and custody are unchanged. This
review adds this report and one data-free check script,
[`docs/analysis/b5/opus_coldreview_check.py`](../analysis/b5/opus_coldreview_check.py).

**Verdict: the 157 hand checks are confirmed. None is refuted.** The seat's script is independent of the
repository pipeline. The committed record holds no member-level value at recordable precision (one minor
observation below). MISMATCH 1 is real and correctly classified. **MISMATCH 2 is not a real disagreement:**
`RESULTS.md`'s "84 leaves" counts normalized leaf paths, the seat's 118 counts scalar leaf instances, and the
same groups give exactly 84 paths. Of the 31 held rows, 24 are held correctly and 7 can be released or
re-ruled (table below). RL-3's gate is a lead ruling. This review supplies the condition-9 check it needs.

## 1. Hand checks, redone independently

I wrote my own stdlib code before reading the seat's arithmetic. I used the registered text, not the seat's
formula column, as the definition: analysis plan §4 (steps 1-7), §5, §7.1, §7.3, §8.1 and §8.2. The code has
its own Student t: a closed-form integer-df CDF in 80-digit `Decimal`, with quantiles found by bisection. The
seat used an incomplete-beta power series. My quantiles reproduce the plan's pinned values
(t(0.975, 9) = 2.262157162798205, …). The inputs are member-level values from `RC.members.*` and
`RC.disclosures.whole_machine.windows.*.members`, plus these stored structural inputs: kept-unit lists, the
GAMMA kept quads (checked against `EXC.cells[*].dropped_units`, identical), window NEG-8 allowances, and the
comparative-floor `shared_j` trace-sweep widths. The `shared_j` widths cannot be derived from member scalars.

| Group (ledger rows) | Rows | Result |
|---|---:|---|
| Primary contrasts: d̄, s_d, se, df, t*, metrology interval, both repeats (15-39) | 24 | all agree |
| D, clock, drift, decision interval (40-51) | 10 | all agree |
| Raw p, Holm-adjusted p (58-61) | 4 | all agree (6.0165e-16, 1.7404e-11, 1.2033e-15, 1.7404e-11) |
| LOO min/max, per-quad d_k (63-81) | 15 | all agree |
| Geometric ratio and interval, per-token values (114-131) | 16 | all agree |
| Four reported cells, mean/interval/h/B/attribution/n/per-token (133-168) | 36 | all agree |
| Cross-window deltas (169-172) | 4 | all agree |
| Contention counts 4/14/10 (242-244, 490-492) | 6 | all agree; GAMMA also 10 from `EXC.members_excluded` |
| Floors: minted, guarded, R_cm (53-57, 276-279, 288-293, 502) | 13 | all agree |
| Request rail shares, median/min/max (351-357, 496, 521) | 9 | all agree; 0 of 103 outside the hard band |
| Whole-machine phase means, h, shares (360-374, 497-498) | 12 | all agree |
| Load-correlated sensitivity (376-384) | 8 | all agree; restored b01,b05 (decode), b04,b06,b10 (prefill) |
| **Total** | **157** | **157 confirmed (24 exact, 133 within-rounding), 0 refuted** |

The exact/within-rounding split matches the seat's 24/133. I checked more than the seat at three points:

- I rebuilt the absolute-floor widths from member `a_bop_j` and the comparative local widths from member
  `r_j` (half the sum of four). Both equal the stored `widths_j`/`local_j` exactly (max difference 0.0). The
  seat used the stored widths directly.
- Over every member of all three windows, the recompute's member energies `E_j` equal the stored (harvest)
  `stored_E_j` to 2.3e-13 J. So the hand checks do not depend on which member source is read.
- The four stage-opening causes, from `EXC.cells[*].dropped_units` b01/b06, are contention (decode b01), anchor
  failure (decode b06), admission abort (prefill b01) and contention (prefill b06).

## 2. Independence of the seat's script

`docs/analysis/b5/hand_check_phase2.py` imports only the standard library (`argparse csv collections decimal
hashlib io itertools json math pathlib re stat statistics subprocess`). It imports nothing from `joulewise`,
`scripts/` or the recompute or comparator. Its one `subprocess` call is `git show <base>:docs/analysis/b5/rederivation.tsv`
(ledger text, not code). Its custody reader allow-lists the two roots by lexical check, refuses symlinks, hashes
before parsing, and re-hashes at `finish()`. Its arithmetic (`hand_calculations`) reads only RC member fields
plus the named stored inputs listed in §1; it never copies a stored aggregate in as a "re-derived" value. Its
formulas match the registration. Two of its choices differ from mine without consequence: it rounds the df 4-6
cell quantiles to the nine places the plan prints, and its R_cm numerator starts from the base point floor. **It is
independent.** Its 12 synthetic unit tests pass (`python3.13 -B -m unittest tests.b5_analysis.test_hand_check_phase2`, 0.006 s).

## 3. No member-level values in the committed record (condition 4)

I collected all 24,891 non-integer member- or quad-level numeric leaves from RC, DISC, FILL, CV and EXC: member
records, whole-machine member records, and every numeric list of five or more entries. I then scanned the seven
committed phase-2 files for them: `rederivation.tsv`, `hand_checks_phase2.tsv`, `phase2_sources.tsv`,
`REDERIVATION.md`, the seat report, `hand_check_phase2.py` and its test.

- **At 8 significant digits: 0 matches.**
- At printed precision, the matches are of three kinds:
  - the per-quad d_k, which `RESULTS.md` prints by design;
  - registered extreme statistics, which are one member's value by definition: the attribution floors (the
    largest member clock bound) and ρ minimum/maximum;
  - coincidental 4-digit roundings among about 25k values (for example 6.574 and 2.678 also round from two
    BETA member durations).
- No member arrays, battery-temperature stage readings or monitor values are committed. **Condition 4 holds.**

*Minor observation.* On the eight extreme-statistic rows (attribution floor ×4, ρ min/max ×4), the record gives
the printed value plus a full-precision `difference`. Together they recover that one member's value to about 15
digits. Condition 4 explicitly asks for the difference, so this is compliant. If the lead wants it tighter,
those eight residuals could be rounded to one significant figure.

## 4. The two MISMATCHes and the 31 held rows

**MISMATCH 1 (row 249, "four different causes"): real, correctly classified.** As §1 shows, the record gives
four losses with three distinct causes. This is the RL-39 erratum, and it is now sourced from indexed EXC. The
committed attempt index hashes to REC's `window_index_sha256` (`51b03914…`), which I checked.

**MISMATCH 2 (row 522, 84 vs 118): not real. Reclassify as `exact` with a units note.** I counted every
scalar leaf in exactly the seat's three groups:

- `FILL.gamma.contrasts[*].floor.point_floor_diagnostics`
- `.floor.resolutions[*].point_floor_diagnostics`
- `.claim_evaluation.floor_limit`

That gives **118 instances**. Collapsing list indices to `*`, as the comparator does, gives **84 distinct
normalized paths**:

- 44 under `claim_evaluation.floor_limit`: class, source, published floor, 11 discipline words, and 6 cell/form
  diagnostics of 5 leaves each;
- 30 floor diagnostics: 6 cell/form pairs × 5;
- 10 resolution diagnostics: 2 forms × 5.

That is DLE-5's `14 + 10C + 5R` with C = 6 and R = 2. DLE-5's source line records an observed comparator
refusal "with 84 unmapped leaves". `docs/analysis/b5/reviews/sol-review-704.md` §5 states the formula counts
"normalized path names … Lists collapse to `*`". So `RESULTS.md` §4.1's 84 is the comparator's
unit and is correct in that unit. The seat's "can reach 84" reading missed the observed refusal count. The
most the lead might add is an optional erratum-style clarification: "84 normalized leaf paths (118 scalar
leaves)". No numeric or factual disagreement remains.

**The 31 `source-outside-unseal` rows.** I re-read each against the two roots.

| Rows | Reason | My view |
|---|---|---|
| 236-241 (3.3, 4.3, T_b/T_a values) | D | **Correct.** GAMMA phase durations are absent. GAMMA whole-machine members carry only `request`; RC members carry edge-record durations, not phase durations. |
| 341 (assist quads 0) | B | **Correct.** Corroborating evidence: 0 of 44 kept GAMMA members show meter `battery_activity.active`, and the battery ΔE is 0. But that is a different signal from the registered `battery.assist` (LEAN-COVERAGE row 57). |
| 342 (arm amperage 0) | H | Correct. It is an arm receipt; only the DISC copy is in the roots. |
| 348-350 (monitor cost) | M | Correct. |
| 362, 367 (edge-shift 9.07, 12.17) | E | Correct. Only aggregate shifted corners are present, not member shifted energies. |
| **388, 389, 390 (decode scaled D 9.345, decision [137.095, 156.164])** | S | **Over-conservative: hand-checked here, agree.** The factor is max(1, E/E_ref, T/T_ref). E_b/E_ref = 5.377, using member request energies for E_ref. A member's request duration bounds its decode phase from above, so T_b/T_ref ≤ 5.182 < 5.377. Side a is ≤ 1.59. So the factor is the E term, and the numbers follow. |
| **391 (decode scaled floor gate 15.228)** | S | **Over-conservative: hand-checked here, agree.** ALPHA/BETA meter-side phase durations are in the roots (`RC.disclosures.whole_machine.windows.{ALPHA,BETA}.members[*].phases.*.duration_s`; they match the stored cell T to about 1e-11 s on BETA decode). BETA's factor is the E term (5.343 vs T 5.026) and sets the gate. |
| **395 (prefill scaled floor gate 11.685)** | S | **Over-conservative: hand-checked here, agree.** BETA factor is the E term (3.455 vs T 2.046); ALPHA's factor is 1. |
| 392-394 (prefill scaled D 8.045, decision [93.395, 110.224]) | S | **Correct.** The arithmetic agrees, but T_b/T_ref can only be bounded by 7.51 > 3.478, so the factor cannot be established. |
| 525, 526 (top-up, replacements none) | I | Correct. This is the selection family (LEAN-COVERAGE §2 family 7). |
| 528 (clean windows 0) | C | **Inconsistent with rows 242-244.** At the stored-flag standard the seat used to pass the contention counts, this follows: all 3 windows carry a window-level `meter.pdtr_gain_out_of_band`, so 0 are clean. Either pass both at that standard or hold both. |
| 529 (bracket sensitivity "clean") | T | **Over-conservative.** `sensitivity_bound` is recomputed and compared: 189 sensitivity comparator rows, all AGREE, including `outcome_equals_primary` (LEAN-COVERAGE row 66). It is not one of the seven families, nor an exempt leaf, nor recompute-only. So RL-3 item 3 does not apply, and the exact source match should suffice. |
| 530, 531, 533, 534 (outcome, direction) | I | **Defensible; lead's call.** The comparator compares these (`outcome_word`, AGREE). Every numeric precedence condition holds in my arithmetic: \|d̄\| > floor gate, both intervals exclude 0, Holm rejects, LOO keeps sign and floor. But LEAN-COVERAGE row 44 and family 7 mark the not-estimable reason-code prerequisites as partly uncovered. |
| 532, 535 (ceiling L2) | I | Correct to hold with 525/526. L2 needs confirmatory status, which needs the top-up absence. |

Net: 24 rows are held correctly, counting 530/531/533/534 as defensible. Seven can be released:

- 388-391 and 395 (5 rows) are hand-checked here and agree at printed precision;
- 528 can pass at the stored-flag standard already used for rows 242-244;
- 529 is outside RL-3 item 3 because the comparator covers it.

If the lead accepts the S-row bounding argument, the outside list drops from 31 to 26. With 528 and 529 as
well, it drops to 24.

## 5. Custody files opened, with hashes

All 12 were hashed with `shasum -a 256` before any read. The six I parsed were hashed again by
`opus_coldreview_check.py` before parsing. All 12 were re-hashed at the end (2026-11-11T07:49Z), unchanged.
Every full §0 pin matches. PROJ-A/B match their §0 prefixes and their content-addressed names. VER has no §0
pin; it matches the seat's recorded hash. Nothing was written in custody, and no path named inside a file was
followed. Scratch lived in this session's scratchpad outside custody and was deleted.

| Alias | Path | SHA-256 (before = after) | Use |
|---|---|---|---|
| REC | `dry-m/dry-run/B5-BLIND-DRY-RUN-RECORD.json` | `66adc66e89f1a621009dd2ca98bc7c41b202d5c43a26a82af8a633a54c34aa03` | parsed: `window_index_sha256` |
| FILL | `dry-m/dry-run/restricted/outputs/a29c6cf2…-results-fill-input.json` | `a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4` | parsed: DLE-5 leaf census |
| CV | `dry-m/dry-run/restricted/outputs/67d8c231…-claim-verdicts.json` | `67d8c231eeb5df2e1240cd3d0b965555ab39755042a2b9676f939f1543716f27` | parsed: token provenance, sampling audit |
| EXC | `dry-m/dry-run/restricted/finalized/analysed-attempt-exclusions-a9954365….json` | `a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46` | parsed: dropped units, codes |
| DISC | `dry-m/dry-run/restricted/disclosures/77be1a3e….json` | `77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a` | parsed: leak-scan inventory only |
| SENS | `dry-m/dry-run/restricted/outputs/4a7c4315….json` | `4a7c4315327d29b214e79961d6f991af13dcabc24898368564007ac2e356ff28` | parsed: row 529 |
| STEP | `dry-m/dry-run/restricted/outputs/b0f80f72….json` | `b0f80f7265cf84203ded237245ae25cf87adfd987c2265a92b52c96efb1ea5b5` | parsed: stored verdicts |
| PROJ-A | `dry-m/dry-run/restricted/outputs/ed3cadb1…-projection-alpha.json` | `ed3cadb1f0ac2fc137efab3f4528702c704055ffa5bdf24399c335081570f5bf` | hashed only |
| PROJ-B | `dry-m/dry-run/restricted/outputs/db6d5251…-projection-beta.json` | `db6d525129f90ef24bb46f83ab5e66283424970c743f35d322c8961f9b683e2e` | hashed only |
| RC | `release-check-final-20261108T0942Z/recompute.json` | `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc` | parsed: member inputs |
| CMP | `release-check-final-20261108T0942Z/comparison.json` | `b12b7e1b32b27159be894221dcde7e334784061314fe91a39166faa36f72f4c9` | parsed: coverage rows |
| VER | `release-check-final-20261108T0942Z/verdict.json` | `c73593f397ceaa72fee4fca27b2fad77e00b74c5666b918bed8c6e025f91c9b6` | parsed: uncovered count |

Directory listings: none beyond the paths above. Paths are relative to `/Users/edr/jw-b5-custody`.

## 6. Reproduce

`python3 -I -B docs/analysis/b5/opus_coldreview_check.py` takes under 1 s. It prints counts, verdicts, the
S-row bounding ratios, the DLE-5 instance/path counts and the before = after hashes. It prints no member value.
It reads printed values and keys from `hand_checks_phase2.tsv` and ignores the seat's re-derived column.

## 7. For the lead

1. Rule row 522: `exact` in normalized-path units, or an optional clarification line in the errata.
2. Decide whether the request-duration bound and the ALPHA/BETA meter-side phase durations are acceptable
   inputs for rows 388-391 and 395.
3. Make rows 528 and 242-244 consistent.
4. Take row 529 off the RL-3 item 3 list.
5. The lead's own RL-38 condition-8 event-log audit of the Sol seat is still owed. This review does not
   discharge it.

Blind status: Block-5-aware (RL-38 condition 10). This seat is not to be used later as a Block-5-naive seat.
