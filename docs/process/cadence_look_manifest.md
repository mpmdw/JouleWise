# Look manifest: freeze 1 for the interim look (DRAFT, on RL-166)

Opus builder (Opus 5.5). First draft Sat 14 Nov 2026 20:28 PST; brought to RL-166 Sat 14 Nov 20:57 PST (`date`).
Branch `align/2026-11-14-look-manifest`, off `align/2026-11-14-kit-v1-1` at `9cbb365a6`. Rulings read on
`origin/audit/2026-11-10-fable`: RL-149 to RL-165 at `ce12b6924`, RL-166 at `bd090fee1`.

This document is a draft. It authorizes nothing. RL-166 ruled the first draft's twenty open questions in one
batch. The manifest `lm-interim-01` now carries every value RL-166 fixed. The only items left open are the
sha256 hashes of code that does not exist yet (RL-166 §2 item 3), and each one is written `PENDING:CODE`.
The validator refuses a committed manifest (`status: committed`) that still carries one. The form may change
until the manifest is committed (RL-166 §2 item 11, Tue 06:00). After that, any change needs a ruling and a
new manifest id.

**Blind status.** No campaign, v4 or rehearsal energy, power, meter, journal or custody file was opened for this
work. What I read:
- the decision log, the kit, queue and ledger JSON, and the cadence code on the branch;
- the step 3 script as code, which is committed here byte-identical (sha256 `84a1a553…eb173`);
- step 4's synthetic drift note, for Q11. It is simulation output, not a measurement.

The tests build synthetic inputs only.

## Files

| File | What |
|---|---|
| `docs/process/cadence/looks/lm-interim-01.json` | The draft manifest (`status: draft`) |
| `docs/process/cadence/looks/LOOKS.json` | The look ledger (RL-166 Q18): look id, manifest path, sha256, status. The block ledger is not changed |
| `docs/process/cadence/looks/lm-interim-01.stage1.schema.json` | Stage 1's output schema (no energy), pinned in the manifest. RL-166 adds it to freeze 1 |
| `docs/process/cadence/looks/lm-interim-01.output.schema.json` | Stage 2's output schema, pinned in the manifest |
| `docs/process/cadence/looks/look_manifest.schema.json` | JSON Schema copy of the manifest format. The Python validator is authoritative |
| `joulewise/cadence_looks/manifest.py` | Validator: `validate_manifest`, `check_repo`, `validate_look_ledger`, `resolve_roster` |
| `joulewise/cadence_looks/step3_energy_ratios.py` | Step 3's script, byte-identical (RL-166 Q6). Any edit needs a ruling |
| `joulewise/cadence_looks/inclusion_34.py` | Rules 3 and 4, stage 1. The U1 evaluator's definitions are copied verbatim, with cites: `thermal.Coverage`, `valid_value` and `keys`, and `thermal_desk.member_record`'s pm_gap loop. Both source files are v4 strict paths, so they are copied rather than imported. Rule 4 reads only each KM003C sample line's `rt` stamp |
| `joulewise/cadence_looks/step3_roster.py` | The step 3 adapter. It loads the pinned bytes (and refuses others), rebinds `LEGS` and `ORIGINAL_EIGHT`, and calls `analyse` and `custody_check` once per prompt-size cell, 10k first. It finds a failed leg by its traceback frame. It reads the tripwire. It contains no arithmetic on energy |
| `tests/cadence/test_inclusion_34.py`, `tests/cadence/test_step3_roster.py` | Equality with the registered U1 source and results; boundary tests at every threshold; spy tests (no sample line decoded, no value key kept, no energy file opened); a stubbed step 3 module for the adapter's behaviour; the real module for the sha gate and failure attribution |
| `scripts/cadence_look_manifest.py` | CLI: `validate MANIFEST [--final] [--repo R [--kit K]...] [--span-ledger L] [--looks L]`; `pin MANIFEST --repo R [--write]` (drafts only: fills the sha256 of every pinned file that exists, then the manifest's LOOKS.json row) |
| `tests/cadence/test_look_manifest.py` | Synthetic tests, including a spy test showing that no custody file is opened |

**Where the look code lives.** It is in `joulewise/cadence_looks/`. RL-150 R4 requires two things: adding the
manifest changes no leg kit's frozen paths, and the runner and the leg runtime never import look code. The
first draft said "every file under `joulewise/cadence/` is a frozen path". **That is wrong.**
`joulewise/cadence/blocks.py` is on no kit's frozen-path list (RL-166 "Checked myself"). The other files in
that package are frozen paths of the v1.1 kits. The look code sits in its own package so that it never comes
near them. `check_repo` refuses any look code path that is some kit's frozen path, and any frozen `.py` that
imports look code.

## 1. What the rulings require of the look manifest

The rows are the first draft's, corrected by RL-166 where it amends them.

### 1.1 Home, timing, review

| # | Requirement | Cite |
|---|---|---|
| H1 | Freeze 1 lives in a look manifest, a file of its own beside the kits. Leg kits keep `looks: []` | RL-150 R4 |
| H2 | Contents: the look id; the blocks read; the fit code paths and hashes; the model family and predictor list; the code for rules 3 and 4; the output schema. RL-166 adds the stage-1 schema | RL-150 R4; RL-166 Amends |
| H3 | Committed before any development energy is read. **The pointer is the look ledger `LOOKS.json`, not a BLOCK-QUEUE field.** The span ledger carries the same hash | RL-150 R4; RL-166 Q18 |
| H4 | No leg kit's frozen paths change. The runner and the leg runtime never import look code | RL-150 R4 |
| H5 | No look code reads `condition` | RL-150 R6 |
| H6 | Seats. The Opus analyst seat writes `fit_interim.py` and the CLI, and runs the look. A Sol twin writes the same arithmetic blind. Mythos is the cold seat. The manifest builder writes rules 3/4 and the step 3 adapter. Paper-bound | RL-150 R4; RL-166 Q1 |
| H7 | Order and dates: RL-166 §2 items 1 to 13. This file and the validator are due Sun 12:00; rules 3/4 and the adapter Sun 18:00; the commit Tue 06:00 | RL-166 §2 |

### 1.2 What the look opens

| # | Requirement | Cite |
|---|---|---|
| S1 | Development legs dev-01 to dev-05; the look follows dev-05 | RL-149 §2.6; RL-155 §3.3 |
| S2 | hp-01 is described only and never in the fit. **Freeze 2 does not wait for it.** If hp-01 is not desk-final at stage 1, its table runs later with the same code, as its own disclosed read | RL-149 §2.5; RL-166 Q9 |
| S3 | Reserve legs serving development enter in their own cell and on their own day, if they are desk-final at stage 1. The look does not wait for them | RL-149 §2.4; RL-166 Q13 |
| S4 | **Type-T legs are not read at this look at all** (in `never_read`; `leg_types_never` includes T) | RL-166 Q14 |
| S5 | Never read: qualification, ctl-01 (CPU and package prints belong to its look), F0/F2/F3 and Part C, W1/C/T/v4, rejected attempts, step 3's nine legs | RL-149 §2.6; RL-165 §8.1; RL-166 Q17, Q19 |
| S6 | A leg's day is its span's t0 date. Leave-one-day-out everywhere; at least 3 days | RL-149 §2.3; RL-155a §1.2 |
| S7 | One verified custody copy by the offload tooling; the look runs on the Air | RL-149 §2.9 item 5 |

### 1.3 Two stages

| # | Requirement | Cite |
|---|---|---|
| T1 | **Stage 1 opens inclusion and journal files only.** It writes: the six verdicts per leg, the roster, the day map, the rates, the start medians and calibrated ranges, and the onset fit with its error | RL-166 Q8 |
| T2 | Stage 1's output is committed with its sha256 before stage 2 opens a file. Stage 2 takes it by that hash as its only roster | RL-166 Q8 |
| T3 | Stage 1 goes to the research lead if any of these holds: fewer than 45 development legs included; fewer than 3 days; a cell with fewer than 10 included; more than 10 % of legs without a valid start reading; hp-01 below 9 | RL-166 Q8 |
| T4 | Stage 2 finishes within 20 min at 72 legs on the Air | RL-166 §2 |
| T5 | Stage 1 runs as a dry run on dev-01 to dev-04 after the commit. Counts go to the lead | RL-166 §2 item 12; Q15 |

### 1.4 Energy

| # | Requirement | Cite |
|---|---|---|
| E1 | **GPU rail and DC-in only** | RL-166 Q17 |
| E2 | GPU rail: through the committed step 3 module's loaders and `Trace`. DC-in: the trapezoid between consecutive KM003C samples, cut at the segment's ends | RL-166 Q2 |
| E3 | No joule or watt per leg, turn or block in the output. Per-leg signed relative residuals keyed by leg id are allowed | RL-166 Q16 |

### 1.5 The fit (RL-166 Q1, Q2, Q4, Q5)

| # | Requirement | Cite |
|---|---|---|
| F1 | The unit is the segment: the prefill, then each full 256-token decode block (step 3's convention) | RL-166 Q1 |
| F2 | Count clock: T_p = P/r_p; token m at T_p + m/r_d. A segment is [u, v], with d = v − u and midpoint m | RL-166 Q1 |
| F3 | Start readings z: Tf08, fan rpm, and TV0h less the soak reference. Each is taken under RL-149 §1.3's start rule and centred on the development median (a stage-1 constant) | RL-166 Q1; RL-150 R1 |
| F4 | Heat term: d·m·(κ·z) + δ·w, where w is the part at or after τ̂. Per turn: Ĥ = ½T²(κ·z) + δ·max(0, T − τ̂). No sign is assumed. **No cell effect** | RL-166 Q1 |
| F5 | Count-only base, fitted jointly and never exported as Ĥ: p1·P + p2·P²; a0·n + a1·n·c + a2·n·P | RL-166 Q2 |
| F6 | OLS per channel, 9 parameters (8 without δ), covariance clustered by leg. τ̂'s uncertainty is not propagated. Freeze 2 takes the fit on all included development legs | RL-166 Q2 |
| F7 | Missing or stale start reading: the leg is out of the fit and counted. Out-of-state start: τ̂ = 0. Onset `not_estimable`: δ is dropped | RL-166 Q1 |
| F8 | Rates r_p and r_d come from token stamps in stage 1 and are frozen in freeze 2. Per-cell rates are printed and used nowhere | RL-166 Q5 |
| F9 | **Onset: seconds from the turn's start stamp** (not the first token) to the first off-state reading. Predictors: the three centred start readings and T_p. Censored-normal ML, right-censored at the last token; τ̂ = max(0, linear predictor). Estimable with at least 12 uncensored on at least 3 days; otherwise the count-only cut stays at 116 s. Error: the LODO RMS over held-out uncensored legs. Cut: τ̂ − 2·error. Fitted in stage 1 | RL-166 Q4 |
| F10 | Python standard library plus numpy, no scipy, run with `-I`; the numpy version is printed | RL-166 Q1 |

### 1.6 Inclusion

| # | Requirement | Cite |
|---|---|---|
| I1 | Rules 1 to 6 (rule 5 amended). Rules 3 and 4 are judged at the look, in stage 1, by pinned code (`inclusion_34.py`) | RL-149 §2.4; RL-150 R7, R9; RL-166 Q7 |
| I2 | Interval for rules 3 and 4: from G0's start to the last stamped token | RL-166 Q7 |
| I3 | Rule 3: sidecar coverage of at least 99 % with no gap over 2 s; powermetrics gaps at most **max(1 s, 5 periods)** (U1, `pilot_protocol_v4.md:451`), using the registered U1 evaluator's own definitions | RL-166 Q7 |
| I4 | Rule 4: header and trailer present with a normal stop reason; coverage of at least 99 % of the header's nominal rate and no gap over 2 s inside the leg's interval; timestamps only. **The "trailer counts zero" clause is refused.** The trailer counts print and decide nothing | RL-166 Q7 |
| I5 | Inclusion reads no energy; its verdicts are hashed before stage 2 | RL-157 §4; RL-166 Q8 |

### 1.7 Prints and decisions

| # | Requirement | Cite |
|---|---|---|
| P1 | Hot stretch: the full decode blocks from the first off-state reading onward. Relative error for day D: \|Σpred − Σmeas\|/Σmeas over D's hot blocks, with the base, heat term and onset model fitted without D. Rates and medians are not refitted | RL-166 Q3 |
| P2 | Also printed: the per-day signed error, the pooled error, the holdout RMS (SD_j), and all of these without the heat columns | RL-166 Q3 |
| P3 | `qualified`, interim half: the maximum over counted days (each with at least 3 included legs that have a hot stretch), GPU rail, ≤ 0.02. Fewer than 3 counted days gives `not_evaluable`, which counts as no | RL-151 §2.1; RL-166 Q3 |
| P4 | Prefix bias: the long leg is the whole leg; the short is its prefix of 3,724, 3,151 or 2,981 tokens. Residuals are LODO, each divided by its own length's SD. The statistic is the mean paired difference, with a 90 % t interval on day means | RL-166 Q2 |
| P5 | Step 3 (iii), one call per prompt-size cell, 10k first. The tripwire reads the largest `drift_fraction_linear` over cells where γ is estimable. **Threshold 0.08**, or 0.04 if the cold seat's Q11 check fails | RL-151 §1.3; RL-166 Q6, Q11 |
| P6 | With/without marked spans, both marks in one print | RL-161 §4; RL-166 Q20 |
| P7 | No extension rule | RL-166 Q12 |
| P8 | The qualification prints are declared here (`later_looks`). `lm-qual-01` is committed before any qualification energy is opened. Its scorer is `fit_interim.py`'s predict path at this hash | RL-166 Q10 |

### 1.8 Freezes

| # | Requirement | Cite |
|---|---|---|
| Z1 | Freeze 1: this manifest, its code hashes, the stage-1 schema and the output schema, entered in LOOKS.json, before any development energy is read | RL-149 §2.6; RL-150 R4; RL-166 Amends |
| Z2 | Freeze 2: the base and heat parameters with covariance, the holdout RMS, the rates, the medians and ranges, the onset model and cut, the interim half of `qualified`, and the hashes and numpy version. Never refitted on qualification legs | RL-149 §2.6; RL-166 Q2 to Q5 |
| Z3 | Freeze 2 comes before any qualification energy, any qualification leg, the phase boundary, and the release run's inputs | RL-149 §2.6, §2.8; RL-165 §8.1 |

## 2. RL-166's rulings, and where each sits

| Q | RL-166 | In the manifest |
|---|---|---|
| Q1 | Seats; code paths; segment ramp plus onset step; no cell effect | `fit.authors`, `fit.code`, `fit.heat_term` |
| Q2 | Segment energy; joint count-only base; OLS; clustered covariance; prefix bias | `fit.heat_term`, `fit.prefix_bias`, `energy.channels` |
| Q3 | Hot stretch, relative error, `qualified` rule, extra prints | `fit.validation`, prints, decision `qualified_interim_half` |
| Q4 | Onset from the turn's start stamp, censored ML, in stage 1 | `fit.onset` |
| Q5 | Rates from stage 1 | `fit.rates` |
| Q6 | Step 3 byte-identical; adapter; per cell | `fit.step3`, decisions `drift_tripwire`, `step3_cell_not_run` |
| Q7 | Rules 3 and 4 | `inclusion.rules`, `inclusion.interval` |
| Q8 | Two stages and the five tripwires | `stages`, decision `stage1_tripwires` |
| Q9 | hp-01 later if not ready | `when.describe_blocks_rule`, hp-01 `desk_final_if_any` |
| Q10 | Qualification prints declared here | `later_looks` |
| Q11 | 0.08, with a 0.04 fallback | decision `drift_tripwire` |
| Q12 | No extension rule | decision `extension_rule` |
| Q13 | Reserve legs if desk-final | reserve-01 block, `desk_final_if_any` |
| Q14 | Type T not read | `reads.leg_types_never`, `never_read` |
| Q15 | Synthetic review, then stage-1 dry run | `custody.pre_run_check`, `stages.stage1.dry_run` |
| Q16 | No joules; relative residuals allowed | `energy`, print `per_leg_relative_residuals` |
| Q17 | GPU rail and DC-in only | `energy.channels`, `energy.not_read` |
| Q18 | LOOKS.json; no BLOCK-QUEUE change | `freeze1.ledger_pointer`, LOOKS.json |
| Q19 | Step 3's legs stay out | `never_read` |
| Q20 | Both marks | `fit.sensitivity`, print `marked_span_sensitivity` |

## 3. The validator

| Check | Refuses |
|---|---|
| Structure | A missing or unknown key at any level; a missing cite. `PENDING:CODE` anywhere but a pinned sha256; `PENDING:Qn` without that open question. In a committed manifest: any placeholder or open question; two different hashes for one path |
| Stages | Stage 1 opening energy, or any inclusion- or journal-stage file that carries energy; stage 1 not committed first; stage 2 over 1,200 s; a tripwire threshold other than RL-166's |
| Reads | A forbidden block or phase; hp-01 in the fit; a waited-for development block not read; the look waiting for hp-01 or reserve-01; leg type T not in `leg_types_never`, or no type-T line in `never_read`; any attempt other than the accepted one |
| Energy | Channels other than exactly GPU rail and DC-in; per-leg energy in the output |
| Fit | A missing pinned code path; a runtime other than "numpy, no scipy, `-I`"; unit not `segment`; a predictor outside the whitelist (no cell effect, nothing read inside the turn, no raw TV0h); an assumed sign; onset not measured from the start stamp, not in stage 1, or with predictors other than RL-166's four; rates outside stage 1; any fold refit other than base, heat term and onset; the step 3 file not at its path and hash; the adapter at another path |
| Inclusion | Rules not exactly 1 to 6; rules 3 and 4 not at the look or without pinned code; rule 3 without U1's number; rule 4 with the refused clause; verdicts not hashed before energy |
| Decisions | A missing decision; a threshold other than RL-166's (0.08 with fallback 0.04; 0.02; 9; 2); anything resembling Rule P |
| `--repo` | A hash mismatch; look code that is a frozen kit path; a kit whose `looks` is not empty; a frozen `.py` importing look code; look code reading `condition`; a bad LOOKS.json (hash, look id, or a status that disagrees with the manifest) |
| `--span-ledger` | A ledger whose manifest id or hash differs; spans that are unsealed, out of phase, not desk-final (for waited-for blocks), unknown or filed under another block; a fit roster on fewer than 3 days |

**Span ledger** (`joulewise.cadence_span_ledger.v1`), written by the lead before the look:
- `look_manifest {look_id, sha256}`;
- `spans[{span_id, block_id, phase, desk_final, energy_seal, t0_local_date, serves_phase?}]`;
- `energy_reads[{read_id, spans, cite}]`, which is the disclosure list in machine form.

**What the validator opens:** the manifest, the ledgers, kit JSON and repository source. Never a custody file.

## 4. Notes on rules 3 and 4, and on the adapter

- **Rule 3's clock.** The leg's interval runs from the G0 `phase_start` to the last token event, read from
  `events.jsonl`. The powermetrics supports come from `rich_telemetry.jsonl`. Both are on the wall clock,
  as step 3 has them. Sidecar rows are judged on their `wall_ns` stamps. The registered `thermal.coverage`
  uses `monotonic_ns`, but `Coverage` counts cells on a grid anchored at the first sample, so a constant
  offset does not change the result. Network time is off for the campaign.
- **Rule 4's nominal rate** is the header's `poll_s`: one sample line per poll, empty polls included. The
  check is "sample lines ≥ 99 % of interval / poll_s". The header's `sps` (samples per second inside a poll)
  would need each line's `n`, which is not a stamp. This is a reading of "the header's nominal rate", for
  the cold seat.
- **Rule 4's normal stop:** a signal (the runner stops the monitor's process group), `duration` or
  `stop file`. Not normal: `absent`, `exception`, `consecutive USB errors`. Only streams that overlap the
  leg's interval are judged.
- **Which legs a failure is charged to.** The adapter finds the failing leg from the module's own
  `analyse_leg` frame. An exception anywhere else (the cell's arithmetic, `custody_check`) puts the cell at
  `not_run` with key `(cell)`. Messages are never kept.
- **Not yet shown:** that `analyse_leg` runs on a campaign leg's real bundle layout. RL-166 left this to
  the stage-1 dry run, and the planted-truth run waits for the analyst seat's generator.

## 5. Still owed

| Item | Who | Due |
|---|---|---|
| `fit_interim.py`, `scripts/cadence_look_run.py` and the synthetic generator. Their two sha256 are the only `PENDING:CODE` left; `pin --write` fills them | Analyst seat | Sun 22:00 |
| A planted-truth run of `step3_roster.py` on the generator's bundles | Analyst seat / lead | With item 7 |
| Q11's check of the step 4 note | Cold seat | Mon 14:00 |
| RL-166a, if the design attack changes the form | Research lead | Sun 13:00 |
