# B6-AN-1 report: block-6 analysis driver

bridge-report/v1 · status: **DONE on synthetic data, under the lead's ruling of 2026-10-27 (option 3)**. The run
through the real L9 programs is owed at integration.

## SUMMARY

The block-6 analysis driver is built in new files on `work/2026-10-23-by-slots-draft` (991358f73), as the lead ruled
after this seat's NEEDS_SCOPE: no base merge, and L9 is called only through one adapter module. It does the following:

- Reads counting from the session loop's acceptance (`attempts.jsonl` and `state.json`), never from a harvest's
  `exclusions.json`.
- Indexes every collected session.
- Pairs GAMMA by round (§6.2).
- Runs block 5's steps once per session through the adapter. Sessions are scheduled as a two-level DAG: ALPHA and BETA
  in parallel, each GAMMA after its paired floors, and the block-6 lines last.
- Writes §10's between-session summary, §11.1's side-by-side table, §11.2's replication word, §11.4's flagged-inclusive
  line and the S-15 carry-over into content-addressed restricted objects.
- Publishes a structure-only record.

It also has the single-session mode of §12.2 and the release replay of §13. S-9, S-11 and S-16 are code-only. S-15 is
plumbing only, because block 5's per-phase definition does not exist yet.

72 tests on synthetic fixtures pass (`tests/b6/analysis`). L9 is not in this tree, so the production adapter refuses
with a structure token until integration. Under the lead's ruling, A7's run through the real L9 programs is owed, as
are §13's full-size synthetic run and the two cold passes.

Lead ruling followed (cross-session message, 2026-10-27): build on 991358f73 in new files only, against L9's interface
read from `lane/2026-10-27-l9-2`, with one adapter module and a fake of it for tests. Integration with L9 is a lead task.

## ACCEPTANCE

| Row | Status | Evidence |
|---|---|---|
| A1 counting from the loop's acceptance | **pass** | `census.py` reads only `attempts.jsonl` and `state.json`. Counting is `joulewise.b6.queue.counting_ids`, the loop's own reading, re-harvest corrections included. `test_census_pairing.CountingFromLoopAcceptance.test_r2_gamma_counts_although_its_exclusions_say_claim_usable_false`: a synthetic r2-gamma archive whose `exclusions.json` says `claim_usable: false` from `neg8.midpoint_lost_primary` counts, and an open-tripwire shows the census never opens that file. `test_driver.EndToEnd.test_r2_gamma_counts_and_enters_the_registered_lines` puts r2-gamma in the summary and the replication word. |
| A2 GAMMA pairing by round | **pass** | `pairing.py` implements §6.2 rules 1 to 3 and the S-17 "floor from block 5" label. On the closed block, G r1 → A r1/B r1, G r2 → A r3/B r2 and G r3 → A r3/B r3 (`test_closed_block6_pairing`, and end to end through the DAG in `test_closed_block6_runs_every_session_once_and_alone` and the 3-worker `test_parallel_workers_also_pair_by_round`). §6.2's own worked example passes. Pairing reads only counting and rounds. Before the close, a pairing other than same-round is marked provisional. |
| A3 per-session steps, no pooling; §10 | **pass on the fake adapter** | The adapter takes one session (GAMMA also takes its two paired floor results) and returns that session's results. The recording fake shows one call per session. §10 is per quantity and pack: n = block 5 plus the three counting sessions, the mean and the sample SD (n − 1), with no ratio and no pooled interval. The registration's worked examples pass: 26.15 / 0.148 J, flagged-inclusive 26.216 / 0.195 J, and §11.1's Δ +0.0667 J with own differences +0.21, −0.13 and +0.12 J. |
| A4 replication word | **pass** | `replication.py` gives "replicated" only when every counting GAMMA session's outcome word and dbar sign match block 5's. Block 5 `not_estimable` (or no dbar) gives no word. A short pack prints its own sentence. Flagged-inclusive words are printed beside the word and do not enter it. Tests cover the §11.2 worked example (replicated, then not replicated on an `unresolved` session with every sign agreeing), a sign change, not_estimable, short and floor-from-block-5. |
| A5 flagged-inclusive index | **pass** | Every attempt of every replication pack appears in the public `session_index` with its admission: counting, added, not_registered_experiment (W1 to W3, S1), not_computable (N1 to N4, fewer than 5 kept units per stratum, b_op undefined or drift screen undefined) or not_harvested. P1 to P4 and D1 are ignored, so alpha r2 (synthetic physics stop) is **added**: "including sessions that did not count (n = 5)". A session excluded at pre-admission is never analysed. |
| A6 structure-only public bytes | **pass** | Public outputs are stdout (record path and digest), stderr (`node <kind>:<pack>:<session> <status>` lines) and `B6-ANALYSIS-RECORD.json`. `require_structure_only` refuses any float, any decimal-looking token and any outcome or replication word before writing. Restricted flag codes appear only as a count. Refusal tokens that look like outcome words become `restricted_token`. Every adapter call runs with Python- and descriptor-level stdout and stderr sent to restricted logs, and an unexpected driver exception's text goes to restricted custody. Restricted outputs are canonical JSON at `restricted/objects/<sha256>.json`, and the record names them by digest. A subprocess test with a fake that prints numbers and outcome words on every stream finds structure only in the public bytes, for 1 and 3 workers, and finds the noise in the restricted logs. |
| A7 end-to-end run | **partial: synthetic through the fake; real L9 owed** | Reduced-size synthetic sessions (all nine counting plus alpha r2) run end to end through census, pairing, DAG, lines, custody and record, in serial, parallel, session and release modes. Serial and 4-worker runs give byte-identical custody trees, record digest `af053954…`. Per the lead's ruling, the run through the real L9 programs is owed at integration. §13's full-size synthetic run through the real stage chain is owed, not skipped. |
| A8 only WRITE_SCOPE changed | **pass** | `git diff --stat 991358f73..HEAD` touches only `joulewise/b6/analysis_lane.py`, `joulewise/b6/analysis/**`, `scripts/b6_analyze.py`, `tests/b6/analysis/**`, `configs/b6/analysis/**` and `.codex-report/B6-AN-1.md`. There was no base merge (lead ruling). |

Verification run (this checkout, Linux, Python 3.13.17):
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b6/analysis -t .`, which
ran 72 tests, all OK. `tests.b6.test_lane_adapters` (the existing test of the stub's seam) has 2 failures that are
environmental (`/bin/zsh`, `/opt/homebrew/bin/python3.13` absent), and they are identical on 991358f73 without this
change.

## FILES CHANGED

- `joulewise/b6/analysis/__init__.py`: package statement.
- `joulewise/b6/analysis/census.py`: A1. The loop-acceptance census, structure record and registered order.
- `joulewise/b6/analysis/pairing.py`: A2. §6.2 with S-17 and provisional pairing.
- `joulewise/b6/analysis/adapter.py`: the **only** L9 call site. It holds the `SessionAnalysis` contract,
  `L9ProgramAdapter`, and `L9_TARGETS` naming the exact L9 functions per method.
- `joulewise/b6/analysis/schedule.py`: the DAG executor (process pool, serial at 1) with per-node stream capture.
- `joulewise/b6/analysis/summary.py`: §10 and §11.1.
- `joulewise/b6/analysis/replication.py`: §11.2.
- `joulewise/b6/analysis/inclusive.py`: §11.4 pre-admission and admission.
- `joulewise/b6/analysis/public.py`: custody preflight, content-addressed restricted objects and the structure guard.
- `joulewise/b6/analysis/slots.py`: S-11, S-9, S-15 (carry and the GAMMA refusal) and S-16.
- `joulewise/b6/analysis/driver.py`: orchestration and the blind-dry-run, session and release modes.
- `joulewise/b6/analysis_lane.py`: `AnalysisLane.analyse` delegates to the driver. `precision_reached` still returns
  None (the replication packs register no precision stopping, §5.3). `HarvestLane` is unchanged.
- `scripts/b6_analyze.py`: the command line (`analyse`, and `slots` for S-11/S-9).
- `configs/b6/analysis/driver.json`: packs, contrasts, target, §11.4's code groups (from §8.2) and F_min.
- `tests/b6/analysis/{__init__,fakes,test_census_pairing,test_lines,test_driver,test_slots_cli}.py`.
- `.codex-report/B6-AN-1.md`: this report.

## L9 INTERFACE TARGETED

- `lane/2026-10-27-l9-2` at **8ad47455ce55203949ea77a3ee330432d5a48101**, read with `git show` only; nothing is imported
  from this tree. The functions targeted are in `adapter.L9_TARGETS`, all in `joulewise/b5_analysis/dry_run.py`:
  - **Floor session:** `step_1`, `step_2`, `step_3` (`RunState.prepare_tripwires`, i.e. `kept_units.load_kept_units`),
    `step_3b`, `step_4` (`scripts.extract_detection_floors.main` with `steps.classify_step4_exit`), `step_10`
    (`scripts.issue_reported_energy.main` with `require_step10_admission`) and `step_11`.
  - **GAMMA session:** steps 1 to 3b for the GAMMA window, then `step_5` (pinset and mint from the paired floor
    sessions' step-4 reports), `step_8`, `step_6`, `step_9`, `step_9b` and `step_11`.
  - **Block 5:** its release record and restricted outputs.
- **Seam L9 lacks at that commit:** L9's only public entry is the whole-block `run(mode, index, custody)` over one
  block-5 window per pack, with `joulewise.b5_window_index.v1` sealed to block-5 pins. The adapter names three
  per-session seams (`run_floor_session`, `run_gamma_session` and `released_block5_session`) and refuses with
  `l9_session_seam_absent` until they exist. It never reaches into `RunState` internals. Calling L9's step functions
  per session also inherits L9-2's shared calibration cache and parallel steps 1–2, rather than copying them.

## DECISIONS I MADE

1. **No summary for a quantity undefined in any session.** If any session in a §10 summary lacks a value, there is
   no mean and no SD, and the sessions lacking it are named (`undefined_in`). A mean over fewer sessions would print
   an n other than §10's "1 + counting sessions" without saying so. (Also in NEEDS_RULING.)
2. **Which sessions are analysed.** I analyse the counting sessions and the non-counting sessions that pass §11.4
   pre-admission. Not-harvested, W/S and N1/N2/N4 sessions are indexed but not analysed. (Also in NEEDS_RULING,
   against §12.3 item 3.)
3. **A non-counting GAMMA session added to the flagged-inclusive line** is paired by the same §6.2 rule over counting
   floor sessions (§6.2: "pairing depends only on which sessions count").
4. **An outcome-class stop is a completed result.** Its session's values feed the lines and its dependents run.
   Exit 3, as in L9.
5. **Public flag codes.** Codes whose catalog `blinding` is STRUCTURE are shown. The others, and codes the catalog
   lacks, are counted as `restricted_codes_removed` (§12.1).
6. **The public record is deterministic.** It has no worker count, time or host, so serial and parallel runs and the
   release replay can be byte-compared. Release compares the commit, config digest, census, pairings, index, node
   structure, line refusals and every restricted object digest.
7. **S-15 gets no arithmetic.** Block 5's per-phase whole-machine definition (its S-15 commit) does not exist at the
   L9 target. The driver carries `whole_machine/` values from the adapter, summarises them like any quantity, prints
   the boundary sentence, and refuses them on GAMMA (§9.5 item 5).
8. **S-11 input.** S-11 reads automation-supplied non-claim smoke rows (`pack`, `phase`, `duration_s`,
   `claim: false`). It refuses claim rows and non-target phases, and never defaults a missing T_phase. S-9 is
   `1.9 / (4 × T_phase)`, which reproduces the registration's 0.238 W and 0.0720 W comparison values.
9. **Seat setup was not run.** The `JouleWise-data` seat setup was not needed: the work needs only the standard
   library and in-tree modules, and no real data.

## OPEN ISSUES

- **Owed at integration (A7):**
  - L9's per-session seams (above).
  - The authenticated **block-6 session index** (per session: archive root, claim-runs root and harvest record
    digest), which block 5's window index cannot express.
  - The run through the real L9 programs on reduced-size synthetic sessions.
- **Owed before the blind dry run (§13, S-14):**
  - The **full-size** production-shaped synthetic run through the real stage chain.
  - One independent executing review.
  - The two blind executing cold passes of §13.
  - The pin of the analysis commit.
- **Independent recompute, block-6 adaptation (another seat; it shares no code with L9 or this driver).** The
  interface it needs from this driver:
  - The census from the public record's `census` and `session_index`, which give counting from loop acceptance.
  - The pairings from `pairings`.
  - Per session, the restricted `sessions` object's `quantities` keys (`reported/<model>/<phase>/mean_j`,
    `floor/…/operative_j`, `dominance/…/R`, `contrast/<c>/energy_ratio`, contrasts' `dbar` and `outcome`) to compare
    unrounded under S-13.
  - Per run, the phase energies from L9's re-reduced outputs, at 1 mJ.
  - It should emit the same keys, so the comparator is a key-by-key join.
- **Integration of the block-6 line with L9 (lead task).** The base merge (0576a734d into 991358f73) conflicts in 9
  files:
  - `joulewise/b5/harvest.py` (4 hunks)
  - `joulewise/whole_window.py` (12)
  - `scripts/digest_pin_census.py` (3)
  - `scripts/repin.py` (1)
  - `scripts/extract_detection_floors.py` (2)
  - `tests/test_harvest_b5_window.py` (2)
  - `configs/gates/hazard_refusals.json` (2)
  - `configs/pins/registry.json` (717)
  - `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` (1)

  Regenerate the pins registry and hazard refusals with the tooling, not by hand.
- **My reading of the harvest-program-list conflict.**
  - The b6 line keeps `HARVEST_PROGRAM_FILES = (harvest.py, whole_window.py, scripts/harvest_b5_window.py)` and adds
    `B6_HARVEST_PROGRAM_FILES` plus `harvest_checkout(block_six=...)`.
  - L9 inserts `joulewise/calibration_bracketing.py` into `HARVEST_PROGRAM_FILES`.
  - Both lines' `harvest.py` and `whole_window.py` import `calibration_bracketing`, so it is harvest program on both.
    The resolution is the union: L9's four-file `HARVEST_PROGRAM_FILES`, plus the b6 list and the `block_six`
    argument.
  - Consequence: a new K-7 record lists one more file. Earlier harvest records keep their pins. Nothing here gates,
    because the record is "a record, never a flag".
- **`joulewise/b6/analysis_lane.py` is in `B6_HARVEST_PROGRAM_FILES`** on this line, so my change alters that file's
  digest in any future block-6 harvest-checkout record. The block-6 harvests already ran from the measurement checkout
  at the S-1 pin and are unaffected. If the lead prefers that file's bytes unchanged, revert it: the driver needs
  nothing from it.
- **The command line `analyse` can only refuse until integration.** It refuses `analysis_checkout_not_clean` on a
  dirty checkout, then `l9_absent_from_checkout`.

## NEEDS_RULING

1. **§10 with a missing value.** Should the summary be withheld when any session lacks the quantity (my choice,
   Decision 1), or computed over the sessions that have it with n printed?
2. **§12.3 item 3 ("the blind dry run has completed over every block-6 session").** Does this require L9 runs over
   sessions that §11.4 pre-admission already excludes (W/S or N1/N2/N4, for example a structurally failed session)?
   Or is indexing them, as now, enough?

Base and bookkeeping: an earlier commit on this lane carries a model-naming `Co-Authored-By` trailer. The lead said
to leave it; there was no force push.
