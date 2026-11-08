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
| Sol primary engine | `engine-r23d` (R21 + A37 + R23 + R23c/d; Opus delta review ADMITted r23b) | `a2e36bc19` | `fill.json`, `verdict.json`, `thresholds.json` |
| Opus independent recompute | `align/2026-11-08-v4-recompute-opus` (R23 + R23c/d) | `fdd02a96b` (program sha256 `48d7752b…`) | one JSON (`RECOMPUTE-opus.md`) |

History: the first rehearsal (2026-11-08, engine `8eb7982f0` vs recompute `c0d1efcae`) held on five
families and found engine bug E1; lead ruling R23 and its clarifications (R23b-d) resolved all of them.

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

There are 61 recomputed families and 23 that are not recomputed. Each family's reason is in
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
  - with an R21 ruling: `a3_attribution_bounds`, `a9_reason_vocabulary`, `a9_class_components`,
    `a28_not_captured_flags`, `a18_sabotage_bound`, `a27_sealed_counts`,
    `a32_no_rebuild`, `a36_battery_bar`, `u5_intercept_print`, `dc_model_print`, `w1_turn_tables`,
    `known_h_unregistered`, `known_h_dose_residual`, `fit_support_cov`, `a8_curve_diagnostics`;
  - OPEN interpretations: `a7_hstar_grid` and `a8_noncouncil_doses`;
  - no ruling yet: `claim_contract_open`, which is ENGINE-sol's remaining ruling 1;
  - constants and text: `registered_constants`, `registered_text`.

An `agree` says nothing about these families except integrity.

## 5. The synthetic rehearsal

`tests/v4_release/common_series.py` writes ONE series in both layouts. It uses the recompute's own writer
(`synth.py` at the pinned recompute commit) for members, frames, sidecar and meter, and adds:
- the R15 22-member allocation, the R20 24-member escalation (T3);
- zero-capture first attempts retried in their slots (C3 and T2);
- the A37 seam fixture: C5's frame elapsed values are 1 s + 333/777 ns, so the A21 float support rule leaves
  238-256 ns interior gaps (<= 1 us, snapped);
- screen fixtures: W1 anchor 2 and T1/T2-retry ordinal 6 carry a battery B code (W1 leaves the σ_w table,
  `W1_anchor_block: excluded:B`; the B run crosses T2's zero-capture attempt);
- the engine's raw-source manifest over the same bytes, and the structure-only crosswalk, both to the R23
  export contract (section 6a).

Series: W1 (18), C1-C8, T1-T3 (T3 has 24), plus the two zero-capture attempts: 11 counted windows, 13
attempts with W1. The PROBE plan (`support.PLANS["probes"]`) adds two hard cases kept apart because each is a
classified hold (section 6): a G1 timeout on W1 anchor 2, and C6 at a synthetic 9e9 s epoch where the float
seconds grid is 1.907 us, so its seams are 1-2 us (> 1 us).

```bash
for m in test_compare_v4 test_release_v4 test_rehearsal_v4; do
  python3.13 -B -m unittest tests.v4_release.$m; done
```

- **Tests need the pinned commits' objects.** A shallow clone skips the tests that need them.
- **Rehearsal caching.** Each plan is built once (generation, the serial two-stage engine run and the
  recompute) and cached read-only under the system temporary folder, keyed by the commits and the generator
  bytes.

- **Per-module run times** (Air, 2026-11-08, load 10-25, rehearsals cached):

  | Module | Tests | Time |
  |---|---|---|
  | `test_compare_v4` | 18 | 40 s |
  | `test_release_v4` | 12 | 24 s |
  | `test_rehearsal_v4` | 7 | about 3 min (one engine re-run for its code mutation; the probe plan cached) |

  Building a plan cold takes 4.5-7 min, almost all of it the serial engine (C-only stage, then the full run
  against the freeze); the recompute takes 5 s.

**Release runtime on the synthetic series** (306 roster rows, 262 captured members, 419 MB). These are
`release_v4.py` wall times, stages (a)-(c), at load average 10-25:

| Workers | Total | Recompute (two stages) | Comparator |
|---|---|---|---|
| 4 | 11.2 s and 10.7 s (two runs) | 7.1 s and 6.8 s | 1.7 s and 1.9 s |
| 1 | 16.6 s | 12.7 s | 1.7 s |

Stage (a) re-hashes 748 files; stage (b) confirms 262 members read the same raw bytes. The engine's own run
is not part of the release: it runs incrementally as windows land.

## 6. Findings on the synthetic series

**Final rehearsal, 2026-11-08: exact AGREE.** Engine `a2e36bc19` (engine-r23d) against recompute
`fdd02a96b`, on the full series (C3 and T2 zero-capture retries, the A37 <= 1 us seam window, the W1/B screen
fixtures, the 24-member T3): comparator exit 0, `agree`, 61 families compared, 0 expected-empty,
0 unexplained-empty, **0 unmapped** of 274,099 engine leaves. `release_v4.py` on the same custody exits 0,
`agree`.

**Probe plan: two classified holds** (`test_probe_series_holds_only_on_the_classified_findings`). Every
failing row traces to one of these two members/windows:

| # | Probe | Leaf paths (engine → recompute) | Classification |
|---|---|---|---|
| P1 | W1 anchor 2: G1 timeout stops its episode (one turn kept, the timed-out G1 last) | `/fill/W1/checks/qwen3-30b-a3b/U1/thermal_excluded_members` 0 vs `acceptance.U1.W1.30B.x1_x4_members` 1; `/fill/anchor_sigma_w/{K, W1_anchor_block, ms_*, sigma_w2_*}`: K 12 / `included` vs W 10 / `excluded:X2` | **Bug, engine** (provisional): protocol v4 lists X1-X8 with X2 = "thermal gate/hold timeout" and G1: "Timeout stops the episode (X2)"; A9 applies the union of re-derived and recorded classes. Both builds count the timeout in U1(d) (`g1_h_timeouts` 1 = 1); only the recompute re-derives X2 from the timed-out gate. If the lead rules that X2 for a G1/H timeout must come from a recorded flag, it is an interpretation (A9). The fixture has no recorded flag; production may write one. |
| P2 | C6 at a 9e9 s epoch: every interior seam 1.9-2.0 us (> 1 us) | every C6 member: engine eligible with energies equal to the recompute's own energies under full snapping (difference <= 2e-16 relative), recompute `energy_unavailable` (`pm_turn_span_uncovered`); then `eligible_m_per_pair` 56 vs 49 (REFUSE) and the C6-dependent fits, thresholds, U4/U6, carriers and balance | **Open interpretation, A21 (with A2(4)/A37)**: the restated A21 support rule (end accumulates own elapsed in float seconds, start = end - elapsed, seconds -> ns) leaves > 1 us interior gaps at this magnitude, which A2(4) excludes; the engine's placement leaves none it counts as uncovered. A second probe at 4.3e9 s showed the recompute's `round(x * 1e9)` making 1,024 ns seams where exact rounding makes 954 ns, so the seconds -> ns reading (RECOMPUTE-opus "Still open") is part of it. **No 2026-epoch impact**: at today's epoch both builds' seams are <= 512 ns and A37 snaps them; C5 agrees exactly. Raw bytes cannot place a > 1 us seam at a 2026 epoch under the A21 rule, so the 1.001 us boundary is covered by unit tests only (recompute `test_uncovered_owned_time_excludes_but_rounding_gaps_do_not`; engine-r23 hand tests). |

**Resolved since the first rehearsal** (engine `8eb7982f0` / recompute `c0d1efcae`): E1 (zero-capture raw
window crashed the engine), anchor σ_w (W1 included, raw and clamped), the honest H = 0 carrier fraction and
`level_reached_at_h0`, the carrier status word, the W1 DC residual (now: value rows for every captured
benign member, residual rows mirroring the GPU benign rows), the A2 G0/episode overlap, the A20 dropped-
sample check and meter rate index, and the export contract (section 6a). Comparator-side corrections in the
same work: A9 compares the class union only (`a9_class_components` exempt), A28 flags only for captured
members, attempt-aware member tables for retried slots, and T assignments counted from the roster.

## 6a. Export contract (R23, RUN_STATE lead ruling on the 2026-11-08 report)

The exporter writes one custody in both layouts. Both adapters hold to these rules, and so does the
synthetic writer (`tests/v4_release/common_series.py`).

| Rule | Engine side (`engine-r23d`) | Recompute side (`independent_recompute_v4.py` @ `fdd02a96b`) |
|---|---|---|
| Sensor keys are production `policy.sensors.{s_fast, s_slow}` | production `Episode` layout, unchanged | `thermal_summary` reads `s_fast`/`s_slow` |
| Anchors are exactly ordinals 1-4 (W1 included) with strictly series-unique ids `"<window_id>:<run_id>"`; bare, mixed, wrong-prefix and duplicate anchor ids refuse, and so does a prefixed non-anchor | engine window name as `window_id` (`C3:` in both C3 attempts); it strips a matching prefix for the R15 check | window RECORD id as `window_id` (`C3-z1:` for the zero-capture record); non-anchor ids repeat only across a retried slot's attempts; two captured members never share an id |
| W1 is delivered as a window record (A34) | refuses a selection-only W1 in release runs | W1 is a window in `series.json` |
| The export carries the W1 sentinel ordinals | the reference input keys `w1_sentinel_j` by `"5"`/`"17"` | the W1 record carries `sentinel_ordinals: [5, 17]`; it must equal the R15 W1 roster's sentinels, else `w1_sentinel_ordinals_mismatch` |
| A G0 that overlaps the episode is custody-invalid (A2: "G0 lies before the episode") | production attribution | `g0_overlaps_episode` → `custody_invalid` |
| KM003C rate index matches the poll period; a dropped sample inside a span makes that span's DC value unavailable, with a reason (A20) | production `span_has_drops` | `meter_stream` drops from the header `rate_idx`; `unavailable_reasons` |

**A27 token-count seal scope, applied as written.** IR A27: "**Not scored; sealed** (hash only). 'Toward
nothing' plus the v5 seal: a GPU score is as outcome-bearing for v5 as DC is. Only T sabotage is scored, and
only for known-H" (RS 226 R15: "Sabotage members in C windows count toward nothing. Their DC rows stay sealed
for v5"). The text seals the C-window sabotage MEMBER (hash only), not only its score. The recompute prints
nothing but a hash for those members, token counts included; T-window members are outside A27 and print.
The engine's `realized_counts` still lists token counts for these members. The comparator compares them by
presence (`sealed_presence`) and names the engine's rows under `a27_sealed_counts`. This is not ambiguous; it
is an engine-side cleanup that should drop those rows.

## 7. Before the real release

1. Lead rulings on P1 (G1/H-timeout X2 source) and P2 (A21 seconds -> ns and support placement at large
   magnitude; no 2026-epoch impact), and the still-open A7 H* grid.
2. The exporter writes the engine manifest, the recompute layout and the crosswalk from one custody, with the
   same raw bytes, to section 6a. Stage (b) refuses otherwise.
3. Re-run the three test modules, then run the release on the real custody into a new `$OUT`.
