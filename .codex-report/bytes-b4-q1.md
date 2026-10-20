gpt-6.1-sol

Activation af419b16, 2026-10-20. **Items 1–5 DONE, committed and published individually in order.** Scope expansion granted at 16:15 PDT.

Branch: `lane/2026-10-20-b6-blinding-group`. Verified base: `fd5a3bc7bab12c0f6e657e2ea814e1372575231f`. Published five-item head: `79a3b2c486b3419bad4fe24488691c7c7586ace3`; the final verification commit carries the corrected pre-existing ingress assertion and this report. Its delivery SHA is in the final response. No other branch was pushed.

All five direct Git pushes failed with `could not read Username for https://github.com`. Each item was published through the connected GitHub API, using a checked expected parent and an identical tree; local checkout was synchronized after verifying tree equality.

## Per-item completion

| Item | Status and file:line | Published commit |
|---|---|---|
| 1. Census expected withheld files before reduction | DONE — `joulewise/bytes_analysis.py:510`, `:535`, `:541`, `:789`, `:1011`; public registered identity at `scripts/bytes_manifest.py:255`, `:293` and `tests/fixtures/bytes/campaign.py:44`; tests at `tests/test_bytes_manifest.py:220`, `tests/test_bytes_analysis.py:1355`. | `32ba71a79` |
| 2. Preserve blinded post-commit flags/placeholders | DONE — `joulewise/bytes_analysis.py:806`; `scripts/bytes_analyze.py:74`. Both stores missing now exits 0 and prints missing pass/model/H1/MoE records. | `486d24816` |
| 3. Union `_missing_labels` flags | DONE — `scripts/bytes_analyze.py:37`. Preserves existing point and pass disclosures on computed survivors and no-point models. | `c3c58e901` |
| 4. Explicit missing H1 and active-or-resident rows | DONE — `joulewise/bytes_analysis.py:1141`, `:1174`; regression `tests/test_bytes_analysis.py:1126`; contract `docs/contracts/bytes_tables.md:50`. No H1 word is invented. | `548981c89` |
| 5. Three real CLI-chain regressions with sub-pack sessions | DONE — fixture `tests/fixtures/bytes/campaign.py:17`, `:51`; `tests/test_bytes_analysis.py:1574`, `:1583`, `:1586`, `:1589`. | `79a3b2c48` |
| Pre-commit blinded fewer-than-ten check | DONE — `scripts/bytes_analyze.py:75`; all three chains exit 0 with exactly the three fit models and empty H1/MoE/H2. | item 5 |

Missing pass cells print `status="missing"`, `bytes.withheld_missing`, the sidecar's total `withheld_row_count`, and the model's `withheld_config_row_count`. This distinguishes a two-model session total of 100 from the affected model's 50 expected rows. The placeholders contain no energy and never restore absent data. `configs/b6/flag_catalog_b6.json:143` registers the flag as DISCLOSE / REPRESENTATION / RECORDS. No refusal-registry edit was necessary: the census is clean.

## End-to-end results after the fix

Target: Qwen3-30B-A3B-4bit in s2, with fit model Qwen3-8B-4bit. Each case uses a newly generated synthetic campaign, native reducer/export/subset-release/unblind processes and an actual Git commitment before held-out release. There are 12 collected sessions, or 11 when optional s2-p2 is genuinely never collected; 50 science runs/model/pass and 13 references/session. Pass 2 reverses sub-pack and model order, including the registered within-module midpoint for single-model sub-packs. Unequal pass durations (1, 2), signed clock latency (-8, +3) ms and a native 10 Hz meter remain enabled.

`M` = `bytes.withheld_missing`; `missing(50)` includes both sidecar counts, each 50 for s2. H2 is primary n/k; two-pass sensitivity n/k. The table records the focused CLI run (31.934 s). Rows are rails / gross primary / primary selection; missing statuses and point labels are checked across every basis, selection and available boundary.

| Case | Stage | Target pass rows | Point / flags | Target H1 | MoE | H2 n/k | Exit |
|---|---|---|---|---|---|---|---|
| All three | blinded pre-commit | — | — | — | — | — | 0 |
| All three | release fit: four explicit keys | — | — | — | — | — | 0 |
| All three | fit | — | — | — | — | — | 0 |
| All three | local stage-1 Git commit | — | — | — | — | — | 0 |
| One store missing: s2-p2 | blinded post-commit | p1 computed; p2 missing(50), M | computed / one_pass, M | mean+p1 neither, M | active; target miss M | 10/9; 9/9 | 0 |
| Both s2 stores missing | blinded post-commit | p1+p2 missing(50), M | missing / no_pass, M | explicit missing, no word, M | explicit missing, M | 9/9; 9/9 | 0 |
| Optional s2-p2 uncollected | blinded post-commit | p1 computed only | computed / one_pass, no M | mean+p1 neither | active | 10/9; 8/9 | 0 |
| All three | release heldout: eleven keys + stage-1 hash | — | — | — | — | — | 0 |
| One store missing | heldout | p1 computed; p2 missing(50), M | computed / one_pass, M | mean+p1 bytes, M | active; target miss M | 10/9; 9/9 | 0 |
| Both stores missing | heldout | p1+p2 missing(50), M | missing / no_pass, M | explicit missing, no word, M | explicit missing, M | 9/9; 9/9 | 0 |
| Optional s2-p2 uncollected | heldout | p1 computed only | computed / one_pass, no M | mean+p1 bytes | active | 10/9; 8/9 | 0 |
| One store missing | unblind s2-p2 | 63 public rows; M printed | — | — | — | — | 0 |
| Both stores missing | unblind s2-p2 | 63 public rows; M printed | — | — | — | — | 0 |
| Optional s2-p2 uncollected | unblind existing s2-p1 | 113 rows; no M | — | — | — | — | 0 |

DC-input H2 uses the same n/k as rails; rest uses the same n with k=11, including sensitivity. Optional sensitivity n=8 is expected because the uncollected s2-p2 session also contains fit 8B; losing only the withheld store preserves that fit pass and leaves sensitivity n=9. Blinded H1 words are diagnostic only. Prediction bytes are unchanged throughout each chain.

An additional boundary capture ran the same three CLI tests without source changes. At heldout, one missing store gives H1 `bytes` on rails and DC input; rest gives mean `unresolved`, descriptive p1 `bytes`. Optional gives mean+p1 `bytes` on all three boundaries. Both missing gives explicit missing H1 and MoE rows on all three boundaries. The surviving one/optional MoE answer is `active` on all three. Blinded configuration factors are freshly random: optional's diagnostic word was `bytes` in this repeat versus `neither` in the table; status, flags, n/k and every stage's exit remain as reported. No blinded word is a claim.

## Tests before and after

All complete checks use Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1` and a fresh TMPDIR for each module. Pytest is absent, so the command is `python3.13 -B -m unittest -v MODULE`. The final analysis-module run partitions all 64 test IDs into three disjoint isolated processes: coverage (1), campaigns (1), and remaining (62), each with its own fresh TMPDIR; there are no test omissions. All three passed: coverage 158.012 s, campaigns 296.221 s, remaining 239.053 s. The final manifest module passed all 16 tests in 0.229 s. The before run used a separate unchanged local clone at the verified base; an initial partial run was restarted there so lane edits could not affect its source.

| Module | Before: run / passed / skipped | After: run / passed / skipped | Failing names |
|---|---|---|---|
| `tests.test_bytes_analysis` | 56 / 56 / 0 (640.044 s) | 64 / 64 / 0 (final three shards) | none |
| `tests.test_bytes_manifest` | 15 / 15 / 0 | 16 / 16 / 0 | none |
| `tests.hazards.test_refusal_allowlist` | 23 / 22 / 1 | 23 / 22 / 1 | none |
| `tests.hazards.test_import_graph` | 6 / 6 / 0 | 6 / 6 / 0 | none |
| `tests.test_schemas` | 43 / 43 / 0 | 43 / 43 / 0 | none |
| `tests.test_digest_pin_census` | 19 / 19 / 0 | 19 / 19 / 0 | none |
| Total distinct methods | 162 / 161 / 1 | 171 / 170 / 1 | none |

Both `python3.13 -B -m tests.hazards.refusal_census` runs exit 0: `unlisted`, `stale`, `miscounted`, `guard_changed` and `scope_gaps` are empty. The skip is the historical Block-5 design-branch guard. The brief's known container orphan-census zombie failure is historical evidence; that module is outside this brief's allowed runs and was not run or represented as a fresh failure.

An earlier complete after run executed 64 tests in 660.687 s: 63 passed, and `ProductionArchiveTests.test_full_size_real_reducer_harvest_and_export_ingress` failed an old assertion that every H1 row must be rails-only when the meter is absent. Q1 item 4 now requires explicit missing DC/rest rows, so the assertion was corrected to require rails-only **numeric words**, plus 80 explicit missing rows without words (8 groups × 10 models). Production code was not changed. The full affected class then passed 3/3 tests in 18.119 s, followed by the final complete 64-ID run reported above. The earlier failure is retained here rather than silently removed.

Focused development checks passed: 16 manifest tests, 4 census/flag tests, 3 D9/missing-presentation tests, and the three CLI chains (31.934 s). Replaying the new CLI tests with only the analysis CLI replaced by the unchanged-base CLI reproduces exactly two expected failures: `test_both_withheld_files_missing_cli_chain` refuses at the ten-model guard; `test_one_withheld_file_missing_cli_chain` loses the point flag. The genuinely uncollected optional control passes. These repeats are not added to the distinct totals. The initial item-5 development run exposed a fixture-only ordering error: positional indices in the name-sorted design JSON did not represent R6 sub-packs. It was corrected to registered model identities before publication.

Source-AST checks confirm that the estimator, phase-cell, weighting, kept-unit, H1-line/decision, H2/regression, meter and NEG-8 arithmetic functions are unchanged. Removing only the new `config_key` entry from the manifest producer's AST restores every existing function exactly, including merge and all W/R/KV accounting. The production lookup resolves ten distinct identities for all ten registered roster models. `git diff --check` passes; `git diff fd5a3bc7b -- configs/bytes/` is empty. No whole suite, real archive/key read, model inference or hardware measurement was run.

Logs: `/tmp/jw-q1-evidence/before-*.log`, `after-*.log`, `item5-cli.log`, `base-cli-new-tests.log`, `boundary-cli.log`, `after-ingress-expectation.log`, `final-analysis-*.log` (temporary synthetic evidence; the tables here are durable).

## decisions I made

1. Apply origin/main B6-RULING Q1 in full, both cited council Q1 reports and the B4 report; R1–R8/Addenda 1–8 and Block-5 arithmetic/exclusions remain controlling. The flagged surviving pass is primary as ruled; Q2 is untouched.
2. Use the granted `scripts/bytes_manifest.py` to derive `config_key` from registered run configs through Block 6's existing identity function. Do not guess workload/token components or open archives in blinded analysis. The fixture exposes its actual synthetic identity. Every other manifest field and W/R/KV calculation stays unchanged.
3. Census retained collected-session sidecars as well as CSVs before reduction. Match sidecar digests only through the public key, retain total/per-model counts, and emit invalid-record placeholders with no replacement energy. The missing-file flag is a disclosure, not an added physical exclusion.
4. Union all retained pass and point flags, including unrelated disclosures. A computed survivor remains `one_pass`; a no-point model has an explicit missing H1 row without a word and an explicit incomplete MoE answer. H2's inputs, n, k and sensitivity follow D9 unchanged.
5. **Number rule:** every tolerance on a measured/derived quantity needs a derivation comment, between 1e6 times float noise and 1% of the smallest printed half-width; without a half-width use 1e-6 relative or absolute in the column's unit. Exact equality is only for integers, hashes, identities, labels, counts, and identical code on identical inputs. This round adds no measured/derived numeric tolerance: new checks cover identities, labels, flags, counts, exits and identical-input field/byte preservation. No numerical bar was invented.
6. Follow the requested setup; it reports permission denied creating `/opt/homebrew`, while installed Python/zsh suffice for the allowed checks. Keep workspace user files, raw evidence, registration prose, Q2 and `configs/bytes/` untouched. Use API publication with expected-parent checks after every failed Git push.

## left for a later round

No Q1 code item remains. CI/Mac whole-suite validation and independent twin agreement remain external release gates. Q2 and lead-owned registration prose are outside this fix. No new ruling or scope expansion is needed.

**NEEDS_RULING:** none.

## Retained diagnostic evidence from the prior round (unchanged base)


These are current-base defects and controls, **not fixed-code verification**. Every substantive run used `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, Python 3.13.5 and a fresh module TMPDIR. No real archive or key directory was read. Native mock reduction, export, subset release, analysis and unblind were used; stages ran in separate CLI processes, and each stage-1 directory was actually Git-committed before held-out release.

Target: **Qwen3-30B-A3B-4bit**, in s2 with fit model Qwen3-8B-4bit. The diagnostic generator schedules the existing fixture in memory into the R6 sub-pack model groups, with one session per sub-pack/pass: 12 sessions for the missing-file cases; 11 for the optional case. It retains 50 science runs per model/pass, 13 NEG-8 references per session, native random offsets, unequal pass durations (1, 2), signed clock latency (-8, +3) ms and the native 10 Hz meter. This probe changes session scheduling only, uses a midpoint after the first complete model rather than production's within-module midpoint for single-model sub-packs, and does not change the estimator or repository fixture. Missing-file interventions remove only s2's withheld store(s); public fit rows and references remain. The optional intervention never generates s2-p2 and never lists it in the manifest.

`M` below means `bytes.withheld_missing`; `—` means no target row or no table. Point flags shown as absent are literally absent from JSON. H2 is `primary n/k; two_pass_sensitivity n/k`. Rows below show rails / gross primary / primary selection.

| Case | Stage | Target pass rows | Point / flags | Target H1 | MoE answer | H2 n/k | Exit |
|---|---|---|---|---|---|---|---|
| All three | blinded before commitment | — | — | — | — | — | 0 |
| All three | release fit (four explicit keys) | — | — | — | — | — | 0 |
| All three | fit | — | — | — | — | — | 0 |
| All three | local stage-1 Git commit | — | — | — | — | — | 0 |
| One store missing (s2-p2) | blinded post-commit | p1 computed; p2 absent | computed / one_pass; flags absent | mean and p1: neither | active | 10/9; 9/9 | 0 |
| Both stores missing (s2-p1 and p2) | blinded post-commit | no artifacts | no artifacts | no artifacts | no artifacts | no artifacts | **1** |
| Optional s2-p2 uncollected | blinded post-commit | p1 computed | computed / one_pass; flags absent | mean and p1: neither | active | 10/9; 8/9 | 0 |
| All three | release heldout (eleven explicit keys, stage-1 hash) | — | — | — | — | — | 0 |
| One store missing | heldout | p1 computed; p2 unavailable, M | computed / one_pass; flags absent | mean and p1: bytes | active | 10/9; 9/9 | 0 |
| Both stores missing | heldout | p1 and p2 unavailable, M | missing / no_pass; M | **no row** | **no row** | 9/9; 9/9 | 0 |
| Optional s2-p2 uncollected | heldout | p1 computed, no M | computed / one_pass; flags absent | mean and p1: bytes | active | 10/9; 8/9 | 0 |
| One store missing | unblind s2-p2 export | 63 public rows; M printed | — | — | — | — | 0 |
| Both stores missing | unblind s2-p2 export | 63 public rows; M printed | — | — | — | — | 0 |
| Optional s2-p2 uncollected | unblind existing s2-p1 export | 113 rows; no M | — | — | — | — | 0 |

Both-missing post-commit stderr: `BYTES analysis refused: held-out analysis requires all ten model records, including refusals`. This differs from Fable's all-seven-models-per-session probe: with production sub-pack sessions, other held-out models still exist, so the evaluator is called on nine records and refuses.

Missing heldout pass rows currently say `fewer than five kept units per stratum`, rather than `missing`, and omit the sidecar's expected row count. The affected sidecar stores 50 withheld rows for the 30B model; its remaining 63 public rows are 50 fit science rows plus 13 references.

DC-input H2 n and k match rails. Rest uses the same n and k=11, including the labelled sensitivity row. The optional case's sensitivity n=8 is expected: the genuinely uncollected s2-p2 session contains two models, including fit 8B. Missing only the withheld store loses only the held-out 30B pass, leaving sensitivity n=9. Blinded H1 words are blinded diagnostics; no claim is drawn from them.

Local evidence: `/tmp/jw-q1-cli-probe.py`, `/tmp/jw-q1-cli-probe.log`, campaigns under `/tmp/jw-q1-cli-probe.uLMHVA/cli-probe/`; independent pre-commit check `/tmp/jw-q1-precommit.log`. These temporary synthetic artifacts are not a durable delivery or an independent twin agreement.
