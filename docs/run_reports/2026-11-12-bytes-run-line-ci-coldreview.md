# Cold review (Fable 5.2, non-author): PR #738 commits 89e06a64b and 8041c288c

VERDICT: 89e06a64b — ADMIT. 8041c288c — ADMIT-WITH-FIXES. The fixes are wording only: one gate sentence omitted a refusal, and one commit message was inaccurate. There is no code or science defect.

Both commits were reviewed at the branch head 8041c288c (parent 89e06a64b), on synthetic fixtures only.

## 89e06a64b: the NEG-8 omission test under the RL-7a guard

- **F1 (pass).** The repaired test now exercises NEG-8 detection, and it is non-vacuous.
  - The unmodified test passes: OK in 374.7 s.
  - A no-op mutant, byte-identical to the twin, fails at the NEG-8 assertion (376.7 s). The twin exits 0, its output is compared, and 0 rows are above the bar.
  - The faulty mutant passes: OK in 362.7 s. It puts 164 `neg8/` held-out rows above the bar.
  - In both variants the guard ran and admitted.
- **F2 (low, pre-existing).** The test comment overstated how isolated the mutation is. In the faulty run, 2,095 non-NEG-8 rows also move. The assertion filters on `neg8/` held-out rows, so the test is still correct. The comment is fixed in b490b40a4.
- **F3 (low).** The test does not assert a clean NEG-8 baseline; only `test_bytes_world` asserts that. Hardening it is optional and was not taken.
- **F4 (pass).** The guard path is faithful to production, and no bypass was added:
  - the mutant runs through `ample_space_command` → `commitment_command` → `--run-cli`;
  - the symlink resolves to the repo ROOT, so the production `scripts.bytes_commitment` is imported;
  - the only patch is the existing test-process `bc.ROOT`.
- **F5 (pass).** No test-order dependence. The journal admission is committed by `synthetic_checkout`, and nothing later reads it.
- **F6 (pass).** The bound files are untouched: twin `4820dc2e…03de`, estimator `18582818…0a71`.

## 8041c288c: CI fixes

- **G1 (pass, with a wording fix).** "Run metadata" is the right class.
  - `b_fiducial_s` is used on twin lines 1161, 1163 and 1165. It is never printed, written or returned.
  - The value drives two refusals: evidence incomplete, and operative bound narrower. Both are fixed text, written to `anchor_join_status`.
  - The gate sentence named only one refusal. It is reworded in b490b40a4.
- **G2 (pass).** The D-188 row and body are byte-equal to main and sit at main's position. Main has no entry numbered 187. The lane's log is main's minus the entries numbered 189 and 190; b490b40a4's message corrects the earlier claim.
- **G3 (pass).** At 89e06a64b both modules fail as claimed. At 8041c288c, `test_battery_float_sweep` (5) and `test_docs_freshness` (31) are OK.

## Process notes, from the seat

- It ran one `git fetch --dry-run`, which updated no refs.
- It wrote nothing in the target worktree.
- It kept logs in `/Volumes/JW-EXT/scratch/bytes-commit/review/`.

---

# Cold review (Fable 5.2, non-author): PR #738 commit b490b40a4

VERDICT: b490b40a4 ADMIT. The earlier verdicts stand: 89e06a64b ADMIT, and 8041c288c ADMIT-WITH-FIXES, whose fixes are now applied.

## Findings

- **H1 (pass).** `FIXTURE_PACKS_CLOSE` = 1793606400.0 = 2026-11-02T00:00:00-08:00. The clock starts at 2026-10-19T01:00:00-07:00 once wall time is past that date. Before that date, behaviour is unchanged.
- **H2 (pass), executing check.** `test_capture_screen_reachability…test_opening_40ms_reaches_real_screen_and_desk`:
  - OK at b490b40a4 (217.1 s);
  - with the old wall clock restored in-process, it FAILS with "did not reach SESSION_RUN: DONE None" (19.7 s), which is the CI failure.
- **H3 (pass).** The synthetic clock is never compared with wall time, file mtimes or fixture epochs:
  - every clock use in `loop.py`, `driver_lane.py` and `queue.py` is a difference between clock readings, a t0 derived from the clock, or the `end_t0_before` comparison;
  - the fixture epochs (2026-08-08) stay earlier than the clock;
  - the steps of 1801 s and 301 s fall well inside the 14-day margin.
- **H4 (note).** `round_support.py:696` passes `clock=time.time` to another object. This commit does not touch it, and it was not checked.
- **H5 (pass).** The roster migration is faithful. The same chain runs with the same assertions; the four bare-git commands are replaced by `fixture_options`. 3 tests OK (132.4 s); `NINE_MODEL_AGREEMENT` shows 0 above the bar of 239,792.
- **H6 (pass).** The production guard runs. `bc.admit` is called in-process with only `bc.ROOT` patched, and the journal is committed after each of the four admissions.
- **H7 (low, cosmetic).** The held-out analysis receives `--predictions` twice. Argparse keeps the last one, and the two files are byte-identical copies, the same as in the agreement module.
- **H8 (pass).** The wording fixes are applied.

Bound files at b490b40a4: twin `4820dc2e…03de`, estimator `18582818…0a71`.

---

# Cold review (Fable 5.2, non-author): PR #738 commit 569646b68

VERDICT: 569646b68 ADMIT. No fix is required. One scope choice (K4) goes to the research lead as a notification, not a gate.

## Findings

- **K1 (pass).** The registry edits are minimal: one line added, one changed (the guard digest only) and one removed, with no re-serialization. `test_refusal_allowlist` passed 23 tests in 3 of 3 runs.
- **K2 (pass).** The release row is correct.
  - The new guard digest covers the non-bytes condition.
  - NUMBER_INTEGRITY and the existing protects text stay true of the site.
  - For the bytes group, `bc.admit(..., "heldout_keys")` enforces the same protection.
- **K3 (pass).** Removing the stale `b6_unblind.main` row is correct. RL-7a deleted that raise and replaced it with `bc.admit(args, "heldout_rows")`.
- **K4 (pass, note for the lead).** Listing `scripts/bytes_commitment.py` as `not_scanned: analysis` is honest.
  - The file has 37 sites, all provenance refusals.
  - Its callers are the held-out key release, the withheld-row unblind, held-out analysis and the twin's stage-2 guard.
  - A refusal can stop a desk step. It cannot stop a collection or exclude a member or window.
  - Cost of the choice: the census would not notice one of those refusals being weakened. That coverage rests on `tests/test_bytes_commitment.py`.
  - The lead should be told, because RL-86 C09 shows the lead has ruled on scan scope before. If the paper says the census covers the held-out release gate, that sentence should cite the commitment tests instead.
- **K5 (judgment).** By their text, RL-86 and RL-93 do not require a ruling here: no row is added, no category changes, and the reason used already exists.
- **K6 (pass).** `tests/test_agent_identity.py` is verbatim main's post-#712 blob (`0a8cefacef6d…`). The lane's previous blob equals main's pre-#712 blob (`fdd6828e99e8…`). The test passed 14 of 14 in each of 5 runs.
- **K7 (low).** #712 also added five run reports. The test file was its only code change, so the port is complete.

Bound files at 569646b68: twin `4820dc2e…03de`, estimator `18582818…0a71`.

---

# Cold review (Fable 5.2, non-author): PR #738 commit 000a716de

VERDICT: 000a716de ADMIT. No fix is required. The review offers two optional hardenings (M2, M5) and one wording nit (M6); none was taken, to avoid another CI restart.

## Findings

- **M1 (pass).** The guard path is production.
  - Subprocess calls go through `commitment_command`, the `--run-cli` wrapper.
  - In-process calls use `synthetic_checkout`, which patches only `bc.ROOT`.
  - `bytes_analyze.main` calls production `bc.admit` → `verify_commitment`.
  - Only five files under `tests/` change.
- **M2 (pass, static argument).** The expected refusals ("unreleased-heldout", and A4-08's "blocked") still refuse because the keys are unreleased, not because of the guard. Each is followed by a call with the same options that must exit 0, and the guard's inputs differ only by state that is more permissive on the first call. Optional hardening: assert that the refusal text does not name the commitment guard.
- **M3 (pass).** The harness migration is faithful. The repo is keyed by the predictions hash, and the probes assert on exit codes.
- **M4 (low, cosmetic).** `--predictions` is passed twice. Argparse keeps the last, and the two files are byte-identical.
- **M5 (pass).** Exempting the 12 `stage1_verification` receipt fields is honest.
  - They are the guard's receipt, and they are provenance, not estimates.
  - Three fields differ legitimately between the two programs: `checked_utc`, `historical_metadata_revisions_checked` and `analysis_head`.
  - The commitment content is already compared by `compare_commit`.
  - Optional, as an operational check for real runs: compare `stage1_commit` and `predictions_sha256` exactly between primary and twin.
- **M6 (low, wording).** The exemption reason says the receipt is copied into the "held-out" record. The primary also writes it into the post-commit blinded record.
- **M7 (pass).** Inventorying `anchor_narrow` and `anchor_wide` is the minimal, forced edit.
- **M8 (pass).** `init_git_fixture` runs the same init plus the four maintenance-off keys. The import inside the function is right, because the module also runs as a script.
- **M9 (pass).** The rehearsal clock is correct.
  - `BYTES_PACKS_CLOSE` equals the 2026-11-05 close of all 12 bytes packs.
  - One shifted wall-rate clock goes to the Loop, its lanes and the Mailer.
  - `test_bytes_guard_shaped_rehearsal` is OK in 11.4 s.
  - This closes H4.

Bound files at 000a716de: twin `4820dc2e…03de`, estimator `18582818…0a71`.
