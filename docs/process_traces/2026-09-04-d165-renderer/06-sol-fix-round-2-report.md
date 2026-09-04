# D165-OUTCOME-RENDERER-01 — Sol fix round 2

Date: 2026-09-04  
Seat: Sol xhigh implementation  
Ruling: `docs/process_traces/2026-09-04-paper-i/07-magistrate-rulings-addendum.md`,
REPLACED R4-F1  
Base/head at intake: `93896ed89f5a08c680fa5f173cbe2051ef57e5e5`  
Branch: `feat/2026-09-04-d165-outcome-renderer`

## Outcome

Replaced the caller-constructible `BeforeComparisonValidationResult` and raw
byte-list channel with a path-and-expected-digest boundary. A whole-window
attempt now supplies the runs root and separate path/digest pairs for the
authoritative `campaign_log.jsonl`, the standalone
`joulewise.idle_admission_whole_window_verdict.v1` row, the prospective
analysis manifest, and its plan tree. The renderer reads regular non-symlink
files, requires the standalone row's writer-exact bytes to occur exactly once
in the bound log, and reopens every caller-supplied source after validator
replay.

`validate_prospective_analysis_manifest_v3` authenticates the prospective
manifest and plan-tree binding. The renderer then derives all frozen members
from the two contrasts, reopens their digest-bound configs, and requires arm A
to be the exact Qwen3-1.7B `_v5` name/revision/family, arm B to be the exact
Qwen3-8B `_v5` identity, and every config to bind its manifest phase. The
whole-window row and its evaluation basis must each cover the exact prospective
member census once. Every authenticated source campaign manifest must bind the
same prospective manifest ID/digest, run IDs, and bundle IDs. Finally,
`whole_window_refusal_reasons` is replayed with the exact census,
evaluation-basis digest, and consumption-semantics ID.

The existing whole-window validator still returns one refusal-code tuple for
both an authentic failed-admission row and a provenance/structure failure. It
does not expose the ruled `source_valid` versus `admission` distinction.
Therefore this round deliberately renders both OB-01 and OR-01 as `STOP_FILL`
for every whole-window stop after completing the evidence-chain checks; no
receipt schema was invented. `WHOLE-WINDOW-STOP-RECEIPT-01` remains the queued
producer/API mission required before the registered whole-window sentence can
issue.

A missing `joulewise.claim_verdicts.v1` file is now represented only by the
absence of positive before-comparison evidence and returns `STOP_FILL`.
`docs/paper/results-fill-registry.md` preserves the exact registered future
sentence but records that DS-32/PG-08's “not evaluated — required ... verdict
absent” text can issue only after the queued
`CLAIM-NONISSUANCE-RECEIPT-01` supplies a governed positive artifact and
validator.

## Retained fix-round-1 cures

| Cure | Round-2 state |
|---|---|
| B1 registered bytes | OB-01 and every close-out OR-01 string remain exact registry oracles. The two narrowed before cases now compare to separately registered current `STOP_FILL` oracles; the future sentence bytes remain registered. |
| F2 stage order | No precedence input exists. A structurally bound before-comparison stop wins and remains `STOP_FILL`; an authenticated later close-out reason stays secondary non-paper metadata. |
| F3 close-out coverage | Source and census top-level refusals still render their registered strings, including `none recorded` where no ratio row is refused. |
| F4 `_v5` identity | Finalized close-out and prospective before lanes both require the exact two Qwen3 names/revisions/family before any fill. Wrong identity returns `identity_not_v5`. |

## RED / GREEN evidence

RED after installing the replacement acceptance contract, before production
changes:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome
Ran 8 tests in 2.546s
FAILED (failures=3, errors=9)
```

The failures were the missing current registry oracles, the still-exported
caller result/byte channel, and the absent path arguments.

Final focused acceptance:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome
Ran 8 tests in 2.992s
OK
```

Final permitted renderer/close-out/whole-window-validator suite:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome tests.test_d165_dominance_closeout tests.test_whole_window tests.test_whole_window_selection
Ran 168 tests in 148.574s
OK
```

Final permitted registry checks:

```text
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
Ran 13 tests in 2.986s
OK
```

The repository-wide suite was not run because the brief's preflight rule
exhaustively limited test modules.

## Mutation proofs

The harness patched one production or registry-read site at a time in memory
and ran only the owning `tests.test_results_fill_outcome` method. It wrote no
repository file.

| Guard | Counterfactual | Observed |
|---|---|---|
| B1 | Append one byte to the `branch_b` registry oracle at read time. | `B1_MUTANT_KILLED failures=1 errors=0` |
| F1 exact-once | Make every campaign log pass the exact-once check. | `F1_EXACT_ONCE_MUTANT_KILLED failures=2 errors=0` |
| F1 manifest binding | Accept every source-campaign-manifest/prospective join. | `F1_MANIFEST_BINDING_MUTANT_KILLED failures=1 errors=0` |
| F1 API ambiguity | Publish caller prose after an undifferentiated whole-window result. | `F1_AMBIGUOUS_STOP_MUTANT_KILLED failures=1 errors=0` |
| F1 old channel | Restore a `before_comparison_source_bytes` parameter. | `F1_OLD_CHANNEL_MUTANT_KILLED failures=1 errors=0` |
| F2 | Drop the authenticated close-out reason from secondary metadata when the before stage wins. | `F2_MUTANT_KILLED failures=0 errors=1` (missing required key) |
| F3 | Require a refused ratio record before rendering a top-level close-out source refusal. | `F3_MUTANT_KILLED failures=1 errors=0` |
| F4 | Continue with an empty identity map after `_v5` identity rejection. | `F4_MUTANT_KILLED failures=1 errors=0` |

## Clause map delta

| R4-F1 proposition | Production/registry site | Biting assertion |
|---|---|---|
| Only paths plus expected digests cross the before boundary; no caller result object/normalized bytes | `joulewise/results_fill_outcome.py:154,400,658` | `tests/test_results_fill_outcome.py:457,599` |
| Real prospective validator and plan tree bind exact `_v5` models/phases/member census | `joulewise/results_fill_outcome.py:242` | `tests/test_results_fill_outcome.py:457,497` |
| Standalone row bytes occur exactly once in bound `campaign_log.jsonl` | `joulewise/results_fill_outcome.py:228,400` | duplicate/missing cases in `tests/test_results_fill_outcome.py:497` |
| Campaign manifests and evaluation basis bind the same prospective census and semantics | `joulewise/results_fill_outcome.py:330,400` | census/manifest-rebind cases in `tests/test_results_fill_outcome.py:497` |
| Existing whole-window API ambiguity never emits professor-facing bytes | `joulewise/results_fill_outcome.py:568,708` | `tests/test_results_fill_outcome.py:457` |
| Missing claim verdict is non-issuance; future absence sentence requires a governed artifact | `docs/paper/results-fill-registry.md:917` | `before_comparison_absent_verdict.json` in the B1 table test |

## Scope and handoff

All writes are within the exhaustive allowlist. No commit was created. The
untracked `05-consult-sol-before-comparison-authority.md` existed at intake and
was read in full but not modified. The next exact step is independent delta
re-audit of this round; whole-window prose issuance remains blocked on
`WHOLE-WINDOW-STOP-RECEIPT-01`, and verdict-absence prose remains blocked on
`CLAIM-NONISSUANCE-RECEIPT-01`.
