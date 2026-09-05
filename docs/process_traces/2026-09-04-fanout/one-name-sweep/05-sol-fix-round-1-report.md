```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Restored every producer, generated artifact, and focused test path to current origin/main bytes; the final tree delta is three pure terminology edits plus trace files, with branch-head DG replay deferred to the magistrate-owned merge verification.",
  "workspace": {
    "base_requested": "3153a686a3b99b18e447c2894de7d1cffe222633",
    "base_mode": "exact",
    "head_start": "3153a686a3b99b18e447c2894de7d1cffe222633",
    "head_end": "3153a686a3b99b18e447c2894de7d1cffe222633",
    "upstream_end": "36e7d539c795cf8a60f2bace8d640ff81499c336",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/paper/results-fill-registry.md",
    "docs/paper/round7/built-terms-lexicon.md",
    "docs/paper/round7/prefill-resolvability-projection.json",
    "docs/paper/round7/prefill-resolvability-projection.md",
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/05-sol-fix-round-1-report.md",
    "scripts/paper_prefill_resolvability_projection.py",
    "scripts/paper_terms_lint.py",
    "tests/test_paper_terms_lint.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics tests.test_paper_terms_lint tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 33 tests in 3.079s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 33 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "for p in docs/paper/round7/built-terms-lexicon.md docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md docs/paper/round7/prefill-resolvability-projection.json docs/paper/round7/prefill-resolvability-projection.md scripts/issue_dg071_dg075_statistics.py scripts/paper_prefill_resolvability_projection.py scripts/paper_terms_lint.py tests/test_issue_dg071_dg075_statistics.py tests/test_paper_terms_lint.py; do git diff --quiet origin/main -- \"$p\" || exit 1; done; echo RESTORED_PATHS_MATCH_ORIGIN_MAIN",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["RESTORED_PATHS_MATCH_ORIGIN_MAIN"]},
      "expected": {"exit_code": 0, "tail_regex": "^RESTORED_PATHS_MATCH_ORIGIN_MAIN$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "task_tmp_dir=$(mktemp -d); git show origin/main:docs/paper/results-fill-registry.md | rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 issuance' > \"$task_tmp_dir/main-rows\"; rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 issuance' docs/paper/results-fill-registry.md > \"$task_tmp_dir/worktree-rows\"; cmp \"$task_tmp_dir/main-rows\" \"$task_tmp_dir/worktree-rows\"; for p in docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md scripts/issue_dg071_dg075_statistics.py; do git diff --quiet origin/main -- \"$p\" || exit 1; done; echo R1_COUNTERFACTUAL_CLOSED",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R1_COUNTERFACTUAL_CLOSED"]},
      "expected": {"exit_code": 0, "tail_regex": "^R1_COUNTERFACTUAL_CLOSED$"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "task_tmp_dir=$(mktemp -d); R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out \"$task_tmp_dir/dg071-dg075-statistics.json\" >/dev/null; if cmp -s \"$task_tmp_dir/dg071-dg075-statistics.json\" docs/paper/round7/dg071-dg075-statistics.json && cmp -s \"$task_tmp_dir/dg071-dg075-statistics.md\" docs/paper/round7/dg071-dg075-statistics.md; then echo R2_REPLAY_MATCH; else echo R2_REPLAY_MISMATCH; issued_commit=$(rg -o '\"git_commit\": \"[0-9a-f]+\"' docs/paper/round7/dg071-dg075-statistics.json | rg -o '[0-9a-f]{40}'); generated_commit=$(rg -o '\"git_commit\": \"[0-9a-f]+\"' \"$task_tmp_dir/dg071-dg075-statistics.json\" | rg -o '[0-9a-f]{40}'); echo \"issued_commit=$issued_commit\"; echo \"generated_commit=$generated_commit\"; exit 1; fi",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["R2_REPLAY_MISMATCH", "issued_commit=6b6deb2f8f9bbe88b604b18d544856d6ae4e0013", "generated_commit=375656a384e5583317d1f33878bd559605eaed02"]},
      "expected": {"exit_code": 0, "tail_regex": "^R2_REPLAY_MATCH$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check && echo DIFF_CHECK_CLEAN",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["DIFF_CHECK_CLEAN"]},
      "expected": {"exit_code": 0, "tail_regex": "^DIFF_CHECK_CLEAN$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "changed=$(git diff --name-only origin/main -- docs/paper/draft-v1.md docs/paper/results-fill-registry.md docs/paper/round7/built-terms-lexicon.md docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md docs/paper/round7/prefill-resolvability-projection.json docs/paper/round7/prefill-resolvability-projection.md docs/paper/round7/survival-map.md scripts/issue_dg071_dg075_statistics.py scripts/paper_prefill_resolvability_projection.py scripts/paper_terms_lint.py tests/test_issue_dg071_dg075_statistics.py tests/test_paper_terms_lint.py); test \"$changed\" = $'docs/paper/draft-v1.md\\ndocs/paper/results-fill-registry.md\\ndocs/paper/round7/survival-map.md'; echo PURE_RENAME_PATHSET_ONLY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PURE_RENAME_PATHSET_ONLY"]},
      "expected": {"exit_code": 0, "tail_regex": "^PURE_RENAME_PATHSET_ONLY$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The ruled tree-level cure is complete, but replay at the unmerged branch head still traverses historical producer commit 375656a3; only the final merge onto main can prove that path-history simplification retains origin/main's 6b6deb2f provenance.",
      "needs": "Magistrate: commit and merge the pure final delta as ruled, then rerun V4 from the merged main checkout; if it does not pass byte-for-byte, do not land and issue a new ruling."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The required git checkout origin/main -- <paths> command could not create the linked-worktree index.lock because the parent gitdir is read-only in this sandbox; a git-archive copy restored the same bytes, and V2 proves exact equality.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main is 36e7d539 at report time, newer than 04cd6e52 recorded by the preceding seat report; restoration and comparisons used the current ref.",
      "needs": ""
    }
  ]
}
```

## Change

Applied the magistrate's history-preserving tree cure. These paths are now byte-identical to current `origin/main`: `docs/paper/round7/built-terms-lexicon.md`, both `dg071-dg075-statistics` artifacts, both `prefill-resolvability-projection` artifacts, all three producer scripts, and both focused test modules. Restoring the tests removes the non-rename lint/exemption behavior, leaving only authored terminology edits at `docs/paper/draft-v1.md:249,256`, `docs/paper/results-fill-registry.md:647`, and `docs/paper/round7/survival-map.md:274` outside the trace directory.

| Finding | Cure | File:line / regression |
|---|---|---|
| R1 | Preserved all issued DG-071/DG-075 values, statuses, pins, and artifact bytes; retained only the DG-072 terminology edit outside that immutable surface. | `docs/paper/results-fill-registry.md:647`; V3 replays the refuter's reopened-`STOP_FILL` counterfactual by requiring the complete three-row extraction and issued bytes to equal `origin/main`. |
| R2 | Removed every DG producer/artifact path from the final tree delta. | `scripts/issue_dg071_dg075_statistics.py:1`; V2 is the ruled tree regression. V4 records the remaining branch-history replay condition for mandatory post-merge verification. |

## Verification notes

V4 cannot pass before the magistrate-owned final merge: the restored script is byte-identical to main, but `git log -1 -- <producer>` at this branch head still resolves the historical one-name commit. No whole-suite run was made, per preflight.

## Residual risk

Do not treat the branch head itself as a byte-replayable DG issuance checkout. Acceptance becomes ready only if V4 passes from the merged main tree.
