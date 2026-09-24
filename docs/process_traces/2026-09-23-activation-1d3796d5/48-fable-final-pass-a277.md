VERDICT: MERGE

# 48 — Cold Fable 5.1 final pass, lane A277 (ZERO-CAPTURE-EVIDENCE-WRITER-01)

Judge: Claude Fable 5.1, cold, no loop context. Worktree /Users/edr/code/wt-1d3796d5-fable277, detached at fafd056b (verified `git rev-parse HEAD`, working tree clean). Base for the lane: 313efcca. Prior ruling 47 (PROCEED-AFTER-DICTATED-CLOSURES on 408b96c3) and its three closure diffs read from /Users/edr/code/wt-1d3796d5-bk/.seat-out/. Everything below marked "executed" ran in this session; anything else is marked NOT EXECUTED. No repository file was edited; no launchctl, sudo, night-custody or JouleWise-measurement path was touched; nothing was imported from /Users/edr/code/JouleWise.

## Q1. Mechanical check: `git diff 408b96c3..fafd056b` = three dictated diffs + only the Q5(b) doc changes — VERIFIED (executed)

`git diff --stat 408b96c3..fafd056b` touches exactly eight files: docs/contracts/night_quiet_admission.md, docs/phase_2/derivation_night_runbook.md, docs/process/NIGHT_HANDBACK.md, joulewise/arm_retry.py, joulewise/evidence_night.py, tests/test_arm_retry.py, tests/test_evidence_night.py, tests/test_zero_capture_facts.py.

The dictated diffs were produced with plain `diff -u` (no git headers, hunk offsets 761 vs 763, blank-line placement differs inside one hunk), so a textual diff-of-diffs is noisy. I therefore applied them: `git archive 408b96c3` into /tmp/a277-base, `patch -p1` with all three dictated diffs (all hunks applied cleanly, no rejects), then byte-compared the resulting files against HEAD:

| File | Result |
|---|---|
| joulewise/evidence_night.py | SAME |
| tests/test_evidence_night.py | SAME |
| tests/test_arm_retry.py | SAME |
| tests/test_zero_capture_facts.py | SAME |
| joulewise/arm_retry.py | one line differs: the D-182 paragraph inside `render_policy()` (the Q5(b) sentences); the dictated C5-row hunk at line 256 is present verbatim |

Doc changes (executed `git diff --word-diff`): the contract gains exactly two inserted passages (the C5-row/veto-only sentence, and the launchctl-spelling + claim-file-name sentences); NIGHT_HANDBACK.md and derivation_night_runbook.md each gain only the same two inserted phrases inside the policy block. Regeneration check (executed): `arm_retry.render_policy().strip()` is contained verbatim in both docs, one `BEGIN ARM-RETRY-POLICY` block each. Nothing else in the lane diff. Q1 passes.

## Q2. The three new sentences — true against the code, and readable

**Sentence A (policy):** "The successor route also requires the driver's receipt shape with exactly one C5 row; early release keeps the receipt's veto-only role." Contract form adds: "so a receipt without that row still allows release but licenses no successor."
Enforcing lines: joulewise/arm_retry.py `successor_license`, after `terminal_zero_capture_refusal` has already passed:
```
        if sum(1 for row in receipt["conditions"] if row["condition_id"] == "C5") != 1:
            return Decision(False, "malformed_successor_evidence")
```
Release side: `terminal_zero_capture_refusal` is byte-identical to 313efcca (executed function-text diff: TERMINAL_IDENTICAL) and is the only receipt predicate the watchdog's `_delivered_zero_capture_refusal` calls (scripts/magistrate_watchdog.py:817). "Driver's receipt shape" is real: scripts/run_night.py:2053-2058 writes condition rows C1..C5 once each. TRUE.

**Sentence B (policy):** "The real launchctl must be spelled launchctl; any other spelling that resolves to it is refused, never treated as a rehearsal." Contract form: "Only the literal `launchctl` is the real launchd tool; any other spelling that resolves to the real tool (an absolute path, a symlink) is refused rather than treated as a rehearsal, so no real publication can skip the claim."
Enforcing lines: joulewise/evidence_night.py:766-788 `rehearsal_launchctl`: literal `"launchctl"` returns False; otherwise resolves via `shutil.which`/absolute path, compares with `os.path.samefile` or equal `Path.resolve()`, and raises `Refused("real launchctl must be spelled exactly 'launchctl'; a path to it is not a rehearsal: ...")`. Used at check (1254), require_fresh_check (1440-1444, which also pins check.json's `launchctl_bin` string and `fake_launchctl` flag), and publish_install (1619); the claim gate is `if not fake: _create_successor_claim(...)` at 1700-1701, before `os.replace(plan, target)`. TRUE.

**Sentence C (policy):** "A predecessor whose plan id cannot name a claim file fails the successor check." Contract form names the pattern `[A-Za-z0-9][A-Za-z0-9._-]*`.
Enforcing lines: evidence_night.py:893-894 in `successor_check`:
```
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", plan.plan_id):
        raise Refused("predecessor plan id cannot name a successor claim: " + plan.plan_id)
```
and the same pattern again in `_create_successor_claim` (928). TRUE.

**Readability for a technical reader with no project grounding.** The contract versions pass: "veto-only role" is glossed in the same sentence in plain words, "any other spelling" is glossed as an absolute path or a symlink, "bare C5 receipt row" is glossed one sentence earlier, and the claim-name pattern is spelled out. Two nits, neither blocking and neither introduced by the dictated wording: (1) the policy-block version of Sentence A carries "veto-only role" without the contract's plain-words gloss (first use of "veto" in that block is this sentence); (2) the contract cites "(cold ruling 16 Q1)", internal provenance shorthand. "Rehearsal" is first used in the policy block one sentence earlier without a gloss ("a run under a fixture launchctl"); pre-existing shape, same nit class. A merge-later doc touch, not a blocker.

## Q3. Tests and mutants (executed at HEAD unless marked)

- `python3 -B -m unittest tests.test_arm_retry tests.test_zero_capture_facts`: Ran 38 tests, OK.
- `python3 -B -m unittest -k a277 -k A277 -k f1_ -k f2_ -k f3_ -k f4_ -k f5_ -k successor -k claim -k rehearsal_launchctl tests.test_evidence_night`: Ran 23 tests in 33.2 s, OK. This covers all `test_a277_*` (20) and `test_f1_`, `test_f2_`, `test_f4_`, both `test_f5_` in LifecycleTests; F3's tests live in tests.test_arm_retry (`test_f3_receipt_without_c5_row_licenses_nothing`) and ran in the 38 above.
- `python3 -B -m unittest tests.test_magistrate_watchdog` (full module): Ran 130 tests, OK. Includes `test_a277_base_fixture_shape_release_parity` (12 fixture shapes with expectations pinned to the 313efcca predicate) and `test_a277_symlink_inside_custody_is_stricter_than_base`.
- Full `tests.test_evidence_night` (150 tests): NOT COMPLETED within budget. The run exceeded the 600 s tool timeout and was still executing when this ruling was written; no failure had been printed. Ruling 47 also did not run this module in full. The 23 lane-relevant tests above plus the eight ruling-47 regressions are executed and green.

Mutants, each in a fresh `git archive fafd056b` copy under /tmp/a277-mut-*, run against the named killing test (five of the ruling's eleven; the ruling asked for at least three):

| Mutant | Edit | Killing test | Result |
|---|---|---|---|
| F1 rehearsal classifier never matches | `if same:` → `if False:` | test_f1_real_launchctl_under_another_spelling_is_refused_not_rehearsed | FAILED (failures=1) — killed |
| F4 skip directory fsync | `os.fsync(directory_fd)` → `pass` | test_f4_claim_directory_entry_is_fsynced_before_publication | FAILED (failures=1) — killed |
| F3 drop C5-row count | C5 `sum(...) != 1` → `if False:` | test_f3_receipt_without_c5_row_licenses_nothing | FAILED (failures=3, all three subtests) — killed |
| F5 drop active-claim check after root removal | `raise Refused("successor claim remains active…")` → `pass` | test_f5_active_foreign_claim_binds_after_root_removal_and_key_forgotten | FAILED (failures=1) — killed |
| F5 final claim by plain copy | `os.link(temporary, path)` → `shutil.copyfile(...)` | test_f5_claim_creation_never_overwrites_a_foreign_final_claim | FAILED (failures=1) — killed |

## Q4. Whole-lane blockers

**(a) A way to arm more than one successor per predecessor — none found.** Routes checked in code (evidence_night.py 850-960, 1611-1705):
- Two candidates racing: each `publish_install` calls `successor_check` then `_create_successor_claim` before `os.replace`. The claim is written to a temp file and `os.link`ed to `<predecessor>.json`; the second linker gets FileExistsError → `Refused("concurrent successor claim")` before `publication_started = True`, so nothing is published. A pre-existing claim naming a different candidate refuses at check (`successor_already_used`) and again at creation (`successor already claimed by another candidate`).
- Successor of a successor: `predecessor_is_successor` → `successor_already_used`.
- Predecessor custody removed: the claim survives outside custody; `successor_check` refuses any other candidate while `now <= predecessor_completion_epoch_s` (the F5 mutant above proves the test binds this).
- More than one released predecessor in span: refused outright.
- Same candidate re-publishing after a failed publication (same id and digest): allowed, and still one successor.
Removing the claim directory by hand is an operator-only action, outside the fail-closed set.

**(b) A real publication that skips the claim — none within the lifecycle.** The claim gate is `if not fake` and `fake` is now decided by resolving the path (Sentence B), pinned to check.json and re-derived at publish. Residual, pre-existing and out of the operator-adversary threat model: an operator-authored wrapper script that is not the real binary is classified as a rehearsal; the installer (scripts/install_night_agent.sh:25-31) forwards whatever `--launchctl-bin` it is given. Ruling 47 records the rehearsal gate as latent since the lifecycle was written; this lane narrowed it. Direct `install_night_agent.sh` performs no successor check, stated in the policy, owned by a follow-up lane. Not a blocker for this merge.

**(c) Release more permissive than 313efcca — no.** Executed: `terminal_zero_capture_refusal` text identical at both commits. The disk-facts side moved from the watchdog's `_zero_capture_disk_facts` into joulewise/zero_capture_facts.py; read side-by-side (executed): identical literal parsing (`_literal` mirrors `night_gate.chain_literal`), identical payload-kind rule (no NIGHT_PAYLOAD_KIND → calibration; ambiguous → exception → not clean, old: exception → False), same chain.started / reservation / capture / envelope-index outcomes, and three stricter-only differences: any symlink in a scanned tree counts as a fact (old only counted symlinks matching the predicate), a symlinked custody root is not a directory under `lstat` (old followed it), and envelope-index rows are parsed (a malformed row is not clean). The 12-shape parity test pins the old outcomes and passes; the stricter symlink case has its own test. Same or stricter everywhere; never more permissive.

**Trial merge (executed, non-destructive):** `git merge-tree --write-tree origin/main(946bce0e) fafd056b` rc=0, tree 384db096, no conflicts.

## Q5. MERGE

The head fafd056b is 408b96c3 plus the three dictated closure diffs, byte-exact, plus exactly the three sentences ruling 47 required, regenerated into the two policy blocks and the contract. All executed tests pass; five ruling mutants are killed at HEAD; release parity with 313efcca holds with only stricter differences; no route arms a second successor or publishes for real without a claim inside the lifecycle. Non-blocking follow-ups: gloss "veto-only role" and "rehearsal" in the policy block text, drop the "(cold ruling 16 Q1)" shorthand from the contract, and finish a full run of tests.test_evidence_night post-merge (fix forward if anything outside the 23 lane tests regresses).

Addendum (end of session, executed): the full `python3 -B -m unittest tests.test_evidence_night` run completed after this ruling's body was written: Ran 150 tests, OK, exit code 0, wall time 11 min 34 s (it exceeded the tool's 600 s timeout, not the budget of the suite). This supersedes the NOT COMPLETED line in Q3: all four modules named by ruling 47 have now run in full and green (test_arm_retry + test_zero_capture_facts 38 OK; test_magistrate_watchdog 130 OK; test_evidence_night 150 OK).
