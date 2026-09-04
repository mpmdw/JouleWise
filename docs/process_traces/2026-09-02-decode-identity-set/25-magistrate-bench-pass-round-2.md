# Magistrate bench pass on fix round 2 (`bd2cae3e` → `9c1dc717`) with executed counterfactuals, 2026-09-02

Sol 262 (file 24) landed R2-A..R2-E at `bd2cae3e`; acceptance `ready`,
446 OK skipped=1, D-165 digest unchanged. The magistrate read the full
diff at the bench and made three corrections in `9c1dc717` BEFORE the delta
re-audit (luna 263, file 26), so the re-audit grades the corrected head:

1. **R2-E FIRST-USE-GAP "committed file tree" — magistrate's own defect.**
   The dictated paragraph used "the digest of its committed file tree"
   without building it. Glossed in place at step (2) from
   `joulewise/arm_readiness.py::committed_pack_tree_sha256` (:2750–2874):
   the sha256 over the pack's committed files — each path, Git mode, byte
   length and content digest in path order (the `framed` fold at
   :2861–2874) — and the function itself raises `ArmReadinessError` on an
   untracked entry or directory (:2833–2842), a missing committed entry
   (:2843–2847), or bytes/mode differing from the blob (:2860–2864), which
   the gate's `except` turns into the same refusal. A first draft of the
   gloss said uncommitted edits were "invisible" to the digest; that was
   WRONG (they are refused, not ignored) and was corrected before commit by
   reading the function to its return. The other three reported gap rows
   (`plan_tree.json` filename at 34; `projection_receipt` in the key list at
   181; `consumer_bindings` key at 200) are proposed NOT gaps — a filename
   or key name in an exhaustive key list is a value the reader copies, the
   file 22 §Q2 reasoning — and are put to luna 263 to refute (brief B2).
2. **R2-E rewrap.** The seat inserted the dictated text verbatim as three
   unwrapped lines; rewrapped at 79 columns to the file's convention. No
   word changed except the gloss above.
3. **R2-D docstring.** The seat's one-line docstring ("Lines 1681/1695 plus
   manifest retention at 218 dominate line 1701.") named line numbers, not
   the argument; replaced with the dominance argument in words (which
   check raises first, which second, why distinct manifests give distinct
   scientific hashes, where the executed proof lives, and that weakening a
   preceding check is a protocol failure), per the
   `test_arm_readiness_integration.py:583` pattern the brief named.

## Executed evidence (bench, `/Users/edr/code/JouleWise-wt-decode-id` at `9c1dc717`, `TMPDIR` under the scratchpad; each reverse-patch reverted with `git diff --exit-code` pasted)

R2-A — F-B biting test, counterfactual `inputs.py:3898` → `if False:`:

```
$ git rev-parse --short HEAD
9c1dc717
$ python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_self_consistent_forged_pack_requires_launch_tree_digest_binding 2>&1 | tail -3
Ran 1 test in 7.601s

OK
$ python3 - <<EOF   # reverse-patch line 3898 comparison -> if False:
PATCHED
$ python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_self_consistent_forged_pack_requires_launch_tree_digest_binding 2>&1 | tail -8
- exact
+ refused


----------------------------------------------------------------------
Ran 1 test in 3.736s

FAILED (failures=1)
$ git checkout -- joulewise/analysis_engine/inputs.py && git diff --exit-code --stat && echo REVERTED-CLEAN
REVERTED-CLEAN
```

R2-B — unmocked transport test, counterfactual gate body → `return frozenset()`; R2-C — mapping pin, mutant routing both labels to `floor_row_missing`:

```
$ python3 - <<EOF   # R2-B: gate body -> return frozenset()
PATCHED
$ python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_generated_multi_identity_transport_uses_real_frozen_gate_and_skips_exact_cell 2>&1 | tail -6
AssertionError: 'consumer_identity_set_unauthenticated' unexpectedly found in ('consumer_identity_set_unauthenticated',)

----------------------------------------------------------------------
Ran 1 test in 1.677s

FAILED (failures=1)
$ git checkout -- joulewise/analysis_engine/inputs.py && git diff --exit-code --stat && echo REVERTED-CLEAN
REVERTED-CLEAN
$ python3 - <<EOF   # R2-C: map both labels to floor_row_missing
4:        if resolution.floor_abs_j is None:
6:        if resolution.floor_cmp_j is None:
9:            if reason == "cell_missing":
10:                reasons.append("floor_row_missing")
11:            elif reason == "cell_stale":
13:            elif reason == "transport_group_incomplete":
15:            else:
16:                reasons.append("floor_transport_inapplicable")
21:    if any(
28:    usable = [resolution for resolution in resolutions if resolution.status in {"exact", "transported"}]
30:    floor_abs = max((value.floor_abs_j for value in usable if value.floor_abs_j is not None), default=None)
31:    floor_cmp = max((value.floor_cmp_j for value in usable if value.floor_cmp_j is not None), default=None)
32:    floor_gate = max((value.floor_gate_j for value in usable if value.floor_gate_j is not None), default=None)
33:    if not all_usable:
PATCHED
$ python3 -m unittest tests.test_analysis_integration.AnalysisIntegrationTests.test_identity_gate_refusals_map_to_transport_inapplicable 2>&1 | tail -4
----------------------------------------------------------------------
Ran 1 test in 0.328s

FAILED (failures=2)
$ git checkout -- joulewise/analysis_engine/__init__.py && git diff --exit-code --stat && echo REVERTED-CLEAN
REVERTED-CLEAN
```

All three named counterfactuals are KILLED at the bench; the F-B closure
now has a test that fails on removal of the cure (rule 11 fix round 2 on
F-B closes on that criterion, subject to the delta re-audit). R2-D's
proof and R2-E's prose carry no executable counterfactual; luna 263 grades
both (A4, B1–B3).

## Seven-module verification at `9c1dc717`

```
$ python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_docs_freshness 2>&1 | tail -4
Ran 446 tests in 92.083s

OK (skipped=1)
rc=0
```
