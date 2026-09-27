# ISSUANCE-CUSTODY-OUTSIDE-REPO-01: Opus 5.5 contract lens (gate rows 2 and 6)

Seat: Opus 5.5, read-only, not an author. Candidate: `c84b1dc2` (the seat commit `cc8346c2` merged with main `b69c39eb`), diff `git diff b69c39eb c84b1dc2`.
Contract: `30-lead-synthesis.md` (design C, rulings 1–5), `14-fable-consult.md` §5, and R1–R9 of item 6(d) in `../60-prepare-record/00-refusal-branch-final-statement.md`.

**Outcome-blind compliance.** I opened no W1 or W2 value. For R8 I parsed each ledger line in memory and kept only `custody_locator`, `attempt_id` and `session_id`; no other field was printed or stored. The naming function `lstat`s the two primary files, which tests existence only; no custody file was opened. Every run used `/opt/homebrew/bin/python3` with `PYTHONDONTWRITEBYTECODE=1` on `git archive` copies under `/tmp/corpus-lens-opus-77b1bee2/`. No repository was written except this report file, which the caller asked for.

## Executed evidence

| # | Check | Result |
|---|---|---|
| E1 | `git diff --stat b69c39eb c84b1dc2` | 3 files: the issuer, `tests/fixtures/epoch_bootstrap/build.py`, and the new `tests/test_issuer_corpus_root.py`. No change under `configs/` or `joulewise/`, to the verifier, to the reissue tool, or to `tests/test_issue_calibration_acceptance_generation.py` (a `--stat` over those paths is empty). |
| E2 | Merge fidelity | The +/- lines of `git diff 670756f3 cc8346c2` are identical to those of `git diff b69c39eb c84b1dc2`. The base issuer's sha256 is `ceaf3807…7105`, the digest the statement cites. |
| E3 | `_repo_relative_custody` | Its body is byte-identical between base and candidate. The only difference in the extracted range is the next `def` line. |
| E4 | New tests on the candidate | `Ran 8 tests … OK`. |
| E5 | The same new tests (plus the new fixture builder) on the **base** issuer | RED: every test that uses the flag fails with `unrecognized arguments: --corpus-root`; direct calls fail with `has no attribute '_corpus_relative_custody'`. The `None` subtest (legacy refusal "lies outside the repository") passes on base, as it should. R7's fail-before/pass-after test holds. |
| E6 | Existing suites on the candidate: `test_issue_calibration_acceptance_generation` + `test_reissue_calibration_acceptance` + `test_calibration_bracketing` | `Ran 255 tests in 337.216s`, `OK (skipped=1)`, exit 0. Outside the seat's sandbox the live `sysctl` probe also passes, so the seat's flag F1 was environmental. |
| E7 | **Flag absent, same fixture, base vs candidate** | Output bytes identical (sha256 `b9c1351e…f46a` both). Behaviour without the flag is byte-identical. |
| E8 | **Flag absent vs present, same ledger** (fixture built with custody parent = repo root, so both modes name the same string `plan-w1/runs/instrument_validation/plan-w1-d01`) | Only 2 leaves differ: `derivation_notes.member_custody` and `derivation_sha256`. `derivation_input_sha256`, `ledger_cutoff`, member order and `source_directory` are equal. This is R2/T2 in executable form. |
| E9 | R8 value-blind probe on the real locators (candidate function, root `/Users/edr/night-custody`) | 24 rows, 24 distinct, **24 accepted**. All have the shape `<session>/runs/instrument_validation/<session>-dNN` (list matches the seat's report exactly). Wrong roots refuse 24/24 each: `/Users/edr`, `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927`, the run checkout, `/Users`, `/`. For contrast, the old function against the run checkout refuses all 24. |
| E10 | My own adversarial naming-function inputs (23 cases, synthetic) | All behave as specified. Refused: a root that is a file, a missing root, a root that is too high, too low, `/` or a relative root; a locator with trailing `/.`, a NUL, a backslash, or case-variant session text; a session directory that is a symlink to another session; a row's session not equal to the first part; an empty capture id; a primary file that is a directory, a symlink (even inside the same parent), or missing; a missing capture directory; a locator through the `/tmp` symlink; a non-string locator. Accepted: the baseline; a root given through a symlink alias (same stored string); a capture nested deeper in the middle part (N3). |
| E11 | My own adversarial `verify-members` inputs (16 cases) | Baseline 20 PASS, exit 0. Each of these exits 3 with exactly the tampered member FAIL: an absolute stored path; a member pointing at another member's directory, with or without the other's digests; a prior row with its session or disposition altered; a member entry that is a string; a `member_id` of `../x`; a primary file replaced by a FIFO (no hang, because the `lstat` regular-file check comes before the open); a night directory that is a symlink inside the root (10 FAIL). A missing root or a root at the session level gives 20 FAIL. A list artifact, non-JSON or an empty member list gives `REFUSED` with the exception type name only. Output lines hold only the member id and PASS/FAIL, never a value. A duplicated member entry passes 21/21 (N6). |
| E12 | Lens mutation cuts against the 8 new tests | Ledger-snapshot load at `:1752` switched to the corpus root: **caught** (9 failures). Note removed: caught. **M1: `authenticate_battery_epoch(repo_root=Path(args.corpus_root or args.repo_root))` at `:1813`: SURVIVES** (S1). The `len(parts) < 2` guard dropped: survives (N5). The locator `is_dir()` check dropped: survives (the `resolve(strict)` check and the primary-file `lstat` still refuse a regular-file locator). |

## Answers to the brief

**1. Design C fidelity.** Every site is implemented and nothing is out of scope.
- Site 1 is `_corpus_relative_custody` at `issuer:926-960`: canonical raw-string checks before `Path()`, a canonical-locator check (`resolve(strict) == path`), containment, first part = session id, last part = capture id, at least 2 parts, and both primary files canonical regular files.
- Site 2: `_select_members` gains `corpus_root=None`. There is no fallback: the choice between the two functions is made once, by `corpus_root is not None` (`:1303-1307`). A pre-pass names every valid row before `_read_member_evidence` is reached (`:1266-1275`). The ruling-4 order holds, and tests `:143-177` prove it by mocking the value reader to raise.
- Sites 3 and 4: the call site `:1888`, and the parser `--corpus-root` with `type=Path, default=None` (`:2527-2530`).
- Site 5: `verify-members` (`:2364-2430`).
- Site 6: fixed-text `member_custody` with no absolute path (`:2154-2158`). T7 is asserted at test `:99`.
- Site 7: the fixture builder.
- Ruling 1 (the flag's name) holds.
- Ruling 3, guard F2, holds in code. Within `_prepare_candidate`, `args.corpus_root` appears only at `:1888` (naming) and `:2158` (note presence). The ledger, pin, battery and git lookups keep `args.repo_root`. E8 confirms it on the non-Revision-5 path.
- Ruling 4 holds (E10, E11).
- No scope creep. `tests/test_issue_calibration_acceptance_generation.py` is untouched. The one deviation is noted in N1.

**2. Byte identity.** Answered by E3, E6, E7 and E8. The flag's presence or absence cannot move `derivation_input_sha256` for a fixed ledger, because the stored path is not an input to it. Member selection and order come from the unchanged loop; the pre-pass only adds refusals.

**3. Data-dependent drop or root choice (R1/R5).** None found.
- The naming inputs are three ledger path and id fields. No measured value is among them.
- A naming failure raises and refuses the whole run. There is no `continue` or fallback, and the members come from the loop, not from the dict.
- One root value is accepted per ledger (E9, E10).
- A relative, `..`, absolute, symlinked or other-session locator is refused (E10). So is any stored path of those kinds in `verify-members` (E11).

**4. R8.** Answered by E9: 24 accepted, and every wrong root refuses 24/24.

**5. Tests.** They are defect-shaped (E5), and the named cuts go RED in the seat's table and in E12. The missing cases are S1 (F2 on the Revision-5 path) and N5 (len<2). There is no committed same-ledger R2 equivalence test like E8; see S1.

## Findings

**BLOCKER:** none.

**SHOULD-FIX**
- **S1. Guard F2 is untested on the Revision-5 path, which is the production path for W1/W2.**
  - `tests/test_issuer_corpus_root.py:72` patches `REVISION_FIVE_EPOCH` to `{}`, so `authenticate_battery_epoch` (`issuer:1811-1815`) never runs with the flag.
  - Mutation M1 routes the battery epoch to the corpus root, and all 8 tests stay green.
  - The assertions at test `:102-104` (no `.git` or ledger under the parent) are fixture facts, not guards.
  - The code is correct today (E8 and the `grep` above), and the ledger-load path is covered (E12).
  - Cure, at bench scale and before the cold gate:
    - Add one Revision-5 fixture test (`verdict_records`) whose corpus parent holds no pin or battery records, so that M1 goes RED.
    - Add the E8 same-ledger equivalence test (custody parent = repo root; flag absent vs present differ only in `member_custody` and `derivation_sha256`; `derivation_input_sha256` equal). This is Fable T2 and F2.

**NIT**
- **N1.** Site 5 reimplements the member check (`issuer:2364-2408`) instead of calling `authenticate_derivation_corpus`, as Fable §5.1 site 5 worded it. The reimplementation is justified: it adds the no-follow reads of ruling 4 and the session binding, and prints no values. Its evidence parse is lax `json.loads`, not the reissue tool's strict lexeme parser, but digest equality is checked first. State the deviation in the PR.
- **N2.** The `--repo-root` help at `issuer:2521-2525` still says member paths are recorded relative to it. Fable F11 asked for "unless `--corpus-root` is given".
- **N3.** The middle part `runs/instrument_validation` is not enforced, so a nested capture directory is accepted (E10). This is within the spec; the digests remain bound by the ledger.
- **N4.** `corpus_paths` is keyed by `attempt_id` (`issuer:1269-1275`). Duplicate valid attempt ids would overwrite silently. Key it by `sequence`, or refuse duplicates.
- **N5.** `len(parts) < 2` has no killing test (E12). The refusal message at `:949-950` names the session check even when the cause is length. The case is reachable only if session id = capture id.
- **N6.** `verify-members` passes duplicated member entries. Uniqueness is the validator's job; the command could say so, or count ids.
- **N7.** The committed test hard-codes the seat's scratch path (`tests/test_issuer_corpus_root.py:21`, `/tmp/corpus-root-impl-77b1bee2`). Use the `tempfile` default.
- **N8.** The pre-pass also refuses on a bad path in a valid row that the replay later excludes. This is stricter than needed and consistent with ruling 4 (a failure refuses the whole run). Disclose it in the PR.

**Verifiability for a future reader.** It holds.
- The artifact stores relative `<session>/…/<capture>` strings, and the note names the command.
- `verify-members` passes after the corpus is relocated (seat test `:179-189`; my E11 used a copied tree).
- It fails on a flipped byte.
- It needs only the artifact and the restored night directories under any parent.
- Replaying the ledger still needs the ledger archive, which is lane ISSUANCE-ARCHIVE-PACKET-01 (out of scope, and registered).

LENS: PASS
