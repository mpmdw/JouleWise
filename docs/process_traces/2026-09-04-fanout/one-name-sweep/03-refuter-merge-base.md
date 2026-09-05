```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the refresh regresses origin/main's issued DG-071/DG-075 registry state and the checked-in DG artifacts do not replay at the reviewed head.",
  "workspace": {
    "base_requested": "5b45b415e95e5e03bdf4b8f0b0279267d140451a",
    "base_mode": "exact",
    "head_start": "5b45b415e95e5e03bdf4b8f0b0279267d140451a",
    "head_end": "5b45b415e95e5e03bdf4b8f0b0279267d140451a",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/03-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "location": "docs/paper/results-fill-registry.md:643,647,908; docs/paper/round7/survival-map.md:275; docs/paper/round7/dg071-dg075-statistics.json; docs/paper/round7/dg071-dg075-statistics.md",
        "text": "The refreshed tree does not preserve origin/main's reviewed DG-071/DG-075 issuance. It replaces the issued values, sample counts, two artifact SHA-256 pins, ISSUED statuses, and PR #276 resolution row with the older PENDING/STOP_FILL/VALUE_UNISSUED state; survival-map likewise says the artifacts have not issued. The branch also changes the issued artifact bytes: JSON 9a4fddde... -> c2cb5788... and Markdown 041a045e... -> 65afbb4d....",
        "counterfactual": "Landing this head would reopen already-issued rows as unresolved, remove their reviewed values and pins, and make survival guidance instruct omission despite PR #276 issuance. A correct refresh makes the extracted origin/main and worktree rows byte-identical before applying only an allowed one-name edit outside the immutable issuance surface."
      },
      {
        "id": "R2",
        "severity": "blocker",
        "location": "docs/paper/round7/dg071-dg075-statistics.json:28; docs/paper/round7/dg071-dg075-statistics.md:12",
        "text": "The checked-in artifacts name producer commit 6b6deb2f..., but the producer's last-changing commit at HEAD is 375656a3.... Fresh generation changes exactly that provenance field, so the implementation report's required post-commit reissue was not performed and its DG_ARTIFACTS_MATCH claim is false at this head.",
        "counterfactual": "A reader replaying the documented producer at the reviewed checkout gets different bytes, defeating the artifact's byte-exact provenance contract. Reissue after the producer commit and then reconcile the result with origin/main's immutable issued-artifact policy before review."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git branch --show-current && git merge-base origin/main HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["5b45b415e95e5e03bdf4b8f0b0279267d140451a", "feat/2026-09-04-fan-one-name-sweep", "849915bc1393a6c1cb962a4dc12b25c33dad1f74"]},
      "expected": {"exit_code": 0, "tail_regex": "5b45b415e95e5e03bdf4b8f0b0279267d140451a\\nfeat/2026-09-04-fan-one-name-sweep\\n[0-9a-f]{40}"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); allowed_re='^(docs/paper/(draft-v1\\.md|results-fill-registry\\.md|round7/(built-terms-lexicon\\.md|dg071-dg075-statistics\\.(json|md)|prefill-resolvability-projection\\.(json|md)|survival-map\\.md))|docs/process_traces/2026-09-04-fanout/one-name-sweep/(01-sol-report|02-merge-resolution)\\.md|scripts/(issue_dg071_dg075_statistics|paper_prefill_resolvability_projection|paper_terms_lint)\\.py|tests/test_(issue_dg071_dg075_statistics|paper_terms_lint)\\.py)$'; delta_unexpected=$(git diff --name-only \"$base\"..HEAD | rg -v \"$allowed_re\"); test -z \"$delta_unexpected\"; echo SCOPE_OK; test -z \"$(git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md PROJECT_STATUS.md AGENT_PLAN.md docs/process/state_kernel.json)\"; echo STATE_DOCS_NO_DELTA",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["SCOPE_OK", "STATE_DOCS_NO_DELTA"]},
      "expected": {"exit_code": 0, "tail_regex": "^SCOPE_OK\\nSTATE_DOCS_NO_DELTA$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "tmpdir=$(mktemp -d); git show origin/main:docs/paper/results-fill-registry.md | rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 issuance' > \"$tmpdir/main\"; rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 ratification' docs/paper/results-fill-registry.md > \"$tmpdir/head\"; cmp -s \"$tmpdir/main\" \"$tmpdir/head\" || { echo REGISTRY_ROWS_DIFFER; exit 1; }",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["REGISTRY_ROWS_DIFFER"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics tests.test_paper_terms_lint tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 35 tests in 3.440s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 35 tests in .*\\n\\nOK"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "python3 scripts/paper_terms_lint.py one-name --root docs/paper --exclude docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["0 one-name finding(s)"]},
      "expected": {"exit_code": 0, "tail_regex": "^0 one-name finding\\(s\\)$"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "task_tmp_dir=$(mktemp -d); R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out \"$task_tmp_dir/dg071-dg075-statistics.json\" >/dev/null; if cmp -s \"$task_tmp_dir/dg071-dg075-statistics.json\" docs/paper/round7/dg071-dg075-statistics.json && cmp -s \"$task_tmp_dir/dg071-dg075-statistics.md\" docs/paper/round7/dg071-dg075-statistics.md; then echo DG_ARTIFACTS_MATCH; else echo DG_ARTIFACTS_MISMATCH; exit 1; fi",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["DG_ARTIFACTS_MISMATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "^DG_ARTIFACTS_MATCH$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "task_tmp_dir=$(mktemp -d); python3 scripts/paper_terms_lint.py lexicon --draft docs/paper/draft-v1.md --out \"$task_tmp_dir/built-terms-lexicon.md\" >/dev/null; cmp \"$task_tmp_dir/built-terms-lexicon.md\" docs/paper/round7/built-terms-lexicon.md; python3 scripts/paper_prefill_resolvability_projection.py --corpus-root /Users/edr/code/JouleWise --repo-root /Users/edr/code/JouleWise --out \"$task_tmp_dir/prefill.json\" >/dev/null; cmp \"$task_tmp_dir/prefill.json\" docs/paper/round7/prefill-resolvability-projection.json; echo GENERATED_ARTIFACTS_MATCH",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["GENERATED_ARTIFACTS_MATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "^GENERATED_ARTIFACTS_MATCH$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --check \"$base\"..HEAD && echo DIFF_CHECK_CLEAN",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["DIFF_CHECK_CLEAN"]},
      "expected": {"exit_code": 0, "tail_regex": "^DIFF_CHECK_CLEAN$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No previous one-name-sweep refuter verdict exists in the worktree, origin/main tree, or reachable path history; this round therefore reran the prescribed checks independently.",
      "needs": "Provide the prior verdict only if a wording-by-wording round comparison is required."
    }
  ]
}
```

## Findings

- **R1 — blocker:** The conflict refresh did not keep origin/main's DG-071/DG-075 issuance. Current rows are `PENDING` / `STOP_FILL` / `VALUE_UNISSUED`; origin/main has `n = 406` and `n = 405`, medians/IQRs, JSON and Markdown pins, `ISSUED`, and `ISSUED_ARTIFACT (PR #276)`. The survival map also reverted from “issued by” to “until ... artifacts issue.” The issued artifact files themselves are not byte-identical to main.
- **R2 — blocker:** DG replay changes producer commit `6b6deb2f...` to the actual last-changing commit `375656a3...`. Both JSON and Markdown therefore fail byte comparison at HEAD.

## Evidence

The exact requested HEAD and branch gate passed. The review delta was `git diff $(git merge-base origin/main HEAD)..HEAD`, with merge base `849915bc1393a6c1cb962a4dc12b25c33dad1f74`. Its 15 paths are the 14 paths declared by `01-sol-report.md` plus `02-merge-resolution.md`; `RUN_STATE.md`, `TASK_QUEUE.md`, `PROJECT_STATUS.md`, `AGENT_PLAN.md`, and `docs/process/state_kernel.json` have no delta.

Origin/main preservation was checked by extracting and byte-diffing the governed rows rather than reviewing a direct origin/main whole-tree diff. The diagnostic census rows remain exact (`50`, `37`, `50`, `13`, `37`, `13`), and the registry's census-summary lines match. DG-071/DG-075 rows, statuses, pins, and the issuance-resolution row do not. Artifact hashes are:

| Artifact | origin/main | HEAD |
|---|---|---|
| JSON | `9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7` | `c2cb5788d18615ff78a2aec03247c41f431c9667e70b105b265c0e2188f4870a` |
| Markdown | `041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b` | `65afbb4d8a0ff0ded5664883355c702683711941fa3d48b81d64187825d3254a` |

Rename enumeration over the mission delta:

| Object | Old name(s) | Canonical name | Surfaces |
|---|---|---|---|
| Power sample | `sampler record(s)` | `sampling record(s)` | draft, DG producer/artifacts, projection, focused expectations |
| Covered interval | `support interval(s)`, possessive “record's support” | `record support(s)` | draft, projection, lexicon |
| Positive-overlap cardinality | `overlapping-record count`, `two-overlap count`, `three-overlap counts`, prose “rule is a count” | `overlap count`, qualified as “of two/three” | draft, DG-072 label, projection producer/artifacts, survival map, lexicon |

Apart from the enforcement command and tests, the rename hunks preserve calculations and numerical payloads. Normalizing only the renamed DG text and `producer.script_sha256` makes the current DG JSON's inputs, values, and counts byte-identical to origin/main. That digest exception is material: the requested no-digest-change condition fails, and the changed artifacts are no longer the immutable files pinned by main.

The only authorized test modules touched by or explicitly required for this landing ran: 35 tests passed. The first-use ledger and terms-lint regressions are included in that run; the standalone one-name lint reports zero findings. The lexicon and prefill projection regenerate byte-identically. No whole-suite run was attempted, per preflight.

## Residual risk

The previous-round verdict was not present in reachable repository state, so this report cannot compare its wording or finding IDs. The current blocker evidence is independently reproducible and does not depend on that artifact.
