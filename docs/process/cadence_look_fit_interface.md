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
  "marks": [ "reference from a redo" | "reference from an excluded leg", ... ],  # Q20; [] if none
  "meter_offsets_ns": { "header": int | null,    # KM003C header start_real_ns − start_raw_ns
                        "end": int | null }      # the span's last poll line: rt − rx (RL-167 R-20); null if none
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
  "cell_prompt_tokens": 2000 | 10000 | 19458 | null,   # the nominal cell (RL-158 Q7); null only for a roster
                                          # leg that never ran (no leg_record.json; R-21)
  "g0_role": null | "capture" | "consume",      # null = own-reference G0 (v1.0 legs, own-shaped v1.1 legs)
  "inclusion": {                          # the six rules, RL-149 §2.4 with RL-150 R7; each true = passes
    "ran_to_cap": bool,                   # rule 1 (runner)
    "g0_released": bool,                  # rule 2 (runner)
    "sidecar_coverage": bool,             # rule 3 (inclusion_34.py, stage 1)
    "km003c_clean": bool,                 # rule 4 (inclusion_34.py, stage 1)
    "not_a_contaminated_attempt": bool,   # rule 5 (runner)
    "block_power_mode": bool              # rule 6 (runner)
  },
  "turn": Turn | null                     # null for type T, a leg that never ran, or a G0 timeout (a bundle and no
                                          # turn): a type-A leg with no turn must fail at least one rule (R-21)
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

- Keys: exactly the legs that stage 1 marked `in_energy_fit` (RL-167 §3: no hp-01 energy is opened at this look).
  A missing or extra key is refused.
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
  "synthetic": bool,                      # copied from level R
  "code_sha256": {"<path>": hex64, ...},
  "numpy_version": str,
  "roster": { "spans": [Span minus marks, + "marks"], "fit_days": [ "YYYY-MM-DD", ... ] },
  "rates": { "r_p": float, "r_d": float,                 # tokens/s (Q5)
             "per_cell": {"2000": {"r_p": float | null, "r_d": float | null, "n_legs": int},
                          "10000": {...}, "19458": {...}} },  # print only; null with n_legs 0 (RL-167 row 18)
  "centring": { "tf08_c": float, "fan_rpm": float, "tv0h_excess_c": float },   # medians (Q1)
  "calibrated_range": { "tf08_c": [min, max], "fan_rpm": [min, max], "tv0h_excess_c": [min, max] },
  "onset": Onset,
  "tripwires": Tripwires,
  "counts": Counts,
  "meter_clock": { "spans": {span_id: {"form": "two_pairs" | "single_offset",
                                        "end_minus_header_s": float | null}},
                   "max_abs_s": float | null, "threshold_s": 0.1,
                   "to_research_lead": bool },  # RL-167 R-20: over 0.1 s on any span goes to the research lead
  "active_readings": {                    # RL-166b B-2, decided once here; an inactive reading's kappa column and
    "tf08_c" | "fan_rpm" | "tv0h_excess_c": {   # onset predictor are dropped everywhere
        "active": bool, "tolerance": 0.25 | 25.0 | 0.25,
        "min_count_off_day": int | null,  # min over fit days D of energy-fit legs off D with |z| > tolerance
        "threshold": 6 } },
  "onsets_before_116_s": {                # RL-166b P-4
    "by_g0_role": {"null": int, "capture": int, "consume": int},  # in-state start, observed onset < 116.0 s
    "total": int, "onset_status": "estimable" | "not_estimable",
    "to_research_lead": bool },           # not_estimable and total > 0: the 116 s cut does not stand by default
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
  "prefill_tokens": int | null, "decode_tokens": int | null,   # realized P and N; null when the leg has no turn
  "inclusion": {six bools}, "included": bool,
  "in_energy_fit": bool,                  # role fit, type A, included, valid start reading
  "hp_describe": bool,                    # role describe, type A, included; counted, never read for energy
  "not_in_fit_reason": null | "excluded" | "type_T" | "start_reading_missing" | "describe_only",
  "start": null | {                       # null for a leg with no turn (type T, never ran, no accepted attempt)
    "status": "ok" | "start_reading_missing",           # missing or stale reading (Q1)
    "state": "in_state" | "start_out_of_state" | "start_state_unobserved",
    "tf08_c": float | null, "fan_rpm": float | null, "tv0h_excess_c": float | null,
    "z": [float, float, float] | null,                  # centred: tf08, fan, tv0h_excess
    "extrapolated": bool                                # any reading outside calibrated_range
  },
  "state": null | {                       # null for a leg with no turn
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
  "n_uncensored_by_cell": {"2000": int, "10000": int, "19458": int},       # RL-166b B-3
  "left_out": {"start_out_of_state": int, "state_unobserved": int, "start_reading_missing": int},
  "predictors": ["intercept", <active readings, in the order tf08_c, fan_rpm, tv0h_excess_c>, "t_p_s"],  # B-2
  "coefficients": {name: float} | null,   # null when not_estimable
  "sigma_s": float | null,
  "converged": bool | null,               # null: not attempted (fails B-3's counts); false: B-5's test failed
  "lodo": { "per_day_rms_s": {day: float}, "rms_s": float | null,   # null: no held-out uncensored leg (RL-167 row 10)
            "heldout_censored_below_tau": int, "heldout_censored": int,
            "folds_not_estimable": [day] } | null,    # see §4.3
  "count_only_cut": { "form": "tau_hat_minus_2rms" | "fixed_116_s",
                      "offset_s": float | null, "fixed_s": 116.0 | null } }
```

### 3.3 Tripwires (Q8; stage 1 comes to the research lead if any is true)

```
{ "dev_included_below_45": {"value": int, "trips": bool},
  "days_below_4": {"value": int, "trips": bool},        # RL-166b B-7: fewer than 4 fit days
  "cell_below_10": {"value": {"2000": int, "10000": int, "19458": int}, "trips": bool},
  "start_reading_invalid_over_10pct": {"value": float, "trips": bool},
  "hp01_below_9": {"value": int | null, "trips": bool},     # included type-A hp-01 legs (RL-167 row 21)
  "any": bool }
```

### 3.4 Counts

```
{ "legs_named": int, "legs_included": int, "dev_included": int, "in_energy_fit": int, "hp_describe": int,
  "type_T": int, "by_block": {block_id: {"named": int, "included": int}},
  "by_cell": {"2000" | "10000" | "19458": int}, "by_g0_role": {"null" | "capture" | "consume": int},
  "by_day": {day: int}, "excluded_by_rule": {rule_id: int} }   # by_cell/by_g0_role/by_day count energy-fit legs;
                                                                 # the own-reference g0_role key is "null"
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
  "synthetic": bool,                      # copied from level D
  "tau_uncertainty_propagated": false,    # RL-166b: the onset's scatter is in the delta column; its coefficients'
                                          # uncertainty is not propagated
  "delta_column": "kept" | "dropped_onset_not_estimable",
  "channels": { "gpu_rail": ChannelFit, "dc_in": ChannelFit },
  "qualified_interim_half": { "statistic": "gpu_rail.lodo.hot.max_abs", "value": float | null,
                              "threshold": 0.02, "verdict": "passes" | "fails" | "not_evaluable" }
}
```

### 4.1 ChannelFit

```
{
  "columns": ["p1", "p2", "a0", "a1", "a2", <k_tf08, k_fan, k_tv0h for ACTIVE readings>, "delta"],
                                          # 5 to 9 entries; "delta" absent if dropped (B-2, B-1)
  "coefficients": {column: float},
  "covariance": [[float]],                # cluster-by-leg, column order as above
  "n_legs": int, "n_segments": int, "n_days": int,
  "lodo": {
    "hot":  { "per_day": {day: float},    # SIGNED (Σpred − Σmeas)/Σmeas over the day's hot blocks
              "counted_days": [day], "n_hot_legs_per_day": {day: int},
              "max_abs": float | null,       # over counted days
              "pooled": float | null,        # over every hot block on every day (RL-167 row 12)
              "verdict": "passes" | "fails" | "not_evaluable" },
    "leg":  { "per_day": {day: float}, "pooled": float, "rms_over_legs": float },
    "hot_rms_over_legs": float | null,    # THE "frozen holdout relative error" freeze 2 takes for SD_j (RL-167 R-14)
    "folds_delta_dropped": [day],         # see §4.3
    "no_heat": { "hot": {same as hot}, "leg": {same as leg}, "hot_rms_over_legs": float | null }
  },
  "prefix_bias": {                        # Q2 P2; unit: score SD
    "1.10":  {"prefix_len": 3724, "estimate": float | null, "ci90": [lo, hi] | null, "n_pairs": int,
              "n_days": int},             # null under 3 pairs or an SD ≤ 1e-12 J; ci90 null under 2 days
    "1.30":  {"prefix_len": 3151, ...},
    "1.374": {"prefix_len": 2981, ...}
  },
  "fold_coefficients": {day: {column: float}},   # RL-166b P-1: each LODO fold's heat-model vector (its own columns)
  "trace_coverage": {"min": float,        # cold seat 9 (PENDING in #793's schema): min over energy-fit legs of the
                     "n_legs_under_0_99": int},   # channel's per-segment covered fraction; printed, decides nothing
  "day_detail": {                         # RL-166b P-2: counted days only
    "days": {day: {"legs_with_hot_block": int, "hot_blocks": int,
                   "se_with_heat": float | null, "se_no_heat": float | null}},   # s / sqrt(legs_with_hot_block)
    "s_with_heat": float | null, "s_no_heat": float | null },   # SD of per-leg signed hot errors within days,
                                                                # pooled over counted days
  "onset_offset_residuals": {             # RL-166b P-3: held-out (pred - meas)/meas by block offset from the
    "offsets": {"-2" .. "5": {"n": int,   # leg's first hot block, legs with an observed onset
                "mean_with_heat": float | null, "rms_with_heat": float | null,
                "mean_no_heat": float | null, "rms_no_heat": float | null}},
    "rms_offsets_m2_to_p3": {"with_heat": float | null, "no_heat": float | null} },
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

### 4.3 The two fold lists (RL-167 row 7: "listed in both lists")

A leave-one-day-out fold whose onset model cannot be fitted on its training legs (fewer than 6 uncensored
onsets, or the censored-normal fit does not converge) is listed by its held-out day in both of these. Item shape:
the day string `"YYYY-MM-DD"`; each list sorted ascending, no repeats; `[]` when no fold failed.

| Field | Level | Location | Days it ranges over | Present when |
|---|---|---|---|---|
| `folds_not_estimable` | D | `onset.lodo.folds_not_estimable` | the days of energy-fit legs whose `onset_use` is `uncensored` or `censored` | `onset.status == "estimable"` (otherwise `onset.lodo` is null) |
| `folds_delta_dropped` | O | `channels.gpu_rail.lodo.folds_delta_dropped` and `channels.dc_in.lodo.folds_delta_dropped` (the two lists are equal) | the days of energy-fit legs (`counts.by_day`'s keys) | always; `[]` when `delta_column` is `dropped_onset_not_estimable` (no fold has δ to drop). Not inside `lodo.no_heat` |

A held-out day listed in `folds_not_estimable` contributes no term to the onset RMS or `per_day_rms_s`. A day in
`folds_delta_dropped` is fitted and predicted without the δ column in that fold only; it still gives hot-stretch
and leg errors. Neither list makes the look refuse. Both use the same fold rule on the same training legs, so on
every day of the onset sample the two lists agree. A day with energy-fit legs but none in the onset sample trains
on the whole onset sample, which the main fit already fitted, so it appears in neither list.

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

### 6.2 R-10 to R-21 and the twin comparison: ruled in RL-167 (Sat 14 Nov 21:22)

RL-167 §1 (R-10 to R-21) and §2 (rows 1 to 23, and §2.1) are the readings both implementations carry; read them
there. The rows that changed this code: 4 and 5 (the gap rule: only fresh-state journal readings count; first
anchor at the turn's start without a fresh-state carry-in; floored at 0), 6 (a fresh start reading with Unknown
or missing state, or a non-integer level, is `start_state_unobserved`: in the energy fit, τ̂ from the linear
predictor, out of the onset fit), 7 (a fold's onset fits with at least 6 uncensored and convergence, else that
fold drops δ and is listed in both lists; no refusal), 8 (a main fit that does not converge is `not_estimable`),
12 (`pooled` over every hot block), 14 (`n_days` always set), 16 (the marked print refits the onset on the
remaining legs under row 7's rule; a failure gives nulls), 20 (`"null"` key), 21 (hp-01 tripwire: type A), 22
(level E: energy-fit legs only), R-11's null rules, R-14's naming, R-18's refusal, R-20's print, and §2.1's
reason precedence (type T, excluded, describe-only, missing start).

---

### 6.3 RL-166b (Sat 14 Nov 21:44): the fit form

RL-166b §3 is the reading both implementations carry for these. In this code:
- **B-1:** the δ column of a segment [u, v] is the expected hot seconds σ̂·[G((v − ℓ)/σ̂) − G((u − ℓ)/σ̂)],
  G(x) = x·Φ(x) + φ(x), with ℓ the UNCLIPPED linear predictor and σ̂ the onset fit's `sigma_s`. The main fit uses the
  main onset model, each fold and the marked-spans print their own. A `start_out_of_state` leg takes v − u; σ̂ under
  1e-6 s takes the old overlap. `tau_hat_s` stays max(0, ℓ).
- **B-2:** `active_readings` (level D) decides once which start readings enter.
- **B-3:** `estimable` needs at least 12 uncensored on at least 3 days, at least 4 uncensored in each of at least two
  prompt-size cells, and B-5. **B-4:** a fold needs at least 6 uncensored, at least 2 in each of at least two cells,
  and B-5.
- **B-5:** the test is applied at the returned point of the problem scaled by column RMS (responses and censoring
  times by theirs), in Olsen's form: finite, η > 0, −H positive definite with condition number ≤ 1e10, Newton
  decrement gᵀ(−H)⁻¹g ≤ 1e-8. The Hessian is analytic.
- **B-6:** columns scaled by RMS over rows; SVD solve; rank deficient when the smallest singular value is under
  1e-10 of the largest; the covariance is formed from the SVD.
- **B-7:** `tripwires.days_below_4`.
- **P-1 to P-4:** `fold_coefficients`, `day_detail`, `onset_offset_residuals` (level O, per channel) and
  `onsets_before_116_s` (level D).

## 7. Custody mode (scripts/cadence_look_run.py)

**Stage 1 opens, per span:** `runner_receipt.json` (`started.epoch_s`, `roster`), `soak/soak_reference.json`
(`sensors_c.TV0h`). **Per leg:** `legs/<id>/leg_record.json` (`spec`, `attempts`, `result`) and
`leg_summary.json` (`span_reference`, for the marks). **Per accepted attempt's bundle**
(`legs/<id>/runtime/<result.bundle>`): `events.jsonl` (token index and stamp), `outputs/align_turns.jsonl`
(start stamp, prompt count, length of the output ids), `outputs/align_thermal.jsonl`, and the row-end stamp,
`elapsed_ns` and `thermal_pressure` of `rich_telemetry.jsonl` and `raw/powermetrics.plist`, extracted by pattern
(no line or frame of those two is parsed). **Per span's meter stream (R-20 only):** the header line, and the last
poll line's `rx` and `rt` by pattern; no sample payload is decoded. **Never:** `power_trace.csv`.

Rules 1, 2, 5 and 6 come from `leg_record.json`: `result.leg_status == "complete"` and
`result.decode_cap_reached`; `result.g0_released`; the last attempt not `contaminated`;
`result.ac_powermode` 0 (automatic) or 2 (hp-01).

**Rules 3 and 4 enter as a verdict file** produced by `inclusion_34.py` (the manifest builder's), hashed into
the stage-1 output:

```
{ "<span_id>/<leg_id>": {"sidecar_coverage": bool, "km003c_clean": bool}, ... }   # one entry per roster leg
```

**The roster** is `manifest.resolve_roster`'s list `[{span_id, block_id, role, t0_local_date}]`; a span's
directory is `<custody>/<span_id>` unless `--span-dir SPAN_ID=PATH` says otherwise.

**Stage 2 opens** each energy-fit leg's (never an hp-01 leg's) `leg_record.json` and `power_trace.csv` (through step 3's

**Cold-seat fixes (5ea1bdee9).** A leg whose bundle has no readable turn is excluded (`turn: null`) when any of
its six verdicts already fails (a G0 timeout); an included leg with no readable turn refuses. A span whose
capture leg is excluded at the look (any verdict, rules 3 and 4 included) is marked "reference from an excluded
leg" when a consumer is on its roster. `synthetic` is true only when every span's `runner_receipt.json` carries
`"synthetic": true`. Type T is `spec.leg_type == "T"` only. The roster is a JSON list only. Stage 1 checks, by
presence only, each energy-fit leg's `power_trace.csv` and its span's meter stream. Stage 2 refuses fewer than two
fit days before opening any energy file. A meter stream with no aligned samples is skipped; a segment it would
have covered refuses.

`load_gpu_trace`, the module's sha256 checked against `84a1a553…eb173`), and each span's
`hazards/meter/stream-*.jsonl` (through `joulewise.external.km003c_parse.parse`). Level E stays in memory.
