# BFG-D gate-ledger row 6 — Opus 5.5 counter-review of merge candidate `b2c31e5b`

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), fresh (not an implementer, not a prior lens), one foreground session in worktree `JouleWise-wt-ed17a643-bfgd-opus` at HEAD `aa5d8c8c`. That HEAD is `b2c31e5b` plus the charge file only: `git diff --quiet b2c31e5b HEAD -- joulewise scripts tests configs` exits 0. Session date 2026-09-26.

**Verdict: FIX-FIRST on one MATERIAL item (M-1), a loader history check that is 2 lines plus one test.** Every other point is MERGE-ready. I found no route by which a charging, stale, missing or custody-failed window counts as evidence, and no route by which a clean window is dropped after B is read (Q2). M-1 cannot produce a wrong number. It is a fail-closed liveness trap: the repository's normal PR merge is `--no-ff`, and the first time a harvest verdict reaches `main` that way, every consumer refuses that window for the rest of the epoch.

## 0. Contamination disclosure

- **Loaded by the harness without my choosing:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers only). A system reminder supplied the git status and five commit subjects.
- **Not opened:** any memory file, `RUN_STATE.md`, `TASK_QUEUE.md`, any council log, or anything in `/Users/edr/night-custody`, `~/Library/LaunchAgents` or the canonical checkout, apart from the read-only `.venv` interpreter at `/Users/edr/code/JouleWise/.venv/bin/python`.
- **Read in the packet:** `31-final-pass-charge.md`; `00-…` (all of it, §5 in full); `06-…` §4.1–§4.12; `29-…`; `30-…`; `15-…` §4 and §6; `18-…`, `20-…`, `24-…`, `26-…` (lead contracts); `23-…` §3; and `11-review/03-opus-contract-lens.md` §5 M-1. The last was read only after I had found and reproduced M-1 independently, to learn why the ruled command had been changed.
- **Code read at `b2c31e5b`:**
  - `joulewise/battery_float.py`, all of it.
  - The full diffs of the writer (`scripts/validate_powermetrics_fiducial.py`), `night_gate.py`, `evidence_night.py`, `night_agent_install.py`, `run_night.py`, `arm_readiness.py`, `arm_readiness_evidence_t0.py`, `controller.py` and `calibration_ledger_backfill.py`.
  - In the issuer, `issue_calibration_acceptance_generation.py:1260-1660`.
  - In `calibration_ledger.py`: `_head_pin`, `_authenticated_head_pin` and the `finalized_slots` construction.
  - The paper tool's corpus selection, the derivation chain's writer invocation, and the runbook diff.
- **Process deviation, disclosed:** my second test command went past the 600 s tool limit, and the harness moved it to the background on its own. I launched nothing in the background. I read its output file when it finished (§2, E11).

## 1. Summary table

| # | Tier | Finding | Blocks merge? |
|---|---|---|---|
| M-1 | MATERIAL | `load_committed_verdict` uses `git log --full-history` without `--no-merges`. An honest harvest commit that reaches the issuing checkout through an ordinary `--no-ff` merge then counts as "2 commits, 1 adding", and the verdict never authenticates again. This is an unruled lead fix (FX-3) that departs from ruled text §4.3 item 2 and is not among the seven decisions put to the gates. | **FIX-FIRST** (dictated closure, §6) |
| N-1 | NIT | R2-8 reverses one sentence of PARSER-ESC §4 ("a present key … of the wrong type records `None` as today"). Contract `18-…` says "none of them reverses the ruling". I affirm the substance; the record should say it reverses that sentence. | No |
| N-2 | NIT | The sweep row for the paper tool says "Revision-5 roots are outside its inputs". That holds only for the default `--corpus-root` (`/Users/edr/code/JouleWise`); the tool reads whatever root it is given. | No |
| N-3 | NIT | In logical-test mode the writer substitutes `tests/fixtures/battery_float/float.ioreg` and re-stamps it fresh, so the pass is synthetic, and the evidence carries no marker that says so. This is unreachable from the pinned chain, and a real sampler cannot complete the logical ack protocol. | No |
| N-4 | NIT | The PR body does not exist yet (`gh pr list --head feat/2026-09-25-bfg-d --state all` returns `[]`). BFG addendum §5.3 item 8 and obligations §4.10 item 10 require its statements. This is a merge-time obligation, not a code defect. | Condition on merge |

## 2. Executed evidence

| # | Command / probe | Result |
|---|---|---|
| E1 | `git merge-base origin/main b2c31e5b`; `git rev-parse origin/main` | Both `cab01506da81…`. The PR diff is `git diff origin/main b2c31e5b`. |
| E2 | Pin proof against main: `git diff --stat cab01506 b2c31e5b -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs scripts/paper_anchor_correction_quantified.py` | **Empty.** |
| E3 | The same paths against `c6814dd8`, plus `git log --oneline c6814dd8..cab01506 -- configs` | The only difference is the registration file (+20/−2). Its two commits are `23dd9909` (the #418 seal) and `ad7565a7` (the A-R5b append), both on main. |
| E4 | The registered A-R5b text in `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, diffed (blank lines ignored) against the ruled §5.8 block quote in `00-…` | **IDENTICAL** (17 lines each). |
| E5 | The decision-log A-R5b-1 entry, diffed against the `06-…` §4.8 code block | **VERBATIM.** |
| E6 | `shasum -a 256 scripts/paper_anchor_correction_quantified.py`; the results-registry line 791 | `3844a8f1…d303f1` on both. `git diff --stat c6814dd8 b2c31e5b` on the file is empty. |
| E7 | `ESTIMATOR_CODE_PATHS` (`calibration_bracketing.py:206-211`) | `powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`. The writer is not an estimator pin. `REVISION_FIVE_EPOCH` (`:279-286`) has no code-digest field. |
| E8 | Writer stamp order at `b2c31e5b` | The pre-observation is at `:2269-2270`, right after `AFTER_CUSTODY_DIRECTORY_CREATION` (`:2268`). `pre_spawn = clock.stamp()` is at `:2337`, and no `clock.stamp()` comes earlier. `post_parse` is at `:2494`. The post-observation is at `:2497-2498`, at function scope after the `with` block. The only path that writes `instrument_evidence.json` is `:2656`. `battery_float` is set at `:2629`, before `status="invalid"` can be set (`:2632`), so valid and ordinary-invalid rows both carry it. Between the post-observation and the evidence write, the only exit is `finalize_abandoned`, which writes no evidence. |
| E9 | Real `battery_float.load_committed_verdict` on two scratch repos. The record binds a slot and a pin, and the adding commit changes the pin. | Linear harvest commit: `LOADED`. The same commit merged into a moved `main` with `--no-ff`: **`NoRecord(path history is not a single adding commit (2 commits, 1 adding))`**. (M-1) |
| E10 | The real loader over five histories: as shipped, and with the cure (its git calls wrapped to add `--no-merges`, plus an adding-blob == HEAD-blob check) | See the table in §4 M-1. The cure accepts both honest shapes and refuses all three tamper shapes. |
| E11 | `python -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep tests.test_revision_five_b_readers` | `Ran 71 tests … OK`. |
| E12 | `python -m unittest tests.test_issue_calibration_acceptance_generation tests.test_calibration_cadence_report tests.test_night_gate tests.test_evidence_night tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_arm_retry tests.test_acc_25g83_rev5 tests.test_epoch_continuation tests.test_epoch_equivalence_check tests.test_t0_rehearsal` | `Ran 755 tests in 1004.707s … OK` (auto-backgrounded by the harness at 600 s; read from its output file on completion). |
| E13 | `grep -n merge tests/test_battery_float.py` | One merge test, `:504` `test_merge_branch_modify_then_restore_is_no_record` (a tamper case). **No honest-merge test.** |
| E14 | Where Revision 5 captures land: the derivation chain `:261` `--output-root "$RUNS_ROOT/instrument_validation"`; `gen_derivation_night.py:557` `runs_root = <custody_root>/runs`; runbook `:380` `NIGHT_ROOT=/Users/edr/night-custody/$PLAN_ID` | Revision 5 roots sit under `/Users/edr/night-custody/…`. They are never under the paper tool's default root. |

## 3. The seven lead decisions

1. **FX-2 (`battery-verdict` authenticates the working-tree pin; consumers add check 5): AFFIRM.**
   - The ruled order cannot run as written. §4.9 (iii) runs `battery-verdict` with `require_committed_pin=True`, but the pin it needs is committed only at (iv), together with the verdict (Astra B2).
   - The substitute is sound. The writer still refuses unless its snapshot is head-equals-pin (`refuse_ledger(snapshot)` after the load). It requires `--head-pin` to be the repo's own `configs/calibration/calibration_ledger_head.json` (`issuer:1589`). Consumers require that the adding commit changed that pin and that the pin at that commit equals the record's `ledger_head` (`battery_float.py:613-626`). Tests `test_battery_float.py:478,486` and `issuer tests:2837-2845` cover it.
   - Soundness does not rest on the pin anyway. The record must agree with a recomputation from ledger-authenticated bytes (`compare_verdict`), so no pin timing can manufacture an exclusion.
2. **R1 liveness bound 610 s: AFFIRM.**
   - The old constant was 600 = 11 × 45 + 105. The new ioreg site runs under its ruled 10 s timeout, not 45 s: `_PROBE_TIMEOUT_OVERRIDES` (`arm_readiness_evidence_t0.py`) maps `IOREG_BATTERY_ARGV` to `PROBE_TIMEOUT_S = 10`, and `_fresh_probe` → `_execute_probe` uses that override. So 11 × 45 + 10 + 105 = 610 is the derivation that matches the code.
   - The literal 645 (12 × 45 + 105) would be a bound on a probe that does not exist. A tighter bound can only add refusals.
3. **R2-8..R2-11 adopted without an addendum: AFFIRM, with N-1.** Each moves only toward "not a pass" or "refuse", and each is decided from instrument bytes before any B:
   - **R2-8** matches the registered A-R5b text ("a missing, duplicated, malformed or unreadable property … is not a pass"), whose property list includes the recorded keys. Both real captures still pass (E11 covers the fixtures).
   - **R2-9** is in place: the `getsource` pin at `test_battery_float.py:880`, plus the docstring freeze sentence.
   - **R2-10** is in place: `issue_epoch_continuation.py:85-87` refuses Revision 5 before any member read.
   - **R2-11** is in place at every feeder: `observe` refuses `str`; `run_night._probe_runner` and `evidence_night.probe_command` capture ioreg without text mode; `night_gate` and `arm_readiness_evidence_t0` pass `stdout_bytes`; the writer uses `subprocess.run` without `text`.
   - N-1 is a disclosure defect only.
4. **The AST guard misses `importlib` with a computed name (D-161 limitation): AFFIRM.**
   - The guard catches honest drift. A computed module name is deliberate authorship, which D-161 puts outside the threat model.
   - Its effect is also bounded. Even a consumer that bypassed the seam could only misreport. It could not change what `prepare-candidate` issues, because the issuer calls `authenticate_battery_epoch` itself.
5. **Pin proof against `cab01506` rather than `c6814dd8`: AFFIRM.**
   - Executed: E2 is empty. E3 shows the only `c6814dd8` delta is main's own seal and A-R5b commits, and E4 shows the latter is the ruled text verbatim.
   - Taking the proof against the merge base is the correct question: what does this PR change?
6. **C-2(b) reverted; the paper tool dispositioned as pinned-historical: AFFIRM, with N-2.**
   - The file is byte-identical and matches its registry pin (E6).
   - Its default root never holds a Revision 5 capture (E14).
   - Pointing it at a custody root takes a deliberate `--corpus-root /Users/edr/night-custody/…`, an operator act under D-161. A paper tool that reads B also licenses nothing.
7. **Kernel label and test comment follow the rename; decision-log `:11131` left as history: AFFIRM.**
   - The kernel label now names the 610 s test and records "600 s -> 610 s … BFG-D". `:11131` is a dated historical entry, and rewriting it would falsify history.

## 4. Findings

### M-1 (MATERIAL): the history check refuses an honest harvest commit that arrives through a merge. FIX-FIRST.

**Where.**
- `joulewise/battery_float.py:580-582`:
  ```python
  touching = _git(root, "log", "--full-history", "--format=%H", "--", rel)
  adding   = _git(root, "log", "--full-history", "--diff-filter=A", "--format=%H", "--", rel)
  if len(touching) != 1 or adding != touching …: raise NoRecord(…)
  ```
- Ruled text (§4.3 item 2) is `git log --no-renames …`, with git's default history simplification.
- Fix contract `12-…` FX-3 replaced it with `--full-history`, following Opus lens M-1. That lens itself proposed `--full-history --no-merges --no-renames` plus an adding-blob == HEAD-blob check, and its own table shows "honest merge → record" for its cure.
- The shipped variant dropped `--no-merges`. Under `--full-history`, git lists a merge commit that differs from one parent at the path, so the merge that brings in an honestly added file counts as a second "touching" commit.

**Failure scenario (executed, E9).**
1. W1 is harvested in its measurement clone, which runs detached at H. Step (iv) commits the pin and `W1.json` together, linearly, and W1's own `check` and cadence report pass.
2. The harvest commit reaches `main` the way everything reaches `main` here: a PR merged with `--no-ff`. First-parent history on main shows only `Merge pull request #…`.
3. W2's measurement clone is cloned from main at a later H. At W2's harvest, step (vii) `check`, and later `prepare-candidate`, authenticate W1, because W1 is in the computed set S.
4. The loader then raises `NoRecord("path history is not a single adding commit (2 commits, 1 adding)")`. That becomes the blocker `computed session W1: battery harvest verdict missing or uncommitted (…)` and the refusal `… not issued`.

**Why it matters.**
- The refusal is permanent under the ruled text. The record cannot be re-added, since delete-and-re-add is "3 commits, 2 adding". Main's history cannot be rewritten. The only way out is a code change to the authentication path in the middle of the epoch, which is itself a gated change landing after B values exist.
- It is not a science hole. It fails closed, never excludes, never counts toward the one-replacement bound, and E10 shows the shipped code refuses every tamper shape.
- It also does not touch W1's arm or W1's own harvest. It fires at the first cross-window authentication after a merge, which is the critical path to issuance.
- It is cheap to fix now and costly to fix later.

**The cure, verified (E10, real loader, five histories):**

| History | `b2c31e5b` | cure: `--full-history --no-merges` + adding blob == HEAD blob |
|---|---|---|
| honest, linear | LOADED pass | LOADED pass |
| **honest, merged `--no-ff` into a moved main** | **NoRecord (2 commits, 1 adding)** | **LOADED pass** |
| main add; side branch modify then restore; `--no-ff` merge (the existing test `:504`) | NoRecord (3, 1) | NoRecord (3, 1) |
| side-branch forged add; main honest add; add/add conflict resolved `--theirs` (lens M-1 route) | NoRecord (3, 2) | NoRecord (2, 2) |
| evil merge: the merge commit itself rewrites the record | NoRecord (2, 1) | NoRecord (adding blob ≠ HEAD blob) |

Check 5 (pin at the adding commit) stays valid under the cure, because with `--no-merges` the adding commit is never a merge.

### N-1 (NIT): R2-8 is a reversal of one ruled sentence, labelled as a tightening

PARSER-ESC §4 says: "a present key with a structurally valid value of the wrong type records `None` as today, because they are never gated." `_recorded_values` (`battery_float.py:228-234`) now raises `ProbeError` for a wrong-typed optional key.

- I affirm the change (§3 item 3).
- Closure: one sentence in the PR body or the decision trace: "R2-8 reverses PARSER-ESC-01 §4's 'records None' sentence for wrong-typed recorded keys; it is adopted because A-R5b's registered text makes a malformed property not a pass."

### N-2 (NIT): the paper-tool sweep row overstates the fence

`tests/test_battery_float_sweep.py:56-60` says "Revision-5 roots are outside its inputs". The tool reads whatever `--corpus-root` names (`paper_anchor_correction_quantified.py:751-756`, `:700-705`).

- Closure: reword to "default `--corpus-root` is the canonical checkout, which never holds a Revision-5 custody root (those live under `/Users/edr/night-custody/<plan_id>/runs`); pointing it at one is an operator act outside D-161".
- This is text only. The tool itself must not change (registry pin).

### N-3 (NIT): the synthetic battery pass in logical-test mode is unlabelled

`validate_powermetrics_fiducial.py:2158-2175`: when `logical_test_clock` is set (any `--time-scale-for-test ≠ 1`), the writer always uses a fixture runner. It defaults to `float.ioreg` and re-stamps `UpdateTime` to the logical clock.

- It is not reachable from the pinned chain (the chain passes no test flag). A real `powermetrics` cannot complete `_LogicalTestPulseDriver`'s acknowledgement protocol either.
- Optional hardening, not required: record `"fixture": true` in the observation when the fixture runner is used.

### N-4 (NIT/condition): the PR body is not yet written

When the PR is opened, it must carry verbatim:
- §5.3 item 8's two statements. BFG-D does not close BATTERY-FLOAT-GATE-01. Every transaction-pack campaign must re-freeze `arm_readiness.sources` before any transaction-pack window arms, because the writer is pinned there. That is a BFG-S prerequisite.
- §4.10 item 10's sentence.

## 5. The four questions

**Q1. Does the diff implement every governing obligation, with nothing weakened?**
Yes, except M-1, which departs from ruled §4.3 item 2 through an unruled lead fix. Verified:
- **Registered text.** A-R5b is verbatim (E4) and A-R5b-1 is verbatim (E5).
- **Parser.** The whole-document grammar; typing, which is stricter than ruled (N-1); the framing byte checks; the 200 mA and 180 s rules.
- **Admission sites.**
  - t0 C3 sits after the AC-power block, before `PMSET_GENERAL`, on both `legacy_load` branches. A probe error becomes `ProbeError` → `night_probe_error`; a failure becomes `night_refused_battery_float`.
  - The arm-check `inspect("battery_float")` is unconditional inside the sealed branch and outside any `NIGHT_KINDS` flag branch. It is not in the skip exemption.
  - Publication is observed after the successor comparison and before `phase="publishing"`, and is journaled.
  - Also present: the `validate_install` refusal `Refused(3)` and the `_derive_power` underivable.
- **Writer.** Brackets sit outside every clock stamp (E8), with the key set unchanged (E2 and test 5, inside E11).
- **Custody and records.** The custody rule's order E0–E6; `CustodyFailure` is a `RuntimeError`.
- **The one seam.** `authenticate_committed_verdict` is the consumer entry; the collector authenticates named sessions first; the policy has one decision and two renderings; the registry is digest-pinned.
- **Other consumers.** Continuation and equivalence refuse Revision 5; the three ungated B readers are fenced or dispositioned.
- **Liveness constant.** 610 s is the right bound for the code as built.

**Q2. Is there any route by which a charging, stale, missing or custody-failed window could count as evidence? Is there any route by which a clean window could be dropped after B is seen?**
No to both, outside D-161 operator-authorship routes and the disclosed between-observation excursion limitation. The routes I tried, and what closes each:

- *A charging, stale or malformed slot counts.* The per-slot pre and post observations are in the hashed evidence, which the ledger row digests. `validate_window` re-parses them from raw bytes and never trusts a stored `passed`. Stale is E5 and malformed is E5 (both `evidence_missing`); failing is E6 (confounded). The issuer excludes every non-pass window of the computed set, and the exact-set check forces it to be declared.
- *A slot whose evidence lacks the key.* This is E2 (`evidence_missing`). Every path that writes evidence adds the key before the status is set, so the key's presence cannot correlate with the slot's disposition (E8). That closes a selection-on-outcome route I specifically probed.
- *A custody-failed window becomes an exclusion.* Custody failure raises and is never a verdict. Every consumer refuses before the bound is counted.
- *Hiding a non-pass or clean window by not naming it.* S covers every terminal derivation session of the epoch that owns a target-epoch row. `foreign_owners` catches valid rows even without the predates exemption, and A-7 covers rows of non-terminal sessions. The registry exemption is digest-pinned.
- *Declaring a clean window confounded.* The policy refuses on `clean_declared` and `not_computed`.
- *Re-recording a clean window as non-pass after B.* The record must equal the recomputation from custody-pinned bytes, so a re-record either disagrees (refuse) or fails the history check (refuse). History tampering is refused both as shipped and under the cure (E10).
- *Pre-A-R5b writer on a named window.* `battery-verdict` refuses ("pre-A-R5b session"), so no record is written and issuance refuses. This fails closed. It is a liveness trap only if W1 were armed from a pre-BFG-D clone, which §5.7 item 2 forbids.
- *Test seams.* N-3 is unreachable from the pinned chain.

M-1 is not a Q2 route. It drops nothing and admits nothing. It blocks issuance.

**Q3. Can any battery observation perturb a measured number or a pinned byte?**
No.
- **Timing.** The slot observations fall strictly before `pre_spawn` and strictly after `post_parse` (E8), so no stamp the estimator consumes moves. The pre-observation delays sampler spawn by one ioreg run, which moves when the capture happens, not what the estimator computes. Test 9 (anchor non-overlap, 0 s and 2 s probes) passes in E11.
- **Code pins.** The writer is not an estimator pin, and the identity epoch has no code digest (E7). The frozen paths are unchanged (E2), and the manifest and evidence key sets are unchanged (test 5).
- **What does move.** The writer's digest in the d117 `arm_readiness.sources` pins, as ruled. This is a BFG-S re-freeze prerequisite, not a W1 one (N-4).
- **The admission sites.** Arm, publication, t0 and install all run before any capture exists.

**Q4. Is it fit to merge?**
**FIX-FIRST on M-1 only.** After M-1's closure lands with its test green, and with the PR body carrying N-4's statements, it is **MERGE**. N-1 and N-2 can land in the same fix commit or in the PR body; neither needs another delta round. The M-1 closure is confined to the loader and one test file, and changes no ruled text beyond restoring the ruling's intent. A short delta check by one reviewer running the five-history table is enough; a full lens round is not needed.

## 6. Dictated closure texts

**M-1 (FIX-FIRST).** In `joulewise/battery_float.py` `load_committed_verdict`:

1. Both history calls become:
   ```python
   touching = (_git(root, "log", "--full-history", "--no-merges", "--no-renames", "--format=%H", "--", rel) or b"").decode().split()
   adding = (_git(root, "log", "--full-history", "--no-merges", "--no-renames", "--diff-filter=A", "--format=%H", "--", rel) or b"").decode().split()
   ```
   The existing `len(touching) != 1 or adding != touching` test is unchanged.
2. Immediately after that test, add:
   ```python
   if _git(root, "show", f"{touching[0]}:{rel}") != committed:
       raise NoRecord("path history is not a single adding commit (the adding commit's bytes differ from HEAD)")
   ```
   This catches a merge commit that rewrites the record, which `--no-merges` no longer lists.
3. Comment above step 2: `# --no-merges: an honest harvest commit reaching main through a --no-ff merge is one adding commit; a merge that rewrites the record is caught by the adding-blob check below (BFG-D row-6 M-1).`

Tests in `tests/test_battery_float.py`, beside `:504`, through the shared git-fixture helper:
- (a) `test_honest_harvest_merged_no_ff_into_moved_main_loads`: the harvest commit on a branch; main gains an unrelated commit; `merge --no-ff`. The record loads with `commit` equal to the harvest commit. It must be RED at `b2c31e5b`.
- (b) `test_evil_merge_rewriting_record_is_no_record`: the record on main; an unrelated branch; a `merge --no-ff --no-commit` that rewrites the record, then commit. Expect `NoRecord` containing "adding commit's bytes differ".
- (c) `:504` and the add/add `--theirs` shape still refuse.

Run `tests.test_battery_float`, `tests.test_battery_float_consumers` and `tests.test_issue_calibration_acceptance_generation`, and paste the tails. The pin proof of E2 must stay empty. `_structure` and `_recorded_values` are untouched, so the R2-9 freeze pin stays green.

**N-1.** PR body (or trace) sentence: "R2-8 reverses PARSER-ESC-01 §4's sentence that a wrong-typed recorded key 'records None as today'; a wrong-typed recorded key is now a probe error, adopted because A-R5b's registered text makes a malformed property not a pass. Decided from instrument bytes before any B; cannot select on outcome."

**N-2.** `tests/test_battery_float_sweep.py:57-60` row text: `"pinned by sha in docs/paper/results-fill-registry.md; its default --corpus-root is the canonical checkout, which never holds a Revision-5 custody root (those live under /Users/edr/night-custody/<plan_id>/runs); pointing it at one is an operator act outside D-161 (26-fix-contract-r7b.md H-4; row-6 N-2)"`.

**N-4.** PR body carries §5.3 item 8's two statements and §4.10 item 10's sentence verbatim.

## 7. Cleanup

After writing this file, I removed `/tmp/ed17a643-opus-vpf.py`, `/tmp/ed17a643-opus-iss.py`, `/tmp/ed17a643-opus-ar5b-*.txt`, `/tmp/ed17a643-opus-ar5b1-*.txt`, `/tmp/ed17a643-opus-probe*.py` and the scratch repo `/tmp/ed17a643-opus-git.*`. The probe repos were removed inside the probes. `git status --porcelain` in the worktree is empty. No file in the repository was written.
