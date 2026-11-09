# ALIGN v4 release runbook

**Authority.**
- RUN_STATE 230 (R21, A0-A36), 233 (A37) and 234 (R22-4: the Block 5 comparator rules R-C1 to R-C6, and the
  R22-3 balance check).
- The B5 precedent: `docs/analysis/b5/RELEASE-RUNBOOK-lean.md`, `DEVIATION-LOG.md` DLE-1/DLE-2 and the lessons in
  `docs/analysis/b5/RESULTS.md` §4.3 and `docs/analysis/b5/LESSONS-FOR-V4-V5.md` §5 (`analysis/2026-11-08-b5-results`,
  `analysis/2026-11-08-b5-lessons`).

**Programs.**
- `scripts/release_v4.py` runs stages (a)-(c).
- `scripts/compare_v4_recompute.py` is the blinded comparator.
- `configs/analysis/v4/recompute_bars.json` holds the bars, pinned by SHA-256 in `release_v4.py`
  (`RELEASE_BARS_SHA256`). Any other bytes refuse `release_bars_differ`.
- Tests: `tests/v4_release/`. All of them are synthetic.

**Builds compared** (pinned in `release_v4.py`: `RELEASE_ENGINE_COMMIT`, `RELEASE_RECOMPUTE_COMMIT`,
`RECOMPUTE_PROGRAM_SHA256`; any other commit refuses).

| Build | Branch | Commit | Output |
|---|---|---|---|
| Sol primary engine | `engine-r23k` (R21 + A37 + R23-R26 + R23h-j + R23k seeds/roster names + R23l config custody) | `72410b0b4` | `fill.json`, `verdict.json`, `thresholds.json` |
| Opus independent recompute | `align/2026-11-08-v4-recompute-opus` | `7b06c6058` (program sha256 `f4a06738…`) | one JSON (`RECOMPUTE-opus.md`) |

History: the first rehearsal (engine `8eb7982f0` vs recompute `c0d1efcae`) held on five families and found
engine bug E1. Lead rulings R23 (with R23b-h), R26 (H*) and the A21/P1/P2/A2(4)/A27 rulings of 2026-11-08
resolved every hold; each round re-ran the full rehearsal and the probe plan. The two release reviews of
`99875485d` (Sol seats 1 and 2: F1-F7) were folded in on 2026-11-08 with engine-r23i/r23j; their witness
modules are kept INVERTED in `tests/v4_release/test_review_sol{1,2}.py` (green = defect fixed).

Like B5, the verdict carries only agree or hold per family, with pass and fail counts, structure codes and
counts. It never carries an energy, a difference or an outcome word. Unsealing is a separate step and needs
Ed's OK.

## 0. Inputs

| Name | What it is |
|---|---|
| `ENGINE_INPUT` | The engine's input manifest (`joulewise.align_v4.analysis_input.v1`, raw-source form). Its sources resolve beside it. |
| `ENGINE_OUT` | The engine's FULL run folder: `fill.json`, `verdict.json`, `thresholds.json`, produced against the prospective freeze. |
| `ENGINE_RECORD` | `joulewise.v4_engine_run_record.v1`: `engine_commit`, and the sha256 of the input, fill, verdict and thresholds. The magistrate writes it when the engine run completes. |
| `RECOMPUTE_ROOT` | The series in the recompute's layout (`RECOMPUTE-opus.md`, "Input layout"). Its raw plists are the SAME bytes the engine manifest names. |
| `CROSSWALK` | `joulewise.v4_release.crosswalk.v1`: the structure-only map from the engine's (attempt, ordinal, run id) to the recompute's (window id, run id). The exporter writes it from the roster, before any data. |
| `OUT` | A new restricted folder. It is created with mode 0700 and refused if it exists. |

The release checkout must be clean (`release_checkout_not_clean`). `--programs-repo` is any git repository
holding both pinned commits; it defaults to the checkout. The recompute program is extracted with
`git show <commit>:scripts/independent_recompute_v4.py`, and its sha256 must equal `RECOMPUTE_PROGRAM_SHA256`.

```bash
python3.13 -B scripts/release_v4.py --engine-input "$ENGINE_INPUT" --engine-out "$ENGINE_OUT" \
    --engine-record "$ENGINE_RECORD" --recompute-root "$RECOMPUTE_ROOT" --crosswalk "$CROSSWALK" \
    --restricted-out "$OUT" --workers 4
echo "exit=$?"
```

The command passes no commit flags: `--engine-commit` and `--recompute-commit` default to the pins
(`RELEASE_ENGINE_COMMIT`, `RELEASE_RECOMPUTE_COMMIT`), and any other value refuses. Run it with the same
`python3.13` that ran the engine (CPython 3.13.x is REQUIRED: engine-r23j's runtime calibration identity
check refuses `calibration_identity_drift` under any other version, and release_v4 refuses
`release_python_not_3_13`): stage (a) recomputes the engine's producer identity (its loaded scorer
code depends on the Python version) from the pinned engine tree under this interpreter (`--python`).
`test_release_v4.test_runbook_command_matches_pins` keeps this block in step with the pins.

## 1. Stages

**(a) Digests.** In order, stage (a) checks:
- the checkout is clean, and the bars hash to the pin;
- both commits are 40 hex digits and exist;
- the engine record names the pinned engine commit and the input;
- fill, verdict and thresholds hash to the record;
- the engine verdict is not `refused`;
- every series- and window-level engine source (`series_source`, `raw_source`, `thermal_source`,
  `residual_source`, `terminal_result_source`) is an `input_census` row (else `engine_census_incomplete`);
  every census row re-hashes at the engine input root, and so does EVERY `{path, sha256}` reference inside
  each raw-source manifest's member rows (episode, powermetrics, a referenced thermal `journal`, DC streams,
  any other); a malformed row or reference refuses `engine_census_malformed`;
- the engine's printed producer identity (`loaded_scorer_sha256`, `raw_reducer_sha256`, in the fill's
  `threshold_freeze` and in `thresholds.json`) equals the identity computed from the PINNED engine tree under
  the release interpreter (`git archive` of `joulewise/`, the engine's own `scorer_identity()` and
  `producer_sha256()` in a subprocess); else `engine_producer_identity_differs`. The identity is passed to
  the comparator (`--engine-identity`, family `producer_identity`, refusing);
- the crosswalk equals the engine roster as (attempt, run id, ordinal) and every recompute `window.json` as
  (window id, run id, ordinal);
- the recompute program hashes to its pin.

Files are opened non-blocking. A symbolic link, traversal or special file refuses.

**(b) Recompute.** The A25 two-stage contract runs: first `--stage calibration --freeze-out`, then the full
run with `--freeze-in`. After it, every captured member's raw sha256 in the recompute output must equal the
engine manifest's `powermetrics` digest for the same member. Otherwise it refuses `builds_read_different_bytes`.

**(c) Comparator**, with the pinned bars and the crosswalk.

## 2. Reading the result

| Exit | `verdict` | `reason` | Meaning | Next step |
|---|---|---|---|---|
| 0 | `agree` | null | (a) verified; recompute exited 0 twice; every recomputed family agrees or is expected-empty with its predicate satisfied; 0 unmapped; every manifest count is in range | Ask Ed for the unseal OK |
| 1 | `hold` | `comparator_disagreement` | A family failed, an empty family is unexplained, a manifest count is out of range, or a sensitivity line is uncomputable | Trace blind and structure-only from `$OUT/comparison.json`; classify each failing row as an open interpretation (name the R21 row) or a bug in one build |
| 2 | `refused` | `comparator_refused` | The comparator refused: an unmapped leaf, an `eligible_m_per_pair` mismatch (R-C5), malformed input, or an engine refusal | Tooling or coverage defect |
| 2 | `refused` | `release_digest_differs_from_record`, `engine_census_malformed`, `engine_census_incomplete`, `engine_producer_identity_differs`, `engine_identity_unavailable`, `release_python_not_3_13`, `release_input_malformed` (any other malformed nested shape: never an uncaught exit 1), `engine_run_refused`, `crosswalk_differs_from_roster`, `builds_read_different_bytes`, `recompute_program_differs`, `pinned_commit_*`, `release_bars_differ`, `release_checkout_not_clean`, `restricted_out_exists`, `recompute_failed`, `comparison_output_unreadable`, `comparison_vacuous`, `verdict_not_structure_only` | Custody, binding or tooling | Fix it, then re-run into a new `$OUT` |

Precedence is refused 2 > hold 1 > agree 0. The final guard replaces any verdict whose text contains a decimal
or exponent number with `verdict_not_structure_only`. The comparator's public line reads "N families compared,
E expected-empty, U unexplained-empty", never "agree across N".

**What stays restricted, in `$OUT`:**
- `calibration.json`, `freeze.json` and `recompute.json`;
- `comparison.json`, which holds every row with values, differences and bars, the unmapped list, the coverage
  map and the R22-3 balance table;
- the stage `*.stdout` and `*.stderr`;
- `refusal-location.txt`.

## 3. Coverage: the B5 lessons, built in

In B5, "agree across 24 families" was 23 families that compared something: `window_edge_s` compared 0 rows.
Seven registered families were never recomputed, and 403 leaves sat under named exemptions. The v4 comparator
closes those holes as follows.

- **Every leaf is accounted for.** Each leaf of the engine's fill and verdict is either consumed by a compared
  row or named by an explicit exemption. The exemption names a bars family whose classification is `exempt` or
  `integrity_only`, with a ruling or reason. Anything else is UNMAPPED and refuses (exit 2). On the synthetic
  series that is 282,691 engine leaves, 0 unmapped. The engine's own `leaf_inventory` must equal the
  comparator's walk.
- **R-C1, empty means hold.** A recomputed family with 0 rows holds (`hold_empty`) unless the bars declare
  `expected_empty` and its structural predicate holds. The predicates are:
  - `no_escalated_window`;
  - `calibration_not_complete`;
  - `no_w1_window`;
  - `no_captured_t_sabotage_or_calibration_incomplete`;
  - `no_zero_capture_attempt`.
- **R-C2, row-count manifest.** `row_manifest()` derives the expected unit counts blind, from the crosswalk and
  the recompute's structural booleans (exclusion, barred window, sealed record). It covers:
  - member eligibility, the ledger and pool entry;
  - energies and scores, with a lower bound of expected minus declared exclusions;
  - turn counts and sealed presence;
  - thresholds, tests, U6, carriers and supplemental sentinels;
  - sealed and benign DC.

  A count out of range gives `hold_row_count`.
- **Row completeness (release reviews F2 and the confirmation seat; lead rulings 2026-11-08).** The REFUSING
  family `row_completeness` derives every expected row set independently of the engine's print (crosswalk,
  registered constants, recompute structure); a missing or extra row refuses even when both sides omit it:

  | Table | Expected set |
  |---|---|
  | `windows`, `ledger` | every C/T attempt of the crosswalk |
  | `windows[*].eligibility` | the attempt's roster members |
  | `windows[*].checks`, `acceptance` | every window; both models when the attempt/window captured anything |
  | `windows[*].supplemental_sentinels` | the attempt's ordinals > 22 |
  | `fits`, scored rows | every (window, pair, convention) and member the recompute scored |
  | logged rows' `council_grid` / `H_grid` | the registered council grid / council U H* grid with "full" |
  | `H_star` | EVERY C benign carrier and T sabotage row, on BOTH sides (null/undefined blocks included; R26 and its amendment) |
  | T sabotage `known_H_first_k` | k = 0..n turns, on both sides |
  | `turn_residuals_j`, DC `turn_rows` | the member's recomputed turn count |
  | `U3.pairs` (both locations) | the recompute's replay pairs (A13) |
  | `U4.per_window` | one row per window with a captured counted attempt (W1 included); W >= 3 rows need the statistic, df, both CI ends and W window means; skipped rows their reason (A14) |
  | `U6` | both pairs; each pair's turn positions in `means_j`, `trajectory_counts`, `evaluable` (A16) |
  | `benign_carriers` | both pairs; every curve and `n_by_h` dose = council U H* |
  | `realized_counts`, `cache_diagnostics` | every C/T roster member of every attempt |
  | `residual_by_hold_count` | one trajectory per scored row of the convention |
  | `test` | conventions x pairs x conditions; T windows in `by_window`; the planned T assignments in `members` |
  | `thresholds`, `threshold_freeze.thresholds` | conventions x pairs |
  | `U5.designed_states` | the recompute's designed-state count |
  | `W1.contrast.same_arm_pairs` | X-G, X-S, Y-G, Y-S; common absence when the roster is insufficient (F3) |

  Fixed elsewhere: `dc_secondary` rows (R-C2 manifest `dc_sealed`/`dc_benign_status`, `hold_row_count`),
  `supplemental_sentinels` and the other R-C2 manifest families (hold), the U1/U2/U3-bar/U5/thresholds field
  sets (named fields, a missing one fails its row), fit coefficients (`BETA_ORDER`), R-C4 sensitivity lines
  and R22-3 balance.
- **R-C3, every family is classified.** Each family is `recomputed`, `integrity_only` or `exempt`.
  `comparison.json` carries a `coverage_map` from each normalized engine pointer to its family. A renderer must
  refuse to print an `integrity_only` or `exempt` leaf without a hand-check receipt bound to its pointer
  (item 83, ruling 3).
- **R-C4, sensitivity lines.** The `sensitivity_lines` family requires each registered line to compute on both
  sides:
  - the U5 descriptive;
  - the withheld convention;
  - LOTO and full-fit scores;
  - the R20 supplemental sentinels;
  - the DC battery-assist disclosure;
  - the benign DC residual.

  The synthetic fixture exercises each hard case: a 24-member window, T sabotage on the full fit, and DC
  streams.
- **R-C5, eligibility.** Eligibility is compared member by member: eligible, class sets, re-derived and
  recorded classes, pool eligibility and flags. The recompute re-derives them from raw journals.
  `eligible_m_per_pair` is a REFUSING family.
- **R-C6, bars matched to scale.** The CP bound, the marginal FPR bound and the iid tolerance bound use
  log10-relative bars. Thresholds are compared exactly by rank, m, calibrator set and the member at the rank;
  their value is also compared at the score bar.
- **R22-3, balance.** `balance_by_condition` compares exclusion and flag counts by condition, by pair and by
  cell. The per-member-second rates and exposure-adjusted expectations go only to the restricted
  `balance` table.
- **Sealed sabotage DC rows are compared by presence only** (`dc_sealed`). So are members whose turns the
  recompute seals (`sealed_presence`).
- **Monte-Carlo leaves are compared exactly.** The window bootstrap intervals, undefined-replicate counts,
  seed and replicate count must match, because both builds run the fixed recipe (A8: `Random(0)`, `choices`
  over sorted window ids, 1000 replicates).

## 4. Families and bars

There are 64 recomputed families and 21 that are not recomputed. Each family's reason is in
`recompute_bars.json`. Per-row overrides are fixed in the program: margin_relative 1e-9 rel, E_ref 1e-9 rel,
carrier fractions 1e-12 rel, T member scores 1e-6 abs.

| Bar | Families |
|---|---|
| rel 1e-9 | `turn_owned_energy_j`, `gross_episode_energy_j`, `predictions_j`, `u3_energy_j`, `supplemental_sentinels` |
| abs 1e-6 J | `residuals_j`, `turn_residuals_j`, `u6_values`, `residual_by_hold_count` |
| abs 1e-6 (score) | `scores`, `known_h_scores`, `thresholds_value` |
| exact (R26) | `h_star` (H*_i on C benign carriers and T sabotage: grid, h_star, bounded_above, missing and off-grid lists, status) |
| rel 1e-6 | `fit_coefficients`, `fit_rss`, `prediction_sd_j`, `u3_bar_values`, `u5_values`, `w1_contrast`, `anchor_sigma_w` (IR §5) |
| abs 1e-9 | `u2_values` (°C), `u3_values`, `u4_values` (fractions) |
| log10-rel 1e-6 | `threshold_bounds`, `test_bounds` |
| rel 1e-12 | `test_rates` |
| rel 1e-3 | `dc_benign` (A20, print-only) |
| exact / set | `verdict_structure`, `ledger`, `calibration_stop`, `eligible_m_per_pair` (refuse), `pool_entry`, `member_eligibility`, `member_flags`, `score_method`, `score_identity`, `alarms`, `hold_count`, `fit_dof`, `fit_training_sets`, `known_h_doses`, `thresholds_rank`, `test_counts`, `test_members`, `u1`, `u2`, `u3`, `u3_bar`, `u4`, `u5`, `u6`, `carrier_curve`, `carrier_bootstrap`, `dc_benign_status`, `dc_training_sets`, `turn_counts`, `cache_counts`, `claim_licensing`, `sensitivity_lines`, `balance_by_condition` |
| presence | `dc_sealed`, `sealed_presence` |
| exact, REFUSING | `row_completeness` (F2: exact row sets from the roster, the registered council and H* grids and the recomputed turn counts: window attempts, eligibility members, scored rows per attempt/pair/convention, every logged row's council grid and full H grid, an H* block on exactly the C benign carriers and T sabotage rows, per-turn residual counts, every curve and n_by_h dose, U3 replay pairs in both print locations), `producer_identity` (F4) |

The families that are not recomputed:

- `integrity_only`: `input_echo`, `build_digests`, `engine_inventory`.
- `exempt`:
  - with an R21 ruling: `a3_attribution_bounds`, `a9_reason_vocabulary`, `a9_class_components`,
    `a28_not_captured_flags`, `a18_sabotage_bound`, `a32_no_rebuild`, `a36_battery_bar`,
    `u5_intercept_print`, `dc_model_print`, `w1_turn_tables`, `known_h_unregistered`,
    `known_h_dose_residual`, `fit_support_cov`, `a8_curve_diagnostics`, `a19_insufficient_prints` (seat 1
    F3: with `reason_code: insufficient_contrast_runs` only the code and the common absence of fit
    statistics are compared; reason strings never are);
  - none open: R26 ruled the H* grid and the carrier-curve doses, so `h_star`, every curve dose and the
    print-only `full_cell` are compared, and A27 ruled token counts sealed, so a token-count leaf on a sealed
    member refuses as unmapped;
  - no ruling yet: `claim_contract_open`, which is ENGINE-sol's remaining ruling 1;
  - constants and text: `registered_constants`, `registered_text`.

An `agree` says nothing about these families except integrity.

## 5. The synthetic rehearsal

`tests/v4_release/common_series.py` writes ONE series in both layouts. It uses the recompute's own writer
(`synth.py` at the pinned recompute commit) for members, frames, sidecar and meter, and adds:
- the R15 22-member allocation and the R20 24-member escalation (T3);
- zero-capture first attempts retried in their slots (C3 and T2);
- the bar-plus-reserve scenario (R22-2/R24): C4 ordinal 7 releases G0 4 C warm, C4 fails U2 for D, the export
  declares `barred: u1_u3_fail` (reproduced on both sides), C4 contributes nothing and the reserve C9 (seeds
  100-107 per pair) replaces it; with C3's zero-capture retry; and C1's first attempt AND its retry are
  zero captures, so the slot is barred (recompute `zero_capture_beyond_retry`, engine `zero_capture_refusal`
  in `calibration.barred_windows`; the record-level `barred`/`structural_bar` stay null) and the reserve C10
  replaces it. The comparator maps the bar codes 1:1 (`BAR_CODE`, `RECORD_BAR`; `BarCodeTests` reads both
  pinned sources);
- the r23j export: the full 18-window R24 allocation (engine `series_source`, analysis form; recompute
  `allocation_source`, the frozen native manifest, sha256 `21313cc2…`) and a GO terminal result bound by
  digest for every captured C attempt;
- C benign carriers too short to reach the upper H* grid with no exceedance (permanent; R26 amendment:
  h_star null, `bounded_above` false, the unobserved tail listed on both sides);
- the A37 seam windows (permanent): frame elapsed values of 1 s + 333/777 ns under the registered A21
  float-seconds accumulation with exact recorded-float conversion. C5 at the 2026 epoch: 238/239 ns gaps
  (snapped). C7 at 4.3e9 s: 953/954 ns seams (snapped). C6 at 9e9 s: 1,907/1,908 ns gaps (kept; every C6
  member is excluded for uncovered owned time, A2(4));
- A2(4) owned-time fixtures: C8 ordinal 12 at 9e9 s with > 1 us seams only inside its first G1 gate
  (eligible, disclosed); W1 ordinal 8 whose first turn starts before the first power support (excluded);
- screen fixtures: W1 anchor 2 and T1/T2-retry ordinal 6 carry a battery B code (W1 leaves the σ_w table,
  `W1_anchor_block: excluded:B`; the B run crosses T2's zero-capture attempt);
- the export contract of section 6a: exact production `offset_ns`, `h_star_grid`, W1 sentinel ordinals,
  series-unique anchor ids, W1 as a window record, numeric (never string) seconds.

The PROBE plan is the same series with W1 anchor 2's B code replaced by a G1 timeout that stops its episode
(P1: X2 re-derived; `W1_anchor_block: excluded:X2`), W1 contrast ordinal 6 not token-identical (the A19
contrast is unavailable: `insufficient_contrast_runs` on both sides), and U5 references with a negative slope
and delta = 2 C (seat 2 F7). Both plans must agree. A forged declared bar (C2 `barred: u1_u3_fail` with
passing U1-U3) must refuse on both sides (`test_forged_declared_bar_refuses_on_both_sides`). The fixtures are
producer-shaped (Episode seed = index, production run ids, real kit configs with RunBundleWriter bundle bytes,
producer plan headers). Probes, each on both sides: an episode carrying the derived seed (`seed_index_differs`), a
kit with enable_thinking false (`derived_seed_differs`), a SABOTAGE kit under a benign slot
(`config_identity_differs:condition`), a non-object kit (`config_invalid`), bundle bytes that are not the
writer's and a plan row whose digest is not the kit's (`config_digest_not_planned`), and a foreign window's plan
(`config_digest_not_planned:wrong_window`).

```bash
for m in test_compare_v4 test_release_v4 test_rehearsal_v4 test_review_sol1 test_review_sol2 test_confirm_sol; do
  python3.13 -B -m unittest tests.v4_release.$m; done
```

- **Tests need the pinned commits' objects.** A shallow clone skips the tests that need them.
- **Rehearsal caching.** Each plan is built once (generation, the two-stage engine run at 4 workers and the
  recompute) and cached read-only under the system temporary folder, keyed by the commits and the generator
  bytes. A cold plan takes 2.5-5 min (both plans built in parallel), almost all of it the engine.

- **Per-module run times** (Air, 2026-11-08, rehearsals cached, load 12-21):

  | Module | Tests | Time |
  |---|---|---|
  | `test_compare_v4` | 19 | 27 s |
  | `test_release_v4` | 17 | 18-27 s |
  | `test_rehearsal_v4` | 16 | 8 min (engine re-runs for its code mutation and the seed/config probes, prefix runs for refusals) |
  | `test_review_sol1` | 12 | 18 s |
  | `test_review_sol2` | 14 | 20 s |
  | `test_confirm_sol` | 6 | 55 s (inverted confirmation-seat witnesses) |

**Release runtime on the synthetic series** (16 engine attempts, 284 captured members). These are
`release_v4.py` wall times, stages (a)-(c), 4 workers, 2026-11-08 (r23j; two sessions on the Air):

| Plan | Total | Recompute (two stages) | Comparator |
|---|---|---|---|
| full | 10.5 s (7da631c3f) / 23.2 s (50f4958b6, loaded host) | 6.6 s / 16.7 s | 1.5 s / 2.4 s |
| probes | 11.0 s / 23.2 s | 7.2 s / 16.5 s | 1.3 s / 2.5 s |

Stage (a) re-hashes 823 files and verifies the producer identity; stage (b) confirms 284 members read the
same raw bytes. The engine's own run
is not part of the release: it runs incrementally as windows land.

## 6. Findings on the synthetic series

**Final rehearsal, 2026-11-08: exact AGREE on both plans.** Engine `50f4958b6` (engine-r23j) against
recompute `9f8a8749e`:

| Plan | Comparator | Families | Unmapped | `release_v4.py` |
|---|---|---|---|---|
| full | exit 0, `agree` | 64 compared, 0 expected-empty, 0 unexplained-empty | 0 of 266,566 engine leaves | exit 0, `agree` |
| probes | exit 0, `agree` | 64 compared, 0 expected-empty, 0 unexplained-empty | 0 | exit 0, `agree` |

The forged declared bar refuses on both sides; both seats' witnesses pass inverted. No holds remain. The
rulings that settled them, all blind, 2026-11-08:
- **Release reviews F1-F7** (seats 1 and 2 on `99875485d`): R22-2/R24 admitted-window calibration with
  reserves, R25 N = 22, row completeness, the W1 reason_code, pinned producer identity, journal rehash and
  census audit, fixed-code refusals for malformed shapes, the runbook command, the U5 |beta| x delta mapping.
- **R26 amendment**: whenever h_star is null, every unobserved grid dose is listed (found by this rehearsal:
  short C carriers with no exceedance; the engine's reading was adopted).
- **r23j exports**: reproducible declared bars, digest-bound terminal results, the full R24 allocation.
- **E1** (engine): a zero-capture raw window crashed the analysis; fixed in engine-r23.
- **P1** (engine bug): a G1/H timeout that stops the episode re-derives X2 (A9 union); fixed in engine-r23e.
- **P2 / A21**: seconds are the RECORDED value (binary float taken exactly, never a decimal lexeme);
  supports accumulate in float seconds as registered. The recompute switched to exact conversion; the
  engine reverted r23f's integer-ns accumulation in r23g. C5 agrees at the 1e-9 bar; C6 at 9e9 s is fully
  excluded on both sides.
- **A2(4)**: owned-time level; uncovered gate/pre-turn time is disclosed, not excluded. The recompute's
  print-only gross now integrates native supports with uncovered time as idle 0 (A2(3)).
- **A27**: the scored C-sabotage roster is hash-only on both sides; 30B anchor-sabotage replays print;
  sealed aggregates print `{status: sealed}` beside `benign_only`.
- **R26 (A7/A8)**: H*_i on the C benign carriers and T sabotage; curve doses council U H* grid; `full_cell`.
- Earlier: anchor σ_w with W1 (raw and clamped, `W1_anchor_block`), honest H = 0 carrier fraction, carrier
  status, DC residual rows mirroring the GPU benign rows, the A20 dropped-sample check, the export contract.

**Not a cross-build check:** raw bytes cannot place a 1.001 us seam at a 2026 epoch under the A21 rule, so
the exact 1 us boundary is covered by unit tests (`test_uncovered_owned_time_excludes_but_rounding_gaps_do_not`
and the engine's A37 hand tests); the rehearsal brackets it with 954 ns (snapped) and 1,907 ns (kept).

## 6a. Export contract (R23, RUN_STATE lead ruling on the 2026-11-08 report)

The exporter writes one custody in both layouts. Both adapters hold to these rules, and so does the
synthetic writer (`tests/v4_release/common_series.py`).

| Rule | Engine side (`engine-r23j`) | Recompute side (`independent_recompute_v4.py` @ `9f8a8749e`) |
|---|---|---|
| Sensor keys are production `policy.sensors.{s_fast, s_slow}` | production `Episode` layout, unchanged | `thermal_summary` reads `s_fast`/`s_slow` |
| Anchors are exactly ordinals 1-4 (W1 included) with strictly series-unique ids `"<window_id>:<run_id>"`; bare, mixed, wrong-prefix and duplicate anchor ids refuse, and so does a prefixed non-anchor | engine window name as `window_id` (`C3:` in both C3 attempts); it strips a matching prefix for the R15 check | window RECORD id as `window_id` (`C3-z1:` for the zero-capture record); non-anchor ids repeat only across a retried slot's attempts; two captured members never share an id |
| W1 is delivered as a window record (A34) | refuses a selection-only W1 in release runs | W1 is a window in `series.json` |
| The export carries the W1 sentinel ordinals | the reference input keys `w1_sentinel_j` by `"5"`/`"17"` | the W1 record carries `sentinel_ordinals: [5, 17]`; it must equal the R15 W1 roster's sentinels, else `w1_sentinel_ordinals_mismatch` |
| A G0 that overlaps the episode is custody-invalid (A2: "G0 lies before the episode") | production attribution | `g0_overlaps_episode` → `custody_invalid` |
| KM003C rate index matches the poll period; a dropped sample inside a span makes that span's DC value unavailable, with a reason (A20) | production `span_has_drops` | `meter_stream` drops from the header `rate_idx`; `unavailable_reasons` |
| Seconds are what the harness RECORDED: a binary float taken exactly (`Fraction(float)`), integers exact, never a decimal lexeme; string or bool seconds refuse; supports by float-seconds accumulation (A21, ruled) | refuses string/bool seconds on the release path | `seconds_ns` exact; float accumulation |
| The export carries production's `offset_ns` | `raw.member` checks it exactly | `production_offset_ns`, flag on mismatch |
| A2(4) at owned-time level: exclude iff an owned turn segment has uncovered time (interior or edge); uncovered gate/pre-turn time is disclosed, not excluded | `coverage_disclosures` on eligible members | `pm.episode_covered`; the print-only gross counts uncovered time as idle 0 (A2(3)) |
| A27: the scored C-sabotage roster is hash-only (30B anchor-sabotage replays are anchors and print); a not-captured sealed member prints `captured: false`; U1/U2 (and battery) aggregates involving it print `{status: sealed}` (no hash) beside `benign_only` | rows `status: sealed` + member hash | `members`/`exclusions` sealed rows; `{status: sealed}` aggregate fields |
| Member rows carry `attempt_id`; not-counted attempts print `captured: false` | DC, cache, realized-count, T missing-assignment rows | attempts are separate window records (`C3-z1`) |
| `h_star_grid` = {128, 256, 384, 512, 768, 1024, 1536, 2048} (R26) | registered grid | `series.json` `h_star_grid`, any other refuses |
| Producer shape (lead rulings 2026-11-08, from the exporter build): the Episode records the seed INDEX (workload.py:722); C/T non-anchors carry production run ids `align-v4-<window>-eNN` (align_v4_series.py:pack_id), W1 non-anchors `align-v4-episodes-{a,b}-eNN`, anchors their v3 kit ids; the frozen manifest is the roster authority | engine-r23k | `allocation_roster_check`; every row carries seed_index and expected_episode_seed |
| Scope (lead ruling 2026-11-08, amending A29): the seed and config identity checks apply to EVERY captured member, anchors and 30B included (anchors feed σ_w and U4) | every captured member | every captured member carrying a seed index (all rows carry one) |
| Seed ruling (a): `Episode.seed` = roster seed_index (`seed_index_differs`); production `episode_seed(*seed_inputs(config, enable_thinking), 'shade/'+spec pair, spec seed)` over the bundle config = roster expected_episode_seed (`derived_seed_differs`); both under `seed_identity_differs` | engine-r23k | restated as text over `config.json` |
| Config custody (r23l): window `plan_source` = the window's OWN committed collection_plan.json (series_window.v1 header, W1 kit plan); member `planned_config` = its kit config; plan row by ordinal with run_id = local id and config_sha256 = kit digest; bundle `config.json` = RunBundleWriter's bytes for the kit; breaks refuse `config_digest_not_planned` (`:wrong_window` for another window's plan); a non-object kit or bundle is that member's `config_invalid`; config run_id / align-model tag / spec pair, condition, seed must be the slot's (`config_identity_differs:{run_id,model,pair,condition,seed}`) | engine-r23k @ 72410b0b4 (`plan_source`, raw row `config`, `planned_config`) | window `plan_source`, row `planned_config`, member `config.json` |
| R24 allocation: the full 18-window frozen manifest (W1, C1-C14, T1-T3); an 11-window shape refuses | `series_source` (analysis form) | `series.json` `allocation_source` = the native manifest, sha256 `21313cc2…` (`allocation_missing`, `allocation_differs`) |
| Calibration attempts name their slot; a zero-capture attempt and its retry share it | attempt ids `C3#1`, `C3#2` | window records `C3-z1` and `C3`, `slot: C3` |
| Every captured C window binds its completed-chain terminal result `{verdict, chain_exit_code}` by digest; non-GO or a nonzero exit is a whole-window capture failure | `terminal_result_source` | `terminal_result_source` (`terminal_result_missing`, `terminal_result_digest_differs`) |
| A declared bar must be reproducible: a declared `u1_u3_fail` the window's own U1-U3 does not reproduce refuses; a declared `whole_window_capture_failure` needs non-GO evidence | `barred` on the window record | `barred` on the window record (`declared_bar_not_reproduced`, `capture_failure_unevidenced`) |

**A27 token-count seal scope (lead ruling).** The scored C-sabotage member is hash-only on both sides, token
counts included; the comparator compares the seals by presence, and any token-count leaf the engine printed for
a sealed member would be unmapped and REFUSE.

### 6a.1 The native exporter (`scripts/export_v4_series.py`)

```bash
python3.13 -B scripts/export_v4_series.py export --config EXPORT.json --window C3#2   # as each window lands
python3.13 -B scripts/export_v4_series.py export --config EXPORT.json --all           # every configured attempt
```

**Config** (`joulewise.v4_export.config.v1`; unknown keys refuse). It holds:
- `export_root`;
- `records_repo`;
- `kit_root`: the measurement checkout that holds the kit configs at the plan rows' `config_path`;
- `allocation` (the frozen manifest; its sha256 must be `21313cc2…`);
- `u3_bar`, `registration_inputs` and `r1_references`, each `{path, sha256}`;
- `engine_route`: `raw_source` only. Lead ruling 4 refuses `thermal_source` with `thermal_source_refused`;
- `windows[]` in series order, each with:
  - `attempt_id` (`C3#2`);
  - `record_commit` and `record_path` (read with `git show` through `WindowRecord`);
  - `session_root`: the harvest-off restore, which must equal the finalized manifest's `source_root`;
  - optionally `final_record`: the successor record whose `previous_final` makes this one final.

**What it reads.** Only the committed record and the files of the restored session. Every file is checked three ways:
- lexically, with no traversal;
- with lstat on each component, so no symlink;
- by its sha256 and size in the record-bound finalized manifest.

The capture descriptor (`captures[run_id]`, locator or blob) must carry the member's `raw/powermetrics.plist` sha256
and bytes. A planned member whose bundle holds a plist but whose capture is `null` refuses. A record that is not
final refuses, since the release reads final adjudications only.

**What it writes.**
- Per window, immutable once landed:
  - `engine/windows/<record id>/` holds `raw.json`, each member's production `align_episode.json` (hard link) and
    its `journal.json` (the sidecar rows as one JSON array);
  - `recompute/windows/<record id>/` holds the RECOMPUTE-opus layout;
  - `state/<record id>.json`.
- Rebuilt after every landing: `engine-input.json`, `engine/series-manifest.json`, `recompute/series.json`,
  `u3_bar.json`, `references.json`, `allocation/`, `crosswalk.json` and `census.json`.
- A re-export must reproduce a landed window byte for byte, or it refuses `window_already_exported_differs`.
- Two attempts resolving to one record id refuse `anchor_id_collision`.

**Same bytes.** The engine's `powermetrics`, `config` and `dc_streams` references and both builds'
`terminal_result_source` point at the same placed files under `recompute/`. Placement is a hard link, or a byte copy
re-hashed after placing.

**Mapping** (production source → engine raw row / recompute layout). No arithmetic of the exporter's own except
where noted.

| Field | Production source | Engine (`raw.json` row) | Recompute |
|---|---|---|---|
| config chain | the plan row by ordinal, whose `run_id` must be the member's local id → kit bytes must match `config_sha256` (refuses) → a kit that is not a JSON object or fails BenchmarkConfig normalization is exported unjudged (the builds' `config_invalid`) → otherwise bundle `config.json` = `align_v4_kit.bundle_config_bytes(BenchmarkConfig.from_mapping(kit))` (joulewise/bundle.py:964-967), or `config_digest_not_planned`. Config identity against the roster is never judged by the exporter (the builds' `config_identity_differs`) | checked again by the engine | checked again by the recompute |
| roster | record `sources.collection_plan.members[]`, checked field by field against the frozen manifest (pair, condition, seed_index, episode_seed, model_id; W1 role) | `roster` rows with series_role/held_out from the manifest `pool` (W1: anchor 1-4, sentinel 5/17, contrast X-/Y-, development) | `members[]` kind/model/pair/condition/contrast; `seed_index` and `expected_episode_seed` for EVERY member (30B included) |
| run ids | collection plan, verbatim; C/T non-anchors must be `align-v4-<slot>-eNN` by ordinal (align_v4_series.py:38, :285) | anchors `<slot>:<id>` | anchors `<record id>:<id>` (`C3-z1:`) |
| Episode | `outputs/align_episode.json` (records.py:181-202) | `episode` `{path, sha256}`, unmodified bytes | the same JSON with contract fields added, nothing removed (below) |
| plist | `raw/powermetrics.plist` | `powermetrics` ref | `raw/powermetrics.plist` (same file) |
| config | `config.json` (lead ruling (a), seed check) | `config` ref | `config.json` (same file) |
| plan | record `sources.collection_plan` bytes, verbatim, header included (every attempt). It must be this window's plan: C/T `schema_version` `joulewise.align_v4.series_window.v1`, `plan_id` `align-v4-<window>`, `window_id`, `series_manifest_sha256` (align_v4_series.py:339-340); W1 `joulewise.align_v4.v1` / `align-v4`. A plan `attempt_id` must equal the record's | window `plan_source` ref | window.json `plan_source` (same file) |
| kit config | `kit_root/<plan row config_path>`, sha256 = plan row `config_sha256` (align_v4_series.py:302); copied into the export (it lies outside custody) | `planned_config` ref (captured members) | member row `planned_config` (same file) |
| stamps | Episode `hardware.paired_clock_stamps_ns` via `sampler._restore_stamp` (sampler.py:56, as workload.read_episode_bundle:900) | `stamps` (ClockStamp seconds, floats) | `paired_clock_stamps_ns` verbatim |
| clock evidence | metadata `uncertainty_evidence` | `clock_evidence` verbatim | metadata verbatim + `clock_anchor.wall_minus_monotonic_bounds_ns` = exact(lower_s, upper_s) (Fraction, ties to even) |
| offset | `sampler.stamp_mapping` (sampler.py:83) over the restored stamps and that evidence | `offset_ns` | `hardware.production_offset_ns` |
| endpoint | metadata `clock_anchor.first_sample_end_point_epoch_s`, as recorded (int/float only) | `first_record_endpoint_s` | metadata verbatim |
| period | `round(1e9 / config.sampling.power_hz)` = workload.read_episode_bundle:916 | `nominal_interval_ns` | metadata `sampling.power_period_ns` |
| registered span | WP22 rule (align_v4_w1_synthetic.py:353): first G0 start (else episode start), episode end | `registered_span_ns` | `hardware.registered_span_ns` |
| sidecar | `outputs/align_thermal.jsonl` (gated members only; absent for ungated 30B anchors, as read_bundle_record reads it) | `journal` ref (JSON array of the rows) | `outputs/align_thermal.jsonl` = `thermal_desk.normalize_journal` rows (thermal_desk.py:118) |
| OS readings | `normalize_journal` rows' `status.os_level` (read_bundle_record:811-813) | `os_readings`, `registered_os_readings` | derived by the recompute from the rows |
| turn rows | `outputs/align_turns.jsonl` | `turn_rows` (inline) | (not read) |
| identity | `[[prompt_token_ids, output_token_ids], …]` per turn (below) | `identity_sha256` | Episode `identity_sha256` |
| reasoning | Episode turn `hidden_tokens` | Episode bytes | turn `reasoning_tokens` = `hidden_tokens` |
| status | `enrich_record` (align_v4_thermal_desk.py:74): token_budget.incomplete | `status` | Episode `completed` = status == completed |
| cache | `diagnostics.cache_statistics(turn rows)` (diagnostics.py:257) | `cache_statistics` | `hardware.cache` |
| cohort | `v4_registration.cohort_identity` (v4_registration.py:698) + spec four slots (enrich_record:68-73) | `cohort_identity`, `configuration`; series `cohort` = W1 ordinal 5, bound to the U3 bar's `d_configuration_sha256` | Episode and window `cohort_sha256` (below) |
| battery | `v4_battery.bundle_evidence` over custody `hazards/monitor/battery.jsonl` (v4_battery.py:46) | `battery` | `battery {run_id: flags + battery.unobserved}` |
| exclusions | record `sources.exclusions.members_excluded` (final), `v4_contention.split_codes` (R22-1) | `exclusion_codes` | `adjudication.excluded` |
| identity map | committed desk: `pilot7_token_identical` (align_v4_thermal_desk.py:133, align_v4_session.py:333) for contrast runs; desk `tokens` equality for the registered replay pairs (WindowRecord.eligibility rule) | (re-derived) | `identity` |
| DC | custody `night/hazard_result.json` `meter.streams` (path, sha256; km003c.py:211-245) | benign `dc_streams` refs + `member_span_ns` = [episode start, end] | `meter/<name>` + `meter.streams` |
| terminal | record `sources.result` (schema `joulewise.unattended_night_result.v1`), cross-checked with `chain_exited.exit_code` and `courier_sent` and with the restored custody `night/result.json` bytes | `terminal_result_source` (captured C only) | `terminal_result_source` (same file) |
| bar | record `barred`, passed through only if it equals `WindowRecord.structural_bar` | `barred` | `barred` |
| U3 / R1 / delta | registered U3 bar (`v4_u3.policy_checks`, `relative_pairs`), registration `inputs.json` R1 policy, R1 references file | `u3_evidence`, `reference`, `r1_sensitivity`, `delta_slow_c`, `u6_split_rule` (A16 constant) | `u3_bar.json`, `references.json` |

**Exporter-defined digests (export contract).**
- `identity_sha256` = SHA-256 of `json.dumps([[p0, o0], [p1, o1], …], separators=(',', ':'), ensure_ascii=True,
  allow_nan=False).encode('ascii')`, with no trailing newline. The pairs are in turn order from
  `outputs/align_turns.jsonl` `generation.{prompt_token_ids, output_token_ids}`. It is null when a turn lacks either
  list. Unit: `test_exporter_units.test_identity_sha256_is_the_registered_canonicalization`.
- `cohort_sha256` = SHA-256 of `json.dumps({"configuration": …, "identity": …}, sort_keys=True,
  separators=(',', ':'), ensure_ascii=True, allow_nan=False)`.
- `Episode.seed` is carried verbatim (the seed index). The seed check is the builds' own (lead ruling (a)).

**Not real producers in the synthetic end-to-end test** (`tests/v4_release/test_exporter_e2e.py`, built by
`native_series.py`):
- the raw powermetrics plist. WP22's synthetic GPU rail writes none, so the test writes one frame per
  `power_trace.csv` row with the pinned recompute's FrameTemplate. Real custody without a plist refuses
  `member_file_missing`;
- the KM003C stream;
- the U3 bar;
- the R1 references file.

Everything else comes from real producers:
- WP22's world, controller, kit and series kit;
- the real thermal desk;
- the harvest-off finalize, pack and unpack;
- the WindowRecord reader.

**Refusal codes** (exit 2; stdout is `{"status": "refused", "code": …}`):

| Code | Cause |
|---|---|
| `config_invalid` | The config is malformed |
| `unknown_contract_key` | An unknown key where a contract key is expected: config, record, `v4_series`, `policy.sensors`, or a projected field already present |
| `thermal_source_refused` | The config asks for the thermal_source route |
| `record_unreadable` | The window record cannot be read |
| `record_window_differs` | The record's window or role differs from the configured attempt |
| `record_not_final` | The record is not final |
| `session_unavailable`, `session_root_differs`, `session_window_differs` | The restored session is missing, is not at the finalized `source_root`, or names another window |
| `path_refused`, `path_outside_session` | A symlink, a traversal, or a path outside the session |
| `file_not_in_finalized_manifest`, `digest_mismatch` | A file is not bound by the finalized manifest, or its bytes differ |
| `member_file_missing` | A member bundle file is missing |
| `member_malformed`, `turn_rows_mismatch` | A member file is malformed, or its turn rows do not match the Episode |
| `seconds_not_numeric` | Recorded seconds are not a number |
| `roster_differs_from_manifest` | The collection plan differs from the frozen manifest |
| `roster_differs_from_plan` | The night plan, a bundle config or the Episode differs from the collection plan |
| `capture_missing_from_record`, `capture_digest_differs` | A capture is null while a plist exists, or its digest differs from the plist |
| `terminal_evidence_missing`, `terminal_evidence_mismatch` | Terminal evidence is missing, or result, chain.exited and custody disagree |
| `config_digest_not_planned` | The plan row's `config_path`/`config_sha256`, the kit bytes and the bundle `config.json` do not form the writer chain |
| `config_digest_not_planned:wrong_window` | The committed plan is not this window's producer plan (header, or `attempt_id`) |
| `kit_not_normalized` | A valid kit config whose bytes differ from `json.dumps(BenchmarkConfig.from_mapping(kit).to_dict(), indent=2, sort_keys=True) + "\n"` (lead ruling), which would split the builds' bundle-byte derivations |
| `desk_record_differs` | The committed desk's battery, cohort, configuration, status or cache differs from the derivation |
| `owned_energy_flags_unexpected` | The desk record carries `owned_energy_flags` |
| `declared_bar_inconsistent` | A declared bar does not match the committed structural bar |
| `cohort_unbound` | The W1 ordinal-5 cohort is missing, or its digest is not the U3 bar's |
| `meter_custody_invalid` | The KM003C stream listing is invalid |
| `allocation_differs` | The allocation is not the frozen manifest |
| `u3_bar_invalid`, `r1_references_invalid`, `registration_inputs_invalid` | A series input is invalid |
| `window_order_gap` | An earlier configured window has not landed |
| `window_already_exported_differs` | A re-export does not reproduce the landed window |
| `anchor_id_collision` | Two attempts resolve to one record id, or captured ids or anchors repeat |
| `export_layout_collision` | Two outputs would land at the same path |

### 6a.2 Real-producer end-to-end: findings (2026-11-08, synthetic only)

**Run.** The series was W1, C1, a C2#1 zero capture and a C2#2 retry, built with the real producers of 6a.1.

**Status at the release pins (engine-r23k `72410b0b4`, recompute `7b06c6058`).**
- The exporter lands every window, and re-export is byte-identical.
- release_v4 stage (a) verifies: 490 engine files rehashed, producer identity verified, crosswalk equals both rosters.
- Stage (b): the recompute runs twice, and both builds read the same raw bytes for all 62 captured members.
- The engine completes; EXP-G1 and EXP-G2 are closed in r23k.
- The comparator refuses (`comparator_input_malformed`) on EXP-G3.
- Diagnostically past EXP-G3 it refuses `unmapped_leaf` on EXP-G4.
- Past both, EXP-D1 dominates. The recompute bars C1 and C2 (U1 FAIL) while the engine fits them, so every fit,
  score, threshold, known-H and carrier family holds, and `eligible_m_per_pair` refuses (R-C5).

**Status at engine-r23m `5e1f564a2` / recompute `c595cc07b`** (with the release-tools comparator G3/G4 fixes).
- G3, G4, D1, D5 and D6 are closed.
- Stage (a) verifies and stage (b) shares all 62 raw members.
- 59 families are compared. Eligibility, U1/U3/U4, the fits, scores, ledger, cache and battery agree.
- The comparator still refuses (`unmapped_leaf`) on the open items below. Every one concerns a PREFIX series (two
  counted C windows, calibration incomplete) or a fixture artifact:

| Id | Item | Class | Evidence |
|---|---|---|---|
| EXP-P1 | known_h_scores/doses, h_star, carrier_curve and carrier_bootstrap: the engine prints them before calibration_complete, the recompute withholds them (A25), so row_completeness refuses | build disagreement (D7 incomplete) | 532 + 1540 + 196 + 60 + 14 rows `absent_recompute`; row_completeness 47 rows |
| EXP-P2 | Thresholds at the prefix: status `continue` with rank 14 but null bounds (engine) vs `withheld_until_calibration_complete` with bounds 1/(m+1) and iid_upper90 (recompute) | build disagreement (D7) | thresholds_rank 24 rows, threshold_bounds 16 rows |
| EXP-P3 | calibration_stop `windows`: engine 8 vs recompute 2 counted | engine prefix print, or comparator mapping | 1 row |
| EXP-P4 | U2 for the ungated 30B in C windows (no planned G0): engine `not_applicable` (= the D2 ruling) vs recompute `pass` | recompute D2 implementation | 4 rows |
| EXP-P5 | U6 bank `imprecise`: engine true, recompute false | open, needs a trace | 1 row |
| EXP-P6 | DC residuals of a constant-power synthetic meter are floating-point noise (~1e-9 J, ~1e-12 J apart), and a relative bar fails | fixture artifact exposing a comparator gap (no absolute floor) | dc_benign 7 rows |
| EXP-P7 | Empty W1 anchor block: the engine prints `anchor_sigma_w` nulls and a `reason` (the one unmapped leaf), the recompute prints nothing | empty-state print + comparator mapping | 5 rows + `/fill/anchor_sigma_w/reason` |

The table below was first recorded on the engine-r23j / recompute-9f8a8749e run. `test_exporter_e2e` now pins engine-r23k
(`72410b0b4`) and the recompute at `7b06c6058`, which implement `plan_source`, `planned_config` and the plan owner
check. The recompute
derives the bundle bytes as `json.dumps(json.loads(kit), indent=2, sort_keys=True)` and the engine through
`BenchmarkConfig`. These agree only because the writer's normalization is the identity on real kit configs (checked on
the C1 kit and on the repository's W1 kit configs). A kit field that `to_dict()` normalizes would split the builds.
- The exporter landed every window, and re-export was byte-identical.
- The recompute ran (exit 0).
- engine-r23j read all 62 captured members through `io.load` and the raw adapter. That includes the exact
  exported production `offset_ns` check on non-integer stamps. `analyze()` then refused (EXP-G2).
- A DIAGNOSTIC run patched the engine's `roster()` run ids to the production names and the comparator's
  `MODEL_SHORT` to the production display names. It never feeds a release.
- In that run the comparator still refuses `unmapped_leaf` and holds the families below.
- `test_exporter_e2e.test_release_agrees` stays an expected failure until EXP-G1 to EXP-G4 are closed.

| Id | Item | Class | Evidence |
|---|---|---|---|
| EXP-G1 | `Episode.seed` is the seed index; both builds compared it with the derived seed | contract gap, ruled (a) 2026-11-08; closed in r23k / 7b06c6058 | workload.py:722 vs engine.py:255, recompute `derive_exclusions`; fixture common_series.py:338 |
| EXP-G2 | C/T run ids are `align-v4-c1-e06` in production, while the engine's frozen `roster()` expects `align-v4-c1-episodes-a-e06` | engine (contract gap); closed in r23k | align_v4_series.py:38,285 vs engine.py:70-71; fixture common_series.py:85-86 |
| EXP-G3 | `Episode.agent_model` is the config display name (`Qwen3-30B-A3B-4bit`). The engine keys acceptance by it, and the comparator's `MODEL_SHORT` (compare_v4_recompute.py:65) holds only model ids, so it raises KeyError and refuses `comparator_input_malformed` | comparator (release tools) | workload.py:721; fixture common_series.py:511 (`agent_model=model_id`) |
| EXP-G4 | Production `cache_statistics` keys `{status, cached_tokens, fed_tokens, trims, trimmed_tokens, rebuilds, prefill_removed_tokens}` are unmapped in the comparator's `cache_diagnostics`, giving `unmapped_leaf`. Production has no `rewinds` | comparator | diagnostics.py:257-265; fixture common_series.py:547 `{rebuilds, rewinds}` |
| EXP-D1 | U1(c) sidecar coverage. The recompute counts `ceil(span/1 s)` cells from the span start. A real G0 span is non-integer (42.46 s), so it covers 42/43 cells = 0.977 < 0.99, and U1 FAILs for every gated model in every window, which bars C1 and C2. The engine (production `temperature.Coverage` on the collector grid) passes | build disagreement (A11 reading), needs a ruling | recompute `thermal_summary.coverage` (independent_recompute_v4.py:1018), `u1_model_window`; synth spans are whole seconds |
| EXP-D2 | U2(a) for a model with no G0 at all (ungated 30B anchors in C windows): the engine says `inconclusive`, the recompute `not_applicable` | build disagreement (A12) | synth writes a G0 for every member, so the fixture never shows it |
| EXP-D3 | A13 replay eligibility. The engine makes a 5/22 pair inconclusive when either member has ANY class (here `seed_identity_differs`). The recompute excludes only `REPLAY_INELIGIBLE` classes and computes the pair (`pass`) | build disagreement, surfaced by EXP-G1 | recompute `REPLAY_INELIGIBLE` |
| EXP-D4 | A29 scope: the engine applies the seed check to every member (30B anchors too), the recompute to D only | build disagreement | engine.py:255 vs recompute `derive_exclusions` |
| EXP-D5 | Not-captured members: the engine adds class `incomplete` (`raw.member` status for `captured: false`), the recompute prints only `not_captured` | build disagreement | raw.py:37-38 (r23j) |
| EXP-D6 | DC for 30B benign members (ungated, no thermal): the engine prints `meter.turn_uncovered`, while the recompute integrates DC | build disagreement, print-only family | `dc.capture` |
| EXP-D7 | A prefix series (no T landed): the engine prints T rows from the manifest and the recompute none (`row_completeness`). An empty W1 anchor block: the engine prints `anchor_sigma_w` nulls and the recompute nothing | comparator/build empty-state rows | |
| EXP-F1 | The W1 30B anchors' first turn starts as sampling starts, so it is not PM-covered and `energy_unavailable` in BOTH builds. The cause is the WP22 synthetic rail plus the test-side plist; a real powermetrics capture has pre-roll | fixture limitation (not a build disagreement) | tests/align/w1_synthetic.py:405 |

**Synthetic fixture vs real producer** (every difference found in this sweep; fixture = `tests/v4_release/common_series.py`
and the pinned recompute's `tests/independent_recompute_v4/synth.py`):

| Field | Synthetic fixture | Real producer | Exporter / status |
|---|---|---|---|
| Episode `seed` | derived episode seed (common_series.py:338, :512) | seed index (workload.py:722) | verbatim; EXP-G1 ruled |
| non-anchor run ids | engine naming `align-v4-c1-episodes-a-e06` (common_series.py:85-86) | `align-v4-c1-e06` (align_v4_series.py:285) | verbatim; EXP-G2 |
| `agent_model` | model id (common_series.py:511) | config display name (workload.py:721) | Episode bytes; EXP-G3 |
| `cache_statistics` | `{rebuilds, rewinds}` (common_series.py:547) | diagnostics.py:257-265 keys | production value; EXP-G4 |
| reasoning | `reasoning_tokens` (synth turns) | Episode `hidden_tokens` | recompute alias = hidden_tokens |
| `registered_span_ns`, `production_offset_ns`, `identity_sha256`, `cohort_sha256`, `completed`, `hardware.cache` | written into the episode by synth/common_series | absent from the production Episode | exporter contract fields (6a.1) |
| metadata | `sampling.power_period_ns`, anchor only (synth.py:190-192) | no `sampling`; `clock_anchor.wall_minus_monotonic_{lower,upper}_s`; power_hz in config.json | `power_period_ns` from config; `bounds_ns` exact |
| clock stamps, spans | whole seconds (common_series EXPORT_NOTES) | non-integer (WP22: 4387.603199999 s) | verbatim; the offset check passes; EXP-D1 |
| power cadence | 1 Hz frames (common_series `period_ns=NS`) | 10 Hz (kit config `power_hz`) | verbatim |
| thermal sidecar | pre-normalized `kind: sample` rows for EVERY member (synth; common_series.py:522-525) | `joulewise.align_thermal.v1` reading/session rows, gated members only | engine: raw rows (JSON); recompute: `normalize_journal` rows; anchors: none (recompute flag `thermal_journal_missing`) |
| G0 / thermal policy on 30B anchors | present (synth writes a G0 for all) | absent for ungated 30B anchors | EXP-D2 |
| gate `reference` | copy of the G0 release (common_series.py:356-357) | production reference `{fast_c, slow_c, source_member, span_ns}` | Episode bytes |
| turn rows | token ids fabricated from the identity hash (common_series.py:548-551) | full generation rows with cache fields | inline verbatim |
| battery | static `{observed, soc 100, charger 80, 'c'*64}` (common_series.py:544-545) | `v4_battery.bundle_evidence` (spans, assist, per-reading lists) | production value, cross-checked with the desk |
| DC span | `[episode start, end]` (common_series.py:547) | production desk: `harvest.member_spans(metadata, events)` (km003c.py:256) | `[episode start, end]` (the recompute's span); open item |
| meter stream | `km003c-0.jsonl` in the window dir | custody `hazards/meter/stream-NNN.jsonl`, listed with sha256 in `night/hazard_result.json` | placed under `recompute/windows/<W>/meter/` |
| terminal result | derived `{verdict, chain_exit_code}` file (common_series.py:397-406) | `night/result.json` (`joulewise.unattended_night_result.v1`, more keys) | result.json bytes by digest; both builds accept the extra keys |
| identity map | `identical` for every sentinel/contrast run (common_series.py:327-328) | desk `pilot7_token_identical` and desk token equality | from the committed desk |
| W1 desk | n/a | WP22's dry-run desk also lists the two pilot-7 references | the fixture drops them from the record (the session desk covers only the roster) |

## 7. Before the real release

1. The exporter writes the engine manifest, the recompute layout and the crosswalk from one custody, with the
   same raw bytes, to section 6a. Stage (b) refuses otherwise.
2. Re-run the three test modules, then run the release on the real custody into a new `$OUT`.
