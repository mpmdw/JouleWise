# C1 round-two proof index handoff

19 November 2026 · Row 13 · Tier 0 · sol_build · xhigh · cap 1

The [round-two rehearsal index][index] gives the integration owner independent expectations, required fixture variants and exact evidence slots. Final producer executions and operational acceptance are **OPEN**. Item 471 leaves W1 at `b2e01464d6d4fbf2901ff4d4154df9455104a12a`, with promotion reserved to the lead.

## Public pins and scope

| Reference | Exact binding |
|---|---|
| Dispatch anchor and cited RLD | `c39ec79931db9da0155cc39623ca9f581e4aebb7`, tree `449899f0a049fa13a6f6bba703753e1b0cb4ad4b`. This was also the live audit base at intake. |
| Reviewed authoring base | `origin/audit/2026-11-10-fable` advanced by two commits to `ea2f55318cbc9806be5570a2b21b362ad12b1db4`, tree `066c9d5bb0a274815ca9ccb986e2f69369a93671`. Reviewed the delta from the dispatch anchor before fast-forwarding the assigned local branch. |
| Draft branch and target | `align/2026-11-19-c1-round-two-proof-index` into `audit/2026-11-10-fable`. Clean branch at the anchor at intake. No assigned remote ref or PR existed, so no fast-forward was needed. |
| W1 round-two contract | `b2e01464d6d4fbf2901ff4d4154df9455104a12a`, spec blob `b2a0fe625a78f03f154b3c7e39cc9a624e1d7760`. P4 text at the same pin, blob `9a19e54b4741c60cc61046f6ae47397a8eca197b`. [R2][r2] |
| Process lane | `origin/main` at `366dcf9c8dc8622e07a90714d9033dbfbf5fa842`, PIPELINE lines 10–18 and 36–64. [Pipeline][pipeline] |
| PR #852 component | `refs/pull/852/head` over HTTPS at `b3519bf0cd791df81264c4374b99f5098344196f`, tree `f8463e791da0a8a8bfe0a021070e2b048976ef39`. Its RL-187 report cites ruling pin `9fffb60141b3dbf6cbff8504dd415e4a806689df`. [RL-187 component report][component] · [Owner requests][owners] |
| Amended inventory / scorer tests | AM at `82542232dbb7459b0320c37380925e9372afb7e8`. PR #813 synthetic module at `6093a7454d181c87ae6fcb2e3d30c25fb1e97cce`. Both are reference inputs to the index. |
| Caller contrast | PR #836 `7c6c24cc5067ca7ea818ab4a1efdb640a3dd003a`. The stated captured eligible/no-S test expects 1 and no report, so the final four-world contrast still needs a caller that emits paired reports. [Owner request][owners] |

Mission M0 found no active stop card. This is the dispatched synthetic [AGENT] documentation row. The worktree and seat carried the setup and verification. The cited C1-EVIDENCE, COMPARATOR-SPEC and OUTPUT-FAMILY-LEDGER notes supplied indexing leads, checked against the public contract and rulings. CI has no dependency on those scratch notes. The draft has two Markdown additions. The lead's signed bytes, actual records, RUN_STATE and TASK_QUEUE remain outside the diff.

The advance added RL-190 after the end of the pinned log and a separate stability kit index. Reviewed the ruling's scope and amendments and checked the kit-index path and change metadata. RL-190 did not change the comparator's §2 or the RL-21 cases. It retains a Claude-family executing review for the RL-176 scoring gate. The advance changes no workflow, classifier, protocol or round-two spec path. [RL-190 review scope][rl190]

## Executed evidence

### PR #852 synthetic component

Fetched the public pull ref into a fresh partial checkout under this seat's `tmp/`. The sparse worktree materialized the two synthetic modules and their bundled fixture support, comparator source, bars and expected synthetic JSONL only. Used CPython **3.13.18**, Apple Git **2.50.1**, GitHub CLI **2.97.0**.

```sh
git status --short --branch
git ls-remote origin refs/heads/align/2026-11-19-c1-round-two-proof-index \
  refs/heads/audit/2026-11-10-fable refs/heads/main refs/pull/852/head
git fetch --no-tags origin refs/heads/audit/2026-11-10-fable refs/heads/main refs/pull/852/head
git show origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md
```

In the fresh seat-only checkout, where `checkout_dir` is the new directory:

```sh
git -C "$checkout_dir" init -q
git -C "$checkout_dir" remote add origin https://github.com/mpmdw/JouleWise.git
git -C "$checkout_dir" config remote.origin.promisor true
git -C "$checkout_dir" config remote.origin.partialclonefilter blob:none
git -C "$checkout_dir" fetch --depth=1 --filter=blob:none --no-tags origin refs/pull/852/head
printf '%s\n' '/tests/v4_release/' '/scripts/compare_v4_output_census.py' \
  '/configs/analysis/v4/c1_comparator_bars.json' \
  '/docs/run_reports/2026-11-18-c1-comparator-synthetic-index.jsonl' |
  git -C "$checkout_dir" sparse-checkout set --no-cone --stdin
git -C "$checkout_dir" checkout --detach FETCH_HEAD
cd "$checkout_dir"
test "$(git rev-parse HEAD)" = b3519bf0cd791df81264c4374b99f5098344196f
python3.13 --version
PYTHONPATH=tests:. python3.13 -B -m unittest v4_release.test_claim_output_mutations v4_release.test_rl187_comparator
set -o pipefail
PYTHONPATH=tests:. python3.13 -B -m v4_release.test_claim_output_mutations --evidence-index |
  cmp docs/run_reports/2026-11-18-c1-comparator-synthetic-index.jsonl -
shasum -a 256 docs/run_reports/2026-11-18-c1-comparator-synthetic-index.jsonl
```

| Check | Result |
|---|---|
| Both named modules | PASS, exit 0, 15 tests in 0.789 s. |
| Existing byte comparison | PASS, pipe exit 0 with no cmp output. JSONL SHA-256 `c43d9da366d3f63677cfeb30be5c4ed9475088112f7ea3a1820816e93e718bff`. Two headers and 142 result rows including the two intact controls. Full binds 27 L / 26 R locations and prefix binds 30 L / 29 R. |
| Additional three-copy check | PASS on the invented full and prefix cards. The bound clean, three-copy mutant and restored exits were 0, 2, 0. The three findings were claim state on L, L, R. The unbound mutant returned 0 in both modes. |
| Owner-supplied sentence template | OPEN. The adapter owners owe the actual full/prefix template literals, figure positions, occurrence map and independent expected text at accepted pins. |
| PR #852 hosted reference | Historical exact-head CI succeeded, including 12 Python 3.13 shards. This is separate from the evidence-index draft's CI. [PR #852 CI][ci852] |

The supplemental replay used `PYTHONPATH=tests:. python3.13 -B -` in the same isolated checkout with this input:

```python
from dataclasses import replace
from v4_release import test_claim_output_mutations as suite

for prefix in (False, True):
    census = suite.synthetic_census(prefix)
    key = suite.cmp.Key("claim", (), "interpretation")
    bound = replace(census, rules={
        **census.rules, key: replace(census.rules[key], expected="fixture-text"),
    })
    original = suite.synthetic_reports(prefix)
    assert suite.compare(bound, original).exit_code == 0
    left, right = suite.synthetic_reports(prefix)
    for name in left["claim"]:
        left["claim"][name] = "fixture-wrong"
    right["decision"]["text"] = "fixture-wrong"
    unbound = suite.compare(census, (left, right))
    outcome = suite.compare(bound, (left, right))
    restore = suite.compare(bound, original)
    assert (unbound.exit_code, outcome.exit_code, restore.exit_code) == (0, 2, 0)
    assert tuple((f.family, f.side, f.code) for f in outcome.findings) == (
        ("claim", "L", "state"), ("claim", "L", "state"), ("claim", "R", "state"),
    )
```

### Index and docs range

Checked 152 unique case IDs and every case table for unique IDs, independent oracles and either exact component evidence or named owner inputs. Checked all nine RL-21 entries, the 12 full/prefix rows and separate attachment fields, 19 C/T identities plus W1, four RL-185 worlds, and all B7, claim, coverage and owner-handoff rows. Reconstructed every B5 placement from the full pair tags and registered hash law. Verified K's cited example tails by independent binomial-difference convolution in `fractions.Fraction` and the RL-185 benign witness by the registered assignment count. The K and RL-185 numbers are oracle expectations for future runs.

```sh
git diff --check ea2f55318cbc9806be5570a2b21b362ad12b1db4 HEAD
git diff --name-status ea2f55318cbc9806be5570a2b21b362ad12b1db4 HEAD
git show ea2f55318cbc9806be5570a2b21b362ad12b1db4:scripts/ci_docs_only.sh |
  bash -s -- ea2f55318cbc9806be5570a2b21b362ad12b1db4 "$(git rev-parse HEAD)"
```

The base classifier returned exit 0 for the two-file docs-only range. The two Markdown additions require no local Python code suite. The named component replay above is executed separately. Hosted PR CI supplies the exact-head build, fences, wheel and required-context result. The draft PR checks view records the run against the published head.

## Condition-13 metadata comparison

Compared each path using `git rev-parse --verify -q "$rev:$file_name"` at W1, the audit base and the authoring head. The audit base already lacks all ten paths. The draft keeps that inherited state and adds no replacement blob. This branch leaves the W1 line at the item-471 pin.

| Path | W1 at b2e01464d · blob ID | Audit base and draft |
|---|---|---|
| `scripts/align_r1_rehearsal.py` | `33c6876e6a988bee93fc49a0ba554f7c2c3bf277` | Absent at both |
| `scripts/align_r1_runtime.py` | `96b249a6eb44c4de2887aeeadff089c3040d8cfa` | Absent at both |
| `joulewise/align/apple/r1_runtime.py` | `261761f1a5e39220614b74d53d125022278502db` | Absent at both |
| `joulewise/align/apple/r1_runtime_contract.py` | `1ef822bee6d3b4951ad24cd1991ea31741d30161` | Absent at both |
| `joulewise/align/apple/smc_enumeration.py` | `8a1a96dcb10ebb16809717af15918d5366b0d31c` | Absent at both |
| `joulewise/align/apple/thermal_gates.py` | `b46769d70df02de09dbeb07e4c0020c472477dcb` | Absent at both |
| `configs/align/v4/r1_runtime.json` | `bf8479b26774b4d6a7bb3d44c6e2d662ddeb199e` | Absent at both |
| `joulewise/align/apple/r1_phase_table.py` | `e412bb4389aae4e4239b47842512db178d4b53a2` | Absent at both |
| `joulewise/align/apple/workload.py` | `ff30c29178ad9ccceab96140c569b8f14afa16e9` | Absent at both |
| `joulewise/align/apple/thermal.py` | `e7cbd6808c5a407524e3a85254090a46c33fa910` | Absent at both |

`RUN_STATE.md` and `TASK_QUEUE.md` are respectively blobs `71f2c09b27e0408bcdc7624a1059982a7a3c283e` and `708886bdefd6f727fe7ed3c6e199d22c0f5fac59` on the audit base and draft.

## Outstanding inputs and next run

1. The integration owner names the successor, exporter, release driver, independent build pair, comparator, bars, exact synthetic cut IDs and the accepted invocation or paired output identities.
2. Each adapter owner supplies its schema descriptor and independently authored truth cards, including W1/desk applicability, sentence templates and actual AUC marker/reasons/folds. The series owner supplies committed replay and the four finalized RL-185 worlds. The evaluator owner and lead attach the frozen evaluator, authorization and seal bindings.
3. The existing comparator lane runs the intact comparisons, occurrence-by-occurrence mutations and clean restores with the owner package. It sends blinded verdicts and indices to Opus cold review. The lead retains final acceptance and any later retarget.

**NEEDS_SPEC.** This indexing run exposed no new confirmed missing rule. The [index][index] records the exact clause, synthetic witness and decision owner for conditional escalation on the committed held-window relation, A9 no-capture reason/conflict, unmapped governed leaf or population, and impossible rail-only layout. Producer runs await their named owner inputs.

[index]: ../research-audits/2026-11-10-fable/evidence/align-v4-campaign/c1-prearm/ROUND2-REHEARSAL-INDEX.md
[r2]: https://github.com/mpmdw/JouleWise/blob/b2e01464d6d4fbf2901ff4d4154df9455104a12a/docs/align/v4/CLAIM-CONTRACT-B-ROUND2-SPEC.md
[pipeline]: https://github.com/mpmdw/JouleWise/blob/366dcf9c8dc8622e07a90714d9033dbfbf5fa842/docs/process/PIPELINE.md
[component]: https://github.com/mpmdw/JouleWise/blob/b3519bf0cd791df81264c4374b99f5098344196f/docs/run_reports/2026-11-18-c1-comparator-rl187.md
[owners]: https://github.com/mpmdw/JouleWise/blob/b3519bf0cd791df81264c4374b99f5098344196f/docs/run_reports/2026-11-18-c1-comparator-owner-inputs.md
[ci852]: https://github.com/mpmdw/JouleWise/actions/runs/44424199343
[rl190]: https://github.com/mpmdw/JouleWise/blob/ea2f55318cbc9806be5570a2b21b362ad12b1db4/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22537-L22564
