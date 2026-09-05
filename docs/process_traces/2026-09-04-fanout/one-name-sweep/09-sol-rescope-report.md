```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the adopted asymmetric DG replay proof, preserved the issued v2 artifacts and producer, and kept the one-name mission scoped to mutable authored terminology.",
  "workspace": {
    "base_requested": "cc4309a0c931442b801b381f5de12bfc2e8e68d4",
    "base_mode": "exact",
    "head_start": "cc4309a0c931442b801b381f5de12bfc2e8e68d4",
    "head_end": "cc4309a0c931442b801b381f5de12bfc2e8e68d4",
    "upstream_end": "a1184ccae2f62535b53c8c6e09c1bac37ff7f795",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/09-sol-rescope-report.md",
    "tests/test_issue_dg071_dg075_statistics.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "test \"$(git rev-parse HEAD)\" = cc4309a0c931442b801b381f5de12bfc2e8e68d4; test \"$(git branch --show-current)\" = feat/2026-09-04-fan-one-name-sweep; echo EXACT_BASE_AND_BRANCH",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["EXACT_BASE_AND_BRANCH"]},
      "expected": {"exit_code": 0, "tail_regex": "^EXACT_BASE_AND_BRANCH$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "task_tmp_dir=$(mktemp -d)\nR7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out \"$task_tmp_dir/replayed.json\" >/dev/null\nISSUED=docs/paper/round7/dg071-dg075-statistics.json REPLAYED=\"$task_tmp_dir/replayed.json\" python3 -c 'import json,os; from pathlib import Path; issued=json.loads(Path(os.environ[\"ISSUED\"]).read_text()); replayed=json.loads(Path(os.environ[\"REPLAYED\"]).read_text()); old=issued[\"producer\"][\"git_commit\"]; new=replayed[\"producer\"][\"git_commit\"]; assert old != new; issued[\"producer\"][\"git_commit\"]=new; assert issued == replayed; print(f\"COUNTERFACTUAL_RED mismatch_only=producer.git_commit issued={old} current={new}\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["COUNTERFACTUAL_RED mismatch_only=producer.git_commit issued=6b6deb2f8f9bbe88b604b18d544856d6ae4e0013 current=94af46458aab6bb8597f2c4564f9b6d1e0d6975e"]},
      "expected": {"exit_code": 0, "tail_regex": "^COUNTERFACTUAL_RED mismatch_only=producer\\.git_commit issued=6b6deb2f[0-9a-f]{32} current=94af4645[0-9a-f]{32}$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics.Dg071Dg075StatisticsTests.test_change_then_exact_restore_replays_with_divergence_warning",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.297s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in .*\\n\\nOK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 28 tests in 1.461s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 28 tests in .*\\n\\nOK"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json\nfrom pathlib import Path\nimport tempfile\nimport warnings\nfrom tests.test_issue_dg071_dg075_statistics import ROOT, _verify_asymmetric_replay\nissued = ROOT / 'docs/paper/round7/dg071-dg075-statistics.json'\nbundle = Path('/Users/edr/code/JouleWise') / json.loads(issued.read_text())['input_bundle']['path']\nwith tempfile.TemporaryDirectory() as directory:\n    with warnings.catch_warnings(record=True) as caught:\n        warnings.simplefilter('always')\n        record = _verify_asymmetric_replay(checkout=ROOT, bundle=bundle, issued_json=issued, replay_json=Path(directory) / 'replayed.json')\n    assert len(caught) == 1\n    print('REAL_V2_ASYMMETRIC_REPLAY_PASS')\n    print(f'warning={caught[0].message}')\n    print(f'record={json.dumps(record, sort_keys=True)}')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["REAL_V2_ASYMMETRIC_REPLAY_PASS", "warning=producer_last_touch_divergence: stored=6b6deb2f8f9bbe88b604b18d544856d6ae4e0013 current=94af46458aab6bb8597f2c4564f9b6d1e0d6975e; replay accepted by content identity", "record={\"current_last_touch\": \"94af46458aab6bb8597f2c4564f9b6d1e0d6975e\", \"reason\": \"producer_last_touch_divergence\", \"stored_commit\": \"6b6deb2f8f9bbe88b604b18d544856d6ae4e0013\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "REAL_V2_ASYMMETRIC_REPLAY_PASS\\nwarning=producer_last_touch_divergence: .*replay accepted by content identity\\nrecord=.*"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check; git diff --quiet cc4309a0 -- docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md scripts/issue_dg071_dg075_statistics.py scripts/paper_terms_lint.py tests/test_paper_terms_lint.py; test \"$(shasum -a 256 docs/paper/round7/dg071-dg075-statistics.json | cut -d' ' -f1)\" = 9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7; test \"$(shasum -a 256 docs/paper/round7/dg071-dg075-statistics.md | cut -d' ' -f1)\" = 041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b; test \"$(git diff --name-only cc4309a0)\" = $'docs/process_traces/2026-09-04-fanout/one-name-sweep/09-sol-rescope-report.md\\ntests/test_issue_dg071_dg075_statistics.py'; echo SCOPE_IMMUTABILITY_AND_DIFF_CHECK_CLEAN",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["SCOPE_IMMUTABILITY_AND_DIFF_CHECK_CLEAN"]},
      "expected": {"exit_code": 0, "tail_regex": "^SCOPE_IMMUTABILITY_AND_DIFF_CHECK_CLEAN$"}
    }
  ],
  "flags": []
}
```

## Change

The adopted Q4 ruling is installed as follows:

| Ruling clause | File:line implementation |
|---|---|
| Current-head last-touch equality is WARN-AND-RECORD, not a replay blocker. | `tests/test_issue_dg071_dg075_statistics.py:117-130` records both commits and emits `producer_last_touch_divergence` only after content replay succeeds. |
| Current producer bytes must match the stored script SHA-256; the stored commit must independently resolve to the same bytes. | `tests/test_issue_dg071_dg075_statistics.py:66-91` checks current content first, then authenticates `git show <stored commit>:<script path>` fail-closed. |
| The input digest and regenerated statistical payload must match. | `tests/test_issue_dg071_dg075_statistics.py:93-115` reissues against the stored input digest and requires byte-exact JSON and Markdown after normalizing only the history locator. |
| Re-scope one-name work to mutable authored terminology surfaces. | The surviving terminology is confined to `docs/paper/draft-v1.md:249,256`, `docs/paper/results-fill-registry.md:647`, and `docs/paper/round7/survival-map.md:274`. The retired broad one-name linter/exemption machinery remains absent; `scripts/paper_terms_lint.py:622-639` exposes only its original `lexicon` and `lint` commands. |
| Preserve issued DG-071/DG-075 bytes and their producer. | `docs/paper/round7/dg071-dg075-statistics.json:27-30` retains the historical tuple; V6 pins JSON `9a4fddde…`, Markdown `041a045e…`, and no session delta to either artifact or the producer. |
| Acceptance is P → producer edit → exact restoration R, where last-touch differs but the historical anchor and replay pass with a warning. | `tests/test_issue_dg071_dg075_statistics.py:857-971` is the one named acceptance regression. V2 demonstrates the old equality counterfactual red; V3 demonstrates the ruled mechanism green. |

No commit, squash, merge, or magistrate-owned state edit was made. The branch is ready for the lead's ordinary ancestry-preserving merge.

## Verification notes

Only the touched test module ran, per preflight. V2 is an expected-red counterfactual whose wrapper exits zero only after proving that the old byte comparison differs exclusively at `producer.git_commit`.
