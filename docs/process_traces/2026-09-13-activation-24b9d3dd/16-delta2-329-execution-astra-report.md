```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Committed fixes pass all requested checks; only accepted historical and retired-site reference nits remain.",
  "workspace":{
    "base_requested":"a4bb8838",
    "base_mode":"descendant",
    "head_start":"f636f70b1685fda446b5240a7e012f27674d28ad",
    "head_end":"f636f70b1685fda446b5240a7e012f27674d28ad",
    "upstream_end":null,
    "branch":null
  },
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{
    "findings":[
      {"id":"F1","severity":"nit","title":"Historical references retain old paths under README:16 policy"},
      {"id":"F2","severity":"nit","title":"Retired generated site pages retain old paths; explicitly out of scope"}
    ]
  },
  "verification":[
    {
      "id":"V1","kind":"inspection",
      "cmd":"python3 -B /tmp/ref329-r2-audit.py","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["TABLE: 17 rows; sum(Files)=310; sum(Size)=83134998; MiB=79.28","RENAMES: count=310; bytes=83134998; MiB=79.28; missing table delta=0 file, 0 bytes","CENSUS: 310 old paths; 3291 surfaces; 3311 dated traces excluded; 290 literal hit lines; 100 boundary-valid lines"]},
      "expected":{"exit_code":0,"tail_regex":"missing table delta=0 file, 0 bytes"}
    },
    {
      "id":"V2","kind":"lint",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness tests.test_gen_state","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 75 tests in 4.289s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V4","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_paper_comparison_placements tests.test_paper_reported_energy tests.test_paper_custody","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 103 tests in 60.141s","OK","KILLED 130 owner-source mutations and 5 grant-policy mutations: stale receipts refused","PENDING production Git-blob role: fixture coverage is not production coverage","PENDING production Git-blob role: fixture coverage is not production coverage","KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V5","kind":"lint",
      "cmd":"git diff --check a4bb8838..HEAD","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V6","kind":"inspection",
      "cmd":"git diff --stat a4bb8838..HEAD -- . ':!docs' ':!*.md'","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[" tests/test_docs_freshness.py | 2 ++"," 1 file changed, 2 insertions(+)"]},
      "expected":{"exit_code":0,"tail_regex":"1 file changed, 2 insertions"}
    },
    {
      "id":"V7","kind":"inspection",
      "cmd":"git status --short","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags":[]
}
```

## Findings

No blocker or should-fix found.

**Rename purity — PASS.**

```text
$ git diff -M100% --diff-filter=R --name-status ae5b09e7..HEAD
R100	docs/process_traces/RESUME-2026-07-26.md	docs/legacy/process_traces/RESUME-2026-07-26.md

$ git diff -M ae5b09e7..HEAD --stat
 RUN_STATE.md                                                      | 2 +-
 docs/legacy/README.md                                             | 5 +++--
 docs/{ => legacy}/process_traces/RESUME-2026-07-26.md             | 0
 docs/paper/results-fill-registry.md                               | 2 +-
 docs/process/model_allocation_ledger.md                           | 6 +++---
 .../process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md | 8 +++++---
 .../2026-09-10-side-threads/docs-thin-01-test-pinned-paths.txt    | 6 +++---
 docs/project_critique_review.html                                 | 2 +-
 docs/specs/axi/sb_static_batch_verdict.md                         | 2 +-
 9 files changed, 18 insertions(+), 15 deletions(-)

$ git show HEAD:docs/legacy/process_traces/RESUME-2026-07-26.md | wc -c
   13223
```

Both `git show HEAD:docs/legacy/process_traces/RESUME-2026-07-26.md | shasum -a 256` and `git show ae5b09e7:docs/process_traces/RESUME-2026-07-26.md | shasum -a 256` returned:

```text
6fd4c507ee42f723514de6a9622488dbb0a6580afc7f49678a1a0f71f8dc27f1  -
```

**README arithmetic — PASS.** The [replay script](/tmp/ref329-r2-audit.py) parses numeric Files and Size cells, sums both columns, and independently totals destination Git-blob lengths:

```text
TABLE: 17 rows; sum(Files)=310; sum(Size)=83134998; MiB=79.28
RENAMES: count=310; bytes=83134998; MiB=79.28; missing table delta=0 file, 0 bytes
```

This matches `docs/legacy/README.md:20`; `83134998 / 1048576`, formatted to two decimals, is `79.28`.

**Repaired references — PASS.** Actual lines inspected: `RUN_STATE.md:7–8`, `docs/paper/results-fill-registry.md:132`, `docs/project_critique_review.html:880`, and `docs/specs/axi/sb_static_batch_verdict.md:200`. RUN_STATE’s abbreviated sibling names inherit the newly stated archive directory.

```text
test -e docs/legacy/process_traces/RESUME-2026-07-26.md => rc 0
test -e docs/legacy/process_traces/RESUME-2026-07-27.md => rc 0
test -e docs/legacy/process_traces/RESUME-2026-07-28.md => rc 0
test -e docs/legacy/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md => rc 0
test -e docs/legacy/process_traces/2026-07-16-axi-sb-live-probes/axi-sb-b2.jsonl => rc 0
(cd docs && test -e legacy/test_audit_2026-07-07.md) => rc 0
```

The three additional ledger citations at `docs/process/model_allocation_ledger.md:96,220,395` use the archive target. RUN_STATE’s generated fences remain at `5206,5239`, outside the repaired sentence. FIX-4’s dated note is present at `docs/process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md:292`.

**Census:** 310 old paths searched literally across 3,291 surfaces, excluding the archive and 3,311 dated trace files. All **290 matching lines** appear with file:line and classification in the [complete census](/tmp/ref329-r2-classified.tsv); [unabridged matching text](/tmp/ref329-r2-literal.txt) is also retained. Breakdown: 190 filename-substring false positives, 87 historical lines, 12 retired-site lines, and one resolved-link display label.

`docs/project_critique_review.html:880` retains `docs/test_audit_2026-07-07.md` as visible link text, but its actual `href="legacy/test_audit_2026-07-07.md"` resolves. This is not a broken pointer.

**F1 — nit, accepted historical references.** Every remaining historical hit follows, accepted under `docs/legacy/README.md:16`:

```text
RUN_STATE.md:1875,2192,2614,2829,2841,2919,3019,3045,3134,3171,3832,3922,3983,4002,5505,5507,5591,5595,5597,5600
TASK_QUEUE.md:184
docs/advisor_briefs/2026-07-17-window-a-brief.html:962,1020,1038,1100
docs/council_log.md:2740,3041,3050,3206,3355,3367,3397
docs/decision_log.md:170,3651,3974,3992,4013,8186,8694,8987,9177
docs/paper/draft-v1-review-round2-lensA.md:30,41,52,62,125
docs/reviews/2026-07-13-comprehensive-audit/manifests/EXCLUDED.txt:12,13,14,15,16,17,18,19,20,166
docs/reviews/2026-07-13-comprehensive-audit/receipts/WO-021-pre-demotion-freeze-cross-check.json:179
docs/run_reports/2026-07-13-bridge-v11.md:122
docs/run_reports/2026-07-16-resumption-nohw-batch.md:89
docs/run_reports/2026-07-17-window-a-floors.md:261,318
docs/run_reports/2026-08-07-paper-first-session.md:63
docs/run_reports/2026-08-08-t1-window-session.md:28
docs/run_reports/2026-08-10-t4-window-session.md:3,7,26,39,71,73,123,124,135,207
docs/run_reports/2026-08-12-t4-late-addendum.md:46,120,161,166
docs/run_reports/2026-08-12-t5-window-session.md:20,286,417
docs/run_reports/2026-08-13-t6-session.md:463,545,609,885
docs/run_reports/2026-08-23-t21-t22-session.md:814
docs/stream_logs/2026-07-17-advisor-brief.md:68
docs/stream_logs/2026-07-17-axes-foldin.md:4
```

**F2 — nit, retired generated pages, excluded by lead ruling:**

```text
docs/site/advisor_brief.html:963,1021,1039,1101
docs/site/council_log.html:1
docs/site/decision_log_archive_1.html:1
docs/site/decision_log_archive_4.html:1
docs/site/project_status.html:1
docs/site/readme.html:1
docs/site/record.html:1
docs/site/run_state.html:1
docs/site/task_queue.html:1
```

**Sibling runtime pins — none.** Tree-wide `rg -n --hidden --glob '!.git' --glob '!docs/legacy/**' 'RESUME-2026-07-26' .` found repaired citations, historical records, and retired pages; [full output](/tmp/ref329-r2-sibling-pins.txt). Targeted search of `state_kernel.json`, scripts, tests, configs, joulewise, and `.github` found no match.

## Residual risk

Focused suites passed; the full canonical suite was not run for this documentation delta. Literal searching does not establish absence of dynamically assembled references. The paper suite’s production-coverage qualifications remain as pasted above.

**What the lead should double-check:** perform the final integration-head review and replay after any further merge; this audit covers unchanged `f636f70b` against the requested bases. No repository files were modified; final status is empty.

Same signature as a round-0 finding? **NO** — no in-scope live reading surface still points to a moved path; remaining old references are accepted history, retired pages, or a label with a working href.