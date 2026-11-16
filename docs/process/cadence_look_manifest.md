# Look manifest: freeze 1 for the interim look (DRAFT, on RL-166)

Opus builder (Opus 5.5). First draft Sat 14 Nov 2026 20:28 PST; brought to RL-166 Sat 14 Nov 20:57 PST (`date`).
Branch `align/2026-11-14-look-manifest`, off `align/2026-11-14-kit-v1-1` at `9cbb365a6`. Rulings read on
`origin/audit/2026-11-10-fable`: RL-149 to RL-165 at `ce12b6924`, RL-166 at `bd090fee1`.

This document is a draft. It authorizes nothing. RL-166 ruled the first draft's twenty open questions in one
batch; RL-166a to RL-166c and RL-167 followed; the two cold seats on the combined head `5ea1bdee9` (Mythos:
ADMIT WITH FIXES; Sol: REFUSE) are answered in section 7, and the second round on `632f58fb8` (Mythos: ADMIT WITH
FIXES; Sol: REFUSE) in section 7a. The manifest `lm-interim-01` carries every value those
rulings fixed. Every file it pins is pinned, the analyst seat's two on a draft basis until the cold reviews close.
The validator refuses a committed manifest (`status: committed`) that still carries a placeholder. The form may change
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
| `docs/process/cadence/looks/lm-interim-01.stage1.schema.json` | Stage 1's output schema (no energy): level D of the analyst seat's interface (`docs/process/cadence_look_fit_interface.md` §3, PR #795), field for field. Pinned in the manifest; RL-166 adds it to freeze 1 |
| `docs/process/cadence/looks/lm-interim-01.output.schema.json` | The look's output: level O (interface §4) embedded exactly as `fit`, step 3's file as `step3`, `realized_prompt_tokens`, the decisions and the disclosure (with `holds_cleared`). No High Power table: RL-167 §3 moved it to look `lm-hp-01`. Pinned in the manifest |
| `docs/process/cadence/looks/evidence/` | Synthetic evidence the manifest's dictated sentences cite, byte-identical, hashed by the validator |
| `tests/cadence/look_minirepo.py` | Test helper: a pinned copy of every file the look runs, as a git repository whose HEAD is `origin/main`, so the entry points' pin checks and the committed-ledger gate run on real bytes and real git state |
| `joulewise/cadence_looks/schema_check.py` | A standard-library checker for the subset of JSON Schema the look's schemas use (CI has no `jsonschema`). `assemble` and `validate --output` use it. It refuses a schema keyword outside the subset rather than ignore it |
| `tests/cadence/look_fixtures.py`, `tests/cadence/test_schema_check.py` | The smallest schema-valid stage-1, fit and step 3 documents, built from the pinned schemas; keyword tests of the checker, and, where `jsonschema` is installed, its verdict equal to `jsonschema`'s on every one-edit mutant of those documents |
| `docs/process/cadence/looks/look_manifest.schema.json` | JSON Schema copy of the manifest format. The Python validator is authoritative |
| `joulewise/cadence_looks/manifest.py` | Validator: `validate_manifest`, `check_repo`, `validate_look_ledger`, `resolve_roster` |
| `joulewise/cadence_looks/step3_energy_ratios.py` | Step 3's script, byte-identical (RL-166 Q6). Any edit needs a ruling |
| `joulewise/cadence_looks/inclusion_34.py` | Rules 3 and 4, stage 1. The U1 evaluator's definitions are copied verbatim, with cites: `thermal.Coverage`, `valid_value` and `keys`, and `thermal_desk.member_record`'s pm_gap loop. Both source files are v4 strict paths, so they are copied rather than imported. Rule 4 reads only each KM003C sample line's `rt` stamp |
| `joulewise/cadence_looks/step3_roster.py` | The step 3 adapter. It loads the pinned bytes (and refuses others), rebinds `LEGS` and `ORIGINAL_EIGHT`, and calls `analyse` and `custody_check` once per prompt-size cell, 10k first. It finds a failed leg by its traceback frame. It reads the tripwire. It contains no arithmetic on energy |
| `tests/cadence/test_inclusion_34.py`, `tests/cadence/test_step3_roster.py` | Equality with the registered U1 source and results; boundary tests at every threshold; spy tests (no sample line decoded, no value key kept, no energy file opened); a stubbed step 3 module for the adapter's behaviour; the real module for the sha gate and failure attribution |
| `scripts/cadence_look_manifest.py` | CLI: `validate MANIFEST [--final] [--repo R [--kit K]...] [--span-ledger L] [--looks L] [--output OUT]`; `pin MANIFEST --repo R [--write]` (drafts only: fills the sha256 of every pinned file that exists, then the manifest's LOOKS.json row); `assemble` (one output file from the fit and step 3 files, refused unless both name the stage-1 hash) |
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
| S2 | hp-01 is counted only, in stage 1 (its inclusion verdicts and the `hp01_below_9` tripwire). Stage 2 opens no hp-01 energy; the High Power table is look `lm-hp-01`, with its own manifest | RL-149 §2.5; RL-167 §3 (superseding RL-166 Q9) |
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
| T3 | Stage 1 goes to the research lead if any of these holds: fewer than 45 development legs included; fewer than 4 days (RL-166b B-7); a cell with fewer than 10 included; more than 10 % of legs without a valid start reading; hp-01 below 9 | RL-166 Q8 |
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
| Q9 | Superseded by RL-167 §3: hp-01 counted only; its table is `lm-hp-01` | `when.describe_blocks_rule`, never_read `hp01_energy` |
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
| Reads | A forbidden block or phase; hp-01 in the fit; a waited-for development block not read; the look waiting for hp-01 or reserve-01; leg type T not in `leg_types_never`; a `never_read` list missing any of its nine ids (qualification, ctl01, fillers, v4, type_T, rejected_attempts, step3_legs, reserve_qualification, hp01_energy); any attempt other than the accepted one |
| Verbatim | Any of 31 dictated or ruled texts changed by one character (`VERBATIM_SHA256`: the stated limits, the deferred freeze-2 rules, the heat-term form, the onset's response and estimability, the hot stretch, the relative error, the qualified rule, the stage-2 holds, the nine `never_read` sentences); a dictated sentence's note that does not cite the evidence file at its sha256; with `--repo`, an evidence file that differs |
| Pins | A missing dependency pin (the DC-in decoder `km003c_parse.py` and its imports, the rest of the measured import closure, rule 3's sensor policy `r1_runtime.json`, the validator itself) |
| Removed | A `high_power_table` print (RL-167 §3) |
| Energy | Channels other than exactly GPU rail and DC-in; per-leg energy in the output |
| Fit | A missing pinned code path; a runtime other than "numpy, no scipy, `-I`"; unit not `segment`; a predictor outside the whitelist (no cell effect, nothing read inside the turn, no raw TV0h); an assumed sign; onset not measured from the start stamp, not in stage 1, or with predictors other than RL-166's four; rates outside stage 1; any fold refit other than base, heat term and onset; the step 3 file not at its path and hash; the adapter at another path |
| Inclusion | Rules not exactly 1 to 6; rules 3 and 4 not at the look or without pinned code; rule 3 without U1's number; rule 4 with the refused clause; verdicts not hashed before energy |
| Decisions | A missing decision; a threshold other than RL-166's (0.08 with fallback 0.04; 0.02; 9; 2); anything resembling Rule P. The fallback 0.04 carries `ruled_threshold` 0.08 and either the `pending` note (a draft) or `disposed_by` (the disposing ruling, RL-n); a committed manifest never carries `pending` (Mythos N10) |
| `--repo` | A hash mismatch; look code that is a frozen kit path; a kit whose `looks` is not empty; a frozen `.py` importing look code; look code reading `condition`; a bad LOOKS.json (hash, look id, or a status that disagrees with the manifest) |
| `--span-ledger` | A ledger whose manifest id or hash differs; spans that are unsealed, out of phase, not desk-final (for waited-for blocks), unknown or filed under another block; a fit roster on fewer than 3 days |

**Span ledger** (`joulewise.cadence_span_ledger.v1`), written by the lead before the look:
- `look_manifest {look_id, sha256}`;
- `spans[{span_id, block_id, phase, desk_final, energy_seal, t0_local_date, serves_phase?}]`;
- `energy_reads[{read_id, spans, cite}]`, which is the disclosure list in machine form.

**What the validator opens:** the manifest, the ledgers, kit JSON and repository source. Never a custody file.

**The committed ledger** (`manifest.committed_ledger`, Sol N1). Every gate that asks "is this committed?" reads
LOOKS.json from git, never from a path the caller names: the bytes at `HEAD` (`git show HEAD:...`), which must
equal the working file with no uncommitted change, at a `HEAD` that is an ancestor of the shared ref (the
branch's upstream, else `origin/main`; `--ledger-ref` names another). The ledger must validate. `verify_pins`
then requires the row for this look to name the manifest's sha256 at status `committed`, `stage1_committed`,
`run` or `frozen` (Mythos N5). `require_stage1_committed(repo, look_id, stage1_sha256, stage1_doc=...)` requires
`stage1_committed`, `run` or `frozen`, the row's `stage1_sha256` equal to the file's, the manifest at `HEAD` equal
to the working one, and the row's `roster_sha256` equal to the stage-1 file's `input:roster_sha256` (Mythos N7).

**What each stage records** (Sol N2, Mythos N2, N6). The stage-1 file, the fit and step 3's file each carry
`manifest_sha256`, `allow_draft`, and `code_sha256`: the sha256 of every repository source file loaded in the
process (`manifest.loaded_repo_files`; keys starting `input:` record inputs). Each entry point refuses before it
writes when a loaded repository file is unpinned or differs from its pin (`unpinned_loaded_modules`). `assemble`
requires the fit's recorded set to be exactly stage 2's pinned code (`fit_interim.py`, `cadence_look_run.py`, the
step 3 file and every `fit.dependencies` file but the stage-1-only `r1_runtime.json`), each at its pin; stage 1's
and step 3's recorded hashes to be pins; and all three to name this manifest. `--allow-draft` runs only on
synthetic input (every receipt, or the stage-1 file's flag), is recorded in every file, and a file made under it
is refused by any step run without it.

## 4. Notes on rules 3 and 4, and on the adapter

- **Rule 3's clock.** The leg's interval runs from the G0 `phase_start` to the last token event, read from
  `events.jsonl`. The powermetrics supports come from `rich_telemetry.jsonl`. Both are on the wall clock,
  as step 3 has them. Sidecar rows are judged on their `wall_ns` stamps. The registered `thermal.coverage`
  uses `monotonic_ns`, but `Coverage` counts cells on a grid anchored at the first sample, so a constant
  offset does not change the result. Network time is off for the campaign.
- **Rule 4's nominal rate** is the header's `sps`. Each sample line's `rt` stamp and sample count `n` are taken
  by pattern; no payload is decoded. The check is "Σ n ≥ 99 % of interval × sps", and the gap is measured
  between polls that carried samples, so a run of empty polls (`n` 0) covers nothing (Sol N5; the earlier
  reading, one line per `poll_s`, counted empty polls as coverage). Streams that disagree on `sps`, or lack it,
  refuse.
- **Rule 4's normal stop:** a signal (the runner stops the monitor's process group), `duration` or
  `stop file`. Not normal: `absent`, `exception`, `consecutive USB errors`. Only streams that overlap the
  leg's interval are judged.
- **Which legs a failure is charged to.** The adapter finds the failing leg from the module's own
  `analyse_leg` frame. An exception anywhere else (the cell's arithmetic, `custody_check`) puts the cell at
  `not_run` with key `(cell)`. Messages are never kept.
- **Not yet shown:** that `analyse_leg` runs on a campaign leg's real bundle layout. RL-166 left this to
  the stage-1 dry run, and the planted-truth run waits for the analyst seat's generator.

## 5. The interface with the fit (PR #795)

| Piece | Who writes it | Command |
|---|---|---|
| The roster (one JSON list) | `cadence_look_manifest.py validate` | `--span-ledger L --roster-out R.json`; its sha256 goes into LOOKS.json's `roster_sha256` |
| Rules 3 and 4 verdict file `{"<span_id>/<leg_id>": {"sidecar_coverage", "km003c_clean"}}` | `inclusion_34.py` | `python3 -I -B joulewise/cadence_looks/inclusion_34.py --manifest M --roster R --custody C --out V.json [--detail-out D.json]` |
| Level D (stage 1) | `scripts/cadence_look_run.py stage1 ... --rules-3-4 V.json` | #795 |
| Level O (stage 2) | `scripts/cadence_look_run.py stage2 --stage1 S1 --stage1-sha256 H ...` | #795 |
| Step 3's statistic (iii) and the drift tripwire (the stage-2 CLI does not compute it) | `step3_roster.py` | `python3 -I -B joulewise/cadence_looks/step3_roster.py --manifest M --stage1 S1 --stage1-sha256 H --custody C --out STEP3.json` |
| The output file the lead checks | `cadence_look_manifest.py assemble` | `--manifest M --stage1 S1 --fit FIT --step3 STEP3 --analyst-seat NAME [--hold-cleared FLAG=RL-n ...] --out OUT` |

Every entry point verifies the manifest's pins before it opens a custody file (`manifest.verify_pins`), and every
stage-2 entry point refuses unless the committed LOOKS.json names the stage-1 file's sha256 and roster
(`require_stage1_committed`; section 3). `--allow-draft` waives both, for synthetic custody only, and is recorded.
`assemble` checks the stage-1 file, the fit and step 3's file against their pinned schemas before anything else,
and the assembled output again before writing (Sol N3); `validate M --output OUT` repeats the output check.

**Run end to end on #795's synthetic custody** (an integration of this branch with #795, off any PR): all seven
generator scenarios run stage 1, stage 2, step 3 and `assemble`, and every stage-1 file and assembled output
validates against both schemas under `jsonschema` (not installed in CI). The generator now plants rules 3 and 4
(bc03018d2 on #795); the Mythos cold seat found `inclusion_34.py` agreeing with the planted verdicts on 71 of 72
legs. The stage-1 dry run on real custody remains the check of the real layout.

## 6. RL-166b (the Mythos attack on the fit form), as the manifest carries it

- **The fit (B-1 to B-7).**
  - `fit.heat_term.form` uses expected hot seconds w̃ in the δ column. RL-166's sentence that Ĥ is zero before the predicted onset is withdrawn, and the validator refuses it if it comes back.
  - `start_readings` takes B-2's activity rule; `estimation` takes B-6's scaled solve.
  - `onset.estimable_when` takes B-3, B-4 and B-5, plus the 0.30 censored-share report.
  - The days tripwire is `days_below_4`.
- **Sentences RL-166b dictates.** They sit in `fit.stated_limits`, and the validator requires each id:
  - what `yes` means, and its pass rate (0.421 for a correct model, about 4 in 10, 0.04 to 0.69 over five worlds; 0.095 with no heat term, about 1 in 10.5), and that `no` is not evidence against the term;
  - the pooled error;
  - the limit of ½T² (3 % of its 439 s value at 75 s; under about 150 s, Ĥ is the onset step alone);
  - the partial-correction share;
  - Ĥ before the onset;
  - δ's standard error;
  - the joint range of warm series turns;
  - token ratios.
  The pass-rate figures come from the re-run with B-1's column (Mythos, Sat 14 Nov 22:19 PST, 40,000 synthetic campaigns). The report is held byte-identical at `docs/process/cadence/looks/evidence/2026-11-14-mythos-passrate-rerun-REPORT.md`, and the sentence's `note` pins its sha256. The correct-model rate is inside RL-166b's 0.25 to 0.60 band, so nothing went to the research lead.
- **Rules deferred to freeze 2.** They sit in `freeze2.deferred_rules`, and the validator requires each id:
  - κ's signs;
  - the SD_j covariance term, which is the larger of the leg-clustered SE and the day-jackknife over P-1;
  - the leverage flag;
  - the hot-prefill flag.
- **RL-166c.** The partial-correction sentence is RL-166c §5's, verbatim: 0.84 to 0.96 over twelve worlds, 0.88 in the default world. Its `note` cites the re-run's evidence file. `stages.stage2.holds` names the two flags the lead holds stage 2 on, `onsets_before_116_s.to_research_lead` and `meter_clock.to_research_lead` (RL-166c §2 row 7). The fit itself does not refuse on them. `assemble` refuses while either flag is true in stage 1's file, unless `--hold-cleared FLAG=RL-n` names the clearing ruling. The output's `disclosure.holds_cleared` records those rulings.
- **The 116 s print rule.** It is decision `onsets_before_116_s`, with threshold 0. When the onset model is `not_estimable` and the count is above zero, the decision sends stage 1 to the research lead.
- **Schema fields, named here because the interface page does not name them yet.**
  - Level D: `active_readings.{tf08_c,fan_rpm,tv0h_excess_c}.{active, tolerance, min_count_off_day, threshold}`; `onset.n_uncensored_by_cell`; `onsets_before_116_s.{by_g0_role, total, onset_status, to_research_lead}`; `tripwires.days_below_4`; RL-167's `meter_clock` and `roster.spans[].meter_offsets_ns`; `onset.predictors` as a list (B-2 may drop entries); `rates.per_cell` values nullable (RL-167 row 18).
  - Level O, per channel: `fold_coefficients` (P-1); `day_detail.{days.{legs_with_hot_block, hot_blocks, se_with_heat, se_no_heat}, s_with_heat, s_no_heat}` (P-2); `onset_offset_residuals.{offsets."-2".."5".{n, mean_with_heat, rms_with_heat, mean_no_heat, rms_no_heat}, rms_offsets_m2_to_p3.{with_heat, no_heat}}` (P-3). `columns` may hold as few as 5 entries.
  - The analyst seat emits these names, or the interface page renames them and the schemas follow.

## 7. The cold seats on `5ea1bdee9`, answered on this branch

| Finding | Fix here | Test |
|---|---|---|
| Sol 1 (blinding): inclusion decodes energy values before discarding them | `read_pm_supports` takes `timestamp_s` and `elapsed_ns` by pattern; no rich-telemetry line is JSON-decoded. Meter sample and error lines were already pattern-only | energy fields written as bytes no JSON parser accepts; `json.loads` spied, never called |
| Sol 2, Mythos 12: type-T bundles opened; a legacy field overrides the selector; unpinned sensor policy | A leg with `spec.leg_type == "T"` is never opened (both verdicts false, reason printed); no other field selects; `r1_runtime.json` resolves from the module's path and is pinned and its hash recorded | open-spy on a type-T leg; a legacy `spec.type` selects nothing; a changed policy refuses the run |
| Sol 5, Mythos 5: the hp-01 table | Out of the manifest (title, describe rule, print), the output schema and `assemble` (`--hp-table` removed); `never_read` names hp-01 energy; RL-166a and RL-167 §3 cited | validator refuses the print; schema carries neither field; the option is gone |
| Sol 6: Q11 | `drift_tripwire.threshold` 0.04, `ruled_threshold` 0.08, `pending` names the research lead's disposition; `step3_roster.py` reads the threshold from the manifest (its `--threshold` flag is gone) | 0.04 and 0.08 accepted, 0.05 refused, 0.04 without the pending note refused; the applied threshold equals the manifest's |
| Sol 7, Mythos 11: verbatim texts, complete never_read, the fallback | `VERBATIM_SHA256` (22 texts); `never_read` ids, all nine required; evidence note and file hash checked | every pinned text, one character changed, refused; each id removed refused |
| Mythos 3, Sol 9: pins not enforced; DC-in decoder unpinned | `fit.dependencies` pins the measured import closure (17 files, with `km003c_parse.py`, `aggregate.py`, `desk_compress.py`, `r1_runtime.json`, the validator); `scripts/cadence_look_manifest.py` joins `fit.code`; `verify_pins` runs in `inclusion_34.py`, `step3_roster.py` and `assemble` before anything is opened; `assemble` compares every hash the fit recorded with its pin | a changed dependency, a changed adapter, a fit hash not the pin, an unpinned running file: each refused |
| Mythos 8: "committed" not checkable; no roster writer | LOOKS.json rows carry `roster_sha256`, `stage1_sha256`, `output_sha256`, `coefficients_sha256`, required by status; `require_stage1_committed`; `validate --roster-out` writes the one roster shape (a list), which `inclusion_34.py` alone accepts; `assemble` also holds on Q8's tripwires | status without its hashes refused; stage-1 hash mismatch refused in step 3 and assemble; a `{"roster": ...}` file refused; tripwire hold needs a ruling |
| Mythos 10: text | Off-state reading per R-4 (any stamp age; Unknown never cuts); r_p, r_d per R-1; n and c per R-2, R-3; `passes`/`fails`/`not_evaluable`; custody_files gains the stage-1 meter read for R-20; `realized_prompt_tokens` computed by `assemble`; span trailer counts from the detail file; this spec | verbatim pins cover the ruled texts |
| Mythos 2 (part): host-command census | The step 3 file's usage line is listed in `tests/host_command_sites.json` with its seam; the file itself is unchanged (RL-166 Q6) | `tests.test_host_command_sites` |

**For the research lead (not changed here):** Mythos 10 notes the pass-rate sentence says "0.04 to 0.69 over the
five worlds" while its evidence file has twelve worlds (down to 0.001); RL-166c §5 moved the other sentence to
twelve worlds. Mythos's Q11 reading (the 8 % cell exists and is the same quantity) differs from Sol's (not
verified); the manifest takes the ruled fallback 0.04 until the research lead disposes.

**On the fit side (#795):** Mythos 1, 4, 6, 7, 9, 13, 14, Sol 3, Sol 4 / Mythos 2 (numpy in CI, the synth census
entry), and wiring `verify_pins` and `require_stage1_committed` into `cadence_look_run.py` stage 1 and stage 2.

## 7a. The cold seats on `632f58fb8` (round 2), answered on #795's branch

The manifest-side items. The fit-side items (Mythos N1's stage-2 caller, N3, N7's `--input`/`--energy`, N8, N9;
Sol N5's stage-2 bridging) are the analyst seat's, on the same branch.

| Finding | Fix | Test |
|---|---|---|
| Sol N1, Mythos N1 (gate side): a caller-named or loose LOOKS.json satisfied the stage-1 gate | `committed_ledger` reads LOOKS.json at `HEAD` from git, requires the working file clean and `HEAD` on the shared ref, validates it (status, hashes, duplicate rows); `require_stage1_committed` takes the repository, not a ledger | `test_require_stage1_committed_reads_git` (not committed; Sol's loose ledger; committed but unpublished; wrong hash; wrong roster; duplicate row), the same cases through `assemble` and `step3_roster.py` |
| Sol N2: the fit's recorded hashes did not bind the decoder | `assemble` requires the fit's recorded code set to equal stage 2's pinned set exactly, at the pins, and every stage to name this manifest | `test_the_fit_records_exactly_the_pinned_stage` (a missing dependency hash; an extra file; the same code under another manifest) |
| Sol N3: `assemble` wrote a per-leg joule payload | Inputs and output are checked against the pinned schemas (`schema_check`) before anything is written | `test_inputs_must_pass_their_schemas` (`per_leg_joules` in the fit, joules in step 3, `energy_j` on a stage-1 leg); `test_schema_check` |
| Sol N4: a mutant that does not compile counted as killed | The harness compiles each mutant first; one that does not compile is INVALID and fails the run. `stage1_opens_power_trace` re-indented | the harness run (section 8) |
| Sol N5 (rule 4 side): empty polls counted as coverage | Rule 4 counts samples (`n`) against the header's `sps`, and measures gaps between polls with samples | `test_empty_polls_cover_nothing`, `test_sample_rate_must_agree` |
| Mythos N2: `--allow-draft` on real custody, unrecorded | Inclusion refuses `--allow-draft` unless every receipt is synthetic; step 3 and `assemble` unless the stage-1 file is; every file records `allow_draft`; without the flag, a draft-made input is refused; `validate --output` refuses a draft-made output that is not synthetic | `test_allow_draft_refuses_custody_that_is_not_synthetic`, `test_allow_draft_needs_a_synthetic_stage1`, `test_allow_draft_is_synthetic_only_and_recorded`, `test_assemble_writes_the_schema_shape` |
| Mythos N4: `look-fit` not required | Not changed here (branch protection is the lead's). Proposal in the PR report | — |
| Mythos N5: any status but `draft` ran | `verify_pins` requires `committed`, `stage1_committed`, `run` or `frozen` in the committed, validated ledger | `test_a_ledger_status_short_of_committed_is_refused` |
| Mythos N6: the dependency list could fall short | `unpinned_loaded_modules` at each entry point before it writes; stages record every loaded repository file | `test_a_loaded_module_the_manifest_does_not_pin_is_named` |
| Mythos N7 (gate side): roster hash never compared | `require_stage1_committed` compares the row's `roster_sha256` with the stage-1 file's `input:roster_sha256` | the wrong-roster cases above |
| Mythos N10: text, validator and test leftovers | The print reads "passes, fails or not_evaluable"; the step 3 method gives `--manifest M`; the nine `never_read` sentences are pinned (31 texts); a committed manifest refuses `pending` and needs `disposed_by`; a test for "does not name this manifest's sha256" | `test_dictated_texts_are_pinned_verbatim`, `test_q11_fallback_and_ruled_threshold`, `test_verify_pins` |

**Still for the research lead:** Mythos 6 (no coefficient writer or predict path; the later-look declarations in
`lm-interim-01.json` still name them), the `trace_coverage` print, Q11, and the five-world pass-rate sentence.

## 7b. RL-172a: the soak retry (the qualification pin, #794 at `6010985a3`)

RL-171 lets the runner retry a span's soak once, on a slope or a load refusal. RL-172a (F2, condition from Mythos
F3) has the look read `soak_attempts` from each receipt and print the retried soaks by refusal kind.

- **What is read** (`inclusion_34.soak_retries`, stage 1): receipt fields only. The lead ruled out log reads to
  keep the open list as tight as it was: a stderr log is a free-text channel. The fields are `soak_attempts`
  and the receipt's soak steps (`soak`, `soak.a<n>`). They are checked against each other: numbered attempts,
  every attempt but the last refused, one step per attempt, and a refused attempt's step nonzero. A mismatch
  refuses. No field, as on the v1 and v1.1 pins, is one attempt. An empty list is a span stopped before its soak.
- **The kind.** The RL-171 receipt does not record it: each attempt's `refused` text, and its step's `error`, read
  "the idle soak failed its settle or quiet check" for both. So each retry counts under "kind not recorded"
  unless a receipt field (`refusal_kind`) names the kind. None does at `6010985a3`. The research lead is told
  that the kind needs a receipt field at the next runner pin. No log and no soak file is opened.
- **The print** (`soak_retries`, level D and the output, copied by `assemble`): per span, attempts, accepted, and
  each retried attempt's kind and where it was read. In sum: spans with a retry, retried soaks by kind,
  spans accepted after a retry, and spans the soak stopped. It decides nothing.
- **Not a stop.** Whether the soak was accepted is its last soak step's rc. No look code reads the stage journal
  (`chain-stages.jsonl`). A span whose retry was accepted has its legs judged as any other span's.
- **Fit side.** The stage-1 CLI (`cadence_look_run.py`) writes `soak_retries` into level D from the same function
  (the analyst seat's part).

| Requirement | Where | Test |
|---|---|---|
| Read `soak_attempts` and the soak steps; absent is one attempt | `inclusion_34.soak_attempts` | `test_absent_field_is_one_attempt`, `test_attempts_that_disagree_with_the_steps_refuse`, `test_no_log_or_soak_file_is_opened` |
| Retried soaks by kind; "kind not recorded" unless a receipt field names it | `soak_refusal_kind`, `soak_retries`; the print, the D and output schemas, `assemble` | `test_kind_not_recorded_unless_a_receipt_field_names_it`, `test_a_soak_refused_twice_or_interrupted_stopped_the_span`, `test_soak_retries_print_is_required`, `test_assemble_writes_the_schema_shape` |
| A retried-then-accepted soak is not a stopped span | No stage-journal read; verdicts unchanged | `test_a_retried_then_accepted_soak_is_not_a_stop` |

## 7c. The cold seats on `553e4cf00` (round 3), manifest side

Both seats: ADMIT WITH FIXES, no new HIGH. The fit-side halves of these items (stage 1 and stage 2 in
`cadence_look_run.py`) are the analyst seat's.

| Finding | Fix | Test |
|---|---|---|
| Sol NEW-1, Mythos N9: nested energy passes the closed outer schemas | `step3.cells[].ii_gamma` and `.vi_slope_lnE_on_lnclock` are closed to the producer's shapes (each fixed-effects slope is `{slope, se, n_obs, n_groups, n_groups_with_2plus}`). Every map in both schemas constrains its keys (`propertyNames`, new in `schema_check.py`): days, columns, cells, roles, rules, span ids, leg keys, code paths. `assemble` and `validate --output` also require each channel's coefficient maps to carry that channel's columns only | `test_no_energy_nests_anywhere_in_the_output` (joules in `ii_gamma` and in its slope, watts in `vi`, a leg key in `coefficients` and in a fold, a dropped column; the producer's shape passes); `test_schema_check` (still equal to `jsonschema`) |
| Sol NEW-2, Mythos N3: `--ledger-ref` wired unevenly, `HEAD` accepted | `manifest.shared_ref` is the one resolver. It accepts a remote-tracking branch only, and refuses `HEAD`, a local branch, a tag, a commit or an expression. `inclusion_34.py` gains `--ledger-ref`. Every gate passes it. Outputs record what satisfied the gate (`ledger_gate`: HEAD, ref, ref commit; null under `--allow-draft`). **Detached HEAD on a campaign branch not yet on main:** run every tool with `--ledger-ref origin/<campaign-branch>`, for example the PR's base branch | `test_shared_ref_is_a_remote_tracking_branch`; step 3 refuses `HEAD`, `main`, a sha and `origin/main~0`, and runs from a detached HEAD with `--ledger-ref origin/look`; inclusion and `assemble` refuse `--ledger-ref HEAD`; the recorded gate is checked |
| Mythos N1 (step 3's half) | Under `--allow-draft`, step 3 reads each span's receipt in the stage-1 file and refuses unless every one says synthetic, before any bundle opens | `test_allow_draft_needs_a_synthetic_stage1` |
| Mythos N2 (step 3's half) | Step 3 refuses a stage-1 file made under another manifest before any energy | same test |
| Mythos N4: a docs-only change skips CI | The `changes` job counts `docs/process/cadence/looks/*` and `docs/process/cadence/kits/*` as code | `test_ci_runs_the_tests_on_a_change_to_the_look_s_frozen_files` (runs the job's own case block) |
| Mythos N5: `GIT_DIR` redirects the gate | Every git call the gate makes drops the caller's `GIT_*` variables | `test_the_gate_ignores_the_caller_s_git_environment` |
| Mythos N6: rule 4 admits a leg that stage 2 refuses | Rule 4 is the ruled rule (RL-166 Q7) and is unchanged. `inclusion_34.meter_bracket` applies stage 2's support test from the poll stamps (`tx`, `rx`, `rt`, `n`; no payload), conservatively. Its result is in inclusion's detail per leg, for stage 1's preflight (the analyst's half). An exact match would need the samples' device times, which sit inside the payload | `Stage2Bracket` (the reproduced stream ending 1 s early: rule 4 passes and is flagged; the margin edge; empty polls) |
| Mythos N8: stage 1 cannot authenticate its roster or verdict file | LOOKS.json rows carry `verdicts_sha256` beside `roster_sha256`. The lead commits both before stage 1, and they are required from `stage1_committed` on. Stage 1 calls `require_inputs_committed`. `require_stage1_committed` compares both with the stage-1 file's `input:` hashes. Inclusion's detail names both hashes, and its output line prints them | `test_stage1_inputs_are_committed_by_hash`, `test_looks_rows_record_the_hashes`, `test_require_stage1_committed_reads_git`, step 3's wrong-verdict case, inclusion's detail check |
| Sol NEW-3: exact disclosure for the fit only | `STAGE1_CODE` and `STEP3_CODE` (the measured import closures) are required exactly, at the pins, as the fit's set is | `test_every_stage_records_exactly_its_code` (missing `joulewise/schemas.py`, an extra pinned file, each stage) |
| Sol NEW-4: a step-3 threshold that contradicts the manifest | `assemble` requires `threshold_applied` to equal the manifest's `drift_tripwire.threshold` | `test_step3_threshold_is_the_manifest_s` |

**The lead's sequence at the look**, with N8:
1. `validate --span-ledger L --roster-out R`.
2. `inclusion_34.py`.
3. Commit `roster_sha256` and `verdicts_sha256` in the row.
4. Stage 1.
5. Commit `stage1_sha256` (status `stage1_committed`).
6. Stage 2, step 3 and `assemble`.

Every tool takes the same `--ledger-ref`.

## 7d. The cold seats on `d7a5202a0` (round 4), manifest side

Sol: REFUSE (its HIGH, NEW-1, is stage 2's support rule, on the fit side). Mythos: ADMIT WITH FIXES.

| Finding | Fix | Test |
|---|---|---|
| Mythos N2: the freeze commit turns the look's tests red | The tests no longer depend on the checked-in status. `draft()` and the mini repo work on a draft copy (`look_minirepo.to_draft`), and the Q11 test sets its own form. `look_minirepo.frozen_copy` applies the lead's freeze commit to a copy of the tree: status committed, Q11 disposed, and the row | `FreezeCommit`: the frozen copy passes `validate --final --repo` and runs all six look test modules green |
| Mythos N3: a second stage 1 after energy | `manifest.stage1_history` reads every commit of LOOKS.json reachable from HEAD. `require_inputs_committed` refuses once any commit names a stage-1 hash, so stage 1 runs once. `require_stage1_committed` refuses when the history names more than one (stage-1, roster, verdict) triple for the look. There is no override | `test_a_committed_stage1_is_never_replaced`: G11's redo, a changed verdict hash, stage 1 run again |
| Mythos N4, Sol NEW-2: stale bytecode outside the two-stage CLI | `inclusion_34.py`, `step3_roster.py` and `assemble` each run with a fresh, empty pycache prefix, which is removed at exit. Each refuses on `manifest.cached_bytecode`. `load_step3` executes the bytes it hashed | `StaleBytecode`: a planted, same-mtime and same-size cache entry for `manifest.py` runs unguarded (control) and never in the three tools; prefixes are cleaned up; a stale step 3 entry never runs; `cached_bytecode` names a module with a cache file |
| Sol NEW-3 (step 3's half): stage-1 defects pass the readers | `manifest.stage1_problems` holds schema, manifest, run mode and the exact code set at the pins. Step 3 calls it before any bundle, `assemble` uses it, and stage 2 can call it (the analyst's half). The exact code sets now live in manifest.py, and `schema_check.py` joins every stage's set | `test_a_stage1_defect_refuses_before_energy`: missing hash, wrong hash, unknown field |
| Sol NEW-4: an unrecognized meter prefix is JSON-decoded | Only a line positively recognized as a header or trailer is decoded: kind "h" or "t", and none of a sample line's keys. The sample pattern accepts any JSON whitespace | `test_an_unrecognized_sample_prefix_is_never_decoded` (the `"k" : "b"` spelling with SMC power, an unknown key order, and a kindless line) |
| Mythos N5: the GPU-hole switch cannot be set | The validator accepts `fit.gpu_trace_hole_refusal {enabled, max_gap_s, cite?}` and checks it; a cite is needed when enabled. The JSON-schema copy matches | `test_the_gpu_hole_switch_can_be_set` |
| Mythos N6: `ledger_gate` gaps | A record carries a gate exactly when it is not a draft; `assemble` and `validate --output` refuse either mismatch. The shared ref must belong to a configured remote, and `origin/HEAD` or a bare remote name is refused. A reproduction of a stage-1 file compares everything but `ledger_gate`, which records the run's HEAD | `test_a_ledger_gate_exactly_when_not_a_draft`, the `validate --output` case, `test_shared_ref_is_a_remote_tracking_branch` (`origin/HEAD`, `nowhere/x`) |
| Mythos N7: `shared_ref_accepts_remote_HEAD` survived | As above | as above |

## 7e. The cold seats on `246a41db6` (round 5) and RL-173, manifest side

Mythos: REFUSE (N1 HIGH). Sol: ADMIT WITH FIXES. RL-173 §E and §E.1 (research lead, Sun 15 Nov 11:58) ruled the open
items. The fit side's map is `docs/process/cadence_look_fit_interface.md` §7 "Round 5 and RL-173".

| Finding or ruling | Fix | Test |
|---|---|---|
| RL-173 E.1 items 1-2: trace holes exclude the leg in stage 1, from time fields through one reader | `joulewise/cadence_looks/time_fields.py` is the one reader (pinned in `fit.code`, required by the validator). Stage 1 excludes a development leg by rule 3 (a power_trace stretch over 2 s with no gpu_power row) or rule 4 (an interval not bracketed by decoded samples, a decoded gap over 2 s, a clock-fit excess over 2 s). The manifest's custody files, stage 1's writes and the blind statement say so: "Of the energy files, stage 1 read time stamps and sample counters only" | `test_time_fields`: the perturbation test (every power value changed, verdict file and stage-1 output byte-identical), reader equivalence with the decoder and step 3, the clauses through the CLI |
| RL-173 E.1 item 3: the backstop | `fit.gpu_trace_hole_refusal` is on at 2 s; the validator requires it for an interim look and refuses a null switch; the JSON-schema copy now needs a cite when it is on (Mythos r5 N10) | `test_the_gpu_hole_switch_can_be_set`, the schema/validator agreement test |
| RL-173 E.1 item 4; Mythos r5 N3, N5: a second stage 1 | The LOOKS.json row may carry `stage1_superseded` [{stage1_sha256, roster_sha256, verdicts_sha256, ruling, ruled_exclusions}]. A replaced commitment stands only when an entry names it with the research lead's ruling. Stage 1 runs once more only with exactly the last entry's ruled exclusions (`--ruled-exclusion`), on the replaced roster and verdict file, from a row without a stage-1 hash. A typo'd hash is corrected by an entry with no exclusions; stage 1 does not run again. The history is read over HEAD and every remote-tracking ref. `cadence_look_manifest.py row` writes the row's hashes from the files after checking them; messages print full hashes | the ledger tests in `test_look_manifest` (typo correction, ruled rerun, mismatched exclusions, a second remote branch, `row`) |
| RL-173 E: Q11 | The 8 % cell's two rows at 10,000 repetitions: 0.0280 (SE 0.0017) and 0.0231 (SE 0.0015), both at or under .035. `drift_tripwire.threshold` is 0.08, `disposed_by` RL-173, `evidence` the pinned report `evidence/2026-11-15-q11-drift-10k-REPORT.md` | the validator's Q11 cases |
| RL-173 E: the coefficient writer | `freeze2.schema` pins `lm-interim-01.coefficients.schema.json`; stage 2's `--coefficients-out` writes the file through `fit_interim.write_coefficients` and checks it against that schema | `test_predict` |
| Mythos r5 N6: the custody stage 2 reads is not bound to stage 1's | Level R carries per span the sha256 of the receipt and each leg record and a digest of the meter time fields, and per leg the digest of the trace's row stamps; stage 2 checks them before any energy opens, and records the files it read by sha256. Step 3 checks the leg records and records its files; `assemble` refuses unless the fit and step 3 read one root and the same GPU traces | the custody-binding tests in `test_look_run` and `test_look_manifest` |
| Mythos r5 N7: stage 1 never checks its own file | Stage 1 runs `manifest.stage1_problems` on its output before writing it; the stage-1 schema's block-id pattern is the validator's | `test_look_run` self-check test |
| Mythos r5 N8: a `.zst` custody file | The reader refuses a `.zst` sibling of a stream or trace: the look reads a decompressed custody copy; seal/marker verification is the lead's upstream handoff, not this CLI's check | `test_time_fields` |
| Sol r5 NEW-2: a nested `k` decides a line's kind | The reader's lexer takes the TOP-LEVEL `k` and converts only whitelisted members; no line of a stream is given to `json.loads` | `test_time_fields`, inclusion's spy tests |
| Sol r5 NEW-3: the ledger gate checked after energy | `manifest.stage1_problems` checks the gate against the run mode, so stage 2 and step 3 refuse before energy | `test_look_manifest` gate case |
| Mythos r5 N9, N10 | Tests on private temp directories; the six surviving mutants killed; the interface page and this page corrected | the mutant harness |

## 7f. The cold seats on `413697d4b` (round 6), builder round 7

Mythos: ADMIT WITH FIXES (five MED, six LOW). Sol: REFUSE (five MED, two LOW). No HIGH.

| Finding | Disposition |
|---|---|
| Mythos N1 / Sol NEW-4, NEW-5 | Census fixed at 66fa7c452; required NumPy CI and FreezeCommit now include predict and round-6 regressions |
| Mythos N2 / Sol NEW-3 | Closed evidence and freeze-2 schema shapes added; dependency-free actual-manifest checks; interim GPU backstop schema aligned |
| Mythos N3 | Research-lead ruling required: RL-173's 2 s excess line is retained; fitted excess can hide a counter step up to about 3.8 s in the synthetic review |
| Mythos N4 / Sol NEW-1 | Reruns authenticate kept D and R, compare the unchanged source projection, bind historical manifest hashes, and refuse after run/frozen/output history |
| Sol NEW-2 | All reused operational sources bound before later readers, recorded by both stages and compared at assembly; native PM timing/state is bound by a blinded projection, and energy projections remain blinded |
| Mythos N5 / Sol NEW-7 | Timestamp validation and named leg/stream field-only refusals; unknown support is stated without inventing a gap |
| Mythos N6 | Shallow history refuses; gate Git calls ignore replacement objects |
| Mythos N7 | Empty-exclusion corrections retain cumulative earlier exclusions |
| Mythos N8 | Non-admitting in-process reproduction from authenticated kept R documented in interface §7 |
| Mythos N9 | Freeze-2 source hash omits ledger position and local custody locators; retains and compares custody file identities; seal verification boundary stated |
| Mythos N10 | Full SHA-256 identities for all five Q11 scripts and both result files, retained at the original scratch location; no abbreviated-only identity remains |
| Sol NEW-6 | Canonical JSON round-trip accepts coefficient maps independently of insertion order; unique columns required |
| Mythos N11 | Stale custody/help corrected; ruled soak kind supported; named compressed-trace refusal; behavioral regressions and mutants expanded. Real-recording tests excluded by blinding. Reader/provenance policy questions listed for the research lead |

The detailed code map and non-admitting reproduction procedure are in the fit interface §7, “Round 6 fixes”.
Fresh validation results and gate limitations are recorded in the builder run report and PR #795 findings table.

## 8. Still owed

| Item | Who | Due |
|---|---|---|
| Final pins. `fit_interim.py` and `scripts/cadence_look_run.py` are pinned **on a draft basis** at #795's latest head; on this branch `validate --repo` warns that they are absent, and with #795 merged every check passes. `pin --write` re-pins after the fit-side fixes and again after the cold reviews; a change on main to any pinned dependency needs a re-pin too | Lead, after the cold reviews | Mon 18:00 |
| Q11: disposed by RL-173 (0.08, from the 10,000-repetition run); the research lead's cold pass confirms the applied threshold | Research lead | With the cold pass |
| A planted-truth run of `step3_roster.py` on the generator's bundles | Analyst seat / lead | With item 7 |
