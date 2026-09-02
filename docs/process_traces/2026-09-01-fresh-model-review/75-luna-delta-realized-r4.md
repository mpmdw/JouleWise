# 75 — luna (max) delta re-audit of realized-prefill r4 + bench adjudication

Read-only over `$S/realized-r4-audit` (copy of `feat/2026-09-01-realized-prefill`
@ `18a939f3`), mutations replayed by luna on the copy with temporary write
scope. Report verbatim below; magistrate adjudication follows.

## Magistrate adjudication (bench, 2026-09-01 18:10)

- **F1 CONFIRMED — after a wrong first replay.** The magistrate's first replay
  substituted `if False:` for the domain comparison (never-flag) and got
  `test_domain_mutation_is_mismatch` FAIL, and provisionally recorded F1 as
  "not reproduced". Luna's mutant (g) is `if True:` (flag-every-bundle,
  log lines 6270-6289). Replayed exactly: `Ran 81 tests … OK` — SURVIVED.
  Cause: every mismatch row asserts only that its own field is named in the
  single problem string; none asserts a coherent bundle yields nothing.
  Recorded against the magistrate: read the seat's mutation text before
  replaying, never reconstruct it from the finding title.
- **r5 (bench, `925a58c0`):** `test_coherent_registration_and_realization_yield_no_problem`
  — coherent registered/realized bundle → `problems == []` and no field name
  in any reader problem. Suite 82 OK.
- **Post-r5 replay on the scratch copy** (each restored, copy clean):

  | mutant | result |
  |---|---|
  | domain `if True:` (luna g) | KILLED — `test_coherent_registration_and_realization_yield_no_problem` |
  | domain `if False:` | KILLED — `test_domain_mutation_is_mismatch` |
  | count `if True:` | KILLED — coherent test + `test_equal_counts_different_hash_names_hash_mismatch` |
  | hash `if True:` | KILLED — coherent test + `test_coherent_count_mutation_is_one_mismatch` |

- **V4 (luna: `tests.test_schemas` standalone `FAILED (failures=2, skipped=1)`)**
  not reproduced at the bench on main (36 OK) or the branch (40 OK); luna's
  row most likely ran while a mutant was applied. Not a finding.
- Luna's advisory that `prompt_realization_evidence_missing` is the correct
  code for an ill-formed registration (not `mismatch`) is accepted; it is the
  code r4 emits.
- Lane closed to **PR #258**.

## Luna report (verbatim)

```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"R4 is production-correct on the requested paths; one nonblocking positive-domain test gap remains because mutant (g) survived.","workspace":{"base_requested":"18a939f36f5d3362ad5615f0ddf39b59e6397bd9","base_mode":"exact","head_start":"18a939f36f5d3362ad5615f0ddf39b59e6397bd9","head_end":"18a939f36f5d3362ad5615f0ddf39b59e6397bd9","upstream_end":"18a939f36f5d3362ad5615f0ddf39b59e6397bd9","branch":"feat/2026-09-01-realized-prefill"},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"should_fix","title":"Positive domain-match coverage gap","detail":"Mutant (g), replacing the domain comparison with always-True, survived all 81 bundle-reader tests.","recommendation":"Add a coherent registered/realized bundle assertion that expects zero prompt-realization problems."}],"mutation_summary":"Six mutants killed; one survived. No out-of-scope diff hunk."},"verification":[{"id":"V1","kind":"inspection","cmd":"git diff --stat 504af787..18a939f3; git diff --name-only 504af787..18a939f3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["joulewise/bundle_read.py","tests/test_bundle_read.py"]},"expected":{"exit_code":0,"tail_regex":"joulewise/bundle_read\\.py\\ntests/test_bundle_read\\.py"}},{"id":"V2","kind":"suite","cmd":"python3 -m unittest tests.test_bundle_read 2>&1 | tail -3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 81 tests in 10.269s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 81 tests in [0-9.]+s\\nOK"}},{"id":"V3","kind":"suite","cmd":"python3 -m unittest tests.test_bundle_read tests.test_schemas 2>&1 | tail -3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 121 tests in 11.379s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)"}},{"id":"V4","kind":"test","cmd":"python3 -m unittest tests.test_schemas","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 40 tests in 0.083s","","FAILED (failures=2, skipped=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=2, skipped=1\\)"}},{"id":"V5","kind":"inspection","cmd":"git status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"FL1","kind":"verification_gap","level":"nonblocking","text":"Mutant (g) survived because no coherent expectation/domain success case asserts zero problems.","needs":"Add the positive regression test."},{"id":"FL2","kind":"environment","level":"nonblocking","text":"git checkout -- was blocked by the external worktree index.lock permission; each mutation was restored exactly with apply_patch and final status is clean.","needs":""}]}
```

## Findings

F1 — should_fix. No diff hunk exists outside `joulewise/bundle_read.py` and `tests/test_bundle_read.py`.

All rows used `python3 -m unittest tests.test_bundle_read 2>&1 | tail -3`.

| Mutant | Verdict / tail | Failing test |
|---|---|---|
| (a) first 8 | KILLED — `FAILED (failures=1)` | `test_hash_comparison_binds_every_character_not_a_prefix` |
| (b) last 8 | KILLED — `FAILED (failures=1)` | same, vector 0 |
| (c) sorted chars | KILLED — `FAILED (failures=1)` | same, vector 4 |
| (d) first 32 | KILLED — `FAILED (failures=1)` | same, vector 2 |
| (e) raw `.get()` + lowercase | KILLED — `FAILED (failures=1)` | `test_registered_operand_is_canonicalized_before_comparison` |
| (f) uppercase regex | KILLED — `FAILED (failures=1)` | same; additionally `test_model_identity_sha256_pins_reject_noncanonical_values` (`chat_template_sha256`) and `test_prompt_token_expectation_rejects_malformed_registration` (`uppercase-hash`) |
| (g) always-true domain | SURVIVED — `OK` | none |

## Residual risk

`from_mapping` rejects whitespace variants, strings, bools, `None`, aliases, and extra keys before comparison; realized hash/count validators reject the corresponding variants. Realized domains accept any nonempty string, but exact comparison means aliases or whitespace produce mismatch, never a pass. `evidence_missing` is correct for ill-formed registration because mismatch presumes two valid operands.

`git status --short` (copy): empty