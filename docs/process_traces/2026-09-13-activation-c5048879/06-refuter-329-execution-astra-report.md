```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Archive integrity and requested tests pass; the exact-base fence fails because HEAD has not merged 27957b60.",
  "workspace": {
    "base_requested": "27957b60",
    "base_mode": "exact",
    "head_start": "ae5b09e7d704740db82c81a18656a26a1c313ab0",
    "head_end": "ae5b09e7d704740db82c81a18656a26a1c313ab0",
    "upstream_end": "27957b6066104fa470dded61a3db06e723c728f0",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Requested integration baseline is absent from HEAD",
        "scope": "Exact-base acceptance gate; baseline drift, not an archive-induced deletion"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Two retained reading surfaces still cite moved files",
        "paths": [
          "docs/paper/results-fill-registry.md:132",
          "docs/project_critique_review.html:880"
        ]
      },
      {
        "id": "F3",
        "severity": "nit",
        "title": "Historical records retain old source paths by policy",
        "evidence": "/tmp/ref329-reference-census.tsv"
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "Six added lines fail the whitespace check",
        "evidence": "/tmp/ref329-diff-check.log"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat 27957b60..HEAD -- . ':!docs' ':!*.md'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          " configs/production_custody_inventory.json | 9 +--------",
          " tests/test_arm_readiness_schemas.py       | 5 +----",
          " tests/test_docs_freshness.py              | 2 ++",
          " 3 files changed, 4 insertions(+), 12 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 file changed, 2 insertions\\(\\+\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/ref329-audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS: 309 R100; 16 move-table rows sum to 309; 83121775 bytes; zero mapping/selection/kernel-pin violations",
          "REFERENCES: 12105 literal hit lines; 5696 after filename-boundary filtering; zero protected source-path hits; 3252 dated trace files excluded",
          "PASS: merge added no archive file and renamed/deleted nothing; working tree clean"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS: merge added no archive file and renamed/deleted nothing; working tree clean"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 75 tests in 2.796s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_doc*.py'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 40 tests in 0.385s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check 27957b60..HEAD",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "docs/process_traces/2026-09-10-side-threads/docs-thin-01-test-pinned-paths.txt:86: trailing whitespace.",
          "+docs/process_traces/2026-08-30-prefill-margin-coldgate/ and the "
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "B1",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "HEAD merged a4bb8838, not requested base 27957b60; their merge-base is a4bb8838. All independent requested checks were completed.",
      "needs": "Lead must integrate 27957b60 and review the resulting HEAD, or correct the requested baseline."
    }
  ]
}
```

## Findings

**F1 — blocker: exact-base gate fails.** `ae5b09e7` has second parent `a4bb8838`. `git log HEAD..27957b60` contains the successor-night handback commit `27957b60`; it was never merged.

Consequently, the requested two-dot diff includes a missing September 15 custody entry, a six-to-five test expectation change (`tests/test_arm_readiness_schemas.py:1705`), and predecessor-night instructions in `docs/process/NIGHT_HANDBACK.md:44`. Using this HEAD as the claimed current-main integration would supply September 13 coordinates instead of the successor’s coordinates.

This is **baseline drift**, not evidence that merging this PR normally would delete main’s additions. The diagnostic three-dot comparison shows only:

```text
 tests/test_docs_freshness.py | 2 ++
 1 file changed, 2 insertions(+)
```

The two added lines, at `tests/test_docs_freshness.py:290`, are:

```python
        # DOCS-THIN-01: archived history stays outside the live reference scan.
        and not path.relative_to(root).as_posix().startswith("docs/legacy/")
```

**F2 — should-fix: known stale references remain.**

- `docs/paper/results-fill-registry.md:132` points its `PLAN` source to the absent `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`. Following that evidence pointer fails; the file exists under `docs/legacy/process_traces/`.
- `docs/project_critique_review.html:880` links to absent `test_audit_2026-07-07.md`; clicking it fails. Its existing destination is `legacy/test_audit_2026-07-07.md`.

These are the known paper-lane/optional residuals from record 65 §2, not newly discovered runtime consumers. No files were repaired in this read-only review.

**F3 — nit: historical citations remain unresolved at their original locations.** The scan produced **12,105 literal matching lines**. Many are substring matches such as `STATUS.md` inside `PROJECT_STATUS.md`; filename-boundary filtering leaves 5,696 lines, predominantly historical transcripts.

Every literal hit is listed as **file:line** in the [complete census](/tmp/ref329-literal-census.txt); [full matching text](/tmp/ref329-reference-hits.txt) and [source-path matches](/tmp/ref329-reference-census.tsv) are retained separately.

Excluding 3,252 later trace files is supported by `docs/legacy/README.md:16`:

> Old links inside historical documents were not rewritten because rewriting a historical record to match a new layout would alter the record, and the record is the evidence.

The resume note additionally says “Do NOT rewrite them” for decision/council-log citations at `docs/process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md:133`. Historical replay commands or direct old-path lookups can fail; the documented archive lookup resolves them.

**No archive-caused runtime blocker found:** kernel, contracts, runbooks, named night-process surfaces, configs, scripts, tests, `joulewise/`, and `.github/` contain no actual moved-source-path hits.

**F4 — nit: whitespace check fails.** Under `docs/process_traces/2026-09-10-side-threads/`, trailing spaces occur in:

- `docs-thin-01-RESUME.md`: 208, 225, 231.
- `docs-thin-01-test-pinned-paths.txt`: 63, 80, 86.

A `git diff --check` gate exits 2; there is no demonstrated runtime consequence.

**Checks performed:** 309 `R100` renames; no changed archived payload; only `A docs/legacy/README.md` is non-R100 under the archive. The guide has **16 move-table rows summing to 309 files**, totaling **83,121,775 bytes**. All destination mappings conform. No archived trace dates on/after August 15, protected directories, or kernel/generator inputs were found.

All ten retained pre-cutoff trace directories are named and explained in `docs/legacy/README.md:104–113`:

- Kernel pins: `2026-07-15-axi-xhigh-consult`, `2026-08-03-q1-remint-bytecompare`, `2026-08-03-t3-doctrine-gate`, `2026-08-05-cgv-f3-consult`.
- Script/test pins: `2026-07-17-floor-extraction`, `2026-07-24-diagnostic-extraction`, `2026-08-09-prefill-phase-proof`.
- Campaign pins: `2026-08-07-plan-factory`, `2026-08-08-attribution-debate`.
- Historical superseded-charter citation: `2026-08-14-readiness-charter-consult`; explicitly not established as an active reader.

Merge hygiene passes: `HEAD^1..HEAD` changes **zero archive files** and contains **zero renames or deletions**.

Captured test summaries: [focused tests](/tmp/ref329-focused-tests.log): `Ran 75 tests in 2.796s`, `OK`; [discovery](/tmp/ref329-doc-tests.log): `Ran 40 tests in 0.385s`, `OK`. Discovery additionally finds `test_doctor.py`. [Generator check](/tmp/ref329-gen-state.log): empty output, exit 0. Final `git status --short`: empty.

## Residual risk

The full canonical suite was not rerun; this review ran the requested focused checks. No network, measurements, or prohibited-directory access occurred. The next exact step is lead resolution of F1, followed by verification of the resulting integration HEAD.