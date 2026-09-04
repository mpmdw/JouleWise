```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Replaced the printed-negative-result build note with replicable prose, added and registered the labelled overlap SVG, issued DG-071/DG-075 in the registry, and passed the paper suite plus full R7F replay.",
  "workspace": {
    "base_requested": "33290b8bbe82b126037101edf8f15cdf96c920da",
    "base_mode": "exact",
    "head_start": "33290b8bbe82b126037101edf8f15cdf96c920da",
    "head_end": "33290b8bbe82b126037101edf8f15cdf96c920da",
    "upstream_end": null,
    "branch": "feat/2026-09-02-paper-e"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/figures-plan.md",
    "docs/paper/figures/README.md",
    "docs/paper/figures/fig5_phase_record_overlap.svg",
    "docs/paper/results-fill-registry.md",
    "docs/paper/round7/fill-checklist.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=<scratchpad>/paper/tmp-E PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 68 tests in 618.502s",
          "OK (skipped=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 68 tests.*OK \\(skipped=3\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/paper/tmp-E PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.530s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "shasum -a 256 docs/paper/round7/dg071-dg075-statistics.md docs/paper/round7/dg071-dg075-statistics.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b  docs/paper/round7/dg071-dg075-statistics.md",
          "9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7  docs/paper/round7/dg071-dg075-statistics.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "041a045e.*dg071-dg075-statistics.md.*9a4fddde.*dg071-dg075-statistics.json"
      }
    },
    {
      "id": "V4",
      "kind": "build",
      "cmd": "TMPDIR=<scratchpad>/paper/tmp-E PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py --corpus-root /Users/edr/code/JouleWise",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ok   replay XD bytes",
          "ok   replay F4 bytes",
          "ok   replay AQ bytes",
          "R7F PLACED 0/16",
          "R7F COMPARED 184 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F COMPARED 184 / MISMATCHES 0"
      }
    },
    {
      "id": "V5",
      "kind": "build",
      "cmd": "TMPDIR=<scratchpad>/paper/tmp-E PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 3,
        "tail": [
          "R7F CORPUS UNAVAILABLE: /Users/edr/code/JouleWise-wt-paper-e/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/instrument_evidence.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F COMPARED 184 / MISMATCHES 0"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "xmllint --noout docs/paper/figures/fig5_phase_record_overlap.svg",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "scripts/bridge scope-check --baseline .codex-bridge/baselines/paper-e-sol-20260902b.json --expect-digest sha256:56c95eed2cf8aada6fedcee1c3c0898d37b90fd4f756eccf73b8b16e9c81254b --scope docs/paper/draft-v2-skeleton.md:exact docs/paper/results-fill-registry.md:exact docs/paper/figures:subtree docs/paper/figures-plan.md:exact docs/paper/round7:subtree docs/paper/fill-rehearsal:subtree tests:subtree",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SCOPE_OK; HEAD unchanged; 6 persistent paths in scope"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SCOPE_OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The requested bare R7F command treats the isolated worktree as its default corpus root and exits 3 because retained corpora are not copied into that worktree; the same command with the retained corpus root supplied explicitly passed all 184 comparisons, and the required paper suite independently passed the same retained-corpus replay.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The SVG is well-formed and every visual mark is directly labelled in its source, but raster preview was unavailable: native converters were blocked or unsupported and the local browser plugin runtime was missing a cached module.",
      "needs": "Lead visual glance during final diff gate."
    }
  ]
}
```

## Change

Replaced the complete Section 6 build note with reader-facing prose that defines a sampling-record support, gives the positive-time overlap inequality, explains why the three-record minimum is a forcing constraint, walks the retained 0.121034145-s example using only issued statistics, prints the 37-of-50 / 13-of-50 population result, and states both the supported and forbidden conclusions.

Added `fig5_phase_record_overlap.svg`, registered it in the figures plan and figure README, and labelled every record support, phase edge, shared segment, time axis, overlap count, threshold comparison, and decision inside the SVG. The rule counts are illustrative examples; widths and alignments are not to scale, and no measured timing value appears in the diagram.

Changed DG-071 and DG-075 from `STOP_FILL` to `ISSUED`, copied their exact sample counts, medians, and IQR renderings from the PR #276 artifact, and quoted both artifact paths and SHA-256 values in each row. Updated all DG-071/DG-075 checklist and contradiction text found in the registry and round-7 fill checklist. No reference occurred under `docs/paper/fill-rehearsal/`.

### Diff summary

The required `git diff --stat` output (which excludes the new untracked SVG until the lead stages it) was:

```text
 docs/paper/draft-v2-skeleton.md     | 88 +++++++++++++++++++++++++++----------
 docs/paper/figures-plan.md          |  5 +++
 docs/paper/figures/README.md        | 17 ++++++-
 docs/paper/results-fill-registry.md | 28 +++++++-----
 docs/paper/round7/fill-checklist.md | 25 +++++------
 5 files changed, 112 insertions(+), 51 deletions(-)
```

The additional untracked SVG is 97 lines / 7,736 bytes, SHA-256 `35edfb8bcc5ced0d12b2270f0120153c9e761d5067d7939ae58a7f5a70a1ddfc`.

## Executed evidence

### First-use table

| Term | First use | Built or glossed |
|---|---:|---:|
| record support | draft line 921 | line 921: the record's start-to-end interval |
| record width | line 922 | line 922: the duration of the support |
| positive overlap | line 924 | lines 924–927: the strict interval-intersection inequality |
| overlap count | line 928 | line 928: number of supports passing that test |
| resolvability rule | lines 930–934 | overlap count must be at least three; otherwise no phase energy is assigned |
| interquartile range (IQR) | lines 952–953 | upper edge minus lower edge of the middle half of sorted values |
| endpoint convention | lines 956–958 | separately rounded labels may differ in the final printed digit |
| record-period distribution | lines 958–960 | the collection of durations produced by the sampler |

Mechanical ledger test:

```text
...
----------------------------------------------------------------------
Ran 3 tests in 0.530s

OK
```

### Numeric provenance

| Printed value | Authority |
|---|---|
| 0.121034145 s | registry DG-070 |
| 0.121 s | registry DG-074 |
| n = 406, 120.9186 ms median, 5.9508 ms IQR | issued artifact statistic DG-071 |
| n = 405, 120.9224 ms median, 5.8949 ms IQR | issued artifact statistic DG-075 |
| overlap count two; minimum three | registry DG-072 / DG-073 |
| 37 of 50; 13 of 50 | registry DG-067 / DG-068 / DG-069 and DG-076 / DG-077 |

No reader-facing number was computed at the desk.

### Artifact hashes

```text
041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b  docs/paper/round7/dg071-dg075-statistics.md
9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7  docs/paper/round7/dg071-dg075-statistics.json
```

### Test tail

```text
s...s..............s................................................
............
----------------------------------------------------------------------
Ran 68 tests in 618.502s

OK (skipped=3)
```

### Round-7 artifact fence

R7F covers the edited registry and successor skeleton. Its documented zero-placement pin rewrite applies in the commit that places DX markers. This change placed no DX marker and changed no pinned XD/AQ/F4/producer source, so there was no pin to update. The full replay with the retained corpus root supplied explicitly ended:

```text
ok   replay XD bytes
ok   replay F4 bytes
ok   replay AQ bytes
R7F PLACED 0/16
R7F COMPARED 184 / MISMATCHES 0
```

The always-on worktree-local half also passed:

```text
R7F PLACED 0/16
R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
```

### Git status

```text
## feat/2026-09-02-paper-e
 M docs/paper/draft-v2-skeleton.md
 M docs/paper/figures-plan.md
 M docs/paper/figures/README.md
 M docs/paper/results-fill-registry.md
 M docs/paper/round7/fill-checklist.md
?? docs/paper/figures/fig5_phase_record_overlap.svg
```

`git diff --check` passed with no output. The bridge checker returned `SCOPE_OK`, with HEAD unchanged and all six persistent paths inside the declared scope.

## Registry contradictions

The issued artifact and the launch addendum agree exactly on both values: DG-071 is n = 406, median 120.9186 ms, IQR 5.9508 ms; DG-075 is n = 405, median 120.9224 ms, IQR 5.8949 ms. No value conflict was found.

The pre-edit registry nevertheless said both values were still pending, its discrepancy table said no issued artifact existed, and its lead checklist still required issuance. The round-7 fill checklist repeated the same stale state in Batch 4 and in its open-gaps list. Those were status/provenance contradictions rather than numeric conflicts; each now points to the issued PR #276 Markdown and JSON artifacts and their exact hashes.

## Verification notes

The bare R7F command fails because its default corpus root is the isolated worktree, where the retained corpora are absent. Supplying the retained corpus root explicitly passed the complete replay, and the required paper suite passed that same replay path. SVG raster preview was not available in this sandbox; XML structure and direct in-source label coverage were checked instead.

## Residual risk

The lead should visually glance at the SVG during the final diff gate because this environment could not produce a raster preview. No scientific or registry acceptance item remains unmet.
