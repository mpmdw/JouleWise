## PROGRESS

- Done (slice 1): intake at clean baseline `bda481d5af510b29dde4976f172a20170a42c955`; no stop card. Analysis/twin roster implementation; two new regressions fail before/pass after; findings 2–8 bounded edits/dispositions; twin 57 tests, BoundaryAndStagingTests 10, manifest 16, gates 7, release_subset 4 and refusal_allowlist 23 (one skip) pass; census empty; all three generators check clean. Import graph: 5 pass, one NULL-vs-GO failure reproduced on baseline.
- Next: finish finding 1 in `tests/test_bytes_roster_drop.py`: production sub-pack CLI chain, exact h critical arithmetic, twin comparison through existing harness, ten-model identity control after ruling, Q1 missing-file chain. Replay every added test on `/tmp/byint-fix1-slice1/before` (baseline production untouched), copying only new tests/changed fixtures. Run remaining RUN modules/classes separately with fresh TMPDIRs. Clean BoundaryAndStagingTests rerun completed 10/10, exit 0; scratch logs/command records are under `/tmp/byint-fix1-slice1`. No processes remain running from slice 1.
- Open: raw frozen predictions include the analysis source SHA-256, so changing that source necessarily changes those bytes. Need a director ruling on the requested byte-identity control before declaring it passed. No commits/pushes are attempted; the local director owns them.

## SUMMARY

Slice 1 implemented the analysis/twin alternative-roster path and the bounded findings 2–8 edits.
Two new roster regressions fail at the archived baseline and pass with the changes.
Twin 57 tests and clean BoundaryAndStagingTests 10 tests pass; additional focused modules pass as listed.
Refusal census is empty; generated trees/catalog/Mac kit remain unchanged.
One import-graph fixture failure reproduces on the untouched baseline.
The required nine-model CLI/agreement chains, ten-model identity control and remaining analysis classes await the next slice.
Literal frozen-prediction byte identity conflicts with the mandatory source-provenance digest; ruling requested.
Branch is `lane/2026-10-22-bytes-pass1`, HEAD remains `bda481d5af510b29dde4976f172a20170a42c955`; changes are uncommitted for the director.

## FIX LOG

| Finding | Severity | Disposition | Commit / evidence |
| --- | --- | --- | --- |
| 1 | major | In progress: analysis/twin accept registered alternative; full chain tests pending | Working tree; two regressions demonstrate before failure/after pass |
| 2 | minor | fixed | Working tree; dated correction only in BY-INT.md, parity branch grep confirms Q1 coverage |
| 3 | minor | catalog row fixed; other four slots deferred to BY-SLOTS | Working tree; catalog SHA equals Appendix A |
| 4 | nit | fixed; agreement counts pending | Working tree; twin 57/57 unchanged; pivot rule and FPMIN comment |
| 5 | nit | fixed | Working tree; exactly one docstring line changed |
| 6 | nit | fixed | Working tree; authority, Q2 and roster paragraphs outside Inputs and release |
| 7 | information | rejected as code change: no_change_needed; text deferred to BY-SLOTS | Information only; reviewer says flag, not refuse; D-161 operator-only protection is procedural |
| 8 | nit | fixed | Working tree; removed blank line after reference_drift assignment |

## CHANGES

- `joulewise/bytes_analysis.py`: registered names/constants near H1/H2 constants; `h1_checks` helper immediately before `validate_manifest`; replace only the roster cardinality predicate in `validate_manifest`, preserving role/fit/MoE/tier checks; `_phase_cell` keyword family and quantile; pass that family from `reduce_models` including without-assisted diagnostic; frozen H1/H2 roster counts; `evaluate` cardinality from frozen roster family (three fit plus H1/three). Empty manifest stubs retain full-roster counts for existing arithmetic-only callers; CLI still validates all manifests.
- `scripts/bytes_analyze.py`: one hunk, analysis_record H1_checks reads frozen H1_checks.
- `scripts/bytes_twin.py` (BY-MERGE carry map): `_betacf` FPMIN comment; `_solve` scale-relative pivot threshold; `read_manifest` duplicate canonical name check; start of `analyse` validates full/drop roster and derives held_out/h1_family; alpha_h1 uses family; h2_points loops present roster; multiplicity prints family; two held-out loops and manifest predictions loop use local held_out; output roster contains present models. No header or CLI refactor.
- `tests/fixtures/bytes/campaign.py`: optional drop_8b_8bit filters design models before config keys, removes extra blank, filters absent name from sub-pack schedule. The remaining model in the shared sub-pack remains scheduled, with single-model midpoint treatment.
- `tests/test_bytes_roster_drop.py`: new RegisteredRosterTests, currently two tests; full/drop acceptance plus wrong nine/eleven refusals; frozen H1/H2 counts for both rosters. Each fails baseline. More required chain coverage pending.
- `tests/test_bytes_agreement.py`: exactly one docstring line, replacing erroneous 4,500 factor with about 4.5e9 and derivation; next line unchanged.
- `docs/contracts/bytes_tables.md`: authority hunk names Addendum 9 and Q2; two paragraphs immediately below Arithmetic and output schema describe dropped roster and Q2 fields. Inputs and release untouched.
- `docs/registrations/bytes_pack_v1.md`: only §18 catalog-SHA row marked FILLED, pointing to Appendix A.
- `.codex-report/BY-INT.md`: only dated finding-2 correction following original agreement paragraph. Read-only parity branch grep finds canonical missing flag, both counts, missing cell/point/H1 status and MoE answer regression.
- `.codex-report/BY-INT-fix1.md`: progress and evidence for this round.

## TESTS RUN

All repository-code commands used `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B`. Temporary directories were created with `tempfile.TemporaryDirectory(prefix="jwtmp-byintf1.", dir="/tmp")` and cleaned after each run. No whole suite ran.

Baseline export: `mkdir -p /tmp/byint-fix1-slice1/before`; `git -C /Users/edr/code/JouleWise-by-int archive bda481d5a | tar -x -C /tmp/byint-fix1-slice1/before`. Copied new test module and changed campaign fixture only. Python cwd was that before directory for the baseline run.

Before and after command (each fresh TMPDIR): `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_roster_drop`. Baseline: 2 tests, exit 1, one error (ten-model refusal), one failure (21 != 18). After: 2 tests, exit 0, no skips, 0.002 s.

`/opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/run_tests.py twin tests.test_bytes_twin` runs `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_twin`: 57 tests, exit 0, no skips, 20.600 s. Evidence: twin.log/twin.json in that scratch directory.

`/opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/run_tests.py focused tests.test_bytes_roster_drop tests.test_bytes_analysis.BoundaryAndStagingTests`: 12 tests in 46.375 s, exit 1: only changed-manifest stub errored; the other 11 passed. That empty-stub compatibility error was fixed immediately. A focused replay via `run_tests.py freeze-rerun tests.test_bytes_roster_drop tests.test_bytes_analysis.BoundaryAndStagingTests.test_changed_manifest_refuses_commitment tests.test_bytes_analysis.BoundaryAndStagingTests.test_predictions_only_fit_and_hash_is_exact_file_bytes` passed 4 tests, exit 0, 0.035 s. A separate full BoundaryAndStagingTests rerun, `run_tests.py boundary-final tests.test_bytes_analysis.BoundaryAndStagingTests`, passed 10 tests, exit 0, no skips, 44.004 s. These initial combined invocations shared a TMPDIR across their two named modules; remaining module acceptance runs must be separate.

`/opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census`: exit 0, all five arrays empty. `/opt/homebrew/bin/python3.13 -B scripts/bytes_plan_trees.py --check`, `/opt/homebrew/bin/python3.13 -B scripts/build_b6_flag_catalog.py --check`, `/opt/homebrew/bin/python3.13 -B scripts/bytes_mac_kit.py --check`: all exit 0. These are check-only commands, not test modules. `git diff --check`: exit 0.

Catalog SHA-256: `4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f`, still equals Appendix A.

A first shell cleanup wrapper was rejected before execution for `rm -rf`; replaced with Python TemporaryDirectory cleanup. No tests ran in the rejected calls.


Additional separate-module runs used `/opt/homebrew/bin/python3.13 -B /tmp/byint-fix1-slice1/run_tests.py MODULE MODULE`, which invokes `/opt/homebrew/bin/python3.13 -B -m unittest -v MODULE` in the repository, each in its own fresh cleaned TMPDIR, with both required environment variables. Exact module arguments and results:

| MODULE | Count | Exit | Skips / elapsed |
| --- | ---: | ---: | --- |
| tests.test_bytes_manifest | 16 | 0 | none; 0.588 s |
| tests.test_bytes_gates | 7 | 0 | none; 1.193 s |
| tests.b6.test_release_subset | 4 | 0 | none; 0.132 s |
| tests.hazards.test_import_graph | 6 | 1 | 5 pass; synthetic arm fixture decision NULL rather than GO; 4.375 s |
| tests.hazards.test_refusal_allowlist | 23 | 0 | 1 skip: historical block-5 design branch absent from clone; 18.046 s |

Import-graph baseline replay: `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.hazards.test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module`, subprocess cwd `/tmp/byint-fix1-slice1/before`, required environment variables plus its own TemporaryDirectory TMPDIR. Exit 1, 1 test, 3.416 s, identical NULL-vs-GO failure at line 217. This failure predates all fixes; no import-graph/registry file was edited. No physical arm or measurement ran: the authorized test uses its synthetic hardware seams. No changes were made to chase this inherited/environmental fixture outcome.

## END-TO-END

Pending production-shaped nine-model chain, Q1 missing-file chain and ten-model before/after control. Do not claim finding 1 complete from the two unit regressions.

## CI

No network in this local seat. Director's supplied baseline observation: PR #535 at `bda481d5a` has 20/20 green jobs, except the expected gate-ledger failure. New-head CI is director-owned and unobserved here.

## DECISIONS I MADE

- Registration §2 and §10 identify the optional row by its exact `model` name, `Qwen3-8B-8bit`. The full roster and only that roster minus this row are accepted.
- Keep `H1_CHECKS = 21` as the full-roster compatibility constant for the existing repro; compute actual H1 family from manifest held-out membership, including missing rows.
- User's local route and exhaustive allowlist override general bookkeeping, commit/push and whole-suite instructions.

## OPEN ISSUES

- BY-SLOTS/BY-REG own dropped-roster plan-tree and registration generation. The shared sub-pack with Qwen3-32B-4bit must retain that model and its references while excluding every dropped-model run/config/key; no generator edits are authorized here.

- BY-SLOTS slot hand-forward: group key directory is `<pack_records_root>/bytes/blinding` (`joulewise/b6/blinding.py:102`, identity at 104, directory at 108). Withheld store is `<group records root>/withheld/<pack_id>/<session_id>.runs.csv` (`joulewise/b6/blinding.py:91`, path at 96; exporter calls at `joulewise/b6/export_runs.py:190`). Flag is `bytes.withheld_missing` (`scripts/bytes_analyze.py:42`; analysis census/reduction retains row counts). Stage option `--stage1-commit` is declared at `scripts/bytes_analyze.py:55` and format-checked at 65; subset release checks at `scripts/b6_release_subset.py:22`. It accepts 40 or 64 hexadecimal characters, without Git object existence validation. Registration slot text should explicitly call this procedural protection. Four slot texts deliberately remain unfilled.

## NEEDS_RULING

Ten-model frozen predictions contain `bytes_analysis_sha256 = sha256(bytes_analysis.py)`. A correct source change necessarily changes that field and the prediction-file SHA. Options: compare every other frozen field byte-for-byte after replacing only this provenance digest with the baseline value; or require literal bytes and block source changes. Recommendation: allow only that digest difference, keep raw hashes visible, and require the four numerical output files to remain byte-identical. Remaining independent work can proceed.
