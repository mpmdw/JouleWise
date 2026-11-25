# Look manifest: freeze 1 for the interim look (DRAFT, on RL-166)

Opus builder (Opus 5.5). First draft Sat 14 Nov 2026 20:28 PST; brought to RL-166 Sat 14 Nov 20:57 PST (`date`).
Branch `align/2026-11-14-look-manifest`, off `align/2026-11-14-kit-v1-1` at `9cbb365a6`. Rulings read on
`origin/audit/2026-11-10-fable`: RL-149 to RL-165 at `ce12b6924`, RL-166 at `bd090fee1`.

The look manifest is a draft. RL-166 ruled the first draft's twenty open questions in one
batch; RL-166a to RL-166c and RL-167 followed; RL-179 F-12 and RL-180 define the release contract. The manifest `lm-interim-01` carries every value those
rulings fixed. The checked-in code and schemas are pinned, including the independently authored reader from PR #816.
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
| `docs/process/cadence/looks/lm-interim-01.output.schema.json` | The pinned closed schema for the 15 fields of stage 2’s public report |
| `docs/process/cadence/looks/evidence/` | Synthetic evidence the manifest's dictated sentences cite, byte-identical, hashed by the validator |
| `tests/cadence/look_minirepo.py` | Test helper: a pinned copy of every file the look runs, as a git repository whose HEAD is `origin/main`, so the entry points' pin checks and the committed-ledger gate run on real bytes and real git state |
| `joulewise/cadence_looks/schema_check.py` | A standard-library checker for the subset of JSON Schema the look's schemas use (CI has no `jsonschema`). The manifest validator and stage 2 use it. It refuses a schema keyword outside the subset rather than ignore it |
| `tests/cadence/look_fixtures.py`, `tests/cadence/test_schema_check.py` | Synthetic schema-checker fixtures and keyword tests |
| `docs/process/cadence/looks/look_manifest.schema.json` | JSON Schema copy of the manifest format. The Python validator is authoritative |
| `joulewise/cadence_looks/manifest.py` | Validator: `validate_manifest`, `check_repo`, `validate_look_ledger`, `resolve_roster` |
| `joulewise/cadence_looks/step3_energy_ratios.py` | Step 3's script, byte-identical (RL-166 Q6). Any edit needs a ruling |
| `joulewise/cadence_looks/inclusion_34.py` | Rules 3 and 4, stage 1. The U1 evaluator's definitions are copied verbatim, with cites: `thermal.Coverage`, `valid_value` and `keys`, and `thermal_desk.member_record`'s pm_gap loop. Both source files are v4 strict paths, so they are copied rather than imported. Rule 4 reads only each KM003C sample line's `rt` stamp |
| `joulewise/cadence_looks/step3_roster.py` | The step 3 adapter. It loads the pinned bytes (and refuses others), rebinds `LEGS` and `ORIGINAL_EIGHT`, and calls `analyse` and `custody_check` once per prompt-size cell, 10k first. It finds a failed leg by its traceback frame. It reads the tripwire. It contains no arithmetic on energy |
| `tests/cadence/test_inclusion_34.py`, `tests/cadence/test_step3_roster.py` | Equality with the registered U1 source and results; boundary tests at every threshold; spy tests (no sample line decoded, no value key kept, no energy file opened); a stubbed step 3 module for the adapter's behaviour; the real module for the sha gate and failure attribution |
| `scripts/cadence_look_manifest.py` | Validates and pins the draft and records commitments and execution outcomes in the look ledger |
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
| E3 | The public report carries only listed words, a stage-1 count and artifact hashes. All fit diagnostics stay in custody | RL-179 F-12; RL-180 |

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
| F10 | Python standard library plus numpy, no scipy, run with `-I`; stage 2 matches the numpy version recorded in committed stage 1 | RL-166 Q1; RL-180 |

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
| P2 | Private fit diagnostics include the per-day signed error, pooled error, holdout RMS (SD_j), and the corresponding results without heat columns | RL-166 Q3 |
| P3 | `qualified`, interim half: the maximum over counted days (each with at least 3 included legs that have a hot stretch), GPU rail, ≤ 0.02. Fewer than 3 counted days gives `not_evaluable`, which counts as no | RL-151 §2.1; RL-166 Q3 |
| P4 | Prefix bias uses the whole leg and its 3,724-, 3,151- or 2,981-token prefix. Each LODO residual is divided by its length's SD. The mean of day means and its 90% t interval use equal-day weights | RL-166 Q2, RL-175 B.4 |
| P5 | Step 3 (iii), one call per prompt-size cell, 10k first. The tripwire reads the largest `drift_fraction_linear` over cells where γ is estimable. **Threshold 0.08**, or 0.04 if the cold seat's Q11 check fails | RL-151 §1.3; RL-166 Q6, Q11 |
| P6 | With/without marked spans, both marks in one private sensitivity fit | RL-161 §4; RL-166 Q20 |
| P7 | No extension rule | RL-166 Q12 |
| P8 | The qualification prints are declared here (`later_looks`). `lm-qual-01` is committed before any qualification energy is opened. Its scorer is `fit_interim.py`'s predict path at this hash | RL-166 Q10 |

### 1.8 Freezes

| # | Requirement | Cite |
|---|---|---|
| Z1 | Freeze 1: this manifest, its code hashes, the stage-1 schema and the output schema, entered in LOOKS.json, before any development energy is read | RL-149 §2.6; RL-150 R4; RL-166 Amends |
| Z2 | Freeze 2 takes effect when the mainline report records `twin_agrees = yes` and commits the exact coefficient file by SHA-256 | RL-179 F-12; RL-180 |
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
| Q16 | Public words, a stage-1 count and hashes | `outputs`, RL-179 F-12 and RL-180 |
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
| Public report | Any field, type or word outside the closed interim schema |
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
branch's upstream, else `origin/main`; a caller in code may name another remote-tracking ref), and equal to the
shared ref's own LOOKS.json, which is the public record (audit 3, rule P3). The look's committed CLIs take no ref:
they fetch origin's `main` and gate on it. The ledger must validate. `verify_pins`
then requires the row for this look to name the manifest's sha256 at status `committed`, `stage1_committed`,
`run` or `frozen` (Mythos N5). `require_stage1_committed(repo, look_id, stage1_sha256, stage1_doc=...)` requires
`stage1_committed`, `run` or `frozen`, the row's `stage1_sha256` equal to the file's, the manifest at `HEAD` equal
to the working one, and the row's `roster_sha256` equal to the stage-1 file's `input:roster_sha256` (Mythos N7).

**Provenance.** Stage 1 records its manifest and code hashes, run mode and
ledger gate. Stage 2 binds the exact stage-1 bytes and the commit that
authenticates the execution row. Full fit and Step 3 records stay in custody.

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

## 5. Execution and publication

The committed `LOOKS.json` row supplies `execution_host`, `public_root`
(repository-relative), `custody_root` (absolute), and any `holds_cleared` ruling
ids. Establish the two look directories before running. They must be on the
same filesystem so stage 2 can publish the complete report by atomic rename
without creating a public temporary file. Under RL-184 the lead runs
`cadence_look_run.py host-id` at the admitted commit on the execution machine
and records its `hw1:` token in the `stage1_committed` row on main. The token
is derived from the machine's hardware UUID. Stage 2 derives it again before
reservation. The campaign row awaits Astra's paired census rerun and Fable's
manifest cold pass.

Use `cadence_look_manifest.py port-files M --repo .` to enumerate the verified
files for the main-targeted integration. The list includes the two historical
kit blobs and the decoder closure, including files outside the topic delta.
Validate the complete port before registration. Preserve the separate v2
qualification row and its registered bytes when adding the interim row.

Stage 1 checks every rostered bundle locator before reading trace data.
`runs/cadence-leg` is a valid literal relative POSIX path beneath a leg's
`runtime/` directory. Staged span overrides preserve the locator. A null
locator for an unrun leg remains absent. Stage 1 and stage 2 preflight reject
empty, absolute or noncanonical paths and locators that resolve outside the
leg's runtime directory. The pinned twin checks them independently.

Stage 2 checks pins, host, stage-1 commitments, hold clearances, rank, and prior
execution history. Its exclusive creation of `RESTRICTED/` consumes the id.
The primary fit, Step 3 and the pinned isolated twin share this reservation. The parent derives the comparison word from the child frame and the stored primary artifacts. An existing
reservation or report prevents another execution. After an interruption, a
successor manifest needs a named research-lead ruling.

`cadence_look_manifest.py row --output` reads the registered `PUBLIC.json` and
records its digest and the coefficient commitment. `row --error-type` records
the closed error word from the fixed failure notice. After confirming a
reservation ended without a notice or completed report, the lead uses
`row --interrupted` to record `interrupted` and `none_recorded`. These
operations use public records only. See the six private names in the
[fit interface](cadence_look_fit_interface.md#4-stage-2-fit-and-public-report).

## 6. RL-166b (the Mythos attack on the fit form), as the manifest carries it

- **The fit (B-1 to B-7).**
  - `fit.heat_term.form` uses expected hot seconds w̃ in the δ column. RL-166's sentence that Ĥ is zero before the predicted onset is withdrawn, and the validator refuses it if it comes back.
  - `start_readings` takes B-2's activity rule; `estimation` takes B-6's scaled solve.
  - `onset.estimable_when` takes B-3, B-4 and B-5, plus the 0.30 censored-share report.
  - The days tripwire is `days_below_4`.
- **Sentences RL-166b dictates.** They sit in `fit.stated_limits`, and the validator requires each id:
  - what `yes` means, and its pass rate (0.421 for a correct model, about 4 in 10, 0.001 to 0.693 over all twelve committed worlds, 0.421 in the default; 0.095 with no heat term, about 1 in 10.5), and that `no` is not evidence against the term;
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
- **RL-166c.** The partial-correction sentence is RL-166c §5's, verbatim: 0.84 to 0.96 over twelve worlds, 0.88 in the default world. Its `note` cites the re-run's evidence file. `stages.stage2.holds` names the two flags the lead holds stage 2 on, `onsets_before_116_s.to_research_lead` and `meter_clock.to_research_lead` (RL-166c §2 row 7). Stage 2 requires a clearing ruling in the committed ledger for each raised flag before reservation.
- **The 116 s print rule.** It is decision `onsets_before_116_s`, with threshold 0. When the onset model is `not_estimable` and the count is above zero, the decision sends stage 1 to the research lead.
- **Schema fields, named here because the interface page does not name them yet.**
  - Level D: `active_readings.{tf08_c,fan_rpm,tv0h_excess_c}.{active, tolerance, min_count_off_day, threshold}`; `onset.n_uncensored_by_cell`; `onsets_before_116_s.{by_g0_role, total, onset_status, to_research_lead}`; `tripwires.days_below_4`; RL-167's `meter_clock` and `roster.spans[].meter_offsets_ns`; `onset.predictors` as a list (B-2 may drop entries); `rates.per_cell` values nullable (RL-167 row 18).
  - Level O, per channel: `fold_coefficients` (P-1); `day_detail.{days.{legs_with_hot_block, hot_blocks, se_with_heat, se_no_heat}, s_with_heat, s_no_heat}` (P-2); `onset_offset_residuals.{offsets."-2".."5".{n, mean_with_heat, rms_with_heat, mean_no_heat, rms_no_heat}, rms_offsets_m2_to_p3.{with_heat, no_heat}}` (P-3). `columns` may hold as few as 5 entries.
  - The analyst seat emits these names, or the interface page renames them and the schemas follow.

## 7. Stage-1 rehearsal for the manifest pass

Run `python3 -I -B scripts/cadence_look_run.py stage1 --rehearsal NEW_DIRECTORY`
from a fresh detached checkout of the lead's input-bound commit. Before
the commit reaches main, the rehearsal reads the committed draft row
from `origin/align/2026-11-14-look-manifest` and the offload Check items
from `origin/main`. It fetches main like campaign stage 1 and refuses
if the fetch fails. It also checks that the rehearsal branch matches
origin. The draft row must
bind the manifest, roster and rules 3/4 verdict hashes. The manifest
registers the custody root and carries the pin list for the full roster.

Stage 1 selects the range in `stages.stage1.dry_run`, verifies the
selected spans against the pins and uses the campaign's stage-1 time
readers and fit. The hash-only verifier reads the selected pinned files as
opaque bytes. The stage decodes no energy values. The command takes the
registered raw custody copy.

Use an absolute destination with an existing parent and symlink-free
components. It must be disjoint from the checkout and from the physical
roots registered in either the rehearsal branch or fetched main.
Those roots cover the campaign output and span directories. Stage 1
creates the destination exclusively with private
permissions and writes `level_r.json` and `stage1.json` there. The
stage-1 artifact carries a rehearsal marker that the campaign schema
refuses. Successful stdout gives the lead the selected block names, the
manifest and file hashes, the five public tripwire words and
`in_energy_fit`. The tripwires describe the rehearsal population,
including the absence of hp-01. Send the summary only to the lead.

## 8. Remaining authorization

The manifest remains draft. The research lead confirms the host binding at
the cold pass. The pinned reader accepts a one-component bundle locator and
refuses a nested locator under `runs/`. The custody-layout check needs a
reviewed reader and corresponding pin that support the producer's layout.
The prior round reports preserve the development history.
