```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "R1 is cured with byte-exact PR #276 issuance restoration and a regression; R2 needs a magistrate ruling on history-preserving landing versus forbidden artifact reissuance.",
  "workspace": {
    "base_requested": "5b45b415e95e5e03bdf4b8f0b0279267d140451a",
    "base_mode": "exact",
    "head_start": "5b45b415e95e5e03bdf4b8f0b0279267d140451a",
    "head_end": "5b45b415e95e5e03bdf4b8f0b0279267d140451a",
    "upstream_end": "04cd6e52e9d6ed2da369398bb448c5454f1917b3",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/paper/results-fill-registry.md",
    "docs/paper/round7/dg071-dg075-statistics.json",
    "docs/paper/round7/dg071-dg075-statistics.md",
    "docs/paper/round7/survival-map.md",
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/04-sol-fix-round-1-report.md",
    "scripts/issue_dg071_dg075_statistics.py",
    "scripts/paper_terms_lint.py",
    "tests/test_issue_dg071_dg075_statistics.py",
    "tests/test_paper_terms_lint.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/03-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 34 tests in 3.079s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 34 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/paper_terms_lint.py one-name --root docs/paper --exclude docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["0 one-name finding(s)"]},
      "expected": {"exit_code": 0, "tail_regex": "^0 one-name finding\\(s\\)$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "task_tmp_dir=$(mktemp -d); git show origin/main:docs/paper/results-fill-registry.md | rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 issuance' > \"$task_tmp_dir/main\"; rg '^\\| DG-0(71|75) |^\\| DG-071 / DG-075 issuance' docs/paper/results-fill-registry.md > \"$task_tmp_dir/head\"; cmp -s \"$task_tmp_dir/main\" \"$task_tmp_dir/head\"; git show origin/main:docs/paper/round7/survival-map.md | sed -n '275,279p' > \"$task_tmp_dir/main-survival\"; sed -n '275,279p' docs/paper/round7/survival-map.md > \"$task_tmp_dir/head-survival\"; cmp -s \"$task_tmp_dir/main-survival\" \"$task_tmp_dir/head-survival\"; test \"$(shasum -a 256 docs/paper/round7/dg071-dg075-statistics.json | cut -d' ' -f1)\" = 9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7; test \"$(shasum -a 256 docs/paper/round7/dg071-dg075-statistics.md | cut -d' ' -f1)\" = 041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b; echo R1_ISSUANCE_SURFACES_MATCH",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R1_ISSUANCE_SURFACES_MATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "^R1_ISSUANCE_SURFACES_MATCH$"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "task_tmp_dir=$(mktemp -d); R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out \"$task_tmp_dir/dg071-dg075-statistics.json\" >/dev/null; if cmp -s \"$task_tmp_dir/dg071-dg075-statistics.json\" docs/paper/round7/dg071-dg075-statistics.json && cmp -s \"$task_tmp_dir/dg071-dg075-statistics.md\" docs/paper/round7/dg071-dg075-statistics.md; then echo DG_ARTIFACTS_MATCH; else echo DG_ARTIFACTS_MISMATCH; exit 1; fi",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["DG_ARTIFACTS_MISMATCH"]},
      "expected": {"exit_code": 0, "tail_regex": "^DG_ARTIFACTS_MATCH$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check && echo DIFF_CHECK_CLEAN",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["DIFF_CHECK_CLEAN"]},
      "expected": {"exit_code": 0, "tail_regex": "^DIFF_CHECK_CLEAN$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R1 requires the PR #276 artifacts to remain byte-identical, but R2's current-branch replay derives producer.git_commit=375656a3 while the immutable artifact records 6b6deb2f; those requirements cannot both hold in this ancestry, and the supplied magistrate ruling only queues the gauntlet.",
      "needs": "Rule whether to rebuild/squash the landing from origin/main so the reverted producer hunk never enters final ancestry (recommended), or authorize reissuance/new pins or a provenance-contract change."
    }
  ]
}
```

## Change

R1 is cured. The issued registry introduction, DG-071/DG-075 rows, resolution row, and survival guidance are restored at `docs/paper/results-fill-registry.md:539`, `:646`, `:650`, `:911`, and `docs/paper/round7/survival-map.md:275`. Both issued artifacts again have PR #276's exact bytes. The producer and its focused expectations were restored to those bytes' source, so they are absent from the intended final-tree delta against `origin/main`.

The one-name lint now exempts only the two exact issued artifact paths at their reviewed SHA-256 values (`scripts/paper_terms_lint.py:135`, `:608`); a same-named mutable file is still scanned. The R1 counterfactual regression at `tests/test_paper_terms_lint.py:224` hashes both artifacts and the complete three-row registry extraction, and rejects the reopened `STOP_FILL` state.

R2 remains blocked by ancestry, not content. Fresh generation differs in exactly one field: `producer.git_commit` is `375656a3...` in this branch history and `6b6deb2f...` in the immutable artifact. A normal fix commit would only replace `375656a3...` with the new fix commit and cannot cure replay.

NEEDS_RULING: should the lead rebuild/squash the final-tree delta onto `origin/main`, excluding the restored producer/artifact/test paths so `6b6deb2f...` remains the producer's last-changing commit (recommended), or instead authorize either PR #276 artifact reissuance with new registry pins or a change to the last-changing-commit provenance contract? The R2 current-checkout replay regression is blocked on that choice.

## Verification notes

Only the two touched test modules ran, per preflight. V4 is the deliberate blocking reproduction; its generated JSON and Markdown differ from the immutable files only at the producer commit.

## Residual risk

A normal merge or fix commit on this ancestry preserves a later producer-path commit and therefore preserves R2. The lead must use the ruled landing method before rerunning the replay smoke.
