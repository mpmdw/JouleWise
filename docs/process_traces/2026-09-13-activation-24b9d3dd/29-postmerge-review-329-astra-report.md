```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No archive-induced runtime break found; the literal-existence criterion has 36 pre-existing missing matches.",
  "workspace": {
    "base_requested": "64fc4e27",
    "base_mode": "exact",
    "head_start": "64fc4e27408f1a13c57803fa8bbbcbad22bb1852",
    "head_end": "64fc4e27408f1a13c57803fa8bbbcbad22bb1852",
    "upstream_end": "64fc4e27408f1a13c57803fa8bbbcbad22bb1852",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "summary": "The requested every-literal test-e gate fails on 36 baseline matches, including fixtures, patterns, fragments and optional directories; see Findings."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat 27957b60..64fc4e27 -M",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["334 files changed, 1589 insertions(+), 26 deletions(-)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "334 files changed"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness tests.test_gen_state tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_paper_custody",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 131 tests in 59.113s",
          "OK",
          "KILLED 130 owner-source mutations and 5 grant-policy mutations: stale receipts refused",
          "PENDING production Git-blob role: fixture coverage is not production coverage",
          "PENDING production Git-blob role: fixture coverage is not production coverage",
          "KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --help",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["  --check               region mode: refuse instead of updating"]
      },
      "expected": {"exit_code": 0, "tail_regex": "region mode"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/postmerge329-audit.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "CHECKED 1292 occurrences; 304 distinct; 36 missing distinct",
          "PROCESS_DOCS: 0 cross-matches of old/new moved paths across 5 docs",
          "RENAMES_ALL_IN_LEGACY: True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "0 missing distinct"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

**B1 — BLOCKER under the requested “any miss” criterion.** Every extracted match received `test -e`. All 36 missing matches were also absent at `27957b60`; none establishes an archive-induced runtime failure. Exact paths and all occurrence locations are in the [pasted census log](/tmp/postmerge329-paths.log).

Missing-match source locations, grouped by file:

```text
docs/process/state_kernel.json:6405
scripts/build_site.py:881,888,902,909 (two placeholder paths)
scripts/build_site.py:1434,2106,2196
scripts/claims_lint.py:847,849,851
scripts/gen_state.py:252,253
tests/fixtures/state_kernel/selection_semantics.json:53
tests/test_build_site_parsers.py:204,206,215,220,226,231,232,238,239,242,424,480,554
tests/test_build_site_parsers.py:45
tests/test_claims_lint.py:664,666,668,673,675
tests/test_d165_rationale_census.py:208,262,273
tests/test_dependence_sensitivity.py:446
tests/test_docs_freshness.py:286,1016,1017,1018,1029,1033,1037
tests/test_floor_extraction.py:187
tests/test_gen_state.py:501
tests/test_identity_pins.py:412
tests/test_pack_capsule.py:196,203,293
tests/test_partial_record_enclosure.py:54
tests/test_rpt001_report_slice.py:591
tests/test_single_count_discipline_census.py:1153
```

Context explains these misses: optional directories are guarded by `exists()` in `scripts/claims_lint.py:854`; the stop-card prefix is conditional on an active card at `scripts/gen_state.py:249`; `tests/test_rpt001_report_slice.py:591` explicitly asserts absence. Other matches include fixture names, glob/interpolation expressions, comments and filename stems.

**Merge inventory:** exactly **310 R100, 17 M, 7 A**; all rename destinations are under `docs/legacy/`. Parents match the supplied hashes. No unexpected code changes: `tests/test_docs_freshness.py:290` adds only the comment and archive exclusion.

Non-rename list:

```text
M CLAIMS_STATUS.md
M README.md
M RUN_STATE.md
M docs/contracts/bridge_protocol.md
A docs/legacy/README.md
M docs/paper/results-fill-registry.md
M docs/phase_2/alpha_arm_readiness.md
M docs/phase_2/three_night_freeze_manifest.md
M docs/phase_2/window_runbook.md
M docs/process/model_allocation_ledger.md
A docs/process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md
A docs/process_traces/2026-09-10-side-threads/docs-thin-01-archived-trace-dirs.txt
A docs/process_traces/2026-09-10-side-threads/docs-thin-01-phaseB-astra-blocked.md
A docs/process_traces/2026-09-10-side-threads/docs-thin-01-phaseB2-astra.md
A docs/process_traces/2026-09-10-side-threads/docs-thin-01-scout-astra.md
A docs/process_traces/2026-09-10-side-threads/docs-thin-01-test-pinned-paths.txt
M docs/project_critique_review.html
M docs/specs/axi/sb_static_batch_verdict.md
M docs/specs/axi/sc_spec_decode_verdict.md
M docs/strategy/2026-08-07-three-night-operator-packet.md
M docs/strategy/2026-08-08-40h-plan.md
M docs/strategy/2026-08-09-extension-axes-roadmap.md
M docs/strategy/2026-08-14-70h-plan.md
M tests/test_docs_freshness.py
```

**Derivation integration:** `scripts/gen_derivation_night.py:50` still names the existing, tracked, LIVE `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`. The `--verify` branch at lines 897–910 reads supplied plan/binding files, the clone’s tracked chain, wrapper and sidecar. It returns before the runsheet read at line 925. Static inspection found no archived dependency. Only `--help` was executed.

All five named magistrate/courier documents had **zero cross-matches against both old and new paths of all 310 renames**. Final Git status was empty; no repository files were changed.

## Residual risk

**What the lead should double-check:** adjudicate B1’s baseline fixture/pattern/optional-path exceptions before marking the literal gate green. The sweep checks textual paths, not every dynamically constructed dependency. Wrapper verification was inspected, not executed against custody inputs. The suite’s production Git-blob coverage remains explicitly PENDING. No network or hardware verification was performed.