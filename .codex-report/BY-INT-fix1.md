## PROGRESS

- Done (slice 2): continued clean director commit b253a8a09. All three new roster tests fail on archived bda481d5a and pass after. Nine-model native CLI chain and all twin stages pass; H1=18, H2 k=8/8/10; 8,033 comparisons with zero above bar. Wrong-nine/eleven rosters refuse in both programs. Ten-model numerical outputs are raw byte-identical and frozen predictions differ only in the director-approved source digest. One-missing-withheld-file chain passes and discloses bytes.withheld_missing. Required focused modules/classes pass; static import checks 5/5; census empty; all generator checks exit 0.
- Next: director commits/pushes these final test/report changes, records PR #535 CI, and runs the host dynamic import-graph check outside the sandbox per note 3. BY-MERGE carries the mapped hunks; BY-SLOTS/BY-REG own the listed deferred generation/slot text.
- Open: no unresolved ruling or in-scope implementation work. No repository Git writes/pushes attempted. Current HEAD b253a8a09e62c3a5fd694ca26e0085a016a0b5c1; final slice is uncommitted for the director.

BY-INT-fix1 COMPLETE

## SUMMARY

The registered nine-model alternative works through the complete native CLI stage chain.
Analysis and twin retain H1 k=18 from the frozen roster and H2 primary k=8/8/10.
All three new tests fail at untouched production baseline bda481d5a and pass after the fix.
Nine-model agreement compares 8,033 fields with zero differences above the existing bars.
The ten-model numerical files are byte-identical; only expressly permitted provenance digests differ.
The one-missing-withheld-file chain exits 0 and retains H1=18 with bytes.withheld_missing disclosure.
Findings 2–8 have their directed fixes or named BY-SLOTS hand-forwards; generators and census remain clean.
Required local tests/checks pass; host dynamic import verification and new-head PR #535 CI remain director-owned.

## FIX LOG

| Finding | Severity | Disposition | Commit / evidence |
| --- | --- | --- | --- |
| 1 | major | fixed; generator hand-forward deferred to BY-SLOTS/BY-REG | Production/fixture changes committed by director in b253a8a09; final new tests in this working tree. Three failures before / three passes after; native nine-model chain, 8,033 comparisons, identity and missing-file controls below. |
| 2 | minor | fixed | b253a8a09; only dated correction in BY-INT.md. Parity branch grep confirms both Q1 counts, normalized flag, missing status and answer coverage. |
| 3 | minor | catalog row fixed; four slots deferred to BY-SLOTS | b253a8a09; Appendix A equals current catalog SHA; slot values and code locations under OPEN ISSUES. |
| 4 | nit | fixed | b253a8a09; scale-relative solver pivot and FPMIN comment. Twin still 57 passing tests; agreement comparison counts checked below. |
| 5 | nit | fixed | b253a8a09; one docstring line only: 1e-6 / 2.2e-16 is about 4.5e9. |
| 6 | nit | fixed | b253a8a09; authority includes Addendum 9 and Q2; Q2/roster paragraphs outside Inputs and release. |
| 7 | information | rejected as a code change: no_change_needed; procedural wording deferred to BY-SLOTS | Information only; reviewer dispositions flag, not refuse; D-161 regards operator-only refusal as over-engineering. |
| 8 | nit | fixed | b253a8a09; extra blank removed in campaign.py. |

## CHANGES

- `joulewise/bytes_analysis.py`: registered names/constants near H1/H2 constants; `h1_checks` helper immediately before `validate_manifest`; replace only the roster cardinality predicate in `validate_manifest`, preserving role/fit/MoE/tier checks; `_phase_cell` keyword family and quantile; pass that family from `reduce_models` including without-assisted diagnostic; frozen H1/H2 roster counts; `evaluate` cardinality from frozen roster family (three fit plus H1/three). Empty manifest stubs retain full-roster counts for existing arithmetic-only callers; CLI still validates all manifests.
- `scripts/bytes_analyze.py`: one hunk, analysis_record H1_checks reads frozen H1_checks.
- `scripts/bytes_twin.py` (BY-MERGE carry map): `_betacf` FPMIN comment; `_solve` scale-relative pivot threshold; `read_manifest` duplicate canonical name check; start of `analyse` validates full/drop roster and derives held_out/h1_family; alpha_h1 uses family; h2_points loops present roster; multiplicity prints family; two held-out loops and manifest predictions loop use local held_out; output roster contains present models. No header or CLI refactor.
- `tests/fixtures/bytes/campaign.py`: optional drop_8b_8bit filters design models before config keys, removes extra blank, filters absent name from sub-pack schedule. The remaining model in the shared sub-pack remains scheduled, with single-model midpoint treatment.
- `tests/test_bytes_roster_drop.py`: new module with RegisteredRosterTests and RosterCLIChainTests, three tests; full/drop acceptance plus wrong nine/eleven refusals in both programs; frozen H1/H2 counts; production sub-pack campaign through native subset release and real stage-1 Git commitment, exact H1 interval arithmetic, all twin stages and the existing agreement harness. Every new test fails baseline. Reusable build_campaign/run_chain helpers also drive the recorded identity and missing-file checks.
- `tests/test_bytes_agreement.py`: exactly one docstring line, replacing erroneous 4,500 factor with about 4.5e9 and derivation; next line unchanged.
- `docs/contracts/bytes_tables.md`: authority hunk names Addendum 9 and Q2; two paragraphs immediately below Arithmetic and output schema describe dropped roster and Q2 fields. Inputs and release untouched.
- `docs/registrations/bytes_pack_v1.md`: only §18 catalog-SHA row marked FILLED, pointing to Appendix A.
- `.codex-report/BY-INT.md`: only dated finding-2 correction following original agreement paragraph. Read-only parity branch grep finds canonical missing flag, both counts, missing cell/point/H1 status and MoE answer regression.
- `.codex-report/BY-INT-fix1.md`: progress and evidence for this round.

BY-MERGE carry map, relative to bda481d5a (production edits all in b253a8a09):

- `joulewise/bytes_analysis.py`: constants at 27; helper plus `validate_manifest` roster predicate at 385–399; `_phase_cell` signature at 1060; quantile at 1091; main and without-assisted calls at 1160 and 1169; frozen counts at 1273; evaluation record count at 1291. Preserve the parallel config_key check after role checks. The only validate_manifest edit is its opening cardinality/name predicate.
- `scripts/bytes_analyze.py`: line 129, use frozen H1_checks in analysis_record; no other hunk.
- `scripts/bytes_twin.py`: FPMIN comment at 113; solver rule at 196; duplicate canonical-name check at 538; analyse opening roster/family at 1301; alpha at 1322; h2_points roster iteration at 1401; multiplicity at 1412; the two held_out loops at 1429/1435; manifest predictions at 1452; output roster at 1473. Carry each onto the twin-parity rewrite without its superseded header/read_manifest/analyse/main implementation.
- `tests/test_bytes_agreement.py`: line 153 only. No comparison function changed.
- `docs/contracts/bytes_tables.md`: authority lines 3–5; two paragraphs after Arithmetic and output schema at 171–186. No Inputs and release hunk or change to its ten-distinct-models sentence.

## TESTS RUN

All repository-code commands used `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B`. Temporary directories were created with `tempfile.TemporaryDirectory(prefix="jwtmp-byintf1.", dir="/tmp")` and cleaned after each run. No whole suite ran.

Baseline export: `mkdir -p /tmp/byint-fix1-slice1/before`; `git -C /Users/edr/code/JouleWise-by-int archive bda481d5a | tar -x -C /tmp/byint-fix1-slice1/before`. Copied new test module and changed campaign fixture only. Python cwd was that before directory for the baseline run.

Slice-1 initial before and after command (each fresh TMPDIR): `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_roster_drop`. Baseline: 2 tests, exit 1, one error (ten-model refusal), one failure (21 != 18). After: 2 tests, exit 0, no skips, 0.002 s.

`/opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/run_tests.py twin tests.test_bytes_twin` runs `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_twin`: 57 tests, exit 0, no skips, 20.600 s. Evidence: twin.log/twin.json in that scratch directory.

`/opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/run_tests.py focused tests.test_bytes_roster_drop tests.test_bytes_analysis.BoundaryAndStagingTests`: 12 tests in 46.375 s, exit 1: only changed-manifest stub errored; the other 11 passed. That empty-stub compatibility error was fixed immediately. A focused replay via `run_tests.py freeze-rerun tests.test_bytes_roster_drop tests.test_bytes_analysis.BoundaryAndStagingTests.test_changed_manifest_refuses_commitment tests.test_bytes_analysis.BoundaryAndStagingTests.test_predictions_only_fit_and_hash_is_exact_file_bytes` passed 4 tests, exit 0, 0.035 s. A separate full BoundaryAndStagingTests rerun, `run_tests.py boundary-final tests.test_bytes_analysis.BoundaryAndStagingTests`, passed 10 tests, exit 0, no skips, 44.004 s. These initial combined invocations shared a TMPDIR across their two named modules; all final module acceptance runs were separate.

`/opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census`: exit 0, all five arrays empty. `/opt/homebrew/bin/python3.13 -B scripts/bytes_plan_trees.py --check`, `/opt/homebrew/bin/python3.13 -B scripts/build_b6_flag_catalog.py --check`, `/opt/homebrew/bin/python3.13 -B scripts/bytes_mac_kit.py --check`: all exit 0. These are check-only commands, not test modules. `git diff --check`: exit 0.

Catalog SHA-256: `4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f`, still equals Appendix A.

A first shell cleanup wrapper was rejected before execution for `rm -rf`; replaced with Python TemporaryDirectory cleanup. No tests ran in the rejected calls.


Additional separate-module runs used `/opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/run_tests.py MODULE MODULE`, which invokes `/opt/homebrew/bin/python3.13 -B -m unittest -v MODULE` in the repository, each in its own fresh cleaned TMPDIR, with both required environment variables. Exact module arguments and results:

| MODULE | Count | Exit | Skips / elapsed |
| --- | ---: | ---: | --- |
| tests.test_bytes_manifest | 16 | 0 | none; 0.588 s |
| tests.test_bytes_gates | 7 | 0 | none; 1.193 s |
| tests.b6.test_release_subset | 4 | 0 | none; 0.132 s |
| tests.hazards.test_refusal_allowlist | 23 | 0 | 1 skip: historical block-5 design branch absent from clone; 18.046 s |

Slice 2 final acceptance evidence (all test commands use a fresh module-specific TemporaryDirectory TMPDIR, cleaned after exit, plus both required environment variables):

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_roster_drop`

Result: 3 tests, exit 0, no skips; pass; unittest elapsed 15.808 s.

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_twin`

Result: 57 tests, exit 0, no skips; pass; unittest elapsed 18.738 s.

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_agreement`

Result: 8 tests, exit 0, no skips; pass; unittest elapsed 81.423 s.

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_agreement`

Result: 8 tests, exit 0, no skips; pass on archived baseline; unittest elapsed 92.731 s. Python cwd was `/tmp/byint-fix1-slice1/before`.

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_analysis.Q1WithheldCensusTests tests.test_bytes_analysis.Q1MissingFilesCLIChainTests tests.test_bytes_analysis.Q2CommitmentCLIChainTests tests.test_bytes_analysis.SubsetReleaseChainTests tests.test_bytes_analysis.ProductionArchiveTests.test_full_size_real_reducer_harvest_and_export_ingress tests.test_bytes_analysis.H2WorkedExamples tests.test_bytes_analysis.Addendum4RegressionTests.test_a4_02_p02_primary_family_and_two_regressor_tier`

Result: 16 tests, exit 0, no skips; pass; unittest elapsed 167.153 s.

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.hazards.test_import_graph.ImportGraphTests.test_hazard_modules_reach_no_retired_module tests.hazards.test_import_graph.ImportGraphTests.test_the_analyzer_sees_the_measurement_core_reach_arm_readiness tests.hazards.test_import_graph.ImportGraphTests.test_hazard_modules_import_no_flag_code tests.hazards.test_import_graph.ImportGraphTests.test_flags_package_reaches_no_retired_module tests.hazards.test_import_graph.ImportGraphTests.test_the_adapter_import_is_confined_to_the_capture_child`

Result: 5 tests, exit 0, no skips; pass; unittest elapsed 0.372 s.

Before new-test command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/slice2_checks.py baseline` invokes `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_roster_drop`, with Python cwd `/tmp/byint-fix1-slice1/before` and fresh cleaned TMPDIR. Baseline production was untouched; only the new test and changed campaign fixture were copied into the archive. All three tests fail: frozen family 21 != 18; alternative roster validation errors; real blinded CLI exits 1 with ten-distinct-models refusal. Exit 1, two failures/one error, no skips; 10.874 s. After: all three pass as above. The homebrew executable resolves internally to /opt/homebrew/opt/python@3.13/bin/python3.13 (the same interpreter).

The five static import-graph checks pass; director note 3 assigns the host process-group dynamic child to the director outside this sandbox. No dynamic check was rerun this slice. An initial static invocation used two nonexistent test method names and exited 1 with two loader AttributeErrors; the corrected five real method names above passed immediately. Historical slice-1 dynamic attempts are superseded by director note 3 and are not acceptance evidence here.

The final remaining-analysis command includes every required Q1/Q2/subset class plus the test calling validate_manifest, H2 quantile/critical examples and the P02 family critical test. BoundaryAndStagingTests already passed separately 10/10 in slice 1. No existing test mentions H1_CHECKS; the new CLI test checks the H1 critical arithmetic exactly. CampaignWordRates and test_a4_05_p03_coverage remain CI-only per the local route; the whole module/suite was not run.

Agreement comparison totals are unchanged at baseline/current: bytes 9,966; defects 10,026; minimum 10,091; resident 9,966; time 9,966. Every above-bar count is zero. Equal/under-bar subdivisions depend on the independently drawn hidden offsets and were before → after: bytes 5,580/4,386 → 5,556/4,410; defects 5,569/4,457 → 5,591/4,435; minimum 5,535/4,556 → 5,559/4,532; resident 5,735/4,231 → 5,684/4,282; time 5,621/4,345 → 5,637/4,329. No expected field/word/refusal count changed.

Final check-only commands (fresh cleaned TMPDIR for each, required environment variables): `/opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census`; `/opt/homebrew/bin/python3.13 -B scripts/bytes_plan_trees.py --check`; `/opt/homebrew/bin/python3.13 -B scripts/build_b6_flag_catalog.py --check`; `/opt/homebrew/bin/python3.13 -B scripts/bytes_mac_kit.py --check`. Each exits 0. Census unlisted/stale/miscounted/guard_changed/scope_gaps are all []. Catalog SHA remains 4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f, matching Appendix A. No registry edits were needed. `git diff --check` exits 0.

## END-TO-END

Nine-model test uses seed 1100, real reducer/export fixtures with all twelve registered sub-pack sessions, non_claim=False, and no initial key release. Qwen3-8B-8bit is filtered before configurations, runs, references, native registration and key draws. The other model in its shared sub-pack remains with single-model midpoint placement. Its manifest/private key identities and all JSON outputs contain no dropped name.

The helper commands in tests/test_bytes_roster_drop.py run blinded; native fit subset release; fit; an actual disposable stage-1 Git commit; blinded with that commit; native held-out subset release with that commit; heldout using frozen predictions. Every process exits 0. Twin blinded/1/2 also exit 0; stage 2 receives the withheld CSVs explicitly because this baseline twin does not auto-open the B4 store. H1=18 at all twin stages and in frozen analysis predictions. Every computed fit/held-out pass h is exactly student_t_quantile(1 - 0.05/36, df) * sqrt(variance), using the same function and inputs. H2 primary k is rails 8, DC input 8, rest 10. Existing agreement.compare_campaign supplies all bars: 8,033 comparisons, 4,599 equal, 3,434 under bar, zero above.

Ten-model identity command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/slice2_checks.py identity`, exit 0. A seed-1100 production-shaped campaign is generated once and both complete CLI chains run against exactly those inputs/paths, first with archived baseline production as Python cwd, then current production as cwd. Each chain makes its own fit commitment and uses its own code throughout. The four held-out output files compare as raw bytes:

| File | Before SHA-256 = after SHA-256 |
| --- | --- |
| model_estimates.json | `9615cd8d5f122e5446ab353e4f61e4a86a94b8940f3f01696f314d984e68bdb9` |
| h1.json | `a17d36891a04d4ffa119c6c78bd27f89b7507ab42c10cb3da36737f879569c82` |
| h2.json | `117caed5542fc39a8863093d26c789156878a3331708cb1f34b1920cd329fc8f` |
| moe.json | `51cea32c55891d92325f4534f8b063efaf9274da39d586fa9b5f40d5d9a3917b` |

Director note 1 permits only source and derived commitment digests to differ. Raw frozen bytes become exactly identical after replacing the after bytes_analysis_sha256 string with the before string; every other field and byte is identical. Provenance values (both committed/evaluating values in analysis_record are identical within their own run):

| Field | Before | After |
| --- | --- | --- |
| Frozen bytes_analysis_sha256; analysis_record.bytes_analysis_sha256.committed and .evaluating | `ae8c856d6467f8f51fae3c4e966d7948e64fadbbad22ada066d28748d52a1186` | `cdedcd5d53cea3cafc99052bc4200dfcf4fba9bc19e12d62b61b63ce42216471` |
| Raw predictions.json SHA-256; predictions.sha256 sidecar; analysis_record.predictions_sha256 | `66c9b4b49593066ca7f36f4eda2e2bd90d449ea816482e597c2b0617a7d9a83a` | `c1d8fe4f97dc2210d1d3f9937b382d0e3fe42bc863fc58fea23b19b966710c19` |

No other commitment-digest field is compared or exempted. Numerical artifacts are unnormalized raw bytes. Keys are drawn once and read-only reused to make the inputs identical, avoiding differences from independent random offsets.

Q1 missing-file command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/slice2_checks.py missing`, exit 0. A fresh nine-model campaign has only bytes-s2-p2's held-out store deleted before the chain. Generation, blinded, fit release, fit, stage-1 Git commit, blinded post-commit, heldout release and heldout all exit 0. Frozen H1 stays 18. Blinded post-commit prints primary rails n=9, k=8 and two-pass sensitivity n=8, k=8. Heldout prints primary n=9 for each boundary, k=8/8/10; the two-pass sensitivity has n=8 for each boundary, k=8/8/10. The Qwen3-30B-A3B-4bit survivor is one_pass, n_passes=1 with bytes.withheld_missing on every boundary. The aggregate point flag union is exactly [bytes.withheld_missing]. Evidence JSONs retain exact process argv/exit records; their temporary campaigns are cleaned.

## CI

Branch is lane/2026-10-22-bytes-pass1, current HEAD b253a8a09e62c3a5fd694ca26e0085a016a0b5c1 (director's slice-1 commit). This slice leaves only the new tests/report additions uncommitted. The local route prohibits repository Git writes and network pushes; the director commits and pushes the final slice. PR #535 is already draft. Director reports CI running at b253a8a09; this seat cannot observe its result. Last supplied finished baseline observation is 20/20 green except expected gate-ledger at bda481d5a. No unobserved green result is claimed.

## DECISIONS I MADE

- Registration §§2/10 select the optional model by exact manifest model name Qwen3-8B-8bit; twin uses its canon() equivalent. No other nine-model or eleven-model roster is accepted.
- H1 uses registered held-out membership even if a cell is missing. Keep H1_CHECKS=21 as the full-roster compatibility value for p02; actual manifests determine 21 or 18. Arithmetic-only empty manifest stubs retain their historic full-roster expectation; CLI validation remains mandatory.
- Preserve the twin duplicate canonical-name check per director note 2: it mirrors the analysis's existing duplicate desk-input refusal.
- Apply director note 1's exact provenance-only digest exception; no numerical normalization or new numerical bar. Native twin/analysis comparison functions and their bars are reused unchanged.
- User local route/exhaustive allowlist override general bookkeeping, whole-suite and commit/push instructions. No other branch was merged or cherry-picked; registries and generators needed no edits.

## OPEN ISSUES

- BY-SLOTS/BY-REG own dropped-roster plan-tree and registration generation. The shared sub-pack with Qwen3-32B-4bit must retain that model and its references while excluding every dropped-model run/config/key; no generator edits are authorized here.

- BY-SLOTS slot hand-forward: group key directory is `<pack_records_root>/bytes/blinding` (`joulewise/b6/blinding.py:102`, identity at 104, directory at 108). Withheld store is `<group records root>/withheld/<pack_id>/<session_id>.runs.csv` (`joulewise/b6/blinding.py:91`, path at 96; exporter calls at `joulewise/b6/export_runs.py:190`). Flag is `bytes.withheld_missing` (`scripts/bytes_analyze.py:42`; analysis census/reduction retains row counts). Stage option `--stage1-commit` is declared at `scripts/bytes_analyze.py:55` and format-checked at 65; subset release checks at `scripts/b6_release_subset.py:22`. It accepts 40 or 64 hexadecimal characters, without Git object existence validation. Registration slot text should explicitly call this procedural protection. Four slot texts deliberately remain unfilled.

## NEEDS_RULING

none. The slice-1 provenance question was resolved by director note 1; applied as recorded above.


## ROUND B (review of ad145c044)

### PROGRESS (round b)

BY-INT-fix1 ROUND B COMPLETE

- All after/before checks and evidence complete. Round a byte-preserved; only this report changed. Scratch exports, helpers and module TMPDIRs cleaned after recording evidence.
- Branch lane/2026-10-22-bytes-pass1; HEAD da27be7b965088b7d2e6697ca48c98512a9b442b. Next: director reviews/commits report; BY-MERGE integrates 478873066.

### SUMMARY

Finding 1 is verified by execution at merged tree ca623e0f3345b6fb60b3b7b15a1d828bb042b65f (review-fixes 478873066 plus main abd9f1597).
The manifest reproduces byte for byte; all ten config_key values match the reviewer regeneration and registered_config_key(model_name).
The Q1 probe returns both disclosure counts; deleting one key raises AnalysisError at validation.
All required after modules and named Q1 end-to-end checks pass; all five refusal-census arrays are empty.
At da27be7b9, copied FrozenManifestTests fails and the analysis-shaped baseline silently loses the withheld disclosure.
Finding 2 goes to the CI-timings owner; finding 3 requires no repository edit; finding 4 goes to BY-SLOTS/BY-REG.
Only this report changed; round a is unchanged. No code/config/test or repository Git metadata write, push or PR action occurred.
The director commits this report; BY-MERGE carries the existing review-fixes next.

### FIX LOG

| Finding | Severity | Disposition | Commit / branch | Evidence / hand-forward |
| --- | --- | --- | --- | --- |
| 1 | minor | fixed | bd4a5603c5dbe5d6e095e81122d3db60a576f933; follow-up 4788730660b8a9b9342890a75d69c36b36057b88 on lane/2026-10-22-bytes-pass1-review-fixes | Verified here at ca623e0f3: byte reproduction, ten exact key matches, manifest/roster/Q1 tests pass, both disclosure counts, missing key rejected. Baseline regression fails and silent path reproduces. BY-MERGE carries it next. |
| 2 | minor | deferred to CI-timings owner | CI-timings lane | Director routes missing tests.test_bytes_* timings and shard imbalance. scripts/test_timings.json is outside scope. |
| 3 | nit | rejected as a repository change | Director ledger correction; existing .codex-report/BY-INT.md retained | Literal rg search finds no erroneous re-dispatch sentence in repository reports/docs. Existing report remains authoritative; director records correction. No claim that BY-TWIN's pending fields are complete. |
| 4 | nit | deferred to BY-SLOTS/BY-REG | BY-SLOTS/BY-REG | docs/contracts/bytes_tables.md line 13 still says ten distinct models at 478873066; Arithmetic and output schema permits nine. Hand-forward: align Inputs and release with that alternative. |

### TESTS RUN

Synthetic desk execution only. Every Python command used `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B`. Each invocation received a separate fresh cleaned TMPDIR under `/tmp/jwtmp-byintf1b.*`, via `TemporaryDirectory(prefix='jwtmp-byintf1b.', dir='/tmp')`. Children inherit those variables. Commands use `subprocess.run(command, cwd=export_path, env=..., ...)`; no compound cd. No whole analysis module or whole repository suite ran.

Scratch root `S=/tmp/jwtmp-byintf1b.ij6h27_1`, resolved spelling `/private/tmp/jwtmp-byintf1b.ij6h27_1`. Exports, exit 0 each:

```sh
git -C /Users/edr/code/JouleWise-by-int archive ca623e0f3345b6fb60b3b7b15a1d828bb042b65f | tar -x -C /tmp/jwtmp-byintf1b.ij6h27_1/after
git -C /Users/edr/code/JouleWise-by-int archive da27be7b965088b7d2e6697ca48c98512a9b442b | tar -x -C /tmp/jwtmp-byintf1b.ij6h27_1/before
```

Read `scripts/bytes_manifest.py merge --help` in after, exit 0. Options: --headers, --kv, --pilot, --out. --pilot is optional, default docs/design/bytes_pilot/summary_rows.json; supplied explicitly. Generator command in after, following the common environment/interpreter prefix, exit 0:

```sh
scripts/bytes_manifest.py merge --headers configs/bytes/records/*.headers.json --kv configs/bytes/records/*.kv.json --pilot docs/design/bytes_pilot/summary_rows.json --out /tmp/jwtmp-byintf1b.ij6h27_1/regenerated.json
```

The helper expands both globs into lexically sorted paths before subprocess execution. Raw bytes satisfy `assert committed == regenerated`; no normalization. SHA-256:

- Committed configs/bytes/bytes_manifest.json: `76452108c1a10b1f63b48fc95b306b6c4aa936a0d2e94244be65dc067c356264`.
- Regenerated scratch output: `76452108c1a10b1f63b48fc95b306b6c4aa936a0d2e94244be65dc067c356264`.

Reviewer input was read only: `/private/tmp/claude-501/-Users-edr-code-JouleWise/2dc9c377-4ec4-4750-b44d-4d8cd5ae9354/scratchpad/byint/manifest_regen.json`, SHA-256 `642f260bfd5638fc435f08041359f4fdc009f8f7edf1fb783e6642c417ea8d79`. Compared keys by exact model_name, since BY-REV adds analysis metadata absent from reviewer file. Every key below equals both reviewer[model_name].config_key and registered_config_key(model_name):

| Model | config_key |
| --- | --- |
| Llama-3.3-70B-Instruct-4bit | `Llama-3.3-70B-Instruct-4bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3-1.7B-4bit | `Qwen3-1.7B-4bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3-14B-4bit | `Qwen3-14B-4bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3-30B-A3B-4bit | `Qwen3-30B-A3B-4bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3-32B-4bit | `Qwen3-32B-4bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3-4B-4bit | `Qwen3-4B-4bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3-8B-4bit | `Qwen3-8B-4bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3-8B-8bit | `Qwen3-8B-8bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3-Next-80B-A3B-Instruct-4bit | `Qwen3-Next-80B-A3B-Instruct-4bit\|bytes_synthetic_2048_decode_512\|512` |
| Qwen3.5-122B-A10B-4bit | `Qwen3.5-122B-A10B-4bit\|bytes_synthetic_2048_decode_512\|512` |

Separate test processes: exact arguments after the common environment/interpreter prefix above. Cwd S/after unless marked before. Counts include the skip.

| Label / cwd | Arguments | Tests | Exit | Skips / wall seconds |
| --- | --- | ---: | ---: | --- |
| after-manifest / after | `-m unittest -v tests.test_bytes_manifest` | 17 | 0 | none; 1.28 |
| after-roster / after | `-m unittest -v tests.test_bytes_roster_drop` | 3 | 0 | none; 14.853 |
| q1-census / after | `-m unittest -v tests.test_bytes_analysis.Q1WithheldCensusTests` | 4 | 0 | none; 0.839 |
| q1-cli / after | `-m unittest -v tests.test_bytes_analysis.Q1MissingFilesCLIChainTests.test_one_withheld_file_missing_cli_chain tests.test_bytes_analysis.Q1MissingFilesCLIChainTests.test_both_withheld_files_missing_cli_chain tests.test_bytes_analysis.Q1MissingFilesCLIChainTests.test_genuinely_uncollected_optional_pass_cli_chain` | 3 | 0 | none; 35.925 |
| before-frozen / before | `-m unittest -v tests.test_bytes_manifest.FrozenManifestTests` | 1 | 1 | none; 1.098 |
| refusal-tests / after | `-m unittest -v tests.hazards.test_refusal_allowlist` | 23 | 0 | 1: historical block-5 design branch unavailable in archive; 14.715 |
| q1-extra / after | `-m unittest -v tests.test_bytes_analysis.SubsetReleaseChainTests.test_three_worlds_full_synthetic_cli_chain_and_clock_removal tests.test_bytes_analysis.Addendum7RegressionTests.test_q1_missing_moe_has_explicit_h1_and_active_or_resident_rows tests.test_bytes_analysis.ReviewInputTests.test_manifest_requires_public_config_key tests.test_bytes_analysis.ReviewInputTests.test_missing_store_records_and_pass_rows_disclose_checked_path` | 4 | 0 | none; 56.953 |

Before run copied only S/after/tests/test_bytes_manifest.py into S/before/tests/test_bytes_manifest.py with shutil.copyfile. Baseline production/config files unchanged. FrozenManifestTests ran one test and failed at line 346, the raw-byte assertion: committed bytes have config_sha256 where regenerated bytes introduce config_key. Exit 1 is the expected negative control. The same test passes in the 17-test after module.

Found Q1 names with `rg -n 'withheld_missing|^class Q1|^    def test_' tests/test_bytes_analysis.py`, then ran explicit names above. One-file, both-file and genuinely uncollected optional-pass chains pass, retain missing-versus-uncollected labels and assert bytes.withheld_missing on relevant pass/point/H1/MoE rows. Subset-release three-world chain and MoE missing-label regression pass. Nine-model native analysis/twin chain compares 8,033 fields, zero above existing bars.

Probe commands, common environment/interpreter prefix and fresh TMPDIR each: `S/probe.py after S`, cwd S/after, exit 0; `S/probe.py before S`, cwd S/before, exit 0. Exact source preserved because scratch is deleted:

```python
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from joulewise import bytes_analysis as ba
from scripts.bytes_manifest import registered_config_key
mode=sys.argv[1]
s=Path(sys.argv[2])
frozen=json.loads(Path('configs/bytes/bytes_manifest.json').read_bytes())
if mode=='after':
    reviewer=json.loads(Path('/private/tmp/claude-501/-Users-edr-code-JouleWise/2dc9c377-4ec4-4750-b44d-4d8cd5ae9354/scratchpad/byint/manifest_regen.json').read_bytes())
    review={m['model_name']:m['config_key'] for m in reviewer['models']}
    assert len(frozen['models'])==10
    checks=[]
    for m in frozen['models']:
        key=m['config_key']
        assert key==review[m['model_name']]==registered_config_key(m['model_name'])
        checks.append({'model':m['model_name'],'config_key':key,'sha256':hashlib.sha256(key.encode()).hexdigest()})
    (s/'keys.json').write_text(json.dumps(checks,indent=2))
    m=frozen['models'][0]
    info={'row_count':3,'config_key_sha256':{hashlib.sha256(m['config_key'].encode()).hexdigest():2}}
    counts=ba._withheld_counts(info,m)
    assert counts=={'withheld_row_count':3,'withheld_config_row_count':2}
    ba.validate_manifest(frozen)
    invalid=copy.deepcopy(frozen)
    del invalid['models'][0]['config_key']
    try:ba.validate_manifest(invalid)
    except ba.AnalysisError as exc: error=str(exc)
    else:raise AssertionError('missing config_key accepted')
    print(json.dumps({'models_checked':len(checks),'counts':counts,'validation_error':error},sort_keys=True))
else:
    assert all('config_key' not in m for m in frozen['models'])
    # Baseline raw frozen rows lack the analysis-only metadata as well as config_key.
    # Supply the registered metadata only; preserve every baseline row field and omit config_key.
    after=json.loads((s/'after/configs/bytes/bytes_manifest.json').read_bytes())
    metadata={m['model_name']:{k:m[k] for k in ('model','role','moe','tier','cell_ids')} for m in after['models']}
    manifest=copy.deepcopy(frozen)
    for m in manifest['models']:m.update(metadata[m['model_name']])
    assert ba.validate_manifest(manifest) is manifest
    model=manifest['models'][0]
    key=registered_config_key(model['model_name'])
    info={'row_count':3,'config_key_sha256':{hashlib.sha256(key.encode()).hexdigest():2}}
    counts=ba._withheld_counts(info,model)
    assert counts=={}
    print(json.dumps({'raw_models_without_key':len(frozen['models']),'analysis_metadata_added':list(metadata[model['model_name']]),'validation_accepted':True,'counts':counts,'registered_config_key':key},sort_keys=True))
```

After output: `{"counts":{"withheld_config_row_count":2,"withheld_row_count":3},"models_checked":10,"validation_error":"manifest model requires non-empty string config_key"}`. Integer fixture counts distinguish two matching rows from three total rows; these are not comparison bars.

Before output: all ten frozen rows lack config_key; validation accepts the analysis-shaped copy; _withheld_counts returns `{}` despite withheld rows indexed by sha256(registered_config_key(model_name)). Raw baseline rows also lack model/role/moe/tier/cell_ids and are not themselves valid analysis inputs. Probe supplies only those registered metadata fields from fixed rows, preserves every existing baseline field and inserts no config_key. This demonstrates the silent unavailable path without claiming raw baseline JSON validates.

Refusal census command in after: common prefix plus `-m tests.hazards.refusal_census`, exit 0:

```json
{"unlisted": [], "stale": [], "miscounted": [], "guard_changed": [], "scope_gaps": []}
```

Fixed export allowlist has no joulewise/bytes_analysis.py in scan.modules and no site listing the config_key error. AnalysisError is analysis-input validation following validate_manifest's invalid-model-role pattern, not a collection refusal. No registry update. Refusal module: 23 tests run, 22 passed and one skip because historical design branch is unavailable in Git archive. No other skips or environmental failures.

### DECISIONS I MADE

- Applied report-only route and BRANCH DISCIPLINE: verified BY-REV's fix instead of generating a competing pass-1 config. No estimator, acceptance bar or printed number changed.
- Compared exact bytes and key/digest strings; no new tolerance. Existing agreement bars unchanged.
- Supplied only required analysis metadata for baseline validation, never config_key. Census digest comes from a frozen model's actual registered key.
- Rejected finding 3 as a repository edit; director owns return-message ledger correction.
- No implementation clause-map delta: only report changed. Final merge/CI/hardware verification remain lead-owned.

### OPEN ISSUES

- No unresolved in-scope work. Director reviews/commits report; BY-MERGE carries review-fixes 478873066 into pass 1.
- CI-timings owner receives finding 2; BY-SLOTS/BY-REG receives finding 4; director records finding 3 correction.
- Existing BY-TWIN hand-forward remains governed by .codex-report/BY-INT.md: coefficient_C, offset_intervals, meter_offset_bound_j, d_beta_d_delta_per_ms, withheld_row_count and fields_not_rebuilt. This round does not declare them complete.
- No new PR/CI action under local report-only route. Supplied #560 result is historical reviewer evidence, not this seat's observation.
- Two report-writer preparation attempts had Python quoting SyntaxErrors before execution, with no file writes. Replaced by successful direct writer; test outcomes unaffected.

### NEEDS_RULING

none.
