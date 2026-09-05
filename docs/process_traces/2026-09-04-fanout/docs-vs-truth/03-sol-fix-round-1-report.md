```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Cured DVTR-R1, R2, and R4 with regressions; DVTR-R3 requires the out-of-scope freshness test module.",
  "workspace": {
    "base_requested": "019c09dc8a51294282b6189c74e5bcc654557940",
    "base_mode": "exact",
    "head_start": "019c09dc8a51294282b6189c74e5bcc654557940",
    "head_end": "019c09dc8a51294282b6189c74e5bcc654557940",
    "upstream_end": "019c09dc8a51294282b6189c74e5bcc654557940",
    "branch": "feat/2026-09-04-fan-docs-vs-truth"
  },
  "pathspec": [
    "PROJECT_STATUS.md",
    "docs/process_traces/2026-09-04-fanout/docs-vs-truth/02-sol-resume-report.md",
    "docs/process_traces/2026-09-04-fanout/docs-vs-truth/03-sol-fix-round-1-report.md",
    "scripts/build_site.py",
    "tests/test_build_site_parsers.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/docs-vs-truth/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "JOULEWISE_SITE_CONTENT_TESTS=1 python3 -m unittest tests.test_build_site_parsers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 29 tests in 26.053s", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 29 tests.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 23 tests in 1.004s", "FAILED (failures=5)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 23 tests.*OK"
      }
    },
    {
      "id": "V3",
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
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'named={\"docs/process_traces/2026-09-04-fanout/docs-vs-truth/02-sol-resume-report.md\",\"docs/project_status_history.md\"}; authorized={\"docs/process_traces/2026-09-04-fanout/docs-vs-truth/**\",\"docs/project_status_history.md\"}; assert \"docs/project_status_history.md\" in authorized; assert all(p.startswith(\"docs/process_traces/2026-09-04-fanout/docs-vs-truth/\") or p in authorized for p in named); print(\"scope counterfactual PASS: 2/2 refuter-named paths authorized prospectively\")'",
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
      "id": "V5",
      "kind": "inspection",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "DVTR-R3 can only be cured honestly by updating the freshness checker's retired PROJECT_STATUS boundaries; that module is outside WRITE_SCOPE.",
      "needs": "Resume with tests/test_docs_freshness.py added to WRITE_SCOPE."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The connected Marked 18.0.6 integration case skipped because the pinned local binary is unavailable; the offline production build and pack path passed.",
      "needs": "Integration may rerun the connected case where Marked 18.0.6 is installed."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The production build reports D-135 advisory page and decode budgets; D-135 makes these warnings non-gating and the regression now preserves that contract.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_docs_freshness.py"],
    "reason": "DVTR-R3 names this checker: it still slices PROJECT_STATUS.md at removed Previous Update, Summary, and Process Note headings instead of the ruled seven-section current document and separate history archive.",
    "blocked_work": "Update the five failing freshness checks, add the refuter-named compact-document counterfactual, and make the focused module green.",
    "minimal_change": "Retarget _current_sections and the direct project-status slice to the seven current H2 sections / ADVISOR-PAGE-END boundary, keep docs/project_status_history.md excluded as history, and update the related mutations."
  }
}
```

## Change

| Finding | Cure | Evidence map |
|---|---|---|
| DVTR-R2 | Restored the two production source contracts without undoing the ruled seven-H2 compaction: the project-phase line is current, and Status At A Glance is a third-level subsection. Only that parser may accept the subsection form. The regression passes the actual compact document to both consumers, asserts its exact seven H2s, and removes each refuter-named field in turn to prove fail-closed behavior. | `PROJECT_STATUS.md:9`, `PROJECT_STATUS.md:95`, `scripts/build_site.py:727`, `scripts/build_site.py:773`, `tests/test_build_site_parsers.py:99` |
| DVTR-R3 | Not modified: the required checker is outside the exhaustive allowlist. Its five failures still stop at the retired Previous Update boundary before evaluating content. | `tests/test_docs_freshness.py:319`, `tests/test_docs_freshness.py:324`, `tests/test_docs_freshness.py:330`, `tests/test_docs_freshness.py:333` |
| DVTR-R1 | The resumed prompt prospectively authorizes both refuter-named paths: the trace wildcard covers the resume report and `docs/project_status_history.md` is explicit. The scope counterfactual checks exactly those two names. | `docs/process_traces/2026-09-04-fanout/docs-vs-truth/02-sol-resume-report.md:1`, `docs/project_status_history.md:1` |
| DVTR-R4 | Replaced mutable `HEAD` with the pre-compaction identity `09c327f45da793af55538565cd6ce9bad7571a1e`; the exact replay now passes 3/3 archived source blocks. | `docs/process_traces/2026-09-04-fanout/docs-vs-truth/02-sol-resume-report.md:47` |

The production module then reached two live-source conditions that its earlier
failure had masked. Markdown table parsing now retains unescaped mathematical
pipes and pipes inside code spans in a single cell, with a combined regression
at `scripts/build_site.py:689` and `tests/test_build_site_parsers.py:272`.
The pack assertion at `tests/test_build_site_parsers.py:1084` now accepts only
the D-135 advisory prefix rather than contradicting the established warn-only
contract. No magistrate-owned state document was modified, and no state row is
needed for these cures.

## Verification notes

The site module is green through the production build and pack path. Its one
skip is the unavailable pinned Marked 18.0.6 binary; the offline production
renderer executed. The freshness module remains red only at the out-of-scope
legacy boundaries named in DVTR-R3. Per the preflight rule, no whole suite was
run.

## Residual risk

NEEDS_SCOPE: add `tests/test_docs_freshness.py` and resume this fix round. Until
then, five freshness checks cannot inspect the compact advisor document, so the
landing is not acceptance-ready despite the green production site module.
