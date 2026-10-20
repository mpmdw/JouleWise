gpt-6.1-sol

Activation af419b16, 2026-10-20. **Investigation paused for scope; the five code items are not implemented.**

Branch: `lane/2026-10-20-b6-blinding-group`. Verified implementation/base head: `c68269de8959491f94e61e73a1cbadce5fc44ea9`. The delivery commit adds only this report; its SHA is supplied in the final response. No other branch is pushed.

## Blocking scope request

Add **`scripts/bytes_manifest.py`** to WRITE_SCOPE for a public per-model `config_key`, derived from the registered configuration identity. The production manifest model rows are built at `scripts/bytes_manifest.py:270` and returned at `:284`. The synthetic analysis manifest is built separately at `tests/fixtures/bytes/campaign.py:40`, which is already in scope.

The grouped sidecar exposes only `path`, `row_count`, and a `config_key_sha256` count mapping (`joulewise/b6/export_runs.py:200`). An absent store has no CSV rows from which the blinded loader can recover its model identity. The analysis manifest currently has no `config_key`. Matching only model names would guess the workload identity and token-count components of Block 6's `configuration_key`; opening archive configurations in the blinded stage would break its input boundary. Updating only the fixture would leave the production manifest producer without the required public identity.

The brief explicitly says: **"if that file is outside WRITE_SCOPE, stop and ask for it by name."** The scope question was sent during the investigation. The builder is preserved. Numbered edits remain paused in the requested order. This is a scope request, not NEEDS_RULING about data inclusion or arithmetic.

## Per-item status

| Item | Status | Current source / finding |
|---|---|---|
| 1. Census expected withheld files before reduction | NOT DONE; scope prerequisite above | `joulewise/bytes_analysis.py:764` discovers only CSVs that exist; `:510` loads withheld stores. |
| 2. Blinded post-commit flags and placeholders | NOT DONE; follows item 1 | `joulewise/bytes_analysis.py:777` discards the missing-store result. Both missing files cause the production-session probe to refuse at `:1100`. |
| 3. Union `_missing_labels` flags | NOT DONE; paused under the ordered stop | `scripts/bytes_analyze.py:42` replaces flags and only handles unavailable points; a computed survivor has no point-level missing flag. |
| 4. Explicit missing H1 / active-or-resident rows | NOT DONE; paused under the ordered stop | `joulewise/bytes_analysis.py:1108` skips unavailable H1 points; `:1128` emits a MoE answer only when all three results exist. |
| 5. Three committed CLI-chain regressions with sub-pack sessions | NOT DONE as repository tests | `tests/test_bytes_analysis.py:1342` still uses the inherited two-session campaign. Three separate diagnostic CLI chains with sub-pack sessions were executed below. |
| Pre-commit blinded fewer-than-ten check | DONE; no repair needed at this base | `scripts/bytes_analyze.py:71`: exit 0, exactly three fit models, no H1/MoE/H2 rows, no stage-1 hash supplied. Repeated successfully in all three diagnostic campaigns. |

## End-to-end diagnostic evidence on the unchanged base

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

## Tests before and after

| Before check | Run / passed / skipped | Failing names |
|---|---|---|
| `tests.test_bytes_analysis` | 56 / 56 / 0; 637.253 s | none |
| `tests.hazards.test_refusal_allowlist` | 23 / 22 / 1 | none |
| `tests.hazards.test_import_graph` | 6 / 6 / 0 | none |
| `tests.test_schemas` | 43 / 43 / 0 | none |
| `tests.test_digest_pin_census` | 19 / 19 / 0 | none |
| Total (distinct test methods) | **147 / 146 / 1** | **none** |
| `python3.13 -m tests.hazards.refusal_census` | exit 0; unlisted, stale, miscounted, guard_changed, scope_gaps all empty | none |
| Three diagnostic CLI chains | all stages exit 0 except both-missing blinded post-commit, exit 1 as recorded above | existing Q1 defect |

The single skip is the historical Block-5 branch guard in the refusal allowlist module. Baseline logs are `/tmp/jw-q1-before-analysis.log`, `/tmp/jw-q1-before-tests.*.log`, and `/tmp/jw-q1-before-census.log`.

Commands: `python3.13 -m unittest tests.test_bytes_analysis`; each of the four named registry modules separately with `python3.13 -m unittest`; `python3.13 -m tests.hazards.refusal_census`. Pytest is absent. No whole suite or out-of-scope test module was run. `tests/fixtures/bytes/campaign.py` is a fixture without its own test methods and was exercised through the analysis module and separate CLI chains.

After-implementation checks: **not run**, because implementation stopped before item 1 and no executable repository file changed. The report must not be read as five completed fixes. The known container orphan-census zombie failure is historical evidence from the brief/B4 report; `tests.test_fixture_orphan_census` is not among this brief's allowed test modules and was not run or reported as a fresh failure.

## decisions I made

1. Read Q1 in full on fresh origin/main `2eaa3465b`, both cited Q1 reports, the B4 report, R1-R8 and Addenda 1-8, and the targeted Block-5 arithmetic/exclusion authority. Apply the ruling's flagged survivor result; do not reopen the council dissent or Q2.
2. Preserve `scripts/bytes_manifest.py` and request it by name. Do not guess production configuration keys or treat a fixture-only field as a production fix.
3. Preserve the requested item order at the scope stop. Change only this report; leave estimators, exclusions, registry entries and flag catalogs unchanged. `bytes.withheld_missing` is not yet registered in `configs/b6/flag_catalog_b6.json`; that file is the catalog to update within the brief's conditional catalog scope when implementation resumes.
4. **Number rule:** every tolerance on a measured or derived quantity carries a derivation comment, between 1e6 times float noise and 1% of the smallest printed half-width; without a half-width, use 1e-6 relative or absolute in the column's unit. Exact equality is only for integers, hashes, identities, labels, counts and identical code on identical inputs. This investigation adds no numerical tolerance or arithmetic assertion; it checks labels, identities, counts and exit codes.
5. Run all diagnostics on synthetic inputs. Follow the seat setup script; it reported permission denied creating `/opt/homebrew`, while installed Python 3.13.5 and zsh 5.9 were usable. Do not repair unrelated machine setup or change a registered numerical rule.

## left for a later round

Grant `scripts/bytes_manifest.py`, then implement and separately commit/push items 1-5 in order, including the allowed fixture's public configuration identities and sub-pack sessions, disclose-only catalog registration, contract text, any census-listed registry changes and all requested after checks. Preserve actual unavailable pass causes and sidecar counts; retain flags on surviving points and explicit missing presentation rows. No arithmetic, exclusion or Q2 commitment-provenance change is proposed.

**NEEDS_RULING:** none. **Scope expansion required:** `scripts/bytes_manifest.py`.

## Continuation after the 16:15 scope grant — item 1

The investigation and scope stop above are retained as historical diagnostic evidence. The grant authorizes `scripts/bytes_manifest.py` and `tests/test_bytes_manifest.py`; verified continuation base is `fd5a3bc7bab12c0f6e657e2ea814e1372575231f`.

Item 1 DONE: production manifest merge derives the public `config_key` through Block 6's `configuration_key` on registered run configurations. The fixture carries its actual synthetic configuration identity. Collected session sidecars are censused even when the public CSV is absent. Missing-file metadata retains sidecar total `withheld_row_count` and per-model `withheld_config_row_count`; missing cells print `missing`, without changing the estimator or using raw data to replace absent rows. `configs/b6/flag_catalog_b6.json` now registers `bytes.withheld_missing` as DISCLOSE / REPRESENTATION / RECORDS. Focused checks: 16 manifest tests and 2 census tests passed. The unchanged-base complete checks run in a separate local clone at the verified base so source changes cannot affect them.

Items 2–5 remain pending at this checkpoint. No `configs/bytes/` path was edited.
