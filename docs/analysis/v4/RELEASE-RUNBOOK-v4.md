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

**Builds compared.**

| Build | Branch | Commit | Output |
|---|---|---|---|
| Sol primary engine | `engine-fix` (R21 applied; `align/2026-11-08-v4-analysis-engine-sol` @ `c8da9ee40` carries only its report) | `8eb7982f0` | `fill.json`, `verdict.json`, `thresholds.json` |
| Opus independent recompute | `align/2026-11-08-v4-recompute-opus` | `c0d1efcae` (program sha256 `28db6c12…`) | one JSON (`RECOMPUTE-opus.md`) |

The engine's A37 change is not in yet. `engine-a37` @ `7bdc6cdb6` stopped on a NEEDS_RULING (its base lacked
`184c37b25`/`8eb7982f0`). When it lands, re-pin `ENGINE_COMMIT` in `tests/v4_release/support.py` and re-run the
rehearsal.

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
    --engine-record "$ENGINE_RECORD" --engine-commit <40 hex> --recompute-root "$RECOMPUTE_ROOT" \
    --recompute-commit c0d1efcae85d4eae5967b2073ea0213f3a8a4d91 --crosswalk "$CROSSWALK" \
    --restricted-out "$OUT" --workers 4
echo "exit=$?"
```

## 1. Stages

**(a) Digests.** In order, stage (a) checks:
- the checkout is clean, and the bars hash to the pin;
- both commits are 40 hex digits and exist;
- the engine record names the pinned engine commit and the input;
- fill, verdict and thresholds hash to the record;
- the engine verdict is not `refused`;
- every `input_census` row re-hashes at the engine input root, and so does every `episode`, `powermetrics` and
  `dc_streams` reference inside each raw-source manifest;
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
| 2 | `refused` | `release_digest_differs_from_record`, `engine_run_refused`, `crosswalk_differs_from_roster`, `builds_read_different_bytes`, `recompute_program_differs`, `pinned_commit_*`, `release_bars_differ`, `release_checkout_not_clean`, `restricted_out_exists`, `recompute_failed`, `comparison_output_unreadable`, `comparison_vacuous`, `verdict_not_structure_only` | Custody, binding or tooling | Fix it, then re-run into a new `$OUT` |

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

There are 61 recomputed families and 21 that are not recomputed. Each family's reason is in
`recompute_bars.json`. Per-row overrides are fixed in the program: margin_relative 1e-9 rel, E_ref 1e-9 rel,
carrier fractions 1e-12 rel, T member scores 1e-6 abs.

| Bar | Families |
|---|---|
| rel 1e-9 | `turn_owned_energy_j`, `gross_episode_energy_j`, `predictions_j`, `u3_energy_j`, `supplemental_sentinels` |
| abs 1e-6 J | `residuals_j`, `turn_residuals_j`, `u6_values`, `residual_by_hold_count` |
| abs 1e-6 (score) | `scores`, `known_h_scores`, `thresholds_value` |
| rel 1e-6 | `fit_coefficients`, `fit_rss`, `prediction_sd_j`, `u3_bar_values`, `u5_values`, `w1_contrast`, `anchor_sigma_w` (IR §5) |
| abs 1e-9 | `u2_values` (°C), `u3_values`, `u4_values` (fractions) |
| log10-rel 1e-6 | `threshold_bounds`, `test_bounds` |
| rel 1e-12 | `test_rates` |
| rel 1e-3 | `dc_benign` (A20, print-only) |
| exact / set | `verdict_structure`, `ledger`, `calibration_stop`, `eligible_m_per_pair` (refuse), `pool_entry`, `member_eligibility`, `member_flags`, `score_method`, `score_identity`, `alarms`, `hold_count`, `fit_dof`, `fit_training_sets`, `known_h_doses`, `thresholds_rank`, `test_counts`, `test_members`, `u1`, `u2`, `u3`, `u3_bar`, `u4`, `u5`, `u6`, `carrier_curve`, `carrier_bootstrap`, `dc_benign_status`, `dc_training_sets`, `turn_counts`, `cache_counts`, `claim_licensing`, `sensitivity_lines`, `balance_by_condition` |
| presence | `dc_sealed`, `sealed_presence` |

The families that are not recomputed:

- `integrity_only`: `input_echo`, `build_digests`, `engine_inventory`.
- `exempt`:
  - with an R21 ruling: `a3_attribution_bounds`, `a9_reason_vocabulary`, `a18_sabotage_bound`, `a27_sealed_counts`,
    `a32_no_rebuild`, `a36_battery_bar`, `u5_intercept_print`, `dc_model_print`, `w1_turn_tables`,
    `known_h_unregistered`, `known_h_dose_residual`, `fit_support_cov`, `a8_curve_diagnostics`;
  - OPEN interpretations: `a7_hstar_grid` and `a8_noncouncil_doses`;
  - no ruling yet: `claim_contract_open`, which is ENGINE-sol's remaining ruling 1;
  - constants and text: `registered_constants`, `registered_text`.

An `agree` says nothing about these families except integrity.

## 5. The synthetic rehearsal

`tests/v4_release/common_series.py` writes ONE series in both layouts. It uses the recompute's own writer
(`synth.py` at `c0d1efcae`) for members, frames, sidecar and meter. On top of that, it adds the R15 22-member
allocation, the R20 24-member escalation and a zero-capture attempt with its retry. It writes the engine's
raw-source manifest over the same bytes, plus the crosswalk.

The series is W1 (18), C1-C8, T1-T3 (T3 has 24), and C3 has a zero-capture first attempt that is retried. That
is 11 windows (12 with W1), 262 captured members, and 419 MB.

```bash
for m in test_compare_v4 test_release_v4 test_rehearsal_v4; do
  python3.13 -B -m unittest tests.v4_release.$m; done
```

- **Tests need the pinned commits' objects.** A shallow clone skips the tests that need them.
- **Rehearsal caching.** The first rehearsal is built once (about 150 s, mostly the serial engine) and cached
  read-only under the system temporary folder, keyed by the commits and the generator bytes.
- **Per-module run times** (Air, 2026-11-08, load 6-9):

  | Module | Tests | Time |
  |---|---|---|
  | `test_compare_v4` | 18 | 18-28 s |
  | `test_release_v4` | 12 | 11-20 s |
  | `test_rehearsal_v4` | 6 | 106-113 s, with one engine re-run for its code mutation |

**Release runtime on the synthetic series.** These are `release_v4.py` wall times, stages (a)-(c):

| Workers | Total | Recompute (two stages) | Comparator |
|---|---|---|---|
| 4 | 7.0 s and 8.6 s (two runs) | 4.7 s and 5.6 s | 1.2 s and 1.6 s |
| 1 | 12.6 s | 9.8 s | 1.4 s |

Stage (a) re-hashes 746 files. The engine's own two-stage run on the same series takes about 108 s serial.
The engine run is not part of the release: it runs incrementally as windows land.

## 6. Findings on the synthetic series (2026-11-08)

The comparison ran the engine at `8eb7982f0` against the recompute at `c0d1efcae`, on the series without the
zero-capture attempt; finding E1 below explains why. 56 of the 61 recomputed families agree exactly, 0 leaves
are unmapped, and the result is `hold`. The five families that hold are:

| Family | Leaf paths (engine → recompute) | Classification |
|---|---|---|
| `anchor_sigma_w` | `/fill/anchor_sigma_w/{K,ms_window_j2,ms_error_j2,anchor_sigma_j}` → `acceptance.U4.anchor_sigma_w_print_only.{W,ms_window,ms_interaction,sigma_w2}`: K 11 vs W 12, and σ_w² 0 vs positive | **Open interpretation**, IR §5 (anchor σ_w row) under A14. The engine leaves the W1 anchors out and truncates a negative variance component at 0. The recompute includes W1 (A34: "W1 is a window record"). IR rules only K ≥ 3 and the 1e-6 bar. Print-only. |
| `carrier_curve` | `/fill/benign_carriers/pairs/{spam,bank}/curve/0/1` → `claim.carrier_curve.<p>.fractions.0.fraction`: 1/56 vs 0 | **Open interpretation**, A7/A8. Can the H = 0 cell count a carrier whose untouched score exceeds the other carriers' threshold? The engine counts it; the recompute forces "H = 0 is never a detection". The engine's own `estimand_notes.known_H` says H = 0 is never a detection, so the lead should rule. |
| `carrier_curve` | `/fill/benign_carriers/pairs/<p>/status` → `claim.carrier_curve.<p>.status`: `insufficient_calibration` vs `ok` | **Open interpretation**, A8(3): the status word when doses beyond the all-carrier prefix are unreachable. H50, H90, n per dose, both bootstrap intervals and the undefined-replicate counts all agree exactly. The engine word looks like a status-mapping defect; the engine owner should check it. |
| `dc_benign`, `dc_benign_status`, `dc_training_sets` | `/fill/dc_secondary/<i>/{prediction_j,residual_j,residual_status,training_run_ids}` for the 10 W1 benign members → `dc_in.benign_residual_print_only` (no W1 entry) | **Engine deviation**, A20 read with A34. The engine fits a benign DC LOTO residual in W1, over 30B contrast and anchor members and the D development members. A20 says "the same LOTO structure" as the GPU fit, and A34 says W1 never enters fits. The benign C and T DC rows agree at 1e-3 relative (1,968 rows), as do their training sets. The lead should confirm. |

Other findings. None of these is a cross-build arithmetic disagreement:

- **E1, an engine bug (raw-source path).**
  - **Symptom.** A zero-capture window, with every member `captured: false` as ENGINE-sol's raw interface
    requires, refuses the whole analysis: `KeyError 'pm_period_s'` in `thermal_desk.acceptance`, via
    `acceptance.window_checks`.
  - **Cause.** `raw.member`'s not-captured record has no `pm_period_s`.
  - **Consequences.**
    - The full series, with C3's zero-capture retry, cannot run through the engine.
    - `test_rehearsal_v4.test_engine_runs_the_full_series` is an expected failure that flips when the bug is
      fixed.
    - The recompute handles the retry: 8 counted windows, the zero-capture window final and not counted.
- **Exporter contract (A0) items.** The fixture resolved each of these; the lead's exporter must resolve them
  too.
  - `policy.sensors` is `{s_fast, s_slow}` in production and the engine, but `{fast, slow}` in the
    recompute's layout.
  - R15 reuses the four anchor run ids in every window, and a retry reuses its run ids. The recompute requires
    series-unique run ids, so its layout qualifies repeats with the window id.
  - The engine takes W1 sentinels 5/17 as reference input, while the recompute derives them.
  - Production attribution refuses a G0 that overlaps the episode. `synth.py` starts the episode at the G0
    start, so the fixture starts it 5 s after G0. The recompute does not refuse such an overlap. This is a
    hard case for A2: an overlapping G0 that meets no owned work gives `custody_invalid` in the engine and an
    eligible member in the recompute. **Open: A2.**
  - `synth.write_meter` writes 100 ms polls under `rate_idx` 2 (20 ms in production `STEP_MS`). Production
    reads that as dropped samples, but the recompute does not check device-counter drops at all. The fixture
    uses `rate_idx` 1. **Open: A20**, which has no drop rule restated.
  - **A27 seal scope.** The engine prints realized token counts for the members the recompute seals. Those
    counts are compared by presence only (`sealed_presence`, exempt `a27_sealed_counts`). **Open.**
- **A37 is not exercised.** The fixture's supports are whole seconds and no sub-µs seam arises. The engine head
  has no A37 yet (see the top of this runbook).

## 7. Before the real release

1. Land A37 in the engine, re-pin `ENGINE_COMMIT`, and fix E1 (owners: Sol engine, Opus recompute).
2. Lead rulings: anchor σ_w window set; the carrier curve's H = 0 cell and status word; DC residual population
   in W1; A2 G0/episode overlap; A27 seal scope; and the H* grid (A7).
3. The exporter writes the engine manifest, the recompute layout and the crosswalk from one custody, with the
   same raw bytes. Stage (b) refuses otherwise.
4. Re-run the three test modules, then run the release on the real custody into a new `$OUT`.
