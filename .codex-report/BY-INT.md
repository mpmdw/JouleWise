# BY-INT — BYTES pass-1 integration

## SUMMARY

One integration line contains B2, B4, B3, exact H/B5, manifest/KV, registration and current main `4d49364ca`.
All merge checkpoints were pushed, without force, only to `lane/2026-10-22-bytes-pass1`; draft PR #535 is open.
The sole manual conflict was `tests/fixtures/bytes/campaign.py`; NR1, M1, Q1/Q2 and blinding behavior are preserved.
The new Q2 CLI regression fails under the pre-judge CLI and passes on the integrated CLI in both cases.
All 39 plan-generator outputs reproduce byte for byte; the Mac kit check passes; catalog SHA and README are filled.
The 14 requested modules cover 258 tests: 256 pass, one catalog-reproduction test failed until the builder fix below, and one branch-presence test skips.
The main-refresh bridge module adds 3 passing tests; no whole suite ran locally.
The 12-session synthetic CLI chain and scratch open_packs checks pass; alpha/beta/gamma and loop hashes are unchanged; refusal census arrays are empty.
Catalog builder: the lead granted `scripts/build_b6_flag_catalog.py`; the three B4 entries were added (243e398e3), `--check` and the catalog test pass, catalog bytes unchanged. CI shard 7's git-fixture guard defect (two B4 `git init` sites) was fixed in 960c7c163.
Legacy agreement passes but omits NR1/Q2 fields pending BY-TWIN. CI and the lead's local verification are under CI and LEAD VERIFICATION.

## MERGES

1. B4 `0b6023dcc`: `e564d4db75137f307ee726f7d8f92dd7916e6bb9`. Conflict: `tests/fixtures/bytes/campaign.py`, two hunks. Combined B2's fixture defaults and synthetic-parameter manifest (unequal durations, signed clock latency, 50 ms sample phase, independent random edge phase, 10 ms minimum arrival latency, reference drift) with B4's `subpack_sessions` / `uncollected_sessions` and configuration keys. Governing: Addendum 7 item 12 and Addendum 8 item 4 (`docs/design/bytes_pack_design.md` at `298a292a7`); `docs/process_traces/2026-10-21-magistrate-a017b694/B2-NR1-RULING.md` items 1, 3, 5; `docs/process_traces/2026-10-21-magistrate-283e9802/B2-NR1-COLD-DISPOSITION.md` M1; `docs/process_traces/2026-10-20-magistrate-af419b16/B6-RULING.md` Q1 and Q2; `docs/process_traces/2026-10-20-magistrate-4b350f47/RECORD.md` blinding ruling items 1–3. Other paths merged automatically; generated drafts came from the B4 generator output.
2. B3 `0c04bb181`: resulting head `990763f02e021e28bbae6d7b5d78fd71d4374e0d`; no conflicts.
3. H `c10b6895f` exactly (including B5 `20e6984c9`): resulting head `33fda48b643b82b6d2aab0e573a36c1af18d4897`; no conflicts. Later H branch commits were excluded.
4. Manifest/KV `99c9099d8`: resulting head `4f6237d46d7ed8bd87e1f50e2a4b4d961c18492e`; no conflicts.
5. Registration `91b20d7c2`: resulting head `e7ffa7c8c1e55b18e6dd9bb48035b416979e75ca`; no conflicts. Twelve registrations auto-merged B4 flag effects with registration-lane estimators and notes.
6. Regeneration: resulting checkpoint head `b2da126598da59dbaea3ef8a4318e5e88d556d69`. `scripts/bytes_plan_trees.py` produced no tracked differences. `--check` and `scripts/bytes_mac_kit.py --check` pass. `scripts/build_b6_flag_catalog.py --check` exits 1: inherited B4 catalog entries are absent from its builder. Exact-file scope expansion requested; builder untouched pending reply.
7. `origin/main` at `ef520743cec50833a8ee6af37388610bef22798e`: resulting head `5f89a9e0051b64f74454a193f9f3e9f20db7d65a`; no conflicts. Auto-merges in `configs/gates/hazard_refusals.json`, `tests/test_b5_plan.py`, and `tests/test_night_agent_install.py` required no manual changes. Final remote observation found main advanced to `4d49364ca720c6ccf505f5c277ddfe27f26a9e90` (PR #530, bridge/tooling only). Refreshed step 7 by merging that head cleanly, resulting in `2f5bd560a9d546c5e07bfcbc6b714035c8770707`, then pushed. No conflict files; no BYTES arithmetic, fixture, registration or generator changed. `tests.test_codex_app_bridge`: 3 tests, exit 0. Lead refresh (director, 10-22): main advanced again to `bfab7c950` (PR #538, Codex MCP server and census tests); merged cleanly as `d401c6213`. The two sides change no common file; no BYTES path changed.

## GENERATED

Commands (all with `JW_B5_SYNTHETIC_ONLY=1` and `/opt/homebrew/bin/python3.13 -B`):

- `/workspace/JouleWise/scripts/bytes_plan_trees.py`: exit 0; no tracked differences.
- `/workspace/JouleWise/scripts/bytes_plan_trees.py --check`: exit 0.
- `/workspace/JouleWise/scripts/bytes_plan_trees.py --output-root /tmp/by-int/regenerated`: exit 0; all 39 emitted files equal both the generator bytes and checkout bytes (12 plan trees, 12 registrations, 12 collection plans, smoke keep, loop, pass order).
- `/workspace/JouleWise/scripts/bytes_mac_kit.py --check`: exit 0.
- `/workspace/JouleWise/scripts/build_b6_flag_catalog.py --check`: exit 1, inherited three-code builder omission. Scope request pending; repository builder unchanged.

Per-file generator hashes: `/tmp/by-int/generated.json`, SHA-256 `38f9e6a9c7f4963ce123b5661cbd8e127949a6e30a9931a465b8472016bd9923`.

## B4 OPEN ITEMS

- Added `Q2CommitmentCLIChainTests.test_changed_module_evaluates_original_commitment_and_labels_rebuild` to `tests/test_bytes_analysis.py`. It runs CLI processes for comment-only provenance and a deliberately defective central fit line, then checks C1 evaluated as committed, C2 separately, immutable prediction bytes, module digests, exact field lists, and both disclose-only flags. No new comparison bar.
- Before: test replay with `scripts/bytes_analyze.py` from `c2dad351e` and the integrated arithmetic/fixture: 1 test, 2 failing subtests, exit 1 (`frozen line/fit-point mismatch`). After: integrated CLI, 1 test, both cases pass, exit 0, 26.999 s. Logs `/tmp/by-int/q2-before.log` and `/tmp/by-int/q2-after.log`.
- Catalog SHA filled in Appendix A: `4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f`.
- README: both passes now say 1/1, with optional pass 2 governed by the analysis (Addendum 6).
- Inherited builder mismatch remains pending the exact-file scope grant for `scripts/build_b6_flag_catalog.py`. An in-memory addition of precisely the existing three entries makes its output byte-identical to the catalog; no catalog value needs changing.

## TESTS RUN

All commands ran from `/workspace/JouleWise`, with a distinct fresh TMPDIR for each module, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, and the required `/opt/homebrew/bin/python3.13`. The module runner stores full output and exit status in `/tmp/by-int/<module>.log` and `.json`. No whole-suite run was made locally. The changed current-main bridge module was also run after its merge.

| Module | Tests | Exit | Result |
| --- | ---: | ---: | --- |
| `tests.b6.test_blinding` | Ran 8 tests in 0.078s | 0 | OK |
| `tests.b6.test_bytes_packs` | Ran 9 tests in 2.534s | 0 | OK |
| `tests.b6.test_catalog` | Ran 4 tests in 0.793s | 1 | FAILED (failures=1) |
| `tests.b6.test_export_runs` | Ran 11 tests in 0.434s | 0 | OK |
| `tests.b6.test_release_subset` | Ran 4 tests in 0.066s | 0 | OK |
| `tests.hazards.test_import_graph` | Ran 6 tests in 13.475s | 0 | OK |
| `tests.hazards.test_refusal_allowlist` | Ran 23 tests in 31.177s | 0 | Audit-fix batch 1 (item 7): the draft sealed catalog on the design branch makes ... skipped 'the block-5 design branch is not in this clone'; OK (skipped=1) |
| `tests.test_bytes_agreement` | Ran 8 tests in 222.203s | 0 | OK |
| `tests.test_bytes_analysis` initial process | 9 completed before 570 s process budget | 124 | Nine pass, including full p03; next test interrupted |
| `tests.test_bytes_analysis` managed replay | Ran 60 tests in 1427.805s | 0 | OK; 69/69 module tests passed across both processes |
| `tests.test_bytes_gates` | Ran 7 tests in 1.427s | 0 | OK |
| `tests.test_bytes_h_session` | Ran 32 tests in 405.728s | 0 | OK |
| `tests.test_bytes_mac_kit` | Ran 4 tests in 0.462s | 0 | OK |
| `tests.test_bytes_manifest` | Ran 16 tests in 0.739s | 0 | OK |
| `tests.test_bytes_twin` | Ran 57 tests in 40.238s | 0 | OK |
| `tests.test_codex_app_bridge` | Ran 3 tests in 0.958s | 0 | OK; main-refresh delta |
| `tests.b6.test_catalog` scope-grant local rerun | Ran 4 tests in 0.270s | 0 | OK; `test_reproduces_and_loads` passes after the builder repair |

Scope-grant local rerun: `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.b6.test_catalog` ran from `/Users/edr/code/jw-wt/by-int-verify`, with `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, and its own fresh TMPDIR under that worktree's `.tmp-byint/`. The complete scope-grant checks and exit codes are recorded under OPEN ISSUES.

Exact module commands:

```bash
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_b6_test_blinding.rdoqo0sd /opt/homebrew/bin/python3.13 -B -m unittest -v tests.b6.test_blinding
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_b6_test_bytes_packs.opn7w61e /opt/homebrew/bin/python3.13 -B -m unittest -v tests.b6.test_bytes_packs
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_b6_test_catalog.qbqqap2o /opt/homebrew/bin/python3.13 -B -m unittest -v tests.b6.test_catalog
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_b6_test_export_runs.q6frrb4v /opt/homebrew/bin/python3.13 -B -m unittest -v tests.b6.test_export_runs
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_b6_test_release_subset.zl7o_6yf /opt/homebrew/bin/python3.13 -B -m unittest -v tests.b6.test_release_subset
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_hazards_test_import_graph.vtdwjd9c /opt/homebrew/bin/python3.13 -B -m unittest -v tests.hazards.test_import_graph
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_hazards_test_refusal_allowlist.ij24oi7p /opt/homebrew/bin/python3.13 -B -m unittest -v tests.hazards.test_refusal_allowlist
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_bytes_agreement.o2g639ez /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_agreement
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_bytes_analysis.1xdk5401 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_analysis
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_bytes_gates.suzfhce2 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_gates
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_bytes_h_session.l8jky1ac /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_h_session
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_bytes_mac_kit.bzamupj3 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_mac_kit
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_bytes_manifest.hv9f3vmc /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_manifest
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_bytes_twin.8d7614qs /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_twin
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_codex_app_bridge.xxav18a0 /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_codex_app_bridge
```

Analysis completion: the first process reached its explicit 570 s budget after nine successful tests, including the full 36-row, 400-draw-per-world p03 diagnostic. HC3 plain-95% coverage ranges: bytes 0.9700–0.9850; time 0.9425–0.9725; resident 0.9975–1.0000 (all above the existing 0.93 floor). `analysis-resume-plan.json` records all 69 test ids, the nine completed ids, and the 60 selected for resume. A first detached nohup process disappeared without a result footer; it is not counted as evidence. The managed asynchronous replay runs only the unfinished tests under a new TMPDIR. Managed replay completed 60 remaining tests in 1427.805 s, exit 0, failures 0, errors 0, skips 0. Together with the nine completed tests, all 69 tests in the module passed. The interrupted test was rerun in full; no result is inferred from an unfinished test.

Exact resume command:

```bash
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/tests_test_bytes_analysis_resume.MA1b PYTHONPATH=/workspace/JouleWise /opt/homebrew/bin/python3.13 -B /tmp/by-int/resume_analysis.py
```


Analysis evidence: `/tmp/by-int/tests.test_bytes_analysis.resume.log`, SHA-256 `8f35c1851677ccab292267c46734b205e028c870e88dfb2300ac7cd4939ea60b`; `/tmp/by-int/analysis-resume-plan.json`, SHA-256 `3de6516cf658507b4ef54802608c0e0bb5452c8cc3a6c24a9595cb094becaa70`. Full transient logs remain in scratch because WRITE_SCOPE permits only this report; their results, commands and hashes are promoted here.

Standalone Q2 commands:

```bash
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/q2-after.sYio /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_analysis.Q2CommitmentCLIChainTests
```

Result: 1 test, 2 cases, exit 0, 26.999 s. Before replay: `git -C /workspace/JouleWise show c2dad351e:scripts/bytes_analyze.py > /tmp/by-int/pre-q2/scripts/bytes_analyze.py`, with a symlink to the integrated package at `/tmp/by-int/pre-q2/joulewise`, then:

```bash
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp/q2-before.zxTq /opt/homebrew/bin/python3.13 -B - <<'BEFORE'
import unittest
from pathlib import Path
from tests import test_bytes_analysis as test
test.ROOT = Path('/tmp/by-int/pre-q2')
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(test.Q2CommitmentCLIChainTests))
raise SystemExit(not result.wasSuccessful())
BEFORE
```

Result: 1 test, both cases fail, exit 1, 37.290 s, each at the pre-judge `frozen line/fit-point mismatch` guard. Before-log SHA-256 `b21a8cd2100819dbef86949c020196a9fd897d9a8ee94173044cb3ac256b2ae6`; after-log SHA-256 `26dd9bf646fff4c9ee64c911bd23bf8f2fdff55fb4a3e590e21f5281573447bc`. The cold judge's harness was read from JouleWise-data `claude/b6-q2-judge:reports/b6-q2-judge/harness.py` through the read-only GitHub connector; the data checkout was not changed.

Catalog failure: `tests.b6.test_catalog.CatalogTests.test_reproduces_and_loads` compares builder bytes with the catalog and finds precisely B4's three disclose-only entries absent from the builder. It is an inherited repository defect, not an environmental failure. The requested exact-file scope expansion is pending.

Skips/environment: `tests.hazards.test_refusal_allowlist` has one skip because the block-5 design branch is not a local branch in this clone. No failures naming `/private/tmp`, launchd, launchctl, powermetrics, a macOS process-group check, or fixture Git commit exit 128 were observed in the completed modules. Seat setup lacked Unix ownership for `/opt/homebrew`; the requested symlink was made via the managed Docker daemon and the required interpreter works.

Agreement: 8 tests pass. Per campaign (compared / under bar / above bar): bytes 9966 / 4434 / 0; defects 10026 / 4395 / 0; minimum 10091 / 4501 / 0; resident 9966 / 4268 / 0; time 9966 / 4315 / 0. Unlike the brief's anticipated NR1 failures, this comparer does not inspect NR1 fields at all. Waiting for BY-TWIN by name: `meter_offset_bound_j`, `meter_offset_bound_w`, `meter_offset_sensitivity_w`, `coefficient_C`, `offset_intervals`, `offset_ols_intervals`, `d_beta_d_delta_per_ms`, `sensitivity_units`, `coefficient_decisions`, `offset_decisions`, their primary-row `coefficient_decision` / `offset_decision`, `resident_adds_nothing_offset`, `interval_scope`, `offset_scope`, `offset_disclosure`, `systematics_flag`, `sensitivity_flag`. The Q2 record's flags, digests and `fields_not_rebuilt` also await twin comparison under B6 Q2. This head does not claim NR1 or Q2 twin agreement.

## END-TO-END

The analysis module also completed 20 CLI campaigns in each of bytes, time and resident worlds (60 total) and the three-world subset-release/clock-removal chain, with no failing assertions.

- Retained production-shaped synthetic CLI chain: `/tmp/by-int/e2e.py`; 12 R6 sub-pack sessions, 1,000 science runs (10 models × 2 passes × 50), 156 references (13 × 12), 456 clock-free visible rows and 700 withheld rows. CLI exits: blinded 0; unreleased fit 1; fit 0; blinded post-commit 0; held-out with fit-only keys 1; released held-out 0. `h1.json`: 360 rows; `h2.json`: 12 groups; `unavailable.json`: empty. Commitment unchanged, SHA-256 `f6cf713c6683ba083161510edc6532dfe83182496dd808db69e77ca499b51fd6`. This supplemental fixture passes the integration SHA as the synthetic post-commit locator; the repository subset-release tests exercise an actual separately committed prediction directory. The supplemental summary initially used the wrong flat export locator, then was read back from the retained per-subpack directories; all CLI expectations had already passed. Summary `/tmp/by-int/e2e/summary.json`, SHA-256 `6fd36ff91d7597c9e5eaf396ef28e97f25bc79a721e07dd1714e876cb08d772f`.
- `open_packs`: scratch clone `/tmp/by-int/open-packs` at `5f89a9e0051b64f74454a193f9f3e9f20db7d65a`; real subprocess Git runner, no live state. Opened exactly alpha, beta and gamma; all twelve BYTES packs rejected only as draft. Every registration and loop hash unchanged. Before = after: alpha `3a999f88068ded30398575816fc45040541597ea283415ec307b11f0cc1dee0d`; beta `1cdb1026b4e4db28757980d26ff01faa95752862d5088fd2f9704d9a33ab76e3`; gamma `722ddf2bab8d4f143f8520f6e6d401af533ffa6560dfe60c8827dc2c3ca05563`; loop `5f120d7310b7240a81d5e12927e082112555950a2a8879ffadeabc7a6c7f370f`. Those four hashes were checked again against the current-main integration head and still match.
- `JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census`: exit 0; `unlisted`, `stale`, `miscounted`, `guard_changed`, `scope_gaps` all `[]`.
- `/opt/homebrew/bin/python3.13 -B /workspace/JouleWise/scripts/fixture_orphan_census.py --fail-on-orphans`: exit 0, output `[]`.

## CI

Draft PR #535: https://github.com/mpmdw/JouleWise/pull/535 (DRAFT, base main, head `lane/2026-10-22-bytes-pass1`).

Latest observation while local work was still running, 2026-10-22 03:05:06 UTC, code head `2f5bd560a9d546c5e07bfcbc6b714035c8770707`:

- CI run https://github.com/mpmdw/JouleWise/actions/runs/39713991637: build, changes, fences, quick and installed-wheel all green (5 jobs); one calibration-exclusive job and test shards 1, 2 and 9 running (4); the other 11 jobs queued. No final suite result yet.
- Gate ledger https://github.com/mpmdw/JouleWise/actions/runs/39713991678: failed as expected; independent execution review, whole-suite evidence, final-head CI and cold gates are not claimed by this seat.
- The report-only closeout push will trigger a fresh CI run; no green final-head claim is made. The known catalog-builder mismatch independently blocks the requested green acceptance. The seat does not wait on CI after its other work is complete.

Lead observation, 2026-10-22 05:31 UTC: CI run https://github.com/mpmdw/JouleWise/actions/runs/39721528108 on `960c7c163` completed with all 20 jobs green (12 test shards, calibration exclusives, build, quick, fences, installed-wheel, changes). Gate ledger failed as expected (merge-ledger keys not claimed). The main-refresh head `d401c6213` and this report update start a new run.

## LEAD VERIFICATION

The director re-ran the acceptance on the Mac at `d401c6213` (worktree `/Users/edr/code/jw-wt/by-int-verify`), each process with `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, its own fresh TMPDIR and `/opt/homebrew/bin/python3.13 -B`, test by test in parallel for the three long modules:

- `tests.test_bytes_analysis` 69/69 (the 60-campaign `CampaignWordRates` test run one world per process; every assertion in it is per world); `tests.test_bytes_h_session` 32/32; `tests.test_bytes_agreement` 8/8; `tests.test_bytes_twin` 57; `tests.test_bytes_manifest` 16; `tests.test_bytes_mac_kit` 4; `tests.test_bytes_gates` 7; `tests.b6.test_bytes_packs` 9; `tests.b6.test_blinding` 8; `tests.b6.test_export_runs` 11; `tests.b6.test_release_subset` 4; `tests.b6.test_catalog` 4; `tests.hazards.test_import_graph` 6; `tests.hazards.test_refusal_allowlist` 23 (no skip on the Mac); `tests.test_git_fixture_maintenance` 5; main-delta `tests.test_codex_mcp_server` 34 and `tests.test_arm_census` 20. All exit 0.
- `tests.hazards.refusal_census`: all five arrays empty.
- `scripts/bytes_plan_trees.py --check`, `scripts/build_b6_flag_catalog.py --check`, `scripts/bytes_mac_kit.py --check`: exit 0. `bytes_plan_trees.py --output-root <scratch>` emits 39 files, all byte-identical to the checkout.
- Q2 regression replayed against `scripts/bytes_analyze.py` from `c2dad351e`: both cases fail at `frozen line/fit-point mismatch` (exit 1); on the integrated CLI both pass.
- Catalog SHA-256 `4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f` equals the file and Appendix A.
- `tests.test_agent_identity.AncestorCensusLiveTests` fails on the Mac at this head and identically on main `bfab7c950`: with more than 20 listed processes (concurrent agent sessions), the census stderr truncates at 20 entries and the test's own pid falls in the elided part. Environmental for this lane; a main test defect to note, not a BYTES one.

## DECISIONS I MADE

- Combined orthogonal fixture controls; kept B2's ruled stress settings instead of B4's older equal-duration defaults.
- Preserve C_j as pass-averaged joules divided by mean decode time (M1); Q1 missing-file pass flags and survivor fallback; Q2 fixed-module evaluation of committed content with disclose-only provenance flags.
- Q2 regression uses only the existing interval's upper endpoint for its defective-line mutation, with no new stress magnitude or comparison tolerance. Exact comparisons check committed bytes, hashes, field lists and identical arithmetic on identical committed inputs.
- Kept all existing numerical bars, including B4's 1e-9 relative round-trip bar from `docs/process_traces/2026-10-20-magistrate-4ec5d597/RECORD.md` (above 1e6 × float noise and below 1% of the smallest printed relative half-width), and Addendum 8's field-specific agreement bars.
- Added no registry sites or refusal predicates. The merged refusal allowlist already covers its paths and the census is empty.
- The builder repair is a scope question, not a scientific ruling: adding the current entries leaves every byte of the catalog unchanged. `NEEDS_RULING` stays none.
- User write scope overrides repository end-of-work bookkeeping and whole-suite instructions. No unrelated files will be edited and no full suite will run locally.

## OPEN ISSUES

- CI run `39715668140`, shard 7, git-fixture guard defect FOUND AND FIXED: `tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper` reported direct initialization at original `tests/test_bytes_analysis.py` lines 1791 and 1940, inherited from B4 (`lane/2026-10-20-b6-blinding-group`). Per `docs/process_traces/2026-08-26-t26-ci-reliability/README.md`, imported `tests.git_fixture.init_git_fixture` and replaced only those calls with `init_git_fixture(root / "stage1", "-q")` in `SubsetReleaseChainTests` and `init_git_fixture(root / "fit", "-q")` in `Q1MissingFilesCLIChainTests`, disabling detached auto-maintenance before fixture commits. Add, commit, rev-parse, assertions and every existing number are unchanged.

  All commands below ran from `/Users/edr/code/jw-wt/by-int-verify` with `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1` prepended. Each test command additionally had `TMPDIR="$(/usr/bin/mktemp -d /private/tmp/LABEL.XXXXXX)"` prepended, with its distinct LABEL below; every temporary directory was fresh and outside the worktree. The import check ran first. No whole suite ran and no final-CI result is claimed.

  | LABEL | Command | Exit | Result |
  | --- | --- | ---: | --- |
  | import (no TMPDIR override) | `/opt/homebrew/bin/python3.13 -B -c "import joulewise; print(joulewise.__file__)"` | 0 | `/Users/edr/code/jw-wt/by-int-verify/joulewise/__init__.py` |
  | `by-int-git-guard` | `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_git_fixture_maintenance` | 0 | 5 tests, OK |
  | `by-int-git-subset` | `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_analysis.SubsetReleaseChainTests` | 0 | 2 tests, OK |
  | `by-int-git-q1` | `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_analysis.Q1MissingFilesCLIChainTests` | 0 | 3 tests, OK |
  | `by-int-git-q2` | `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_bytes_analysis.Q2CommitmentCLIChainTests` | 0 | 1 test, both cases, OK |
- Scope blocker RESOLVED by the lead's exact-file grant for `scripts/build_b6_flag_catalog.py`. Added `bytes.withheld_missing`, `bytes.module_changed_after_commitment`, and `bytes.commitment_not_rebuilt` to `NEW_CODES`, copying the catalog's family, klass, effect, blinding and note exactly. B6-RULING.md Q1/Q2 determine that all three stay `DISCLOSE`; no refusal, arithmetic, tolerance or threshold changed. The catalog file is unchanged, SHA-256 `4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f`, matching registration Appendix A. This resolves the builder check and catalog-test blocker; it makes no final-CI claim.

  All commands below ran from `/Users/edr/code/jw-wt/by-int-verify`. Each had `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$(/usr/bin/mktemp -d /Users/edr/code/jw-wt/by-int-verify/.tmp-byint/LABEL.XXXXXX)"` prepended, using its distinct LABEL shown below and a fresh directory. `.tmp-byint/` remains uncommitted. No whole suite ran.

  | LABEL | Command | Exit | Result |
  | --- | --- | ---: | --- |
  | `import` | `/opt/homebrew/bin/python3.13 -B -c "import joulewise; print(joulewise.__file__)"` | 0 | `/Users/edr/code/jw-wt/by-int-verify/joulewise/__init__.py` |
  | `builder` | `/opt/homebrew/bin/python3.13 -B /Users/edr/code/jw-wt/by-int-verify/scripts/build_b6_flag_catalog.py --check` | 0 | Exact generated bytes equal the catalog |
  | `sha` | `/usr/bin/shasum -a 256 /Users/edr/code/jw-wt/by-int-verify/configs/b6/flag_catalog_b6.json` | 0 | Unchanged SHA-256 above |
  | `catalog_diff` | `git -C /Users/edr/code/jw-wt/by-int-verify diff --exit-code -- /Users/edr/code/jw-wt/by-int-verify/configs/b6/flag_catalog_b6.json` | 0 | No catalog diff |
  | `catalog` | `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.b6.test_catalog` | 0 | 4 tests, OK, 0.270s |
  | `bytes_packs` | `/opt/homebrew/bin/python3.13 -B -m unittest -v tests.b6.test_bytes_packs` | 0 | 9 tests, OK, 2.014s |
  | `refusal` | `/opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census` | 0 | `unlisted`, `stale`, `miscounted`, `guard_changed`, `scope_gaps` all `[]` |
- BY-TWIN must implement and compare the NR1 fields and Q2 record fields listed under TESTS RUN. The existing comparer passes because those fields are outside its comparison set.
- Final CI is pending as recorded below; the catalog-reproduction defect is known independently. No waiting for CI extends this seat past its other work.

## NEEDS_RULING

none
