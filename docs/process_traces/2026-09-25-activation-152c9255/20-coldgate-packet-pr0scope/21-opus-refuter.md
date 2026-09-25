I found 1 BLOCKER, 6 MATERIAL and 3 NIT problems with the ruling's acceptance text. **Verdict: amend before seating the round.** The biggest problem is that the acceptance can be met at PR-0, but the standing tests it creates break at the CG-4 PR by design, and CG-4's write scope doesn't allow a fix.

# Opus 5.5 refuter report — PR0-SCOPE-01 ruling, §4–§5

**Files.** `R` = `docs/process_traces/2026-09-25-activation-152c9255/20-coldgate-packet-pr0scope/20-coldgate-fable-pr0scope-ruling.md`. `CG4` = `…/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md`.

**Probes.** I ran these read-only in a /tmp clone, `/tmp/152c9255/pr0scope-ref` at `576f3989`:
- read the sweep script, the capture script and the golden test;
- compared the kept CG-4 WIP commit `0d2b4497` against its merge-base with `576f3989`;
- measured the size of each function with the AST.

I did not run the sweep or the test suite.

**Can the acceptance be met without touching `joulewise/`?** Yes, at PR-0. Every row the ruling asks for is reachable from `scripts/` and `tests/`:
- `ordered_reason_codes` and `adjust_p_values` are called directly;
- `analyze_claims` exposes the private keyword argument `_floor_request_factory` (`__init__.py:1663`);
- `custody._replay_family` runs under the existing mock seams;
- `evaluate_session` is called directly;
- the corpus only calls `validate_claim_verdicts`.

I did not build the rows, so the claim that they kill the 70 survivors is still the ruling's estimate.

---

## BLOCKER

**B-1. The mutation, coverage and ratchet tests are guaranteed to fail at CG-4, and CG-4 has no allowed way to fix them.** Anchors: `R:57`, `R:65` (d)(e), `R:67` (1)–(3).

The acceptance defines these as ordinary tests in the unit suite. The CG-4 PR must pass the full suite, and three things break there:
- **The oracle is the whole golden file.** Each mutant is checked by `canonical_bytes(capture()) == GOLDEN.read_bytes()` (`claimgate_golden_sweep.py:218-222`), and `capture()` computes `transitions` from live code (`capture_claim_replay_golden.py:587-590`). CG-4 commit (7) sets `APPLIED_TRANSITIONS={"WR-6"}` (`CG4:83`). From then on the live WR-6 `pre` equals the ruled `post`, so every sweep clone stops at `RuntimeError: mutation clone baseline differs from golden`.
- **CG-4's new v2 code sits inside a whole-file gated target.** The kept WIP adds 34 lines above `claims.py:386`, plus a v2 path in `evaluate_claim` that no v1 golden runs. Those lines produce survivors and uncovered branches that cannot be removed without editing the test.
- **Every exception key contains a line number.** That covers `EQUIVALENT_MUTANTS`, `UNREACHABLE_ARCS`, the `v1-wire-unreachable` entries and the residual file. All of them move with CG-4's edits.

Neither `scripts/claimgate_golden_sweep.py` nor `tests/test_claim_replay_golden.py` is in any CG-4 write scope (`CG4:77`, `CG4:83`). The CG-4 seat would have to choose how to get out, which breaks Q3's "executable without choosing".

**Corrected text (add as R-6v2 (f)):**
> "(f) The mutation and coverage results certify the golden's sensitivity at the PR-0 source. `claimgate_golden_sweep.py` holds `CERTIFIED_SOURCE_BLOBS = {path: git-blob-sha}` for every `_GATED_TARGETS`/`_RESIDUAL_TARGETS` file and each coverage module. The mutant oracle compares exactly what the standing tests compare: `invariant`, `v1_golden_manifest_ids`, and the `transitions` `pre` states. `test_golden_branch_coverage_complete`, `test_golden_mutation_sweep_zero_unlisted_survivors` and `test_validator_residual_ratchet` run only when every working-tree blob equals `CERTIFIED_SOURCE_BLOBS`. Otherwise they call `skipTest("sensitivity certified at PR-0 blobs; re-certification is a reviewed PR")`. After PR-0, `test_claimgate_v1_replay_golden_unchanged` and `test_transitions_match_applied_state` are the live guard."

## MATERIAL

**M-1. The target map misses v1-path functions that CG-4 edits, and the plain summary to Ed is therefore false.** Anchors: `R:44`, `R:46`, `R:69` line 1.

CG-4 edits these functions, which the golden runs through, but which are neither gated nor measured:

| Function | Size | CG-4 edit |
|---|---|---|
| `estimators.estimate_paired_blocks` | 63 lines | WIP hunks at `:453-511` |
| `estimators._ci_t_critical` / `_sample_stddev` | 5 / 11 lines | WIP hunks at `:224`, `:228` |
| `__init__.analyze_claims` | 245 lines | WR-6's v1-closure check, the riskiest v1-moving edit (`CG4:75`); WR-5's `envelope_member_only` |
| `claim_side_bound.py` | — | WR-5 |
| `epoch_equivalence_check.reference_envelope` | — | WIP +53 lines at `:314` |
| `validate_claim_verdicts` | — | WR-0(iii) |

The corpus pins `validate_claim_verdicts` only partly. The manifest-v3 validators (WR-4) are pinned only by recorded outcomes.

**Corrected text:**
- Append to `R:46`: "`_RESIDUAL_TARGETS` also holds `joulewise/analysis_engine/estimators.py: {"estimate_paired_blocks","_ci_t_critical","_sample_stddev"}`, `joulewise/analysis_engine/__init__.py: {"analyze_claims"}`, `joulewise/analysis_engine/claim_side_bound.py: None`, `scripts/epoch_equivalence_check.py: {"reference_envelope"}`. Targets are keyed (path, function), so one file may hold both classes."
- Replace `R:69` line 1: "The snapshot test now catches every code change in the core decision functions, with a short proof-carrying exception list; that is the gate. Other functions the rewrite edits (interval estimator, claim assembly, side-bound, input validator) are measured and listed, not gated."

**M-2. The 11 `_claim_issuance_gate` kills sit in a part of the golden that no standing test compares.** Anchor: `R:52`, which puts the shim rows under `transitions…real_v1_wire.post.variants`.

`post` is computed live (`capture…:504-506`), so the whole-file mutation oracle counts these rows as kills. But while D-1 is unapplied, `test_transitions_match_applied_state` compares only `pre` (`test_claim_replay_golden.py:52-54`). Once D-1 is applied, it compares live `pre` with `post` minus `shim`, and `variants` exists only in `post`, so the comparison fails. The kills protect nothing.

Moving the rows into `invariant` does not work either. WR-6's check sits in the loop after `:632` (ex-02 placement rule), so it removes `l2` grants from shim outcomes, and CG-4 would then have to refresh the golden.

**Corrected text:**
> "Record each as scenario `shim_<name>` of `transitions["WR-6"]`, `pre` = live shim replay, `post` = `pre` with every `l2` grant removed and `reason_codes_added: ["claim_rule_version_v1_closed"]` where the row reaches `evaluate_claim`; compared by `test_transitions_match_applied_state`."

**M-3. The ruling contradicts R-1, which it says "stands unchanged".** Anchor: `R:63`.

R-1 fixes the `invariant` key set and restricts `window_engine` to "only `minimal_v1_artifact` and `metric_selector_mismatch`" (ex-02 R-1). The ruling adds `invariant.validator_corpus`, four `window_engine` rows (`R:51`) and `post.variants`. A re-audit under item (7) could refute any of them.

**Corrected text:**
> "R-1 is amended: `invariant` gains `validator_corpus`; `window_engine` gains the four Q2 rows; `transitions["WR-6"]` gains the `shim_*` scenarios (M-2)."

Related: the ruling says `request_factory` (`R:51`); the real name is the `_floor_request_factory` keyword argument of `analyze_claims`.

**M-4. The gated test can be passed by listing exceptions.** Anchors: `R:46`, `R:48`, `R:67` (3).

"A row that does not kill is replaced by an `equivalent:` entry citing the row tried" lets any sloppy row become an exception. Nothing checks the class prefix, whether the cited row exists, or how many entries there are. Recording rows as `{"raised": <type>}` alone also makes false non-kills likely: several multiplicity guards all raise `ValueError`.

**Corrected text:**
> "Rows record `{"raised": type, "message": str(exc)}`. A test asserts every `EQUIVALENT_MUTANTS` value matches `^equivalent: .+ \[row: <golden key path>\]$` (path present in the golden) or equals the ruled `v1-wire-unreachable:` sentence with its key inside `_claim_issuance_gate`. `equivalent:` entries beyond `claims.py:386 Gt_to_GtE` and `claims.py:385 And_delete_1@7` each need individual affirmation by the delta re-audit before merge; the PR body gives per-class counts."

**M-5. The ratchet quietly loosens itself.** Anchor: `R:57`.
- "The sweep writes `…validator_residual.json`" means every `--mutate` run overwrites the baseline, including the acceptance run.
- The residual file has no blob pin, unlike the golden (`test_golden_blob_pinned`).
- Keys contain line numbers (B-1).

**Corrected text:**
> "`--mutate` never writes. `--write-residual` writes only if the new survivor set ⊆ the tracked set, the residual target files equal `origin/main`, and otherwise exits 2 `refusing residual refresh: survivors grew`. `test_residual_blob_pinned` pins the file's blob sha as a code constant; changing it is a reviewed PR."

**M-6. The corpus specification can be implemented two valid ways, and it may not cover enough.** Anchor: `R:55`.

These points are left open:
- `bool` is a subclass of `int`, and no order of type checks is given. Depending on the order, `wrong_type` turns `True` into `"true"` or `"x"`.
- `nan`, `sign_flip` and `off_by_one` are unspecified for bools.
- `None` leaves have no `wrong_type` target.
- Operations that change nothing (`null` on `None`, `empty` on `""`, `[]` or `{}`, `sign_flip` on `-0.0`) are not skipped.
- Pointer escaping (RFC 6901 `~0`/`~1`) and the key separator are not given.
- The validator's keyword arguments are not given (`frozen_manifest` gates `artifact.py:1688`, `:3182`).

**Corrected text:**
> "Dispatch order `None`→`bool`→`int|float`→`str`→`list`→`dict`; `None`: only `drop`; `bool`: `drop`, `null`, `wrong_type`→`"true"`; skip any operation whose result equals the input; `drop` also applies to every non-empty mapping key and list element (subtree drops); key = `base + "|" + RFC6901 pointer + "|" + op`; call `validate_claim_verdicts(case)` with no keyword arguments."

The PR body must also show the residual kill rate before the corpus (164/934 at `576f3989`) and after it. Without the before figure, a weak corpus is invisible.

## NIT

- **N-1.** The gated test and the ratchet test would each run the full sweep, about 10 minutes each in the suite. Share one run per test class (`setUpClass`). Anchor: `R:57`.
- **N-2.** "The golden asserts `validate_claim_verdicts(base) == []`" (`R:55`): a golden only records values. Add `test_validator_corpus_bases_clean`.
- **N-3.** `claimgate_golden_sweep.py:4-5` says the side-bound paths are "pinned by mutations", but `_TARGETS` doesn't include them. Fix the docstring together with M-1.
