# Look manifest: freeze 1 for the interim look (DRAFT)

Opus builder (Opus 5.5), Sat 14 Nov 2026 20:28 PST (`date`). Branch `align/2026-11-14-look-manifest`, off
`align/2026-11-14-kit-v1-1` at `9cbb365a6`. Rulings read on `origin/audit/2026-11-10-fable` at `ce12b6924`.

This document is a draft. It authorizes nothing. RL-165 §8.2: "No look manifest is on any ref, and freeze 2
cannot happen without the interim look." This branch adds the first one, `lm-interim-01`, together with its
schema, its output schema and a validator. Twenty points are not settled by any ruling. Each is a
`PENDING:Qn` in the manifest and an open question in §4. A manifest with any `PENDING` left cannot be
committed (`status: committed`): the validator refuses it.

**Blind status.** No campaign, v4 or rehearsal energy, power, meter, journal or custody file was opened for this
work. Sources: the decision log, the kit, queue and ledger JSON, the cadence code on the branch, and the
header and `sha256` of the step 3 script, which is code. Step 4's synthetic drift note
(`evidence/align-v4-campaign/step4-rl151-drift.md`) was read for the Q11 threshold. It is simulation output,
not a measurement. The tests build synthetic inputs only.

## Files

| File | What |
|---|---|
| `docs/process/cadence/looks/lm-interim-01.json` | The draft manifest for the interim look (`status: draft`) |
| `docs/process/cadence/looks/lm-interim-01.output.schema.json` | The look's output schema, pinned by sha256 in the manifest (a freeze 1 item) |
| `docs/process/cadence/looks/look_manifest.schema.json` | JSON Schema copy of the manifest format. The Python validator is authoritative |
| `joulewise/cadence_looks/manifest.py` | Validator: `validate_manifest`, `check_repo`, `resolve_roster` |
| `scripts/cadence_look_manifest.py` | CLI: `validate MANIFEST [--final] [--repo R [--kit K]...] [--span-ledger L]` |
| `tests/cadence/test_look_manifest.py` | 33 tests, synthetic only, including a spy test showing that no custody file is opened |

The package is `joulewise/cadence_looks/`, **not** `joulewise/cadence/`. Every file under `joulewise/cadence/`
is a frozen path of the v1.1 kits. RL-150 R4 requires that adding the manifest changes no leg kit's frozen
paths, and that the runner and the leg runtime never import look code.

## 1. What the rulings require of the look manifest

### 1.1 Home, timing, review

| # | Requirement | Cite |
|---|---|---|
| H1 | Freeze 1 lives in a look manifest: a file of its own beside the kits, not in a leg kit. "These are in the kit" becomes "these are in the look manifest". Leg kits keep `looks: []` | RL-150 R4 (amends RL-149 §2.6 item 1) |
| H2 | Contents: the look id; the blocks it reads; the fit code's paths and hashes; the model family and predictor list (as R1 amends); the code that judges inclusion rules 3 and 4; the output schema; the one decision of §2.6. RL-151 §2.1 withdrew that decision (H9) | RL-150 R4; RL-151 §2.1 |
| H3 | It is committed before any development energy is read. The block ledger points at it by hash | RL-150 R4; RL-150 §4 item 4; RL-155 Gate line ("Development energy waits for the look manifest") |
| H4 | Adding it changes no leg kit's frozen paths, so the §2.8 authorization does not end and line 8 is not re-run. The runner and the leg runtime must never import it, and the manifest's check states this | RL-150 R4 |
| H5 | The manifest's check includes that the fit code does not read the `condition` field. Every campaign leg carries the constant `benign` there | RL-150 R6 |
| H6 | Review: one cold seat that did not write the fit code, against §2.6 and §2.7, then the research lead's cold pass. Paper-bound | RL-150 R4; RL-155 §5.3 |
| H7 | Owners: an Opus builder for the schema and the analyst seat for the fit code | RL-155 §5.3; RL-165 §8.2 |
| H8 | Due: the cold seat's report and the manifest go to the research lead by Mon 16 Nov 18:00; the research lead's pass is the same day. The manifest gates Thursday before the kits do | RL-165 §8.2 |
| H9 | The manifest now also carries step 3's statistic (iii) and RL-151 §2.2's prints | RL-151 §1.3 item 2; RL-151 §6 item 2 |

### 1.2 What the look opens: spans and legs

| # | Requirement | Cite |
|---|---|---|
| S1 | The interim look reads the development legs and hp-01 | RL-149 §2.6 table |
| S2 | Development is dev-01 to dev-05, 60 legs. dev-02 was added and the mixed-cell blocks became dev-03 to dev-05. The look follows dev-05. RL-149's "after dev-04 is DESK_FINAL" is superseded | RL-155 §3.3; RL-155 §2 slot 11; RL-158 §3; RL-165 §1 |
| S3 | The counted pilot (dev-01 L001-L003) and every v1.1 class A smoke are development legs under the inclusion rules | RL-149 §2.9 item 3; RL-150 R5 |
| S4 | hp-01 is description and never in the fit. It has no reserve. If fewer than 9 of its 12 legs are included, the lead tells the research lead before the interim look | RL-149 §2.3, §2.5; RL-157 §4 |
| S5 | "Matched blocks" for High Power means the same cell, the same soak and the same span position. The Automatic spread (dev-01 and dev-02) prints beside each ratio. The caption reads "soak in Automatic; mode set N s before the first leg's G0", and the research lead owns it at the interim look | RL-157 §1, §3, §4 |
| S6 | Qualification energy stays sealed until freeze 2 is committed. Qualification legs do not run before freeze 2 | RL-149 §2.6 item 3; RL-165 §8.1 |
| S7 | ctl-01 has its own look, after its print code is frozen | RL-149 §2.6 |
| S8 | F0, F2 and Part C runs: their energy is not read under any look unless the research lead rules so | RL-149 §5 (bridge); RL-155 §4 rule 5 |
| S9 | No W1, C or T energy enters any fit | RL-149 §2.6 item 4 |
| S10 | The unit of independence is the calendar day. Every leave-one-out error is leave-one-day-out. A leg's day is the local date of its span's t0. A block's pilot and remainder on one date count as one day | RL-149 §2.3; RL-155a §1.2; RL-155 §2 notes |
| S11 | Development falls on at least three calendar days, with a day span and a night span | RL-149 §2.3; RL-165 §1 |
| S12 | Every attempt stays in custody, replaced ones included. A contaminated attempt is excluded whether or not a redo replaced it | RL-149 §2.4; RL-150 R7 |
| S13 | Custody reaches the look as one verified custody copy made by the existing offload tooling | RL-149 §2.9 item 5 row 3 |
| S14 | The reserve replaces an excluded leg in the same cell, in a later block of the same phase | RL-149 §2.4; RL-157 §4 |

### 1.3 Which energy fields

| # | Requirement | Cite |
|---|---|---|
| E1 | Campaign energy is the GPU rail, the other rails and DC-in | RL-149 §2.6 |
| E2 | Every leg is analysed on DC-in as well as on the GPU rail. The interim prints repeat on DC-in | RL-149 §2.4 rule 4; RL-149 §2.6 table |
| E3 | S_w's E_j is the GPU-rail integral over the episode, less its G0 and G1 intervals, ending at the last stamped token | RL-149 §2.7 |
| E4 | The runner hashes each meter stream and decodes only its header and trailer. No sample line is decoded outside a look | RL-150 R8 |
| E5 | Step 3's convention, which the frozen step 3 code uses: GPU-rail block energy is the window-mean power times the overlap, in 256-token blocks | RL-149 §1.4; RL-151 §1.3 item 2 |
| E6 | SMC system total and DC-in watts for sabotage-instructed rows are sealed. This concerns the series, not the campaign, and is listed so that the look never touches them | RL-149 §4 |

### 1.4 The fit: heat term and onset

| # | Requirement | Cite |
|---|---|---|
| F1 | Ĥ is a fixed offset, not a sixth column: the sum over turns of a heat term in count-derived load seconds and that turn's start readings | RL-149 §2.7 |
| F2 | Allowed predictors: logged counts; turn order; frozen prefill and decode rates; the turn's start Tf08 and fan speed from the last journal reading at or before the turn's start, on a fresh stamp; **start TV0h as the excess over the span's soak reference**. The sign of the start term is not assumed | RL-149 §2.7; RL-150 R1 part 1; RL-158 Q1 |
| F3 | Never allowed: any reading, clock, state or duration from inside the turn | RL-149 §2.7 |
| F4 | A missing or stale start reading gives the count-only prediction and a flag. A reading outside the calibrated range sets `heat_extrapolated` | RL-149 §2.7; RL-149 §1.6 item 1 (2 s age rule) |
| F5 | SD_j gains the term's parameter covariance and the frozen holdout relative error on hot exposure | RL-149 §2.7 |
| F6 | S_w is print-only in one form: L* = ∞, with the covariance in its SD. Rule P and the L* family are retired | RL-151 §2.1 |
| F7 | Onset model: the predicted onset from start Tf08 and load seconds, with its leave-one-day-out error. The count-only cut is the predicted onset less twice that error | RL-149 §4 item 1; RL-149 §2.6 |
| F8 | The OS-onset residual is the seconds to the first off-state reading, against the frozen onset model | RL-149 §4 item 9 |
| F9 | Size is a cell assigned by the cell law, not a free draw | RL-158 Q7 |
| F10 | Tables and the fit read `g0_role` and the measured start from the leg record, never the kit's shape or band label | RL-161 §3 (F12); RL-150 R2 |
| F11 | The fit reports with and without spans marked "reference from an excluded leg" | RL-161 §4 |
| F12 | The realized prompt count is read from the bundle. The lead reports any leg more than 5 % from nominal | RL-158 Q5 |
| F13 | The coefficients also serve K_w and the count-only cut's onset model | RL-151 §2.2 |
| F14 | hp-01 is never in the fit | RL-149 §2.3 |

### 1.5 Inclusion rules at the look

| # | Requirement | Cite |
|---|---|---|
| I1 | Rules 1 to 6, with rule 5 as amended | RL-149 §2.4; RL-150 R7 |
| I2 | **Rules 3 and 4 are judged at a look, not at the pilot.** INSTRUMENT_FAULT covers the meter until then | RL-150 R9 |
| I3 | The code that judges rules 3 and 4 is pinned in the manifest | RL-150 R4 |
| I4 | No leg is dropped for its energy, its residual, its OS level or state, or its heat | RL-149 §2.4 |
| I5 | Inclusion reads no energy, so decisions taken on it stay blind | RL-157 §4 |
| I6 | Until F8's column exists, inclusion is taken from the summary's `admitted` field. The column now exists in `desk.py` | RL-150 R9; RL-161 §3 |

### 1.6 Who runs it, and blinding

| # | Requirement | Cite |
|---|---|---|
| B1 | Campaign energy is read only by frozen code, at the named looks, by one analyst seat, into an output schema fixed beforehand. The lead checks the output against the schema | RL-149 §2.6 |
| B2 | No desk, watcher, queue or agent opens an energy, power or meter file of a campaign leg | RL-149 §2.6; RL-150 R8 |
| B3 | The blind statement lists each look with its date, code hash and output, as a disclosure and not as "blind". R6's sentence replaces "none carries a condition" | RL-149 §2.6; RL-150 R6 |
| B4 | Every print that depends on a campaign model carries the model's hash and `qualified: yes / no / not_run` | RL-149 §4 |
| B5 | Step 3's precedent: one analyst script, reviewed against a synthetic input before it runs; joules divided in memory | RL-149 §1.4 |

### 1.7 Prints and decisions at the interim look

| # | Requirement | Cite |
|---|---|---|
| P1 | The heat-term fit; the leave-one-day-out relative error over the hot stretch and over the leg; the prefix length-only bias in score SD; the onset fit and its leave-one-day-out error; the High Power table; the same for DC-in | RL-149 §2.6 |
| P2 | The prefix bias prints at 1.10, 1.30 and 1.374. 1.374 is a grid point with no standing. The prefix comparison uses the corrected definition | RL-150 §3.2; RL-151 §2.2 |
| P3 | Step 3's statistic (iii) on the development legs, by the frozen step 3 code. **If it is above the largest drift at which step 4 keeps the rows at or under .035, the S row returns to the research lead before the W1 receipt is signed.** Otherwise nothing happens | RL-151 §1.3 item 2; RL-151 §6 item 4 |
| P4 | `qualified` is yes when the interim leave-one-day-out error over the hot stretch is at or under 2 % **and** the qualification bias at 1.10 has its 90 % interval inside ±0.10. The interim look supplies the first half | RL-151 §2.1 |
| P5 | The interim look's "one decision" (S_w print-only above 2 %) is withdrawn. Rule P is retired. No selection is made at the look | RL-151 §2.1, "Amends" |
| P6 | An extension beyond the cap (now 132) needs a ruling. It is sized from the interim errors by a rule written before qualification energy is opened | RL-149 §2.3; RL-155 §3.3 |
| P7 | The look's output goes to the research lead | RL-149 §5 "What comes back" item 4 |

### 1.8 Freeze 2, and what commits before data is read

| # | Requirement | Cite |
|---|---|---|
| Z1 | **Freeze 1**, before any development energy is read: the fit code and its hash, the model family and predictor list, the inclusion rules, and the looks' output schema, all in the look manifest | RL-149 §2.6 item 1; RL-150 R4 |
| Z2 | **Freeze 2**, the development freeze at the interim look: the coefficient file and its hash, committed. The series uses these coefficients, and they are not refitted on qualification legs | RL-149 §2.6 item 2 |
| Z3 | Qualification energy stays sealed until freeze 2 is committed. Qualification legs do not run before it. The phase boundary is crossed only after freeze 2 | RL-149 §2.6 item 3; RL-149 §2.8; RL-165 §8.1 |
| Z4 | Before the release run opens a joule of the series, the coefficient hash is in its preregistered inputs | RL-149 §2.6 item 4 |
| Z5 | Derived (no ruling enumerates the file): freeze 2 must hold what F4, F5, F7 and P4 consume. That is the coefficients and covariance per channel, the holdout relative error, the calibrated range, the onset model and its error, the interim half of `qualified`, and the hashes of the manifest, code and output | RL-149 §2.7; RL-149 §4; RL-151 §2.1 |

## 2. How the draft manifest encodes these

- `reads.blocks` lists dev-01 to dev-05 with role `fit` and hp-01 with role `describe`, each with `spans: "all_desk_final"`. Spans are resolved from a span ledger at the look, not listed now: dev-03 to dev-05 have not run and dev-01's spans were re-cut (s03b, s04b). The rule "every desk-final span of these blocks" is fixed now. Its resolution is mechanical.
- `reads.never_read` lists every class of run the look must not open, with its ruling.
- `reads.custody_files` names, by basename and stage, what each stage opens. **Stage `inclusion` and stage `journal` open no energy file.** The validator refuses an inclusion-stage entry that carries energy.
- `inclusion.verdicts_frozen_before_energy: true` is a proposal (Q8). The inclusion verdicts are computed and hashed before the energy stage opens anything.
- `decisions` holds the drift tripwire (threshold PENDING:Q11), the interim half of `qualified` (0.02), the hp-01 count below 9 (reads no energy) and the extension rule (Q12). Any decision id that resembles Rule P or "the one decision" is refused.
- `outputs.schema` pins `lm-interim-01.output.schema.json` by sha256. That schema is closed, holds fits, errors and ratios only, and has no per-leg energy (Q16).
- Placeholders are written `PENDING:Qn`. The validator requires each one to name an open question in the file. A committed manifest may carry none, and no open questions.

## 3. The validator

`python3 -B scripts/cadence_look_manifest.py validate docs/process/cadence/looks/lm-interim-01.json --repo .`

| Check | Refuses |
|---|---|
| Structure | A missing or unknown key at any level, a missing cite, a bad id, or a placeholder that names no open question. With `--final` or `status: committed`, any placeholder |
| Phases | A block the look kind may not read: qualification, ctl, reserve (unless it serves development), F0, F2, F3, Part C, W1, C or T. hp-01 in the fit. A development block that is waited for but not read |
| Fit | A predictor outside RL-149 §2.7 with R1's amendment; a forbidden list that lacks in-turn readings, clocks, states and durations, raw start TV0h, `condition` or the kit's band or shape; an assumed sign; validation that is not leave-one-day-out or covers fewer than 3 days |
| Inclusion | Rules not exactly 1 to 6; rules 3 and 4 not judged at the look or without pinned code; any rule that reads energy |
| Outputs and decisions | A required print or decision missing; prefix ratios other than [1.10, 1.30, 1.374]; prints lacking `model_sha256` or `qualified`; per-leg energy in the output |
| Freezes, custody, review | Freeze 1 not before any development energy; freeze 2 refitted on qualification or lacking its commit-before list; more than one seat; the lead not checking the output; not paper-bound |
| `--repo` | A pinned hash that does not match; a fit path that is a frozen path of a kit; a kit with `looks` not empty; **any frozen `.py` of any kit importing `joulewise.cadence_looks` or a fit module**; fit code reading `condition` |
| `--span-ledger` (at the look) | A span that is **unsealed** (seal broken, or named by an earlier energy read), **out of phase** (the ledger phase differs from the block's, or the look may not read that phase), not desk-final, unknown, or filed under another block; a fit roster on fewer than 3 calendar days |

**The span ledger** (`joulewise.cadence_span_ledger.v1`) is operational JSON: `spans[{span_id, block_id, phase,
desk_final, energy_seal, t0_local_date, serves_phase?}]` and `energy_reads[{read_id, spans, cite}]`. Its
`energy_reads` list is the disclosure list of RL-149 §2.6 in machine form. This PR does not build its producer.
The lead writes it from QUEUE.json, BLOCK-QUEUE.json and the desk finals before the look.

**What it opens:** the manifest, the ledger, kit JSON and repository source (the pinned code, plus the frozen
`.py` paths for the import scan). It never opens a custody, energy, meter or journal file.
`OpensNoEnergy` places such files beside it, records every `open`, and checks this.

## 4. Open questions for the research lead

Each one is also in the manifest's `open_questions`, with a proposal.

| Q | Question | Proposal |
|---|---|---|
| Q1 | No fit code exists on any ref, and no ruling fixes the heat term's functional form, though freeze 1 must hold "the model family". Who writes it, and in what form? | The analyst seat (Opus) writes `joulewise/cadence_looks/fit_interim.py`: Ĥ = load s × (b0 + b1 ΔTf08 + b2 fan + b3 ΔTV0h), with one fixed effect per size cell and no sign assumed |
| Q2 | What is the response on campaign legs? In the series Ĥ is an offset beside the five-term leave-one-out count prediction, which a conditionless single-turn leg does not have | Per-turn channel energy less a count-only prediction at the frozen rates, fitted jointly on development legs |
| Q3 | Definitions of "hot stretch" and "relative error", including the one compared to 2 % for `qualified` | Hot stretch: from the first off-state reading to the last token. Relative error per held-out day; the maximum is compared to 2 % |
| Q4 | Onset: does start TV0h excess join the predictors (R1 amended §2.7 only)? Is the clock load seconds or wall seconds? How are turns that never leave the state censored? | As RL-149 §4 item 1 wrote (Tf08 and load seconds); load seconds; right-censored at the last token |
| Q5 | Where do the "frozen prefill and decode rates" come from? | Fitted at this look from token stamps (no energy) and frozen in freeze 2 |
| Q6 | The step 3 code (`step3_energy_ratios.py`, sha256 `84a1a553…eb173`) exists only in scratch and hard-codes its nine legs. How is "the frozen step 3 code" applied to development legs? | Commit it byte-identical under `joulewise/cadence_looks/`, plus a small frozen adapter that calls its per-leg functions on the roster; the cold seat checks that no definition changes |
| Q7 | Rule 3's U1 number for powermetrics gaps, and what "clean" means for the KM003C under rule 4. May rule 4 read sample *timestamps* at the look? | U1's registered number, cited by protocol line; clean = trailer counts zero and no sample gap over 2 s in the leg's interval, from timestamps only |
| Q8 | Are inclusion verdicts computed and hashed before the energy stage opens anything? | Yes: a two-stage look |
| Q9 | If hp-01 is not desk-final when dev-05 is, does freeze 2 wait for it? | No. The High Power table runs later by the same frozen code, as a separately disclosed read |
| Q10 | Freeze 1 fixes "the looks' output schema" (plural), and RL-151 §6 asks for §2.2's prints here. Does this manifest also fix the qualification look's prints? | Yes, declared here; `lm-qual-01` pins its code before freeze 2. The type-M residual prints `not_run` (RL-165 §8.1 removed type M) |
| Q11 | The drift threshold. Step 4 kept the rows at or under .035 at every drift from 3 to 8 %, the top of the scan, so no boundary was found | 8 %, plus step 4's caveat as a print: if (iii) is well above 2 %, print the drift's form |
| Q12 | Does the extension rule (RL-149 §2.3) go in this manifest? | No rule; any extension beyond 132 legs needs a ruling |
| Q13 | Do reserve-01 legs that replace excluded development legs enter the fit? | Yes, marked `serves_phase: development` |
| Q14 | Type-T legs in dev-05, if the code lands: in the heat-term fit? | No, describe-only at this look |
| Q15 | Pre-run check: RL-149 §1.4 reviewed step 3 against a synthetic input; standing practice since 11-13 is a blind dry run on real custody | Both: synthetic unit tests for review, then a structure-only dry run on the roster that opens no energy file |
| Q16 | May the output carry per-leg energy, or only fits, errors and ratios? | Fits, errors and ratios only |
| Q17 | Are the CPU, ANE and package rails read at this look? | No |
| Q18 | R4's ledger pointer by hash: BLOCK-QUEUE's schema is closed and has no field for it | A small `blocks.py` change (not a frozen path of any kit) adds `look_manifests` when the manifest is committed |
| Q19 | Are step 3's nine rehearsal legs kept out of the fit? | Yes |
| Q20 | Is "reference from a redo" treated like "reference from an excluded leg" in the with/without print? | Yes, both |

## 5. Not in this PR

- The fit code (Q1), the code for rules 3 and 4 (Q7), the committed step 3 code and its adapter (Q6). These are the analyst seat's work. Their paths and hashes fill the placeholders.
- The span ledger's producer, and the BLOCK-QUEUE pointer (Q18).
- `lm-qual-01` (Q10).
- No energy is read. No look is run.
