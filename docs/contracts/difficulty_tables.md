# DIFFICULTY tables (SPEC v1.1)

The pack measures gross whole-request energy per correct answer at each published
MATH level. Accuracy and token counts come from the generation bench; energy
comes from a per-level subset. Collection and the run-bundle adapter are separate
work. These CSVs use UTF-8, a header, and LF record endings. Flags are separated
by `;`; a clean flags field is empty. Missing numbers are empty fields, floats
use `repr(float)`, and counts use `str(int)`.

## Bench: `bench.csv`

One row per input generation, in input order. Columns, in order:

| Column | Type | Meaning |
|---|---|---|
| model, mode | string | Configuration; mode is `off` or `on` |
| item_id | string | Manifest item identifier |
| level | integer 1–5 | Manifest level; blank for an unknown item |
| outcome | string | `correct`, `incorrect`, `truncated`, or `malformed` |
| correct | integer 0/1 | Whether outcome is `correct` |
| prompt_tokens, generated_tokens | integer ≥ 0 | Recorded token counts; blank for invalid values |
| cap_hit | integer 0/1 | Whether finish reason is `length` |
| flags | string | Row flags |

Generations are JSONL objects with `model`, `mode`, `item_id`, `response_text`,
`finish_reason`, `prompt_tokens`, and `generated_tokens`. Finish reasons map
`stop` to `succeeded`, `length` to `capped`, and `error` to `runtime_failed`.
The existing MATH importer scores the answer; capped answers count as truncated
and incorrect. Thinking-on answers require `</think>` before their final answer.

Scoring flags: `unknown_item`, `unknown_config`, `missing_text`,
`unknown_finish_reason`, `duplicate` (second and later attempt with the same
model, mode, item), and `bad_number` (a token count is not an integer ≥ 0).
`finish_reason=error` also adds `runtime_failed`; its outcome stays `malformed`,
correct 0. These harness failures are excluded by default. An unknown finish
reason adds only `unknown_finish_reason`, scores as runtime failure and remains usable unless
explicitly excluded. Invalid JSON generation lines become empty attempts and
receive the applicable missing-field flags; every line produces a row.

Bench rows flagged `unknown_item`, `unknown_config`, `duplicate`, `bad_number`,
`missing_text`, or a configured excluding flag are excluded from bench cells.
Invalid CSV levels or modes receive `bad_level` or `bad_mode` and are excluded.
Both programs add bench parse flags: `bad_number` for invalid correct/cap-hit
bits or token counts, `bad_level` for any level outside integer 1–5 (including
blank), `bad_mode` for modes other than `off`/`on`, and `duplicate` for repeated
(model, mode, item_id). Integer text accepts only an optional sign followed by
ASCII `[0-9]` digits; `"١"` and `"12.0"` are invalid on either input table.
Each (model, mode, level) bench cell supplies accuracy, generated-token mean and
cap-hit rate to every measured boundary.

## Energy: `energy.csv`

One row per measured attempt per boundary, with columns in this order:

| Column | Type and unit | Meaning |
|---|---|---|
| model, mode | string | Configuration; mode is `off` or `on` |
| level | integer 1–5 | Manifest level |
| item_id | string | Manifest item from the energy subset |
| boundary | string | `rails` (powermetrics CPU+GPU+ANE) or `wall` (meter) |
| energy_j | finite float > 0, J | Gross whole-request energy, prefill plus decode |
| prompt_tokens | integer ≥ 0, tokens | Prompt tokens in this attempt |
| generated_tokens | integer ≥ 0, tokens | Generated tokens in this attempt |
| flags | string | Adapter flags, such as `battery_assist` or `contention` |

Energy covers the request's first prompt token in through its last generated
token out. Idle is not subtracted. A wall value is meter energy; battery assist
is an adapter flag. v1 assumes greedy decoding and one attempt per
(model, mode, item_id, boundary). The adapter supplies boundary and configuration
identity; these tools introduce no capture or measurement validation.

Estimator-added flags:

| Flag | Condition |
|---|---|
| bad_number | Energy is not finite and positive, or a token count is not an integer ≥ 0 |
| bad_level | Level is not an integer 1–5 |
| bad_mode | Mode is neither `off` nor `on` |
| duplicate | A later row repeats (model, mode, item_id, boundary) |
| not_in_bench | No bench row has the same (model, mode, item_id) |
| level_mismatch | Energy level differs from that bench row |
| token_mismatch | Generated-token count differs from that bench row |

The join uses the first bench row for an item, including flagged bench rows;
`not_in_bench` describes absence, not exclusion. A malformed token count receives
`bad_number` without `token_mismatch`; comparison requires two parsed counts. Original adapter flags are
retained. Flag counts count each flag at most once per row.

## Exclusion and output interpretation

Energy rows flagged `bad_number`, `bad_level`, `bad_mode`, `duplicate`,
`unknown_item`, or `unknown_config` are always excluded. Config `exclude_flags`
adds exclusions. Other flagged rows remain used. Bench exclusions are described
above. `exclude_flags` defaults to `["runtime_failed"]` when absent from config
or when the estimate CLI has neither config nor `--exclude-flags`. An explicit
config list replaces that default; `--exclude-flags ""` excludes no optional
flags. The twin also defaults to `runtime_failed`. Cells exist for keys with used
energy or used bench rows, crossed with
boundaries appearing in used energy rows. With no used energy, cells are empty.
`excluded_rows` counts excluded energy rows for that exact cell; `bad_level` and
`bad_mode` rows are unplaceable and appear only in summary flag counts.
`token_mismatch_count` counts used energy rows carrying that flag. Decomposition
and residuals use exactly the same energy rows as cells.

Intervals follow the DIFFICULTY spec: Wilson accuracy, Student t mean energy,
log-scale MOVER energy per correct answer, and a ratio interval for whole-request
joules per generated token. EPC divides mean energy by holdout accuracy:
used bench rows of (model, mode, level) whose item_id appears in no energy row
with that model and mode, across every boundary, flagged or not, used or excluded.
Headline `n_bench`, `k_correct`, `accuracy`, `acc_lo`, and `acc_hi` still use all
used bench rows. `cells.csv` inserts integer `n_holdout`, `k_holdout` between
`energy_hi_j` and `epc_j`. EPC's Wilson interval uses these holdout counts, making
the accuracy and energy intervals independent. `k_holdout=0`, including an empty
holdout, leaves EPC blank with `not_estimable_zero_correct`; fewer than two
energy attempts give `not_estimable_few_attempts` when holdout correctness is nonzero.
Fewer than two energy attempts leave mean energy
and its interval blank. Level residual means use all available rows; their
intervals require two rows. `contains_zero` is blank when the interval is unavailable. OLS coefficients
and standard errors use centred prompt/generated token counts and a recovered
intercept; the fixed decomposition schema exposes standard errors rather than
coefficient interval columns. Exact point ties in the crossover choose the
lexicographically first configuration; rivals, excluding the winner, appear in
`tied` as sorted `<model>/<mode>` identifiers separated by `;`.

`summary.json` contains `boundaries` (each with `verdict` and `resolved_winners`,
keyed by level string), `flag_counts` (separate `bench` and `energy` maps),
`confidence`, and `method_note`. The note states the independent holdout rule,
the headline accuracy's use of all used bench rows,
configuration dependence, unadjusted confidence and the whole-request basis.
Published level is a stratum and licenses no causal difficulty claim. Pack
registration owns estimator adoption and the multiple-comparisons policy.

## Manifest exclusion files

Every configured `exclude_item_id_files` entry must be readable UTF-8 text
(one item id per line; blank lines ignored). A missing or unreadable entry stops
the build with a message naming the file. The manifest CLI exits 2 for this
configuration error and writes no manifest. Bad table data remains flagged and
the scoring and estimation CLIs exit 0; usage errors and unreadable inputs fail.
