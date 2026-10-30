VERDICT: ACCEPT_WITH_FIXES

# L9-ENV-5-OPUS-REV: delta review of the opt-in analysis clamp (lane L9-ENV)

Seat L9-ENV-5-OPUS-REV (Opus family). Code reviewed at `d8050fca6` on
`lane/2026-10-30-l9-env-analysis-clamp`. Delta: `0a799146c..d8050fca6`. Flag-off comparison:
`origin/main` (`12ce1241d`) against `d8050fca6`. The merged tree is `954ca4661`, a local merge of
`d8050fca6` with `origin/main` `12ce1241d`; it was not pushed. `.codex-report/L9-ENV-5.md` at
`6b7063860` (interim, `STATUS: BLOCKED`, with placeholders) was read as claims only. I used synthetic
data only (`JW_B5_SYNTHETIC_ONLY=1`). I did not open or search for real block-5/6/BYTES data. History
was fetched with `git fetch --unshallow origin`. Evidence is in `.codex-report/l9-env-5-opus-rev/`.

## Bottom line

The code applies O-F1, O-F3, O-F4 and O-F5 correctly and completely:

- With the flag off, the session is behaviourally origin/main.
- `reduce.py` and `scripts/run_campaign.py` are byte-identical to origin/main, and run_campaign
  cannot reach the clamp.
- Every session that the block-5 dry run constructs opts in.
- The new tests kill every seat mutant I re-ran (11 of 11 non-equivalent ones).

There is one blocker, and it only appears after merging. Current origin/main adds a registered
step-4 reason-class table. The table's blind generator reads string constants in
`analysis_engine/inputs.py`. The signature-gated opt-in at `inputs.py:3801-3804` introduces the
string constant `"analysis_clamp"`, so `tests/b5_analysis` fails on the merged tree (F1). Both of my
flag-plumbing mutants survive (F2, test gap only). The seat report's mutation bookkeeping is
inconsistent (F3).

## Findings (ranked)

### F1 (High, blocks merge). Merged with origin/main, `tests/b5_analysis` fails: the gated opt-in adds a step-4 "tooling" code

- **Where.** `joulewise/analysis_engine/inputs.py:3801-3804`:
  `if "analysis_clamp" in inspect.signature(AuthenticatedConsumptionSession).parameters:
  session_kwargs["analysis_clamp"] = True`. Both `"analysis_clamp"` literals are `ast.Constant`
  strings. `joulewise/analysis_engine/inputs.py` is in the generator's `modules` list.
- **Evidence.** Origin/main `b255ad1fe` added `tests/b5_analysis/test_step4_reason_table.py` and the
  registered `configs/analysis/b5/step4_reason_classes.json`, which pins `(len(mask), len(tooling))
  == (42, 1898)`. That test file is absent at `d8050fca6`, so the seat's own b5 run could not see the
  failure. I diffed the fresh generator output against the registered file on the merged tree:
  `tooling added ['analysis_clamp'] removed []`, with `modules` and `mask` unchanged. On origin/main
  alone, `tests.b5_analysis.test_step4_reason_table` gives `Ran 8 tests in 6.056s` / `OK`. On the
  merged tree, the whole directory fails:

  ```
  FAIL: test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file (tests.b5_analysis.test_step4_reason_table.Step4ReasonTableTests.test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file)
  AssertionError: {'sch[3968 chars]sis_corpus', 'analysis_manifest_file_sha256', [48109 chars] 4'}} != {'sch[3968 chars]sis_clamp', 'analysis_corpus', 'analysis_manif[48127 chars] 4'}}
  Ran 1035 tests in 4133.590s

  FAILED (failures=1, skipped=13)
  ```

  Full output: `l9-env-5-opus-rev/b5_analysis_failure.txt` and `b5_analysis_merged.log`.
- **Fix (recommended).** Do not regenerate the registered table: it is a pinned config with a
  recorded ruling. Instead, take the seat's NR1, which is now required rather than optional:
  - Pass `analysis_clamp=True` as a literal keyword at `inputs.py:3805`, as `9641561fb` did. A keyword
    name is an `ast.keyword`, not a string `Constant`.
  - Do the same at `floor_mint_estimator.py:490-491` for consistency. That module is not in the
    generator's list today.
  - Widen WRITE_SCOPE to `tests/test_analysis_integration.py`, so its fake session accepts
    `analysis_clamp`, and to `tests/test_floor_mint_estimator.py`, so its `assert_called_once_with`
    gains `analysis_clamp=True`.
  - Update `SIGNATURE_GATED` and the call-site test in `tests/test_whole_window_analysis_clamp_flag.py`
    to expect a literal `True` at all 12 sites.

  The other option is a string-free gate, but it would keep the mock-accommodation in production code
  (see F4).
- **Recheck.** Rerun `tests/b5_analysis` after a fresh merge with origin/main.

### F2 (Low, test binding). The runtime opt-in is never exercised in the block-5 session shape; both reviewer mutants survive

- **Where.** `joulewise/whole_window.py:1853-1857`, which selects the re-derivation from
  `self.analysis_clamp` alone. The code is correct. The finding is that no test binds that.
- **Evidence.** The block-5 dry run builds `mode='read_replay', archive_context=context`
  (`dry_run.py:1078-1081`). The produce_b5 and issuer sites pass `archive_context`. Every runtime
  clamp test, however, runs through `run_session` with the constructor defaults
  (`mode="issuing"`, no `archive_context`). The dry-run tests
  (`test_dry_run_step_results_session_opts_in`, `test_floor_extraction_with_kept_units_opts_in`) spy
  on the constructor kwargs only. Results (`l9-env-5-opus-rev/mutation_results.txt`,
  `own_mutants.py`):

  ```
  R-M1_flag_ignored_with_archive_context | SURVIVED | Ran 43 tests in 200.569s | OK
  R-M2_flag_ignored_in_read_replay | SURVIVED | Ran 43 tests in 207.064s | OK
  ```

  - R-M1 changes the selection to `if self.analysis_clamp and self._archive_context is None`.
  - R-M2 changes it to `if self.analysis_clamp and self.mode != "read_replay"`.

  Either mutant silently disables the clamp for exactly the block-5 dry run. By reading, `_prepare`
  has no mode- or archive-dependent branch between line 1848 and the `rederive` call, so the
  production code is not affected.
- **Fix.** Either:
  - parametrize `test_flag_off_refuses_permanent_widening_like_origin_main`'s flag-on contrast (and
    `run_session`) over `mode in {"issuing", "read_replay"}`, and add a case with a synthetic
    `ArchiveContext` whose survivors are the member; or
  - add a cheap AST pin that the `rederive` selection's test expression is exactly
    `self.analysis_clamp`.

### F3 (Low, report accuracy). The seat report's mutation bookkeeping does not match its own results file

- **Survivor count.** `L9-ENV-5.md` (at `6b7063860`) says "34 are killed and 4 survive" and "The
  table has 38 rows: 34 KILLED and 4 SURVIVED". `l9-env5/mutation_results.txt` has 38 rows: 35
  KILLED and 3 SURVIVED (`O-M03_eps_off_sign`, `O-M08_clamp_le`, `E-M14_always_recompute_body`).
  The "four" survivors are three mutants, one of which (OPUS M08) has two names (FABLE M03).
- **N12.** The report says "N01-N05 and N08-N12 are killed", but N12
  (`N12_floor_mint_estimator_gate_inverted`) is defined in `mutants.py` and has no row in
  `mutation_results.txt`. I ran it, and it is killed:
  `N12_floor_mint_estimator_gate_inverted | KILLED | Ran 43 tests in 188.750s | FAILED (failures=1)`.
- **Placeholders.** `MUTATION_RERUN_PLACEHOLDER`, `FINAL_TAILS_PLACEHOLDER` and
  `BASELINE_TAILS_PLACEHOLDER` are still present in the report. The report itself says it is
  interim.
- **Fix.** Correct the counts to "35 killed, 3 survived (4 names)", add the N12 row, and fill in the
  placeholders. The final tails should be re-taken after F1, on a tree merged with current
  origin/main.

### F4 (Info). The signature gates accommodate mocks in production code

At `inputs.py:3801` and `floor_mint_estimator.py:490`, `inspect.signature` of a `MagicMock`
constructor is `(*args, **kwargs)`, so patched tests never see the flag. With the real class the flag
is always passed: `test_default_is_off` pins the parameter, and the exact gated text is pinned. So
production is correct. F1's fix removes both gates.

## Q1: is each ruling applied correctly and completely?

**O-F1, flag off equals origin/main: PASS.** I diffed `git diff origin/main d8050fca6 --
joulewise/whole_window.py` hunk by hunk:

- The imports add only existing names from `reduce` and `bundle_read`. No import has side effects,
  and there is no new mutable module state (one str constant and one tuple).
- The three new functions are reached only through `_rederive_operative_summary`, which
  `_prepare:1853-1857` selects only when `self.analysis_clamp` is true.
- `__init__` stores `analysis_clamp is True`. `None`, `1` and `"yes"` count as off, and the flag is
  keyword-only with default `False`.
- The removed-member audit session passes `analysis_clamp=self.analysis_clamp` (`:1748`), so a
  flag-off parent builds flag-off members.
- With the flag off, the loop calls `_rederive_summary_for_authenticated_fiducial_bound` with the
  same arguments as origin/main.
- The only other difference is the new `analysis_clamp` attribute, which no serializer reads.
  `test_flag_off_*` checks this by comparing session state `json.dumps`-equal against
  `7ebb7db2a:joulewise/whole_window.py`, which is the merge base and equals origin/main for this
  file.
- No other caller of reduce's re-derivation exists outside `whole_window.py`. The only other
  session constructor inside `whole_window.py` is the member one.

**O-F1, run_campaign: PASS.** `git diff origin/main d8050fca6 -- joulewise/reduce.py
scripts/run_campaign.py` is empty, also on the merged tree. reduce.py blob is
`82449d58209278e756050762a0de6cd958558f7e`. run_campaign constructs one session without the flag
(`:8425`).

It does transitively import three opted-in modules:

- `analysis_manifest_v3`: `validate_prospective_analysis_manifest_v3`, `calculate_manifest_id`
- `analysis_engine.inputs`: `cleanup_claim_evidence_flags`, `normalized_campaign_representatives`,
  `token_provenance_from_artifacts`
- `floor_extraction`: `anchor_fallback_member_unusable`

An AST call-graph walk from those imported names reaches no `AuthenticatedConsumptionSession`
constructor in any of the three modules (`reaches constructor: False` for each). So run_campaign
cannot reach a flag-on session. `tests.test_run_campaign*` passes on the merged tree (tails below).

**O-F1, dry-run consumers: PASS.** I traced the step functions of `joulewise/b5_analysis/dry_run.py`:

- Steps 1, 2 and 9 go through `joulewise.cli`, i.e. reduce and the analyze path, which reaches
  `load_analysis_inputs` (gated, on).
- Step 4: `scripts.extract_detection_floors` → `floor_extraction.extract_cells` → `:3171`, flag on.
- Step 5: `mint_floor_artifact_generalized` → `mint_floor_artifact.py:547/1251`, flag on, plus
  `floor_mint_estimator._authenticated_common_mode_session` (gated, on).
  `mint_floor_artifact_generalized` pins signatures only, not source bytes, so the call-site edits
  do not trip it.
- Step 6: `run_d165_closeout_from_custody` → `block5_claim_gate_inputs`.
- Step 8: `finalize_analysis_manifest` → `analysis_manifest_v3:3771`, flag on.
- `_step_results`: `dry_run.py:1078`, flag on.
- produce_b5_disclosures and the issuer: flag on.

No constructor is left without the flag in `joulewise/` or `scripts/`. A grep outside those trees
finds only `docs/process_traces/**` exhibit copies. Origin/main since `4c26b2e2c` adds no
constructor (0 matches in `git diff 4c26b2e2c origin/main -- joulewise scripts`).

**O-F1, the two gated sites: correct in production, but see F1 and F4.** Both modules import
`inspect` (`inputs.py:15`, `floor_mint_estimator.py:11`), and the real class has the parameter.
N10 and N12 (the gate removed or inverted) are killed.

**O-F3: PASS.**

- `reproduced` counts only the four member-group prefixes, and is incremented only when the
  recorded envelope equals reduce's own function on the mirrored contributions.
- With zero reproduced, the summary is returned unchanged.
- The K3 fake-reader differential is present (`test_fake_reader_differential_against_reduce_v060_grouping`).
- N06 is killed by 3 tests.

**O-F4: PASS.** K1, K2 and K4 are ported, and so are the ulp seeds. O-M01 and E-M02 are killed;
I re-ran both.

**O-F5: PASS.** The guard `any(window.end_s < window.start_s ...)` is in the `None` guard
(`whole_window.py:990-992`), after reduce's own mint call. N07 is killed by 3 tests.

## Q2: mutants re-run by this reviewer

Run in `/tmp` worktrees at `d8050fca6`. The command was `python3.13 -m unittest
tests.test_whole_window_inverted_corner_clamp tests.test_whole_window_analysis_clamp_flag`. Each
mutant was applied in place and then restored, with a `git diff --quiet` assertion after each one.
Runner: `l9-env-5-opus-rev/runner.py`, using the seat's `mutants.py` and my `own_mutants.py`.

Unmutated baseline: `Ran 43 tests in 195.311s` / `OK`.

```
N08_dry_run_flag_off | KILLED | Ran 43 tests in 206.825s | FAILED (failures=2)
N09_floor_extraction_flag_dropped | KILLED | Ran 43 tests in 207.899s | FAILED (failures=1, errors=1)
O-M01_clamp_to_start | KILLED | Ran 43 tests in 204.453s | FAILED (failures=3)
E-M02_clamp_to_end | KILLED | Ran 43 tests in 200.942s | FAILED (failures=1)
N12_floor_mint_estimator_gate_inverted | KILLED | Ran 43 tests in 188.750s | FAILED (failures=1)
N06_drop_OF3_reproduced_guard | KILLED | Ran 43 tests in 198.440s | FAILED (failures=3)
N07_drop_OF5_input_inversion_guard | KILLED | Ran 43 tests in 211.929s | FAILED (failures=3)
N04_member_sessions_drop_flag | KILLED | Ran 43 tests in 209.330s | FAILED (failures=1)
O-M13_flag_on_session_unclamped(rt) | KILLED | Ran 43 tests in 180.329s | FAILED (errors=5)
O-M08_clamp_le | SURVIVED | Ran 43 tests in 196.572s | OK          (equivalent, see Q3)
R-M1_flag_ignored_with_archive_context | SURVIVED | Ran 43 tests in 200.569s | OK   (F2)
R-M2_flag_ignored_in_read_replay | SURVIVED | Ran 43 tests in 207.064s | OK         (F2)
```

All of these match the seat's verdicts. N12 had no seat row before (F3). N04 is killed only by the
AST pin `test_removed_member_audit_sessions_inherit_the_flag`. That is acceptable, because the pin
requires the literal expression `self.analysis_clamp`.

## Q3: are the survivors equivalent?

There are three distinct mutants. The fourth "name" is the FABLE alias of OPUS M08.

- **OPUS M03 (`end_s - eps_off_s`): equivalent.** `eps_off` iterates over `(-e, +e)`, so the mutant
  visits the same four corners in a different order. A `None` at any corner refuses in either order.
  `min` and `max` are order-free unless there is a NaN or a signed-zero tie:
  - NaN is excluded, because each corner envelope from `_anchor_shift_envelope` passes its own
    finiteness check (`reduce.py:2121-2124`).
  - `-0.0` cannot occur, because `_shift_energy_j` starts from `total = 0.0` (`reduce.py:1999`) and
    adds nonnegative terms (power is guarded ≥ 0, overlap is `max(0.0, ...)`).
- **OPUS M08 / FABLE M03 (`<=`): equivalent.** The two differ only when `end_s == start_s` exactly.
  Then the result is `(s + s) / 2.0`, which equals `s` bit for bit for every finite
  `|s| < 2^1023` (exact doubling and halving, including subnormals and `-0.0`). Re-origined times are
  far below that.
- **FABLE M14 (drop `return minted`): equivalent.** I diffed the AST source segments of
  `reduce._corner_composed_anchor_shift_envelope` and `_clamped_corner_composed_anchor_shift_envelope`.
  Apart from docstrings and comments, they differ in exactly three places:
  - the early `minted` call and return;
  - the O-F5 guard;
  - the clamp list comprehension, which replaces `if any(...end_s < start_s...): return None`.

  When reduce defines an envelope, no corner inverted. An inverted input window inverts at least at
  the `(+e, -e)` corner, and at every corner when `e = 0`, so reduce refuses it. In that case the
  O-F5 guard is false and the comprehension is the identity. The body then performs reduce's
  operations in reduce's order and returns an equal dict with the same key order.

## Q4: tests at `d8050fca6` merged with origin/main `12ce1241d` (merge `954ca4661`)

Environment:

- Python 3.13, Linux container.
- `TMPDIR=/tmp/lninerev/tmp` (outside the checkout, no float-like token).
- `JOULEWISE_CUSTODY_PARENT=/tmp/lninerev/custody`.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`.

`tests/b5_analysis` was run with `python3.13 -m unittest discover -s tests/b5_analysis -t .`. Every
other module ran as its own process (`l9-env-5-opus-rev/suite.sh`, `modules.txt`). Format:
`module | Ran line | last line`.

```
b5_analysis | Ran 1035 tests in 4133.590s | FAILED (failures=1, skipped=13)     <- F1
tests.test_floor_extraction | Ran 145 tests in 33.992s | OK (skipped=2)
tests.test_run_campaign | Ran 267 tests in 497.104s | OK (skipped=1)
tests.test_run_campaign_hazard_flags | Ran 46 tests in 32.722s | OK (skipped=3)
tests.test_run_campaign_max_blocks | Ran 22 tests in 11.810s | OK
tests.test_run_campaign_p2_rc | Ran 35 tests in 47.235s | OK
tests.test_whole_window | Ran 26 tests in 1.848s | OK
tests.test_whole_window_analysis_clamp_flag | Ran 11 tests in 118.613s | OK
tests.test_whole_window_inverted_corner_clamp | Ran 32 tests in 191.867s | OK
tests.test_whole_window_parallel_strict | Ran 8 tests in 2.551s | OK
tests.test_whole_window_selection | Ran 57 tests in 225.617s | OK
```

The single b5 failure is
`test_step4_reason_table.Step4ReasonTableTests.test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file`
(F1). The same module at origin/main alone: `Ran 8 tests in 6.056s` / `OK`. Wall times are inflated
because the mutant runs shared the 4 CPUs.

## Required before merge

1. F1: pass the flag as a literal keyword at `inputs.py:3805` and `floor_mint_estimator.py:480`.
   This needs WRITE_SCOPE for the two pinned tests. Then re-run `tests/b5_analysis` on a fresh merge
   with origin/main.
2. F3: correct the seat report.
3. Recommended: F2's test.
