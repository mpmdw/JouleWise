```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Refreshed 135 locators and registered 26 traceable appendix values; DG-063 needs a ruling because its anchor is absent.",
  "workspace": {
    "base_requested": "paper/t26-round4",
    "base_mode": "exact",
    "head_start": "6bb9e5747d725c07857638e371e84611b1df9c59",
    "head_end": "6bb9e5747d725c07857638e371e84611b1df9c59",
    "upstream_end": "6bb9e5747d725c07857638e371e84611b1df9c59",
    "branch": "paper/t26-round4"
  },
  "pathspec": [
    "docs/paper/results-fill-registry.md"
  ],
  "unowned_dirty": [
    "docs/paper/artifact-guide.md",
    "docs/paper/draft-v1.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 /Users/edr/code/JouleWise/scripts/check_paper_replay_fence.py --draft docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MEMBER 20260722T145535-e941c821",
          "COMPARED 43",
          "MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MISMATCHES 0"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m pytest tests/test_render_results_fills.py -q",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "/opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "27 passed"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m pytest tests/test_render_results_fills.py -q",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "27 passed, 2 subtests passed in 0.49s"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "27 passed, 2 subtests passed"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "DG-063's own anchor, `10.818 ms`, no longer occurs in the draft, so its stale line 194 locator was not guessed or changed.",
      "needs": "Rule whether DG-063 should be retired as provenance or rebound to a deliberately restored value-site."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The literal system-python pytest command lacks pytest; the repository's existing main-checkout virtual environment passed the requested test.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The replay script still parses Section 2 only; appendix occurrences remain registry-bound rather than mechanically fenced.",
      "needs": ""
    }
  ]
}
```

## Change

Updated [results-fill-registry.md](/Users/edr/code/JouleWise-wt-r4/docs/paper/results-fill-registry.md:63) for the capstone:

- Checked all 139 pre-existing explicit locators by their own anchors.
- Moved 135; confirmed 136 live anchors. DG-001 remained correctly at line 11.
- Left retired DS-04 and DS-07 byte-identical.
- No live row required a section-number correction.
- Added DG-102–DG-127 under the [appendix continuation binding](/Users/edr/code/JouleWise-wt-r4/docs/paper/results-fill-registry.md:660): 26 values registered, 26 traceable, zero gaps.
- Six appendix literal sites state values already replay-fenced through Section 2; 20 are appendix-only registry bindings.

Repeated anchors were found for these rows:

- Shared calibration values: DG-005/009/013/017/021/107, DG-024, DG-026/029/110/111/125, DG-027/028/124, and DG-030/126.
- Body/comment or repeated-clause values: DG-032/033 and DG-037/042.
- Repeated diagnostic values: DG-043/098, DG-050/099, DG-051/100, DG-052/101, and DG-055.
- Repeated screen values: DG-058/059/061/062.
- Population/count values: DG-066/067/068/069/072/073/076/077.
- Prompt-sizing values: DG-079/081/082/083/086/087/088/091/092/093/096/097.
- Appendix repetitions: DG-121 and DG-123.

They were disambiguated using the row’s named section, stamp/table/site role, surrounding labeled clause, and—where a value appeared in an evidence comment—the requested body site. Same-line repetitions were distinguished by their semantic clause.

## Verification notes

The required replay fence passed with `COMPARED 43`, `MISMATCHES 0`.

The literal `python3 -m pytest` command could not import pytest. Running the same renderer test with the repository’s existing virtual environment passed all 27 tests and two subtests.

## Residual risk

DG-063 at [line 620](/Users/edr/code/JouleWise-wt-r4/docs/paper/results-fill-registry.md:620) is NEEDS-RULING. Its `10.818 ms` anchor is absent; the draft now says only “a larger figure.” The recommended disposition is retirement as provenance unless the lead deliberately restores a numeric draft site.

For mechanical appendix coverage, the replay script would need unique fail-closed A.3.3/A.3.6 extractors, comparisons for all 26 values and their rounding rules, an increased comparison census, and corresponding tests.