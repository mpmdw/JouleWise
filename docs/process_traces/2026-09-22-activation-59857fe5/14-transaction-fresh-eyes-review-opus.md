# Fresh-eyes review — D-138 r7 re-issue on the A267/A269 base (row 10)

Head `0f8a395d`, worktree clean. Scope: `git diff 56ea8ae0..0f8a395d` (ten paths).

## Q1 — D-138 clause (3): pin moves only, in the five test paths?

Yes for all five. Every hunk is a generation/id/digest move or a new
counterfactual; no assertion about a live artifact or a science value is
weakened. Deciding evidence:

- `tests/test_calibration_bracketing.py:607-628` — the live-default assertion
  moves r6→r7 **and gains an assertion** (`ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH`
  still hashes to its own pin). Strictly stronger. `:3331/:3354/:3370/:3379`
  re-key the three D-102 counterfactual contexts to the ACTIVE id — these only
  select which registry row the counterfactual perturbs; the refusal assertions
  (`assertFalse(_valid_acceptance_bound(...))`) are untouched.
- `tests/test_calibration_exits.py:1451, 3630/3634, 5398` — path of the
  acceptance copied into the **private synthetic** writer repo, then re-keyed by
  `_rekey_private_writer_acceptance`. Explicitly the fixture case D-138 permits.
- `tests/test_capture_pipeline_era.py:266-291` — renamed to r7, asserts r7 is
  recognised, **adds** an assertion that r6 stays recognised, and moves the
  negative counterfactual to the still-unissued r8. Coverage increases; the
  bracketing property (an unissued generation is refused) is preserved.
- `tests/test_powermetrics_fiducial.py:1568-1578` — path, file sha256 and
  `acceptance_id` moved to r7; `derivation_corpus.n == 17` and the decimal
  derivation assertions below are unchanged.
- `tests/verify_calibration_acceptance_corpus.py:64-66` — pure addition: r7
  aliases the r3 expectation row, same as r5/r6 do. Nothing removed.

No hunk in these five files deletes or relaxes an assertion. (The only deleted
assertion line, `test_calibration_bracketing.py`, is the r6 `acceptance_id`
equality, replaced one line later by the r7 equality plus the new r6-retention
check.)

## Q2 — r7 vs r6 leaf diff

Ran a recursive leaf diff (428 leaves r6, 426 r7). **Complete** changed set:

| leaf | verdict |
|---|---|
| `.acceptance_id` r6→r7 | allowed |
| `.derivation_sha256` `18d09aa9…`→`2c7dab72…` | allowed |
| `.prospective_rederivation.estimator_code_sha256["joulewise/uncertainty_evidence.py"]` `257cda08…`→`b583f35a…` | the one estimator pin |
| `.derivation_notes.generation` | describes r7 |
| `.derivation_notes.predecessor.{acceptance_id, file_sha256, derivation_sha256, relative_path, relationship}` | describes r7 |
| `.derivation_notes.reissue_delta.changed_estimator_pins["joulewise/uncertainty_evidence.py"].{predecessor, reissued}` | describes r7 |
| `.derivation_notes.reissue_delta.changed_estimator_pins["joulewise/reduce.py"].{predecessor, reissued}` **removed** (the −2 leaves) | correct: r6 rotated two files, r7 rotates one |
| `.derivation_notes.reissue_delta.science_neutrality_evidence` | describes r7 |

Nothing else moved — no member table, bound, screen, disposition, epoch or
`derivation_corpus` leaf. Independently verified with the production rule
`calibration_bracketing._canonical_sha256`: r7 recomputes to `2c7dab72…`
(MATCH) and r6 to `18d09aa9…` (MATCH), so the recorded `predecessor.
derivation_sha256` is r6's true derivation hash and `predecessor.file_sha256`
`0227bca3…` is r6's true file hash (`shasum -a 256`). `b583f35a…` equals the
actual `joulewise/uncertainty_evidence.py` at this head.

## Q3 — pin sites and ACTIVE selection

`shasum` of the r7 file at `0f8a395d` = `9c3a29f61a6f72bb…`. Exactly two tree
sites pin it, both correct and both naming r7:
`joulewise/calibration_bracketing.py:142` (`ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256`,
used by `ISSUED_ACCEPTANCE_REGISTRY`) and `tests/test_powermetrics_fiducial.py:1574`.

The r6 file sha `0227bca3…` appears at four tree sites, all of which *should*
name r6 and do: `calibration_bracketing.py:132` (retained registry row),
`tests/test_d117_v3_family.py:24` (the r6-bound D-117 v3 pack family — frozen
mint-time binding), `tests/test_mint_floor_artifact_generalized.py:6288`
(synthetic bytes under "must not move any issued acceptance field"), and a
process trace.

`ACTIVE_ACCEPTANCE_ID` / `DEFAULT_ACCEPTANCE_BOUND_PATH`
(`calibration_bracketing.py:196-197`) now name r7; r6 is retained as
`ANCHOR_V3_R6_*` with its own registry row and `_D102_GENERATION_DERIVATIONS`
entry (`:379`), and `arm_readiness._issued_d079:6217` **adds** r7 without
removing r6. Ruled history preserved.

## Q4 — interaction with the A267/A269 code underneath

`git diff --stat 447fd6bf..56ea8ae0 -- <the ten paths>` is **empty** — verified.
The fix rounds moved nothing under these five commits, so the cold-gate-#3
review carries to the new base for those paths. The one semantic coupling —
r7 pinning `uncertainty_evidence.py` at `b583f35a…` — holds: that is the file's
actual digest at `0f8a395d`, i.e. the A267 head the fix rounds froze.

## Q5 — what a merge reviewer must also see

No "DRY RUN", scratch-branch or `/tmp` wording appears in any tracked file
content changed by the five commits (the `dry-run` hits in `arm_readiness.py`
are the pre-existing arm-rehearsal receipt domain; the `/private/tmp` constants
at `tests/test_calibration_bracketing.py:116-118` predate this diff). "DRY RUN"
in the five commit subjects is the known, accepted case.

### Findings

**SHOULD-FIX (dependent-pin completeness — the D-138 clause (3) atomicity edge).**
Three sibling test modules stage the *live* acceptance into a private synthetic
repo by filename, exactly as `tests/test_calibration_exits.py` does, and were
**not** moved to r7 while `test_calibration_exits.py` was:
- `tests/test_calibration_writer_crash_matrix.py:270-284` — worst case, because
  the tracked comment is now factually wrong: *"It copies the LIVE issued
  generation … because that is what the production loader resolves by default."*
  It copies r6, which this transaction demotes.
- `tests/test_validate_powermetrics_fiducial_derivation_only.py:48-51, 249-252`
  (`_ACCEPTANCE_RELATIVE` pinned to the r6 filename; the script under test reads
  `DEFAULT_ACCEPTANCE_BOUND_PATH` at `scripts/validate_powermetrics_fiducial.py:380, 540, 939`).
- `tests/test_arm_readiness_evidence_author.py:120-130` — the fixture allowlist
  comment says "any retained n17 r3-r6 issuance" and stops at r6, so a successor
  pack naming the now-ACTIVE r7 has no file available.

These either break under the moved default or silently exercise a superseded
generation while claiming to exercise the live one. **None of the three is in
the quick tier** (`scripts/quick_suite.py` selects on a 5 s weight; all three are
heavy writer/live modules), so the "quick tier PASS 153 modules" in `0f8a395d`
does not discharge them. Confirm the magistrate's thirteen-module run includes
all three before merge; if it does not, that is the gap to close.

**NIT.** `tests/test_reduce.py:2098-2112` asserts the live `joulewise/reduce.py`
estimator pin by reading the **r6** file. It still passes (r7 carries the same
`reduce.py` pin and r6 stays byte-identical), but it reads a superseded
generation as the source of truth for a live pin and will silently go stale at
the next rotation that touches `reduce.py`.

**NIT.** `tests/fixtures/epoch_continuation/s9-*.json:4-5` record
`reference_envelope.acceptance_id = …_r6`. Correct as frozen witness output, and
`tests/test_epoch_equivalence_check.py` resolves `ACTIVE_ACCEPTANCE_ID`
symbolically so it follows r7 automatically — but `scripts/epoch_equivalence_check.py:151`
now *requires* r7, so an auditor replaying an s9 witness against the live tool
will get a generation refusal. Worth a line in the transaction record.

**Verdict:** the five commits are a clean, correctly-recomputed pure pin delta —
no science value moves, no assertion weakens, no overlap with the A267/A269 fix
rounds; MERGE once the thirteen-module run is confirmed to cover
`test_calibration_writer_crash_matrix`, `test_validate_powermetrics_fiducial_derivation_only`
and `test_arm_readiness_evidence_author`, whose r6 staging the transaction left behind.
