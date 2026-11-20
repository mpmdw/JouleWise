# Row 10 protected source comparison

2026-11-19 · Tier 2 · Sol 6.2 builder · draft against `align/2026-11-17-rl176-build`

The helper compares committed dependency bytes, the eight RL-182 bindings, and the two supplied prompt-hash maps. Spec v3 adds a behavioural oracle to the isolated release import and freezes the conservative import and resource closure. A change anywhere in that byte scope returns 2. Runtime identity and the static binding hashes provide additional signals. Exit 0 in combined mode supplies one input to row 10. The signatory owns the actual comparison inputs, the authoritative prompt population and the anti-hindsight review.

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

## Initial static verification

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

### Synthetic static diagnostic

The following full IDs are from the seat's temporary fixture Git repository, built from the `ProtectedSourceComparisonTests` toy source and maps with author and committer date `2020-01-01T00:00:00+00:00`. `ROW10_TOY` names the fixture directory.

```sh
python3.13 -B scripts/compare_c1_protected_sources.py \
  --static-only \
  --repo "$ROW10_TOY/repo" \
  --w1-commit 546e6481910bdd3cb43ca2f527046f8e5a926785 \
  --c1-commit d0d28d564fb31f1ec1303a4511ca74d7a298cc3c \
  --w1-prompts "$ROW10_TOY/w1.json" --c1-prompts "$ROW10_TOY/c1.json"
```

In spec v3 this returns 2 and lists `rl176.py` in `files_for_review`, with an empty protected binding change map. Substituting `546e6481910bdd3cb43ca2f527046f8e5a926785` for C1 returns 0 with no changed files. Substituting `6bb5615be138b728d0f026777de333d11e1941b7` returns 2 and names `_decode_rows`. Static-only mode emits `mode: static-only`. These are diagnostics without runtime evidence.

### Lead invocation template

The lead supplies full commit IDs from the signed bindings, two privately verified public-safe identifier-to-digest projections and a trusted preloaded Python 3.13 Docker image ID. Both Git commits must carry the production release entry point. The isolation setup and spec v3 review scope are specified below.

```sh
python3.13 -B scripts/compare_c1_protected_sources.py \
  --runtime-image "$ROW10_RUNTIME_IMAGE" \
  --repo "$ROW10_PUBLIC_CODE_REPO" \
  --w1-commit "$ROW10_W1_COMMIT" --c1-commit "$ROW10_C1_COMMIT" \
  --w1-prompts "$ROW10_W1_PROJECTION" --c1-prompts "$ROW10_C1_PROJECTION"
```

Use the paths in `files_for_review` for the lead's ordinary review. Protected changes route to the research lead under RL-182 §1.5. The command below covers both ruled modules.

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
| RL-182 register row 7 | Lead privately verifies extraction against the authoritative population and attests that it is complete, no prompt was padded and no fourth timing term entered. The prompt check compares the supplied keys and hashes. |
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
python3.13 -B scripts/compare_c1_protected_sources.py --static-only --repo "$AUDIT_FIXTURES/repo" \
  --w1-commit 1d49220cd74f86248be22db49d60600cb834a001 \
  --c1-commit 37fcf2f44021a2719e540705a6ae80e543b785ba \
  --w1-prompts "$AUDIT_FIXTURES/map.json" --c1-prompts "$AUDIT_FIXTURES/map.json"
python3.13 -B scripts/compare_c1_protected_sources.py --static-only --repo "$AUDIT_FIXTURES/repo" \
  --w1-commit 94f1d185daec9bf5ee988fc2a99b60efaa1eed31 \
  --c1-commit 63bfaf4ceb611720ae95cae4f6feeb16a2c3d6e8 \
  --w1-prompts "$AUDIT_FIXTURES/map.json" --c1-prompts "$AUDIT_FIXTURES/map.json"
```

## Astra round 2 correction

Astra assessed `3f781222f3cd4ae1bc6cea3dd738abe9cbd9748b`, tree `a2d5ec016702eb9a54a7a1f49a6e3f3402420fca`, and blocked on one VERIFIED HIGH. The exact invented pair adds `_holm.__code__ = revised.__code__`. Both the initial helper at `edbc41023` and the audited round 1 repair returned 0 with an empty protected change map in both directions. The correction and regression were assessed at `2ab96a5123d8c0a88e51eac49833aece1b5ade7d`, tree `014a6d13a7cd4d828ae44c73c7ebfdb6633c62a3`.

| Round | VERIFIED HIGH | VERIFIED MED | VERIFIED LOW | Root cause |
| --- | ---: | ---: | ---: | --- |
| 2 | 1 | 0 | 0 | `impl-bug`, same indirect-mutation guard gap as round 1 |

The guard refuses a protected callable reference used as a value, including exposure through an alias, container, argument, import, attribute read or pattern capture. Direct calls remain supported. The guard uses syntactic names and can decline a benign use of the same spelling as a value. Such source goes to the lead for manual review. This closes the first-class callable mutation paths in the regression across code, defaults and keyword defaults. The scorer source at `82542232d` still yields all eight protected bindings without executing it.

`test_mutating_or_exporting_protected_callable_objects_fails_closed` produced eight failing subtests on the old helper. The correction rejects all eight variants on either side and when the invalid input is identical, and retains exit 0 with a scorer review entry for a residual edit that uses direct calls. All nine frozen cases and both round 1 regressions were preserved. The exact round 2 pair returns 2 naming `_holm` in both directions. The exact round 1 decorator and module-object pairs still return 1 with the expected hashes and 2 naming the level, respectively.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration.ProtectedSourceComparisonTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration align.test_rl176
python3.13 -B scripts/compare_c1_protected_sources.py --static-only --repo "$AUDIT_FIXTURES/repo" \
  --w1-commit 406c3abeb29412197d1de6d53dba09dab6a07d73 \
  --c1-commit 3e17c928df2df49e4412dc1b1a70e6500b672ec0 \
  --w1-prompts "$AUDIT_FIXTURES/map.json" --c1-prompts "$AUDIT_FIXTURES/map.json"
```

The focused class passed 12 tests and 102 synthetic CLI invocations. The combined suite passed 44 tests. The audited aggregate is 3 VERIFIED HIGH, 0 MED and 0 LOW across two independent rounds. Round 2 decays under §3 with `H₂ = 1 ≤ floor(2 / 2)` and the existing `impl-bug` root cause. A VERIFIED HIGH in round 3 returns to spec. Integration-owner and Opus acceptance and the signatory's actual receipt comparison, attestation and review remain open.

## Astra round 3 and spec v2 (historical)

Astra assessed `d0fb89a78b417bc43986366c01fe3b3ec7322e55`, tree `f1086f105d50964396437f6ae8d661218ac95ef0`, and blocked. The exact invented pair `b409e110b1531ffade1f130bb267cc466321ec83` → `7769e46b0c5fef95d8e6006079b1b3665357b148` changes only the phase module. At import it sets the scorer's level to 0.75 from 0.25. The old static comparator returned 0 in both directions. The round had 1 VERIFIED HIGH, 0 MED and 0 LOW. The `spec-gap` was that static scorer extraction could establish the source span while a sibling changed the effective binding. The three v1 audits ended with 4 VERIFIED HIGH, 0 MED and 0 LOW, and the round 3 finding returned the work to spec under Pipeline §3.

The lead's P1/P2 engineering rule is spec v2. Its executable freeze is `46dc0bbfbf3dadbd6f27b0d3b8395131b532d069`, tree `74f6737555b47c9f5c9984b115b161a40dc5cc40`, on assessed v1 head `d0fb89a78`. Before implementation, the original 12 static tests passed and the seven new tests gave 102 failing assertions on the old helper. Expected failures included absent runtime and wiring options, the phase-only false negative, lack of unapproved-byte review and default equality without runtime evidence. The new phase fixture keeps Astra's circular import and uses an invented release entry point carrying the production module name. Both directions must refuse and name the level. The 96-case sweep covers all eight protected names through each of the three other modules in the invented package, exercising direct assignment, `setattr`, `sys.modules` and a class-body import-time effect.

### Runtime identity

The combined command requires an approved, preloaded local Docker image by full `sha256:` image ID. It must provide Linux Python 3.13 at `/usr/local/bin/python3` and GNU `timeout` at `/usr/bin/timeout`. The tool uses the local Unix Docker socket and requests no pull, no network, a read-only root, non-root execution, dropped capabilities and bounded workers. The only read-only mounts are a private projection of committed, regular `.py` blobs under `joulewise/` and `scripts/` and a snapshot of the trusted worker. The repository checkout, Git administration, projection JSON and measurement roots stay outside the mounts. Each side uses the same trusted worker snapshot in a fresh interpreter. [Docker run reference](https://docs.docker.com/reference/cli/docker/container/run/) · [None network driver](https://docs.docker.com/engine/network/drivers/none/) · [Read-only bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)

The worker imports `scripts.align_v4_series_release` and follows its top-level production import graph. It observes the scorer from that graph after the import. It fingerprints recursive code-object fields, defaults and keyword defaults, closure cells, function state and wrapper links such as `__wrapped__`, and the level's value. Repeated references to a mutable object remain distinct from independent copies with equal contents. Source staging prefixes are normalized, and source line metadata remains part of the code identity. Static spans retain declared decorator bytes. Runtime evidence covers effective wrapper state visible after import. An import failure, missing object or unsupported runtime representation requires review.

The assigned seat has no usable Docker backend and denied a nested sandbox attempt on invented files. The synthetic tests use a fixture transport that verifies the isolation arguments and starts the real worker in fresh interpreters over invented code. The suite establishes worker and comparison behavior. Execution with a real, approved isolated image on the lead's authorized desk host remains open. The pinned `82542232d` anchor lacks the release entry point. A missing entry point on either receipt commit returns 2. The lead still owns any ruling for an actual W1 receipt that predates the release entry.

### Wiring spans and dispositions

The default wiring allowlist is empty because RL-182 §1.5 identifies the wiring exception without enumerating admitted spans. The lead can supply `--wiring-allowlist "$ROW10_APPROVED_WIRING"` with a public JSON array of entries. Each entry has `path`, `before` and `after`. Each side has the complete blob's lowercase `sha256` and a `spans` array of sorted, disjoint, zero-based half-open byte ranges `[start, end]`. An insertion or deletion can use an empty spans array on one side. An entry applies in either direction to that exact blob pair. The bytes outside the ranges must match and the ranges must avoid the eight static protected bindings. The lead owns approval of what qualifies as wiring.

`files_for_review` continues the ordinary file inventory. `research_lead_review` names either ruled module with uncovered bytes, including when runtime hashes match or runtime evidence fails. Combined mode returns 2 for a runtime difference or unresolved input, 1 for static differences or uncovered bytes with a complete matching runtime comparison, and 0 for complete equal protected inputs with no uncovered bytes. Diagnostic `--static-only` preserves the previous static return codes and the new review inventory.

The revised builder checks use the following commands in seat scratch.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration.ProtectedSourceComparisonTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration.ProtectedRuntimeComparisonTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration align.test_rl176
git diff 82542232d..HEAD --check
```

The implementation was assessed at `74334dbabbed1d9e65c291ed380fb4d59f4e57fe`, tree `44a92c533d668b24914d550c008b330b76a16ee3`. The final focused run passed 52 tests. The v2 class made 113 synthetic comparison invocations, including the 96 mutations, and both directions of the adapted phase-only reproduction reported the level and phase-review flag. The exact retained audit pair still reports the phase-review flag and fails combined mode because its original invented commits have no release entry. All 12 v1 static cases and all seven frozen v2 cases were preserved. An extra aliasing regression was red against the first encoder and passes with reference tracking. The first sweep overlapped a worker edit and observed mismatched encoder versions. An invented concurrent-edit probe passed after the parent pinned one worker snapshot for both sides.

The lead's signatory and anti-hindsight work, new-spec acceptance, and integration-owner and Opus decisions remain open. The v1 audit count stays at three.

## Audit 4 and spec v3

Audit 4 assessed `e831e9149ef9c6192ac38a47a4a71a257dd155d9`, tree `72d6d66ebdd0837c166200fd2cc379b6d50c5cba`, and recorded 2 VERIFIED HIGH, 2 VERIFIED MED and 0 VERIFIED LOW. The lead replaced the v2 byte-exemption policy with B1/B2. Spec v3 froze at `5ff27161af1d7a1118384fa327b0fbb5cdce7538`, tree `805f157b909bf542de1ad5c4f8bfc0d6777c657e`, against that assessed v2 head. The six targeted cases showed four failures and two errors before implementation. The two supplemental regressions cover multiple simultaneous oracle differences and a file-existence branch skipped in the source-only projection. The latter reproduced an exit 0 on the partial implementation.

| Audit 4 finding | Regression and disposition |
| --- | --- |
| HIGH · shared NaN in the exclusion default is replaced by a separate NaN | `test_audit_four_nan_alias_changes_default_oracle` returns 2 in both directions with `_holm/defaults` and the changed dependency. P1 also tracks reference identity for floats and complex numbers. |
| HIGH · root-level imported options module changed the effective S level | `test_audit_four_root_module_is_projected_and_in_the_closure` returns 2 in both directions with the root module and the level in P1 and B2. |
| MED · a deleted phase module hid a simultaneous scorer edit | `test_audit_four_deleted_phase_preserves_every_flagged_path` returns both paths in both directions and gives the deleted file a null identity on the missing side. |
| MED · the new isolated interpreter requires a reviewed command site | `test_tracked_command_sites_match_reviewed_allowlist` remains a scope hold at `isolated_identity:d16cb64193a201ee`. The B1 removal of byte exceptions applies to wiring. The existing repository command inventory is a separate gate. |

The static closure follows literal absolute and relative imports transitively, including package initializers. The source-only runtime projection includes root-level modules and the rest of the committed Python source. The worker records tracked project paths opened during the release import, including failed open attempts. An observed, unprojected import-time resource returns 2, preserving the file report and any oracle differences still available.

B1 also freezes all remaining tracked paths by Git blob ID and mode. A file-existence test can suppress both an open and a behavioural difference when the source-only projection omits that file. The complete tracked-tree fallback covers that case without reading other blobs. `closure_changes` labels each changed path as an import-time open, a static import, a potential module or a potential resource. Added and deleted paths are included. The conservative resource scope can flag unrelated tracked changes for the lead. Spec v3 has no wiring exemptions.

B2 evaluates a fixed synthetic table following each full release import. It covers zero and one decode token, NaN and infinity, empty traces and rank strata, equal-rank ties, the five/six-row training boundary, the S significance threshold, both Holm cutoffs, and stamp ownership boundaries. A no-argument case applies when the effective signature permits it, including the audit's default-alias reproduction. Inputs are freshly copied for each case. The table includes the in-place Holm result and distinguishes an exception outcome by type. The frozen public scorer witness pins representative expected outputs for all eight protected names. The combined CLI reports every differing function and input in `oracle_changes`, alongside `runtime_changes` and the complete file flags. It emits digests for outcomes.

```sh
export TMPDIR=/Volumes/JW-EXT/scratch/pl-d-c1-protected-source-diff/build/tmp
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_rl182_registration.ProtectedSourceComparisonTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_rl182_registration align.test_rl176
PYTHONPATH=tests:. python3.13 -B -m unittest \
  tests.test_host_command_sites.HostCommandSiteTests.test_tracked_command_sites_match_reviewed_allowlist
git diff 82542232d..HEAD --check
```

The implementation was assessed at `cdcbee79934a43e721d9ee668b59050f676611b4`, tree `76b2ca8c67c2da5a1e61a42f49a3f1643d28283f`. The six targeted cases passed after implementation. The 25 frozen v3 test methods are preserved and the combined focused run passed 59 tests. Condition 13 still matches all ten Git entries in the W1 baseline, the base and this implementation. The focused command site check reproduced the single unregistered launcher entry, with zero stale entries. The reviewed inventory file is outside this seat's authorized write scope.

The real isolated-image run remains open. The builder exercised invented commits and the same worker through the fixture transport, plus the frozen synthetic table on the public anchor scorer. The signatory retains the actual comparison and the anti-hindsight review. The integration owner and Opus retain acceptance.

## Lead ruling on a missing release entry point

If either signed commit lacks `scripts/align_v4_series_release.py`, the combined command exits 2, identifies the affected side and retains every flagged file. Row 10 stays open. Only the full release import from each commit can establish behavioural equality under this comparison. RL-182 §1.5 permits W1 to be signed before the release caller exists. The comparison refusal leaves that signing rule intact. [RL-182 §1.5](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19776-L19796)

The frozen missing-entry case remains in place. The supplemental case removes the caller and edits both ruled modules in the invented tree. With either input order it requires exit 2, the missing side in the error, and all three affected paths in both review outputs. Both tests passed without a comparator change.

```sh
TMPDIR=/Volumes/JW-EXT/scratch/pl-d-c1-protected-source-diff/build/tmp \
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_rl182_registration.ProtectedRuntimeComparisonTests.test_missing_release_entry_point_fails_closed_on_either_side \
  align.test_rl182_registration.ProtectedRuntimeComparisonTests.test_missing_release_entry_point_names_side_and_preserves_all_file_flags
```

The final-head run at `85484fb881726b175690d6c8f37b152649862aa2` passed 20 of 21 jobs. The sole failure requires a reviewed row in `tests/host_command_sites.json` for `scripts/compare_c1_protected_sources.py`, locator `isolated_identity:d16cb64193a201ee`, command `python-isolated`. The builder requested lead authorization for exactly that row. `NEEDS_SCOPE` remains open until authorization. Acceptance requires zero missing or stale command sites and green final-head CI. The approved isolated-image run is a separate open check. [Failing shard](https://github.com/mpmdw/JouleWise/actions/runs/44756704940/job/136359419715)
