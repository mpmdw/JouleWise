```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Applied F1's registry and census paper-destination cures.",
  "workspace": {
    "base_requested": "b3a953e5",
    "base_mode": "exact",
    "head_start": "b3a953e5cc64841d307099de48c11dc0f1430ce9",
    "head_end": "b3a953e5cc64841d307099de48c11dc0f1430ce9",
    "upstream_end": "b3a953e5cc64841d307099de48c11dc0f1430ce9",
    "branch": "feat/2026-09-05-d166-prompt0"
  },
  "pathspec": [
    "docs/paper/results-fill-registry.md",
    "docs/process_traces/2026-09-05-d166-prompt0/01-dependency-census.md",
    "docs/process_traces/2026-09-05-d166-prompt0/04-fix-round-1-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "ready"},
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check; printf '%s\\n' 'PASS git diff --check'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS git diff --check"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS git diff --check"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nfrom pathlib import Path\n\nregistry = Path('docs/paper/results-fill-registry.md').read_text(encoding='utf-8')\ncensus = Path('docs/process_traces/2026-09-05-d166-prompt0/01-dependency-census.md').read_text(encoding='utf-8')\nrequired_rule = 'd166_fixed_prompt_zero.v1'\nrequired_old = 'd166_block_prompt_cycle.v1'\nrequired_authority = 'docs/process_traces/2026-09-04-peer-audit/43-magistrate-synthesis-gate-17.md'\nrequired_disclaimer = 'The comparison supports this fixed prompt and makes no prompt-population generality claim.'\nrequired_destination = 'draft-v2-skeleton.md, workload paragraph, paper-K seat'\nfor row_id in ('V5-WL-001', 'V5-WL-004'):\n    row = next(line for line in registry.splitlines() if line.startswith(f'| {row_id} |'))\n    assert len(row.strip('|').split('|')) == 5, row\n    for value in (required_rule, required_old, required_authority, 'Q-17-4'):\n        assert value in row, (row_id, value)\nassert registry.count(required_disclaimer) == 1\nassert required_destination in registry\nassert census.count('## Paper destination') == 1\npaper_destination = census.split('## Paper destination', 1)[1]\nfor value in ('V5-WL-001', 'V5-WL-004', required_destination):\n    assert value in paper_destination, value\nprint('PASS registry rows: 2; five cells each; fixed-zero rule, supersession, Q-17-4, disclaimer, and destination present')\nprint('PASS census Paper destination: one section; both registry rows and paper-K placement named')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS registry rows: 2; five cells each; fixed-zero rule, supersession, Q-17-4, disclaimer, and destination present",
          "PASS census Paper destination: one section; both registry rows and paper-K placement named"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS census Paper destination: one section; both registry rows and paper-K placement named"}
    }
  ],
  "flags": []
}
```

## Change

Amended only registry rows V5-WL-001 and V5-WL-004 with the ratified fixed-zero
decode assignment, superseded rule, Q-17-4 authority, and exact fixed-prompt
disclaimer. Added the census's Paper destination section naming both rows and
the Section 1 placement `draft-v2-skeleton.md, workload paragraph, paper-K seat`.

## Verification notes

The read-only structural inspection and `git diff --check` passed. No test was
run: `tests.test_paper_first_use_ledger` does not cover the registry, and the
discovery suite was not run. Consequently, there is no test tail to paste.
