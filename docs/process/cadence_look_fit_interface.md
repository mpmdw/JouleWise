# Interim-look fit: the data interface (lm-interim-01)

Analyst seat (Opus 5.5), Sat 14 Nov 2026 (from `date`). Ruling: RL-166 (Q1 to Q8, Q16, Q17, Q20), on
`origin/audit/2026-11-10-fable` at `bd090fee1`. Branch `align/2026-11-14-fit-interim`.

This page fixes **data shapes only**: what the fit consumes and what it must emit. The arithmetic is RL-166's.
Where RL-166 leaves a convention open, it is listed in section 6 as an open reading, not answered here.

Three levels, each a JSON document (UTF-8, `allow_nan=False`; every float finite; times are seconds as floats):

| Level | Document | Reads energy | Who makes it | Who reads it |
|---|---|---|---|---|
| R | `look_input` (one file) | no | production: the stage-1 reader from custody; synthetic: the generator | stage 1 |
| D | `stage1_output` (committed with its sha256) | no | stage 1 | stage 2, by hash |
| E | `segment_energy` | **yes** | production: built **in memory** by stage 2 from custody, never written; synthetic: the generator writes it | stage 2 only |
| O | `fit_output` | derived | stage 2 | the lead (schema check), then the research lead |

Units: tokens are integers; temperatures °C; fan speed rpm; energy J. "Epoch" is wall-clock UNIX seconds.

---

## 1. Level R: `look_input` (no energy)

```
{
  "schema": "joulewise.cadence_look_input.v1",
  "look_id": "lm-interim-01",
  "synthetic": bool,                      # true only for generator output
  "spans": [Span, ...],
  "legs":  [Leg, ...]                     # every leg the roster names, included or not
}
```

### 1.1 Span

```
{
  "span_id": str,                         # e.g. "dev-03-s01"; unique
  "block_id": str,                        # "dev-01".."dev-05", "hp-01", or a "reserve-01" span serving development
  "phase": "development" | "extension",   # hp-01 is "extension" (manifest reads.blocks)
  "role": "fit" | "describe",             # describe = hp-01: never in any fit (Q9, RL-149 §2.3)
  "power_mode": "automatic" | "high_power",
  "t0_epoch_s": float,                    # the span's t0
  "t0_local_date": "YYYY-MM-DD",          # the calendar day; the unit of every leave-one-out (RL-149 §2.3)
  "soak_reference_tv0h_c": float | null,  # the span's soak reference on TV0h (RL-150 R1 part 1); null = missing
  "marks": [ "reference from a redo" | "reference from an excluded leg", ... ]   # Q20; [] if none
}
```

### 1.2 Leg

One leg is one turn. Type-T legs appear (they are counted) but carry no `turn` and are never read (Q14).

```
{
  "leg_key": str,                         # "<span_id>/<leg_id>", unique over the file
  "span_id": str,
  "leg_id": str,                          # "L001".."L012" (or "H001".. on hp-01)
  "leg_type": "A" | "T",                  # T: counted, not read
  "cell_prompt_tokens": 2000 | 10000 | 19458,   # the nominal prompt-size cell (cell law, RL-158 Q7)
  "g0_role": null | "capture" | "consume",      # null = own-reference G0 (v1.0 legs, own-shaped v1.1 legs)
  "inclusion": {                          # the six rules, RL-149 §2.4 with RL-150 R7; each true = passes
    "ran_to_cap": bool,                   # rule 1 (runner)
    "g0_released": bool,                  # rule 2 (runner)
    "sidecar_coverage": bool,             # rule 3 (inclusion_34.py, stage 1)
    "km003c_clean": bool,                 # rule 4 (inclusion_34.py, stage 1)
    "not_a_contaminated_attempt": bool,   # rule 5 (runner)
    "block_power_mode": bool              # rule 6 (runner)
  },
  "turn": Turn | null                     # null for type T, and for a leg with no accepted attempt
}
```

`included` is not an input field: it is the AND of the six, computed by stage 1.

### 1.3 Turn

```
{
  "prefill_tokens": int,                  # REALIZED count from the bundle (RL-158 Q5), = P
  "decode_tokens": int,                   # N, the number of stamped decode tokens
  "turn_start_s": float,                  # epoch: the turn's start stamp
  "first_token_s": float,                 # epoch: stamp of decode token 0
  "last_token_s": float,                  # epoch: stamp of decode token N-1
  "segments": [Segment, ...],             # the prefill, then every FULL 256-token decode block, in order
  "prefix_tails": [PrefixTail, ...],      # one per prefix length in {3724, 3151, 2981} that is < N
  "journal": [JournalReading, ...],       # sorted by t_s; see the window below
  "native_pm": [NativePmRow, ...]         # sorted by t_end_s; see the window below
}
```

#### Segment

Token-index edges follow step 3's block convention (block 0 = [tok 0, tok 255]; block k >= 1 =
[tok 256k-1, tok 256k+255]), so the segments tile [turn start, stamp of token 256*n_blocks - 1].

```
{ "seg": 0, "kind": "prefill",
  "n_tokens": P,                          # prompt tokens processed
  "edge_lo": null, "edge_hi": null,       # prefill has no decode-token edges
  "tok_first": null, "tok_last": null,
  "wall_start_s": turn_start_s, "wall_end_s": first_token_s,
  "first_token_s": null }

{ "seg": k+1, "kind": "decode", "block": k,          # k = 0 .. floor(N/256)-1
  "n_tokens": 256,
  "tok_first": 256k, "tok_last": 256k+255,           # the tokens this block decodes
  "edge_lo": 0 if k == 0 else 256k-1,                # token index whose stamp opens the interval
  "edge_hi": 256k+255,                               # token index whose stamp closes it
  "wall_start_s": stamp(edge_lo), "wall_end_s": stamp(edge_hi),
  "first_token_s": stamp(256k) }                     # used for the hot-stretch test (Q3)
```

Decode tokens past the last full block (N not a multiple of 256) are in no segment.

#### PrefixTail

The short member of a prefix pair (Q2, P2) needs the decode tokens past its last full block. A prefix of
L tokens is: the prefill, the full blocks k < floor(L/256), and this tail.

```
{ "prefix_len": 3724 | 3151 | 2981,
  "kind": "prefix_tail",
  "tok_first": 256*floor(L/256), "tok_last": L-1,
  "n_tokens": L - 256*floor(L/256),
  "edge_lo": 256*floor(L/256) - 1, "edge_hi": L-1,
  "wall_start_s": stamp(edge_lo), "wall_end_s": stamp(edge_hi),
  "first_token_s": stamp(tok_first) }
```

(For the three registered lengths: 3724 = 14 blocks + 140; 3151 = 12 blocks + 79; 2981 = 11 blocks + 165.)

#### JournalReading (from `outputs/align_thermal.jsonl`, `kind == "reading"`, no `error`)

Window: every reading with `t_s` in [turn_start_s − 60, last_token_s + 5].

```
{ "t_s": float,                           # epoch of the reading's `finished.wall_ns`
  "os_level": int | null,
  "pm_state": str | null,                 # "Nominal", "Moderate", "Heavy", "Trapping", "Sleeping", "Unknown", or null
  "pm_fresh": bool,                       # started.monotonic_ns - status.pm_observed_ns <= 2 s
  "tf08_c": float | null,                 # sensor Tf08
  "fan_rpm": float | null,                # mean of the host's fan keys; null if any key is missing (R-7)
  "tv0h_c": float | null }                # sensor TV0h, raw (the excess is formed by stage 1)
```

#### NativePmRow (from `raw/powermetrics.plist` frames, paired with `rich_telemetry.jsonl` rows)

Window: rows with `t_end_s` in [turn_start_s, last_token_s]. State is read at the row's end (RL-149 §1.3 T2).

```
{ "t_end_s": float, "state": str | null }  # thermal_pressure; null when the key is absent
```

Nothing else from inside the turn is carried. In particular no clock, no power and no energy field exists at
level R.

---

## 2. Level E: `segment_energy` (energy; stage 2 only)

```
{
  "schema": "joulewise.cadence_look_energy.v1",
  "look_id": "lm-interim-01",
  "synthetic": bool,
  "input_sha256": hex64,                  # sha256 of the level-R file whose intervals these are; stage 2
                                          # refuses it unless it equals the stage-1 file's input_sha256
  "legs": {
    "<leg_key>": {
      "gpu_rail": { "segments": [float, ...],            # J, same order and length as Turn.segments
                    "prefix_tails": {"3724": float, "3151": float, "2981": float},
                    "coverage_min": float },              # min over segments of covered fraction, 0..1
      "dc_in":    { same shape }
    }, ...
  }
}
```

- Keys: exactly the legs that stage 1 marked `in_energy_fit` or `hp_describe` (section 3). A missing or extra
  key is refused.
- **gpu_rail**: step 3's convention over `[wall_start_s, wall_end_s]`, through the committed step 3 module's
  own loaders and `Trace` (Q2).
- **dc_in**: trapezoid between consecutive KM003C samples, cut at the interval's ends (Q2).
- In production this object exists only in memory inside stage 2. The synthetic generator writes it so the
  twin and the tests can read it.

---

## 3. Level D: `stage1_output` (no energy; committed, hashed)

```
{
  "schema": "joulewise.cadence_look_stage1.v1",
  "look_id": "lm-interim-01",
  "input_sha256": hex64,                  # sha256 of the level-R file bytes
  "code_sha256": {"<path>": hex64, ...},
  "numpy_version": str,
  "roster": { "spans": [Span minus marks, + "marks"], "fit_days": [ "YYYY-MM-DD", ... ] },
  "rates": { "r_p": float, "r_d": float,                 # tokens/s (Q5)
             "per_cell": {"2000": {"r_p", "r_d", "n_legs"}, "10000": {...}, "19458": {...}} },  # print only
  "centring": { "tf08_c": float, "fan_rpm": float, "tv0h_excess_c": float },   # medians (Q1)
  "calibrated_range": { "tf08_c": [min, max], "fan_rpm": [min, max], "tv0h_excess_c": [min, max] },
  "onset": Onset,
  "tripwires": Tripwires,
  "counts": Counts,
  "legs": [LegD, ...]                     # every Leg of level R, same order
}
```

### 3.1 LegD

```
{
  "leg_key": str, "span_id": str, "block_id": str, "day": "YYYY-MM-DD",
  "role": "fit" | "describe", "leg_type": "A" | "T",
  "cell_prompt_tokens": int, "g0_role": null | "capture" | "consume",
  "marks": [str, ...],                    # the span's marks
  "inclusion": {six bools}, "included": bool,
  "in_energy_fit": bool,                  # role fit, type A, included, valid start reading
  "hp_describe": bool,                    # role describe, type A, included
  "not_in_fit_reason": null | "excluded" | "type_T" | "start_reading_missing" | "describe_only",
  "start": {
    "status": "ok" | "start_reading_missing",           # missing or stale reading (Q1)
    "state": "in_state" | "start_out_of_state" | "start_state_unobserved",
    "tf08_c": float | null, "fan_rpm": float | null, "tv0h_excess_c": float | null,
    "z": [float, float, float] | null,                  # centred: tf08, fan, tv0h_excess
    "extrapolated": bool                                # any reading outside calibrated_range
  },
  "state": {
    "first_off_s": float | null,          # seconds from turn_start_s to the first off-state reading (Q4)
    "first_off_kind": str | null,         # "os_level_above_0" | "journal_pm_state_off" | "native_pm_state_off" (joined by "+")
    "unobserved_at_s": float | null,      # seconds from turn start: last fresh reading before a >2 s gap
    "censored_at_s": float | null,        # last_token_s - turn_start_s when no off-state reading
    "onset_use": "uncensored" | "censored" | "left_out_start_out_of_state" | "left_out_state_unobserved"
               | "left_out_missing_start" | "not_in_fit"
  },
  "t_p_s": float | null,                  # count-derived prefill seconds P / r_p
  "load_s": float | null,                 # count-derived turn seconds T
  "tau_hat_s": float | null,              # predicted onset (Q4); 0 for start_out_of_state; null when not_estimable
  "segments": [ { ...the level-R Segment..., "u_s": float, "v_s": float, "hot": bool } ],
  "prefix_tails": [ { ...the level-R PrefixTail..., "u_s": float, "v_s": float } ]
}
```

`u_s`, `v_s` are the count-derived segment ends (Q1). `hot` is true for a decode block in the leg's hot stretch
(Q3); false for the prefill.

### 3.2 Onset

```
{ "status": "estimable" | "not_estimable",
  "n_uncensored": int, "n_censored": int, "n_days_uncensored": int,
  "left_out": {"start_out_of_state": int, "state_unobserved": int, "start_reading_missing": int},
  "predictors": ["intercept", "tf08_c", "fan_rpm", "tv0h_excess_c", "t_p_s"],
  "coefficients": {name: float} | null,   # null when not_estimable
  "sigma_s": float | null,
  "converged": bool | null,
  "lodo": { "per_day_rms_s": {day: float}, "rms_s": float,
            "heldout_censored_below_tau": int, "heldout_censored": int, "folds_not_estimable": [day] } | null,
  "count_only_cut": { "form": "tau_hat_minus_2rms" | "fixed_116_s",
                      "offset_s": float | null, "fixed_s": 116.0 | null } }
```

### 3.3 Tripwires (Q8; stage 1 comes to the research lead if any is true)

```
{ "dev_included_below_45": {"value": int, "trips": bool},
  "days_below_3": {"value": int, "trips": bool},
  "cell_below_10": {"value": {"2000": int, "10000": int, "19458": int}, "trips": bool},
  "start_reading_invalid_over_10pct": {"value": float, "trips": bool},
  "hp01_below_9": {"value": int | null, "trips": bool},
  "any": bool }
```

### 3.4 Counts

```
{ "legs_named": int, "legs_included": int, "dev_included": int, "in_energy_fit": int, "hp_describe": int,
  "type_T": int, "by_block": {block_id: {"named", "included"}}, "by_cell": {...}, "by_g0_role": {...},
  "by_day": {day: int}, "excluded_by_rule": {rule_id: int} }
```

---

## 4. Level O: `fit_output` (what the fit must emit)

Closed at every level. **No joule or watt per leg, turn or block (Q16).** Coefficients, covariances, errors,
ratios, counts and per-leg *signed relative* residuals only. The manifest builder's
`lm-interim-01.output.schema.json` embeds this object as its fit section; the field names below are the
contract between the two.

```
{
  "schema": "joulewise.cadence_look_fit.v1",
  "look_id": "lm-interim-01",
  "stage1_sha256": hex64, "code_sha256": {path: hex64}, "numpy_version": str,
  "tau_uncertainty_propagated": false,    # Q2: stated, not computed
  "delta_column": "kept" | "dropped_onset_not_estimable",
  "channels": { "gpu_rail": ChannelFit, "dc_in": ChannelFit },
  "qualified_interim_half": { "statistic": "gpu_rail.lodo.hot.max_abs", "value": float | null,
                              "threshold": 0.02, "verdict": "passes" | "fails" | "not_evaluable" }
}
```

### 4.1 ChannelFit

```
{
  "columns": ["p1", "p2", "a0", "a1", "a2", "k_tf08", "k_fan", "k_tv0h", "delta"],   # "delta" absent if dropped
  "coefficients": {column: float},
  "covariance": [[float]],                # cluster-by-leg, column order as above
  "n_legs": int, "n_segments": int, "n_days": int,
  "lodo": {
    "hot":  { "per_day": {day: float},    # SIGNED (Σpred − Σmeas)/Σmeas over the day's hot blocks
              "counted_days": [day], "n_hot_legs_per_day": {day: int},
              "max_abs": float | null, "pooled": float | null,
              "verdict": "passes" | "fails" | "not_evaluable" },
    "leg":  { "per_day": {day: float}, "pooled": float, "rms_over_legs": float },
    "hot_rms_over_legs": float | null,    # the "frozen holdout relative error" of SD_j (Q3)
    "folds_delta_dropped": [day],         # R-12
    "no_heat": { "hot": {same as hot}, "leg": {same as leg}, "hot_rms_over_legs": float | null }
  },
  "prefix_bias": {                        # Q2 P2; unit: score SD
    "1.10":  {"prefix_len": 3724, "estimate": float, "ci90": [lo, hi], "n_pairs": int, "n_days": int},
    "1.30":  {"prefix_len": 3151, ...},
    "1.374": {"prefix_len": 2981, ...}
  },
  "residuals": {                          # Q16: signed relative, keyed by leg_key; LODO
    "leg": {leg_key: float},
    "hot_stretch": {leg_key: float | null}
  },
  "marked_sensitivity": { "marked_spans": [span_id], "n_legs_without": int,
                          "coefficients_without": {column: float} | null,
                          "lodo_hot_max_abs_without": float | null },
  "model_sha256": hex64, "qualified": "yes" | "no" | "not_run"
}
```

### 4.2 Freeze-2 coefficient file

The coefficient file of freeze 2 is the subset `{stage1.rates, stage1.centring, stage1.calibrated_range,
stage1.onset, channels.*.columns/coefficients/covariance, channels.*.lodo.hot_rms_over_legs,
qualified_interim_half}` plus the hashes. Its exact keys belong to the manifest's `freeze2` block.

---

## 5. What is refused at the boundary

The fit refuses (exits non-zero, writes nothing) when: a level-R leg lacks a required key or carries an unknown
key; a `leg_key` repeats; a span named by a leg is missing; `segments` are not prefill-then-blocks 0..n-1 in
order; wall stamps are not non-decreasing; `decode_tokens` disagrees with the segments; a journal reading is
outside its window; the stage-1 file's sha256 differs from the hash stage 2 was given; level-E keys
differ from the legs stage 1 put in the energy fit; a level-E list length differs from its segments; any value
is NaN or infinite; the level-E `input_sha256` differs from the stage-1 file's `input_sha256`; any field named `condition`, `slot`, `instruction` or `start_band` appears anywhere.

---

## 6. Readings

### 6.1 R-1 to R-9: ruled in RL-166a (Sat 14 Nov 20:49). Both implementations carry exactly this column

| # | Ruling |
|---|---|
| R-1 | r_d = Σ (N − 1) / Σ (`last_token_s` − `first_token_s`); r_p = Σ P / Σ (`first_token_s` − `turn_start_s`); over included development legs. T = P / r_p + (N − 1) / r_d |
| R-2 | n = `edge_hi` − `edge_lo` for every decode segment: 255 for block 0, 256 for k ≥ 1, the tail's own count. `n_tokens` is not read for n |
| R-3 | c = P + (`edge_lo` + 1 + `edge_hi`) / 2. Block 0: P + 128; block k ≥ 1: P + 256k + 127.5; tail: P + (`tok_first` + `tok_last`) / 2 |
| R-4 | An off-state reading: a journal reading with level above 0 (whatever its stamp's age), or a journal reading or native row whose state is present and not Nominal or `Unknown`, at a time in (`turn_start_s`, `last_token_s`]. A `state_unobserved` gap is not one. A block is hot when its `first_token_s` is at or after the first such reading |
| R-5 | Censored at `last_token_s` − `turn_start_s`, wall seconds |
| R-6 | The onset model uses the Q1 medians, not refitted per fold. T_p enters uncentred |
| R-7 | `fan_rpm` = the mean of the host's fan keys at that reading; null if any of the host's keys is missing in the reading |
| R-8 | One SD per channel and length: sample SD (ddof 1) of the LODO residual in joules at that length, over all legs in the energy fit, all folds pooled |
| R-9 | Legs with τ̂ = 0 count in the hot-stretch error and toward a day's three legs. The hot stretch is set by R-4's observed reading, never by τ̂ |

### 6.2 Further readings the analyst seat's code applies (not yet ruled; for the research lead before item 7)

| # | Point | Applied |
|---|---|---|
| R-10 | Cluster-by-leg covariance small-sample factor | CR1: G/(G − 1) · (n − 1)/(n − k), G legs, n segments, k columns |
| R-11 | Prefix bias sign and centre | residual = measured − predicted (LODO, J); bias = mean over legs of (long/SD_long − short/SD_short); 90 % interval = bias ± t(0.95, D − 1) · SD(day means)/√D, day means of the same per-leg difference |
| R-12 | A LODO fold in which the onset model is not estimable (fewer than 12 uncensored on 3 days without D) | that fold drops the δ column; the look's own status is unchanged; the fold is listed in `lodo.folds_delta_dropped` (energy) and `onset.lodo.folds_not_estimable` (onset) and gives no onset error |
| R-13 | Onset LODO RMS | pooled over all held-out uncensored legs (not a mean of per-day values); per-day values print |
| R-14 | "RMS over held-out legs" (Q3, SD_j's holdout error) | printed twice: over each leg's whole-leg relative residual (`leg.rms_over_legs`) and over each leg's hot-stretch relative residual (`hot_rms_over_legs`) |
| R-15 | Population of each stage-1 constant | rates: included type-A development legs with a turn (a missing start reading does not remove a leg from the rates); medians and calibrated ranges: legs in the energy fit (valid start reading) |
| R-16 | "Hit `state_unobserved`" (Q4) | the unobserved time is earlier than the first off-state reading, or there is no off-state reading |
| R-17 | A counted day (Q3) | at least three legs in the energy fit on that day with at least one hot block; the pooled hot value is over counted days only |
| R-18 | Signed relative errors | (Σ predicted − Σ measured) / Σ measured |
| R-19 | Censored-normal fit | Newton's method in Olsen's (β/σ, 1/σ) form, from OLS on the uncensored; ML σ (no degrees-of-freedom correction); converged when the step is under 1e-11 relative and the score under 1e-6 |
