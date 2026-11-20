# Row 10 protected source comparison

2026-11-19 · Tier 2 · Sol 6.2 builder · draft against `align/2026-11-17-rl176-build`

The helper compares the eight RL-182 source bindings and the two supplied prompt-hash maps. The comparison is offline and reads raw Git blobs from the named commits. It reports the identity of each scorer and phase module and lists any changed file for ordinary diff review, including if all eight bindings match. Exit 0 supplies one input to row 10. The signatory owns the actual comparison inputs, the authoritative prompt population and the anti-hindsight review.

## Spec freeze and assessed trees

| Stage | Commit | Tree |
| --- | --- | --- |
| Assigned and remote base | `82542232dbb7459b0320c37380925e9372afb7e8` | `865619340d39c4ae9198951d9112889ab7b69860` |
| Executable spec freeze | `2ec202babd981a2751bfe91a79327514b57ce90d` | `9ae020f7a8acec357944a26a43cdaff64d605fb3` |
| Assessed implementation and frozen tests | `edbc4102347f25e3f0333801ff40d55ed320d3fe` | `de787434a91cc8d76087ddb79b8e17eea0881386` |

The baseline RL-176 and RL-182 registration modules passed 32 tests. At the freeze, the 9 new tests exited 1 and reported 39 failing assertions. Every failure reached the expected CLI boundary and found the script absent. In particular, missing-script status 2 could satisfy an exit-code assertion by itself, so each invocation also checks for empty stderr and reads JSON. The freeze preceded the implementation commit and the frozen cases are preserved.

Scope and authority are [RL-182 §1.4(g) and §1.5](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19774-L19796), [its register rows 3 and 7](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19924-L19929) and [the anti-hindsight review](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20265-L20272). The v4 pilot protocol and the existing RL-182 registration text assertions were context. The acceptance oracle is invented source and prompt-hash projections with known mutations. [P4 at the W1 baseline](https://github.com/mpmdw/JouleWise/blob/b2e01464d6d4fbf2901ff4d4154df9455104a12a/docs/align/pilot_protocol_v4.md) · [Registration context](https://github.com/mpmdw/JouleWise/blob/82542232dbb7459b0320c37380925e9372afb7e8/tests/align/test_rl182_registration.py#L19-L119)

## Protected bindings

All locations are in `joulewise/align/apple/rl176.py` at `82542232d`. Each fixture changed one byte and reported exactly the named binding with two distinct SHA-256 values.

| Binding | Baseline line | Synthetic mutation | Result |
| --- | ---: | --- | --- |
| `S_SUPERIORITY_ALPHA` | 35 | Assignment | PASS |
| `_tail_test` | 85 | Parenthesized decorator | PASS |
| `_holm` | 178 | Inline comment | PASS |
| `_decode_design` | 194 | Body comment | PASS |
| `_decode_rows` | 200 | Final indented body comment | PASS |
| `_residual_scores` | 258 | Body literal | PASS |
| `_s_rank` | 300 | Signature default | PASS |
| `_q_energies` | 481 | Body literal | PASS |

The helper compares the whole scorer blob before locating definitions. It uses Python syntax and symbol tables to delimit each binding, validate direct uniqueness and catch statically visible extra module or explicit global bindings. It compares physical byte spans, including decorators, inline comments, trailing indented body comments and line endings. Other bytes go to ordinary review through the changed-file inventory. The Git inputs require regular blobs at both ruled module paths. The projection is a nonempty UTF-8 JSON object with unique, nonblank identifiers and 64-digit hexadecimal SHA-256 values. Identifier matching is exact. Hexadecimal case represents the same digest.

## Verification

Executed locally with Python 3.13. Temporary files went into the assigned seat. The two commands below are the focused suite for this helper and its neighboring public contracts. The anchor and `origin/main` have no `tests/contracts` directory.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration.ProtectedSourceComparisonTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration align.test_rl176
git diff 82542232d..HEAD --check
```

The focused helper suite passed 9 tests covering 55 CLI invocations. The combined focused suite passed 41 tests. Diff check passed. The same commit and equal trees at distinct commits returned 0 with identical invented maps. Changes confined to an unrelated top-level function, the phase module or both returned 0 and named every changed file. The eight one-byte mutants and a single LF-to-CRLF change returned 1. Missing, duplicate and rebound definitions on either side, invalid syntax, an unreadable tree, invalid commit IDs, missing or non-regular module paths and missing, empty, duplicate-key or malformed maps returned 2. A changed key set and a changed digest returned 1 with the relevant identifiers. Canonical full-suite evidence is the hosted `ci` workflow on the draft PR, including its twelve Python 3.13 shards and exclusive jobs.

### CI fixture correction

At initial draft head `8c9489541e20063e2b5ba0230355e9a8c40d2a09`, shard 12 reproduced one MED integration-seam finding. The repository-wide Git fixture maintenance guard flagged the direct Git initialization in the new test setup. The fix uses `tests.git_fixture.init_git_fixture`, which disables detached maintenance for disposable repositories. All nine frozen cases and the comparator are preserved. [Failing shard](https://github.com/mpmdw/JouleWise/actions/runs/44690615074/job/136135409032)

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper
PYTHONPATH=tests:. python3.13 -B -m unittest tests.test_git_fixture_maintenance
```

The first command confirmed the original failure locally. The full five-test maintenance module and the two focused commands above passed with the shared helper. The builder verified zero HIGH, one MED and zero LOW findings in CI triage. The independent audit round count remains zero.

### Synthetic invocation

The following full IDs are from the seat's temporary fixture Git repository, built from the `ProtectedSourceComparisonTests` toy source and maps with author and committer date `2020-01-01T00:00:00+00:00`. `ROW10_TOY` names the fixture directory.

```sh
python3.13 -B scripts/compare_c1_protected_sources.py \
  --repo "$ROW10_TOY/repo" \
  --w1-commit 546e6481910bdd3cb43ca2f527046f8e5a926785 \
  --c1-commit d0d28d564fb31f1ec1303a4511ca74d7a298cc3c \
  --w1-prompts "$ROW10_TOY/w1.json" --c1-prompts "$ROW10_TOY/c1.json"
```

This returned 0, with `rl176.py` in `files_for_review` and both change maps empty. Substituting `546e6481910bdd3cb43ca2f527046f8e5a926785` for C1 returned 0 with no changed files. Substituting `6bb5615be138b728d0f026777de333d11e1941b7` returned 1 and named `_decode_rows`.

### Lead invocation template

The lead supplies full commit IDs from the signed bindings and two privately verified, public-safe identifier-to-digest projections. The helper takes only the projections.

```sh
python3.13 -B scripts/compare_c1_protected_sources.py \
  --repo "$ROW10_PUBLIC_CODE_REPO" \
  --w1-commit "$ROW10_W1_COMMIT" --c1-commit "$ROW10_C1_COMMIT" \
  --w1-prompts "$ROW10_W1_PROJECTION" --c1-prompts "$ROW10_C1_PROJECTION"
```

Use the paths in `files_for_review` for the ordinary public source diff. For both ruled modules the corresponding command is:

```sh
git --no-replace-objects -C "$ROW10_PUBLIC_CODE_REPO" diff --no-ext-diff --no-textconv \
  "$ROW10_W1_COMMIT" "$ROW10_C1_COMMIT" -- \
  joulewise/align/apple/rl176.py joulewise/align/apple/rl176_phases.py
```

## Condition 13 metadata

The ten paths are the literal `R1_EXECUTED_SOURCES` tuple at the anchor. For each of `b2e01464d6d4fbf2901ff4d4154df9455104a12a`, `82542232d` and the assessed head, the command was `git ls-tree -r <revision> -- <the ten paths below>`. All ten blob IDs and file modes matched. No condition-13 path had an inherited absence. The older W1 baseline is the condition-13 reference here. The receipt comparison requires the lead's separate signed commit IDs.

| Path | Shared Git blob ID |
| --- | --- |
| `scripts/align_r1_rehearsal.py` | `33c6876e6a988bee93fc49a0ba554f7c2c3bf277` |
| `scripts/align_r1_runtime.py` | `96b249a6eb44c4de2887aeeadff089c3040d8cfa` |
| `joulewise/align/apple/r1_runtime.py` | `261761f1a5e39220614b74d53d125022278502db` |
| `joulewise/align/apple/r1_runtime_contract.py` | `1ef822bee6d3b4951ad24cd1991ea31741d30161` |
| `joulewise/align/apple/smc_enumeration.py` | `8a1a96dcb10ebb16809717af15918d5366b0d31c` |
| `joulewise/align/apple/thermal_gates.py` | `b46769d70df02de09dbeb07e4c0020c472477dcb` |
| `configs/align/v4/r1_runtime.json` | `bf8479b26774b4d6a7bb3d44c6e2d662ddeb199e` |
| `joulewise/align/apple/r1_phase_table.py` | `e412bb4389aae4e4239b47842512db178d4b53a2` |
| `joulewise/align/apple/workload.py` | `ff30c29178ad9ccceab96140c569b8f14afa16e9` |
| `joulewise/align/apple/thermal.py` | `e7cbd6808c5a407524e3a85254090a46c33fa910` |

## Dispositions and holds

| Obligation | Disposition |
| --- | --- |
| Row 10 tooling | Builder fixture proof complete. Actual W1-to-C1 comparison and row disposition open with the signatory. |
| RL-182 register row 3 | Send each changed protected binding to Fable before rebind. Any changed scientific meaning or protected rule requires Fable's ruling. |
| RL-182 register row 7 | Lead privately verifies extraction against the authoritative population and attests that it is complete, no prompt was padded and no fourth timing term entered. The helper compares only the supplied keys, hashes and protected source spans. |
| Ordinary diff and anti-hindsight | Lead reviews every listed scorer or phase diff and assembles the rule changes since R1, with ruling IDs, for Fable under RLD:20269–20272. |
| Builder exit and merge | Astra executing audit, integration owner acceptance and Opus final-tree acceptance remain open at this report's build cutoff. Opus owns the merge. |
| Live receipt evidence | Signatures and other arm gates remain with their owners. PR #813 and PR #836 are references in the public workflow. |

At initial builder handoff, independent audit rounds were 0 of 3. Apply the round cap and return to spec for a VERIFIED HIGH spec gap or contract conflict in any round, a non-decaying second round, or a VERIFIED HIGH in round three. [Pipeline at the process pin](https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/docs/process/PIPELINE.md#L36-L68)

## Astra round 1 corrections

Astra assessed `e291acc786926397f2a04a4b35019d9005584154`, tree `09838f079d11674176a7ebf5fe4df92d7022f11f`, and blocked. The builder replicated both findings against the exact audit Git objects and added the two red regressions. The correction was assessed at `86453f6b191434d8605b09dc34e2d1f8aaadc3be`, tree `02675e12800ab7175c8cbd3561f055f90c4a9a16`.

| Round | VERIFIED HIGH | VERIFIED MED | VERIFIED LOW | Root cause |
| --- | ---: | ---: | ---: | --- |
| 1 | 2 | 0 | 0 | Both implementation bugs in the frozen contract |

| Finding | Correction and regression | Exact audit fixture result |
| --- | --- | --- |
| A form feed before the first `_holm` decorator hid it from the span | Use Python's tokenizer and module indentation to locate the actual `@` tokens, require the token count to match the AST decorator count, and hash the original physical bytes. `test_first_decorator_is_hashed_after_form_feed_indentation_reset` covers the original prefix and mixed whitespace with a multiline expression, verifying independently calculated hashes in both directions. | Before 0 with an empty change map. After 1 with `_holm` and both expected SHA-256 values. |
| A write through `sys.modules[__name__]` hid a level rebound | Refuse protected attribute stores or deletes and visible dynamic namespace access throughout the scorer, including nested functions and aliased namespace primitives. `test_indirect_module_namespace_rebindings_fail_closed` covers the audit write, attribute deletion, aliased registry and mapping access, a function's global dictionary and aliased reflection. Each variant is refused on either side and when identical. | Before 0 with an empty change map. After 2 naming `S_SUPERIORITY_ALPHA`. |

The namespace guard is conservative. A scorer with visible reflection or mutable namespace access requires manual review before a byte comparison can support row 10. The ordinary scorer and phase diff and the anti-hindsight review remain with the lead. Both findings were implementation bugs, so the §3 criteria permit a repair in this round. Round 2 must have at most one VERIFIED HIGH or MED in total and any VERIFIED HIGH must have a root cause seen in round 1.

The two new regressions produced eight failing subtests on the old helper. All nine frozen cases were preserved. These commands passed with the correction, with 11 tests and 77 synthetic CLI invocations in the named class and 43 tests in the combined run. All eight protected bindings also extracted from the public anchor without executing it.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration.ProtectedSourceComparisonTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration align.test_rl176
```

The exact audit fixture checks use the retained invented Git repository and map in `AUDIT_FIXTURES`.

```sh
python3.13 -B scripts/compare_c1_protected_sources.py --repo "$AUDIT_FIXTURES/repo" \
  --w1-commit 1d49220cd74f86248be22db49d60600cb834a001 \
  --c1-commit 37fcf2f44021a2719e540705a6ae80e543b785ba \
  --w1-prompts "$AUDIT_FIXTURES/map.json" --c1-prompts "$AUDIT_FIXTURES/map.json"
python3.13 -B scripts/compare_c1_protected_sources.py --repo "$AUDIT_FIXTURES/repo" \
  --w1-commit 94f1d185daec9bf5ee988fc2a99b60efaa1eed31 \
  --c1-commit 63bfaf4ceb611720ae95cae4f6feeb16a2c3d6e8 \
  --w1-prompts "$AUDIT_FIXTURES/map.json" --c1-prompts "$AUDIT_FIXTURES/map.json"
```
