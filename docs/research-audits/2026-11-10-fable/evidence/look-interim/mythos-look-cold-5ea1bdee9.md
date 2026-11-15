# Seat: mythos, interim look cold

Sat Nov 14 23:27:33 PST 2026 (from `date`).

Manifest PR #793 plus fit PR #795, combined head `5ea1bdee9`. The worktree at `/Volumes/JW-EXT/scratch/mythos-look-cold/wt` is clean; nothing was pushed or committed. Synthetic data only.

## Verdict: ADMIT WITH FIXES

**The arithmetic matches the rulings and stage 1 is blind to energy.** I found no ruled number, formula, threshold or refusal that the fit code gets wrong.

**Findings 1 to 6 have to be fixed before the manifest is committed.** After the commit the code changes only by a ruling and a new manifest id.
- Stage 1 refuses the whole look on a G0-timeout leg, which the campaign expects (finding 1).
- CI is red at this head because of this package (finding 2).
- Nothing in the run path checks the pins, and the DC-in decoder is not pinned (finding 3).
- Stage 2 can die after energy is opened, on three causes no ruling names (finding 4).
- The manifest and output schema still carry the hp-01 table that RL-167 §3 removed (finding 5).
- The freeze-2 coefficient file and RL-166 Q10's predict path have no code (finding 6).

Findings 7 and 8 should go in the same pass. Findings 9 to 14 are low.

## What I verified

| Check | Result |
|---|---|
| Tests on python 3.14 with numpy 2.2.6 | 75 + 13 + 15 + 29 + 53 pass (1 skip) |
| The package's mutation check | 75 mutants, all killed |
| Twin agreement, analyst side re-run at this head against Sol's stored outputs | 9 of 9 sets pass, levels D and O |
| Step 3 bytes | sha256 `84a1a553…eb173`: working file, git blob and the scratch original are identical (`cmp`) |
| Tool outputs against the two pinned schemas | All valid, 7 scenarios plus 4 edge sets |
| Two runs of stage 1 and stage 2 | Byte-identical |
| `validate --repo` at this head | ok, 0 placeholders; every pin matches its file |

## Findings

`R` is `/Volumes/JW-EXT/scratch/mythos-look-cold/repro`. Run `python3 -I -B $R/blinding_invariance.py` once first; it writes the custody copy the custody cases use.

### 1. HIGH. Stage 1 refuses the whole look when any leg has a bundle and no turn

- **Where:** `scripts/cadence_look_run.py:298-299` builds a turn for every type-A leg whose record has `result.bundle`. `build_turn` (`:183-186`) then refuses, or `_jsonl` (`:72`) raises.
- **Why it will happen:** a G0 timeout has exactly that shape. `joulewise/align/apple/cadence_leg.py:199` always sets `bundle`, and `:212-217` returns `leg_status: g0_unreleased` with no turn. RL-158 and RL-161 expect timeouts among consumers.
- **Why no test saw it:** the generator writes `"bundle": … if turn else None` (`scripts/cadence_look_synth.py:657`), so synthetic custody never has this shape. `inclusion_34.py` handles the same leg correctly, per leg.
- **Reproduce:** `python3 -I -B $R/custody_cases.py g0_timeout_empty g0_timeout_absent`. Result: `REFUSED align_turns: not one turn` and `FAILED FileNotFoundError at cadence_look_run.py:72`; no stage-1 file.
- **Fix:**
  - Judge rules 1, 2, 5 and 6 from the leg record first.
  - For a leg those rules already exclude, a bundle read failure gives `turn: null` and a named count.
  - For a leg that would be included, keep the refusal.
  - Add this shape to the generator and a test.

### 2. HIGH. CI is red at `5ea1bdee9`, from this package

- **numpy.** `tests/cadence/test_fit_interim.py:17` imports numpy at module level, and `tests/cadence/test_look_run.py` does so through `fit_interim.py:27`. CI runs python 3.13 from `actions/setup-python` with no install step.
  - PR #795, run 43687220431: shard 4 reports `MODULE LOAD ERROR tests.cadence.test_fit_interim: No module named 'numpy'`.
  - `quick` and shard 8 fail in `tests.test_shard_tests`, because unittest discovery itself errors.
  - `tests.cadence.test_look_run` fails the same way locally; its shard was still pending.
- **Host-command census.** `tests.test_host_command_sites` fails on two unlisted sites:
  - `joulewise/cadence_looks/step3_energy_ratios.py`, already red on #793's own head (run 43687149525);
  - `scripts/cadence_look_synth.py`.
- **Reproduce:** `cd wt && /opt/homebrew/bin/python3.13 -B -m unittest tests.cadence.test_fit_interim` (that interpreter has no numpy, as in CI); `python3 -B -m unittest tests.test_host_command_sites`. CI logs are in `out/ci_job_*.log`.
- **Fix:**
  - A CI job that installs a pinned numpy and runs the two modules, as `align-templates` does for jinja2.
  - A module-level skip when numpy is absent, so discovery does not error. A skip alone would leave the fit untested in CI.
  - Add the two sites to `tests/host_command_sites.json`. **Do not edit the step 3 file to quiet the census** (RL-166 Q6).
- **Not traced:** six v4-line modules these PRs do not touch are also red: `tests.align.test_v4_dynamic_closure`, `test_v4_executed_closure`, `test_smoke_delta_sol1`, `test_smoke_delta_sol2` (#795) and `test_w1bm_sol2`, `test_timing_receipts` (#793).

### 3. MEDIUM. Nothing in the run path enforces the pins, and the DC-in decoder is outside them

- **Where:**
  - `scripts/cadence_look_run.py` and `step3_roster.py` take no manifest and read no `LOOKS.json`.
  - `assemble` (`scripts/cadence_look_manifest.py:156-161`) copies the hashes it is given and compares none with a pin.
  - Stage outputs carry no manifest hash.
- **Reproduce:** `$R/pin_not_enforced.sh`. A copy of the tree with `QUALIFIED_THRESHOLD = 0.5` ran stage 1, stage 2, step 3 and `assemble`, all exit 0. The verdict went from `fails` to `passes`. Only the separate `validate --repo` refuses.
- **Unpinned code that reads energy:** `python3 -I -B $R/import_closure.py`. Stage 2 executes 15 repository files that are neither pinned nor recorded in `code_sha256`. They include `joulewise/external/km003c_parse.py`, which decodes every DC-in sample and fits the device clock, and its imports `joulewise/aggregate.py` and `joulewise/desk_compress.py`.
- **Fix:**
  - Pin those three files in `fit.code` and record them in `code_sha256`.
  - Both stages and the adapter take `--manifest` and refuse when a running file's hash differs from its pin.
  - `assemble` refuses on the same comparison.

### 4. MEDIUM. Stage 2 can stop after energy is opened, on causes no ruling names

In custody mode energy is read first (`cadence_look_run.py:437`) and the fit runs after (`:439`).

| Cause | What happens | Reproduce |
|---|---|---|
| A per-leg relative residual with magnitude 1 or more | `ValueError` at `fit_interim.py:1355-1356`; nothing is written. The residuals RL-166 Q16 allowed for diagnosis vanish when a fit fails badly | `python3 -I -B $R/edge_cases.py residual_over_one` |
| One fit day | Uncaught `TypeError` at `fit_interim.py:907` (empty training fold) | `… edge_cases.py one_day` |
| A meter stream file with no aligned samples anywhere in a span | `REFUSED a meter stream without aligned samples` (`cadence_look_run.py:343-344`) after 12 GPU files were opened. Rule 4 passes, because it judges only streams that overlap a leg | `… custody_cases.py meter_stub` |

**Fix:**
- Keep the residual. It is a ratio by construction (`fit_interim.py:1195-1196`); add a count of values at or over 1.
- Refuse fewer than two fit days from the stage-1 file, before any energy file is opened.
- `MeterSpan` skips a stream with no aligned samples and refuses only when a segment of an energy-fit leg has no samples.
- Add a structural preflight to stage 1 for every file stage 2 will open (presence and header line only), so the dry run finds layout faults.

### 5. MEDIUM. The manifest, the output schema, the validator and `assemble` still carry the hp-01 table

RL-167 §3 and its Amends: stage 2 opens no hp-01 energy at this look, and the table is `lm-hp-01`. The code obeys (`fit_interim.py:1283`, `cadence_look_run.py:379`; the spy shows no hp-01 energy file opened). The frozen text does not:
- `lm-interim-01.json:6` (title), `:42` ("If hp-01 is desk-final when stage 1 runs, it is in this look … by the same pinned code"), `:943-958` (print `high_power_table`).
- The output schema has `high_power_table` with `energy_ratio`, and `decisions.hp01_table` allows "in this output".
- `manifest.py:108` requires the print.
- `assemble --hp-table` (`scripts/cadence_look_manifest.py:154,164`) embeds whatever file it is given. In `python3 -B $R/validator_cases.py` (last line), a table with per-leg joules was written into the output, exit 0.
- `rulings` (`:7-33`) cites neither RL-166a nor RL-167.

**Fix:** state hp-01 as counts only at this look, remove `--hp-table` and the schema object, and cite RL-166a and RL-167.

### 6. MEDIUM. Freeze 2's coefficient file and Q10's predict path do not exist

- `lm-interim-01.json:1206` says the coefficient file is "written by stage 2". No code writes it, and no schema or key list exists. The interface page §4.2 leaves "its exact keys" to the manifest, which has prose only.
- `lm-interim-01.json:1172` and RL-166 Q10 name the qualification scorer as "`fit_interim.py`'s predict path at the hash this manifest pins". The file has no predict entry point. The design row and the fold are private to `_channel` (`fit_interim.py:878-897`, `:933-952`).
- So the file the series uses would be assembled by hand after the output is seen, and `lm-qual-01` cannot score at this hash.
- **Fix, before the pins are final:**
  - a `write_coefficients` with a pinned schema;
  - a `predict(coefficients, leg)` returning the turn's Ĥ and its segment predictions, tested to reproduce the main fit's fitted values.

### 7. MEDIUM. A span whose reference leg is excluded at the look gets no mark

- **Where:** `cadence_look_run.py:284-290` reads marks only from `leg_summary.json`. The runner's `excluded` there is "not admitted under rules 1, 2, 5, 6" (`scripts/cadence_legs_runner.py:392`). Rules 3 and 4 are judged later, at the look.
- **Reproduce:** `… custody_cases.py capture_excluded`. The capture leg fails rule 4, three consumers stay in the fit, and the span's marks are `[]`. The with/without print (RL-161 §4, RL-166 Q20) does not move.
- **Fix:** after the six verdicts, mark a span "reference from an excluded leg" when its capture leg is not included and a consumer is in the roster.
- **For the research lead:** I read RL-161 §4's "excluded" to cover a leg excluded at the look.

### 8. MEDIUM. "Committed" cannot be checked, and the roster has no writer

- Stage 2 accepts any stage-1 file whose bytes match the hash on its command line. In `… custody_cases.py edited_stage1`, two legs were removed by hand, the edited file's own hash was passed, and stage 2 ran on 51 legs.
- `LOOKS.json` has a status `stage1_committed`, but its row is closed at four keys (`manifest.py:948`). It cannot hold the stage-1 hash, the output hash or the coefficient hash.
- `validate --span-ledger` prints the roster and writes no file. Stage 1 does not check its roster against the manifest or the ledger.
- `inclusion_34.py` accepts `{"roster": [...]}`; stage 1 fails on it (`… custody_cases.py roster_dict`: `FAILED TypeError at cadence_look_run.py:313`).
- `assemble` asks for a clearing ruling on the two hold flags (`:141-153`) and not on Q8's five tripwires.
- **Fix:**
  - ledger fields for the three hashes;
  - stage 2 takes `--looks` and refuses unless the row names that stage-1 hash;
  - `validate --span-ledger --roster-out`;
  - one roster shape.

### 9. LOW. GPU trace coverage is computed and then dropped

- `coverage_min` is built at `cadence_look_run.py:393-395`, type-checked at `fit_interim.py:986`, and neither printed nor used.
- In `… custody_cases.py trace_hole`, 6 s of power rows removed inside a 20 s block moved that leg's relative residual from −0.0077 to +0.0036, with no trace in the output.
- Rule 3 allows powermetrics gaps up to max(1 s, 5 periods).
- **Fix (a new print, so it needs a ruling):** per channel, the minimum coverage over energy-fit legs and the count under 0.99.

### 10. LOW. Manifest text that differs from the rulings or the code

| Where | Text | Ruling or code |
|---|---|---|
| `lm-interim-01.json:538` | The off reading is "on a fresh stamp" | RL-166a R-4, RL-167 row 3: it cuts whatever the stamp's age; `Unknown` never cuts. The code is right (`fit_interim.py:307-328`) |
| `:528` | r_d is "sum of decode tokens" | R-1: Σ(N − 1) |
| `:485` | "n the block's tokens" | R-2: 255 for block 0 |
| `:1092` | "print yes, no or not_evaluable" | The output prints `passes`, `fails`, `not_evaluable` |
| `:662` | "0.04 to 0.69 over the five worlds tried" | Its own evidence file has twelve worlds, down to 0.001 (about 45 % censored) and 0.010 (day SD 5 points). RL-166c §5 moved the other sentence to twelve worlds. **For the research lead** |
| `:327-376` | `custody_files` | Omits stage 1's read of each meter stream (the header line, and the last 256 KB by pattern, for R-20) |
| Prints `realized_prompt_tokens` and the span trailer counts | Declared | No code emits the first; the second appears only with `inclusion_34.py --detail-out` |
| `docs/process/cadence_look_manifest.md:81, 100, 102, 105, 222-227, 262` | Pre-RL-166b rows; "does not exercise rules 3 and 4"; pins at `acea4a919` | Stale. `inclusion_34.py` now agrees with the planted verdicts on 71 of 72 legs |

### 11. LOW. The validator checks ids, not the dictated sentences, and refuses the ruled fallback

Reproduce with `python3 -B $R/validator_cases.py`.
- **Enforced:** pins (with `--repo`), both stage-2 holds, type T in `leg_types_never`, the type-T `never_read` line, every stated-limit id, thresholds, channels, blocks.
- **Accepted, and should not be:**
  - the partial-correction sentence changed back to "0.85 to 0.95";
  - the pass-rate sentence replaced;
  - the evidence sha256 changed;
  - `never_read` cut to its type-T line;
  - `estimable_when: "always"`;
  - the withdrawn δ form without its "H is zero" sentence.
- **Refused, and should not be:** `drift_tripwire.threshold: 0.04`, which RL-166 Q11 requires if the check fails (`manifest.py:116`, `:750-755`). The applied threshold is a run-time flag of `step3_roster.py` (`:138`), not a frozen value.
- **Fix:** pin the dictated sentences verbatim; check the evidence file's hash in `check_repo`; accept 0.08 or 0.04 and record the Q11 outcome in the manifest.

### 12. LOW. `inclusion_34.py`: type-T legs are opened, and its sensor list is unpinned

- No leg-type filter (`inclusion_34.py:439-450`). The spy shows a type-T leg's `events.jsonl`, `config.json`, `align_thermal.jsonl` and `rich_telemetry.jsonl` opened. RL-166 Q14 says "not read at this look at all". No energy is involved.
- `--runtime-config` defaults to a path relative to the working directory (`:421`); from another directory the tool exits with a traceback. The file decides rule 3's sensor keys and is neither pinned nor hashed into the verdict file.
- **Fix:** skip `spec.leg_type == "T"`; resolve the default from the module's path; pin the config and record its hash.

### 13. LOW. Custody mode labels every output `synthetic: false`

- `cadence_look_run.py:316` and `:376` hard-code the flag. Every stage-1 and stage-2 file in my scratch says `synthetic: false`. A rehearsal output can be taken for the real one.
- **Fix:** the generator writes a synthetic marker into each `runner_receipt.json`, and the reader carries it.

### 14. LOW. A leg that never ran gets an invented cell

- `cadence_look_run.py:304-306` writes `cell_prompt_tokens: 2000` for a roster leg with no record. A 19,458 leg printed as 2,000 in my run.
- The level-R validator also accepts a leg with all six rules true and no turn (`… edge_cases.py unrun_included`), against RL-167 R-21.
- **Fix:** allow null for a turn-less leg, and require all six false with no turn.

## Check 1. The rulings, traced to code

`F` is `joulewise/cadence_looks/fit_interim.py`, `C` is `scripts/cadence_look_run.py`, `M` is `docs/process/cadence/looks/lm-interim-01.json`. "ok" means I read the code against the rule's text and it matches. A number in brackets is the finding.

**RL-166 Q1 to Q20**

| Q | Where | Result |
|---|---|---|
| Q1 | pins `M:449-470`; clock `F:625-635`; start readings `F:273-286`, `:706`, `:716-719`; heat row `F:878-897`; missing start `F:671-672`; out-of-state τ̂ = 0 `F:565-569`; numpy version `F:830`, `:1325` | ok; pins not enforced (3) |
| Q2 | GPU through step 3's loader and `Trace` `C:385-392`; DC-in trapezoid `C:357-369`; base `F:889-893`; OLS and CR1 `F:900-930`; prefix bias `F:1043-1066`, `:1248-1260` | ok; DC-in decoder unpinned (3) |
| Q3 | hot blocks `F:774-777`; errors `F:1143-1203`; verdict `F:1191-1194`; no-heat lines `F:1208-1210` | ok |
| Q4 | response `F:307-328`; censored ML `F:369-450`; estimable `F:521-545`; error `F:575-606`; cut `F:753-754` | ok, as amended |
| Q5 | `F:686-702` | ok |
| Q6 | sha gate `step3_roster.py:52-61`, `C:320-329`; rebinding and calls `:113-117`; per cell, 10k first `:130-145`; tripwire `:146-158`; kept and dropped `:89-101`; failed legs `:104-127` | ok |
| Q7 | interval `inclusion_34.py:369-383`; rule 3 `:184-214`; rule 4 `:221-264`; stamps only `:70`, `:278-300` | ok; trailer counts (10) |
| Q8 | stage 1 `F:638-839`; tripwires `F:783-794`; hash gate `C:428-432`, `F:1278` | ok; (1) and (8) |
| Q9 | no hp-01 energy `F:1283`, `C:379` | code ok; manifest differs (5) |
| Q10 | `M:1160-1181` | declared; predict path missing (6) |
| Q11 | `step3_roster.py:43-44`, `:138`; `M:1073-1086` | 0.08 stands, see check 5; (11) |
| Q12, Q13 | `M:1135-1146`; `M:228-240`, `manifest.py:1042-1044` | ok |
| Q14 | `F:173-175`, `:663-664`; `C:291`, `:298` | stage 1, stage 2 and step 3 ok; `inclusion_34.py` (12) |
| Q15 | `scripts/cadence_look_synth.py` | ok; finding 1's shape is not planted |
| Q16 | `F:1343-1365`; residuals `F:1195-1196` | ok by scan; (4) |
| Q17 | two channels `C:390`; GPU rows only `step3_energy_ratios.py:198` | ok |
| Q18 | `LOOKS.json`; `manifest.py:936-979`; no change under `joulewise/cadence/` | ok |
| Q19, Q20 | `M:312-318`, `step3_roster.py:113-114`; `F:1291-1316` | ok; mark source (7) |

**RL-166a R-1 to R-9**

| R | Where | Result |
|---|---|---|
| R-1 | `F:686-694`, `:635` | ok |
| R-2, R-3 | `F:891`, `F:892` | ok |
| R-4 | `F:307-328`; hot `F:774-777` | ok |
| R-5 | `F:658` | ok |
| R-6 | `F:484-486`, `:716-718` | ok |
| R-7 | `C:148-149` (keys fixed at `C:49`) | ok |
| R-8 | `F:1049-1050` | ok |
| R-9 | `F:565-569`, `:774-777`, `:1157-1167` | ok |

**RL-167 R-10 to R-21, and §2's rows**

| Item | Where | Result |
|---|---|---|
| R-10 | `F:927` | ok |
| R-11 | `F:1043-1066` | ok; t quantiles match tables to 6 digits |
| R-12 | row 7 | ok |
| R-13, R-14 | `F:575-606`; `F:1200-1202` | ok |
| R-15, R-16 | `F:694`, `:706-708`; `F:724-727` | ok |
| R-17, R-18 | `F:1166-1167`, `:1172`, `:1199`; `F:1145-1146`, `:1161-1162`, `:1174-1175` | ok |
| R-19 | `F:369-450` | ok |
| R-20 | Vbus × Ibus `joulewise/external/km003c_parse.py:155-156`; header offset `C:345`; print `C:223-249`, `F:852-866` | ok; my report is in check 5 |
| R-21 | `C:291`, `:277-281` | ok; (14) |
| Rows 1, 2 | `F:891-892` | ok |
| Row 3 | `F:316-319` | ok |
| Rows 4, 5 | `F:301-304`, `:336-343` | ok |
| Row 6 | `F:289-298`, `:724-725` | ok |
| Row 7 | `F:548-558`, `:1116-1120` | ok |
| Row 8 | `F:543-544`, `:759-765` | ok |
| Rows 9, 10, 11 | `F:753-754`; `F:599` | ok |
| Row 12 | `F:1164-1165`, `:1199` | ok |
| Rows 13, 14 | `F:1048-1066` | ok |
| Row 15 | `F:190-194`, `:218-221` | ok |
| Rows 16, 17 | `F:1293-1316` | ok |
| Rows 18 to 21 | `F:696-702`; `F:783`, `:790`; `F:808-827`; `F:784-785` | ok |
| Row 22 | `F:1283`, `C:379` | ok |
| §2.1 | start validity `F:273-286`; precedence `F:662-672`; `dev_included` `F:679-680`, `:787-792`; `extrapolated` `F:719`; `qualified: not_run` `F:1320` | ok |
| §3 | code as row 22 | manifest and schema differ (5) |

**RL-166b B-1 to B-7 and P-1 to P-4**

| Item | Where | Result |
|---|---|---|
| B-1, B-1a | `F:609-622`, `:895-896`, `:955-960`; `F:565-572` | ok; the formula matches a 2,000,000-draw simulation, and RL-166b's example gives 0.636 s |
| B-2 | `F:733-742`, `:842-849`; used at `F:1077`, `:1290` | ok |
| B-3, B-4 | `F:521-545`; `F:548-558` | ok |
| B-5 | `F:399-475` | ok |
| B-6 | `F:900-930` | ok |
| B-7 | `F:70`, `:790` | ok |
| P-1 | `F:1127`, `:1269` | ok |
| P-2 | `F:1173-1190`, `:1241-1244` | ok |
| P-3 | `F:1212-1240` | ok |
| P-4 | `F:796-806`; hold recorded by `scripts/cadence_look_manifest.py:141-153` | ok |

**RL-166c rows 1 to 11**

| Row | Where | Result |
|---|---|---|
| 1 | Names: every output validates against both schemas | ok |
| 2, 3 | `F:842-849`; `F:1176-1189` | ok |
| 4, 5 | `F:1217`; `F:1229-1235` | ok |
| 6 | `F:797-806` | ok |
| 7 | `stage2` has no refusal on either flag | ok |
| 8 | `F:444-446` | ok |
| 9, 10 | `F:790`; `F:1290` | ok |
| 11 | no clamp, `F:613-622` | ok |
| §5 | `M:684`, verbatim | ok; not enforced (11) |

## Check 2. Blinding

**Stage 1 opens no GPU energy file, and its output cannot depend on any energy value.**

- **Spy.** `$R/spy_cli.py` records every open through `sys.addaudithook`, which also sees `os.open` and `pathlib`. The custody copy had decoys: energy files in every bundle, a rejected attempt per leg, a real-shaped type-T bundle, and a qualification span outside the roster. Across the seven scenarios, stage 1 opened no `power_trace.csv`, no decoy, no rejected attempt, no type-T bundle and no span outside the roster (`out/spy_noisy.out`).
- **Three kinds of file it does open also carry power values.** RL-166 Q4 and RL-167 R-20 require these reads, but the CLI's sentence "Stage 1 opens NO energy file" is too strong as written.
  - `rich_telemetry.jsonl` and `raw/powermetrics.plist`: row stamp, `elapsed_ns` and `thermal_pressure`, by pattern.
  - Each span's meter stream: the header line, and the last 256 KB for the last poll's `rx` and `rt`.
- **Functional proof.** For `python3 -I -B $R/blinding_invariance.py` I changed every power and energy value in a second custody copy: 70,564 power rows, 133,739 meter samples, 36,956 telemetry rows and 36,956 plist frames. The rules-3/4 verdict file, its detail, level R and the stage-1 output are byte-identical. Stage 2's output differs, as a control.
- **Stage 2's order.** It opens the stage-1 file first and energy after the hash matches. With a wrong hash it opened no custody file at all (`… custody_cases.py wrong_hash`). It opens `power_trace.csv` for the 53 energy-fit legs only: no hp-01 leg, no type-T leg. Whether that hash was committed is not checked by code (finding 8).
- **Output.** `python3 -B $R/leak_scan.py data/<scenario>` compared about 7,800 candidate per-leg, per-turn and per-block joule and watt values per scenario with every number in the stage-1, fit, step 3 and assembled files. There is no match in any of the seven scenarios, no leg-keyed map outside `residuals`, and no vector of leg or segment length.

## Check 3. The manifest and its validator

- **Present and correct:** pins (all match at this head), both stage-2 holds, the leg types, `never_read` with type T, the partial-correction sentence (RL-166c §5, verbatim), and the pass-rate figures. The figures match the evidence file, whose sha256 `f1c6bc32…` matches the note and whose bytes equal the seat's own report.
- **Not right:** findings 5, 6, 10 and 11.

## Check 4. Edge cases

The generator's seven scenarios all run through the five tools (`out/scenarios.out`). My own sets are in `out/edge_cases.out`:

| Set | Ruled | Got |
|---|---|---|
| All onsets censored | `not_estimable`, `converged` null, δ dropped, 116 s, `not_evaluable` | As ruled |
| One day | Days tripwire; readings inactive at 0 | Stage 1 as ruled; stage 2 crashes (4) |
| Two days | `not_evaluable` | As ruled |
| A constant reading; all three constant | Inactive; κ column and onset predictor dropped | As ruled; 8 and 6 columns |
| Two active readings exactly collinear | Onset `converged: false`; the energy design refuses | As ruled |
| Zero-energy block outside P-3; negative block | No refusal (R-18 is on sums) | As ruled |
| Zero-energy block inside P-3; a leg with zero energy | Refuse | As ruled |
| Missing fan key at the start | Leg out of the fit, counted | As ruled |
| P-4's flag with `not_estimable` | Flag true; the fit does not refuse | As ruled |
| A leg residual over 1 | Not ruled | Crash (4) |

## Check 5. Rules 3 and 4, the adapter, and what this seat owed

- **`inclusion_34.py`** matches RL-166 Q7, and its three criteria equal the registered evaluator's (`thermal_desk.py:691-696`). On synthetic custody it finds the planted sidecar and meter holes. See finding 12.
- **RL-166 Q6's check.** `step3_roster.py` contains no arithmetic on energy. It selects fields, takes a maximum over drift fractions and compares with a threshold. Its roster is stage 1's included type-A fit-role legs: 55 in the synthetic set, two more than the energy fit. That is "the development legs" of RL-151 §1.3.
- **RL-166 Q11's check: passes, so 0.08 stands.**
  - The 8 % cell exists in `/Volumes/JW-EXT/scratch/desk-step4-s-oc/results_rl151_drift.json`: rows .034 (+30 % all) and .030 (bank +30 %, spam −11 %), 1,000 repetitions each.
  - The simulated drift is the same quantity as (iii). In `s_oc_sim.py:94-95, 209` the per-token cost ramps from the turn's start to d at the off-nominal time. Step 3's (iii) is max |γ| times the median TV0h rise from the first token to the cut.
  - **Caveat:** at 1,000 repetitions one standard error is about .006, so .034 is not resolved from .035.
- **RL-167 R-20's condition: the stream carries a second pair, periodic.**
  - Every poll line has `rx` (CLOCK_MONOTONIC_RAW) and `rt` (CLOCK_REALTIME) (`scripts/km003c_monitor.py:207`).
  - The trailer has `end_raw_ns` and `end_mono_ns` and no wall stamp (`:246-248`).
  - So the two-pair print applies, and the code implements it.
  - Not tested: whether the two clocks drift apart by more than 0.1 s over a multi-hour span. The dry run's `meter_clock` print will show it.

## Check 6. CI

No. CI has no numpy, and these tests fail there now (finding 2).

## Check 7. Reliability and reproducibility

Beyond findings 1, 3, 4, 6, 8 and 13:
- **The reader layer has no twin.** The Sol twin covers levels R, E, D and O. The custody readers, the meter trapezoid and the clock offset are tested only by their author, on a custody layout the same author wrote. Finding 1 is in that layer.
- **Stage 2's reader first meets real files at the real look.** The stage-1 dry run opens none of them.
- **`model_sha256` hashes exact float bits.** I did not test whether another machine or BLAS reproduces it. The output prints the numpy version and no platform.
- **Timing.** Stage 2 took 0.6 s and step 3 1.0 s at 72 legs on this machine, which is not the Air. The synthetic meter runs at 2 samples a second, so real stream sizes are not represented.

## Not checked

- Any real custody file. Leg-record field names were checked against the runner's code, not against a real record.
- The Air's interpreter and numpy under `-I`.
- The Sol twin's code. I reused its stored outputs. I did not open the parallel seat's scratch.
- Step 3's `OUTPUT.json`.
- The v4-line CI failures named in finding 2.
- The pass-rate simulation itself; I compared the manifest with the evidence file only.

## Files

- Reproductions and their index: `/Volumes/JW-EXT/scratch/mythos-look-cold/repro/README.md`
- Outputs of my runs: `/Volumes/JW-EXT/scratch/mythos-look-cold/out/`
- This report: `/Volumes/JW-EXT/scratch/mythos-look-cold/REPORT.md`
- A note for anyone reading the twin evidence: `/Volumes/JW-EXT/scratch/fit-agreement/REPORT.md` still describes the first, failing run. `compare_result.json` beside it is the later pass.