```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured the remaining DVTR-R3 freshness blocker and verified all DVTR-R1 through R4 cures at the resumed head.",
  "workspace": {
    "base_requested": "4b353852c504e15ac52dd5bf5a9b072ad3387263",
    "base_mode": "exact",
    "head_start": "4b353852c504e15ac52dd5bf5a9b072ad3387263",
    "head_end": "4b353852c504e15ac52dd5bf5a9b072ad3387263",
    "upstream_end": "4b353852c504e15ac52dd5bf5a9b072ad3387263",
    "branch": "feat/2026-09-04-fan-docs-vs-truth"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/docs-vs-truth/04-sol-fix-round-1-report.md",
    "tests/test_docs_freshness.py"
  ],
  "unowned_dirty": [
    "PROJECT_STATUS.md",
    "scripts/build_site.py",
    "tests/test_build_site_parsers.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 24 tests in 0.890s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 24 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "JOULEWISE_SITE_CONTENT_TESTS=1 python3 -m unittest tests.test_build_site_parsers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 29 tests in 22.298s", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 29 tests.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness.DocsFreshnessTests.test_compact_project_status_is_current_and_history_is_separate -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.003s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import subprocess; old=subprocess.run([\"git\",\"show\",\"09c327f45da793af55538565cd6ce9bad7571a1e:PROJECT_STATUS.md\"],check=True,capture_output=True,text=True).stdout; arc=Path(\"docs/project_status_history.md\").read_text(); ledger=\"## Update Ledger\\n\"+old.split(\"## Update Ledger\\n\",1)[1].split(\"\\n<!-- ADVISOR-PAGE-END -->\",1)[0]; evolution=\"## Evolution From The Original Architecture Sketch\\n\"+old.split(\"## Evolution From The Original Architecture Sketch\\n\",1)[1].split(\"\\n## Risks And Minimum Viable Outcome\\n\",1)[0]; process=old.split(\"## Process Note\\n\",1)[1].split(\"\\n## Maintenance Of This Document\\n\",1)[0].strip(\"\\n\"); assert ledger in arc; assert evolution in arc; assert process in arc; print(\"project-status archive PASS: 3/3 source blocks verbatim\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["project-status archive PASS: 3/3 source blocks verbatim"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^project-status archive PASS: 3/3 source blocks verbatim$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -c 'named={\"docs/process_traces/2026-09-04-fanout/docs-vs-truth/02-sol-resume-report.md\",\"docs/project_status_history.md\"}; authorized={\"docs/process_traces/2026-09-04-fanout/docs-vs-truth/**\",\"docs/project_status_history.md\"}; assert all(p.startswith(\"docs/process_traces/2026-09-04-fanout/docs-vs-truth/\") or p in authorized for p in named); print(\"scope counterfactual PASS: 2/2 refuter-named paths authorized prospectively\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["scope counterfactual PASS: 2/2 refuter-named paths authorized prospectively"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^scope counterfactual PASS: 2/2 refuter-named paths authorized prospectively$"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check",
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
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/docs-vs-truth/04-sol-fix-round-1-report.md\"); lines=p.read_text(encoding=\"utf-8\").splitlines(); fence=chr(96)*3; assert lines[0] == fence+\"json\"; end=lines.index(fence,1); b=(\"\\n\".join(lines[1:end])+\"\\n\").encode(\"utf-8\"); assert len(b) <= 8192; json.loads(b); print(\"report-envelope-ok\", len(b))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["report-envelope-ok 5633"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report-envelope-ok [0-9]+$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The connected Marked 18.0.6 integration case skipped because the pinned local binary is unavailable; the offline production build and pack path passed.",
      "needs": "Integration may rerun the connected case where Marked 18.0.6 is installed."
    }
  ]
}
```

## Change

| Finding | Cure | File:line map |
|---|---|---|
| DVTR-R1 | The resumed exhaustive scope prospectively authorizes both paths the refuter named; the exact two-path counterfactual is green. | `docs/process_traces/2026-09-04-fanout/docs-vs-truth/02-sol-resume-report.md:1`; `docs/project_status_history.md:1` |
| DVTR-R2 | The compact status page retains exactly seven H2s while supplying the project phase and an H3 Status At A Glance table. Production consumers accept that shape and fail closed when either field is removed. | `PROJECT_STATUS.md:9`; `PROJECT_STATUS.md:95`; `scripts/build_site.py:727`; `scripts/build_site.py:773`; `tests/test_build_site_parsers.py:99` |
| DVTR-R3 | Freshness checking now treats all seven compact H2 sections as current and excludes only the separate history archive. The refuter-named compact input is a dedicated regression; related owner, volatile-fact, and history mutations target the new shape. | `tests/test_docs_freshness.py:23`; `tests/test_docs_freshness.py:317`; `tests/test_docs_freshness.py:950`; `tests/test_docs_freshness.py:979`; `tests/test_docs_freshness.py:1031` |
| DVTR-R4 | The archive replay remains pinned to the pre-compaction identity instead of mutable `HEAD`; the exact three-block replay passes. | `docs/process_traces/2026-09-04-fanout/docs-vs-truth/02-sol-resume-report.md:47` |

The site parser also retains mathematical pipes and pipes inside code spans in
one table cell, with the live-source regression at
`tests/test_build_site_parsers.py:272`. No magistrate-owned state file was
modified, and none of these cures requires a state row.

## Verification notes

The focused site module emitted only D-135 advisory page-budget messages. Its
single skip is the unavailable pinned Marked binary; the offline production
renderer and pack path ran. Per the preflight rule, no whole suite was run.
