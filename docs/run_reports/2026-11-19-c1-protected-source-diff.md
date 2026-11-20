# Row 10 protected source comparison

2026-11-19 · Tier 2 · Sol 6.2 builder · draft against `align/2026-11-17-rl176-build`

The comparator is the B1 closure byte freeze. It uses the union of tracked files as the conservative closure of the release caller and scorer. It compares blob IDs, modes and object kinds using Git metadata. This scope includes dependencies outside the scorer package, resources read at import time and otherwise unrelated tracked changes. It lists every changed path, including additions and deletions. A rename appears as a deletion and an addition.

The only inputs are a local public-code Git repository and two full commit IDs. Exit 0 means the required files are available and the committed file identities match. Exit 2 means one or more identities differ or an input is invalid. `closure_changes` gives the before and after identity for each path. A missing side is `null`. `files_for_review` lists the same paths in sorted order. The helper uses Git object metadata only.

The scorer, phase module and `scripts/align_v4_series_release.py` must exist as regular Git blobs on both sides. A missing caller identifies the affected side, preserves every changed-file flag available from the trees and leaves row 10 open. RL-182 §1.5 permits W1 to be signed before the caller exists. [RL-182 §1.5](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19776-L19796)

## Synthetic invocation

`ROW10_TOY_REPO` names the invented `b1-example` repository in seat scratch. The baseline and change commits use the fixed author and committer date `2020-01-01T00:00:00+00:00`.

```sh
python3.13 -B scripts/compare_c1_protected_sources.py \
  --repo "$ROW10_TOY_REPO" \
  --w1-commit 27fe0a6883b930c21a26ef6753ef9d14138c81ff \
  --c1-commit e8e21699442907a392778129b4dca6e63e7ba6b0
```

The invented `invented-options.txt` and `joulewise/align/apple/rl176.py` are both listed, with exit 2 in either direction. Using the first commit for both inputs returns 0 and an empty file list.

## Lead invocation

Use the full commit IDs from the signed bindings and a local public-code repository.

```sh
python3.13 -B scripts/compare_c1_protected_sources.py \
  --repo "$ROW10_PUBLIC_CODE_REPO" \
  --w1-commit "$ROW10_W1_COMMIT" --c1-commit "$ROW10_C1_COMMIT"
```

Review all paths in `files_for_review`. Examine the flagged scorer and phase module diffs for protected binding changes and other changes in scientific meaning. [RL-182 register rows 3 and 7](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19924-L19929)

```sh
git --no-replace-objects -C "$ROW10_PUBLIC_CODE_REPO" diff --no-ext-diff --no-textconv \
  "$ROW10_W1_COMMIT" "$ROW10_C1_COMMIT" -- \
  joulewise/align/apple/rl176.py joulewise/align/apple/rl176_phases.py
```

## Protected bindings for source review

The locations below are in `joulewise/align/apple/rl176.py` at `82542232d`. Each one-byte fixture changes that file's Git blob ID and produces exit 2.

| Binding | Baseline line | Synthetic mutation |
| --- | ---: | --- |
| `S_SUPERIORITY_ALPHA` | 35 | Assignment |
| `_tail_test` | 85 | Parenthesized decorator |
| `_holm` | 178 | Inline comment |
| `_decode_design` | 194 | Body comment |
| `_decode_rows` | 200 | Final indented body comment |
| `_residual_scores` | 258 | Body literal |
| `_s_rank` | 300 | Signature default |
| `_q_energies` | 481 | Body literal |

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

## Row dispositions

| Obligation | Disposition |
| --- | --- |
| Row 10 byte freeze | Builder fixture evidence below. The lead owns the actual signed input identities and row disposition. |
| Protected source and scientific rules | The lead examines the complete file diff. A changed protected binding or scientific rule goes to Fable before rebind. |
| Prompt population | The signatory checks the private extraction, exact identifier set and hashes against the authoritative population and attests that there was no padded prompt or fourth timing term. |
| Anti-hindsight | The lead assembles rule changes since R1 with ruling IDs for Fable. [RLD:20265–20272](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20265-L20272) |
| Final acceptance | Integration-owner acceptance and Opus final-tree acceptance remain open. Opus owns merges. |

## Spec freeze and verification

| Stage | Commit | Tree |
| --- | --- | --- |
| Assigned and remote base | `82542232dbb7459b0320c37380925e9372afb7e8` | `865619340d39c4ae9198951d9112889ab7b69860` |
| Prior advisory comparator | `243be85ad14a8cc2db963e756c197dc7db5148d3` | `6ee355269f5226ce30cfae9c8ed418a94c42fe54` |
| Closure-only executable freeze | `7830fd8d27684a6844bfc5f6817f2f2d83b285a2` | `ecc98269222d6f7b8ae2837db8eda36825eec6a6` |
| Assessed B1 implementation | `b5c5fc010937b2c7ed86d0823c6ec9bd019db124` | `0caf5804f03b0ba9e9438526f521bbb6dae46a2d` |

Before implementation, five targeted tests produced seven failing assertions against the prior comparator. The previous CLI still required prompt arguments and listed runtime options. The frozen spec checks the B1-only help, equal inputs, all changed paths in both directions, missing-caller flags and metadata-only handling of source. The synthetic commands above returned the documented statuses and path lists on the assessed implementation.

The tests keep the byte regressions for root and transitive dependencies, a guarded import-time resource, phase rebinding, wiring edits, moved files, the simultaneous scorer edit and phase deletion, and both missing-caller directions. They also retain the protected-byte fixtures, including the decorated form-feed and namespace or callable mutations. The code and tests for P1 fingerprints, B2 outcomes and their reporting were removed. Prompt projection and per-binding interpretation now sit with the lead's source and prompt review.

The shard 6 inventory failure came from the deleted `isolated_identity` launcher at `isolated_identity:d16cb64193a201ee`. Removing the launcher addresses that inventory finding at its source. [Prior failing shard](https://github.com/mpmdw/JouleWise/actions/runs/44799288197/job/136507090647)

```sh
export TMPDIR=/Volumes/JW-EXT/scratch/pl-d-c1-protected-source-diff/build/tmp
export JW_B5_SYNTHETIC_ONLY=1
PYTHONPATH=tests:. python3.13 -B -m unittest \
  tests.test_host_command_sites.HostCommandSiteTests.test_tracked_command_sites_match_reviewed_allowlist
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration.ProtectedSourceComparisonTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_rl182_registration align.test_rl176
python3.13 -B scripts/compare_c1_protected_sources.py --help
git diff 82542232d..HEAD --check
```

The local tests run serially on invented inputs. Canonical whole-suite evidence comes from the hosted 21-job CI run on the published draft head.

## Prior audit ledger

| Review | VERIFIED HIGH | VERIFIED MED | VERIFIED LOW | Disposition |
| --- | ---: | ---: | ---: | --- |
| Astra 1 on v1 | 2 | 0 | 0 | Decorator boundary and namespace writes replayed as changed scorer bytes. |
| Astra 2 on v1 | 1 | 0 | 0 | Callable reassignment replayed as a changed scorer file. |
| Astra 3 on v1 | 1 | 0 | 0 | Cross-module phase reassignment returned the work to spec under §3. The phase change stays in the byte freeze. |
| Audit 4 on v2 | 2 | 2 | 0 | Root import, NaN helper mutation, and simultaneous edit or deletion remain file regressions. The isolated-interpreter inventory site was removed with its launcher. |
| Audit 5 on v3 | 1 | 2 | 0 | The skipped-case and unread-level findings concerned the deleted advisory checks. The guarded resource remains in the byte freeze. |

Earlier freezes, fixture commands and the audit dispositions are retained in the prior report. [Historical report at the prior head](https://github.com/mpmdw/JouleWise/blob/243be85ad14a8cc2db963e756c197dc7db5148d3/docs/run_reports/2026-11-19-c1-protected-source-diff.md) · [Pipeline §3](https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/docs/process/PIPELINE.md#L36-L68)
