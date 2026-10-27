# B6-AN-1 report: block-6 analysis driver (the pure layer)

bridge-report/v1 · status: **READY FOR THE TWO EXECUTING REVIEWS** on synthetic data. The run through the real L9
programs is owed at integration, once L9 adds its per-session seams.

## SUMMARY

This round follows the lead's brief corrections of 2026-10-27 (pipeline audit N9, L3 to L5, B6-1 to B6-7, CRITIQUE
item 19; gate policy). The driver is the block-6 "pure layer" (audit N9), and it is built in new files only, on
`work/2026-10-23-by-slots-draft` (991358f73). This round adds:

- **Counting from loop acceptance, checked mechanically (audit L5).** Every session in the census is compared, loop
  counting against its `derived/b6-acceptance.json`. Any disagreement refuses before a unit runs
  (`b6_counting_records_disagree`). After the units run, every analysed session's analysis counting must be reported
  and must equal its acceptance counting (`analysis_counting_not_reported`,
  `analysis_counting_differs_from_acceptance`). Counting is never read from `claim_usable`.
- **Restore once per run (lead item 4).** Each session's desk-compressed bytes are restored before its first unit and
  compressed again after its last, by design §4.1's per-row procedure. ALPHA r3, which serves GAMMA r2 and r3, is
  restored once. An inventory after-check proves the end state.
- **Two phases, each run twice (audit B6-4).** The per-session phase runs any time. The cross-block phase runs after
  block 5's release and the close. The second run of each phase must reproduce the first, digest for digest.
- **Pairing per design §5.** Rule words `same_round`, `later_round`, `earlier_round` and `block5`; ties go to the
  earlier t0; pairings carry `final`. A GAMMA unit that needs block 5's floor is deferred to the cross-block phase.
- **Session index from session records (design §4.4).** It handles re-harvested archives and binds each session's
  harvest and acceptance records by digest.
- **Synthetic root guard (design §17).**
- **S-9 and S-11 removed from scope (lead item 2).** S-16 prints "not evaluated" for a rule its host cannot evaluate
  (audit B6-5).

**Tests:** 108 synthetic tests pass. Sessions are desk-compressed by the real `joulewise.desk_compress`, using a
gzip-backed `zstd` stand-in, because this seat has no zstd. Nine counterfactual mutations each make their regression
test fail, as gate-policy rule 3 asks.

## COMPARISON CONTRACT (lead task, 2026-10-27, evening)

The independent recompute (seat RC-B6-1) joins this driver's outputs key by key and fails closed on any unmatched
key.

- **Key set.** `joulewise/b6/analysis/comparison.py` generates the contract's key set from its rules: models, phases,
  forms and fields. Each run writes a restricted object, `comparison`. Its shape is the one RC-B6-1's report says its
  comparator reads, with nothing else in it: `{sessions: {<id>: {quantities, run_phase_energy_j}}, block:
  {quantities}}`. Metadata (schema `joulewise.b6_comparison_values.v1`, the session-to-pack map, the single-session
  flag) goes to a separate restricted object, `comparison_meta`, so it cannot become unmatched keys.
  - `sessions/<id>/quantities`: exactly each analysed session's pack keys, 100 for ALPHA, 100 for BETA, 89 for
    GAMMA. A GAMMA session analysed alone (`--mode session`) emits the 52 single-session keys; its 6 deferred groups
    wait for the block run, as RC-B6-1's lead decision 5 does on its side.
  - `sessions/<id>/run_phase_energy_j`: `<run_id>/<decode|prefill|request>`.
  - `block/quantities` (cross-block phase only): the 310 `summary/`, `inclusive/`, `side_by_side/` and
    `replication/` keys.
- **Whose instruction.** The task came from lead session 015ASG1T by cross-session message. The user's notice of
  2026-10-27 names the laptop copy of 015ASG1T as the only lead and says to note any other sender's instructions; the
  message carried that session's id. Per that notice I read RC-B6-1's report (`.codex-report/RC-B6-1.md` at
  74a4f8123), and only for the comparator's input shape and key rules.
- **Vendored contract.** The recompute's `configs/b6/recompute/comparison_keys.json` is vendored byte for byte into
  `tests/b6/analysis/fixtures/comparison_keys.json`. Its source (`lane/2026-10-27-recompute-b6` at
  **74a4f81238409580bf437c11f2f54c91e7d3da1f**) and SHA-256 are in `comparison_keys.SOURCE.json`. Only that file was
  read; none of the recompute's code or arithmetic.
- **Tests.** `test_comparison.py` asserts that the generated set equals the vendored file in every part:
  - the three session key lists;
  - the single-session list and its deferred patterns;
  - the 310 block keys;
  - the model tags, phases and run-key form;
  - and that the file has no part the driver does not emit.

  `test_driver.py` checks the emitted objects end to end (per-session, cross-block and session modes). A session
  missing a contract key is a tooling refusal (`comparison_key_absent`), never a silent None.
- **What this changes for the adapter.** `SessionAnalysis.quantities` must carry every contract key of the session's
  pack under the contract's name. Words, booleans and None are allowed, for example `neg8/verdict`,
  `contrast/<c>/outcome`, `cross_session/…/agree`. A new restricted field, `run_energies`, carries the run phase
  energies. The §10/§11.1/§11.4 lines now cover exactly the contract's summarised quantities: 20 per floor pack,
  4 for GAMMA, plus any S-15 `whole_machine/` values.
- **Observations for the lead:**
  1. The contract has no `whole_machine/` keys (S-15 is not filled). The driver summarises such values but does not
     emit them for comparison; the contract needs those keys when S-15 lands.
  2. The block `n` is the number of sessions with a value (AD-1); the recompute must count the same way.
  3. Which runs carry `run_energies` ("every run of a kept unit, the surviving drift-screen references and the clean
     corpus") is the binding's to supply through L9's seams. The driver checks only the key form.

## LEAD ITEMS OF 2026-10-27

| # | Item | Done |
|---|---|---|
| 1 | Follow `b6_analysis_additions.md` §4–§14 and §17; explain differences | See DIFFERENCES FROM THE DESIGN |
| 2 | Drop S-9 and S-11 (filled on `lane/2026-10-22-b6-s9-s11` c37614f71) | `slots.s11_phase_lengths`, `s9_power_lines` and the `slots` CLI are removed. I read the fill's registration diff with digits masked and recompute nothing. A test asserts the functions are gone. Their consumer, the desk exclusion (§4.6), is binding work (below). |
| 3 | Counting from loop acceptance; refuse unless it equals acceptance for all 9 sessions | `acceptance_counting.require_loop_equals_acceptance` (every census session, before any unit) and `analysis_counting_problems` (every analysed session, after its unit). Tests: `CountingAgainstAcceptance` (4), and r2-gamma with a synthetic `claim_usable: false` still counts. |
| 4 | Second full per-session blind run, digest-compared; restore each session once per run | `--mode per-session --run 2` compares every bound field, node row and restricted-object digest with run 1, and refuses on any difference (`comparison.differs`). The cross-block phase needs both per-session runs complete and equal, and is itself run twice. `restore.Lifecycle` reference-counts each session over its units: 9 restore cycles per full run (6 floor sessions + 3 GAMMA sessions), against design §4.1's 15. |
| 5 | Nothing of block 6 merges into main before block 5's release | This lane was never aimed at main; no PR. The integration (L3) and the S-14 pin stay on an integration branch (CRITIQUE item 19). |
| 6 | The independent recompute adaptation is a separate seat | Not built. Its interface is below. |
| 7 | Say when ready for reviews | Ready: lane head as pushed with this report. Review guide below. |

## ACCEPTANCE (brief rows A1 to A8)

| Row | Status | Evidence |
|---|---|---|
| A1 counting from loop acceptance | **pass** | `census.py` reads only `attempts.jsonl` and `state.json` (`joulewise.b6.queue.counting_ids`), and `acceptance_counting.py` checks each session against its acceptance record (schema, session id and `counting` only). Tests: a synthetic r2-gamma whose `exclusions.json` says `claim_usable: false` counts, and an open-tripwire shows the census never opens that file. A loop/acceptance disagreement refuses before any unit runs; an analysis counting that is absent or different refuses. Counterfactuals M1, M2 and M5. |
| A2 GAMMA pairing by round | **pass** | Design §5 rules, ties and `final`. The closed block pairs G r1→A r1/B r1, G r2→A r3/B r2 and G r3→A r3/B r3, both unit-tested and end to end in serial and with 3 workers. Design §5 examples 1 and 2 and the registration's §6.2 example pass. Counterfactual M6. |
| A3 per-session steps, no pooling; §10 | **pass on the fake adapter** | One floor unit per ALPHA/BETA session and one GAMMA unit over {g, A(g), B(g)} (design §4.3). A recording fake shows one call per unit. §10 gives n, mean and sample SD (n − 1) with no ratio and no interval. A session without a value is listed with its reason (lead ruling, AD-1). Worked examples reproduced: registration §10, §11.1 and §11.2. |
| A4 replication word | **pass** | §11.2 and design §11.2 items 1 to 6, now including "below the commitment of 2". |
| A5 flagged-inclusive index | **pass** | Every collected session is indexed. Under ruling 2, every session meeting §11.4 (i) is analysed, (ii) is read from the analysis, and a session failing (i) is recorded with W1/W2/W3/S1. The run is incomplete (`sessions_unaccounted`) while any session is undecided or refused. The label reads "including sessions that did not count: none" when none is added. |
| A6 structure-only public bytes | **pass** | The record `B6-BLIND-DRY-RUN-RECORD.json`, stdout and stderr are guarded: no float, no decimal-looking token, no outcome or replication word, and restricted codes appear only as counts. Unit streams go to restricted logs. Restricted objects are content-addressed. Subprocess tests at 1 and 3 workers. Counterfactual M7. |
| A7 end-to-end run | **partial: synthetic through the fake; real L9 owed** | All nine counting sessions (plus a synthetic non-counting one) run as desk-compressed archives: index, counting check, restore, units, re-compression, after-check, both phases twice, session mode. Outputs are byte-identical on compressed and never-compressed trees (design §4.1 item 4). The real L9 seams and §13's full-size synthetic run (audit B6-1: registered member counts, raw files of at least 1 MiB, one known-answer full-size run) are owed. |
| A8 only WRITE_SCOPE changed | **pass** | `git diff --stat 991358f73..HEAD` lists only `joulewise/b6/analysis/**`, `scripts/b6_analyze.py`, `tests/b6/analysis/**`, `configs/b6/analysis/**` and this report. `joulewise/b6/analysis_lane.py` equals 991358f73, and a test checks it. |

## DIFFERENCES FROM THE DESIGN (`b6_analysis_additions.md` at 578685ec3) AND WHY

1. **Place and scope.**
   - **Where it lives:** the driver is in `joulewise/b6/analysis/` and `configs/b6/analysis/`, not
     `joulewise/b6_analysis/` and `configs/analysis/b6/`. This seat's WRITE_SCOPE names the former.
   - **What is mine:** audit N9 scopes this seat to the "pure layer": counting consumer, pairing, §10/§11, the
     structure-only record and the driver around them.
   - **What I did not build, and why:** the design's binding work. Lead ruling 4 put the per-session seams on L9's
     side, and most of this work edits L9 files or reads bundles through L9:
     - the `AnalysisBlock` seam (§4.2, stage B1);
     - the block-6 exclusions document (§4.5);
     - the desk exclusion P* (§4.6);
     - the allowance (§4.7), b_op (§4.8) and verdict admission (§4.9);
     - the §6 lines (items 3, 7 and 8, and the outside-processor alternative);
     - `machine.py` (§8) and the battery lines (§7);
     - `compare.py` (§12.3 item 4).

     The adapter contract carries their results: `quantities`, `reasons`, `kept_units`, `b_op_defined`,
     `drift_screen` and `analysis_counting`. Who builds them is in OPEN ISSUES.
2. **Units call per-session seams.** They do not call L9's step functions through a `RunState` subclass, per ruling 4.
   The unit shapes (§4.3) and the order (floors, then GAMMA, then cross-block) are the design's.
3. **Restore once per session per run, not per unit** (lead item 4). A session's restore spans every unit that reads
   it. The per-row procedure, the 20 GiB reserve, the re-compression through the desk's `compress` and the exact
   after-check are §4.1's.
   - One addition: a session with no compression record is neither restored nor compressed (`after_check:
     not_compressed`), so the analysis never compresses bytes the desk did not.
   - `ditto --hfsCompression` runs where `/usr/bin/ditto` exists. Elsewhere the copy is plain and the row says
     `apfs_compressed: false`.
4. **Phases.** Design §14 has one full dry run plus a release re-run. Audit B6-4 replaces that with two per-session
   runs before the release and two cross-block runs after it. That is what is built (`--mode per-session|cross-block
   --run 1|2`). There is no separate `--mode release`; cross-block run 2 is the digest replay. NEEDS_RULING 2 asks
   whether §13's "after the release the analysis re-runs from identical bytes" needs a third run.
5. **Pairing.** Pairing uses loop counting, which equals acceptance counting by the L5 check. Design §4.6 pairs on
   analysis counting. Any difference between those is a refusal here (L5), so on any completed run they are the same
   sessions.
6. **§10 when n < 2.** Design §10 prints Q̄ = Q₁ with "not defined (n = 1)". The lead's later ruling (AD-1) prints
   "not computable (n < 2)" with no mean. I followed the lead (NEEDS_RULING 1).
7. **Not built, rendering:** §11.3's closed template table and its test, and §11's printed precision. These are
   rendering of restricted values for the paper. The lines carry the registered labels and the two §11.1 facts as
   data.
8. **Record fields.** The record carries a subset of §14's fields:
   - **Carried:** mode and run, the analysis commit, digests (registration, catalog, session index, loop files, every
     `harvest.json` and acceptance record, block 5's release record, the first run's record), and per session t0,
     loop status, loop / acceptance / analysis counting, `analysed`, admission and flags.
   - **Also carried:** pairings with `final`, node step records and kept units, restore cycles (files, logical and
     on-disk bytes, seconds, after-check word), `cross_block`, and the comparison.
   - **Owed by the binding:** the harvest commit, `harvest_bracket_block5_acceptance`, the `b5_*` exclusion fields,
     desk-exclusion counts and peak `$TMPDIR` bytes.

## FILES CHANGED (since 991358f73)

- `joulewise/b6/analysis/`:
  - `census.py`: loop-acceptance census, with t0.
  - `acceptance_counting.py` (new): the L5 checks.
  - `session_index.py`: session records, acceptance digests.
  - `pairing.py`: design §5.
  - `restore.py` (new): restore once per run, re-compress, after-check.
  - `schedule.py`: DAG with the restore lifecycle and earlier-phase results.
  - `adapter.py`: `analysis_counting`, `deferred`.
  - `driver.py`: phases, runs, checks, record.
  - `summary.py`, `replication.py`, `inclusive.py`, `public.py`.
  - `slots.py`: S-15 carry, S-16 "not evaluated"; S-9/S-11 removed.
  - `comparison.py` (new): the comparison contract's key set and the restricted `comparison` output.
  - `__init__.py`.
- `scripts/b6_analyze.py`: `index` and `analyse --mode per-session|cross-block|session --run 1|2`.
- `configs/b6/analysis/driver.json`.
- `tests/b6/analysis/`:
  - `fakes.py`: the synthetic tree builder and fake adapter.
  - `bin/zstd`: a gzip-backed stand-in, for tests only.
  - `test_census_pairing.py`, `test_lines.py`, `test_driver.py`, `test_slots_cli.py`, `test_comparison.py`
    (new).
  - `fixtures/comparison_keys.json` and `fixtures/comparison_keys.SOURCE.json` (vendored contract and its source).
- `.codex-report/B6-AN-1.md`: this report.

## EVIDENCE

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b6/analysis -t .`, Linux,
  Python 3.13.17: **108 tests, OK** (189 s) on the pushed tree.
- Counterfactuals (gate policy, rule 3). Each mutation was applied to a scratch copy, then the named regression test
  was run; all fail:

  | Mutation | Test(s) | Result |
  |---|---|---|
  | M1: drop the loop/acceptance check | `test_a_loop_acceptance_disagreement_refuses_before_anything_runs` | FAILED |
  | M2: drop the analysis-counting check | two `CountingAgainstAcceptance` tests | FAILED (2) |
  | M3: re-compress after every unit (per-unit lifecycle) | `test_each_session_is_restored_once_and_compressed_again` | FAILED |
  | M4: no second-run comparison | `test_the_second_per_session_run_must_reproduce_the_first` | FAILED |
  | M5: counting that excludes r2-gamma (the item-53 defect) | `test_r2_gamma_counts_although_its_exclusions_say_claim_usable_false` | FAILED |
  | M6: pairing ignores rounds | `test_closed_block6_pairing` | FAILED |
  | M7: guard lets floats through | `test_guard_refuses_numbers_and_words` | FAILED |
  | M8: no after-check | `test_a_write_into_a_session_during_the_run_is_caught` | FAILED |
  | M9: the generated contract drops one cross-session field | `test_key_set_equals_the_contract` | FAILED |
- `tests.b6.test_lane_adapters` keeps its 2 environmental failures (`/bin/zsh`, `/opt/homebrew/bin/python3.13`
  absent). They are identical on 991358f73.

## L9 INTERFACE TARGETED

- `lane/2026-10-27-l9-2` at 8ad47455c, read only. The adapter (`joulewise/b6/analysis/adapter.py`) is the only L9
  call site; `L9_TARGETS` maps each method to L9's step functions.
- The seams L9 adds (ruling 4) are `run_floor_session(request, custody, index=)`,
  `run_gamma_session(request, alpha, beta, custody, index=)` and `released_block5_session(pack, block5_custody)`.
  Each returns a `SessionAnalysis` and should fill `analysis_counting` from the binding's desk exclusion; the driver
  refuses an analysed session without it.
- The index they take is `joulewise.b6_session_index.v1` from `scripts/b6_analyze.py index`. It is per session, not
  design §4.4's per-unit L9 `IndexEntry` file. The binding derives that from it.

## INDEPENDENT RECOMPUTE: THE INTERFACE (separate seat RC-B6-1; shares no code)

The key contract is fixed (section COMPARISON CONTRACT above), and the driver writes its side of it.

**What the recompute reads:**
- The session index (`joulewise.b6_session_index.v1`).
- The public record's `sessions` and `pairings`, for counting from loop acceptance and the pairing rules.
- The desk-compressed bytes, through `desk_compress.read_bytes`.

**What it compares under S-13:** its values against the restricted `comparison` object:
- each run's phase energy, within 1 mJ;
- every printed quantity, unrounded, within half a unit of its last printed digit.

## OPEN ISSUES

- **Binding work (design §4.2 and §4.5 to §4.9, §6 to §8, `compare.py`).** Owner per the lead: the L9 side or an
  integration seat. These pieces live in L9 files or need bundle reads. The desk-exclusion count test of audit L4 ("0
  of 840") belongs with that consumer.
- **Integration base (audit L3):** main + L9 + 1706257c + #573's readers (903b5a2f, db9e8ab3, `desk_restore.py`,
  `restore_run_to_scratch.py`), with `registry.json` and `hazard_refusals.json` regenerated by their tools. The nine
  conflict files of the first round still apply.
  - **Harvest-program-list reading:** the union, i.e. L9's four-file `HARVEST_PROGRAM_FILES` with
    `calibration_bracketing.py`, plus the b6 list and the `block_six` argument.
- **Mac-only paths, owed on the analysis host:** real `zstd`, `ditto --hfsCompression`, and the APFS on-disk sizes.
  This seat has neither tool. The restore code calls them exactly as `desk_compress` does, but its tests ran on the
  gzip stand-in with plain copies.
- **Before the blind dry run:**
  - §13's full-size synthetic run (audit B6-1);
  - S-15's fill (B6-7);
  - S-14's pin (B6-3);
  - custody roots at identical paths on the analysis host (B6-6);
  - S-16 run where block 5's raw bytes are (B6-5), before the release.
- **Speed:** each `test_driver` class builds desk-compressed trees, so the package takes about 3 minutes.

## REVIEW GUIDE (for the two executing reviews)

Probe and mutate in this order:
1. `acceptance_counting.py` and `driver.analyse` / `_finish` (the L5 refusals and completeness).
2. `restore.py` (per-row restore, reserve, after-check, once-per-run reference counting under parallel workers).
3. `pairing.py`.
4. `driver._difference` / `COMPARED` (what the second runs must reproduce).
5. `public.py` (the guard).
6. `summary.py` / `replication.py` / `inclusive.py` against registration §10 to §11.4.

## NEEDS_RULING

1. **§10 with one value:** design §10 (Q̄ = Q₁, SD "not defined (n = 1)") or the lead's AD-1 ("not computable (n <
   2)", no mean)? AD-1 is applied.
2. **The release replay:** is cross-block run 2 (after block 5's release, same bytes, digests equal) §13's "after the
   release the analysis re-runs from identical bytes", or does the release need a third, separately recorded run?

## DECISIONS I MADE

1. **AD-1 (§15 style; lead ruling of 2026-10-27; for the next dated §17 entry). §10 with a missing value.**
   - **Text:** a session in which a quantity Q is undefined is left out of Q's summary. n is the number of sessions
     with a value, and each session left out is listed with its reason. With fewer than two values the summary prints
     "not computable (n < 2)".
   - **Rests on:** §10 ("no claim rests on it") and §11.3 (state n).
   - **Effect:** changes no registered number or counting decision.
2. **A never-compressed session is left untouched** by the restore lifecycle (DIFFERENCES item 3).
3. **An analysed session must report analysis counting.** A missing value is a refusal, not a pass (L5, "requires
   equality").
4. **A GAMMA unit that needs block 5's floor is `deferred`** in the per-session phase and accounted as such. The
   cross-block phase runs it.
5. **The record carries no worker count or host.** Restore seconds are recorded but excluded from the comparison.
