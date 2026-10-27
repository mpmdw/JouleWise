# B6-AN-1 report: block-6 analysis driver

bridge-report/v1 · status: **DONE on synthetic data**. Built under the lead's rulings of 2026-10-27 (option 3, then
rulings 1 to 4). The run through the real L9 programs is owed at integration, once L9 adds its per-session seams.

## SUMMARY

The block-6 analysis driver is built in new files on `work/2026-10-23-by-slots-draft` (991358f73). There is no base
merge, and L9 is called through one adapter module only.

- **Counting** is read from the session loop's acceptance (`attempts.jsonl` and `state.json`), never from a harvest's
  `exclusions.json`. Every collected session is indexed.
- **Pairing:** GAMMA is paired with its floor sessions by round (§6.2).
- **Per-session steps:** block 5's steps run once per session through the adapter, as a two-level DAG. ALPHA and BETA
  run in parallel, each GAMMA waits only on its paired floors, and the block-6 lines run last. Serial and parallel
  scheduling give the same bytes.
- **Block-6 lines:** §10's between-session summary, §11.1's side-by-side table, §11.2's replication word and §11.4's
  flagged-inclusive line, plus the S-15 carry. All go to content-addressed restricted objects, and the public record
  is structure only.
- **Session index:** the block-6 session index (archive root, claim-runs root and harvest-record digest per session)
  is built from the loop's records and re-checked on load.
- **Modes:** a single-session mode (§12.2) and a release replay (§13).
- **Slots:** S-9, S-11 and S-16 are code only. S-15 is plumbing only, because block 5's per-phase definition does not
  exist yet.
- **Tests:** 82 tests on synthetic fixtures pass (`tests/b6/analysis`).
- **`analysis_lane.py`:** reverted to the bytes of 991358f73 (ruling 3).
- **Production adapter:** it refuses with structure tokens until L9's per-session seams exist (ruling 4).

## ACCEPTANCE

| Row | Status | Evidence |
|---|---|---|
| A1 counting from the loop's acceptance | **pass** | `census.py` reads only `attempts.jsonl` and `state.json`. Counting is `joulewise.b6.queue.counting_ids`, the loop's own reading, including re-harvest corrections. `test_r2_gamma_counts_although_its_exclusions_say_claim_usable_false`: a synthetic r2-gamma whose `exclusions.json` says `claim_usable: false` from `neg8.midpoint_lost_primary` counts, and an open-tripwire shows the census never opens that file. End to end, r2-gamma enters the summary and the replication word (`test_r2_gamma_counts_and_enters_the_registered_lines`). |
| A2 GAMMA pairing by round | **pass** | `pairing.py`: §6.2 rules 1 to 3, the S-17 "floor from block 5" label, and provisional pairing before the close. On the closed block, G r1 → A r1/B r1, G r2 → A r3/B r2 and G r3 → A r3/B r3. This holds unit-tested, end to end in serial, and through 3 worker processes. §6.2's worked example passes too. |
| A3 per-session steps, no pooling; §10 | **pass on the fake adapter** | The adapter takes one session (GAMMA also takes its two paired floor results). A recording fake shows exactly one call per session. §10, per quantity and pack: block 5 plus the counting sessions, their mean and sample SD (n − 1), with no ratio and no pooled interval. A session without a value is left out and listed with its reason, and fewer than two values print "not computable (n < 2)" (decision AD-1). Worked examples reproduced: 26.15 / 0.148 J, flagged-inclusive 26.216 / 0.195 J, and §11.1's Δ +0.0667 J with own differences +0.21, −0.13 and +0.12 J. |
| A4 replication word | **pass** | "replicated" only when every counting GAMMA session's outcome word and dbar sign match block 5's. Block 5 `not_estimable` (or no dbar) gives no word. A short pack prints its sentence. Flagged-inclusive words are printed beside and never enter the word. Tests cover §11.2's worked example, a sign change, not_estimable, short and floor-from-block-5. |
| A5 flagged-inclusive index | **pass** | Every collected session appears in the public `session_index` with its admission. Under ruling 2, every session that meets §11.4 (i) (no W1/W2/W3/S1), counting or not, is analysed, and (ii) (at least 5 kept units per stratum, defined b_op, defined drift screen) is read from its results. A session failing (i) is recorded with its structural reason and is not analysed. P1 to P4 and D1 are ignored. Ruling 2 also reports that r2-alpha was a smoke hold and never collected, so the fixture of the closed block has the nine sessions. A synthetic non-counting `r5-alpha` exercises the rule: it is **added**, "including sessions that did not count (n = 5)". `test_every_collected_session_is_indexed` covers added, not_computable from the analysis (an N2-flagged session is analysed and judged by its drift word), W2 and S1. |
| A6 structure-only public bytes | **pass** | The public bytes are stdout (record path and digest), stderr (`node <kind>:<pack>:<session> <status>`) and `B6-ANALYSIS-RECORD.json`. `require_structure_only` refuses any float, any decimal-looking token and any outcome or replication word before writing. Restricted flag codes appear only as a count, and outcome-word refusal tokens become `restricted_token`. Adapter calls run with Python- and descriptor-level streams sent to restricted logs. An unexpected driver exception's text goes to restricted custody. Restricted outputs are canonical JSON at `restricted/objects/<sha256>.json`, named in the record by digest. A subprocess test with a fake that prints numbers and outcome words on every stream finds only structure in the public bytes, at 1 and 3 workers. |
| A7 end-to-end run | **partial: synthetic through the fake; real L9 owed** | The nine counting sessions, plus a synthetic non-counting session where a test needs one, run end to end through census, pairing, DAG, lines, custody and record. This works in serial, parallel, session and release modes. Serial and 4-worker custody trees are byte-identical. The run through the real L9 programs waits for L9's per-session seams (ruling 4). §13's full-size synthetic run through the real stage chain is owed, not skipped. |
| A8 only WRITE_SCOPE changed | **pass** | `git diff --stat 991358f73..HEAD` lists only `joulewise/b6/analysis/**`, `scripts/b6_analyze.py`, `tests/b6/analysis/**`, `configs/b6/analysis/**` and `.codex-report/B6-AN-1.md`. `joulewise/b6/analysis_lane.py` equals 991358f73, and a test checks it. |

Verification run (Linux, Python 3.13.17):
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b6/analysis -t .`, which
ran 82 tests, all OK. `tests.b6.test_lane_adapters` has 2 environmental failures (`/bin/zsh` and
`/opt/homebrew/bin/python3.13` are absent here), and they are identical on 991358f73.

## FILES CHANGED

- `joulewise/b6/analysis/__init__.py`: package statement.
- `joulewise/b6/analysis/census.py`: A1. The loop-acceptance census, its structure record and registered order.
- `joulewise/b6/analysis/session_index.py`: the block-6 session index (`joulewise.b6_session_index.v1`). It is built
  from the census and `session_paths.for_session` (S-2). It binds the harvest-record digests and the two loop files,
  and refuses a stale or changed index.
- `joulewise/b6/analysis/pairing.py`: A2. §6.2 with S-17 and provisional pairing.
- `joulewise/b6/analysis/adapter.py`: the **only** L9 call site. It holds the `SessionAnalysis` contract (with
  restricted `reasons` for missing values), `L9ProgramAdapter` (which validates the session index), and `L9_TARGETS`.
- `joulewise/b6/analysis/schedule.py`: the DAG executor (process pool, serial at 1 worker) with per-node stream
  capture.
- `joulewise/b6/analysis/summary.py`: §10 and §11.1, with AD-1.
- `joulewise/b6/analysis/replication.py`: §11.2.
- `joulewise/b6/analysis/inclusive.py`: §11.4 (i) before analysis and (ii) from the analysis.
- `joulewise/b6/analysis/public.py`: custody preflight, content-addressed restricted objects and the structure guard.
- `joulewise/b6/analysis/slots.py`: S-11, S-9, S-15 (the carry and the GAMMA refusal) and S-16.
- `joulewise/b6/analysis/driver.py`: orchestration, the blind-dry-run, session and release modes, and the completeness
  rule (`sessions_unaccounted`).
- `scripts/b6_analyze.py`: the command line, with `analyse`, `index` and `slots`.
- `configs/b6/analysis/driver.json`: packs, contrasts, target, §11.4 (i)'s code groups (from §8.2) and F_min.
- `tests/b6/analysis/{__init__,fakes,test_census_pairing,test_lines,test_driver,test_slots_cli}.py`.
- `.codex-report/B6-AN-1.md`: this report.

## L9 INTERFACE TARGETED

- `lane/2026-10-27-l9-2` at **8ad47455ce55203949ea77a3ee330432d5a48101**, read with `git show` only; nothing is
  imported from this tree. The functions targeted are in `adapter.L9_TARGETS`, all in `joulewise/b5_analysis/dry_run.py`:
  - **Floor session:** `step_1`, `step_2`, `step_3` (`kept_units.load_kept_units`), `step_3b`, `step_4`
    (`scripts.extract_detection_floors.main` with `steps.classify_step4_exit`), `step_10`
    (`scripts.issue_reported_energy.main` with `require_step10_admission`) and `step_11`.
  - **GAMMA session:** steps 1 to 3b, `step_5` from the paired floor sessions' step-4 reports, then `step_8`, `step_6`,
    `step_9`, `step_9b` and `step_11`.
  - **Block 5:** its release record and outputs.
- **Seams L9 will add (ruling 4):** `run_floor_session(request, custody, index=)`,
  `run_gamma_session(request, alpha, beta, custody, index=)` and `released_block5_session(pack, block5_custody)`.
  Each returns a `SessionAnalysis`. Until they exist the adapter refuses with `l9_absent_from_checkout` or
  `l9_session_seam_absent`. Once they exist, it refuses without a valid session index (`session_index_absent`,
  `session_index_digest_mismatch`, `session_index_malformed`). Calling L9 per session inherits L9-2's calibration
  cache and parallel steps 1–2.

## DECISIONS I MADE

**AD-1 (§15 style; lead ruling of 2026-10-27; for the next dated §17 entry). §10 when a session lacks a quantity.**
*Text:* For a printed quantity Q, a session in which Q is undefined (for example a contrast whose outcome is
`not_estimable`, or a cell whose estimator does not exist) is left out of Q's between-session summary. The summary
prints n as the number of sessions with a value. Each session left out is listed with its reason. When fewer than two
sessions have a value, the summary prints "not computable (n < 2)" and no mean or deviation.
*Rests on:* §10 ("no claim rests on it"; the summary is descriptive) and §11.3 ("Between-session statements use the
summary of §10 and say how many sessions it rests on"). The registration is silent on a missing value. Withholding the
summary would hide information, and an unlabelled smaller n would misstate what it rests on.
*Effect:* changes no registered number or counting decision. The §11.1 table uses the same rule for the block-6 mean.

Other decisions:

1. **Analysis set and completeness (ruling 2).**
   - The driver analyses every collected session that meets §11.4 (i), counting or not.
   - It records sessions failing (i) with their structural group (W1, W2, W3 or S1), unanalysed.
   - §12.3 item 3 counts as met when every session is analysed without tooling refusal or recorded with its
     structural reason. A pending-harvest session, or an analysed session with a tooling refusal, is listed in
     `sessions_unaccounted`, and the run exits 2.
2. **A non-counting GAMMA session** analysed for §11.4 is paired by the same §6.2 rule over counting floor sessions.
3. **An outcome-class stop is a completed result.** Its values feed the lines and its dependents run, with exit 3, as
   in L9.
4. **Public flag codes:** a code shows only when its catalog `blinding` is STRUCTURE. Any other code is counted as
   `restricted_codes_removed`.
5. **The public record carries no worker count, time or host**, so serial, parallel and release runs byte-compare.
   Release compares the commit, config digest, census, pairings, index, node structure, line refusals, unaccounted
   sessions and every restricted object digest.
6. **S-15 defines no arithmetic.** The per-phase definition is block 5's S-15 commit, which is absent at the L9 target.
   The driver carries `whole_machine/` values from the adapter, summarises them, prints the boundary sentence and
   refuses them on GAMMA.
7. **S-11 input:** automation-supplied non-claim smoke rows. Claim rows and non-target phases are refused, and a
   missing T_phase never defaults. S-9 = 1.9 / (4 × T_phase), which reproduces the registration's 0.238 W and 0.0720 W
   comparison values.
8. **Session index location:** the session index locates sessions with the loop's registered layout (S-2,
   `session_paths.for_session`). It hashes each archive's `harvest.json` without reading a field.
9. **The seat setup from `JouleWise-data` was not run.** The work needs only the standard library and in-tree modules,
   and no real data.

## OPEN ISSUES

- **Owed at integration (A7):** L9's three per-session seams (ruling 4), then the run through the real L9 programs on
  reduced-size synthetic sessions, with the session index from `scripts/b6_analyze.py index`.
- **Owed before the blind dry run (§13, S-14):**
  - The full-size production-shaped synthetic run through the real stage chain.
  - One independent executing review.
  - The two blind executing cold passes of §13.
  - The pin of the analysis commit.
- **Independent recompute, block-6 adaptation (another seat; it shares no code with L9 or this driver).** The
  interface it needs:
  - The census and admissions from the public record's `census` and `session_index`.
  - The pairings from `pairings`.
  - The session locations from the session index.
  - Per session, the restricted `sessions` object's quantity keys (`reported/<model>/<phase>/mean_j`,
    `floor/…/operative_j`, `dominance/…/R`, `contrast/<c>/energy_ratio`, contrasts' `dbar` and `outcome`) to compare
    unrounded under S-13.
  - Per run, phase energies from L9's re-reduced outputs, at 1 mJ.
  - It should emit the same keys, so the comparison is a key-by-key join.
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
    The resolution is the union: L9's four files, plus the b6 list and the `block_six` argument.
  - Consequence: new K-7 records list one more file. Old records keep their pins. Nothing gates, because the record is
    "a record, never a flag".
- **Command line `analyse`:** with the production adapter, it can only refuse until L9's seams exist. It refuses
  `analysis_checkout_not_clean` on a dirty checkout, otherwise it gives a refusal token per node.

## NEEDS_RULING

None open. The lead's rulings of 2026-10-27 settled both earlier items (AD-1 and decision 1). The earlier
model-naming trailer on this lane stays, with no force push (lead).
