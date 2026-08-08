# Verdict: FAIL

Same-signature answer: **YES.** FIX-1 closes the reported `new_content_ids` hole, but the same attestation-binding defect remains in `trigger_judgment.triggers`.

## P1 findings

1. **A false trigger attestation survives both validation layers.**

   [calibration_bracketing.py:1164](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:1164) only requires `triggers` to be a nonempty ordered subset of two allowed strings. Parent-aware loading at [calibration_bracketing.py:1023](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:1023) binds basis additions but never recomputes which trigger actually occurred.

   Reproduced scenario:

   - Build a valid successor whose real trigger is `new_valid_same_identity_capture_expands_observed_range`.
   - Replace it with `content_distinct_valid_same_epoch_count_boundary`; the source count is below that boundary.
   - Recompute the artifact derivation hash and registry artifact/derivation pins.
   - `_valid_acceptance_bound(...)` returns `True`.
   - `load_calibration_acceptance_registry(...)` also accepts it.

   Observed reproduction:

   ```text
   real_triggers=["new_valid_same_identity_capture_expands_observed_range"]
   forged_triggers=["content_distinct_valid_same_epoch_count_boundary"]
   standalone_accepts=true
   registry_accepts=true
   ```

   This is another evidence/lineage attestation not bound to its claimed fact—the same signature as the original P1.

2. **FIX-4 does not establish fsync ordering.**

   [test_calibration_acceptance_successor.py:1557](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf6a2f4/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:1557) counts two file and two directory fsync calls, but records no relationship between fsync and `os.replace`.

   Failing mutation: move either directory fsync before its corresponding rename. Counts remain `2/2`, so the test passes even though the rename is not durably synchronized. The named deletion and `ref_advanced=False` mutations are killed, but the lens’s ordering requirement remains open.

## P2 findings

3. **FIX-11’s exactly-one-active regression is not discriminating.**

   The regression at [test_calibration_acceptance_successor.py:350](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:350) stays green after deleting the explicit `active_count != 1` check at [calibration_bracketing.py:808](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:808), because the later `active_ids == leaves` condition at [calibration_bracketing.py:854](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:854) independently rejects the same fixture.

   In-memory mutation result:

   ```text
   current_validator_accepts=false
   validator_without_active_count_check_accepts=false
   ```

   The duplicate-path regression is discriminating; the named one-active mutation is not.

4. **FIX-5 and FIX-6 are conditional on ephemeral `/private/tmp` inputs.**

   The forged-receipt regression at [test_calibration_bracketing.py:722](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_bracketing.py:722) and cadence regression at [test_calibration_acceptance_successor.py:1140](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:1140) skip when two hard-coded external files are absent.

   Failing scenario: a fresh CI checkout lacks those `/private/tmp` files; removing receipt-digest equality or reintroducing one-sequence cadence arithmetic is then unguarded. Locally, with the custody files present, both tests pass, and the forged receipt was independently confirmed schema-valid and self-rehashed.

5. **FIX-9’s missing-field cases do not reach the runtime guard.**

   At [test_calibration_bracketing.py:1709](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_bracketing.py:1709), every missing-field case stops after standalone validation. Thus a runtime fallback that supplies a missing operative instead of returning `invalid_acceptance_arithmetic` would escape. Negative-sign, ordering, and nonfinite runtime cases are discriminating.

## P3 finding

6. `git diff --check e5cf244..878ce9e` fails on trailing whitespace at [ROUND2-DELTA.md:7](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/docs/process_traces/2026-08-07-u2-coldgate/ROUND2-DELTA.md:7), contradicting the fix report’s clean-check claim.

## FIX-1..11 disposition

| FIX | Result | Audit |
|---|---|---|
| 1 | **PASS for original hole** | Exact-set equality exists standalone at lines 1450–1455 and parent-aware at 1043–1044. The regression performs the original build → erase IDs → rehash artifact → repin registry → validate/load scenario, isolating the registry check by bypassing standalone validation. A sibling attestation hole remains as P1 finding 1. |
| 2 | PASS | Faults after both replacements, before/after commit creation, and before ref advance assert old HEAD and old committed selection. |
| 3 | PASS | Registry rollback is exact-bytes; new artifact absence and identical prepublished-artifact preservation are both asserted. |
| 4 | **PARTIAL** | Fsync deletion and `ref_advanced=False` mutations are killed; fsync ordering is not. |
| 5 | Conditional PASS | Forged receipt is well-formed and self-rehashed; equality removal and wrong committed pin are killed before successor logic. Skips without external custody files. |
| 6 | Conditional PASS | Loaded reservation/finalization cadence makes the real cutoff 78, killing one-sequence arithmetic. Skips without external custody files. |
| 7 | PASS | Generation-two boundary, non-11 gap, and strict-above-ceiling mutations are discriminated. |
| 8 | PASS | Full basis equality is independently derived from the parent member mapping. |
| 9 | **PARTIAL** | Named negative-screen mutation and nonfinite/ordering cases are killed; missing fields do not exercise runtime refusal. |
| 10 | PASS | Literal tie result is independent of the implementation rounding constant. |
| 11 | **FAIL** | Duplicate-path mutation is killed; deleting the explicit one-active check leaves the regression green. |

Production changes are properly confined: the only production diff is ten FIX-1 validator lines in `joulewise/calibration_bracketing.py`; publication, rollback, and durability code were not changed speculatively.

Checks performed: exact head/base and clean worktree; `+1038/-46` diff inspection; focused suites `98/98 OK`; FIX-1 and false-trigger rehash reproductions; FIX-11 in-memory mutation; forged-receipt shape/digest verification; `git diff --check` failed as above. No files edited.