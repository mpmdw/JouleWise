# DIFFICULTY pack v2 table contract

Authority: SPEC-v2, sections 2–10 (2026-10-14), implementing D1–D8.
Standard library only. Data problems are row flags; CLIs exit zero for data
problems, and nonzero for usage errors, unreadable inputs, invalid config or
unreadable configured exclusion files. Energy is gross whole-request energy
from first prompt token in to last generated token out, including prefill and
decode, without idle subtraction. Published MATH level is a stratum, not a cause.

## Configuration

`schema_version` is `difficulty_config.v2`. `version`, `seed`, and
`bootstrap.seed` are nonempty strings. `n_per_level` is an integer >= 1.
No number-changing key has a default. A config containing `confidence` or
`energy_per_level` is rejected with the message
`replaced in v2 by descriptive_confidence/decision_confidence and sizes`.
Validation failures raise `ValueError` naming the key.

`sizes` has exactly `off` and `on`; each has exactly `bench` and `energy`;
each has exactly string keys `1` through `5`. Values are integers satisfying
`0 <= energy <= bench <= n_per_level`. Unused modes may carry zeros.
The registered design is:

| Mode | Bench, levels 1–5 | Energy, levels 1–5 | Holdout, levels 1–5 |
|---|---|---|---|
| off | 200, 200, 200, 200, 200 | 20, 20, 40, 40, 40 | 180, 180, 160, 160, 160 |
| on | 64, 64, 64, 64, 64 | 20, 20, 20, 20, 20 | 44, 44, 44, 44, 44 |

`boundaries` is a nonempty list of distinct strings (registered: rails, wall).
`configurations` is a list of objects with nonempty `model`, `mode` off/on,
positive integer `output_cap`, `status` measured/optional; model/mode identifiers
are distinct. `repo` and `revision` carry the panel model references.
The registered roster is 1.7B/off, 4B/off, 8B/off, 4B/on (measured) and 8B/on
(optional), using `qwen3-` model identifiers. Off caps are 4096; on caps 16384.
The 1.7B revision is `3b1b1768f8f8cf8351c712464f906e86c2b8269e`; other revisions
are the frozen panel pins.

`primary_comparison.a` and `.b` are distinct identifiers in the roster;
registered: qwen3-1.7b/off and qwen3-4b/off.
`descriptive_confidence` and `decision_confidence` each satisfy 0.5 < c < 1;
registered: 0.95 and 0.99. They may be equal and are never combined.
`bootstrap.replicates` is an integer >= 20; registered B = 4000.

`exclude_importer_sets` is a boolean; `exclude_item_id_files` is a list of
filenames. `exclude_flags` and `physical_exclude_flags` are lists of strings
with empty intersection. Registered exclusions are runtime_failed and,
respectively, agent_overlap, sleep, contention_above_level, idle_wait_cap.
The adapter determines the physical threshold and writes the flag; the
estimator maps names only. `contention` and `battery_assist` do not exclude
unless explicitly configured.

`loop_detector` requires 0 < `tail_fraction` <= 1, integer `min_span` >= 1,
integer `min_repeats` >= 2; registered values are 0.25, 20, 3.

## Manifest and selections

Use the existing MATH importer, eligibility rules and prompt/scorer. Exclude
its pilot and n=128 selections when configured, and all nonblank IDs in every
configured exclusion file. An unreadable exclusion file stops the build.
For each level, the remaining eligible problems are the population pool.

Let `D = "joulewise.packs.difficulty.selection.v2/" + seed`. For tag and item ID,
the order key is `sha256((D + "/" + tag + "/" + item_id).encode("utf-8")).hexdigest()`;
ascending keys, ties by item ID. `M_L` is the first n_per_level pool problems
under tag `level`. For mode off/on, bench is the first configured bench count
of `M_L` under `bench/<mode>/<L>`; energy is the first configured energy count
of that bench under `energy/<mode>/<L>`. Holdout is bench minus energy.
Short lists are taken whole: `short_level:<L>:<count>` and
`short_selection:<mode>:<role>:<L>:<count>`. Every selection and every prefix
is a seeded uniform sample. Subject balance is not asserted.

Manifest `schema_version` is `difficulty_manifest.v2`. Fields:
`pack_version`, `seed`, `selection_domain`, `source` (dataset, repo_url, commit),
`scorer_id`, `prompt_template_id`, `n_per_level`, `sizes`, `level_counts`,
`excluded_count`, `flags`, `items`, `selections`, `subject_counts`.
Items have `order`, `item_id`, `level`, `subject`, `problem`, `prompt`,
`expected_answer`, `bench_off`, `energy_off`, `bench_on`, `energy_on`.
Items are round-robin by levels 1–5 in M_L order, skipping exhausted levels.
Selections are nested `selections[mode][role][str(level)]` ordered ID lists.
Subject counts are descriptive counts in
`subject_counts[mode][bench|energy|holdout][str(level)][subject]`.

Full manifests containing problem text are written outside the repository.
The manifest CLI also writes `selections-<version>.json` beside the manifest,
containing only `schema_version`, `pack_version`, `seed`, `selection_domain`,
`sizes`, `selections`. The estimator accepts this file or the full manifest,
using only the selection fields. Targets remain the config sizes; any differing
list length is reported as `selection_size_mismatch:<mode>:<role>:<L>`.

## Generations and bench.csv

Generation JSONL fields: `model`, `mode`, `item_id`, `response_text`,
`finish_reason`, `prompt_tokens`, `generated_tokens`; optional `attempt`,
`flags`, `generated_token_ids`. Every line produces a bench row.
Stop/length/error map to succeeded/capped/runtime_failed in the existing
`score_response`. Capped answers are wrong with outcome truncated. Thinking-on
answers without the thinking close marker are malformed.

`attempt` is an integer >= 1; if absent it is one plus the number of earlier
lines for that model/mode/item, regardless of their explicit attempts. Invalid
attempts get bad_number and a blank attempt. Token counts are integers >= 0.
Incoming flags are strings in a list or semicolon-joined string; each must
match `[a-z0-9_.:-]+`. Malformed flags are dropped and bad_flag is added.
Flags are a sorted set joined by semicolons.

Scorer flags: unknown_item, unknown_config, missing_text,
unknown_finish_reason, bad_number, runtime_failed; no scorer-generated duplicate.
An unknown finish reason scores as runtime_failed but adds only
unknown_finish_reason, not runtime_failed. Incoming flags are preserved.

Loop units are valid nonnegative integer generated_token_ids when available,
otherwise response_text.split(), with loop_check_words. Use the whole generated
sequence, thinking included; tail length is ceil(T * tail_fraction). For each
min_span-unit tail window, count occurrences greedily left to right, requiring
starts at least min_span apart. Any count >= min_repeats adds repetition_loop.
A short tail never flags. Loops and cap hits remain included.

Bench columns, in order:
`model, mode, item_id, level, attempt, outcome, correct, prompt_tokens,
generated_tokens, cap_hit, flags`.
Level is from the manifest, blank for unknown items; correct/cap_hit are 0/1.

## energy.csv and parsing

Energy columns, in order:
`model, mode, level, item_id, boundary, attempt, energy_j, prompt_tokens,
generated_tokens, flags`.
Attempt is shared by rails and wall rows of one run. Energy must be finite > 0;
token counts integers >= 0; attempt integer >= 1. Level is integer 1–5,
mode off/on. CSV integers permit optional sign plus ASCII digits only
(`[+-]?[0-9]+`, surrounding whitespace ignored); Unicode digits and decimal
representations of integers are invalid.

Estimator parse flags on both tables: bad_number, bad_level, bad_mode,
unknown_config (outside roster), not_selected (ID outside the mode/role/level
selection); energy also unknown_boundary, not_in_bench, token_mismatch.
Token mismatch compares generated tokens against the first bench row for the
model/mode/item, only when both counts parsed. The latter two flags record
conditions and do not exclude by default. level_mismatch is replaced by
not_selected. Incoming flags are counted at most once per row.

Always excluded: bad_number, bad_level, bad_mode, unknown_item, unknown_config,
not_selected, unknown_boundary, duplicate; bench also missing_text.

## Attempts and variants

Bench key: model/mode/item; energy key: boundary/model/mode/item.
A row with the same key and attempt as an earlier row is duplicate. Ignore
blank attempts for ordering. Order other rows by attempt; primary-selected is
the first row without any always/configured/physical excluding flag. Every
larger attempt is duplicate in both variants. Earlier excluded attempts may be
replaced by the usable retry, including physically excluded attempts. If no
primary usable attempt exists, that key is missing in primary counts.

Each variant uses the first remaining row by attempt that carries no excluding
flag, at most one per key:

- primary: always excluded plus exclude_flags plus physical_exclude_flags.
- flagged_inclusive: always excluded plus exclude_flags.

Inclusive uses the first physically flagged attempt where primary uses its
retry. Runtime failures remain excluded under the registered config in both.
Every output has both variants. Counts mean distinct usable selected problems.
`rows_not_used` counts attributed bench and energy rows minus used rows;
`replaced_rows` counts not-used rows whose key has a used row in that variant.
Bad-level or bad-mode rows are not attributed to any cell.

## Targets and roster

Cell key: variant, boundary, model, mode, level. Config targets are n_bench,
m_energy, and n_holdout = bench − energy. Used holdout rows are used bench
rows in the selection-defined bench minus energy, even if energy rows are missing.
`complete`: all three counts meet targets; `missing`: n_bench = m_energy = 0;
otherwise `short` (complete takes precedence).
Measured roster entries are always parties. Optional entries are not_measured
if neither input table has any row naming them, flagged or not; omit them
from cells and comparisons, print their roster status. Any row activates an
optional party for all levels and boundaries.

## Estimators and bootstrap

All descriptive intervals use c_d = descriptive_confidence. Accuracy is Wilson
on all used bench rows. With p=k/n, z=NormalDist().inv_cdf((1+c_d)/2), denominator
1+z²/n, centre=(p+z²/(2n))/denominator, half=z*sqrt(p(1−p)/n+z²/(4n²))/denominator.
Print holdout accuracy, bench mean generated tokens, cap-hit and loop fractions,
and holdout mean prompt/generated tokens.

Mean energy: mean E ± t_(m−1)((1+c_d)/2)*s/sqrt(m), m >= 2.
Direct EPC: mean E / holdout accuracy. Its secondary interval is log-scale
MOVER from the t energy interval and Wilson holdout accuracy interval:
with D=ln(mean E)−ln(p), lower=exp(D−hypot(ln(mean E/E_lo),ln(p_hi/p))),
upper=exp(D+hypot(ln(E_hi/mean E),ln(p/p_lo))). Direct statuses: ok,
not_estimable_zero_correct (also no holdout), not_estimable_few_attempts (m<2),
energy_lower_nonpositive (E_lo<=0, lower=0).

Joules per generated token: R=sum E/sum G; d_i=E_i−R*G_i;
se=sqrt((sum d_i²/(m−1))/(m*(mean G)²)); R ± t_(m−1)*se.
Blank if m<2 or sum G=0; prompt energy is included.

OLS is pooled over levels per variant/boundary/configuration:
E=a+b_prompt*P+b_gen*G, centred predictors and energies. The exact integer
singularity test uses pp_N=N*sum P²−(sum P)², gg_N analogously,
pg_N=N*sum PG−sum P*sum G; singular when pp_N*gg_N−pg_N²=0.
Slopes use the centred 2×2 covariance inverse; recover a from the means.
Variance RSS/(N−3); standard errors from that variance times (XᵀX) inverse.
Coefficient intervals are estimate ± t_(N−3)*SE. Statuses: ok, few_rows (N<4),
singular. Intervals blank unless ok. Print R², R² of E on G alone with
intercept, and b_gen*mean G/mean E. Level residuals use the full-fit residuals,
mean ± t_(m_L−1)*s/sqrt(m_L), and contains_zero.

Model energy for level L is μ_L=a+b_prompt*mean P_holdout+b_gen*mean G_holdout;
model EPC=μ_L/p_holdout. Statuses: ok, fit_few_rows, fit_singular, few_attempts
(m_L<2), zero_correct, nonpositive (μ_L<=0), bootstrap_invalid (any invalid
model replicate). Print a computable point even if the interval is invalid;
model intervals only when status ok.

One CPython random.Random version-2 string-seeded stream per configuration:
`random.Random(f"{bootstrap.seed}/{variant}/{boundary}/{model}/{mode}")`.
Used energy and holdout rows are sorted by item_id within level. For every
replicate, in this exact order:

1. Levels 1–5: draw m_L energy indices by rng.randrange(m_L), skipping empty lists.
2. Levels 1–5: draw n_L holdout indices by rng.randrange(n_L), skipping empty lists.
3. Refit pooled OLS; N<4 or singular makes model invalid at every level.
4. At each nonempty energy level with a valid refit, record residual statistic
   mean E*−(a*+b_prompt*mean P_energy*+b_gen*mean G_energy*).
5. At each level with energy and holdout, record direct mean E*/p* and model
   μ*/p*; zero correct gives +inf. Nonpositive μ* makes that model replicate
   invalid at that level.

Draws do not depend on estimability. Bootstrap is stratified by level.
Point estimates use the original sample. For B values sorted ascending,
`k=max(1,floor(B*(1−c)/2+1e-9))`; bounds are x_(k), x_(B+1−k), no interpolation.
At B=4000, c=.95 selects 100/3901; c=.99 selects 20/3981. Infinite bounds print inf.

Misfit uses the descriptive percentile interval of the B residual replicates:
lo>τ or hi<−τ, τ=1e-9*max(1, pooled used mean energy). Print boot_lo_j,
boot_hi_j, misfit. No residual statistic exists for a singular refit; when any
replicate's refit is singular there are fewer than B residuals, so boot_lo_j and
boot_hi_j are blank and misfit is 0 (not assessed). The model is then
bootstrap_invalid, so the primary is direct with reason model_bootstrap_invalid.
Primary source is model if model status ok and not misfit. Otherwise direct,
if k_holdout>=1 and m>=2, with reason misfit or model_<model status>.
If neither is estimable, primary is blank with the direct non-estimable status.
Primary EPC bounds always use chosen-source bootstrap percentiles; secondary
direct columns retain MOVER. Report every misfit cell in cells and summary.

## Comparisons

Eligibility: complete cell and epc_status ok. Incomplete reasons are
`<model>/<mode>:<cell_status>` for short/missing, otherwise
`<model>/<mode>:<epc_status>`. Ineligible rivals never disappear.
Zero correct is not estimable, not infinitely expensive.
For eligible x,y, log-ratio point is ln(EPC_x/EPC_y); replicate b is
ln(EPC*_x,b)−ln(EPC*_y,b) from independent per-configuration streams, paired
by replicate index. ln(inf)=inf; inf−inf=0. Print descriptive percentiles at
c_d and decision percentiles only at c_D=decision_confidence.

Primary question compares primary_comparison.a to .b per level: resolved,
cheaper b if dec_lo>0; resolved, cheaper a if dec_hi<0; unresolved if the
interval contains zero; unresolved_incomplete if either is ineligible.
Per boundary/variant, cheaper_size_changes_with_level requires two resolved
levels with different cheaper parties; otherwise no_resolved_change.
Summary lists every level's status, cheaper, log_ratio, dec_lo, dec_hi.

Secondary compares all measured and activated optional parties. No eligible
party: none_estimable. Cheapest is lowest eligible EPC point, ties by identifier.
Each eligible rival is beaten if the decision lower bound of ln(EPC_r/EPC_c)>0.
All eligible and all rivals beaten: resolved. All eligible but some unbeaten:
unresolved, with tied rivals. Any ineligible: unresolved_incomplete, with
cheapest still printed among eligible and incomplete reasons listed. Rival
rows contain blank numbers for ineligible rivals. Secondary verdict is
crossover_resolved if two resolved levels have different cheapest;
otherwise no_resolved_crossover. Registered c_D=.99 is .05/5 for five levels.

## Output columns

Estimate CLI requires `--config --selections --bench --energy --out`; no
confidence/exclusion/bootstrap overrides. All CSVs start with variant and are
sorted by their key columns in order. Numbers use repr(float); blanks are empty;
infinities inf. Cells exist for every variant/configured boundary/party/level
1–5, including missing data. Decomposition rows exist per variant/boundary/party;
residual rows exist for levels with a fitted residual. Rivals have one row per
party other than the eligible cheapest, when there is a cheapest.

`cells.csv`:

```text
variant, boundary, model, mode, level, cell_status, n_bench_target, n_bench, k_correct, accuracy, acc_lo, acc_hi, mean_generated_tokens_bench, cap_hit_rate_bench, loop_rate_bench, n_holdout_target, n_holdout, k_holdout, holdout_accuracy, mean_prompt_tokens_holdout, mean_generated_tokens_holdout, m_energy_target, m_energy, mean_energy_j, energy_lo_j, energy_hi_j, model_energy_j, epc_model_j, epc_model_lo_j, epc_model_hi_j, epc_model_status, epc_direct_j, epc_direct_lo_j, epc_direct_hi_j, epc_direct_status, epc_j, epc_lo_j, epc_hi_j, epc_status, primary_source, primary_reason, j_per_token, jpt_lo, jpt_hi, token_mismatch_count, rows_not_used, replaced_rows
```

`decomposition.csv`:

```text
variant, boundary, model, mode, N, a_j, a_se, a_lo_j, a_hi_j, b_prompt_j_per_tok, b_prompt_se, b_prompt_lo, b_prompt_hi, b_gen_j_per_tok, b_gen_se, b_gen_lo, b_gen_hi, r2, r2_gen_only, gen_share, status
```

`level_residuals.csv`:

```text
variant, boundary, model, mode, level, m, mean_residual_j, lo_j, hi_j, contains_zero, boot_lo_j, boot_hi_j, misfit
```

`primary.csv`:

```text
variant, boundary, level, a, b, epc_a_j, epc_b_j, source_a, source_b, log_ratio, ratio, desc_lo, desc_hi, dec_lo, dec_hi, status, cheaper, reason
```

`rivals.csv`:

```text
variant, boundary, level, cheapest, rival, log_ratio, desc_lo, desc_hi, dec_lo, dec_hi, beaten, reason
```

`crossover.csv`:

```text
variant, boundary, level, cheapest, cheapest_epc_j, status, tied, incomplete
```

`summary.json` fields:

- variants: primary and flagged_inclusive; each boundary maps to primary_question
  (verdict, levels), secondary (verdict, resolved_winners), misfit_cells
  (`<model>/<mode>:<L>`).
- roster: identifier → measured, optional, or not_measured.
- targets: config sizes; descriptive_confidence; decision_confidence;
  bootstrap (replicates, seed); python_version.
- exclusions: always (common exclusions plus bench missing_text), exclude_flags,
  physical_exclude_flags.
- flag_counts: bench and energy flag → row count; selection_size_mismatch: list.
- method_note: primary pooled model with holdout token means, direct secondary,
  misfit rule and switched cells, stratified problem bootstrap/B/percentiles,
  both confidences/decisions only c_D, incomplete parties, retries, inclusive
  first-attempt line, and level as a published stratum rather than a cause.
